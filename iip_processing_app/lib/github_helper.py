# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging, os, pprint

log = logging.getLogger(__name__)


class GHHelper( object ):
    """ Contains support functions for views.git_watcher() """

    def __init__( self ):
        self.AUTH_PASSWORD = unicode( os.environ['IIP_PRC__BASIC_AUTH_PASSWORD'] )
        self.AUTH_USERNAME = unicode( os.environ['IIP_PRC__BASIC_AUTH_USERNAME'] )
        self.DEV_URL = unicode( os.environ['IIP_PRC__DEV_URL'] )
        self.PRODUCTION_HOSTNAME = unicode( os.environ['IIP_PRC__PRODUCTION_HOSTNAME'] )

    def log_github_post( self, request_data ):
        """ Logs data posted from github. """
        data_dct = {
            'datetime': datetime.datetime.now(),
            'host': 'foo',
            'github_json': 'bar'
            # TODO
            }
        log.debug( 'data_dct, ```{}```'.format(pprint.pformat(data_dct)) )
        return data_dct

    def trigger_dev_if_production( self, data_dct ):
        """ Sends github `data` to dev-server (which github can't hit) if this is the production-server. """
        if data_dct['host'] == self.PRODUCTION_HOSTNAME:
            log.debug( 'gonna hit dev, too' )
            payload = data_dct['github_json']
            r = requests.post( self.DEV_URL, data=payload, auth=(self.B_AUTH_USERNAME, self.B_AUTH_PASSWORD) )
        return

    def prep_files_to_process( self, github_json ):
        """ Prepares the data-dict to be sent to the first rq job. """
        files_to_process = { u'files_updated': [], u'files_removed': [], u'timestamp': unicode(datetime.datetime.now()) }
        if github_json:
            commit_info = json.loads( github_json )
            ( added, modified, removed ) = self._examine_commits( commit_info )
            files_to_process[u'files_updated'] = added
            files_to_process[u'files_updated'].extend( modified )  # solrization same for added or modified
            files_to_process[u'files_removed'] = removed
        log.debug( 'files_to_process, ```{}```'.format(pprint.pformat(files_to_process)) )
        return files_to_process

    def _examine_commits( self, commit_info ):
        """ Extracts and returns file-paths for the different kinds of commits.
            Called by prep_files_to_process(). """
        added = []
        modified = []
        removed = []
        for commit in commit_info[u'commits']:
            added.extend( commit[u'added'] )
            modified.extend( commit[u'modified'] )
            removed.extend( commit[u'removed'] )
        return ( added, modified, removed )