# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from iip_processing_app.models import Status


class StatusAdmin( admin.ModelAdmin ):
    date_hierarchy = 'modified_datetime'
    ordering = [ 'inscription_id' ]
    list_display = [
        'inscription_id', 'status_summary', 'status_detail', 'modified_datetime' ]
    # list_filter = [ 'patron_barcode' ]
    search_fields = [
        'inscription_id', 'status_summary', 'status_detail' ]
    readonly_fields = [
        'inscription_id', 'status_summary', 'status_detail', 'modified_datetime' ]


admin.site.register( Status, StatusAdmin )
