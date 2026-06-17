from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")), 
    path("", include("apps.accounts.urls")),
]
from .views import generate_itinerary
urlpatterns += [
    path("api/itinerary/generate/", generate_itinerary, name="generate_itinerary"),
]
