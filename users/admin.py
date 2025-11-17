from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'phone', 'university', 'degree', 'major', 'visa_status', 'graduation_date', 'terms_accepted')
