# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json, logging, os
from iip_processing_app.lib.orphan_helper import OrphanDeleter
from iip_processing_app.lib.processor import Puller


log = logging.getLogger(__name__)
helper = OrphanDeleter()  # yeah, weird, see function's TODO
puller = Puller()


class AllProcessorHelper(object):
    """ Contains functions for processing all inscriptions.
        Helper for views.process_all() """

    def __init__( self ):
        self.ADMINS = json.loads( os.environ['IIP_PRC__LEGIT_ADMINS_JSON'] )

    def validate_request( self, eppn, dev_user, host ):
        """ Validates admin request.
            Called by views.delete_solr_orphans()
            TODO: refactor to common helper with orphan_helper.OrphanDeleter.validate_delete_request() """
        validity = helper.validate_delete_request( eppn, dev_user, host )  # yeah, it's not a delete; see docstring TODO
        log.debug( 'validity, `%s`' % validity )
        return validity

    def prep_data( self ):
        """ Prepares list of ids to be indexed.
            Called by views.process_all() """
        puller.call_git_pull()
        file_system_ids = helper.build_directory_inscription_ids()
        file_system_ids = file_system_ids[0:2]
        log.debug( 'len(file_system_ids), `%s`' % len(file_system_ids) )
        return file_system_ids
