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
    log.debug( 'request.__dict__, ```{}```'.format(pprint.pformat(request.__dict__)) )
    if 'HTTP_AUTHORIZATION' in request.META:
        log.debug( 'HTTP_AUTHORIZATION detected' )
        received_username_password_dct = github_helper.parse_http_basic_auth( request.META['HTTP_AUTHORIZATION'].decode('utf-8') )
        if github_helper.validate_credentials( received_username_password_dct ):
            log.debug( 'returning "ok / basic-auth"' )
            return HttpResponse( 'ok / basic-auth' )
        else:
            log.debug( 'returning "forbidden"' )
            return HttpResponseForbidden
    else:
        log.debug( 'returning "regular ok"' )
        return HttpResponse( 'ok / regular' )
    # data_dct = github_helper.parse_github_post( request.x )
    # gh_helper.trigger_dev_if_production( data_dct )  # github can only hit production; we want dev updated, too
    # files_to_process = gh_helper.prep_files_to_process( data_dct )
    # q.enqueue_call (
    #     func='iip_processing_app.lib.processor.run_call_git_pull',
    #     kwargs = {'files_to_process': files_to_process}
    #     )
    # return HttpResponse( 'received' )


def process_all( request ):
    return HttpResponse( 'process_all coming' )


def process_orphans( request ):
    return HttpResponse( 'process_orphans coming' )
