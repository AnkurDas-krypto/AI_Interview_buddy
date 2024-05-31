from django.contrib import admin
from django.urls import path, include
from resume_hire_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('resume_hire_app.urls')),
    path('interview_status/', include('interview_status.urls')),
    path('next_round/', include('next_round.urls')),
    path('result/', include('qualifier.urls')), 

]
