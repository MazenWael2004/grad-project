from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Protocol

from content import TourGraph, load_giza_tour


class ActiveMode(Enum):
    NOT_STARTED = "not_started"
    NARRATING = "narrating"
    ANSWERING = "answering"
    ENDED = "ended"


class ResumePolicy(Enum):
    START_NEXT_BEAT = "start_next_beat"
    RESUME_FROM_ANCHOR = "resume_from_anchor"


class RouteAction(Enum):
    RESUME = "resume"
    SKIP = "skip"
    SWITCH_TOPIC = "switch_topic"
    ANSWER_QUESTION = "answer_question"
    GO_DEEPER = "go_deeper"
    SIMPLIFY = "simplify"
    PHOTO_EXPLANATION = "photo_explanation"


class TourStateError(ValueError):
    pass


class StaleStateVersionError(TourStateError):
    pass


class IllegalTransitionError(TourStateError):
    pass


StaleStateVersion = StaleStateVersionError
IllegalTransition = IllegalTransitionError


@dataclass(frozen=True)
class SafeAnchor:
    beat_slug: str
    anchor_id: str
    summary: str

    def to_dict(self) -> dict[str, str]:
        return {
            "beat_slug": self.beat_slug,
            "anchor_id": self.anchor_id,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> SafeAnchor:
        return cls(
            beat_slug=str(value["beat_slug"]),
            anchor_id=str(value["anchor_id"]),
            summary=str(value["summary"]),
        )


@dataclass(frozen=True)
class TourState:
    tour_slug: str
    language: str
    active_mode: ActiveMode
    state_version: int
    current_stop_slug: str | None = None
    current_topic: str | None = None
    current_beat_slug: str | None = None
    safe_anchor: SafeAnchor | None = None
    completed_beats: tuple[str, ...] = ()
    skipped_topics: tuple[str, ...] = ()
    return_later_topics: tuple[str, ...] = ()
    recent_recognition_ids: tuple[str, ...] = ()
    last_user_question: str | None = None
    resume_policy: ResumePolicy = ResumePolicy.START_NEXT_BEAT
    applied_event_ids: tuple[str, ...] = ()
    prefetched_next_beat_slug: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "tour_slug": self.tour_slug,
            "language": self.language,
            "active_mode": self.active_mode.value,
            "state_version": self.state_version,
            "current_stop_slug": self.current_stop_slug,
            "current_topic": self.current_topic,
            "current_beat_slug": self.current_beat_slug,
            "safe_anchor": self.safe_anchor.to_dict() if self.safe_anchor else None,
            "completed_beats": list(self.completed_beats),
            "skipped_topics": list(self.skipped_topics),
            "return_later_topics": list(self.return_later_topics),
            "recent_recognition_ids": list(self.recent_recognition_ids),
            "last_user_question": self.last_user_question,
            "resume_policy": self.resume_policy.value,
            "applied_event_ids": list(self.applied_event_ids),
            "prefetched_next_beat_slug": self.prefetched_next_beat_slug,
        }

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> TourState:
        safe_anchor = value.get("safe_anchor")
        return cls(
            tour_slug=str(value["tour_slug"]),
            language=str(value["language"]),
            active_mode=ActiveMode(str(value["active_mode"])),
            state_version=int(value["state_version"]),
            current_stop_slug=_optional_str(value.get("current_stop_slug")),
            current_topic=_optional_str(value.get("current_topic")),
            current_beat_slug=_optional_str(value.get("current_beat_slug")),
            safe_anchor=(
                SafeAnchor.from_dict(safe_anchor)
                if isinstance(safe_anchor, dict)
                else None
            ),
            completed_beats=tuple(str(item) for item in value["completed_beats"]),
            skipped_topics=tuple(str(item) for item in value["skipped_topics"]),
            return_later_topics=tuple(
                str(item) for item in value["return_later_topics"]
            ),
            recent_recognition_ids=tuple(
                str(item) for item in value["recent_recognition_ids"]
            ),
            last_user_question=_optional_str(value.get("last_user_question")),
            resume_policy=ResumePolicy(str(value["resume_policy"])),
            applied_event_ids=tuple(str(item) for item in value["applied_event_ids"]),
            prefetched_next_beat_slug=_optional_str(
                value.get("prefetched_next_beat_slug")
            ),
        )


@dataclass(frozen=True)
class RouteActionProposal:
    action: RouteAction
    event_id: str
    expected_state_version: int
    target_topic: str | None = None
    prompt: str | None = None
    recognition_id: str | None = None


