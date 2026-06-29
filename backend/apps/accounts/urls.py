from django.urls import path
from .views import RegisterView, LoginView, LogoutView,UserDetailView,UpdateProfileView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("users/", UserDetailView.as_view()),
    path("profile/update/", UpdateProfileView.as_view()),
    # path("api/tour-guide/",tour_guidView.as_view(),name= "tour_guid")
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
