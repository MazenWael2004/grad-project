from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")), 
    path("", include("apps.accounts.urls")),
    path("", include("apps.tours.urls")),
]
from .views import generate_itinerary
urlpatterns += [
    path("api/itinerary/generate/", generate_itinerary, name="generate_itinerary"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

