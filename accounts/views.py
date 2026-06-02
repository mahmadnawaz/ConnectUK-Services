import threading
import logging
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

logger = logging.getLogger(__name__)

# --- Helper function for Background Email (Using Brevo API) ---
def send_async_email(subject, message, recipient_list):
    try:
        # Brevo API Configuration
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = os.environ.get('BREVO_API_KEY')
        
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": recipient_list[0]}],
            sender={"email": "ahn63400@gmail.com", "name": "ConnectUK Services"},
            subject=subject,
            text_content=message
        )
        
        api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Email successfully sent via API to {recipient_list}")
    except Exception as e:
        logger.error(f"CRITICAL: Brevo API Email Error: {e}")

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

            current_site = get_current_site(request)
            subject = "Activate your ConnectUK Account"
            uid = urlsafe_base64_encode(force_bytes(myuser.pk))
            token = default_token_generator.make_token(myuser)
            
            activation_link = f"https://{current_site.domain}/accounts/activate/{uid}/{token}/"
            message = f"Hi {username},\n\nThank you for registering. Please click on the link below to activate your account:\n\n{activation_link}"
            
            email_thread = threading.Thread(target=send_async_email, args=(subject, message, [email]))
            email_thread.start()
            
            messages.success(request, "Registration successful! Please check your email.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return render(request, 'accounts/signup.html')
    return render(request, 'accounts/signup.html')

# --- Account Activation View (Waisa hi rahega) ---
def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True 
        user.save()
        messages.success(request, "Your account has been activated! You can now login.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid or has expired!")
        return redirect('signup')

# --- Login View (Waisa hi rahega) ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        email_input = request.POST.get('email')
        p = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email_input)
            username = user_obj.username 
        except User.DoesNotExist:
            username = None

        user = authenticate(username=username, password=p)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back!")
            return redirect('dashboard')
        else:
            if username and User.objects.filter(username=username, is_active=False).exists():
                messages.warning(request, "Please activate your account via email first!")
            else:
                messages.error(request, "Invalid email or password!")
            return render(request, 'accounts/login.html')
            
    return render(request, 'accounts/login.html')

# --- Logout View (Waisa hi rahega) ---
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')