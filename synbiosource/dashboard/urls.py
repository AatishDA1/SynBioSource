from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('moderator/login', include('dashboard.urls')),
]
