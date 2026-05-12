from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

class ServiceRequest(models.Model):
    # Status Choices for Dropdown
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Service Type Choices
    SERVICE_CHOICES = [
        ('card_machine', 'Card Machine'),
        ('epos_system', 'EPOS System'),
        ('business_energy', 'Business Energy'),
        ('business_water', 'Business Water'),
        ('broadband', 'Business Broadband'),
    ]

    # User linkage
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Form Fields
    legal_name = models.CharField(max_length=255)
    trading_name = models.CharField(max_length=255, blank=True, null=True)
    contact_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Updated: Added Choices
    service_type = models.CharField(max_length=100, choices=SERVICE_CHOICES)
    contract_length = models.CharField(max_length=50)
    
    bank_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=50)
    bank_sortcode = models.CharField(max_length=20)
    additional_info = models.TextField(blank=True, null=True)
    
    # File Uploads
    invoices = models.FileField(upload_to='invoices/', blank=True, null=True)
    id_proof = models.FileField(upload_to='id_proofs/', blank=True, null=True)
    
    # Updated: Added Choices to Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.legal_name} - {self.get_service_type_display()}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


# --- Email Signal: Jab Status change ho toh email jaye ---
@receiver(post_save, sender=ServiceRequest)
def notify_status_change(sender, instance, created, **kwargs):
    # 'created' False tab hota hai jab purana record update ho (status change)
    if not created:
        try:
            subject = f"ConnectUK Application Update: {instance.get_service_type_display()}"
            # Human-friendly status text (e.g., 'Approved')
            status_text = instance.get_status_display()
            
            message = f"Dear {instance.contact_name},\n\n" \
                      f"We wanted to inform you that the status of your application for '{instance.legal_name}' " \
                      f"has been updated to: {status_text}.\n\n" \
                      f"Log in to your dashboard to see more details.\n\n" \
                      f"Regards,\nConnectUK Services Team"

            send_mail(
                subject, 
                message, 
                settings.EMAIL_HOST_USER, 
                [instance.email], 
                fail_silently=True
            )
        except Exception as e:
            # Server crash na ho agar email na jaye, isliye sirf print karein
            print(f"Error sending status email: {e}")