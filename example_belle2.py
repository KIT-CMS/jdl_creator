#!/usr/bin/env python

from classes.JDLCreator import JDLCreator  # import the class to create and submit JDL files


def main():
    jobs = JDLCreator("condocker")  # run jobs on condocker cloude site
    jobs.image = "ipython:v1_r26519_v01-01-07_r28283"
    ##################################
    # submit job 
    ##################################
    jobs.executable = "job.sh"  # name of the job script

    # build list of arguments
    arguments = [x for x in range(0, 5)]
    jobs.arguments = arguments  # set arguments for condor job

    jobs.requirements = "(TARGET.PROVIDES_CPU == True) && (TARGET.PROVIDES_EKP_RESOURCES == True) && (TARGET.PROVIDES_BELLE_2 == True)"
    jobs.wall_time = 1 * 60 * 60  # set walltime to 1h in sec
    jobs.memory = 2048  # set memory to 2048 MB
    jobs.job_folder = "condor_jobs"  # set name of the folder, where files and information are stored
    jobs.WriteJDL()  # write an JDL file and create folder for log files


if __name__ == "__main__":
    main()