@dataclass(frozen=True)
class TransitionResult:
    applied: bool
    reason: str
    state: TourState


@dataclass(frozen=True)
class Checkpoint:
    session_id: str
    event_id: str
    event_type: str
    state_version: int
    state_payload: dict[str, object]


class CheckpointStore(Protocol):
    def append(self, checkpoint: Checkpoint) -> bool:
        """Append a checkpoint, returning False for a duplicate event."""

    def latest(self, session_id: str) -> Checkpoint | None:
        """Return the latest checkpoint for a session."""


class InMemoryCheckpointStore:
    def __init__(self) -> None:
        self._checkpoints: dict[str, list[Checkpoint]] = {}
        self._event_ids: dict[str, set[str]] = {}

    def append(self, checkpoint: Checkpoint) -> bool:
        event_ids = self._event_ids.setdefault(checkpoint.session_id, set())
        if checkpoint.event_id in event_ids:
            return False

        latest = self.latest(checkpoint.session_id)
        if latest is not None and checkpoint.state_version <= latest.state_version:
            raise StaleStateVersion(
                "checkpoint version must be greater than the latest version"
            )

        event_ids.add(checkpoint.event_id)
        self._checkpoints.setdefault(checkpoint.session_id, []).append(checkpoint)
        return True

    def latest(self, session_id: str) -> Checkpoint | None:
        checkpoints = self._checkpoints.get(session_id, [])
        if not checkpoints:
            return None
        return checkpoints[-1]


