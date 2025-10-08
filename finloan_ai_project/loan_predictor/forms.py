from django import forms
from .models import LoanApplication

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = [
            'applicant_name', 'gender', 'married', 'dependents', 'education', 'self_employed',
            'applicant_income', 'coapplicant_income', 'loan_amount', 'loan_amount_term',
            'credit_history', 'property_area'
        ]
        
        from django import forms
from .models import LoanApplication

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = [
            'applicant_name', 'gender', 'married', 'dependents', 'education',
            'self_employed', 'applicant_income', 'coapplicant_income', 
            'loan_amount', 'loan_amount_term', 'credit_history', 'property_area'
        ]
        
        # Just add Bootstrap classes - no UI changes
        widgets = {
            'applicant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'married': forms.Select(attrs={'class': 'form-select'}),
            'dependents': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'self_employed': forms.Select(attrs={'class': 'form-select'}),
            'applicant_income': forms.NumberInput(attrs={'class': 'form-control'}),
            'coapplicant_income': forms.NumberInput(attrs={'class': 'form-control'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'loan_amount_term': forms.NumberInput(attrs={'class': 'form-control'}),
            'credit_history': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'property_area': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make fields required
        required_fields = ['applicant_name', 'gender', 'married', 'dependents', 
                         'education', 'self_employed', 'applicant_income', 
                         'loan_amount', 'loan_amount_term', 'property_area']
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
