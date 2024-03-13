from django.contrib import admin
from .models import DatasetRegistry,Keyword

# Register your models here.
admin.site.register(DatasetRegistry)
admin.site.register(Keyword)