from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from services.models import ServiceRequest 
from core.models import ContactMessage  
from django.contrib import messages

@login_required(login_url='login')
def dashboard_view(request):
    requests = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'requests': requests,
        'total': requests.count(),
        'approved': requests.filter(status='approved').count(),
        'processing': requests.filter(status='processing').count(),
        'pending': requests.filter(status='pending').count(),
    }
    return render(request, 'dashboard/dashboard.html', context)

# --- Naya Complaint Function ---
@login_required(login_url='login')
def complaint_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_body = request.POST.get('message')

        # Database mein save ho raha hai
        ContactMessage.objects.create(
            name=full_name,
            email=email,
            mobile=mobile,
            subject=f"[COMPLAINT] {subject}", 
            message=message_body
        )

        messages.success(request, "Your complaint has been submitted successfully!")
        return redirect('complaints') # Wapis usi page par bhej dega

    return render(request, 'dashboard/complaint.html')