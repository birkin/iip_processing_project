# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from iip_processing_app.lib.github_helper import GHHelper, GHValidator
from iip_processing_app.lib.admin_authenticator import AdminValidator
from iip_processing_app.lib.admin_helper import OrphanDeleter
from iip_processing_app.models import Status


log = logging.getLogger(__name__)
github_validator = GHValidator()
github_helper = GHHelper()
admin_validator = AdminValidator()
orphan_deleter = OrphanDeleter()


def info( request ):
    """ Returns simplest response. """
    now = datetime.datetime.now()
    log.debug( 'now, ```{}```'.format(now) )
    return HttpResponse( '<p>hi</p> <p>( %s )</p>' % now )


@csrf_exempt
def gh_inscription_watcher( request ):
    """ Handles github inscriptions web-hook notification. """
    log.debug( 'request.__dict__, ```{}```'.format(pprint.pformat(request.__dict__)) )
    resp = HttpResponseForbidden( '403 / Forbidden' )  # will be returned if incorrect basic-auth credentials are submitted, or if signature check fails.
    if 'HTTP_AUTHORIZATION' in request.META:
        ( submitted_basic_auth_info, submitted_signature, submitted_payload ) = ( request.META['HTTP_AUTHORIZATION'].decode('utf-8'), request.META['HTTP_X_HUB_SIGNATURE'].decode('utf-8'), request.body.decode('utf-8') )
        if github_validator.validate_submission( submitted_basic_auth_info, submitted_signature, submitted_payload ):
            github_helper.handle_inscription_update( request.body, request.META.get('HTTP_HOST', None), submitted_signature )
            resp = HttpResponse( '200 / OK' )
    else:
        resp = github_validator.make_unauthenticated_response()
    log.debug( 'response status code, `{}`'.format(resp.status_code) )
    return resp


def process_all( request ):
    return HttpResponse( 'process_all coming' )


def delete_solr_orphans( request ):
    """ Manages initial request to delete orphaned records from solr. """
    request.session['ids_to_delete'] = json.dumps( [] )
    resp = HttpResponseForbidden( '403 / Forbidden' )
    ( eppn, dev_user, host ) = ( request.META.get('Shibboleth-eppn', ''), request.GET.get('dev_auth_hack', ''), request.get_host() )
    if admin_validator.validate_admin_request( eppn, dev_user, host ):
        data = orphan_deleter.prep_data()
        request.session['ids_to_delete'] = json.dumps( data )
        context = orphan_deleter.prep_context( data )
        resp = render( request, u'iip_processing_templates/show_proposed_deletions.html', context )
    log.debug( 'resp.__dict__, ```{}```'.format(pprint.pformat(resp.__dict__)) )
    return resp


def process_solr_deletions( request ):
    """ Triggers actual deletion-processing.
        The POST requirement, combined with built-in csrf protection, is enough to ensure hits are valid. """
    resp = HttpResponseForbidden( '403 / Forbidden' )
    if request.method == 'POST':
        orphan_deleter.run_deletes( json.loads(request.session.get('ids_to_delete')) )
        resp = HttpResponse( 'deletions completed' )
    request.session['ids_to_delete'] = json.dumps( [] )
    log.debug( 'resp.__dict__, ```{}```'.format(pprint.pformat(resp.__dict__)) )
    return resp


@csrf_exempt
def update_processing_status( request ):
    """ Updates status table. """
    log.debug( 'request.__dict__, ```{}```'.format(pprint.pformat(request.__dict__)) )
    log.debug( 'request.POST, ```{}```'.format(pprint.pformat(request.POST)) )
    resp = HttpResponseForbidden( '403 / Forbidden' )
    if unicode( request.META.get('HTTP_HOST', '') ) == '127.0.0.1':
        log.debug( 'host ok' )
        log.debug( 'request.body, ```{}```'.format(request.body) )
        data_dct = json.loads( request.body )
        log.debug( 'data_dct, ```{}```'.format(pprint.pformat(data_dct)) )
        ##
        to_process_dct = data_dct.get( 'to_process_dct', '' )
        log.debug( 'to_process_dct, ```{}```'.format(pprint.pformat(to_process_dct)) )
        if to_process_dct:
            log.debug( 'here' )
            for inscription_id in to_process_dct.get( 'files_removed', [] ):
                log.debug( 'here' )
                try:
                    log.debug( 'here' )
                    process_status = Status.objects.get( inscription_id=inscription_id )
                except Exception as e:
                    log.debug( 'here' )
                    process_status = Status()
                process_status.status_summary = 'queued for deletion'
                process_status.status_detail = ''
                process_status.save()
            for inscription_id in to_process_dct.get( 'files_updated', [] ):
                log.debug( 'inscription_id, `{}`'.format(inscription_id) )
                try:
                    log.debug( 'here' )
                    process_status = Status.objects.get( inscription_id=inscription_id )
                except Exception as e:
                    log.debug( 'here' )
                    process_status = Status( inscription_id=inscription_id )
                process_status.status_summary='queued for update'
                process_status.status_detail = ''
                process_status.save()
            resp = HttpResponse( '200 / OK' )
        ##
        else:
            ( inscription_id, new_status_summary, new_status_detail ) = (
                data_dct.get('inscription_id', ''), data_dct.get('status_summary', ''), data_dct.get('status_detail', '') )
            log.debug( 'inscription_id, `{}`'.format(inscription_id) )
            log.debug( 'new_status_summary, `{}`'.format(new_status_summary) )
            log.debug( 'new_status_detail, `{}`'.format(new_status_detail) )
            if inscription_id and new_status_summary:
                try:
                    process_status = Status.objects.get( inscription_id=inscription_id )
                except Exception as e:
                    process_status = Status( inscription_id=inscription_id )
                process_status.status_summary = new_status_summary
                process_status.status_detail = new_status_detail
                process_status.save()
                resp = HttpResponse( '200 / OK' )
    return resp
