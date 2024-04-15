from django.urls import path
from .views import (RegisterUserView, VerifyUserEmail, LoginUserView, UserProfile, PasswordResetRequestView,
                    PasswordResetConfirm, SetNewPassword)


urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("verify-email/", VerifyUserEmail.as_view(), name="verify_email"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("profile/<pk>/", UserProfile.as_view(), name="profile"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset-confirm/<uidb64>/<token>", PasswordResetConfirm.as_view(), name="password-reset-confirm"),
    path("set-new-password/", SetNewPassword.as_view(), name="set-new-password"),
]