from django import forms
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ResumeForm(forms.Form):
    job_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), label='Job Description')
    resume = forms.FileField(label='Upload your resume (PDF)')


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(help_text="Enter a valid email address")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
