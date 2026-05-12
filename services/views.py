from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceRequest

# 1. Services List Page
def services(request):
    return render(request, 'services/services.html')

# 2. Main Dashboard View
@login_required(login_url='login')
def dashboard(request):
    user_requests = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'requests': user_requests,
        'total': user_requests.count(),
        'approved': user_requests.filter(status='approved').count(),
        'processing': user_requests.filter(status='processing').count(),
        'pending': user_requests.filter(status='pending').count(),
    }
    return render(request, 'dashboard/dashboard.html', context)

# 3. Updated Submit Function (Auto-select logic ke sath)
@login_required(login_url='login')
def request_service(request):
    # URL se 'type' parameter pakarna (e.g., ?type=Business Gas)
    selected_service = request.GET.get('type', '')

    if request.method == 'POST':
        try:
            ServiceRequest.objects.create(
                user=request.user,
                legal_name=request.POST.get('legal_name'),
                trading_name=request.POST.get('trading_name'),
                contact_name=request.POST.get('contact_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                service_type=request.POST.get('service_type'),
                contract_length=request.POST.get('contract_length'),
                bank_name=request.POST.get('bank_name'),
                bank_account_number=request.POST.get('bank_account_number'),
                bank_sortcode=request.POST.get('bank_sortcode'),
                additional_info=request.POST.get('additional_info'),
                invoices=request.FILES.get('invoices'),
                id_proof=request.FILES.get('id_proof'),
                status='pending'
            )
            messages.success(request, "Your inquiry has been submitted successfully!")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            # Error ki surat mein bhi selected_service bhej rahe hain taake form dropdown kharab na ho
            return render(request, 'services/quote.html', {
                'edit_mode': False, 
                'selected_service': selected_service
            })

    # GET request par selected_service template ko pass karna
    return render(request, 'services/quote.html', {
        'edit_mode': False, 
        'selected_service': selected_service
    })

# 4. Edit Request Function
@login_required(login_url='login')
def edit_request(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk, user=request.user)
    if request.method == 'POST':
        req.legal_name = request.POST.get('legal_name')
        req.trading_name = request.POST.get('trading_name')
        req.contact_name = request.POST.get('contact_name')
        req.email = request.POST.get('email')
        req.phone = request.POST.get('phone')
        req.service_type = request.POST.get('service_type')
        req.contract_length = request.POST.get('contract_length')
        req.bank_name = request.POST.get('bank_name')
        req.bank_account_number = request.POST.get('bank_account_number')
        req.bank_sortcode = request.POST.get('bank_sortcode')
        req.additional_info = request.POST.get('additional_info')
        
        if request.FILES.get('invoices'):
            req.invoices = request.FILES.get('invoices')
        if request.FILES.get('id_proof'):
            req.id_proof = request.FILES.get('id_proof')
            
        req.save()
        messages.success(request, "Your application has been updated successfully!")
        return redirect('dashboard')
    
    return render(request, 'services/quote.html', {'req': req, 'edit_mode': True})

# 5. Delete Request Function
@login_required(login_url='login')
def delete_request(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk, user=request.user)
    req.delete()
    messages.success(request, "Your inquiry has been deleted successfully!")
    return redirect('dashboard')