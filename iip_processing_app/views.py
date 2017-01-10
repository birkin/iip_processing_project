# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

log = logging.getLogger(__name__)


def info( request ):
    """ Returns simplest response. """
    now = datetime.datetime.now()
    log.debug( 'now, ```{}```'.format(now) )
    return HttpResponse( '<p>hi</p> <p>( %s )</p>' % now )


def process_single( request, inscription_id ):
    """ Triggers, after instruction, processing of given iscription. """
    log.info( 'starting; inscription_id, `{}`'.format(inscription_id) )
    if validator.validate_access( a, b ) == False:
        log.info( 'not authorized, returning Forbidden' )
        return HttpResponseForbidden( '403 / Forbidden' )
    if inscription_id == u'INSCRIPTION_ID':
        return HttpResponse( u'In url above, replace `INSCRIPTION_ID` with id to process, eg `ahma0002`. This will not change proofreading status.' )
    else:
        q.enqueue_call( func=u'iip_processing_app.lib.processor.run_process_single_file', kwargs = {u'inscription_id': inscription_id} )
        return HttpResponse( u'Started processing inscription-id, `{}`.'.format(inscription_id) )


def process_new( request ):
    return HttpResponse( 'process_new coming' )


def process_all( request ):
    return HttpResponse( 'process_all coming' )


def process_all_confirm( request ):
    return HttpResponse( 'process_all_confirm coming' )


def process_orphans( request ):
    return HttpResponse( 'process_orphans coming' )
