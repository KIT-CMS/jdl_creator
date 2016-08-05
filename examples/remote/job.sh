#!/bin/bash

echo "hostname: " `hostname`

echo "how am I? " `id`
pwd

SPAWNPOINT=`pwd`

## setup CMSSW
    VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
	source $VO_CMS_SW_DIR/cmsset_default.sh
	cd CMSSW_7_1_19/src
    scram b ProjectRename
	eval `scramv1 runtime -sh`

	echo "arguments:"
    for a in ${BASH_ARGV[*]} ; do
	    echo -n "$a "
    done

    echo '### go back to spawnpoint ###'
	cd ${SPAWNPOINT}
	pwd
	ls
    
    which combine

    # start limit calulation
    echo '### start limit calculation ###'
	combine -M Asymptotic tH_comb_${1}.txt >> limits_${1}.txt
    ls -la

    # move result files to file server
    mv higgsCombineTest.Asymptotic.mH120.root limits_${1}.root	
	echo '### end of job ###'

## end of script

