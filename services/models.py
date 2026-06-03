from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
import os
import threading


def send_brevo_email(subject, message, recipient_email, recipient_name):
    api_key = os.environ.get('BREVO_API_KEY')
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": api_key,
        "content-type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "sender": {"email": "ahn63400@gmail.com", "name": "ConnectUK Services"},
        "to": [{"email": recipient_email, "name": recipient_name}],
        "subject": subject,
        "textContent": message
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"DEBUG: Brevo Status Code: {response.status_code}")
        print(f"DEBUG: Brevo Response Body: {response.text}")
    except Exception as e:
        print(f"DEBUG: Email Error: {e}")


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    SERVICE_CHOICES = [
        ('card_machine', 'Card Machine'),
        ('epos_system', 'EPOS System'),
        ('business_energy', 'Business Energy'),
        ('business_water', 'Business Water'),
        ('broadband', 'Business Broadband'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    legal_name = models.CharField(max_length=255)
    trading_name = models.CharField(max_length=255, blank=True, null=True)
    contact_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    service_type = models.CharField(max_length=100, choices=SERVICE_CHOICES)
    contract_length = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=50)
    bank_sortcode = models.CharField(max_length=20)
    additional_info = models.TextField(blank=True, null=True)
    invoices = models.FileField(upload_to='invoices/', blank=True, null=True)
    id_proof = models.FileField(upload_to='id_proofs/', blank=True, null=True)
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


@receiver(post_save, sender=ServiceRequest)
def notify_status_change(sender, instance, created, **kwargs):
    if not created:
        try:
            subject = f"ConnectUK Application Update: {instance.get_service_type_display()}"
            status_text = instance.get_status_display()

            message = (
                f"Dear {instance.contact_name},\n\n"
                f"We wanted to inform you that the status of your application for '{instance.legal_name}' "
                f"has been updated to: {status_text}.\n\n"
                f"Log in to your dashboard to see more details.\n\n"
                f"Regards,\nConnectUK Services Team"
            )

            thread = threading.Thread(
                target=send_brevo_email,
                args=(subject, message, instance.email, instance.contact_name)
            )
            thread.daemon = True
            thread.start()

        except Exception as e:
            print(f"Error sending status email: {e}")