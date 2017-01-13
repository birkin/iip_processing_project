# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from iip_processing_app.lib import github_helper, validator

log = logging.getLogger(__name__)


def info( request ):
    """ Returns simplest response. """
    now = datetime.datetime.now()
    log.debug( 'now, ```{}```'.format(now) )
    return HttpResponse( '<p>hi</p> <p>( %s )</p>' % now )


@csrf_exempt
def gh_inscription_watcher( request ):
    """ Handles github inscriptions web-hook notification. """
    log.debug( 'request.__dict__, ```{}```'.format(pprint.pformat(request.__dict__)) )
    gh_helper = github_helper.GHHelper()
    data_dct = gh_helper.parse_github_post( request.x )
    gh_helper.trigger_dev_if_production( data_dct )  # github can only hit production; we want dev updated, too
    files_to_process = gh_helper.prep_files_to_process( data_dct )
    q.enqueue_call (
        func='iip_processing_app.lib.processor.run_call_git_pull',
        kwargs = {'files_to_process': files_to_process}
        )
    return HttpResponse( 'received' )


def process_all( request ):
    return HttpResponse( 'process_all coming' )


def process_orphans( request ):
    return HttpResponse( 'process_orphans coming' )
