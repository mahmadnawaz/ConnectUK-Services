"""
Django settings for connectukservices project.
Updated for Oracle 23ai Free - ConnectUK Services Project
Updated for Oracle Cloud Autonomous Database (PaaS) - Thin Mode Fix
Final Version: June 1, 2026
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = 'django-insecure-tr$$1v9t0t-z@xbd5j54a8^q6=h8mk)k0qgtz%63(2t*6he-ak'
DEBUG = True

ALLOWED_HOSTS = ['*']

# CSRF configuration for local, ngrok, and testing environments
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://distant-granola-chrome.ngrok-free.dev',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Hamari Apps
    'core',
    'accounts',
    'services',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'connectukservices.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'connectukservices.wsgi.application'

# --- Oracle Cloud Autonomous Database (Thin Mode Connection) ---
# Dynamic Wallet Path Configuration
WALLET_PATH = os.path.join(BASE_DIR, 'oracle_wallet').replace('\\', '/')

# Autonomous Database DSN String
# --- Oracle Cloud Autonomous Database (Thin Mode Connection Fix) ---
# SSL Server DN Match ko default allow karne ke liye string ko clean kiya gaya hai

# --- Oracle Cloud Autonomous Database (Final Verified Connection) ---
# Sahi Service Name aur SSL validation bypass ke sath optimized cloud connection

CLOUD_DSN = (
    "(DESCRIPTION="
    "(RETRY_COUNT=20)(RETRY_DELAY=3)"
    "(ADDRESS=(PROTOCOL=TCPS)(HOST=adb.uk-london-1.oraclecloud.com)(PORT=1522))"
    "(CONNECT_DATA=(SERVICE_NAME=g543a3981ae5980_connectukservices_low.adb.oraclecloud.com))"
    "(SECURITY=(ssl_server_dn_match=no)))"
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': CLOUD_DSN,
        'USER': 'ADMIN',                  # Master Admin User
        'PASSWORD': 'ConnectUK_216',      # Aap ka verified cloud database password
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static Files
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# MEDIA FILES CONFIGURATION (Images/Uploads ke liye)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication Redirects
LOGIN_URL = '/accounts/login/' 
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Email Settings (mumerconsultant@gmail.com)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mumerconsultant@gmail.com'
EMAIL_HOST_PASSWORD = 'newmwegkgfijkusy' 

DEFAULT_FROM_EMAIL = 'ConnectUK Services <mumerconsultant@gmail.com>'