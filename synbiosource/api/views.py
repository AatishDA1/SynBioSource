from django.shortcuts import render
from django.contrib.auth.models import Group, User
from django.db.models import Q
from rest_framework import permissions, viewsets, generics, views
from rest_framework.response import Response    

from api.serializers import DatasetSerializerList, DatasetSerializerDetails
from dataset.models import DatasetRegistry

# Create your views here.

class DatasetListView(viewsets.ModelViewSet):
    """
    GET API endpoint that lists the available datasets.
    """
    queryset = DatasetRegistry.objects.all().order_by('-id')
    serializer_class = DatasetSerializerList
    permission_classes = [permissions.AllowAny]

class DatasetDetailsView(generics.RetrieveAPIView):
    """GET API endpoint that displays a dataset's information based on its ID."""
    queryset = DatasetRegistry.objects.all()
    serializer_class = DatasetSerializerDetails

class DatasetSearchView(views.APIView):
    """POST API endpoint that searches for datasets based on their title or keywords."""
    def post(self, request, format=None):
        """Function to search for datasets based on their title or keywords."""
        search = request.data['search']
        if search:
            queryset = DatasetRegistry.objects.filter((Q(metadata_file__basic_identity__title__icontains=search)|Q(metadata_file__keywords__icontains=search)))
            serializer = DatasetSerializerList(queryset, many=True)
            return Response(serializer.data)
        return Response([])