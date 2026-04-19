"""
Accounts - URL Configuration
Includes: Auth, Email Verification, Password Reset
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/update/', views.profile_update_view, name='profile_update'),

    # ── Email Verification ────────────────────────────────────────────────────
    path('verify-email/sent/', views.VerificationSentView.as_view(), name='verification_sent'),
    path('verify-email/<uuid:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),

    # ── Password Reset ────────────────────────────────────────────────────────
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/sent/', views.PasswordResetSentView.as_view(), name='password_reset_sent'),
    path('password-reset/confirm/<uuid:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
]
