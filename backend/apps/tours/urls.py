from django.urls import path
from .views import (
    HealthCheckView,
    ToursListView,
    CreateSessionView,
    LiveKitTokenView,
    SessionStateView,
    UploadPhotoView,
    RecognitionStatusView,
    NearbyStopsView,
    RecordEventView,
)

urlpatterns = [
    # Without trailing slashes (matches FastAPI defaults and frontend calls)
    path("health", HealthCheckView.as_view(), name="health"),
    path("tours", ToursListView.as_view(), name="tours_list"),
    path("sessions", CreateSessionView.as_view(), name="create_session"),
    path("sessions/<str:session_id>/livekit-token", LiveKitTokenView.as_view(), name="livekit_token"),
    path("sessions/<str:session_id>/state", SessionStateView.as_view(), name="session_state"),
    path("sessions/<str:session_id>/photos", UploadPhotoView.as_view(), name="upload_photo"),
    path("sessions/<str:session_id>/recognitions/<str:recognition_id>", RecognitionStatusView.as_view(), name="recognition_status"),
    path("nearby-stops", NearbyStopsView.as_view(), name="nearby_stops"),
    path("events", RecordEventView.as_view(), name="record_event"),

    # With trailing slashes for standard Django routing compatibility
    path("health/", HealthCheckView.as_view()),
    path("tours/", ToursListView.as_view()),
    path("sessions/", CreateSessionView.as_view()),
    path("sessions/<str:session_id>/livekit-token/", LiveKitTokenView.as_view()),
    path("sessions/<str:session_id>/state/", SessionStateView.as_view()),
    path("sessions/<str:session_id>/photos/", UploadPhotoView.as_view()),
    path("sessions/<str:session_id>/recognitions/<str:recognition_id>/", RecognitionStatusView.as_view()),
    path("nearby-stops/", NearbyStopsView.as_view()),
    path("events/", RecordEventView.as_view()),
]
