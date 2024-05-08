from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf.urls.static import static 
from django.conf import settings 
from rest_framework import routers

urlpatterns = [
    path('', views.DatasetListView.as_view({'get': 'list'}), name='dataset-list'),
    path('<int:pk>/', views.DatasetDetailsView.as_view(), name='dataset-details'),  
    path('search', views.DatasetSearchView.as_view(), name='dataset-search'),  
]