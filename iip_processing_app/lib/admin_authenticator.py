# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging


log = logging.getLogger(__name__)


class AdminValidator( object ):
    """ Contains funcions for validating admin urls. """

    def __init__( self ):
        """ Settings. """
        pass

    def validate_admin_request( self, eppn, dev_user, host ):
        """ aa.
            Called by views.delete_solr_orphans() """
        pass
