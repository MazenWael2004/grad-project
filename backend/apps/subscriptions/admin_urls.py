from django.urls import path

from . import admin_views

app_name = "subscriptions_admin"

urlpatterns = [
    path("analytics-dashboard/", admin_views.analytics_dashboard, name="analytics_dashboard"),
    path("plans/", admin_views.plan_list, name="plan_list"),
    path("plans/new/", admin_views.plan_create, name="plan_create"),
    path("plans/<int:pk>/", admin_views.plan_detail, name="plan_detail"),
    path("plans/<int:pk>/edit/", admin_views.plan_edit, name="plan_edit"),
    path("plans/<int:pk>/delete/", admin_views.plan_delete, name="plan_delete"),
]
