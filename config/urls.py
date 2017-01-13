# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from iip_processing_app import views

admin.autodiscover()


urlpatterns = [

    # url( r'^admin/', include(admin.site.urls) ),

    url( r'^info/$',  views.info, name='info_url' ),

    url( r'^gh_inscription_watcher/$',  views.gh_inscription_watcher, name='gh_inscription_watcher_url' ),

    url( r'^process/single/(?P<inscription_id>.*)/$', views.process_single, name=u'process_single_url' ),
    url( r'^process/new/$', views.process_new, name=u'process_new_url' ),
    url( r'^process/all/$', views.process_all, name=u'process_all_url' ),
    url( r'^process/delete_orphans/$', views.process_orphans, name=u'process_orphans_url' ),

    url( r'^$',  RedirectView.as_view(pattern_name='info_url') ),

    ]
