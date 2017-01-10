# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint

log = logging.getLogger(__name__)


def validate_access( basic_auth_info, received_ip ):
    """ Validates http-basic-auth.
        Called by different views. """
    return_val = False
    if basic_auth_info is note None and ip is not None:
        if auth_info.startswith('Basic '):
            decoded_basic_info = basic_auth_info.lstrip('Basic ').decode('base64')
            ( received_username, received_password ) = decoded_basic_info.rsplit( ':', 1 )   # cool; 'rsplit-1' solves problem if 'username' contains one or more colons.
            if len(received_username) > 0 and len(received_password) > 0:
                if received_ip in settings_app.LEGIT_ACCESSORS.keys():
                    if settings_app.LEGIT_ACCESSORS[ip]['username'] == received_username and settings_app.LEGIT_ACCESSOR[ip]['password'] == received_password:
                        return_val = True
    log.debug( 'return_val, `{}`'.format(return_val) )
    return return_val
