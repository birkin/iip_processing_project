# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json, logging, os, pprint
from django.conf import settings
from django.contrib.auth import authenticate


log = logging.getLogger(__name__)


class UserGrabber(object):

    def __init__( self ):
        self.LEGIT_VIEWER_USER = unicode( os.environ['IIP_PRC__LEGIT_QUEUE_VIEWER_USER'] )
        self.LEGIT_VIEWER_PASSWORD = unicode( os.environ['IIP_PRC__LEGIT_QUEUE_VIEWER_PASSWORD'] )
        self.LEGIT_VIEWER_GROUPER_GROUPS = json.loads( os.environ['IIP_PRC__LEGIT_QUEUE_VIEWER_GROUPS_JSON'] )
        self.LEGIT_VIEWER_EPPNS = json.loads( os.environ['IIP_PRC__LEGIT_QUEUE_VIEWER_EPPNS_JSON'] )

    def get_user( self, meta_dct ):
        """ Returns user object.
            Called by views.view_processing() """
        shib_checker = ShibChecker()
        if shib_checker.validate_user( meta_dct ):
            log.debug( 'validated via shib' )
            user = self.grab_good_user()
        elif meta_dct['SERVER_NAME'] == '127.0.0.1' and settings.DEBUG == True:
            log.debug( 'validated via localdev' )
            user = self.grab_good_user()
        else:
            log.debug( 'not validated' )
            user = None
        return user

    def grab_good_user( self ):
        """ Grabs generic authenticated user.
            Called by get_user() """
        user = authenticate( username=self.LEGIT_VIEWER_USER, password=self.LEGIT_VIEWER_PASSWORD )
        log.debug( 'user authenticated' )
        return user


class ShibChecker( object ):

    def validate_user( self, meta_dct ):
        """ Checks shib info.
            Called by UserGrabber.get_user() """
        return_val = False
        shib_dct = self.grab_shib_info( meta_dct )
        if shib_dct:
            log.debug( 'shib_dct exists' )
            if self.check_group( shib_dct['member_of'] ):
                return_val = True
            elif self.check_eppn( shib_dct['eppn'] ):
                return_val = True
        log.debug( 'return_val, `{}`'.format(return_val) )
        return return_val

    def grab_shib_info( self, meta_dct ):
        """ Grabs shib values from http-header.
            Called by: validate_user() """
        shib_dct = None
        if 'Shibboleth-eppn' in meta_dct:
            shib_dct = self.grab_shib_from_meta( meta_dct )
        log.debug( 'shib_dct, ```{}```'.format(pprint.pformat(shib_dct)) )
        return shib_dct

    def check_group( self, user_memberships ):
        """ Checks user's grouper groups.
            Called by validate_user() """
        log.debug( 'starting check_group()' )
        try:
            return_val = False
            for group in self.LEGIT_VIEWER_GROUPER_GROUPS:
                if group in user_memberships:
                    return_val = True
                    break
            log.debug( 'check_group() return_val, `{}`'.format(return_val) )
        except Exception as e:
            log.error( 'exception, ```{}```'.format(unicode(repr(e))) )
        return return_val

    def check_eppn( self, eppn ):
        """ Checks user's eppn.
            Called by validate_user() """
        log.debug( 'starting check_eppn()' )
        return_val = False
        if eppn in self.LEGIT_VIEWER_EPPNS:
            return_val = True
        log.debug( 'check_eppn() return_val, `{}`'.format(return_val) )
        return return_val

    def grab_shib_from_meta( self, meta_dct ):
        """ Extracts shib values from http-header.
            Called by grab_shib_info() """
        shib_dct = {
            # 'brown_status': meta_dct.get( 'Shibboleth-brownStatus', '' ),  # eg. 'active'
            # 'brown_type': meta_dct.get( 'Shibboleth-brownType', '' ),  # eg. 'Staff'
            # 'department': meta_dct.get( 'Shibboleth-department', '' ),
            # 'edu_person_primary_affiliation': meta_dct.get( 'Shibboleth-eduPersonPrimaryAffiliation', '' ),  # eg. 'staff'
            # 'email': meta_dct.get( 'Shibboleth-mail', '' ).lower(),
            'eppn': meta_dct.get( 'Shibboleth-eppn', '' ),
            # 'id_net': meta_dct.get( 'Shibboleth-brownNetId', '' ),
            # 'id_short': meta_dct.get( 'Shibboleth-brownShortId', '' ),
            'member_of': sorted( meta_dct.get('Shibboleth-isMemberOf', '').split(';') ),  # only dct element that's not a unicode string
            # 'name_first': meta_dct.get( 'Shibboleth-givenName', '' ),
            # 'name_last': meta_dct.get( 'Shibboleth-sn', '' ),
            # 'patron_barcode': meta_dct.get( 'Shibboleth-brownBarCode', '' ),
            # 'phone': meta_dct.get( 'Shibboleth-phone', 'unavailable' ),  # valid?
            # 'title': meta_dct.get( 'Shibboleth-title', '' ),
            }
        return shib_dct
