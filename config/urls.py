# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from iip_processing_app import views

admin.autodiscover()

urlpatterns = [

    url( r'^admin/', include(admin.site.urls) ),  # eg host/project_x/admin/

    # url( r'^', include('iip_processing_app.urls_app', namespace='foo') ),  # eg host/project_x/anything/

    url( r'^info/$',  views.hi, name='info_url' ),

    # url( r'^$',  RedirectView.as_view(pattern_name='foo:info_url') ),
    url( r'^$',  RedirectView.as_view(pattern_name='info_url') ),

    ]
