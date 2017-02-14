# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, logging, os, pprint


log = logging.getLogger(__name__)


class OrphanDeleter( object ):
    """ Contains funcions for removing orphaned entries from solr. """

    def __init__( self ):
        """ Settings. """
        self.GIT_CLONED_DIR_PATH = unicode( os.environ['IIP_PRC__CLONED_INSCRIPTIONS_PATH'] )

    def prep_data( self ):
        """ Prepares list of ids to be deleted from solr.
            Called by views.delete_solr_orphans() """
        # data = [ 'aaa', 'bbb' ]
        data = []
        ## get file listing
        file_system_ids = self.build_directory_inscription_ids()
        ## get solr listing
        ## find solr entries not in file list
        log.debug( 'data, ```{}```'.format(pprint.pformat(data)) )
        return data

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
        for inscription_id in id_lst:
            ## insert solr deletion url here
            pass
        return
