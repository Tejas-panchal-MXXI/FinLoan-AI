from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import csv
from datetime import datetime
from .models import LoanApplication
from .forms import LoanApplicationForm
import os
import sys

# Add the parent directory to the path to import ml_predictor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the ML predictor
try:
    from .ml_predictor import loan_predictor
    ML_AVAILABLE = True
    print("ML models loaded successfully!")
except ImportError as e:
    print(f"ML models not available: {e}")
    ML_AVAILABLE = False

def home(request):
    """SIMPLE DEBUG VERSION"""
    from django.db.models import Q
    
    # Get actual counts
    all_apps = LoanApplication.objects.all()
    total = all_apps.count()
    approved = all_apps.filter(loan_status='Approved').count()  
    rejected = all_apps.filter(loan_status='Rejected').count()
    
    # Calculate rate
    rate = round((approved/total)*100, 1) if total > 0 else 0
    
    print(f"DEBUG: total={total}, approved={approved}, rejected={rejected}, rate={rate}")
    
    context = {
        'total_applications': total,
        'approved_applications': approved, 
        'rejected_applications': rejected,
        'approval_rate': rate,
    }
    
    return render(request, 'loan_predictor/home.html', context)

def loan_application_view(request):
    """Enhanced loan application view with ML predictions"""
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            
            # Run ML prediction if available
            if ML_AVAILABLE:
                try:
                    prediction_result = loan_predictor.predict(application)
                    application.approval_probability = prediction_result['approval_probability']
                    application.loan_status = 'Approved' if prediction_result['approved'] else 'Rejected'
                    application.save()
                except Exception as e:
                    print(f"ML prediction error: {e}")
                    application.loan_status = 'Pending'
                    application.save()
            else:
                application.loan_status = 'Pending'
                application.save()
            
            return redirect('loan_result', pk=application.pk)
    else:
        form = LoanApplicationForm()
    
    return render(request, 'loan_predictor/loan_form.html', {'form': form})

def ml_analytics_view(request):
    """Display ML Analytics Dashboard with real statistics"""
    
    # Get the same statistics as home page
    applications = LoanApplication.objects.all()
    total_applications = applications.count()
    approved_applications = applications.filter(loan_status='Approved').count()
    rejected_applications = applications.filter(loan_status='Rejected').count()
    
    # Calculate approval rate
    if total_applications > 0:
        approval_rate = round((approved_applications / total_applications) * 100, 1)
    else:
        approval_rate = 0
    
    context = {
        'page_title': 'ML Analytics Dashboard',
        # Real statistics data
        'total_applications': total_applications,
        'approved_applications': approved_applications, 
        'rejected_applications': rejected_applications,
        'approval_rate': approval_rate,
        # ML model data (static for now)
        'models_performance': {
            'logistic_regression': 86,
            'svm': 84,
            'random_forest': 82,
        },
        'feature_importance': {
            'Credit History': 35.2,
            'Total Income': 18.1,
            'Loan-Income Ratio': 14.9,
            'Education Level': 12.2,
            'Property Area': 8.5,
        }
    }
    return render(request, 'loan_predictor/ml_analytics.html', context)

def loan_result_view(request, pk):
    """Enhanced loan result view with detailed analysis"""
    application = get_object_or_404(LoanApplication, pk=pk)
    
    # Calculate additional insights
    total_income = application.applicant_income + (application.coapplicant_income or 0)
    loan_income_ratio = (application.loan_amount * 1000) / total_income if total_income > 0 else 0
    monthly_payment = (application.loan_amount * 1000 * 0.008)  # Rough estimate
    
    # Risk assessment
    risk_level = 'Low'
    if application.approval_probability:
        if application.approval_probability < 40:
            risk_level = 'High'
        elif application.approval_probability < 70:
            risk_level = 'Medium'
    
    context = {
        'application': application,
        'total_income': total_income,
        'loan_income_ratio': loan_income_ratio,
        'monthly_payment': monthly_payment,
        'risk_level': risk_level,
    }
    
    return render(request, 'loan_predictor/result.html', context)

def admin_dashboard_view(request):
    """Enhanced admin dashboard view with comprehensive filtering"""
    from django.db.models import Q, Count, Avg
    
    # Get all applications
    applications = LoanApplication.objects.all()
    
    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        applications = applications.filter(
            Q(applicant_name__icontains=search_query) |
            Q(loan_status__icontains=search_query)
        )
    
    # Apply status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        if status_filter == 'Pending':
            applications = applications.filter(
                Q(loan_status__isnull=True) | Q(loan_status='') | Q(loan_status='Pending')
            )
        else:
            applications = applications.filter(loan_status=status_filter)
    
    # Apply education filter
    education_filter = request.GET.get('education', '')
    if education_filter:
        applications = applications.filter(education=education_filter)
    
    # Apply property area filter
    property_area_filter = request.GET.get('property_area', '')
    if property_area_filter:
        applications = applications.filter(property_area=property_area_filter)
    
    # Order by most recent first
    applications = applications.order_by('-created_at')
    
    # FIXED: Calculate comprehensive statistics (for all applications, not filtered)
    all_applications = LoanApplication.objects.all()
    total_applications = all_applications.count()
    
    # Count each status separately with safe defaults
    approved_count = all_applications.filter(loan_status='Approved').count()
    rejected_count = all_applications.filter(loan_status='Rejected').count()
    pending_count = all_applications.filter(
        Q(loan_status__isnull=True) | Q(loan_status='') | Q(loan_status='Pending')
    ).count()
    
    # Calculate approval rate safely
    if total_applications > 0:
        approval_rate = round((approved_count / total_applications) * 100, 1)
    else:
        approval_rate = 0
    
    # Calculate average ML accuracy if available
    apps_with_probability = all_applications.exclude(approval_probability__isnull=True)
    if apps_with_probability.exists():
        avg_accuracy = round(apps_with_probability.aggregate(
            avg_prob=Avg('approval_probability')
        )['avg_prob'] or 0, 1)
    else:
        avg_accuracy = 86  # Default ML accuracy
    
    context = {
        'applications': applications,
        'total_applications': total_applications,
        'approved_applications': approved_count,
        'rejected_applications': rejected_count,
        'pending_applications': pending_count,
        'approval_rate': approval_rate,
        'ml_accuracy': avg_accuracy,
        
        # Pass filter values back to template
        'search_query': search_query,
        'status_filter': status_filter,
        'education_filter': education_filter,
        'property_area_filter': property_area_filter,
    }
    
    return render(request, 'loan_predictor/admin_dashboard.html', context)

   
