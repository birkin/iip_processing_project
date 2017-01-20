#!/bin/bash

# Note:
# When an app setting is changed for code called by a worker, restart the worker from the `iip_stuff/iip` dir.
#
# Example...
#
# $ ps aux | grep "rq"
# (to find out worker PID)
#
# $ cd /path/to/iip_stuff/iip/
# $ source ../env_iip/bin/activate
# $ kill PID
# $ bash ./iip_search_app/utils/queue_utils/worker_start.sh
#
# $ ps aux | grep "rq"
# (to confirm new worker is running)



echo "worker name: " $IIP_PRC__WORKER_NAME
echo "log filename: " $IIP_PRC__WORKER_LOG_FILENAME
echo "queue name: " $IIP_PRC__QUEUE_NAME

rqworker --name $IIP_PRC__WORKER_NAME $IIP_PRC__QUEUE_NAME >> $IIP_PRC__WORKER_LOG_FILENAME 2>&1 &
