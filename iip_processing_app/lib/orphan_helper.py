# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, glob, json, logging, os, pprint
import requests
from iip_processing_app.lib.processor import Indexer


log = logging.getLogger(__name__)
indexer = Indexer()


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
