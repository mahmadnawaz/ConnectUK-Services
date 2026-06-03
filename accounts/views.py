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


# --- Password Reset View ---
def password_reset_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            current_site = get_current_site(request)
            reset_link = f"https://{current_site.domain}/accounts/reset/{uid}/{token}/"

            subject = "Password Reset - ConnectUK Services"
            message = (
                f"Hi,\n\n"
                f"We received a request to reset your password.\n\n"
                f"Click the link below to reset your password:\n{reset_link}\n\n"
                f"If you did not request this, please ignore this email.\n\n"
                f"Regards,\nConnectUK Services Team"
            )

            thread = threading.Thread(
                target=send_notification_email,
                args=(subject, message, email)
            )
            thread.daemon = True
            thread.start()

        except User.DoesNotExist:
            pass

        return redirect('password_reset_done')

    return render(request, 'registration/password_reset_form.html')


# --- Password Reset Done View ---
def password_reset_done_view(request):
    return render(request, 'registration/password_reset_done.html')


# --- Password Reset Confirm View ---
def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Django 4+ mein token 'set-password' session mein store hota hai
    session_token_key = '_password_reset_token'
    
    if token != 'set-password':
        # Pehli baar link khulta hai — token validate karo aur session mein save karo
        if user is not None and default_token_generator.check_token(user, token):
            request.session[session_token_key] = token
            return redirect(f'/accounts/reset/{uidb64}/set-password/')
        else:
            messages.error(request, "Reset link is invalid or has expired!")
            return render(request, 'registration/password_reset_confirm.html', {'validlink': False})
    else:
        # 'set-password' URL par aaya — session se token lo
        token = request.session.get(session_token_key)
        if user is None or not default_token_generator.check_token(user, token):
            messages.error(request, "Reset link is invalid or has expired!")
            return render(request, 'registration/password_reset_confirm.html', {'validlink': False})

    if request.method == "POST":
        new_pass1 = request.POST.get('new_password1')
        new_pass2 = request.POST.get('new_password2')

        if new_pass1 != new_pass2:
            messages.error(request, "Passwords do not match!")
            return render(request, 'registration/password_reset_confirm.html', {'validlink': True})

        user.set_password(new_pass1)
        user.save()
        # Session clear karo
        request.session.pop(session_token_key, None)
        return redirect('password_reset_complete')

    return render(request, 'registration/password_reset_confirm.html', {'validlink': True})


# --- Password Reset Complete View ---
def password_reset_complete_view(request):
    return render(request, 'registration/password_reset_complete.html')