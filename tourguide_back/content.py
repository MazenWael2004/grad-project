from dataclasses import dataclass


@dataclass(frozen=True)
class TourBeat:
    slug: str
    stop_slug: str
    topic: str
    title: str
    content_en: str
    content_ar_eg: str
    source_ids: tuple[str, ...]
    review_status: str
    estimated_seconds: int

    def to_packet(self, *, language: str) -> dict[str, object]:
        content = self.content_ar_eg if language == "ar-EG" else self.content_en
        return {
            "slug": self.slug,
            "stop_slug": self.stop_slug,
            "topic": self.topic,
            "title": self.title,
            "content": content,
            "source_ids": list(self.source_ids),
            "review_status": self.review_status,
            "estimated_seconds": self.estimated_seconds,
        }


@dataclass(frozen=True)
class TourStop:
    slug: str
    title: str
    beat_slugs: tuple[str, ...]


@dataclass(frozen=True)
class TourGraph:
    slug: str
    stops: tuple[TourStop, ...]
    beats: tuple[TourBeat, ...]

    def __post_init__(self) -> None:
        beat_slugs = [beat.slug for beat in self.beats]
        if len(beat_slugs) != len(set(beat_slugs)):
            raise ValueError("tour beat slugs must be unique")
        beat_lookup = {beat.slug: beat for beat in self.beats}
        for stop in self.stops:
            for beat_slug in stop.beat_slugs:
                if beat_slug not in beat_lookup:
                    raise ValueError(
                        f"unknown beat slug for stop {stop.slug}: {beat_slug}"
                    )

    def first_beat(self) -> TourBeat:
        return self.beats[0]

    def beat(self, slug: str) -> TourBeat:
        for beat in self.beats:
            if beat.slug == slug:
                return beat
        raise KeyError(slug)

    def beat_for_topic(self, topic: str) -> TourBeat | None:
        for beat in self.beats:
            if beat.topic == topic:
                return beat
        return None

    def next_beat_slug(self, current_slug: str) -> str | None:
        slugs = [beat.slug for beat in self.beats]
        try:
            index = slugs.index(current_slug)
        except ValueError:
            raise KeyError(current_slug) from None
        next_index = index + 1
        if next_index >= len(slugs):
            return None
        return slugs[next_index]


def load_giza_tour() -> TourGraph:
    beats = (
        TourBeat(
            slug="arrival_orientation",
            stop_slug="arrival",
            topic="orientation",
            title="Arrival and Orientation",
            content_en=(
                "Welcome the visitor to the Giza plateau, orient them to the "
                "pyramid field, and keep the tone grounded and concise."
            ),
            content_ar_eg=(
                "رحب بالزائر في منطقة الجيزة وعرّفه بهدوء على اتجاه الأهرامات "
                "من غير تفاصيل كتير."
            ),
            source_ids=("giza_scope_brief",),
            review_status="reviewed",
            estimated_seconds=35,
        ),
        TourBeat(
            slug="khufu_overview",
            stop_slug="khufu",
            topic="khufu",
            title="Great Pyramid of Khufu",
            content_en=(
                "Introduce the Great Pyramid as the largest pyramid at Giza "
                "and keep exact claims limited to reviewed source context."
            ),
            content_ar_eg=(
                "قدّم هرم خوفو كأكبر أهرامات الجيزة مع تجنب أي أرقام دقيقة "
                "غير موجودة في المصادر."
            ),
            source_ids=("giza_scope_brief",),
            review_status="reviewed",
            estimated_seconds=40,
        ),
        TourBeat(
            slug="khafre_overview",
            stop_slug="khafre",
            topic="khafre",
            title="Pyramid of Khafre",
            content_en=(
                "Guide the visitor from Khufu toward Khafre and explain that "
                "the route is moving beat by beat."
            ),
            content_ar_eg=(
                "انقل الزائر من خوفو باتجاه خفرع واشرح إن الجولة ماشية خطوة بخطوة."
            ),
            source_ids=("giza_scope_brief",),
            review_status="reviewed",
            estimated_seconds=38,
        ),
        TourBeat(
            slug="menkaure_overview",
            stop_slug="menkaure",
            topic="menkaure",
            title="Pyramid of Menkaure",
            content_en=(
                "Introduce Menkaure as the next stop and keep the narration "
                "short enough to recover cleanly from interruption."
            ),
            content_ar_eg=(
                "قدّم منكاورع كمحطة تالية وخلي الكلام قصير بحيث نعرف نكمل بعد أي مقاطعة."
            ),
            source_ids=("giza_scope_brief",),
            review_status="reviewed",
            estimated_seconds=36,
        ),
        TourBeat(
            slug="sphinx_overview",
            stop_slug="sphinx",
            topic="sphinx",
            title="The Sphinx",
            content_en=(
                "Introduce the Sphinx as a major Giza stop while clearly "
                "separating reviewed facts from uncertain details."
            ),
            content_ar_eg=(
                "قدّم أبو الهول كمحطة مهمة في الجيزة مع توضيح الفرق بين "
                "المعلومة المؤكدة وأي حاجة غير مؤكدة."
            ),
            source_ids=("giza_scope_brief",),
            review_status="reviewed",
            estimated_seconds=42,
        ),
        TourBeat(
            slug="wrap_up_reflection",
            stop_slug="wrap_up",
            topic="wrap_up",
            title="Wrap-up",
            content_en=(
                "Close the first route with a brief recap and invite the "
                "visitor to ask follow-up questions."
            ),
            content_ar_eg=("اختم الجولة بملخص قصير وافتح المجال لأي أسئلة متابعة."),
            source_ids=("giza_scope_brief",),
            review_status="reviewed",
            estimated_seconds=30,
        ),
    )
    stops = (
        TourStop("arrival", "Arrival and orientation", ("arrival_orientation",)),
        TourStop("khufu", "Great Pyramid of Khufu", ("khufu_overview",)),
        TourStop("khafre", "Pyramid of Khafre", ("khafre_overview",)),
        TourStop("menkaure", "Pyramid of Menkaure", ("menkaure_overview",)),
        TourStop("sphinx", "The Sphinx", ("sphinx_overview",)),
        TourStop("wrap_up", "Wrap-up", ("wrap_up_reflection",)),
    )
    return TourGraph(slug="giza-v1", stops=stops, beats=beats)

