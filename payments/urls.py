"""Payments URLs"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<slug:slug>/', views.initiate_payment, name='initiate'),
    path('success/', views.payment_success, name='success'),
    path('failure/', views.payment_failure, name='failure'),
    path('webhook/', views.razorpay_webhook, name='webhook'),
    path('history/', views.payment_history, name='history'),
    path('upi/<slug:slug>/', views.upi_submit, name='upi_submit'),
]
