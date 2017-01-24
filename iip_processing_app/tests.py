# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging, os
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

    # end class RootUrlTest()


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
        """ Checks for successful job-in-progress. """
        ## confirm no jobs running
        q = rq.Queue( self.queue_name, connection=redis.Redis() )
        self.assertEqual( 0, len(q.jobs) )
        ## call processor.run_call_git_pull( to_process_dct )
        to_process_dct = {
            u'files_removed': [],
            u'files_updated': [u'epidoc-files/abur0001.xml'],
            u'timestamp': u'2017-01-24 09:52:38.911009' }
        processor.run_call_git_pull( to_process_dct )
        ## confirm jobs running
        q = rq.Queue( self.queue_name, connection=redis.Redis() )
        self.assertEqual( 1, len(q.jobs) )
