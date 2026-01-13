from django.urls import path
from . import views

urlpatterns = [
    path('airtime/top-up/', views.AirtimeTopUpView.as_view(), name='airtime-top-up'),
]