from django.contrib import admin
from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'file_type', 'original_name', 'size_bytes', 'uploaded_at')
    list_filter = ('file_type',)
    search_fields = ('user__email', 'original_name')
    readonly_fields = ('id', 'uploaded_at')
    ordering = ('-uploaded_at',)
