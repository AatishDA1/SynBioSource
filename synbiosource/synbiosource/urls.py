"""
URL configuration for synbiosource project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from . import views
from django.conf.urls.static import static 
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger API documentation configuration.
schema_view = get_schema_view(
    openapi.Info(
        title="SynBioSource API",
        default_version='v1',
        description="API endpoints for accessing datasets from SynBioSource.",
        contact=openapi.Contact(email="ad2320@ic.ac.uk"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', views.index, name="home"),
    path('admin', admin.site.urls),
    path('login', views.login_user, name="login"),
    path('logout', views.logout_user, name="logout"),
    path('register',views.register_user, name="register"),
    path('forgot-password',views.forgot_password, name="forgot-password"),
    path('reset-password/<str:token>',views.reset_password, name="reset-password"),
    path('dataset/',include('dataset.urls'),),
    path('api/dataset/',include('api.urls'),),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='api-documentation'),
]

# To enable the use of static files. 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)