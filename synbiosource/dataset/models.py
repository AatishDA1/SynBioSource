from django.db import models
from dashboard.models import AllUsers
from django.utils import timezone

# Create your models here.
class DatasetRegistry(models.Model):
    """Class to create the dataset registry table."""
    owner=models.ForeignKey(AllUsers, on_delete=models.CASCADE)
    download_count=models.IntegerField(default=0)
    dataset_file=models.FileField(upload_to='dataset')
    metadata_file=models.JSONField()
    created_at=models.DateTimeField(default=timezone.now)
