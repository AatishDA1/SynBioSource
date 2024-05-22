from django.db import models
from dashboard.models import AllUsers
from django.utils import timezone

# Create your models here.
class DatasetRegistry(models.Model):
    """Class to create the dataset registry table."""
    owner = models.ForeignKey(AllUsers, on_delete=models.CASCADE)
    download_count = models.IntegerField(default=0)
    dataset_file = models.FileField(upload_to='dataset')
    metadata_file = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata Extracted Numerical Fields
     # Dataset Creation
    number_of_samples = models.IntegerField(null=True)
    total_participants = models.IntegerField(null=True)

     # Dataset Composition
      # General fields within Composition
    dataset_size = models.IntegerField(default=0)
    number_of_files = models.IntegerField(default=0)
    average_file_size = models.FloatField(default=0)
      
      # Optional fields withing Composition
    average_sheets = models.IntegerField(null=True)
    average_resolution = models.IntegerField(null=True)
    video_average_duration = models.FloatField(null=True)
    audio_average_duration = models.FloatField(null=True)
    average_bitrate = models.FloatField(null=True)
    fasta_minimum_sequence_length = models.IntegerField(null=True)
    fasta_maximum_sequence_length = models.IntegerField(null=True)
    fasta_coverage_depth = models.IntegerField(null=True)
    fasta_error_rate = models.FloatField(null=True)
    genbank_minimum_sequence_length = models.IntegerField(null=True)
    genbank_maximum_sequence_length = models.IntegerField(null=True)
    genbank_coverage_depth = models.IntegerField(null=True)
    genbank_error_rate = models.FloatField(null=True)

    def __str__(self):
        """Function to return the name of the datasets selected to the admin panel."""
        if "basic_identity" not in self.metadata_file:
            return "no name"+str(self.id)
        return str(self.id)+" "+self.metadata_file['basic_identity']['title']
    
class Keyword(models.Model):
    """Class to store all the keywords from the datasets."""
    name = models.CharField(max_length=255, unique=True)
    dataset_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Function to return the keywords to the admin panel."""
        return self.name