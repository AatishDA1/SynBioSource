from django.shortcuts import render,redirect
from .models import DatasetRegistry,Keyword
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, F, Func, Value, CharField, IntegerField
from django.db.models.functions import Cast
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

def valid_number(value):
    """Function to check if a value is a valid number when uploading/editing datasets."""
    try:
       return float(value)
    except ValueError:
        return False
    
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
    
    # Returns the path where the ZIP file was saved.
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

        # Processes and stores numerical fields from the metadata.
         # General
        try:
            if valid_number(metadata['dataset_creation']['general']['number_of_samples']):
                data.number_of_samples=valid_number(metadata['dataset_creation']['general']['number_of_samples'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_creation']['general']['total_participants']):
                data.total_participants=valid_number(metadata['dataset_creation']['general']['total_participants'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['general']['dataset_size']):
                data.dataset_size=valid_number(metadata['dataset_composition']['general']['dataset_size'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['general']['number_of_files']):
                data.number_of_files=valid_number(metadata['dataset_composition']['general']['number_of_files'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['general']['average_file_size']):
                data.average_file_size=valid_number(metadata['dataset_composition']['general']['average_file_size'])
        except KeyError:
            pass
        
         # Other File Types
        try:
            if valid_number(metadata['dataset_composition']['excel']['average_sheets']):
                data.average_sheets=valid_number(metadata['dataset_composition']['excel']['average_sheets'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['image']['average_resolution']):
                data.average_resolution=valid_number(metadata['dataset_composition']['image']['average_resolution'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['video']['average_duration']):
                data.video_average_duration=valid_number(metadata['dataset_composition']['video']['average_duration'])
        except KeyError:
            pass        
        try:
            if valid_number(metadata['dataset_composition']['audio']['average_duration']):
                data.audio_average_duration=valid_number(metadata['dataset_composition']['audio']['average_duration'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['audio']['average_bitrate']):
                data.average_bitrate=valid_number(metadata['dataset_composition']['audio']['average_bitrate'])
        except KeyError:
            pass
        
         # FASTA
        try:
            if valid_number(metadata['dataset_composition']['fasta']['general_info']['minimum_sequence_length']):
                data.fasta_minimum_sequence_length=valid_number(metadata['dataset_composition']['fasta']['general_info']['minimum_sequence_length'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['fasta']['general_info']['maximum_sequence_length']):
                data.fasta_maximum_sequence_length=valid_number(metadata['dataset_composition']['fasta']['general_info']['maximum_sequence_length'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['fasta']['sequencing_info']['coverage_depth']):
                data.fasta_coverage_depth=valid_number(metadata['dataset_composition']['fasta']['sequencing_info']['coverage_depth'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['fasta']['sequencing_info']['error_rate']):
                data.fasta_error_rate=valid_number(metadata['dataset_composition']['fasta']['sequencing_info']['error_rate'])
        except KeyError:
            pass
        
         # GenBank
        try:
            if valid_number(metadata['dataset_composition']['genbank']['general_info']['minimum_sequence_length']):
                data.genbank_minimum_sequence_length=valid_number(metadata['dataset_composition']['genbank']['general_info']['minimum_sequence_length'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['genbank']['general_info']['maximum_sequence_length']):
                data.genbank_maximum_sequence_length=valid_number(metadata['dataset_composition']['genbank']['general_info']['maximum_sequence_length'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['genbank']['sequencing_info']['coverage_depth']):
                data.genbank_coverage_depth=valid_number(metadata['dataset_composition']['genbank']['sequencing_info']['coverage_depth'])
        except KeyError:
            pass
        try:
            if valid_number(metadata['dataset_composition']['genbank']['sequencing_info']['error_rate']):
                data.genbank_error_rate=valid_number(metadata['dataset_composition']['genbank']['sequencing_info']['error_rate'])
        except KeyError:
            pass
        
        # Saves the dataset to the database.
        data.save()
        
        
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
    # Initializes the list of datasets to be returned.
    datasets=[]
    
    # Initializes variables relating to the datasets' basic identity. 
    keyword=''

    # Initializes variables relating to the datasets' creation.
    data_origin = ''
    software_used = ''
    study_type = ''
    instrumentation = ''
    protocols = ''
    study_start_date = ''
    study_end_date = ''
    min_number_of_samples = ''
    max_number_of_samples = ''
    min_participants = ''
    max_participants = ''
    dataset_status = ''
    raw_data = ''
    cleanliness_status = ''
    labeled_status = ''
    train_split = ''
    validation_split = ''
    test_split = ''

    # Initializes variables relating to the datasets' composition.
     # General
    format=''
    min_dataset_size=''
    max_dataset_size=''
    min_number_of_files=''
    max_number_of_files=''
    min_average_file_size=''
    max_average_file_size=''
     # CSV
    delimiter=''
    has_header=''
     # Excel
    has_macros=''
    min_sheets=''
    max_sheets=''
     # Images
    image_file_type=''
    min_resolution=''
    max_resolution=''
    color_mode=''
    image_processing=''
     # Videos
    video_file_type=''
    min_video_duration=''
    max_video_duration=''
    video_resolution=''
    video_processing=''
     # Audio
    audio_file_type=''
    min_audio_duration=''
    max_audio_duration=''
    min_bitrate=''
    max_bitrate=''
    audio_processing=''
     # FASTA
    fasta_sequence_type=''
    fasta_organism_group=''
    fasta_minimum_sequence_length=''
    fasta_maximum_sequence_length=''
    fasta_sequencing_method=''
    fasta_min_coverage_depth=''
    fasta_max_coverage_depth=''
    fasta_min_error_rate=''
    fasta_max_error_rate=''
    fasta_NCBI_Taxonomy_ID=''
    fasta_GenBank_Accession_Number=''
    fasta_UniProt_ID=''
     # GenBank
    genbank_sequence_type=''
    genbank_organism_group=''
    genbank_minimum_sequence_length=''
    genbank_maximum_sequence_length=''
    genbank_sequencing_method=''
    genbank_min_coverage_depth=''
    genbank_max_coverage_depth=''
    genbank_min_error_rate=''
    genbank_max_error_rate=''
    genbank_NCBI_Taxonomy_ID=''
    genbank_GenBank_Accession_Number=''
    genbank_UniProt_ID=''
     # Matlab
    matlab_version=''
    variables_stored=''
    toolboxes_used=''
     # Text
    encoding=''
    language=''
     # PDF
    text_extractable=''
    pdf_version=''

    # Handles the extraction of the search parameters following a submission of the form.
    if request.method=='POST':
        keyword=request.POST.get('keyword')
        # Dataset Creation
        data_origin=request.POST.get('data_origin')
        software_used=request.POST.get('software_used')
        study_type=request.POST.get('study_type')
        instrumentation=request.POST.get('instrumentation')
        protocols=request.POST.get('protocols')
        study_start_date=request.POST.get('study_start_date')
        study_end_date=request.POST.get('study_end_date')
        min_number_of_samples=request.POST.get('min_number_of_samples')
        max_number_of_samples=request.POST.get('max_number_of_samples')
        min_participants=request.POST.get('min_participants')
        max_participants=request.POST.get('max_participants')
        dataset_status=request.POST.get('dataset_status')
        raw_data=request.POST.get('raw_data')
        cleanliness_status=request.POST.get('data_cleanliness')
        labeled_status=request.POST.get('labeled')
        train_split=request.POST.get('train_split')
        validation_split=request.POST.get('validation_split')
        test_split=request.POST.get('test_split')
        
        # Dataset Composition
         # General
        format=request.POST.get('file-format') 
        min_dataset_size=request.POST.get('min_dataset_size')
        max_dataset_size=request.POST.get('max_dataset_size')
        min_number_of_files=request.POST.get('min_number_of_files')
        max_number_of_files=request.POST.get('max_number_of_files')
        min_average_file_size=request.POST.get('min_average_file_size')
        max_average_file_size=request.POST.get('max_average_file_size')
         # CSV
        delimiter=request.POST.get('delimiter')
        has_header=request.POST.get('has_header')
         # Excel
        has_macros=request.POST.get('has_macros')
        min_sheets=request.POST.get('min_sheets')
        max_sheets=request.POST.get('max_sheets')
         # Images
        image_file_type=request.POST.get('image_file_type')
        min_resolution=request.POST.get('min_resolution')
        max_resolution=request.POST.get('max_resolution')
        color_mode=request.POST.get('color_mode')
        image_processing=request.POST.get('image_processing')
         # Videos
        video_file_type=request.POST.get('video_file_type')
        min_video_duration=request.POST.get('min_video_duration')
        max_video_duration=request.POST.get('max_video_duration')
        video_resolution=request.POST.get('video_resolution')
        video_processing=request.POST.get('video_processing')
         # Audio
        audio_file_type=request.POST.get('audio_file_type')
        min_audio_duration=request.POST.get('min_audio_duration')
        max_audio_duration=request.POST.get('max_audio_duration')
        min_bitrate=request.POST.get('min_bitrate')
        max_bitrate=request.POST.get('max_bitrate')
        audio_processing=request.POST.get('audio_processing')
         # FASTA
        fasta_sequence_type=request.POST.get('fasta_sequence_type')
        fasta_organism_group=request.POST.get('fasta_organism_group')
        fasta_minimum_sequence_length=request.POST.get('fasta_minimum_sequence_length')
        fasta_maximum_sequence_length=request.POST.get('fasta_maximum_sequence_length')
        fasta_sequencing_method=request.POST.get('fasta_sequencing_method')
        fasta_min_coverage_depth=request.POST.get('fasta_min_coverage_depth')
        fasta_max_coverage_depth=request.POST.get('fasta_max_coverage_depth')
        fasta_min_error_rate=request.POST.get('fasta_min_error_rate')
        fasta_max_error_rate=request.POST.get('fasta_max_error_rate')
        fasta_NCBI_Taxonomy_ID=request.POST.get('fasta_NCBI_Taxonomy_ID')
        fasta_GenBank_Accession_Number=request.POST.get('fasta_GenBank_Accession_Number')
        fasta_UniProt_ID=request.POST.get('fasta_UniProt_ID')
         # GenBank
        genbank_sequence_type=request.POST.get('genbank_sequence_type')
        genbank_organism_group=request.POST.get('genbank_organism_group')
        genbank_minimum_sequence_length=request.POST.get('genbank_minimum_sequence_length')
        genbank_maximum_sequence_length=request.POST.get('genbank_maximum_sequence_length')
        genbank_sequencing_method=request.POST.get('genbank_sequencing_method')
        genbank_min_coverage_depth=request.POST.get('genbank_min_coverage_depth')
        genbank_max_coverage_depth=request.POST.get('genbank_max_coverage_depth')
        genbank_min_error_rate=request.POST.get('genbank_min_error_rate')
        genbank_max_error_rate=request.POST.get('genbank_max_error_rate')
        genbank_NCBI_Taxonomy_ID=request.POST.get('genbank_NCBI_Taxonomy_ID')
        genbank_GenBank_Accession_Number=request.POST.get('genbank_GenBank_Accession_Number')
        genbank_UniProt_ID=request.POST.get('genbank_UniProt_ID')
         # Matlab
        matlab_version=request.POST.get('matlab_version')
        variables_stored=request.POST.get('variables_stored')
        toolboxes_used=request.POST.get('toolboxes_used')
         # Text
        encoding=request.POST.get('encoding')
        language=request.POST.get('language')
         # PDF
        text_extractable=request.POST.get('text_extractable')
        pdf_version=request.POST.get('pdf_version')

    # Keyword Handling
    if  request.method=='GET' and keyword=='':
         keyword=request.GET.get('keyword') or ''
    
    # Filters datasets based on search parameters specified with Django QuerySet Field Lookups.
    # If no search parameters are specified, returns all datasets.
    if   keyword == '' and \
            data_origin == '' and \
            software_used == '' and \
            study_type == '' and \
            instrumentation == '' and \
            protocols == '' and \
            study_start_date == '' and \
            study_end_date == '' and \
            min_number_of_samples == '' and max_number_of_samples == '' and \
            min_participants == '' and max_participants == '' and \
            dataset_status == '' and \
            raw_data == '' and \
            cleanliness_status == '' and \
            labeled_status == '' and \
            train_split == '' and \
            validation_split == '' and \
            test_split == '' and \
            format == '' and \
            min_dataset_size == '' and max_dataset_size == '' and \
            min_number_of_files == '' and max_number_of_files == '' and \
            min_average_file_size == '' and max_average_file_size == '' and \
            delimiter == '' and \
            has_header == '' and \
            has_macros == '' and \
            min_sheets == '' and max_sheets == '' and \
            image_file_type == '' and \
            min_resolution == '' and max_resolution == '' and \
            color_mode == '' and \
            image_processing == '' and \
            video_file_type == '' and \
            min_video_duration == '' and max_video_duration == '' and \
            video_resolution == '' and \
            video_processing == '' and \
            audio_file_type == '' and \
            min_audio_duration == '' and max_audio_duration == '' and \
            min_bitrate == '' and max_bitrate == '' and \
            audio_processing == '' and \
            fasta_sequence_type == '' and \
            fasta_organism_group == '' and \
            fasta_minimum_sequence_length == '' and fasta_maximum_sequence_length == '' and \
            fasta_sequencing_method == '' and \
            fasta_min_coverage_depth == '' and fasta_max_coverage_depth == '' and \
            fasta_min_error_rate == '' and fasta_max_error_rate == '' and \
            fasta_NCBI_Taxonomy_ID == '' and fasta_GenBank_Accession_Number == '' and fasta_UniProt_ID == '' and \
            genbank_sequence_type == '' and \
            genbank_organism_group == '' and \
            genbank_minimum_sequence_length == '' and genbank_maximum_sequence_length == '' and \
            genbank_sequencing_method == '' and \
            genbank_min_coverage_depth == '' and genbank_max_coverage_depth == '' and \
            genbank_min_error_rate == '' and genbank_max_error_rate == '' and \
            genbank_NCBI_Taxonomy_ID == '' and genbank_GenBank_Accession_Number == '' and genbank_UniProt_ID == '' and \
            matlab_version == '' and \
            variables_stored == '' and \
            toolboxes_used == '' and \
            encoding == '' and \
            language == '' and \
            text_extractable == '' and \
            pdf_version == '':
         datasets=DatasetRegistry.objects.all().order_by('id')
    else:
        # Else return datasets based on the search parameters, which are combined with the AND operator.
        # Queries can be either based on categories, exact matches, or range matches (< or >). 
        query=Q()
        if keyword:
            query|=Q(metadata_file__basic_identity__title__icontains=keyword)
            query|=Q(metadata_file__basic_identity__keywords__icontains=keyword)
        # Dataset Creation
        if data_origin:
            query = query & Q(metadata_file__dataset_creation__general__data_origin__icontains=data_origin)
        if software_used:
            query = query & Q(metadata_file__dataset_creation__synthetic_data_details__software_used__icontains=software_used)
        if study_type:
            query = query & Q(metadata_file__dataset_creation__natural_data_details__study_type__icontains=study_type)
        if instrumentation:
            query = query & Q(metadata_file__dataset_creation__natural_data_details__experimental_setup__instrumentation__icontains=instrumentation)
        if study_start_date:
            query = query & Q(metadata_file__dataset_creation__natural_data_details__experimental_setup__study_start_date__icontains=study_start_date)
        if study_end_date:
            query = query & Q(metadata_file__dataset_creation__natural_data_details__experimental_setup__study_end_date__icontains=study_end_date)
        if min_number_of_samples and min_number_of_samples!='':
            query = query & Q(number_of_samples__gte=min_number_of_samples)
        if max_number_of_samples and max_number_of_samples!='':
            query = query & Q(number_of_samples__lte=max_number_of_samples)
        if min_participants and min_participants!='':
            query = query & Q(total_participants__gte=min_participants)
        if max_participants and max_participants!='':
            query = query & Q(total_participants__lte=max_participants)
        if dataset_status:
            query = query & Q(metadata_file__dataset_creation__data_completion__dataset_status__icontains=dataset_status)
        if raw_data:
            query = query & Q(metadata_file__dataset_creation__pre_processing__raw_data__icontains=raw_data)
        if cleanliness_status:
            query = query & Q(metadata_file__dataset_creation__pre_processing__data_cleanliness__cleanliness_status__icontains=cleanliness_status)
        if labeled_status:
            query = query & Q(metadata_file__dataset_creation__pre_processing__labeling__labeled__icontains=labeled_status)
        if train_split and train_split!='':
            query = query & Q(metadata_file__dataset_creation__pre_processing__data_split__train_split__iexact=train_split)
        if validation_split and validation_split!='':
            query = query & Q(metadata_file__dataset_creation__pre_processing__data_split__validation_split__iexact=validation_split)
        if test_split and test_split!='':
            query = query & Q(metadata_file__dataset_creation__pre_processing__data_split__test_split__iexact=test_split)
        
        # Dataset Composition
         # General
        if format:
            query = query & Q(metadata_file__dataset_composition__general__format__icontains=format)
        if min_dataset_size and min_dataset_size!='':
            query = query & Q(dataset_size__gte=min_dataset_size)
        if max_dataset_size and max_dataset_size!='':
            query = query & Q(dataset_size__lte=max_dataset_size)
        if min_number_of_files and min_number_of_files!='':
            query = query & Q(number_of_files__gte=min_number_of_files)
        if max_number_of_files and max_number_of_files!='':
            query = query & Q(number_of_files__lte=max_number_of_files)
        if min_average_file_size and min_average_file_size!='':
            query = query & Q(average_file_size__gte=min_average_file_size)
        if max_average_file_size and max_average_file_size!='':
            query = query & Q(average_file_size__lte=max_average_file_size)
         # CSV
        if delimiter:
            query = query & Q(metadata_file__dataset_composition__csv__delimiter__icontains=delimiter)
        if has_header:
            query = query & Q(metadata_file__dataset_composition__csv__has_header__icontains=has_header)
         # Excel
        if has_macros:
            query = query & Q(metadata_file__dataset_composition__excel__has_macros__icontains=has_macros)
        if min_sheets and min_sheets!='':
            query = query & Q(average_sheets___gte=min_sheets)
        if max_sheets and max_sheets!='':
            query = query & Q(average_sheets___lte=max_sheets)
         # Images
        if image_file_type:
            query = query & Q(metadata_file__dataset_composition__image__file_type__icontains=image_file_type)
        if min_resolution and min_resolution!='':
            query = query & Q(average_resolution__gte=min_resolution)
        if max_resolution and max_resolution!='':
            query = query & Q(average_resolution__lte=max_resolution)
        if color_mode:
            query = query & Q(metadata_file__dataset_composition__image__color_mode__icontains=color_mode)
        if image_processing:
            query = query & Q(metadata_file__dataset_composition__image__image_processing__icontains=image_processing)
         # Videos
        if video_file_type:
            query = query & Q(metadata_file__dataset_composition__video__file_type__icontains=video_file_type)
        if min_video_duration and min_video_duration!='':
            query = query & Q(video_average_duration__gte=min_video_duration)
        if max_video_duration and max_video_duration!='':
            query = query & Q(video_average_duration__lte=max_video_duration)
        if video_resolution:
            query = query & Q(metadata_file__dataset_composition__video__resolution__icontains=video_resolution)
        if video_processing:
            query = query & Q(metadata_file__dataset_composition__video__video_processing__icontains=video_processing)
         # Audio
        if audio_file_type:
            query = query & Q(metadata_file__dataset_composition__audio__file_type__icontains=audio_file_type)
        if min_audio_duration and min_audio_duration!='':
            query = query & Q(audio_average_duration__gte=min_audio_duration)
        if max_audio_duration and max_audio_duration!='':
            query = query & Q(audio_average_duration__lte=max_audio_duration)
        if min_bitrate and min_bitrate!='':
            query = query & Q(average_bitrate__iexact=min_bitrate)
        if max_bitrate and max_bitrate!='':
            query = query & Q(average_bitrate__lte=max_bitrate)
        if audio_processing:
            query = query & Q(metadata_file__dataset_composition__audio__audio_processing__icontains=audio_processing)
         # FASTA
        if fasta_sequence_type:
            query = query & Q(metadata_file__dataset_composition__fasta__general_info__sequence_type__icontains=fasta_sequence_type)
        if fasta_organism_group:
            query = query & Q(metadata_file__dataset_composition__fasta__general_info__organism_group__icontains=fasta_organism_group)
        if fasta_minimum_sequence_length and fasta_minimum_sequence_length!='':
            query = query & Q(fasta_minimum_sequence_length__gte=fasta_minimum_sequence_length)
        if fasta_maximum_sequence_length and fasta_maximum_sequence_length!='':
            query = query & Q(fasta_maximum_sequence_length__lte=fasta_maximum_sequence_length)
        if fasta_sequencing_method:
            query = query & Q(metadata_file__dataset_composition__fasta__sequencing_info__sequencing_method__icontains=fasta_sequencing_method)
        if fasta_min_coverage_depth and fasta_min_coverage_depth!='':
            query = query & Q(fasta_coverage_depth__gte=fasta_min_coverage_depth)
        if fasta_max_coverage_depth and fasta_max_coverage_depth!='':
            query = query & Q(fasta_coverage_depth__lte=fasta_max_coverage_depth)
        if fasta_min_error_rate and fasta_min_error_rate!='':
            query = query & Q(fasta_error_rate__gte=fasta_min_error_rate)
        if fasta_max_error_rate and fasta_max_error_rate!='':
            query = query & Q(fasta_error_rate__lte=fasta_max_error_rate)
        if fasta_NCBI_Taxonomy_ID:
            query = query & Q(metadata_file__dataset_composition__fasta__further_source_details__NCBI_Taxonomy_ID__icontains=fasta_NCBI_Taxonomy_ID)
        if fasta_GenBank_Accession_Number:
            query = query & Q(metadata_file__dataset_composition__fasta__further_source_details__GenBank_Accession_Number__icontains=fasta_GenBank_Accession_Number)
        if fasta_UniProt_ID:
            query = query & Q(metadata_file__dataset_composition__fasta__further_source_details__UniProt_ID__icontains=fasta_UniProt_ID)
         # GenBank
        if genbank_sequence_type:
            query = query & Q(metadata_file__dataset_composition__genbank__general_info__sequence_type__icontains=genbank_sequence_type)
        if genbank_organism_group:
            query = query & Q(metadata_file__dataset_composition__genbank__general_info__organism_group__icontains=genbank_organism_group)
        if genbank_minimum_sequence_length and genbank_minimum_sequence_length!='':
            query = query & Q(genbank_minimum_sequence_length__gte=genbank_minimum_sequence_length)
        if genbank_maximum_sequence_length and genbank_maximum_sequence_length!='':
            query = query & Q(genbank_maximum_sequence_length__lte=genbank_maximum_sequence_length)
        if genbank_sequencing_method:
            query = query & Q(metadata_file__dataset_composition__genbank__sequencing_info__sequencing_method__icontains=genbank_sequencing_method)
        if genbank_min_coverage_depth and genbank_min_coverage_depth!='':
            query = query & Q(genbank_coverage_depth__gte=genbank_min_coverage_depth)
        if genbank_max_coverage_depth and genbank_max_coverage_depth!='':
            query = query & Q(genbank_coverage_depth__lte=genbank_max_coverage_depth)
        if genbank_min_error_rate and genbank_min_error_rate!='':
            query = query & Q(genbank_error_rate__gte=genbank_min_error_rate)
        if genbank_max_error_rate and genbank_max_error_rate!='':
            query = query & Q(genbank_error_rate__lte=genbank_max_error_rate)
        if genbank_NCBI_Taxonomy_ID:
            query = query & Q(metadata_file__dataset_composition__genbank__further_source_details__NCBI_Taxonomy_ID__icontains=genbank_NCBI_Taxonomy_ID)
        if genbank_GenBank_Accession_Number:
            query = query & Q(metadata_file__dataset_composition__genbank__further_source_details__GenBank_Accession_Number__icontains=genbank_GenBank_Accession_Number)
        if genbank_UniProt_ID:
            query = query & Q(metadata_file__dataset_composition__genbank__further_source_details__UniProt_ID__icontains=genbank_UniProt_ID)
         # Matlab
        if matlab_version:
            query = query & Q(metadata_file__dataset_composition__matlab__matlab_version__icontains=matlab_version)
        if variables_stored:
            query = query & Q(metadata_file__dataset_composition__matlab__variables_stored__icontains=variables_stored)
        if toolboxes_used:
            query = query & Q(metadata_file__dataset_composition__matlab__toolboxes_used__icontains=toolboxes_used)
         # Text
        if encoding:
            query = query & Q(metadata_file__dataset_composition__text__encoding__icontains=encoding)
        if language and language!='':
            query = query & Q(metadata_file__dataset_composition__text__language__icontains=language)
         # PDF
        if text_extractable:
            query = query & Q(metadata_file__dataset_composition__pdf__text_extractable__icontains=text_extractable)
        if pdf_version and pdf_version!='':
            query = query & Q(metadata_file__dataset_composition__pdf__pdf_version__iexact=pdf_version)

        datasets=DatasetRegistry.objects.filter(query).order_by('id') 
    
    # Handles pagination.
    count="10"
    if request.GET.get('count') and request.GET.get('count') in ['5','20','50']:
        count=request.GET.get('count')
    paginator=Paginator(datasets, count)

    # Gets the current page of datasets.
    page_num=request.GET.get('page')
    selected_datasets = paginator.get_page(page_num)

    # Retrieves the keywords based on datasets selected.
    allKeywords =[]
    for dataset in selected_datasets:
        allKeywords+= dataset.metadata_file['basic_identity']['keywords'].split(',')

    # Returns the top 10 keywords.
    keywords=Keyword.objects.filter(name__in=allKeywords).order_by('-dataset_count')[:10]
    
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
    if (data.owner.id != request.user.id) and (not request.user.is_moderator):
        return redirect('/dataset/browse/'+str(dataset_id))

    # Handles dataset update on POST request.
    if request.method == "POST":
        # Retrieves the existing dataset and metadata for the dataset.
        dataset_file=request.FILES.get("dataset-file")
        json_file=request.FILES.get("json-file")
        mapper=json.loads(request.POST.get("directories"))
        json_file=request.FILES.get("json-file")

        # Reads and parses the JSON file.
        json_data=json_file.read()
        metadata=json.loads(json_data)
        metadata['folder_structure'] = mapper   
        path=upload_and_zip_folder(request,mapper,metadata)
        
        # Updates the dataset file if a new one is provided.
        if dataset_file:
            data.dataset_file=path
        if json_file:
            json_data=json.loads(json_data)
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
            new_keyword=json_data['basic_identity']['keywords'].split(',')
            for keyword in new_keyword:
                obj=Keyword.objects.filter(name=keyword).first()
                if obj:
                   obj.dataset_count= obj.dataset_count+1
                   obj.save()
                else:
                    Keyword.objects.create(name=keyword,dataset_count=1)
            
            # Updates the metadata file with the new data.
            data.metadata_file= metadata

            # Processes and stores numerical fields from the metadata.
             # General
            try:
                if valid_number(metadata['dataset_creation']['general']['number_of_samples']):
                    data.number_of_samples=valid_number(metadata['dataset_creation']['general']['number_of_samples'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_creation']['general']['total_participants']):
                    data.total_participants=valid_number(metadata['dataset_creation']['general']['total_participants'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['general']['dataset_size']):
                    data.dataset_size=valid_number(metadata['dataset_composition']['general']['dataset_size'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['general']['number_of_files']):
                    data.number_of_files=valid_number(metadata['dataset_composition']['general']['number_of_files'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['general']['average_file_size']):
                    data.average_file_size=valid_number(metadata['dataset_composition']['general']['average_file_size'])
            except KeyError:
                pass
            
             # Other File Types
            try:
                if valid_number(metadata['dataset_composition']['excel']['average_sheets']):
                    data.average_sheets=valid_number(metadata['dataset_composition']['excel']['average_sheets'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['image']['average_resolution']):
                    data.average_resolution=valid_number(metadata['dataset_composition']['image']['average_resolution'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['video']['average_duration']):
                    data.video_average_duration=valid_number(metadata['dataset_composition']['video']['average_duration'])
            except KeyError:
                pass        
            try:
                if valid_number(metadata['dataset_composition']['audio']['average_duration']):
                    data.audio_average_duration=valid_number(metadata['dataset_composition']['audio']['average_duration'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['audio']['average_bitrate']):
                    data.average_bitrate=valid_number(metadata['dataset_composition']['audio']['average_bitrate'])
            except KeyError:
                pass
            
             # FASTA
            try:
                if valid_number(metadata['dataset_composition']['fasta']['general_info']['minimum_sequence_length']):
                    data.fasta_minimum_sequence_length=valid_number(metadata['dataset_composition']['fasta']['general_info']['minimum_sequence_length'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['fasta']['general_info']['maximum_sequence_length']):
                    data.fasta_maximum_sequence_length=valid_number(metadata['dataset_composition']['fasta']['general_info']['maximum_sequence_length'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['fasta']['sequencing_info']['coverage_depth']):
                    data.fasta_coverage_depth=valid_number(metadata['dataset_composition']['fasta']['sequencing_info']['coverage_depth'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['fasta']['sequencing_info']['error_rate']):
                    data.fasta_error_rate=valid_number(metadata['dataset_composition']['fasta']['sequencing_info']['error_rate'])
            except KeyError:
                pass
            
             # GenBank
            try:
                if valid_number(metadata['dataset_composition']['genbank']['general_info']['minimum_sequence_length']):
                    data.genbank_minimum_sequence_length=valid_number(metadata['dataset_composition']['genbank']['general_info']['minimum_sequence_length'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['genbank']['general_info']['maximum_sequence_length']):
                    data.genbank_maximum_sequence_length=valid_number(metadata['dataset_composition']['genbank']['general_info']['maximum_sequence_length'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['genbank']['sequencing_info']['coverage_depth']):
                    data.genbank_coverage_depth=valid_number(metadata['dataset_composition']['genbank']['sequencing_info']['coverage_depth'])
            except KeyError:
                pass
            try:
                if valid_number(metadata['dataset_composition']['genbank']['sequencing_info']['error_rate']):
                    data.genbank_error_rate=valid_number(metadata['dataset_composition']['genbank']['sequencing_info']['error_rate'])
            except KeyError:
                pass
        
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
    if (data.owner.id != request.user.id) and not (request.user.is_moderator):
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

@login_required(login_url='/login')
def YourDatasets(request):
    """Function to display the datasets uploaded by the current user. Layout is similar to the BrowseDatasets function."""
    # Initializes the list of datasets to be returned.
    datasets=[]
    
    # Initializes variables relating to the datasets' basic identity. 
    keyword=''

    # Initializes variables relating to the datasets' creation.
    data_origin = ''
    software_used = ''
    study_type = ''
    instrumentation = ''
    protocols = ''
    study_start_date = ''
    study_end_date = ''
    min_number_of_samples = ''
    max_number_of_samples = ''
    min_participants = ''
    max_participants = ''
    dataset_status = ''
    raw_data = ''
    cleanliness_status = ''
    labeled_status = ''
    train_split = ''
    validation_split = ''
    test_split = ''

    # Initializes variables relating to the datasets' composition.
     # General
    format=''
    min_dataset_size=''
    max_dataset_size=''
    min_number_of_files=''
    max_number_of_files=''
    min_average_file_size=''
    max_average_file_size=''
     # CSV
    delimiter=''
    has_header=''
     # Excel
    has_macros=''
    min_sheets=''
    max_sheets=''
     # Images
    image_file_type=''
    min_resolution=''
    max_resolution=''
    color_mode=''
    image_processing=''
     # Videos
    video_file_type=''
    min_video_duration=''
    max_video_duration=''
    video_resolution=''
    video_processing=''
     # Audio
    audio_file_type=''
    min_audio_duration=''
    max_audio_duration=''
    min_bitrate=''
    max_bitrate=''
    audio_processing=''
     # FASTA
    fasta_sequence_type=''
    fasta_organism_group=''
    fasta_minimum_sequence_length=''
    fasta_maximum_sequence_length=''
    fasta_sequencing_method=''
    fasta_min_coverage_depth=''
    fasta_max_coverage_depth=''
    fasta_min_error_rate=''
    fasta_max_error_rate=''
    fasta_NCBI_Taxonomy_ID=''
    fasta_GenBank_Accession_Number=''
    fasta_UniProt_ID=''
     # GenBank
    genbank_sequence_type=''
    genbank_organism_group=''
    genbank_minimum_sequence_length=''
    genbank_maximum_sequence_length=''
    genbank_sequencing_method=''
    genbank_min_coverage_depth=''
    genbank_max_coverage_depth=''
    genbank_min_error_rate=''
    genbank_max_error_rate=''
    genbank_NCBI_Taxonomy_ID=''
    genbank_GenBank_Accession_Number=''
    genbank_UniProt_ID=''
     # Matlab
    matlab_version=''
    variables_stored=''
    toolboxes_used=''
     # Text
    encoding=''
    language=''
     # PDF
    text_extractable=''
    pdf_version=''

    # Handles the extraction of the search parameters following a submission of the form.
    if request.method=='POST':
        keyword=request.POST.get('keyword')
        # Dataset Creation
        data_origin=request.POST.get('data_origin')
        software_used=request.POST.get('software_used')
        study_type=request.POST.get('study_type')
        instrumentation=request.POST.get('instrumentation')
        protocols=request.POST.get('protocols')
        study_start_date=request.POST.get('study_start_date')
        study_end_date=request.POST.get('study_end_date')
        min_number_of_samples=request.POST.get('min_number_of_samples')
        max_number_of_samples=request.POST.get('max_number_of_samples')
        min_participants=request.POST.get('min_participants')
        max_participants=request.POST.get('max_participants')
        dataset_status=request.POST.get('dataset_status')
        raw_data=request.POST.get('raw_data')
        cleanliness_status=request.POST.get('data_cleanliness')
        labeled_status=request.POST.get('labeled')
        train_split=request.POST.get('train_split')
        validation_split=request.POST.get('validation_split')
        test_split=request.POST.get('test_split')
        
        # Dataset Composition
         # General
        format=request.POST.get('file-format') 
        min_dataset_size=request.POST.get('min_dataset_size')
        max_dataset_size=request.POST.get('max_dataset_size')
        min_number_of_files=request.POST.get('min_number_of_files')
        max_number_of_files=request.POST.get('max_number_of_files')
        min_average_file_size=request.POST.get('min_average_file_size')
        max_average_file_size=request.POST.get('max_average_file_size')
         # CSV
        delimiter=request.POST.get('delimiter')
        has_header=request.POST.get('has_header')
         # Excel
        has_macros=request.POST.get('has_macros')
        min_sheets=request.POST.get('min_sheets')
        max_sheets=request.POST.get('max_sheets')
         # Images
        image_file_type=request.POST.get('image_file_type')
        min_resolution=request.POST.get('min_resolution')
        max_resolution=request.POST.get('max_resolution')
        color_mode=request.POST.get('color_mode')
        image_processing=request.POST.get('image_processing')
         # Videos
        video_file_type=request.POST.get('video_file_type')
        min_video_duration=request.POST.get('min_video_duration')
        max_video_duration=request.POST.get('max_video_duration')
        video_resolution=request.POST.get('video_resolution')
        video_processing=request.POST.get('video_processing')
         # Audio
        audio_file_type=request.POST.get('audio_file_type')
        min_audio_duration=request.POST.get('min_audio_duration')
        max_audio_duration=request.POST.get('max_audio_duration')
        min_bitrate=request.POST.get('min_bitrate')
        max_bitrate=request.POST.get('max_bitrate')
        audio_processing=request.POST.get('audio_processing')
         # FASTA
        fasta_sequence_type=request.POST.get('fasta_sequence_type')
        fasta_organism_group=request.POST.get('fasta_organism_group')
        fasta_minimum_sequence_length=request.POST.get('fasta_minimum_sequence_length')
        fasta_maximum_sequence_length=request.POST.get('fasta_maximum_sequence_length')
        fasta_sequencing_method=request.POST.get('fasta_sequencing_method')
        fasta_min_coverage_depth=request.POST.get('fasta_min_coverage_depth')
        fasta_max_coverage_depth=request.POST.get('fasta_max_coverage_depth')
        fasta_min_error_rate=request.POST.get('fasta_min_error_rate')
        fasta_max_error_rate=request.POST.get('fasta_max_error_rate')
        fasta_NCBI_Taxonomy_ID=request.POST.get('fasta_NCBI_Taxonomy_ID')
        fasta_GenBank_Accession_Number=request.POST.get('fasta_GenBank_Accession_Number')
        fasta_UniProt_ID=request.POST.get('fasta_UniProt_ID')
         # GenBank
        genbank_sequence_type=request.POST.get('genbank_sequence_type')
        genbank_organism_group=request.POST.get('genbank_organism_group')
        genbank_minimum_sequence_length=request.POST.get('genbank_minimum_sequence_length')
        genbank_maximum_sequence_length=request.POST.get('genbank_maximum_sequence_length')
        genbank_sequencing_method=request.POST.get('genbank_sequencing_method')
        genbank_min_coverage_depth=request.POST.get('genbank_min_coverage_depth')
        genbank_max_coverage_depth=request.POST.get('genbank_max_coverage_depth')
        genbank_min_error_rate=request.POST.get('genbank_min_error_rate')
        genbank_max_error_rate=request.POST.get('genbank_max_error_rate')
        genbank_NCBI_Taxonomy_ID=request.POST.get('genbank_NCBI_Taxonomy_ID')
        genbank_GenBank_Accession_Number=request.POST.get('genbank_GenBank_Accession_Number')
        genbank_UniProt_ID=request.POST.get('genbank_UniProt_ID')
         # Matlab
        matlab_version=request.POST.get('matlab_version')
        variables_stored=request.POST.get('variables_stored')
        toolboxes_used=request.POST.get('toolboxes_used')
         # Text
        encoding=request.POST.get('encoding')
        language=request.POST.get('language')
         # PDF
        text_extractable=request.POST.get('text_extractable')
        pdf_version=request.POST.get('pdf_version')

    # Keyword Handling
    if  request.method=='GET' and keyword=='':
         keyword=request.GET.get('keyword') or ''
    
    # Filters your datasets based on search parameters specified with Django QuerySet Field Lookups.
    # If no search parameters are specified, returns all datasets.
    if   keyword == '' and \
            data_origin == '' and \
            software_used == '' and \
            study_type == '' and \
            instrumentation == '' and \
            protocols == '' and \
            study_start_date == '' and \
            study_end_date == '' and \
            min_number_of_samples == '' and max_number_of_samples == '' and \
            min_participants == '' and max_participants == '' and \
            dataset_status == '' and \
            raw_data == '' and \
            cleanliness_status == '' and \
            labeled_status == '' and \
            train_split == '' and \
            validation_split == '' and \
            test_split == '' and \
            format == '' and \
            min_dataset_size == '' and max_dataset_size == '' and \
            min_number_of_files == '' and max_number_of_files == '' and \
            min_average_file_size == '' and max_average_file_size == '' and \
            delimiter == '' and \
            has_header == '' and \
            has_macros == '' and \
            min_sheets == '' and max_sheets == '' and \
            image_file_type == '' and \
            min_resolution == '' and max_resolution == '' and \
            color_mode == '' and \
            image_processing == '' and \
            video_file_type == '' and \
            min_video_duration == '' and max_video_duration == '' and \
            video_resolution == '' and \
            video_processing == '' and \
            audio_file_type == '' and \
            min_audio_duration == '' and max_audio_duration == '' and \
            min_bitrate == '' and max_bitrate == '' and \
            audio_processing == '' and \
            fasta_sequence_type == '' and \
            fasta_organism_group == '' and \
            fasta_minimum_sequence_length == '' and fasta_maximum_sequence_length == '' and \
            fasta_sequencing_method == '' and \
            fasta_min_coverage_depth == '' and fasta_max_coverage_depth == '' and \
            fasta_min_error_rate == '' and fasta_max_error_rate == '' and \
            fasta_NCBI_Taxonomy_ID == '' and fasta_GenBank_Accession_Number == '' and fasta_UniProt_ID == '' and \
            genbank_sequence_type == '' and \
            genbank_organism_group == '' and \
            genbank_minimum_sequence_length == '' and genbank_maximum_sequence_length == '' and \
            genbank_sequencing_method == '' and \
            genbank_min_coverage_depth == '' and genbank_max_coverage_depth == '' and \
            genbank_min_error_rate == '' and genbank_max_error_rate == '' and \
            genbank_NCBI_Taxonomy_ID == '' and genbank_GenBank_Accession_Number == '' and genbank_UniProt_ID == '' and \
            matlab_version == '' and \
            variables_stored == '' and \
            toolboxes_used == '' and \
            encoding == '' and \
            language == '' and \
            text_extractable == '' and \
            pdf_version == '':
         
         # Ensures only datasets owned by the current user are returned.
         datasets=DatasetRegistry.objects.filter(owner=request.user.id).order_by('id')
    else:
        # Else return datasets based on the search parameters, which are combined with the AND operator.
        # Queries can be either based on categories, exact matches, or range matches (< or >). 
        query=Q(owner=request.user.id)
        if keyword:
            query|=Q(metadata_file__basic_identity__title__icontains=keyword)
            query|=Q(metadata_file__basic_identity__keywords__icontains=keyword)
        # Dataset Creation
        if data_origin:
            query = query & Q(metadata_file__dataset_creation__general__data_origin__icontains=data_origin)
        if software_used:
            query = query & Q(metadata_file__dataset_creation__synthetic_data_details__software_used__icontains=software_used)
        if study_type:
            query = query & Q(metadata_file__dataset_creation__natural_data_details__study_type__icontains=study_type)
        if instrumentation:
            query = query & Q(metadata_file__dataset_creation__natural_data_details__experimental_setup__instrumentation__icontains=instrumentation)
        if study_start_date:
            query = query & Q(metadata_file__dataset_creation__natural_data_details__experimental_setup__study_start_date__icontains=study_start_date)
        if study_end_date:
            query = query & Q(metadata_file__dataset_creation__natural_data_details__experimental_setup__study_end_date__icontains=study_end_date)
        if min_number_of_samples and min_number_of_samples!='':
            query = query & Q(number_of_samples__gte=min_number_of_samples)
        if max_number_of_samples and max_number_of_samples!='':
            query = query & Q(number_of_samples__lte=max_number_of_samples)
        if min_participants and min_participants!='':
            query = query & Q(total_participants__gte=min_participants)
        if max_participants and max_participants!='':
            query = query & Q(total_participants__lte=max_participants)
        if dataset_status:
            query = query & Q(metadata_file__dataset_creation__data_completion__dataset_status__icontains=dataset_status)
        if raw_data:
            query = query & Q(metadata_file__dataset_creation__pre_processing__raw_data__icontains=raw_data)
        if cleanliness_status:
            query = query & Q(metadata_file__dataset_creation__pre_processing__data_cleanliness__cleanliness_status__icontains=cleanliness_status)
        if labeled_status:
            query = query & Q(metadata_file__dataset_creation__pre_processing__labeling__labeled__icontains=labeled_status)
        if train_split and train_split!='':
            query = query & Q(metadata_file__dataset_creation__pre_processing__data_split__train_split__iexact=train_split)
        if validation_split and validation_split!='':
            query = query & Q(metadata_file__dataset_creation__pre_processing__data_split__validation_split__iexact=validation_split)
        if test_split and test_split!='':
            query = query & Q(metadata_file__dataset_creation__pre_processing__data_split__test_split__iexact=test_split)
        
        # Dataset Composition
         # General
        if format:
            query = query & Q(metadata_file__dataset_composition__general__format__icontains=format)
        if min_dataset_size and min_dataset_size!='':
            query = query & Q(dataset_size__gte=min_dataset_size)
        if max_dataset_size and max_dataset_size!='':
            query = query & Q(dataset_size__lte=max_dataset_size)
        if min_number_of_files and min_number_of_files!='':
            query = query & Q(number_of_files__gte=min_number_of_files)
        if max_number_of_files and max_number_of_files!='':
            query = query & Q(number_of_files__lte=max_number_of_files)
        if min_average_file_size and min_average_file_size!='':
            query = query & Q(average_file_size__gte=min_average_file_size)
        if max_average_file_size and max_average_file_size!='':
            query = query & Q(average_file_size__lte=max_average_file_size)
         # CSV
        if delimiter:
            query = query & Q(metadata_file__dataset_composition__csv__delimiter__icontains=delimiter)
        if has_header:
            query = query & Q(metadata_file__dataset_composition__csv__has_header__icontains=has_header)
         # Excel
        if has_macros:
            query = query & Q(metadata_file__dataset_composition__excel__has_macros__icontains=has_macros)
        if min_sheets and min_sheets!='':
            query = query & Q(average_sheets___gte=min_sheets)
        if max_sheets and max_sheets!='':
            query = query & Q(average_sheets___lte=max_sheets)
         # Images
        if image_file_type:
            query = query & Q(metadata_file__dataset_composition__image__file_type__icontains=image_file_type)
        if min_resolution and min_resolution!='':
            query = query & Q(average_resolution__gte=min_resolution)
        if max_resolution and max_resolution!='':
            query = query & Q(average_resolution__lte=max_resolution)
        if color_mode:
            query = query & Q(metadata_file__dataset_composition__image__color_mode__icontains=color_mode)
        if image_processing:
            query = query & Q(metadata_file__dataset_composition__image__image_processing__icontains=image_processing)
         # Videos
        if video_file_type:
            query = query & Q(metadata_file__dataset_composition__video__file_type__icontains=video_file_type)
        if min_video_duration and min_video_duration!='':
            query = query & Q(video_average_duration__gte=min_video_duration)
        if max_video_duration and max_video_duration!='':
            query = query & Q(video_average_duration__lte=max_video_duration)
        if video_resolution:
            query = query & Q(metadata_file__dataset_composition__video__resolution__icontains=video_resolution)
        if video_processing:
            query = query & Q(metadata_file__dataset_composition__video__video_processing__icontains=video_processing)
         # Audio
        if audio_file_type:
            query = query & Q(metadata_file__dataset_composition__audio__file_type__icontains=audio_file_type)
        if min_audio_duration and min_audio_duration!='':
            query = query & Q(audio_average_duration__gte=min_audio_duration)
        if max_audio_duration and max_audio_duration!='':
            query = query & Q(audio_average_duration__lte=max_audio_duration)
        if min_bitrate and min_bitrate!='':
            query = query & Q(average_bitrate__iexact=min_bitrate)
        if max_bitrate and max_bitrate!='':
            query = query & Q(average_bitrate__lte=max_bitrate)
        if audio_processing:
            query = query & Q(metadata_file__dataset_composition__audio__audio_processing__icontains=audio_processing)
         # FASTA
        if fasta_sequence_type:
            query = query & Q(metadata_file__dataset_composition__fasta__general_info__sequence_type__icontains=fasta_sequence_type)
        if fasta_organism_group:
            query = query & Q(metadata_file__dataset_composition__fasta__general_info__organism_group__icontains=fasta_organism_group)
        if fasta_minimum_sequence_length and fasta_minimum_sequence_length!='':
            query = query & Q(fasta_minimum_sequence_length__gte=fasta_minimum_sequence_length)
        if fasta_maximum_sequence_length and fasta_maximum_sequence_length!='':
            query = query & Q(fasta_maximum_sequence_length__lte=fasta_maximum_sequence_length)
        if fasta_sequencing_method:
            query = query & Q(metadata_file__dataset_composition__fasta__sequencing_info__sequencing_method__icontains=fasta_sequencing_method)
        if fasta_min_coverage_depth and fasta_min_coverage_depth!='':
            query = query & Q(fasta_coverage_depth__gte=fasta_min_coverage_depth)
        if fasta_max_coverage_depth and fasta_max_coverage_depth!='':
            query = query & Q(fasta_coverage_depth__lte=fasta_max_coverage_depth)
        if fasta_min_error_rate and fasta_min_error_rate!='':
            query = query & Q(fasta_error_rate__gte=fasta_min_error_rate)
        if fasta_max_error_rate and fasta_max_error_rate!='':
            query = query & Q(fasta_error_rate__lte=fasta_max_error_rate)
        if fasta_NCBI_Taxonomy_ID:
            query = query & Q(metadata_file__dataset_composition__fasta__further_source_details__NCBI_Taxonomy_ID__icontains=fasta_NCBI_Taxonomy_ID)
        if fasta_GenBank_Accession_Number:
            query = query & Q(metadata_file__dataset_composition__fasta__further_source_details__GenBank_Accession_Number__icontains=fasta_GenBank_Accession_Number)
        if fasta_UniProt_ID:
            query = query & Q(metadata_file__dataset_composition__fasta__further_source_details__UniProt_ID__icontains=fasta_UniProt_ID)
         # GenBank
        if genbank_sequence_type:
            query = query & Q(metadata_file__dataset_composition__genbank__general_info__sequence_type__icontains=genbank_sequence_type)
        if genbank_organism_group:
            query = query & Q(metadata_file__dataset_composition__genbank__general_info__organism_group__icontains=genbank_organism_group)
        if genbank_minimum_sequence_length and genbank_minimum_sequence_length!='':
            query = query & Q(genbank_minimum_sequence_length__gte=genbank_minimum_sequence_length)
        if genbank_maximum_sequence_length and genbank_maximum_sequence_length!='':
            query = query & Q(genbank_maximum_sequence_length__lte=genbank_maximum_sequence_length)
        if genbank_sequencing_method:
            query = query & Q(metadata_file__dataset_composition__genbank__sequencing_info__sequencing_method__icontains=genbank_sequencing_method)
        if genbank_min_coverage_depth and genbank_min_coverage_depth!='':
            query = query & Q(genbank_coverage_depth__gte=genbank_min_coverage_depth)
        if genbank_max_coverage_depth and genbank_max_coverage_depth!='':
            query = query & Q(genbank_coverage_depth__lte=genbank_max_coverage_depth)
        if genbank_min_error_rate and genbank_min_error_rate!='':
            query = query & Q(genbank_error_rate__gte=genbank_min_error_rate)
        if genbank_max_error_rate and genbank_max_error_rate!='':
            query = query & Q(genbank_error_rate__lte=genbank_max_error_rate)
        if genbank_NCBI_Taxonomy_ID:
            query = query & Q(metadata_file__dataset_composition__genbank__further_source_details__NCBI_Taxonomy_ID__icontains=genbank_NCBI_Taxonomy_ID)
        if genbank_GenBank_Accession_Number:
            query = query & Q(metadata_file__dataset_composition__genbank__further_source_details__GenBank_Accession_Number__icontains=genbank_GenBank_Accession_Number)
        if genbank_UniProt_ID:
            query = query & Q(metadata_file__dataset_composition__genbank__further_source_details__UniProt_ID__icontains=genbank_UniProt_ID)
         # Matlab
        if matlab_version:
            query = query & Q(metadata_file__dataset_composition__matlab__matlab_version__icontains=matlab_version)
        if variables_stored:
            query = query & Q(metadata_file__dataset_composition__matlab__variables_stored__icontains=variables_stored)
        if toolboxes_used:
            query = query & Q(metadata_file__dataset_composition__matlab__toolboxes_used__icontains=toolboxes_used)
        # Text
        if encoding:
            query = query & Q(metadata_file__dataset_composition__text__encoding__icontains=encoding)
        if language and language!='':
            query = query & Q(metadata_file__dataset_composition__text__language__icontains=language)
        # PDF
        if text_extractable:
            query = query & Q(metadata_file__dataset_composition__pdf__text_extractable__icontains=text_extractable)
        if pdf_version and pdf_version!='':
            query = query & Q(metadata_file__dataset_composition__pdf__pdf_version__iexact=pdf_version)

        datasets=DatasetRegistry.objects.filter(query).order_by('id') 
    
    # Handles pagination.
    count="10"
    if request.GET.get('count') and request.GET.get('count') in ['5','20','50']:
        count=request.GET.get('count')
    paginator=Paginator(datasets, count)

    # Gets the current page of datasets.
    page_num=request.GET.get('page')
    selected_datasets = paginator.get_page(page_num)

    # Retrieves the keywords based on datasets selected.
    allKeywords =[]
    for dataset in selected_datasets:
        allKeywords+= dataset.metadata_file['basic_identity']['keywords'].split(',')

    # Returns the top 10 keywords.
    keywords=Keyword.objects.filter(name__in=allKeywords).order_by('-dataset_count')[:10]
    
    # Renders the browsing page with the selected datasets you own and pagination controls.
    return render(request, 'dataset/your_datasets.html', {
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