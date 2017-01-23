To start a worker...

- use the `init_iip_worker_caller.sh` script located in `/etc/init.d/`
- that script takes a `start`, `stop`, or `status` argument
- it calls an `init_iip_worker_callee.sh` script located in `iip_processing_stuff`, which...
    - `cd`s to the project directory
    - `source`s the virtual-environment
    - runs an `rqworker` command, which specifies...
        - a pid path
        - a log path

---
