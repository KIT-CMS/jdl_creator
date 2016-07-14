#!/usr/bin/env python
from classes.JDLCreator import JDLCreator # import the class to create and submit JDL files
import numpy

def main():
    jobs = JDLCreator()  #run jobs on condocker cloude site
    ##################################
    # submit job 
    ##################################
    jobs.SetExecutable("job.sh")  # set job script

    #build list of arguments
    arguments=[]
    for i in numpy.arange(0, 5,1):
        arguments.append(i)

    jobs.SetArguments(arguments)              # set arguments

    jobs.requirements= "(Target.PROVIDES_CPU ==True) && (TARGET.PROVIDES_EKP_RESOURCES == True)"
    jobs.SetFolder('condor_jobs/')                # set folder !!! you have to copy your job file into the folder
    jobs.WriteJDL()                           # write an JDL file and create folder for log files

if __name__ == "__main__":
    main()

