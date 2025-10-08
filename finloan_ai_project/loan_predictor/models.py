from django.db import models

class LoanApplication(models.Model):
    # Existing fields...
    applicant_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    married = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')])
    dependents = models.CharField(max_length=2, choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3+', '3+')])
    education = models.CharField(max_length=20, choices=[('Graduate', 'Graduate'), ('Not Graduate', 'Not Graduate')])
    self_employed = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')])
    applicant_income = models.IntegerField()
    coapplicant_income = models.IntegerField(default=0)
    loan_amount = models.IntegerField()
    loan_amount_term = models.IntegerField(default=360)
    credit_history = models.BooleanField()
    property_area = models.CharField(max_length=10, choices=[('Urban', 'Urban'), ('Semiurban', 'Semiurban'), ('Rural', 'Rural')])
    
    # Results fields
    loan_status = models.CharField(max_length=10, choices=[('Approved', 'Approved'), ('Rejected', 'Rejected')], blank=True, null=True)
    approval_probability = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.applicant_name} - {self.loan_status or 'Pending'}"
    
    class Meta:
        ordering = ['-created_at']  # Show newest applications first
        verbose_name = "Loan Application"
        verbose_name_plural = "Loan Applications"
