from django.urls import path
from .views import interview_steps, submission_success, submission_timeout

urlpatterns = [
    path('', interview_steps, name='next_round'),
    path('success/', submission_success, name='success_url'),
    path('timeout/', submission_timeout, name='timeout_url'),
]
