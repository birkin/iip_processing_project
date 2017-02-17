# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, glob, json, logging, os, pprint
import requests
from django.http import HttpResponse
from iip_processing_app.lib.processor import Indexer
from iip_processing_app.models import Status


log = logging.getLogger(__name__)
indexer = Indexer()


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
            self.update_queued_status( inscription_id, 'queued for deletion' )
        for inscription_id in to_process_dct.get( 'files_updated', [] ):
            self.update_queued_status( inscription_id, 'queued for update' )
        resp = HttpResponse( '200 / OK' )
        return resp

    def update_queued_status( self, inscription_id, status_string ):
        """ Updates tracker that entry is queued for deletion.
            Called by handle_enqueues() """
        try:
            process_status = Status.objects.get( inscription_id=inscription_id )
        except Exception as e:
            process_status = Status( inscription_id=inscription_id )
        process_status.status_summary = status_string
        process_status.status_detail = ''
        process_status.save()
        return

    def handle_single_update( self, single_update_dct ):
        """ Updates single entry processed status.
            Called by views.update_processing_status() """
        ( inscription_id, status_summary, status_detail ) = (
            single_update_dct['inscription_id'], single_update_dct['status_summary'], single_update_dct['status_detail'] )
        try:
            process_status = Status.objects.get( inscription_id=inscription_id )
        except Exception as e:
            process_status = Status( inscription_id=inscription_id )
        process_status.status_summary = status_summary
        process_status.status_detail = status_detail
        process_status.save()
        resp = HttpResponse( '200 / OK' )
        return resp

    ## end class ProcessStatusRecorder()


class OrphanDeleter( object ):
    """ Contains funcions for removing orphaned entries from solr. """

    def __init__( self ):
        """ Settings. """
        self.GIT_CLONED_DIR_PATH = unicode( os.environ['IIP_PRC__CLONED_INSCRIPTIONS_PATH'] )
        self.SOLR_URL = unicode( os.environ['IIP_PRC__SOLR_URL'] )

    def prep_data( self ):
        """ Prepares list of ids to be deleted from solr.
            Called by views.delete_solr_orphans() """
        file_system_ids = self.build_directory_inscription_ids()
        solr_inscription_ids = self.build_solr_inscription_ids()
        orphans = self.build_orphan_list( file_system_ids, solr_inscription_ids )
        # orphans = [ 'aaa', 'bbb' ]
        # orphans = []
        log.debug( 'orphans, ```{}```'.format(pprint.pformat(orphans)) )
        return orphans

    def build_directory_inscription_ids( self ):
        """ Returns list of file-system ids.
            Called by prep_data(). """
        inscription_paths = glob.glob( '{}/epidoc-files/*.xml'.format(self.GIT_CLONED_DIR_PATH) )
        log.debug( 'inscription_paths[0:3], ```{}```'.format(pprint.pformat(inscription_paths[0:3])) )
        directory_inscription_ids = []
        for path in inscription_paths:
            filename = path.split( '/' )[-1]
            inscription_id = filename.split( '.xml' )[0]
            directory_inscription_ids.append( inscription_id )
        directory_inscription_ids = sorted( directory_inscription_ids )
        log.info( 'len(directory_inscription_ids), `{len}`; directory_inscription_ids[0:3], `{three}`'.format(len=len(directory_inscription_ids), three=pprint.pformat(directory_inscription_ids[0:3])) )
        return directory_inscription_ids

    def build_solr_inscription_ids( self ):
        """ Returns list of solr inscription ids.
            Called by prep_data(). """
        url = '{}/select?q=*:*&fl=inscription_id&rows=100000&wt=json'.format( self.SOLR_URL )
        log.info( 'url, ```{}```'.format(url) )
        r = requests.get( url )
        json_dict = r.json()
        docs = json_dict['response']['docs']  # list of dicts
        solr_inscription_ids = []
        for doc in docs:
            solr_inscription_ids.append( doc['inscription_id'] )
        solr_inscription_ids = sorted( solr_inscription_ids )
        log.info( 'len(solr_inscription_ids), `{len}`; solr_inscription_ids[0:3], `{three}`'.format(len=len(solr_inscription_ids), three=pprint.pformat(solr_inscription_ids[0:3])) )
        return solr_inscription_ids

    def build_orphan_list( self, directory_inscription_ids, solr_inscription_ids ):
        """ Returns list of solr-entries to delete.
            Called by prep_data(). """
        directory_set = set( directory_inscription_ids )
        solr_set = set( solr_inscription_ids )
        deletion_set = solr_set - directory_set
        orphan_list = sorted( list(deletion_set) )
        log.info( 'orphan_list, ```{}```'.format(pprint.pformat(orphan_list)) )
        return orphan_list

    def prep_context( self, data ):
        """ Prepares response info.
            Called by views.delete_solr_orphans() """
        context = {
            'data': data,
            'datetime': datetime.datetime.now(),
            'inscription_dir_path': self.GIT_CLONED_DIR_PATH
            }
        log.debug( 'context, ```{}```'.format(pprint.pformat(context)) )
        return context

    def run_deletes( self, id_lst ):
        """ Runs deletions.
            Called by views.delete_solr_orphans() """
        log.debug( 'id_lst, ```{}```'.format(pprint.pformat(id_lst)) )
        for inscription_id in id_lst:
            indexer.delete_entry( inscription_id )
        return

    ## end class OrphanDeleter()
