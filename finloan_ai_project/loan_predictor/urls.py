from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('apply/', views.loan_application_view, name='loan_application'),
    path('result/<int:pk>/', views.loan_result_view, name='loan_result'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('ml-analytics/', views.ml_analytics_view, name='ml_analytics'),
    
    # CRUD API endpoints
    path('api/application/<int:pk>/', views.get_application_data, name='get_application_data'),
    path('api/application/<int:pk>/update/', views.update_application, name='update_application'),
    path('api/application/<int:pk>/delete/', views.delete_application, name='delete_application'),
    path('export-csv/', views.export_applications_csv, name='export_csv'),
    
]
