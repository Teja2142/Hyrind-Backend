from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('<uuid:file_id>/download/', views.get_download_url, name='download_url'),
]
