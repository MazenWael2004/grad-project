from django.db import models
from django.utils import timezone

class TourSession(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    owner_subject = models.CharField(max_length=64)
    guest_token_hash = models.CharField(max_length=128, unique=True)
    tour_slug = models.CharField(max_length=100)
    language = models.CharField(max_length=10)
    livekit_room = models.CharField(max_length=100)
    participant_identity = models.CharField(max_length=100)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Session {self.id} ({self.tour_slug})"


class TourStateCheckpoint(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    session = models.ForeignKey(TourSession, on_delete=models.CASCADE, related_name="checkpoints")
    event_id = models.CharField(max_length=64)
    event_type = models.CharField(max_length=100)
    state_version = models.IntegerField()
    active_mode = models.CharField(max_length=50)
    current_beat_id = models.CharField(max_length=100, null=True, blank=True)
    safe_anchor = models.JSONField(null=True, blank=True)
    state_payload = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["state_version"]

    def __str__(self):
        return f"Checkpoint {self.id} (v{self.state_version})"


class RecognitionEvent(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    session = models.ForeignKey(TourSession, on_delete=models.CASCADE, related_name="recognitions")
    request_event_id = models.CharField(max_length=64)
    idempotency_key = models.CharField(max_length=128)
    status = models.CharField(max_length=20, default="pending")
    file_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    result_payload = models.JSONField(null=True, blank=True)
    error_code = models.CharField(max_length=100, null=True, blank=True)
    retryable = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Recognition {self.id} ({self.status})"


class EvalEvent(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    session = models.ForeignKey(TourSession, on_delete=models.CASCADE, related_name="eval_events")
    event_id = models.CharField(max_length=64)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"EvalEvent {self.event_id} ({self.event_type})"
