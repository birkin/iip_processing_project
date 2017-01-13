# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging, os
from django.test import TestCase
from iip_processing_app.lib.github_helper import GHHelper


log = logging.getLogger(__name__)
TestCase.maxDiff = None
gh_helper = GHHelper()


class RootUrlTest( TestCase ):
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


class HBAuthParserTest( TestCase ):
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
