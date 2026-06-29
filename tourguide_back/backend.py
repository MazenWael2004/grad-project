from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from livekit import api as livekit_api

from content import load_giza_tour
from tour_state import ActiveMode, TourState


@dataclass(frozen=True)
class ApiSettings:
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    guest_token_hash_secret: str
    livekit_agent_name: str = "my-agent"
    guest_session_ttl: timedelta = timedelta(hours=4)
    livekit_token_ttl: timedelta = timedelta(minutes=15)
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    cors_allow_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    )

    @classmethod
    def from_env(cls) -> ApiSettings:
        load_dotenv(".env.local")
        livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", "")
        return cls(
            livekit_url=os.getenv("LIVEKIT_URL", ""),
            livekit_api_key=os.getenv("LIVEKIT_API_KEY", ""),
            livekit_api_secret=livekit_api_secret,
            livekit_agent_name=os.getenv("LIVEKIT_AGENT_NAME")
            or os.getenv("AGENT_NAME", "my-agent"),
            guest_token_hash_secret=os.getenv(
                "GUEST_TOKEN_HASH_SECRET", livekit_api_secret
            ),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
            cors_allow_origins=_csv_env(
                "CORS_ALLOW_ORIGINS",
                ("http://localhost:3000", "http://127.0.0.1:3000"),
            ),
        )


@dataclass(frozen=True)
class SessionRecord:
    id: str
    owner_subject: str
    guest_token_hash: str
    tour_slug: str
    language: str
    livekit_room: str
    participant_identity: str
    expires_at: datetime
    created_at: datetime


@dataclass(frozen=True)
class CheckpointRecord:
    id: str
    session_id: str
    event_id: str
    event_type: str
    state_version: int
    state_payload: dict[str, object]
    created_at: datetime


@dataclass(frozen=True)
class RecognitionRecord:
    id: str
    session_id: str
    request_event_id: str
    idempotency_key: str
    status: str
    file_name: str
    content_type: str | None
    confidence: float | None = None
    result_payload: dict[str, object] | None = None
    error_code: str | None = None
    retryable: bool | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass(frozen=True)
class EvalEventRecord:
    id: str
    session_id: str
    event_id: str
    event_type: str
    payload: dict[str, object]
    created_at: datetime


@dataclass(frozen=True)
class LiveKitJoinToken:
    url: str
    room_name: str
    participant_identity: str
    participant_token: str
    expires_at: datetime


class AppRepository(Protocol):
    def create_session(
        self, session: SessionRecord, checkpoint: CheckpointRecord
    ) -> None: ...

    def get_session(self, session_id: str) -> SessionRecord | None: ...

    def get_session_by_token_hash(
        self, guest_token_hash: str
    ) -> SessionRecord | None: ...

    def latest_checkpoint(self, session_id: str) -> CheckpointRecord | None: ...

    def create_pending_recognition(
        self,
        *,
        session_id: str,
        request_event_id: str,
        idempotency_key: str,
        file_name: str,
        content_type: str | None,
        created_at: datetime,
    ) -> RecognitionRecord: ...

    def get_recognition(
        self, *, session_id: str, recognition_id: str
    ) -> RecognitionRecord | None: ...

    def record_event(self, event: EvalEventRecord) -> bool:
        """Return False when the event ID was already recorded."""


class InMemoryAppRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}
        self._token_hash_to_session_id: dict[str, str] = {}
        self._checkpoints: dict[str, list[CheckpointRecord]] = {}
        self._recognitions: dict[str, RecognitionRecord] = {}
        self._recognition_by_event: dict[tuple[str, str, str], str] = {}
        self._event_ids: set[tuple[str, str]] = set()

    def create_session(
        self, session: SessionRecord, checkpoint: CheckpointRecord
    ) -> None:
        self._sessions[session.id] = session
        self._token_hash_to_session_id[session.guest_token_hash] = session.id
        self._checkpoints.setdefault(session.id, []).append(checkpoint)

    def get_session(self, session_id: str) -> SessionRecord | None:
        return self._sessions.get(session_id)

    def get_session_by_token_hash(self, guest_token_hash: str) -> SessionRecord | None:
        session_id = self._token_hash_to_session_id.get(guest_token_hash)
        if session_id is None:
            return None
        return self.get_session(session_id)

    def latest_checkpoint(self, session_id: str) -> CheckpointRecord | None:
        checkpoints = self._checkpoints.get(session_id, [])
        if not checkpoints:
            return None
        return checkpoints[-1]

    def create_pending_recognition(
        self,
        *,
        session_id: str,
        request_event_id: str,
        idempotency_key: str,
        file_name: str,
        content_type: str | None,
        created_at: datetime,
    ) -> RecognitionRecord:
        key = (session_id, request_event_id, idempotency_key)
        existing_id = self._recognition_by_event.get(key)
        if existing_id is not None:
            return self._recognitions[existing_id]

        recognition = RecognitionRecord(
            id=_prefixed_id("rec"),
            session_id=session_id,
            request_event_id=request_event_id,
            idempotency_key=idempotency_key,
            status="pending",
            file_name=file_name,
            content_type=content_type,
            created_at=created_at,
        )
        self._recognitions[recognition.id] = recognition
        self._recognition_by_event[key] = recognition.id
        return recognition

    def get_recognition(
        self, *, session_id: str, recognition_id: str
    ) -> RecognitionRecord | None:
        recognition = self._recognitions.get(recognition_id)
        if recognition is None or recognition.session_id != session_id:
            return None
        return recognition

    def record_event(self, event: EvalEventRecord) -> bool:
        key = (event.session_id, event.event_id)
        if key in self._event_ids:
            return False
        self._event_ids.add(key)
        return True