# CRUD API ENDPOINTS

@require_http_methods(["GET"])
def get_application_data(request, pk):
    """Get application data for editing"""
    try:
        application = get_object_or_404(LoanApplication, pk=pk)
        data = {
            'id': application.id,
            'applicant_name': application.applicant_name,
            'gender': application.gender,
            'married': application.married,
            'dependents': application.dependents,
            'education': application.education,
            'self_employed': application.self_employed,
            'applicant_income': application.applicant_income,
            'coapplicant_income': application.coapplicant_income or 0,
            'loan_amount': application.loan_amount,
            'loan_amount_term': application.loan_amount_term,
            'credit_history': application.credit_history,
            'property_area': application.property_area,
            'loan_status': application.loan_status or 'Pending',
            'approval_probability': application.approval_probability,
        }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def update_application(request, pk):
    """Update application data"""
    try:
        application = get_object_or_404(LoanApplication, pk=pk)
        data = json.loads(request.body)
        
        # Update fields
        application.applicant_name = data.get('applicant_name', application.applicant_name)
        application.gender = data.get('gender', application.gender)
        application.married = data.get('married', application.married)
        application.dependents = data.get('dependents', application.dependents)
        application.education = data.get('education', application.education)
        application.self_employed = data.get('self_employed', application.self_employed)
        application.applicant_income = int(data.get('applicant_income', application.applicant_income))
        application.coapplicant_income = int(data.get('coapplicant_income', application.coapplicant_income or 0))
        application.loan_amount = int(data.get('loan_amount', application.loan_amount))
        application.loan_amount_term = int(data.get('loan_amount_term', application.loan_amount_term))
        application.credit_history = bool(data.get('credit_history', application.credit_history))
        application.property_area = data.get('property_area', application.property_area)
        application.loan_status = data.get('loan_status', application.loan_status)
        
        # Re-run ML prediction if financial data changed
        if any(key in data for key in ['applicant_income', 'coapplicant_income', 'loan_amount', 'credit_history']):
            if ML_AVAILABLE:
                try:
                    prediction_result = loan_predictor.predict(application)
                    application.approval_probability = prediction_result['approval_probability']
                    # Only update status if not manually set
                    if not data.get('loan_status') or data.get('loan_status') == 'Pending':
                        application.loan_status = 'Approved' if prediction_result['approved'] else 'Rejected'
                except Exception as e:
                    print(f"ML prediction error during update: {e}")
        
        application.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Application for {application.applicant_name} updated successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_application(request, pk):
    """Delete application"""
    try:
        application = get_object_or_404(LoanApplication, pk=pk)
        applicant_name = application.applicant_name
        application.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Application for {applicant_name} deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def export_applications_csv(request):
    """Export applications to CSV with current filters"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="finloan_applications_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'ID', 'Applicant Name', 'Gender', 'Married', 'Dependents', 'Education', 
        'Self Employed', 'Applicant Income', 'Coapplicant Income', 'Loan Amount', 
        'Loan Term', 'Credit History', 'Property Area', 'Status', 'ML Probability', 
        'Total Income', 'Loan-Income Ratio', 'Date Created'
    ])
    
    # Apply same filters as dashboard
    applications = LoanApplication.objects.all()
    
    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        applications = applications.filter(
            Q(applicant_name__icontains=search_query) |
            Q(loan_status__icontains=search_query)
        )
    
    # Apply status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        if status_filter == 'Pending':
            applications = applications.filter(
                Q(loan_status__isnull=True) | Q(loan_status='') | Q(loan_status='Pending')
            )
        else:
            applications = applications.filter(loan_status=status_filter)
    
    # Apply education filter
    education_filter = request.GET.get('education', '')
    if education_filter:
        applications = applications.filter(education=education_filter)
    
    # Apply property area filter
    property_area_filter = request.GET.get('property_area', '')
    if property_area_filter:
        applications = applications.filter(property_area=property_area_filter)
    
    # Write data rows
    for app in applications.order_by('-created_at'):
        total_income = app.applicant_income + (app.coapplicant_income or 0)
        loan_income_ratio = (app.loan_amount * 1000) / total_income if total_income > 0 else 0
        
        writer.writerow([
            app.id,
            app.applicant_name or 'N/A',
            app.gender or 'N/A',
            app.married or 'N/A',
            app.dependents or 'N/A',
            app.education or 'N/A',
            app.self_employed or 'N/A',
            app.applicant_income or 0,
            app.coapplicant_income or 0,
            app.loan_amount or 0,
            app.loan_amount_term or 360,
            'Yes' if app.credit_history else 'No',
            app.property_area or 'N/A',
            app.loan_status or 'Pending',
            f"{app.approval_probability:.1f}%" if app.approval_probability else 'N/A',
            total_income,
            f"{loan_income_ratio:.2f}",
            app.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(app, 'created_at') else 'N/A'
        ])
    
    return response
