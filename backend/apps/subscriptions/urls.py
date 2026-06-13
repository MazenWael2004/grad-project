from django.urls import path

from .views import AddMemberView, PlanListView, SubscribeView, UnsubscribeView

urlpatterns = [
    path("plans/", PlanListView.as_view(), name="plan-list"),
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),
    path("members/add/", AddMemberView.as_view(), name="add-member"),
]
