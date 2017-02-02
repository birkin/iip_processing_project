# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from iip_processing_app.lib.github_helper import GHHelper


log = logging.getLogger(__name__)
github_helper = GHHelper()


def info( request ):
    """ Returns simplest response. """
    now = datetime.datetime.now()
    log.debug( 'now, ```{}```'.format(now) )
    return HttpResponse( '<p>hi</p> <p>( %s )</p>' % now )


@csrf_exempt
def gh_inscription_watcher( request ):
    """ Handles github inscriptions web-hook notification. """
    log.debug( 'request.body, ```{}```'.format(pprint.pformat(request.body)) )
    log.debug( 'request.__dict__, ```{}```'.format(pprint.pformat(request.__dict__)) )
    resp = HttpResponseForbidden( '403 / Forbidden' )  # will be returned if incorrect basic-auth credentials are submitted
    if 'HTTP_AUTHORIZATION' in request.META:
        received_username_password_dct = github_helper.parse_http_basic_auth( request.META['HTTP_AUTHORIZATION'].decode('utf-8') )
        if github_helper.validate_credentials( received_username_password_dct ):
            github_helper.handle_inscription_update( request.body, request.META.get('HTTP_HOST', None) )
            resp = HttpResponse( '200 / OK' )
    else:
        resp = github_helper.make_unauthenticated_response()
    log.debug( 'response status code, `{}`'.format(resp.status_code) )
    return resp


def process_all( request ):
    return HttpResponse( 'process_all coming' )


def process_orphans( request ):
    return HttpResponse( 'process_orphans coming' )
