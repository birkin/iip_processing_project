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
    """ Manages request to delete orphaned records from solr. """
    log.debug( 'request.__dict__, ```{}```'.format(pprint.pformat(request.__dict__)) )
    resp = HttpResponseForbidden( '403 / Forbidden' )
    ( eppn, dev_user, host ) = ( request.META.get('Shibboleth-eppn', ''), request.GET.get('dev_auth_hack', ''), request.get_host() )
    if admin_validator.validate_admin_request( eppn, dev_user, host ):
        context = orphan_deleter.prep_context()
        resp = render( request, u'iip_processing_templates/show_proposed_deletions.html', context )
    log.debug( 'resp.__dict__, ```{}```'.format(pprint.pformat(resp.__dict__)) )
    return resp
