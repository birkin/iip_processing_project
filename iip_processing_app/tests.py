# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json, logging, os, time
import redis, rq
from django.test import TestCase
from iip_processing_app.lib.github_helper import GHHelper
from iip_processing_app.lib import processor
from iip_processing_app.lib.processor import Puller


log = logging.getLogger(__name__)
TestCase.maxDiff = None
gh_helper = GHHelper()
puller = Puller()


class RootUrlTest(TestCase):
    """ Checks root urls. """

    def test_root_url_no_slash(self):
        """ Checks '/root_url'. """
        response = self.client.get( '' )  # project root part of url is assumed
        self.assertEqual( 302, response.status_code )  # permanent redirect
        redirect_url = response._headers['location'][1]
        self.assertEqual(  '/info/', redirect_url )

    def test_root_url_slash(self):
        """ Checks '/root_url/'. """
        response = self.client.get( '/' )  # project root part of url is assumed
        self.assertEqual( 302, response.status_code )  # permanent redirect
        redirect_url = response._headers['location'][1]
        self.assertEqual(  '/info/', redirect_url )


class HBAuthParserTest(TestCase):
    """ Checks parsing of http-basic-auth incoming info. """

    def setUp(self):
        self.test_hbauth_header = os.environ['IIP_PRC__TEST_HTTP_BASIC_AUTH_HEADER'].decode( 'utf-8' )
        self.hbauth_good_username = os.environ['IIP_PRC__BASIC_AUTH_USERNAME'].decode( 'utf-8' )
        self.hbauth_good_password = os.environ['IIP_PRC__BASIC_AUTH_PASSWORD'].decode( 'utf-8' )

    def test_legit_info(self):
        """ Checks parsing of username and password. """
        self.assertEqual(
            { 'received_username': self.hbauth_good_username, 'received_password': self.hbauth_good_password },
            gh_helper.parse_http_basic_auth( self.test_hbauth_header )
            )


class GitHubResponseTest(TestCase):
    """ Checks github response parsing. """

    def test_examine_commits(self):
        """ Checks extraction of files to process. """
        commits_list = json.loads('''[
            {
              "added": [],
              "author": {
                "email": "birkin.diana@gmail.com",
                "name": "Birkin James Diana",
                "username": "birkin"
              },
              "committer": {
                "email": "noreply@github.com",
                "name": "GitHub",
                "username": "web-flow"
              },
              "distinct": true,
              "id": "88cb3c31a7bcec4adc0558fbff74347d0a9245e1",
              "message": "test commit of comment.",
              "modified": [
                "epidoc-files/abur0001.xml",
                "blah",
                "epidoc-files/aaa123.xml"
              ],
              "removed": [],
              "timestamp": "2017-01-19T11:00:30-05:00",
              "tree_id": "e45afe1e50d17e94e9bc2a26a35f4b3f3457bb55",
              "url": "https://github.com/Brown-University-Library/iip-texts/commit/88cb3c31a7bcec4adc0558fbff74347d0a9245e1"
            }
          ]''')
        self.assertEqual(
            # ( [], [u'aaa123.xml', u'abur0001.xml'], [] ),  # added, modified, removed
            ( [], [u'aaa123', u'abur0001'], [] ),  # added, modified, removed
            gh_helper.examine_commits( commits_list )
            )


class ProcessorTest(TestCase):
    """ Checks processor.py functions. """

    def setUp(self):
        self.queue_name = unicode( os.environ['IIP_PRC__QUEUE_NAME'] )

    def test_call_git_pull(self):
        """ Checks for successful pull. """
        self.assertEqual(
            0,  # 0 means no problems; 1 means a problem
            puller.call_git_pull()
            )

    def test_run_call_git_pull(self):
        """ Triggers processing; checks for no failed jobs. """
        ## confirm no processing jobs running
        q = rq.Queue( self.queue_name, connection=redis.Redis() )
        self.assertEqual( 0, len(q.jobs) )
        ##
        ## confirm no processing failed jobs
        failed_queue = rq.queue.get_failed_queue( connection=redis.Redis() )
        failed_count = 0
        for job in failed_queue.jobs:
            if job.origin == self.queue_name:
                failed_count += 1
        self.assertEqual( 0, failed_count )
        ##
        ## call processor.run_call_git_pull( to_process_dct )
        to_process_dct = {
            u'files_removed': [],
            u'files_updated': ['abur0001'],
            u'timestamp': u'2017-01-24 09:52:38.911009' }
        processor.run_call_git_pull( to_process_dct )
        ##
        ## confirm no processing failed jobs
        time.sleep( 2 )
        failed_queue = rq.queue.get_failed_queue( connection=redis.Redis() )
        failed_count = 0
        for job in failed_queue.jobs:
            if job.origin == self.queue_name:
                failed_count += 1
        self.assertEqual( 0, failed_count )
