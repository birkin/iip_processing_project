# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os, pprint
import redis, rq


QUEUE_NAME = unicode( os.environ['IIP_PRC__QUEUE_NAME'] )


failed_queue = rq.queue.get_failed_queue( connection=redis.Redis(u'localhost') )

d = { u'failed_target_count': None, u'jobs': [] }
failed_count = 0
for job in failed_queue.jobs:
    if not job.origin == QUEUE_NAME:
        continue
    failed_count += 1
    job_d = {
        u'_args': job._args,
        u'_kwargs': job._kwargs,
        u'_func_name': job._func_name,
        u'description': job.description,
        u'dt_created': job.created_at,
        u'dt_enqueued': job.enqueued_at,
        u'dt_ended': job.ended_at,
        u'origin': job.origin,
        u'id': job._id,
        u'traceback': job.exc_info,
        u'meta': job.meta,
        u'_result': job._result,
        u'_status': job._status,
        }
    d[u'jobs'].append( job_d )
d[u'failed_target_count'] = failed_count
pprint.pprint( d )
