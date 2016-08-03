#!/bin/bash

OUTPUT_PATH="/storage/a/USER/results/"
echo "hostname: " `hostname`

echo "how am I? " `id`
pwd

SPAWNPOINT=`pwd`

## setup CMSSW
    VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
	source $VO_CMS_SW_DIR/cmsset_default.sh
	SCRAM_ARCH=slc6_amd64_gcc481
	scramv1 project CMSSW_7_1_19
	cd CMSSW_7_1_19/src
	eval `scramv1 runtime -sh`

## setup combine
	git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
	echo 'after git clone'
	cd HiggsAnalysis/CombinedLimit
	git fetch origin
	git checkout v5.0.2
	scramv1 b clean; scramv1 b


	echo "arguments:"
    for a in ${BASH_ARGV[*]} ; do
	    echo -n "$a "
    done

	cd ${SPAWNPOINT}
	pwd
	ls

    # copy files in work direcotry of workernode
	cp /storage/a/mschnepf/tHq/13tev/full_workdir/${1}/tH_comb_${1}.txt .
	cp /storage/a/mschnepf/tHq/13tev/full_workdir/${1}/tH_?m_${1}.root .
	cp /storage/a/mschnepf/tHq/13tev/full_workdir/${1}/tH_?m_${1}.txt .

    # start limit calulation
	combine -M Asymptotic tH_comb_${1}.txt >> limits_${1}.txt
    ls -la

    # move result files to file server
	mv limits_${1}.txt ${OUTPUT_PATH}/limits_${1}.txt
    mv higgsCombineTest.Asymptotic.mH120.root ${OUTPUT_PATH}/limits_${1}.root	
	echo '### end of job ###'

## end of script