class SupabaseRestRepository:
    def __init__(self, *, supabase_url: str, service_role_key: str) -> None:
        self._client = httpx.Client(
            base_url=f"{supabase_url.rstrip('/')}/rest/v1",
            headers={
                "apikey": service_role_key,
                "Authorization": f"Bearer {service_role_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            timeout=10,
        )

    def create_session(
        self, session: SessionRecord, checkpoint: CheckpointRecord
    ) -> None:
        self._post("sessions", _session_to_row(session))
        self._post("tour_state_checkpoints", _checkpoint_to_row(checkpoint))

    def get_session(self, session_id: str) -> SessionRecord | None:
        rows = self._get("sessions", {"id": f"eq.{session_id}", "limit": "1"})
        if not rows:
            return None
        return _session_from_row(rows[0])

    def get_session_by_token_hash(self, guest_token_hash: str) -> SessionRecord | None:
        rows = self._get(
            "sessions", {"guest_token_hash": f"eq.{guest_token_hash}", "limit": "1"}
        )
        if not rows:
            return None
        return _session_from_row(rows[0])

    def latest_checkpoint(self, session_id: str) -> CheckpointRecord | None:
        rows = self._get(
            "tour_state_checkpoints",
            {
                "session_id": f"eq.{session_id}",
                "order": "state_version.desc",
                "limit": "1",
            },
        )
        if not rows:
            return None
        return _checkpoint_from_row(rows[0])

    def create_pending_recognition(
        self,
        *,
        session_id: str,
        request_event_id: str,
        idempotency_key: str,
        file_name: str,
        content_type: str | None,
        created_at: datetime,
    ) -> RecognitionRecord:
        existing = self._get(
            "recognition_events",
            {
                "session_id": f"eq.{session_id}",
                "request_event_id": f"eq.{request_event_id}",
                "idempotency_key": f"eq.{idempotency_key}",
                "limit": "1",
            },
        )
        if existing:
            return _recognition_from_row(existing[0])

        recognition = RecognitionRecord(
            id=_prefixed_id("rec"),
            session_id=session_id,
            request_event_id=request_event_id,
            idempotency_key=idempotency_key,
            status="pending",
            file_name=file_name,
            content_type=content_type,
            created_at=created_at,
        )
        rows = self._post("recognition_events", _recognition_to_row(recognition))
        return _recognition_from_row(rows[0])

    def get_recognition(
        self, *, session_id: str, recognition_id: str
    ) -> RecognitionRecord | None:
        rows = self._get(
            "recognition_events",
            {
                "id": f"eq.{recognition_id}",
                "session_id": f"eq.{session_id}",
                "limit": "1",
            },
        )
        if not rows:
            return None
        return _recognition_from_row(rows[0])

    def record_event(self, event: EvalEventRecord) -> bool:
        existing = self._get(
            "eval_events",
            {
                "session_id": f"eq.{event.session_id}",
                "event_id": f"eq.{event.event_id}",
                "limit": "1",
            },
        )
        if existing:
            return False
        self._post("eval_events", _event_to_row(event))
        return True

    def _get(self, table: str, params: Mapping[str, str]) -> list[dict[str, Any]]:
        response = self._client.get(f"/{table}", params=params)
        response.raise_for_status()
        return list(response.json())

    def _post(self, table: str, payload: Mapping[str, object]) -> list[dict[str, Any]]:
        response = self._client.post(f"/{table}", json=payload)
        response.raise_for_status()
        return list(response.json())


class LiveKitTokenIssuer(Protocol):
    def issue(self, *, session: SessionRecord) -> LiveKitJoinToken: ...


class LiveKitAccessTokenIssuer:
    def __init__(self, settings: ApiSettings) -> None:
        self.settings = settings

    def issue(self, *, session: SessionRecord) -> LiveKitJoinToken:
        expires_at = datetime.now(UTC) + self.settings.livekit_token_ttl
        binding = {
            "session_id": session.id,
            "owner_subject": session.owner_subject,
            "room_name": session.livekit_room,
            "participant_identity": session.participant_identity,
            "tour_slug": session.tour_slug,
        }
        metadata = json.dumps(binding, separators=(",", ":"))
        token = (
            livekit_api.AccessToken(
                self.settings.livekit_api_key,
                self.settings.livekit_api_secret,
            )
            .with_identity(session.participant_identity)
            .with_name("AI Tour Guide Guest")
            .with_metadata(metadata)
            .with_attributes(binding)
            .with_ttl(self.settings.livekit_token_ttl)
            .with_grants(
                livekit_api.VideoGrants(
                    room_join=True,
                    room=session.livekit_room,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True,
                    can_publish_sources=["microphone"],
                )
            )
            .with_room_config(
                livekit_api.RoomConfiguration(
                    agents=[
                        livekit_api.RoomAgentDispatch(
                            agent_name=self.settings.livekit_agent_name,
                            metadata=metadata,
                        )
                    ]
                )
            )
            .to_jwt()
        )
        return LiveKitJoinToken(
            url=self.settings.livekit_url,
            room_name=session.livekit_room,
            participant_identity=session.participant_identity,
            participant_token=token,
            expires_at=expires_at,
        )


def repository_from_settings(settings: ApiSettings) -> AppRepository:
    if settings.supabase_url and settings.supabase_service_role_key:
        return SupabaseRestRepository(
            supabase_url=settings.supabase_url,
            service_role_key=settings.supabase_service_role_key,
        )
    return InMemoryAppRepository()


def create_session_record(
    *,
    tour_slug: str,
    language: str,
    settings: ApiSettings,
    now: datetime,
) -> tuple[SessionRecord, CheckpointRecord, str]:
    session_id = _prefixed_id("sess")
    owner_subject = _prefixed_id("owner")
    guest_token = f"gst_{secrets.token_urlsafe(32)}"
    guest_token_hash = hash_guest_token(
        guest_token, secret=settings.guest_token_hash_secret
    )
    session = SessionRecord(
        id=session_id,
        owner_subject=owner_subject,
        guest_token_hash=guest_token_hash,
        tour_slug=tour_slug,
        language=language,
        livekit_room=f"tour_{session_id}",
        participant_identity=f"guest_{owner_subject.removeprefix('owner_')[:16]}",
        expires_at=now + settings.guest_session_ttl,
        created_at=now,
    )
    checkpoint = CheckpointRecord(
        id=_prefixed_id("chk"),
        session_id=session_id,
        event_id=_prefixed_id("evt"),
        event_type="session_created",
        state_version=0,
        state_payload=initial_state_payload(tour_slug=tour_slug, language=language),
        created_at=now,
    )
    return session, checkpoint, guest_token


def initial_state_payload(*, tour_slug: str, language: str) -> dict[str, object]:
    graph = load_giza_tour()
    if tour_slug != graph.slug:
        raise ValueError(f"unknown tour slug: {tour_slug}")
    first_beat = graph.first_beat()
    return TourState(
        tour_slug=tour_slug,
        language=language,
        active_mode=ActiveMode.NOT_STARTED,
        state_version=0,
        current_stop_slug=first_beat.stop_slug,
        current_topic=first_beat.topic,
        current_beat_slug=first_beat.slug,
    ).to_dict()


def public_state(state_payload: Mapping[str, object]) -> dict[str, object]:
    return {
        "state_version": int(state_payload["state_version"]),
        "active_mode": str(state_payload["active_mode"]),
        "current_beat_id": state_payload.get("current_beat_slug"),
        "safe_anchor": state_payload.get("safe_anchor"),
    }


def hash_guest_token(token: str, *, secret: str) -> str:
    return hmac.new(secret.encode(), token.encode(), hashlib.sha256).hexdigest()


def verify_guest_token(token: str, token_hash: str, *, secret: str) -> bool:
    return hmac.compare_digest(hash_guest_token(token, secret=secret), token_hash)


def _csv_env(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    values = tuple(item.strip() for item in raw_value.split(",") if item.strip())
    return values or default


def _prefixed_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _datetime_to_json(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(UTC).isoformat()


def _datetime_from_json(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _session_to_row(session: SessionRecord) -> dict[str, object]:
    return {
        "id": session.id,
        "owner_subject": session.owner_subject,
        "guest_token_hash": session.guest_token_hash,
        "tour_slug": session.tour_slug,
        "language": session.language,
        "livekit_room": session.livekit_room,
        "participant_identity": session.participant_identity,
        "expires_at": _datetime_to_json(session.expires_at),
        "created_at": _datetime_to_json(session.created_at),
    }


def _session_from_row(row: Mapping[str, object]) -> SessionRecord:
    return SessionRecord(
        id=str(row["id"]),
        owner_subject=str(row["owner_subject"]),
        guest_token_hash=str(row["guest_token_hash"]),
        tour_slug=str(row["tour_slug"]),
        language=str(row["language"]),
        livekit_room=str(row["livekit_room"]),
        participant_identity=str(row["participant_identity"]),
        expires_at=_datetime_from_json(row["expires_at"]),
        created_at=_datetime_from_json(row["created_at"]),
    )


def _checkpoint_to_row(checkpoint: CheckpointRecord) -> dict[str, object]:
    state_payload = checkpoint.state_payload
    return {
        "id": checkpoint.id,
        "session_id": checkpoint.session_id,
        "event_id": checkpoint.event_id,
        "event_type": checkpoint.event_type,
        "state_version": checkpoint.state_version,
        "active_mode": state_payload.get("active_mode"),
        "current_beat_id": state_payload.get("current_beat_slug"),
        "safe_anchor": state_payload.get("safe_anchor"),
        "state_payload": state_payload,
        "created_at": _datetime_to_json(checkpoint.created_at),
    }


def _checkpoint_from_row(row: Mapping[str, object]) -> CheckpointRecord:
    payload = row.get("state_payload")
    if not isinstance(payload, dict):
        payload = {}
    return CheckpointRecord(
        id=str(row["id"]),
        session_id=str(row["session_id"]),
        event_id=str(row["event_id"]),
        event_type=str(row["event_type"]),
        state_version=int(row["state_version"]),
        state_payload=dict(payload),
        created_at=_datetime_from_json(row["created_at"]),
    )


def _recognition_to_row(recognition: RecognitionRecord) -> dict[str, object]:
    return {
        "id": recognition.id,
        "session_id": recognition.session_id,
        "request_event_id": recognition.request_event_id,
        "idempotency_key": recognition.idempotency_key,
        "status": recognition.status,
        "file_name": recognition.file_name,
        "content_type": recognition.content_type,
        "confidence": recognition.confidence,
        "result_payload": recognition.result_payload,
        "error_code": recognition.error_code,
        "retryable": recognition.retryable,
        "created_at": _datetime_to_json(recognition.created_at),
        "completed_at": _datetime_to_json(recognition.completed_at),
    }


def _recognition_from_row(row: Mapping[str, object]) -> RecognitionRecord:
    payload = row.get("result_payload")
    return RecognitionRecord(
        id=str(row["id"]),
        session_id=str(row["session_id"]),
        request_event_id=str(row["request_event_id"]),
        idempotency_key=str(row["idempotency_key"]),
        status=str(row["status"]),
        file_name=str(row["file_name"]),
        content_type=str(row["content_type"]) if row.get("content_type") else None,
        confidence=float(row["confidence"]) if row.get("confidence") else None,
        result_payload=dict(payload) if isinstance(payload, dict) else None,
        error_code=str(row["error_code"]) if row.get("error_code") else None,
        retryable=bool(row["retryable"]) if row.get("retryable") is not None else None,
        created_at=(
            _datetime_from_json(row["created_at"]) if row.get("created_at") else None
        ),
        completed_at=(
            _datetime_from_json(row["completed_at"])
            if row.get("completed_at")
            else None
        ),
    )


def _event_to_row(event: EvalEventRecord) -> dict[str, object]:
    return {
        "id": event.id,
        "session_id": event.session_id,
        "event_id": event.event_id,
        "event_type": event.event_type,
        "payload": event.payload,
        "created_at": _datetime_to_json(event.created_at),
    }