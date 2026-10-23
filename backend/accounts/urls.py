
from django.urls import path

from .views import (
    CurrentUserView,
    PublicTokenObtainPairView,
    PublicTokenRefreshView,
    RegistrationView,
    UserSettingsView,
)


urlpatterns = [
    path(
        "register/",
        RegistrationView.as_view(),
        name="register",
    ),
    path(
        "token/",
        PublicTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        PublicTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "me/",
        CurrentUserView.as_view(),
        name="current_user",
    ),
    path(
        "settings/",
        UserSettingsView.as_view(),
        name="user_settings",
),
]
