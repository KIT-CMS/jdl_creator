#!/usr/bin/env python
from classes.JDLCreator import JDLCreator # import the class to create and submit JDL files
import numpy

def main():
    jobs = JDLCreator("condocker")  #run jobs on condocker cloude site
    jobs.image = "ipython:v1_r26519_v01-01-07_r28283"
    ##################################
    # submit job 
    ##################################
    jobs.SetExecutable("job.sh")            # set job script

    #build list of arguments
    arguments=[]
    for i in numpy.arange(0, 5,1):
        arguments.append(i)

    jobs.SetArguments(arguments)            # set arguments

    jobs.requirements= "(TARGET.PROVIDES_CPU == True) && (TARGET.PROVIDES_EKP_RESOURCES == True) && (TARGET.PROVIDES_BELLE_2 == True)"
    jobs.wall_time = 1*60*60                # set walltime to 1h in sec
    jobs.memory = 2048                      # set memory to 2048 MB
    jobs.SetFolder('condor_jobs/')          # set folder 
    jobs.WriteJDL()                         # write an JDL file and create folder for log files

if __name__ == "__main__":
    main()

