#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.dirname('../../classes')) # change path to classes directory
from classes.JDLCreator import JDLCreator  # import the class to create and submit JDL files


def main():
    """Submit a simple example job"""

    jobs = JDLCreator()  # Default: job can run everywhere
    # Some example sites to run on an explecite site:
    # site_name='bwforcluster'      Freiburg
    # site_name='gridka'            gridKa School Training VMs


    jobs.executable = 'job.sh'  # name of the job script
    jobs.wall_time = 10 *  60  # job will finish in 10 min
    jobs.memory = 2048  # Our regular 2048 MB per slot

    # build list of arguments: 1,2,3,4,5
    arguments = [0]
    # you can also build a regular list via arg = []; arg.append(value)

    jobs.arguments = arguments  # set arguments for condor job

    # Our job run only at Freiburg
    jobs.requirements = 'TARGET.CloudSite =="BWFORCLUSTER" '

    # add extra line to run job on remote sites
    jobs.AddExtraLines('+RemoteJob = True')

    # start at the end a script to pack the results in an tar file
    jobs.AddExtraLines('+PreCmd = "setup.sh"')
    jobs.AddExtraLines('+PreArguments = ""')

    # start at the end a script to pack the results in an tar file
    jobs.AddExtraLines('+PostCmd = "pack.sh"')
    jobs.AddExtraLines('+PostArguments = "$(Process)"')
    
    # copy tar file with results back
    jobs.output_files = 'sample_$(Process).tar'

    # file to send to workernode
    #jobs.input_files = '../setup.sh,../cms_analysis.tar,../pack.sh,../tH_3m_0.root,../tH_3m_0.txt,../tH_4m_0.root,../tH_4m_0.txt,../tH_comb_0.txt'
    jobs.input_files = '../setup.sh,../pack.sh,../files/'



    jobs.job_folder = 'condor_jobs'  # set name of the folder, where files and information are stored
    jobs.WriteJDL()  # write an JDL file and create folder for log files


if __name__ == "__main__":
    main()
