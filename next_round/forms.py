from django import forms
from .models import InterviewResponse

class InterviewForm(forms.ModelForm):
    class Meta:
        model = InterviewResponse
        exclude = ['user']  # Exclude the user field from the form
