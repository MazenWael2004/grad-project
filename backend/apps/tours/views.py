import os
import logging
from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
from typing import Literal

from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .content import load_giza_tour
from .backend import (
    ApiSettings,
    DjangoAppRepository,
    LiveKitAccessTokenIssuer,
    create_session_record,
    hash_guest_token,
    public_state,
    SessionRecord,
    RecognitionRecord,
    EvalEventRecord,
)

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {"en", "ar-EG"}
GIZA_STOP_LOCATIONS = {
    "khufu": (29.9792, 31.1342),
    "khafre": (29.9761, 31.1307),
    "menkaure": (29.9725, 31.1283),
    "sphinx": (29.9753, 31.1376),
    "arrival": (29.9784, 31.1329),
}


def authenticate_session(request, session_id: str) -> SessionRecord:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AuthenticationFailed("missing bearer credential")
    
    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationFailed("invalid bearer credential")
    
    token = parts[1]
    settings = ApiSettings.from_settings()
    guest_token_hash = hash_guest_token(token, secret=settings.guest_token_hash_secret)
    
    repository = DjangoAppRepository()
    session = repository.get_session_by_token_hash(guest_token_hash)
    if session is None:
        raise AuthenticationFailed("invalid guest credential")
    
    now = datetime.now(timezone.utc)
    # Convert session.expires_at to offset-aware if it's naive
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        raise AuthenticationFailed("expired guest credential")
    
    if session.id != session_id:
        raise PermissionDenied("guest/session mismatch")
    
    return session


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


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


class ToursListView(APIView):
    def get(self, request):
        graph = load_giza_tour()
        return Response({
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
        })


class CreateSessionView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        tour_slug = request.data.get("tour_slug")
        language = request.data.get("language", "en")

        if not tour_slug:
            raise ValidationError("tour_slug is required")
        if language not in SUPPORTED_LANGUAGES:
            raise ValidationError("unsupported language")

        settings = ApiSettings.from_settings()
        repository = DjangoAppRepository()
        now = datetime.now(timezone.utc)

        try:
            session, checkpoint, guest_token = create_session_record(
                tour_slug=tour_slug,
                language=language,
                settings=settings,
                now=now,
            )
        except ValueError as exc:
            raise ValidationError(str(exc))

        repository.create_session(session, checkpoint)
        return Response(
            {
                "session_id": session.id,
                "guest_session_token": guest_token,
                "expires_at": session.expires_at.isoformat(),
                "initial_state": public_state(checkpoint.state_payload),
            },
            status=status.HTTP_201_CREATED,
        )


class LiveKitTokenView(APIView):
    def post(self, request, session_id):
        session = authenticate_session(request, session_id)
        settings = ApiSettings.from_settings()
        token_issuer = LiveKitAccessTokenIssuer(settings)

        join_token = token_issuer.issue(session=session)
        return Response({
            "url": join_token.url,
            "room_name": join_token.room_name,
            "participant_identity": join_token.participant_identity,
            "participant_token": join_token.participant_token,
            "expires_at": join_token.expires_at.isoformat(),
        })


class SessionStateView(APIView):
    def get(self, request, session_id):
        session = authenticate_session(request, session_id)
        repository = DjangoAppRepository()
        checkpoint = repository.latest_checkpoint(session.id)
        if checkpoint is None:
            return Response({"detail": "state not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(public_state(checkpoint.state_payload))


class UploadPhotoView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, session_id):
        session = authenticate_session(request, session_id)
        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            raise ValidationError("Idempotency-Key header is required")

        file_obj = request.FILES.get("file")
        if not file_obj:
            raise ValidationError("file is required")

        event_id = request.data.get("event_id")
        if not event_id or len(event_id.strip()) == 0:
            raise ValidationError("event_id is required")

        repository = DjangoAppRepository()
        recognition = repository.create_pending_recognition(
            session_id=session.id,
            request_event_id=event_id,
            idempotency_key=idempotency_key,
            file_name=file_obj.name or "upload",
            content_type=file_obj.content_type,
            created_at=datetime.now(timezone.utc),
        )
        return Response(
            {
                "recognition_id": recognition.id,
                "status": recognition.status,
                "request_event_id": recognition.request_event_id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class RecognitionStatusView(APIView):
    def get(self, request, session_id, recognition_id):
        session = authenticate_session(request, session_id)
        repository = DjangoAppRepository()
        recognition = repository.get_recognition(
            session_id=session.id,
            recognition_id=recognition_id,
        )
        if recognition is None:
            return Response({"detail": "recognition not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_recognition_response(recognition))


class NearbyStopsView(APIView):
    def get(self, request):
        session_id = request.query_params.get("session_id")
        tour_slug = request.query_params.get("tour_slug")
        latitude_str = request.query_params.get("latitude")
        longitude_str = request.query_params.get("longitude")

        if not session_id or not tour_slug or not latitude_str or not longitude_str:
            raise ValidationError("session_id, tour_slug, latitude, and longitude are required query params")

        try:
            latitude = float(latitude_str)
            longitude = float(longitude_str)
        except ValueError:
            raise ValidationError("latitude and longitude must be valid float values")

        if not (-90 <= latitude <= 90):
            raise ValidationError("latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValidationError("longitude must be between -180 and 180")

        # Authenticate session
        authenticate_session(request, session_id)

        graph = load_giza_tour()
        if tour_slug != graph.slug:
            raise ValidationError("unknown tour slug")

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
        return Response({"suggestions": suggestions[:5]})


class RecordEventView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        session_id = request.data.get("session_id")
        event_id = request.data.get("event_id")
        event_type = request.data.get("event_type")
        payload = request.data.get("payload", {})

        if not session_id or not event_id or not event_type:
            raise ValidationError("session_id, event_id, and event_type are required")

        session = authenticate_session(request, session_id)
        repository = DjangoAppRepository()

        created = repository.record_event(
            EvalEventRecord(
                id=f"evtlog_{event_id}",
                session_id=session.id,
                event_id=event_id,
                event_type=event_type,
                payload=payload,
                created_at=datetime.now(timezone.utc),
            )
        )
        return Response(
            {"accepted": True, "duplicate": not created},
            status=status.HTTP_202_ACCEPTED,
        )
