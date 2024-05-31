from django.contrib import admin
from .models import InterviewResponse

class InterviewResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp')  # Specify the fields to display

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Customize the queryset if needed, for example, to filter by user
        return qs

admin.site.register(InterviewResponse, InterviewResponseAdmin)
