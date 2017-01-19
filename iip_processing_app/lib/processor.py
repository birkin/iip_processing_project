# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
Contains:
- Puller() class, for running git-pull.
- A job-queue caller function.
"""

import datetime, json, logging, os, pprint, shutil, time
import envoy, redis, rq


log = logging.getLogger(__name__)


class Puller( object ):
    """ Contains funcions for executing git-pull. """

    def __init__( self, log ):
        """ Settings. """
        self.GIT_CLONED_DIR_PATH = unicode( os.environ.get('usep_gh__GIT_CLONED_DIR_PATH') )

    def call_git_pull( self ):
        """ Runs git_pull.
                Returns list of filenames.
            Called by run_call_git_pull(). """
        log.debug( 'starting call_git_pull()' )
        original_directory = os.getcwd()
        os.chdir( self.GIT_CLONED_DIR_PATH )
        command = 'git pull'
        r = envoy.run( command.encode('utf-8') )  # envoy requires strings
        log_helper.log_envoy_output( self.log, r )
        os.chdir( original_directory )
        return

    ## end class Puller()


## runners ##

q = rq.Queue( u'iip_processing', connection=redis.Redis() )

def run_call_git_pull( to_process_dct ):
    """ Initiates a git pull update.
            Eventually spawns a call to indexer.run_update_index() which handles each result found.
        Triggered by views.gh_inscription_watcher(). """
    assert sorted( to_process_dct.keys() ) == [ 'files_removed', 'files_updated', 'timestamp']
    log.debug( 'to_process_dct, ```{}```'.format(pprint.pformat(to_process_dct)) )
    time.sleep( 2 )  # let any existing in-process pull finish
    puller = Puller()
    puller.call_git_pull()
    log.debug( 'enqueuing next job' )
    # q.enqueue_call(
    #     func=u'iip_processing_app.lib.processor.run_some_step',
    #     kwargs={u'files_to_update': files_to_update, u'files_to_remove': files_to_remove} )
    return
