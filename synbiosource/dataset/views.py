from django.shortcuts import render,redirect
from .models import DatasetRegistry,Keyword
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
import os
import json
import zipfile
import io
import time

def upload_and_zip_folder(request, mapper, metadata):
    """Function to create a zip file from the uploaded dataset folder."""
    # Creates an in-memory BytesIO object to hold the ZIP file.
    in_memory_zip = io.BytesIO()
    
    # Creates a ZIP file.
    with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Adds the metadata to the ZIP
        zf.writestr('metadata.json', json.dumps(metadata).encode('utf-8'))
        
        # Loops through each file uploaded in the request.
        for file in request.FILES.getlist('dataset-file'):
            file_content = file.read()
            # Writes each file to the ZIP, using the mapper for the file name.
            zf.writestr(mapper[file.name], file_content)
    
    # Resets the pointer of the in-memory ZIP file.
    in_memory_zip.seek(0)
    
    # Generates a unique filename for the ZIP file.
    zip_filename = str(list(mapper.keys())[0]) + str(time.time()) + ".zip"
    
    # Saves the ZIP file to the default storage under the 'dataset/' directory in the S3 Bucket.
    path = default_storage.save("dataset/" + zip_filename, ContentFile(in_memory_zip.read()))
    
    # Returns the path where the ZIP file was saved
    return path

@login_required(login_url='/login')
def UploadDataset(request):
    """Function to allow users to upload datasets and prevent them from accessing the page if they aren't logged in."""
    # Handles file upload on POST request.
    if request.method == "POST":
        mapper=json.loads(request.POST.get("directories"))
        json_file=request.FILES.get("json-file")

        # Reads and parses the JSON file.
        json_data=json_file.read()
        metadata=json.loads(json_data)
        metadata['folder_structure'] = mapper   
        path=upload_and_zip_folder(request,mapper,metadata)
        # Creates a new DatasetRegistry entry with the uploaded files and parsed metadata.
        data=DatasetRegistry.objects.create(
            owner=request.user,
            dataset_file=path,
            metadata_file= metadata
        )
        
        # Processes and stores keywords from the metadata if they exist.
        if metadata['basic_identity']['keywords']:
            keywords_array=metadata['basic_identity']['keywords'].split(',');
            for keyword in keywords_array:
                # Checks if the keyword already exists, increments dataset_count if it does, or creates a new entry.
                obj=Keyword.objects.filter(name=keyword).first()
                if obj:
                   obj.dataset_count= obj.dataset_count+1
                   obj.save()
                else:
                    Keyword.objects.create(name=keyword,dataset_count=1)

        # Renders the upload page with a success message.
        messages.success(request,'Your dataset has been successfully uploaded.')
        return HttpResponseRedirect('/dataset/upload') 

    # Renders the upload page for GET requests or initial page load.
    return render(request,'dataset/upload_dataset.html')  

def BrowseDatasets(request):
    """Function to allow users to browse the datasets, with dynamic queries to prevent the web-app overloading."""
    datasets=[]
    keyword=''
    format=''
    
    # Handles keyword or file format extraction from POST or GET request.
    print(request.POST)
    if request.method=='POST':
        keyword=request.POST.get('keyword')
        format=request.POST.get('file-format') 

    if  request.method=='GET' and keyword=='':
         keyword=request.GET.get('keyword') or ''
    print('keyword==>',keyword,'format==>',format)
    # Filters datasets based on the title, keywords or Format.
    if   keyword == '' and format == '':
         datasets=DatasetRegistry.objects.all().order_by('id')
    else:
         query=Q()
         if keyword:
             query|=Q(metadata_file__basic_identity__title__icontains=keyword)
             query|=Q(metadata_file__basic_identity__keywords__icontains=keyword)
         if format:
             query|=Q(metadata_file__usage__format__icontains=format)
         print("final query==>",query)
         datasets=DatasetRegistry.objects.filter(query).order_by('id')
    
    # Handles pagination.
    count="10"
    if request.GET.get('count') and request.GET.get('count') in ['5','20','50']:
        count=request.GET.get('count')
    paginator=Paginator(datasets, count)

    # Gets the current page of datasets.
    page_num=request.GET.get('page')
    selected_datasets = paginator.get_page(page_num)

    # Retrieves top keywords for display in the filter section.
    #found_dataset_keyword=datasets.extra(select={"keywords":"metadata_file->>'basic_identity__keywords'"}).values('keywords').values('keywords')
    #found_dataset_keyword=datasets.annotate(keywords=instance)
    #print(found_dataset_keyword)
    keywords=Keyword.objects.filter().order_by('-dataset_count')[:10]

    # Renders the browsing page with the selected datasets and pagination controls.
    return render(request, 'dataset/browse_datasets.html', {
        'selected_datasets': selected_datasets,
        'current_page':selected_datasets.number,
        'end_page':selected_datasets.paginator.num_pages,
        'has_next':selected_datasets.has_next(),
        'has_prev':selected_datasets.has_previous(),
        'prev':selected_datasets.number - 1,
        'next' :selected_datasets.number + 1,
        'count':count,
        'keywords':keywords,
        })

