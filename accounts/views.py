from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

# Verification ke liye zaroori imports
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

# --- Signup View with Verification Link ---
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        # Check passwords match
        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return render(request, 'accounts/signup.html')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'accounts/signup.html')

        # User create karein lekin inactive rakhein
        try:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.is_active = False  # Link click hone tak login nahi kar sakega
            myuser.save()

            # --- Activation Link Generation ---
            current_site = get_current_site(request)
            subject = "Activate your ConnectUK Account"
            
            # Unique token aur UID banana
            uid = urlsafe_base64_encode(force_bytes(myuser.pk))
            token = default_token_generator.make_token(myuser)
            
            # Activation URL path (Iska path accounts/urls.py mein bhi add karna hoga)
            activation_link = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"
            
            message = f"Hi {username},\n\nThank you for registering. Please click on the link below to activate your account:\n\n{activation_link}\n\nIf you didn't register, please ignore this email."
            
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
            
            messages.success(request, "Registration successful! Please check your email to activate your account.")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
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
        user.is_active = True  # Ab user authenticate ho gaya
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
            # Django default authenticate() inactive users ko 'None' return karta hai
            login(request, user)
            messages.success(request, f"Welcome back!")
            return redirect('dashboard')
        else:
            # Yahan check karein ke kahin user inactive toh nahi
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