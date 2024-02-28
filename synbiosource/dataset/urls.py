from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.UploadDataset, name="upload-dataset"),
]

