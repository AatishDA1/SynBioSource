from rest_framework import serializers
from dataset.models import DatasetRegistry

class DatasetSerializerList(serializers.ModelSerializer):
    """Lists what fields to display in the API endpoint for listing all datasets."""
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        """All fields to be displayed in the API endpoint."""
        model = DatasetRegistry
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'dataset_size', 'dataset_file')

    def get_title(self, obj):
        """Gets the title of the dataset from the JSON field."""
        return obj.metadata_file.get('basic_identity', None)['title']
    
    def get_description(self, obj):
        """Gets the description of the dataset from the JSON field."""
        return obj.metadata_file.get('basic_identity', None)['description']
    
class DatasetSerializerDetails(serializers.ModelSerializer):
    """Lists what fields to display in the API endpoint for displaying a dataset's information."""
    
    class Meta:
        """All fields to be displayed in the API endpoint."""
        model = DatasetRegistry
        fields = ('id', 'owner', 'download_count', 'dataset_file', 'metadata_file', 'created_at', 'updated_at')

