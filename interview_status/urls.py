from django.urls import path
from . import views

urlpatterns = [
    path('', views.applied_status, name='interview_status'),
    # path('next_round/', views.next_round_view, name='next_round'),
]