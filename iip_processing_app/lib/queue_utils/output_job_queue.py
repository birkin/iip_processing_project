# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os, pprint
import redis, rq


QUEUE_NAME = unicode( os.environ['IIP_PRC__QUEUE_NAME'] )


q = rq.Queue( QUEUE_NAME, connection=redis.Redis() )

print u'- number of jobs in queue `%s`: %s' % ( QUEUE_NAME, len(q.jobs) )

for job in q.jobs:
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
    print u'- job info...'; pprint.pprint( job_d )
    print u'---'
