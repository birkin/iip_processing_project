To start a worker...

- use the `iip_processor_caller.sh` script located in `/etc/init.d/`
- that script takes a `start`, `stop`, or `status` argument
- it calls a `callee.sh` script located in `iip_processing_stuff`, which...
    - `cd`s to the project directory
    - `source`s the virtual-environment
    - runs an `rqworker` command, which specifies...
        - a pid path
        - a log path

---
