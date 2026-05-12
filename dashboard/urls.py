# dashboard/urls.py mein check karein
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'), # Ye 'name' hona zaroori hai
    path('complaints/', views.complaint_view, name='complaints'), # Naya URL for complaints
]