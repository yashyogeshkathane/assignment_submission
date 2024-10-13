from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('submissions.urls')),  # This assumes that your 'submissions' app has its own urls.py file.
]
