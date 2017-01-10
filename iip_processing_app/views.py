# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

log = logging.getLogger(__name__)


def hi( request ):
    """ Returns simplest response. """
    now = datetime.datetime.now()
    log.debug( 'now, ```{}```'.format(now) )
    return HttpResponse( '<p>hi</p> <p>( %s )</p>' % now )


def process_single( request, inscription_id ):
    return HttpResponse( 'process_single coming' )


def process_new( request ):
    return HttpResponse( 'process_new coming' )


def process_all( request ):
    return HttpResponse( 'process_all coming' )


def process_all_confirm( request ):
    return HttpResponse( 'process_all_confirm coming' )


def process_orphans( request ):
    return HttpResponse( 'process_orphans coming' )
