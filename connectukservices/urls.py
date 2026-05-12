from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Import zaroori hai
from django.conf.urls.static import static # Import zaroori hai

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), 
    path('', include('core.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('services/', include('services.urls')),
]

# Ye line lazmi hai taake uploaded images (ID Proofs/Invoices) browser mein khul saken
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)