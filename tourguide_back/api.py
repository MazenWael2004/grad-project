from __future__ import annotations

from datetime import UTC, datetime
from math import asin, cos, radians, sin, sqrt
from typing import Annotated, Literal

from services.vision_classifier import classify_landmark

from dotenv import load_dotenv

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import uuid
import json
from pathlib import Path

from backend import (
    ApiSettings,
    AppRepository,
    EvalEventRecord,
    LiveKitAccessTokenIssuer,
    LiveKitTokenIssuer,
    RecognitionRecord,
    SessionRecord,
    create_session_record,
    hash_guest_token,
    public_state,
    repository_from_settings,
)
from content import load_giza_tour

load_dotenv(".env.local")

import os

print("LIVEKIT_API_KEY =", os.getenv("LIVEKIT_API_KEY"))
print("LIVEKIT_API_SECRET =", os.getenv("LIVEKIT_API_SECRET"))
print("LIVEKIT_URL =", os.getenv("LIVEKIT_URL"))

SUPPORTED_LANGUAGES = {"en", "ar-EG"}
GIZA_STOP_LOCATIONS = {
    "khufu": (29.9792, 31.1342),
    "khafre": (29.9761, 31.1307),
    "menkaure": (29.9725, 31.1283),
    "sphinx": (29.9753, 31.1376),
    "arrival": (29.9784, 31.1329),
}


class SessionCreateRequest(BaseModel):
    tour_slug: str = Field(min_length=1)
    language: Literal["en", "ar-EG"] = "en"


class EventRequest(BaseModel):
    session_id: str
    event_id: str
    event_type: str
    payload: dict[str, object] = Field(default_factory=dict)


