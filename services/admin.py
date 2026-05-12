from django.contrib import admin
from .models import ServiceRequest, ContactMessage

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    # 'service_type' ki jagah hamara custom function 'display_service_type' use karein
    list_display = ('legal_name', 'email', 'display_service_type', 'status', 'created_at')
    
    # Status ko list view se hi update karne ki ijazat
    list_editable = ('status',)
    
    # Sidebar filters
    list_filter = ('status', 'service_type', 'created_at')
    
    # Search functionality
    search_fields = ('legal_name', 'email', 'contact_name')

    # Ye function khali dash (-) ko khatam karke data show karega
    def display_service_type(self, obj):
        # 1. Dropdown label check karega (e.g., 'Card Machine')
        label = obj.get_service_type_display()
        
        # 2. Agar label aur database value same hain (yani koi match nahi mila), 
        # toh database ki original value (e.g., 'Card Machine - Electric & Gas') dikha dega
        if label == obj.service_type:
            return obj.service_type
        return label
    
    # Column ka header name
    display_service_type.short_description = 'Service Type'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')