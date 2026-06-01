from django.urls import path
from . import views

urlpatterns = [
    # Humne views.login_view aur views.signup_view ko direct link kar diya hai
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'), 
    path('signup/', views.signup_view, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),
]