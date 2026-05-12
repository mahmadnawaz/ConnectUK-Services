from django.shortcuts import render, redirect
from django.contrib import messages
from services.models import ContactMessage # Database mein save karne ke liye model import kiya

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == "POST":
        # Form se data uthana
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_content = request.POST.get('message')
        # Model mein 'subject' field lazmi hai, isliye hum ek default subject de rahe hain
        subject = "Website Inquiry"

        try:
            # Ye step data ko Admin Panel (Database) mein save karega
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_content
            )
            messages.success(request, f"Thank you, {name}! Your message has been sent successfully.")
        except Exception as e:
            messages.error(request, f"Maazrat! Message save nahi ho saka: {e}")
        
        return redirect('contact')
        
    return render(request, 'core/contact.html')

def privacy_policy(request):
    return render(request, 'privacypolicy.html')

def complaint(request):
    return render(request, 'dashboard/complaint.html')