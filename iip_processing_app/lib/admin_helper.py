# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging


log = logging.getLogger(__name__)


class OrphanDeleter( object ):
    """ Contains funcions for removing orphaned entries from solr. """

    def __init__( self ):
        """ Settings. """
        pass

    def prep_context( self ):
        """ aa.
            Called by views.delete_solr_orphans() """
        return False
