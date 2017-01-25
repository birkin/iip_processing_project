# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
Contains:
- Puller() class, for running git-pull.
- A job-queue caller function.
"""

import datetime, json, logging, logging.config, os, pprint, shutil, time
import envoy, redis, requests, rq
from django.conf import settings as project_settings


log = logging.getLogger(__name__)
if not logging._handlers:  # true when module accessed by queue-jobs
    worker_config_dct = json.loads( os.environ['IIP_PRC__JOB_LOG_CONFIG_JSON'] )
    worker_config_dct['loggers']['iip_processing_app']['level'] = unicode( os.environ[u'IIP_PRC__LOG_LEVEL'] )
    logging.config.dictConfig( worker_config_dct )


class Puller( object ):
    """ Contains funcions for executing git-pull. """

    def __init__( self ):
        """ Settings. """
        self.GIT_CLONED_DIR_PATH = unicode( os.environ['IIP_PRC__CLONED_INSCRIPTIONS_PATH'] )

    def call_git_pull( self ):
        """ Runs git_pull.
                Returns list of filenames.
            Called by run_call_git_pull(). """
        log.debug( 'starting call_git_pull()' )
        original_directory = os.getcwd()
        log.debug( 'original_directory, ```{}```'.format(original_directory) )
        os.chdir( self.GIT_CLONED_DIR_PATH )
        log.debug( 'temp directory, ```{}```'.format(os.getcwd()) )
        command = 'git pull'
        r = envoy.run( command.encode('utf-8') )  # envoy requires strings
        track_dct = self.track_envoy_call( r )
        os.chdir( original_directory )
        log.debug( 'directory after change-back, ```{}```'.format(os.getcwd()) )
        return track_dct['status_code']

    def track_envoy_call( self, envoy_response ):
        """ Creates dct convenient for logging and status_code access.
            Called by call_git_pull() """
        track_dct = {
            'status_code': envoy_response.status_code,  # int
            'std_out': envoy_response.std_out.decode(u'utf-8'),
            'std_err': envoy_response.std_err.decode(u'utf-8'),
            'command': envoy_response.command,  # list
            'history': envoy_response.history  # list
            }
        log.debug( 'envoy response, ```{}```'.format(pprint.pformat(track_dct)) )
        return track_dct

    ## end class Puller()


class StatusBackupper( object ):
    """ Manages creation and storage of json file of backup statuses. """

    def __init__( self ):
        """ Settings. """
        self.SOLR_URL = unicode( os.environ['IIP_PRC__SOLR_URL'] )
        self.DISPLAY_STATUSES_BACKUP_DIR = unicode( os.environ['IIP_PRC__DISPLAY_STATUSES_BACKUP_DIR'] )
        self.STATUSES_GIST_URL = unicode( os.environ['IIP_PRC__STATUSES_GIST_URL'] )
        self.STATUSES_GIST_USERNAME = unicode( os.environ['IIP_PRC__STATUSES_GIST_USERNAME'] )
        self.STATUSES_GIST_PASSWORD = unicode( os.environ['IIP_PRC__STATUSES_GIST_PASSWORD'] )
        self.DISPLAY_STATUSES_BACKUP_TIMEFRAME_IN_DAYS = int( os.environ['IIP_PRC__DISPLAY_STATUSES_BACKUP_TIMEFRAME_IN_DAYS'] )

    def make_backup( self ):
        """ Manages the backup process.
            Called by run_backup_statuses(). """
        log.debug( 'starting backup' )
        status_json = self.make_status_json()
        self.update_github( status_json )
        self.save_locally( status_json )
        self.delete_old_backups()
        return status_json

    def make_status_json( self ):
        """ Queries solr for current display-statuses and saves result to a json file.
            Called by make_backup(). """
        log.debug( 'starting status-grab from solr' )
        url = '{}/select?q=*:*&rows=6000&fl=inscription_id,display_status&wt=json&indent=true'.format( self.SOLR_URL )
        log.debug( 'url, ```{}```'.format(url) )
        r = requests.get( url )
        status_json = r.content
        return status_json

    def update_github( self, status_json ):
        """ Saves statuses to gist.
            Called by make_backup(). """
        log.debug( 'starting gist update' )
        auth = requests.auth.HTTPBasicAuth( self.STATUSES_GIST_USERNAME, self.STATUSES_GIST_PASSWORD )
        json_payload = json.dumps( {
            'description': 'backup of iip inscription display statuses',
            'files': {
                'iip_display_statuses.json': { 'content': status_json },
              }
            } )
        r = requests.patch( url=self.STATUSES_GIST_URL, auth=auth, data=json_payload )
        return

    def save_locally( self, status_json ):
        """ Saves data locally.
            Called by make_backup().
            TODO: eventually commit status_json to a repo, and push to github, streamlining local and external backup. """
        log.debug( 'starting local save' )
        filename = 'display_statuses_backup_{}.json'.format( unicode(datetime.datetime.now()) ).replace( ' ', '_' )
        filepath = '{dir}/{fname}'.format( dir=self.DISPLAY_STATUSES_BACKUP_DIR, fname=filename )
        log.debug( 'filepath, ```{}```'.format(filepath) )
        with open( filepath, 'w' ) as f:
            f.write( status_json )
        return

    def delete_old_backups( self ):
        """ Deletes old backup display status files.
            Called by make_backup() """
        log.debug( 'starting old-backup deletion' )
        now = time.time()
        seconds_in_day = 60*60*24
        timeframe_days = seconds_in_day * self.DISPLAY_STATUSES_BACKUP_TIMEFRAME_IN_DAYS
        backup_files = os.listdir( self.DISPLAY_STATUSES_BACKUP_DIR )
        backup_files = [ unicode(x) for x in backup_files ]
        for backup_filename in backup_files:
            backup_filepath = '{dir}/{fname}'.format( dir=self.DISPLAY_STATUSES_BACKUP_DIR, fname=backup_filename )
            if os.stat( backup_filepath ).st_mtime < (now - timeframe_days):
                os.remove( backup_filepath )
        return

    ## end class StatusBackupper()


class Prepper( object ):
    """ Manages prep for solr post. """

    def __init__( self ):
        pass

    def check_if_new( self ):
        existing_solr_inscri
        pass

    ## end class Prepper()


## runners ##

q = rq.Queue( u'iip_prc', connection=redis.Redis() )
puller = Puller()
backupper = StatusBackupper()

def run_call_git_pull( to_process_dct ):
    """ Initiates a git pull update.
            Eventually spawns a call to indexer.run_update_index() which handles each result found.
        Called by views.gh_inscription_watcher(). """
    assert sorted( to_process_dct.keys() ) == [ 'files_removed', 'files_updated', 'timestamp']
    log.debug( 'to_process_dct, ```{}```'.format(pprint.pformat(to_process_dct)) )
    time.sleep( 2 )  # let any existing in-process pull finish
    puller = Puller()
    puller.call_git_pull()
    log.debug( 'enqueuing next job' )
    q.enqueue_call(
        func=u'iip_processing_app.lib.processor.run_backup_statuses',
        kwargs={u'files_to_update': to_process_dct['files_updated'], u'files_to_remove': to_process_dct['files_removed']} )
    return

def run_backup_statuses( files_to_update, files_to_remove ):
    """ Backs up statuses.
        Called by run_call_git_pull() """
    status_json = backupper.make_backup()
    for file_to_update in files_to_update:
        q.enqueue_call(
            func='iip_processing_app.lib.processor.run_prep_file',
            kwargs={'file_to_update': file_to_update, 'status_json': status_json} )
    for file_to_remove in files_to_remove:
        q.enqueue_call(
            func='iip_processing_app.lib.processor.run_remove_file_from_index',
            kwargs={'file_to_remove': file_to_remove} )

def run_prep_file( file_to_update, status_json ):
    """ Prepares file for indexing.
        Called by run_backup_statuses() """
    log.debug( 'file_to_update, ```{}```'.format(file_to_update) )
    prepared_solr_data = prepper.make_solr_data( file_to_update, status_json )
    log.debug( 'enqueuing next job' )
    q.enqueue_call(
        func=u'iip_processing_app.lib.processor.run_update_index',
        kwargs={u'prepared_solr_data': prepared_solr_data} )

def run_update_index( prepared_solr_data ):
    """ Updates index with new or changed info.
        Called by run_prep_file() """
    log.debug( 'call to index-file class/function will go here' )
    log.debug( 'done processing file' )

def run_remove_file_from_index( files_to_remove ):
    """ Removes file from index.
        Called by run_backup_statuses() """
    log.debug( 'call to remove-from-index class/function will go here' )
    log.debug( 'done processing file' )
