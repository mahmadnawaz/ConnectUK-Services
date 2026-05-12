from django.urls import path
from . import views

urlpatterns = [
    path('', views.services, name='services'),
    
    # Dashboard path (Typo fixed: views.views hatakar sirf views.dashboard kar diya)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('get-quote/', views.request_service, name='get_quote'),
    path('edit-request/<int:pk>/', views.edit_request, name='edit_request'),
    path('delete-request/<int:pk>/', views.delete_request, name='delete_request'),
]