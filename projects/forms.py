from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Project
from django.core.validators import RegexValidator

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile_phone = forms.CharField(
        required=True,
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^(?:\+?20)?1[0-5]\d{8}$',
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
            raise forms.ValidationError('A user with that email already exists.')
        return email

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'details', 'target_amount', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }