#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.dirname('../../classes')) # change path to classes directory
from classes.JDLCreator import JDLCreator  # import the class to create and submit JDL files


def main():
    """Submit a simple example job"""

    jobs = JDLCreator("condocker")  # Default (no Cloud Site supplied): Docker with SLC6 image
    # Some example sites:
    # site_name='ekpsupermachines'  "Super Machines" IO intesiv jobs

    jobs.executable = "job.sh"  # name of the job script
    jobs.wall_time = 10 * 60 * 60  # job will finish in 10 hours
    jobs.memory = 2048  # Our regular 2048 MB per slot

    # build list of arguments: 1,2,3,4,5
    arguments = [x for x in range(0, 5)]
    # you can also build a regular list via arg = []; arg.append(value)

    jobs.arguments = arguments  # set arguments for condor job

    # Our job requires lots of CPU resources and needs access to the local EKP resources
    jobs.requirements = "(TARGET.ProvidesCPU ==True) && (TARGET.ProvidesEKPResources == True)"

    jobs.job_folder = "condor_jobs"  # set name of the folder, where files and information are stored
    jobs.WriteJDL()  # write an JDL file and create folder for log files
    jobs.Submit()


if __name__ == "__main__":
    main()
