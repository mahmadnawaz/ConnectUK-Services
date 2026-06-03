import requests
import os
import threading
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site


# --- Helper Function ---
def send_notification_email(subject, message, recipient_email):
    api_key = os.environ.get('BREVO_API_KEY')
    print(f"DEBUG: API Key present: {bool(api_key)}")

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": api_key,
        "content-type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "sender": {"email": "ahn63400@gmail.com", "name": "ConnectUK Services"},
        "to": [{"email": recipient_email}],
        "subject": subject,
        "textContent": message
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"DEBUG: Brevo Status Code: {response.status_code}")
        print(f"DEBUG: Brevo Response Body: {response.text}")
    except Exception as e:
        print(f"DEBUG: Critical Notification Error: {e}")


# --- Signup View ---
def signup_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered!")
            return render(request, 'accounts/signup.html')

        try:
            # Username automatically email se generate karo
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            myuser = User.objects.create_user(username, email, pass1)
            myuser.is_active = False
            myuser.save()

            current_site = get_current_site(request)
            subject = "Activate your ConnectUK Account"
            uid = urlsafe_base64_encode(force_bytes(myuser.pk))
            token = default_token_generator.make_token(myuser)

            activation_link = f"https://{current_site.domain}/accounts/activate/{uid}/{token}/"
            message = f"Hi,\n\nThank you for registering. Please click to activate: {activation_link}"

            thread = threading.Thread(
                target=send_notification_email,
                args=(subject, message, email)
            )
            thread.daemon = True
            thread.start()

            messages.success(request, "Registration successful! Please check your email.")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return render(request, 'accounts/signup.html')

    return render(request, 'accounts/signup.html')


# --- Account Activation View ---
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


# --- Login View ---
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
            messages.success(request, "Welcome back!")
            return redirect('dashboard')
        else:
            if username and User.objects.filter(username=username, is_active=False).exists():
                messages.warning(request, "Please activate your account via email first!")
            else:
                messages.error(request, "Invalid email or password!")
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')


# --- Logout View ---
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')