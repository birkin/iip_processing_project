# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json, logging, pprint
from django.http import HttpResponse
from iip_processing_app.models import Status


log = logging.getLogger(__name__)


class ProcessStatusRecorder( object ):
    """ Contains functions for recording processed-status. """

    def __init__( self ):
        """ Settings. """
        pass

    def check_for_data( self, request_body ):
        """ Returns any multiple-enqueue data and any single-update data.
            Called by views.update_processing_status() """
        data_dct = self.grab_data_dct( request_body )
        to_process_dct = self.grab_to_process_dct( data_dct )
        single_update_dct = self.grab_single_update_dct( data_dct )
        return ( to_process_dct, single_update_dct )

    def grab_data_dct( self, request_body ):
        """ Grabs dct info from request.body.
            Called by check_for_data() """
        try:
            data_dct = json.loads( request_body )
            to_process_dct = data_dct.get( 'to_process_dct', None )
        except:
            data_dct = {}
        log.debug( 'data_dct, ```{}```'.format(pprint.pformat(data_dct)) )
        return data_dct

    def grab_to_process_dct( self, data_dct ):
        """ Grabs possible enqueue-these data.
            Called by check_for_data() """
        try:
            to_process_dct = data_dct['to_process_dct']
        except:
            to_process_dct = {}
        log.debug( 'to_process_dct, ```{}```'.format(pprint.pformat(to_process_dct)) )
        return to_process_dct

    def grab_single_update_dct( self, data_dct ):
        """ Grabs possible single-item data.
            Called by check_for_data() """
        try:
            single_update_dct = {
                'inscription_id': data_dct['inscription_id'],
                'status_summary': data_dct['status_summary'],
                'status_detail': data_dct['status_detail'],
                }
        except:
            single_update_dct = {}
        log.debug( 'single_update_dct, ```{}```'.format(pprint.pformat(single_update_dct)) )
        return single_update_dct

    def handle_enqueues( self, to_process_dct ):
        """ Adds enqueu info to processing-status db.
            Called by views.update_processing_status() """
        for inscription_id in to_process_dct.get( 'files_removed', [] ):
            self.update_processing_status( inscription_id=inscription_id, new_status_summary='queued for deletion', new_status_detail='' )
        for inscription_id in to_process_dct.get( 'files_updated', [] ):
            self.update_processing_status( inscription_id=inscription_id, new_status_summary='queued for update', new_status_detail='' )
        resp = HttpResponse( '200 / OK' )
        return resp

    def update_processing_status( self, inscription_id, new_status_summary, new_status_detail ):
        """ Updates tracker that entry is queued for deletion.
            Called by handle_enqueues(), and by handle_single_update() """
        try:
            process_status = Status.objects.get( inscription_id=inscription_id )
        except Exception as e:
            process_status = Status( inscription_id=inscription_id )
        process_status.status_summary = new_status_summary
        process_status.status_detail = new_status_detail
        process_status.save()
        return

    def handle_single_update( self, single_update_dct ):
        """ Updates single entry processed status.
            Called by views.update_processing_status() """
        ( inscription_id, new_status_summary, new_status_detail ) = (
            single_update_dct['inscription_id'], single_update_dct['status_summary'], single_update_dct['status_detail'] )
        self.update_processing_status(
            inscription_id=inscription_id, new_status_summary=new_status_summary, new_status_detail=new_status_detail )
        resp = HttpResponse( '200 / OK' )
        return resp

    # def handle_single_update( self, single_update_dct ):
    #     """ Updates single entry processed status.
    #         Called by views.update_processing_status() """
    #     ( inscription_id, status_summary, status_detail ) = (
    #         single_update_dct['inscription_id'], single_update_dct['status_summary'], single_update_dct['status_detail'] )
    #     try:
    #         process_status = Status.objects.get( inscription_id=inscription_id )
    #     except Exception as e:
    #         process_status = Status( inscription_id=inscription_id )
    #     process_status.status_summary = status_summary
    #     process_status.status_detail = status_detail
    #     process_status.save()
    #     resp = HttpResponse( '200 / OK' )
    #     return resp

    ## end class ProcessStatusRecorder()
