from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'), 
    path('complaints/', views.complaint_view, name='complaints'), 
]