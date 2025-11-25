from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Project, Donation
from django.core.validators import RegexValidator

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile_phone = forms.CharField(
        required=True,
        max_length=11,
        validators=[
            RegexValidator(
               regex=r'^01[0-2,5]{1}[0-9]{8}$',
                message='Enter a valid Egyptian mobile number (e.g. 010XXXXXXXX or +2010XXXXXXXX).'
            )
        ]
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'mobile_phone', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data.get('mobile_phone', '')
        if len(mobile_phone) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits.")
        return mobile_phone


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'details', 'target_amount', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project title'}),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe your project in detail...'
            }),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in EGP'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ["donor_name", "donor_email", "amount"]
        widgets = {
            "donor_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name (optional)"}),
            "donor_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your email (optional)"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "min": 1, "placeholder": "Amount in EGP"}),
        }

    def clean_amount(self):
        amt = self.cleaned_data.get("amount")
        if amt is None or amt < 1:
            raise forms.ValidationError("Donation amount must be at least 1 EGP.")
        if amt > 1_000_000:
            raise forms.ValidationError("Donation amount is too large.")
        return amt