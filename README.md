# JDL Creator

## What's that???

The JDL Creator is an python class which make submits with HTCondor easier. It creates an folder for the logs, the JDL file and a file for the argument list.

## How can I use it?

The `create_jdl.py` script is an example. It creates 5 jobs with the executable `job.sh` and the arguments `0`, `1`, `2`, `3`, `4`. The requirements for an CPU intesiv EKP job.

When run run the script, it will create a directory `condor_jobs` with subdirectories for logging output and error files for the jobs. In `condor_jobs`your executable will be copied.
