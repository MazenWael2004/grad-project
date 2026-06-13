from django.urls import path

from .views import PlanListView, SubscribeView, UnsubscribeView

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="plan-list"),
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),

]
