"""PIA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from PIA.views import index_view, privacy_view

from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('d/', include('Dynamics.urls')),
]

if not settings.DYNAMICS_SAFE_MODE:
    app_urlpatterns = [

        path('users/', include('Core.Users.urls')),
        path('system/', include('Core.System.urls')),
        path('reports/', include('Core.Reports.urls')),

        path('users/', include('Users.urls')),
        path('masters/', include('Masters.urls')),
        path('thirdparty/', include('thirdparty.urls')),
        path('general/', include('General.urls')),

        path('leads/', include('LeadManagement.urls')),
        path('tenders/', include('TenderManagement.urls')),
        path('purchaseenquiry/', include('PurchaseEnquiry.urls')),
        path('projectmanagement/', include('ProjectManagement.urls')),
        path('quotation/', include('Quotation.urls')),
        path('comparequotation/', include('CompareQuotation.urls')),
        path('purchaseindent/', include('PurchaseIndent.urls')),
        path('purchaseorder/', include('PurchaseOrder.urls')),
        path('payment/', include('Payments.urls')),
        path('materialrequest/', include('MaterialRequest.urls')),
        path('taskmanagement/', include('TaskManagement.urls')),
        path('actions/', include('ActionManagement.urls')),
        path('servicemanagement/', include('ServiceManagement.urls')),
        path('filesystem/', include('FileSystem.urls')),
        path('boq/', include('BOQ.urls')),
        path('dashboard/', include('Dashboard.urls')),

    ]

    urlpatterns = urlpatterns + app_urlpatterns

if  settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Workes Only in Development    
else:
    urlpatterns += [ path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),]

if not settings.USE_S3:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Workes Only in Development
    # urlpatterns += [ path(settings.MEDIA_URL+'<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),] 

urlpatterns += [ path('firebase-messaging-sw.js', serve, {'document_root': settings.STATIC_ROOT, 'path': 'firebase-messaging-sw.js'}),]

urlpatterns += [
    
    path('privacypolicy', privacy_view, name='privacy'),
    path('schema/DJKHIDSRGJKDRGELRUJIODSFKGLWSEKJFKOER/', login_required(SpectacularAPIView.as_view()), name='schema'),
    path('swagger/SJDFHOSIEJKFSLEKJWEIOFJWELKFSPEIOFK/', login_required(SpectacularSwaggerView.as_view(url_name='schema')),name='schema-swagger-ui'),
    path('redoc/',login_required(SpectacularRedocView.as_view(url_name='schema')), name='schema-redoc'),
    re_path(r'^.*', index_view),
]

