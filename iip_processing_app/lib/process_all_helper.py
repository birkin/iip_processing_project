# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json, logging, os


log = logging.getLogger(__name__)


class AllProcessorHelper(object):
    """ Contains functions for processing all inscriptions.
        Helper for views.process_all() """

    def __init__( self ):
        self.ADMINS = json.loads( os.environ['IIP_PRC__LEGIT_ADMINS_JSON'] )

    def validate_request( self, eppn, dev_user, host ):
        """ Validates admin request.
            Called by views.delete_solr_orphans()
            TODO: refactor to common helper with orphan_helper.OrphanDeleter.validate_delete_request() """
        validity = False
        if eppn in self.ADMINS:
            validity = True
        elif dev_user in self.ADMINS and host == '127.0.0.1':
            validity = True
        log.debug( 'validity, `%s`' % validity )
        return validity