def ViewDataset(request, dataset_id):
    """Function that retrieves and displays information about a selected dataset."""
    # Attempts to retrieve the dataset by ID.
    data=DatasetRegistry.objects.filter(id=dataset_id)
    datasetInfo={}

    # If the dataset exists, populates the information to pass to the template.
    if len(data):
        datasetInfo=data[0]

    # Renders the dataset view template with dataset information
    return render(request, 'dataset/view_dataset.html',{'datasetInfo':datasetInfo})

def DownloadDataset(request, dataset_id):
    """Function that increments the download count for a dataset and redirects to its file URL for downloading."""
    # Attempts to retrieve the dataset by ID.
    data=DatasetRegistry.objects.filter(id=dataset_id)
    if len(data):
       obj=data[0];
       # Increments the download counter for the dataset.
       obj.download_count=obj.download_count+1
       obj.save()
       # Redirects to the dataset file's URL for download.
       return redirect(obj.dataset_file.url)
    
    # Redirects to the dataset viewing page.
    return redirect('/dataset/browse/'+str(dataset_id))

@login_required(login_url='/login')
def EditDataset(request, dataset_id):
    """Function that allows the owner or a moderator to edit a dataset's file and metadata."""
    # Attempts to retrieve the dataset by ID.
    data=DatasetRegistry.objects.filter(id=dataset_id).first()
    
     # Redirects if the current user is not the owner or a moderator.
    if data.owner.id != request.user.id or not request.user.is_moderator:
        return redirect('/dataset/browse/'+str(dataset_id))

    # Handles dataset update on POST request.
    if request.method == "POST":
        # Retrieves the existing dataset and metadata for the dataset.
        dataset_file=request.FILES.get("dataset-file")
        json_file=request.FILES.get("json-file")

        # Updates the dataset file if a new one is provided.
        if dataset_file:
            data.dataset_file=dataset_file
        if json_file:
            json_data=json_file.read()
            
            # Deletes existing keywords from the dataset.
            prev_keyword=data.metadata_file['basic_identity']['keywords'].split(',')
            for keyword in prev_keyword:
                obj=Keyword.objects.filter(name=keyword).first()
                if obj:
                    if obj.dataset_count == 0:
                       obj.delete()
                    else:
                        obj.dataset_count=obj.dataset_count-1
                        obj.save()
            
            # Uploads new keywords from the dataset.
            new_keyword=json.loads(json_data)['basic_identity']['keywords'].split(',')
            for keyword in new_keyword:
                obj=Keyword.objects.filter(name=keyword).first()
                if obj:
                   obj.dataset_count= obj.dataset_count+1
                   obj.save()
                else:
                    Keyword.objects.create(name=keyword,dataset_count=1)
            
            # Updates the metadata file with the new data.
            data.metadata_file= json.loads(json_data)

        # Saves the changes to the dataset.
        data.save()

        # Renders the edit page with a success message.
        return render(request, 'dataset/edit_dataset.html', {'datasetInfo':data,'edited':True})
    
    # Renders the edit page for GET requests or if the user has permission but hasn't submitted changes yet.
    return render(request, 'dataset/edit_dataset.html', {'datasetInfo':data})

@login_required(login_url='/login')
def DeleteDataset(request, dataset_id):
    """Function that deletes a specific dataset, adjusting keyword counts accordingly."""
    
    # Attempts to retrieve the dataset by ID.
    data=DatasetRegistry.objects.filter(id=dataset_id).first()

    # Checks for dataset existence and if the user has the right to delete it.
    if data.owner.id != request.user.id or not request.user.is_moderator:
        # Redirects to the viewing page if the user lacks permissions.
        return redirect('/dataset/browse/'+str(dataset_id))
    
    # Processes and decrements keyword counts associated with the dataset.
    metadata=data.metadata_file
    if metadata['basic_identity']['keywords']:
      keywords_array=metadata['basic_identity']['keywords'].split(',');
      for keyword in keywords_array:
        obj=Keyword.objects.filter(name=keyword).first()
        if obj:
            if obj.dataset_count == 0:
                # Deletes the keyword if its count drops to zero.
               obj.delete()
            else:
                # Otherwise, saves the updated count.
                obj.dataset_count=obj.dataset_count-1
                obj.save()
    
    # Deletes the dataset.
    data.delete()

    # Redirects to the dataset browsing page after successful deletion.
    return redirect('/dataset/browse')
