from django.shortcuts import render
from .models import DatasetRegistry
from django.contrib.auth.decorators import login_required
import json

# Create your views here.
@login_required(login_url='/login')
def UploadDataset(request):
    """Function to allow users to upload datasets and prevent them from accessing the page if they aren't logged in."""
    if request.method == "POST":
        dataset_file=request.FILES.get("dataset-file")
        json_file=request.FILES.get("json-file")
        json_data=json_file.read()
        print(json_data)
        print(request.FILES)
        print(type(json_data))
        print(json.loads(json_data))
        data=DatasetRegistry.objects.create(
            owner=request.user,
            dataset_file=dataset_file,
            metadata_file= json.loads(json_data)
        )
    #record=DatasetRegistry.objects.filter(metadata_file__basic_identity__title__contains='Dataset')
    #print(record)
    return render(request,'dataset/upload_dataset.html')  
