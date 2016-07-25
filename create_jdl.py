#!/usr/bin/env python
from classes.JDLCreator import JDLCreator  # import the class to create and submit JDL files


def main():
    """Submit a simple example job"""

    jobs = JDLCreator("condocker")  # Default (no Cloud Site supplied): Docker with SLC6 image
    # Some example sites:
    # site_name='condocker'         Exclusively run the job on our desktop cluster
    # site_name='bwforcluster'      Freiburg
    # site_name='ekpsupermachines'  "Super Machines" in floor 9 server room
    # site_name='gridka'            gridKa School Training VMs

    jobs.executable = "job.sh"  # name of the job script
    jobs.wall_time = 10 * 60 * 60  # job will finish in 10 hours
    jobs.memory = 2048  # Our regular 2 GB per core

    # build list of arguments: 1,2,3,4,5
    arguments = [x for x in range(0, 5)]
    # you can also build a regular list via arg = []; arg.append(value)

    jobs.arguments = arguments  # set arguments for condor job

    # Our job requires lots of CPU resources and needs access to the local EKP resources
    jobs.requirements = "(Target.PROVIDES_CPU ==True) && (TARGET.PROVIDES_EKP_RESOURCES == True)"

    jobs.job_folder = "condor_jobs"  # set name of the folder, where files and information are stored
    jobs.WriteJDL()  # write an JDL file and create folder for log files


if __name__ == "__main__":
    main()