class TourController:
    def __init__(
        self,
        *,
        session_id: str,
        graph: TourGraph,
        store: CheckpointStore,
        state: TourState,
    ) -> None:
        self.session_id = session_id
        self.graph = graph
        self.store = store
        self.state = state

    @classmethod
    def for_giza(
        cls, *, session_id: str, store: CheckpointStore, language: str
    ) -> TourController:
        graph = load_giza_tour()
        return cls(
            session_id=session_id,
            graph=graph,
            store=store,
            state=TourState(
                tour_slug=graph.slug,
                language=language,
                active_mode=ActiveMode.NOT_STARTED,
                state_version=0,
            ),
        )

    @classmethod
    def restore_giza(cls, *, session_id: str, store: CheckpointStore) -> TourController:
        graph = load_giza_tour()
        checkpoint = store.latest(session_id)
        if checkpoint is None:
            return cls.for_giza(session_id=session_id, store=store, language="en")
        return cls(
            session_id=session_id,
            graph=graph,
            store=store,
            state=TourState.from_dict(checkpoint.state_payload),
        )

    def start_tour(self, *, event_id: str) -> TransitionResult:
        if self._is_duplicate(event_id):
            return self._duplicate_result()
        if self.state.active_mode is not ActiveMode.NOT_STARTED:
            raise IllegalTransition("tour has already started")

        first_beat = self.graph.first_beat()
        new_state = replace(
            self.state,
            active_mode=ActiveMode.NARRATING,
            state_version=self.state.state_version + 1,
            current_stop_slug=first_beat.stop_slug,
            current_topic=first_beat.topic,
            current_beat_slug=first_beat.slug,
            safe_anchor=_anchor_for(first_beat.slug, first_beat.topic),
            resume_policy=ResumePolicy.START_NEXT_BEAT,
            applied_event_ids=_append_unique(self.state.applied_event_ids, event_id),
            prefetched_next_beat_slug=self.graph.next_beat_slug(first_beat.slug),
        )
        return self._commit(event_id, "start_tour", new_state)

    def record_speech_outcome(
        self,
        *,
        event_id: str,
        expected_state_version: int,
        interrupted: bool,
    ) -> TransitionResult:
        if self.state.active_mode is not ActiveMode.NARRATING:
            raise IllegalTransition("speech completion is only valid while narrating")
        self._validate_state_version(expected_state_version)
        if self._is_duplicate(event_id):
            return self._duplicate_result()
        if interrupted:
            return TransitionResult(False, "interrupted", self.state)

        current_beat_slug = self._require_current_beat_slug()
        next_beat_slug = self.graph.next_beat_slug(current_beat_slug)
        completed_beats = _append_unique(self.state.completed_beats, current_beat_slug)

        if next_beat_slug is None:
            new_state = replace(
                self.state,
                active_mode=ActiveMode.ENDED,
                state_version=self.state.state_version + 1,
                completed_beats=completed_beats,
                applied_event_ids=_append_unique(
                    self.state.applied_event_ids, event_id
                ),
                prefetched_next_beat_slug=None,
            )
        else:
            next_beat = self.graph.beat(next_beat_slug)
            new_state = replace(
                self.state,
                state_version=self.state.state_version + 1,
                current_stop_slug=next_beat.stop_slug,
                current_topic=next_beat.topic,
                current_beat_slug=next_beat.slug,
                safe_anchor=_anchor_for(next_beat.slug, next_beat.topic),
                completed_beats=completed_beats,
                resume_policy=ResumePolicy.START_NEXT_BEAT,
                applied_event_ids=_append_unique(
                    self.state.applied_event_ids, event_id
                ),
                prefetched_next_beat_slug=self.graph.next_beat_slug(next_beat.slug),
            )
        return self._commit(event_id, "speech_completed", new_state)

    def apply_proposal(self, proposal: RouteActionProposal) -> TransitionResult:
        if self.state.active_mode is ActiveMode.NOT_STARTED:
            raise IllegalTransition("route proposals require an active tour")
        self._validate_state_version(proposal.expected_state_version)
        if self._is_duplicate(proposal.event_id):
            return self._duplicate_result()

        if proposal.action is RouteAction.RESUME:
            new_state = replace(
                self.state,
                active_mode=ActiveMode.NARRATING,
                state_version=self.state.state_version + 1,
                resume_policy=ResumePolicy.RESUME_FROM_ANCHOR,
                applied_event_ids=_append_unique(
                    self.state.applied_event_ids, proposal.event_id
                ),
            )
            return self._commit(proposal.event_id, proposal.action.value, new_state)

        if proposal.action is RouteAction.SKIP:
            return self._skip_current_topic(proposal)

        if proposal.action is RouteAction.SWITCH_TOPIC:
            return self._switch_topic(proposal)

        if proposal.action in {
            RouteAction.ANSWER_QUESTION,
            RouteAction.GO_DEEPER,
            RouteAction.SIMPLIFY,
        }:
            return self._answer_at_anchor(proposal)

        if proposal.action is RouteAction.PHOTO_EXPLANATION:
            return self._explain_photo(proposal)

        raise IllegalTransition(f"unsupported route action: {proposal.action.value}")

    def current_response_packet(self) -> dict[str, object]:
        current_beat_slug = self._require_current_beat_slug()
        current_beat = self.graph.beat(current_beat_slug)
        next_beat_slug = self.graph.next_beat_slug(current_beat_slug)
        return {
            "tour_slug": self.state.tour_slug,
            "language": self.state.language,
            "state_version": self.state.state_version,
            "active_mode": self.state.active_mode.value,
            "current_beat": current_beat.to_packet(language=self.state.language),
            "safe_anchor": (
                self.state.safe_anchor.to_dict() if self.state.safe_anchor else None
            ),
            "allowed_actions": [action.value for action in RouteAction],
            "prefetched_next_beat": (
                self.graph.beat(next_beat_slug).to_packet(language=self.state.language)
                if next_beat_slug
                else None
            ),
        }

    def _skip_current_topic(self, proposal: RouteActionProposal) -> TransitionResult:
        current_beat_slug = self._require_current_beat_slug()
        next_beat_slug = self.graph.next_beat_slug(current_beat_slug)
        skipped_topics = _append_unique(
            self.state.skipped_topics, self._require_current_topic()
        )

        if next_beat_slug is None:
            new_state = replace(
                self.state,
                active_mode=ActiveMode.ENDED,
                state_version=self.state.state_version + 1,
                skipped_topics=skipped_topics,
                applied_event_ids=_append_unique(
                    self.state.applied_event_ids, proposal.event_id
                ),
                prefetched_next_beat_slug=None,
            )
        else:
            next_beat = self.graph.beat(next_beat_slug)
            new_state = replace(
                self.state,
                active_mode=ActiveMode.NARRATING,
                state_version=self.state.state_version + 1,
                current_stop_slug=next_beat.stop_slug,
                current_topic=next_beat.topic,
                current_beat_slug=next_beat.slug,
                safe_anchor=_anchor_for(next_beat.slug, next_beat.topic),
                skipped_topics=skipped_topics,
                resume_policy=ResumePolicy.START_NEXT_BEAT,
                applied_event_ids=_append_unique(
                    self.state.applied_event_ids, proposal.event_id
                ),
                prefetched_next_beat_slug=self.graph.next_beat_slug(next_beat.slug),
            )
        return self._commit(proposal.event_id, proposal.action.value, new_state)

    def _switch_topic(self, proposal: RouteActionProposal) -> TransitionResult:
        if proposal.target_topic is None:
            raise IllegalTransition("switch_topic requires target_topic")
        target_beat = self.graph.beat_for_topic(proposal.target_topic)
        if target_beat is None:
            raise IllegalTransition(f"unknown topic: {proposal.target_topic}")

        return_later_topics = self.state.return_later_topics
        current_topic = self._require_current_topic()
        if current_topic != target_beat.topic:
            return_later_topics = _append_unique(return_later_topics, current_topic)

        new_state = replace(
            self.state,
            active_mode=ActiveMode.NARRATING,
            state_version=self.state.state_version + 1,
            current_stop_slug=target_beat.stop_slug,
            current_topic=target_beat.topic,
            current_beat_slug=target_beat.slug,
            safe_anchor=_anchor_for(target_beat.slug, target_beat.topic),
            return_later_topics=return_later_topics,
            resume_policy=ResumePolicy.START_NEXT_BEAT,
            applied_event_ids=_append_unique(
                self.state.applied_event_ids, proposal.event_id
            ),
            prefetched_next_beat_slug=self.graph.next_beat_slug(target_beat.slug),
        )
        return self._commit(proposal.event_id, proposal.action.value, new_state)

    def _answer_at_anchor(self, proposal: RouteActionProposal) -> TransitionResult:
        return_later_topics = self.state.return_later_topics
        if proposal.action is RouteAction.GO_DEEPER:
            return_later_topics = _append_unique(
                return_later_topics, self._require_current_topic()
            )

        new_state = replace(
            self.state,
            active_mode=ActiveMode.ANSWERING,
            state_version=self.state.state_version + 1,
            return_later_topics=return_later_topics,
            last_user_question=proposal.prompt,
            resume_policy=ResumePolicy.RESUME_FROM_ANCHOR,
            applied_event_ids=_append_unique(
                self.state.applied_event_ids, proposal.event_id
            ),
        )
        return self._commit(proposal.event_id, proposal.action.value, new_state)

    def _explain_photo(self, proposal: RouteActionProposal) -> TransitionResult:
        if proposal.recognition_id is None:
            raise IllegalTransition("photo_explanation requires recognition_id")

        new_state = replace(
            self.state,
            active_mode=ActiveMode.ANSWERING,
            state_version=self.state.state_version + 1,
            recent_recognition_ids=_append_unique(
                self.state.recent_recognition_ids, proposal.recognition_id
            ),
            resume_policy=ResumePolicy.RESUME_FROM_ANCHOR,
            applied_event_ids=_append_unique(
                self.state.applied_event_ids, proposal.event_id
            ),
        )
        return self._commit(proposal.event_id, proposal.action.value, new_state)

    def _commit(
        self, event_id: str, event_type: str, new_state: TourState
    ) -> TransitionResult:
        checkpoint = Checkpoint(
            session_id=self.session_id,
            event_id=event_id,
            event_type=event_type,
            state_version=new_state.state_version,
            state_payload=new_state.to_dict(),
        )
        if not self.store.append(checkpoint):
            return self._duplicate_result()
        self.state = new_state
        return TransitionResult(True, event_type, self.state)

    def _validate_state_version(self, expected_state_version: int) -> None:
        if expected_state_version != self.state.state_version:
            raise StaleStateVersion(
                f"expected version {expected_state_version}, "
                f"current version {self.state.state_version}"
            )

    def _is_duplicate(self, event_id: str) -> bool:
        return event_id in self.state.applied_event_ids

    def _duplicate_result(self) -> TransitionResult:
        return TransitionResult(False, "duplicate_event", self.state)

    def _require_current_beat_slug(self) -> str:
        if self.state.current_beat_slug is None:
            raise IllegalTransition("current beat is not set")
        return self.state.current_beat_slug

    def _require_current_topic(self) -> str:
        if self.state.current_topic is None:
            raise IllegalTransition("current topic is not set")
        return self.state.current_topic


def _anchor_for(beat_slug: str, topic: str) -> SafeAnchor:
    return SafeAnchor(
        beat_slug=beat_slug,
        anchor_id=f"{beat_slug}:start",
        summary=f"Resume the {topic} beat from its current safe opening anchor.",
    )


def _append_unique(values: tuple[str, ...], value: str) -> tuple[str, ...]:
    if value in values:
        return values
    return (*values, value)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
