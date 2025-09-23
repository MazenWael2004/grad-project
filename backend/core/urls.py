from django.urls import path
from . import views

urlpatterns = [
    path("photos/", views.photo_list, name="photo-list"),
]