def create_app(
    *,
    settings: ApiSettings | None = None,
    repository: AppRepository | None = None,
    token_issuer: LiveKitTokenIssuer | None = None,
) -> FastAPI:
    settings = settings or ApiSettings.from_env()
    repository = repository or repository_from_settings(settings)
    token_issuer = token_issuer or LiveKitAccessTokenIssuer(settings)

    app = FastAPI(title="AI Tour Guide API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "Accept"],
    )

    def authenticate_session(
        session_id: Annotated[str, Path()],
        authorization: Annotated[str | None, Header()] = None,
    ) -> SessionRecord:
        print("AUTHORIZATION HEADER:", repr(authorization))
        return _authenticate_session(
            session_id=session_id,
            authorization=authorization,
            repository=repository,
            settings=settings,
        )

    session_dependency = Depends(authenticate_session)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/tours")
    def tours() -> dict[str, list[dict[str, object]]]:
        graph = load_giza_tour()
        return {
            "tours": [
                {
                    "slug": graph.slug,
                    "title": "Giza Plateau Tour",
                    "site": "Giza",
                    "stops": [
                        {"slug": stop.slug, "title": stop.title} for stop in graph.stops
                    ],
                }
            ]
        }

    @app.post("/sessions", status_code=status.HTTP_201_CREATED)
    def create_session(request: SessionCreateRequest) -> dict[str, object]:
        if request.language not in SUPPORTED_LANGUAGES:
            raise HTTPException(status_code=422, detail="unsupported language")

        now = datetime.now(UTC)
        try:
            session, checkpoint, guest_token = create_session_record(
                tour_slug=request.tour_slug,
                language=request.language,
                settings=settings,
                now=now,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        repository.create_session(session, checkpoint)
        return {
            "session_id": session.id,
            "guest_session_token": guest_token,
            "expires_at": session.expires_at,
            "initial_state": public_state(checkpoint.state_payload),
        }

    @app.post("/sessions/{session_id}/livekit-token")
    def livekit_token(
        session: SessionRecord = session_dependency,
    ) -> dict[str, object]:
        print("LIVEKIT_API_KEY =", settings.livekit_api_key)
        print("LIVEKIT_API_SECRET =", settings.livekit_api_secret)
        print("LIVEKIT_URL =", settings.livekit_url)

        join_token = token_issuer.issue(session=session)
        return {
            "url": join_token.url,
            "room_name": join_token.room_name,
            "participant_identity": join_token.participant_identity,
            "participant_token": join_token.participant_token,
            "expires_at": join_token.expires_at,
        }

    @app.get("/sessions/{session_id}/state")
    def session_state(
        session: SessionRecord = session_dependency,
    ) -> dict[str, object]:
        checkpoint = repository.latest_checkpoint(session.id)
        if checkpoint is None:
            raise HTTPException(status_code=404, detail="state not found")
        return public_state(checkpoint.state_payload)

    @app.post("/sessions/{session_id}/photos", status_code=status.HTTP_202_ACCEPTED)
    async def upload_photo(
        file: Annotated[UploadFile, File()],
        event_id: Annotated[str, Form(min_length=1)],
        session: SessionRecord = session_dependency,
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
        captured_at: Annotated[str | None, Form()] = None,
        latitude: Annotated[float | None, Form()] = None,
        longitude: Annotated[float | None, Form()] = None,
    ) -> dict[str, object]:
        del captured_at, latitude, longitude

        if not idempotency_key:
            raise HTTPException(
                status_code=422,
                detail="Idempotency-Key header is required",
            )

        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)

        image_path = uploads_dir / f"{uuid.uuid4()}_{file.filename}"

        with open(image_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        try:
            ai_result = classify_landmark(str(image_path))

            if isinstance(ai_result, str):
                try:
                    ai_result = json.loads(ai_result)
                except Exception:
                    ai_result = {
                        "landmark": "Unknown",
                        "description": ai_result,
                        "confidence": 0.5,
                    }

            recognition = repository.create_pending_recognition(
                session_id=session.id,
                request_event_id=event_id,
                idempotency_key=idempotency_key,
                file_name=file.filename or "upload",
                content_type=file.content_type,
                created_at=datetime.now(UTC),
            )

            # Broadcast the result to the LiveKit room
            try:
                from livekit import api as lk_api
                lk_client = lk_api.LiveKitAPI(
                    settings.livekit_url,
                    settings.livekit_api_key,
                    settings.livekit_api_secret
                )
                payload_data = json.dumps({
                    "type": "photo_recognition",
                    "landmark": ai_result.get("landmark", "Unknown"),
                    "description": ai_result.get("description", ""),
                    "confidence": ai_result.get("confidence", 0.0),
                }).encode('utf-8')
                await lk_client.room.send_data(
                    lk_api.SendDataRequest(
                        room=session.livekit_room,
                        data=payload_data,
                        kind=lk_api.DataPacket.Kind.RELIABLE,
                    )
                )
                await lk_client.close()
                print(f"[API] Broadcasted photo result to LiveKit room: {session.livekit_room}")
            except Exception as lk_err:
                print(f"[API] Failed to broadcast photo result: {lk_err}")

            return {
                "recognition_id": recognition.id,
                "status": "completed",
                "request_event_id": event_id,
                "landmark": ai_result.get("landmark"),
                "description": ai_result.get("description"),
                "confidence": ai_result.get("confidence"),
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image classification failed: {str(e)}",
            )

    @app.get("/sessions/{session_id}/recognitions/{recognition_id}")
    def recognition_status(
        recognition_id: str,
        session: SessionRecord = session_dependency,
    ) -> dict[str, object]:
        recognition = repository.get_recognition(
            session_id=session.id,
            recognition_id=recognition_id,
        )
        if recognition is None:
            raise HTTPException(status_code=404, detail="recognition not found")
        return _recognition_response(recognition)

    @app.get("/nearby-stops")
    def nearby_stops(
        session_id: Annotated[str, Query()],
        tour_slug: Annotated[str, Query()],
        latitude: Annotated[float, Query(ge=-90, le=90)],
        longitude: Annotated[float, Query(ge=-180, le=180)],
        authorization: Annotated[str | None, Header()] = None,
    ) -> dict[str, object]:
        _authenticate_session(
            session_id=session_id,
            authorization=authorization,
            repository=repository,
            settings=settings,
        )
        graph = load_giza_tour()
        if tour_slug != graph.slug:
            raise HTTPException(status_code=422, detail="unknown tour slug")

        stop_titles = {stop.slug: stop.title for stop in graph.stops}
        suggestions = []
        for stop_slug, (stop_lat, stop_lng) in GIZA_STOP_LOCATIONS.items():
            suggestions.append(
                {
                    "stop_slug": stop_slug,
                    "title": stop_titles.get(stop_slug, stop_slug),
                    "distance_meters": round(
                        _distance_meters(latitude, longitude, stop_lat, stop_lng)
                    ),
                    "kind": "suggestion",
                }
            )
        suggestions.sort(key=lambda item: int(item["distance_meters"]))
        return {"suggestions": suggestions[:5]}

    @app.post("/events", status_code=status.HTTP_202_ACCEPTED)
    def record_event(
        request: EventRequest,
        authorization: Annotated[str | None, Header()] = None,
    ) -> dict[str, object]:
        session = _authenticate_session(
            session_id=request.session_id,
            authorization=authorization,
            repository=repository,
            settings=settings,
        )
        created = repository.record_event(
            EvalEventRecord(
                id=f"evtlog_{request.event_id}",
                session_id=session.id,
                event_id=request.event_id,
                event_type=request.event_type,
                payload=request.payload,
                created_at=datetime.now(UTC),
            )
        )
        return {"accepted": True, "duplicate": not created}

    return app


def _authenticate_session(
    *,
    session_id: str,
    authorization: str | None,
    repository: AppRepository,
    settings: ApiSettings,
) -> SessionRecord:
    token = _bearer_token(authorization)
    guest_token_hash = hash_guest_token(token, secret=settings.guest_token_hash_secret)
    session = repository.get_session_by_token_hash(guest_token_hash)
    if session is None:
        raise HTTPException(status_code=401, detail="invalid guest credential")

    now = datetime.now(UTC)
    if session.expires_at <= now:
        raise HTTPException(status_code=401, detail="expired guest credential")
    if session.id != session_id:
        raise HTTPException(status_code=403, detail="guest/session mismatch")
    return session


def _bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="missing bearer credential")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="invalid bearer credential")
    return token


def _recognition_response(recognition: RecognitionRecord) -> dict[str, object]:
    if recognition.status == "pending":
        return {"recognition_id": recognition.id, "status": "pending"}
    if recognition.status == "failed":
        return {
            "recognition_id": recognition.id,
            "status": "failed",
            "error_code": recognition.error_code,
            "retryable": recognition.retryable,
        }

    result = recognition.result_payload or {}
    return {
        "recognition_id": recognition.id,
        "status": "completed",
        "confidence": recognition.confidence,
        "uncertainty_copy": result.get("uncertainty_copy"),
        "recognition_summary": result.get("recognition_summary"),
        "source_refs": result.get("source_refs", []),
    }


def _distance_meters(
    latitude: float,
    longitude: float,
    stop_latitude: float,
    stop_longitude: float,
) -> float:
    earth_radius_meters = 6_371_000
    lat1 = radians(latitude)
    lat2 = radians(stop_latitude)
    delta_lat = radians(stop_latitude - latitude)
    delta_lon = radians(stop_longitude - longitude)
    a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 2 * earth_radius_meters * asin(sqrt(a))


app = create_app()
