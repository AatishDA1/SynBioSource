from django.shortcuts import render
from django.contrib.auth.models import Group, User
from django.db.models import Q
from rest_framework import permissions, viewsets, generics, views
from rest_framework.response import Response    

from api.serializers import DatasetSerializerList, DatasetSerializerDetails
from dataset.models import DatasetRegistry
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Create your views here.

class DatasetListView(viewsets.ModelViewSet):
    """
    GET API endpoint that lists the available datasets.
    """
    queryset = DatasetRegistry.objects.all().order_by('-id')
    serializer_class = DatasetSerializerList
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="List all datasets.",
        operation_description="Retrieves a list of all available datasets, ordered by their ID in descending order."
    )
    def list(self, request, *args, **kwargs):
        return super(DatasetListView, self).list(request, *args, **kwargs)

class DatasetDetailsView(generics.RetrieveAPIView):
    """GET API endpoint that displays a dataset's information based on its ID."""
    queryset = DatasetRegistry.objects.all()
    serializer_class = DatasetSerializerDetails

    @swagger_auto_schema(
        operation_summary="Retrieve a dataset's information.",
        operation_description="Displays detailed information about a dataset based on its unique ID.",
        responses={200: DatasetSerializerDetails()}
    )
    def get(self, request, *args, **kwargs):
        return super(DatasetDetailsView, self).get(request, *args, **kwargs)

class DatasetSearchView(views.APIView):
    """POST API endpoint that searches for datasets based on their title or keywords."""
    @swagger_auto_schema(
        operation_summary="Search datasets by title or keyword.",
        operation_description="Searches for datasets based on provided title or keywords in the metadata.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['search'],
            properties={
                'search': openapi.Schema(type=openapi.TYPE_STRING, description="Search term for dataset titles or keywords.")
            },
        ),
        responses={200: DatasetSerializerList(many=True)}
    )
    
    def post(self, request, format=None):
        """Function to search for datasets based on their title or keywords."""
        search = request.data['search']
        if search:
            queryset = DatasetRegistry.objects.filter((Q(metadata_file__basic_identity__title__icontains=search)|Q(metadata_file__keywords__icontains=search)))
            serializer = DatasetSerializerList(queryset, many=True)
            return Response(serializer.data)
        return Response([])