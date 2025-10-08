from django.contrib import admin
from .models import LoanApplication

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'applicant_name', 
        'loan_amount', 
        'loan_status', 
        'approval_probability',
        'created_at'
    ]
    list_filter = [
        'loan_status', 
        'education', 
        'gender', 
        'married',
        'property_area',
        'created_at'
    ]
    search_fields = ['applicant_name', 'loan_status']
    readonly_fields = ['loan_status', 'approval_probability', 'created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('applicant_name', 'gender', 'married', 'dependents', 'education')
        }),
        ('Employment', {
            'fields': ('self_employed',)
        }),
        ('Financial Information', {
            'fields': ('applicant_income', 'coapplicant_income', 'loan_amount', 'loan_amount_term')
        }),
        ('Credit & Property', {
            'fields': ('credit_history', 'property_area')
        }),
        ('ML Prediction Results', {
            'fields': ('loan_status', 'approval_probability', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Show most recent applications first
    ordering = ['-created_at']
