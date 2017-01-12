# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging, pprint

log = logging.getLogger(__name__)


def log_github_post( request ):
    """ Logs data posted from github.
        Called by views.git_watcher() """
    post_data_dict = {
        'datetime': datetime.datetime.now(),
        # TODO
        }
    log.debug( 'post_data_dict, ```{}```'.format(pprint.pformat(post_data_dict)) )
    return
