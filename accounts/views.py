import threading
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

# Logger setup
logger = logging.getLogger(__name__)

# --- Helper function for background email ---
def send_async_email(subject, message, recipient_list):
    try:
        send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            recipient_list, 
            fail_silently=False
        )
        logger.info(f"Email successfully sent to {recipient_list}")
    except Exception as e:
        # Render ke logs mein ye error dikhega
        logger.error(f"CRITICAL: Background Email Error: {e}")

# --- Signup View ---
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return render(request, 'accounts/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'accounts/signup.html')

        try:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.is_active = False 
            myuser.save()

            # Activation Link Generation
            current_site = get_current_site(request)
            subject = "Activate your ConnectUK Account"
            uid = urlsafe_base64_encode(force_bytes(myuser.pk))
            token = default_token_generator.make_token(myuser)
            
            # protocol ko 'https' fix kar diya hai kyunki Render par SSL hota hai
            activation_link = f"https://{current_site.domain}/accounts/activate/{uid}/{token}/"
            message = f"Hi {username},\n\nThank you for registering. Please click on the link below to activate your account:\n\n{activation_link}"
            
            # Background Thread
            email_thread = threading.Thread(
                target=send_async_email, 
                args=(subject, message, [email])
            )
            email_thread.start()
            
            messages.success(request, "Registration successful! Please check your email to activate your account.")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"Registration error: {e}")
            return render(request, 'accounts/signup.html')
    
    return render(request, 'accounts/signup.html')

# --- Baki views (activate, login, logout) waisay hi rahen ge ---
# (Aapke purane code wale niche yahan paste kar dein)