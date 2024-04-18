from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.UploadDataset, name="upload-dataset"),
    path('browse', views.BrowseDatasets, name="browse-datasets"),
    path('browse/<int:dataset_id>', views.ViewDataset, name="view-dataset"),
    path('browse/download/<int:dataset_id>', views.DownloadDataset, name="download-dataset"),
    path('browse/edit/<int:dataset_id>', views.EditDataset, name="edit-dataset"),
    path('browse/delete/<int:dataset_id>', views.DeleteDataset, name="delete-dataset"),
    path('yourdatasets', views.YourDatasets, name="your-datasets"),
]

