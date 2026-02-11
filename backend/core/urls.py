from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("accounts/", include("apps.accounts.urls")),
    path("subscriptions/", include("apps.subscriptions.urls")),
]
