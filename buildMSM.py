#! /usr/bin/env python
"""
Assumed to be running on SLURM.  Submits jobs to the queueing system for a given
    data directory input.  Now incorporates the genMSMInput.py script.
"""

import os
import time
import sys

sys.path.append("/work/singaram/MSM/singaram/singaram_tools")
from commonTools import runCommand, tail


def getNumStates(inputDir):
    """
    Return the number of states as indicated by mappingBinNumToVal.txt file.
    """
    fileName = os.path.join(inputDir, "mappingBinNumToVal.txt")
    assert os.path.isfile(fileName)

    inF = open(fileName,"r")
    s = tail(inF,1)
    inF.close()
    numStates = int(s.split()[0]) + 1
    return numStates


def main():
    """
    Usage: ./buildMSM.py numDirsToUse <seedNum>

    If seedNum is specified, then a random selection of numDirsToUse trajectories
        will be used.  If not specified, then the first numDirsToUse trajectories
        will be used.
    """
    # command line
    if len(sys.argv) == 2:
        numDirsToUse = int(sys.argv[1])
        seedNum = ""
    elif len(sys.argv) == 3:
        numDirsToUse = int(sys.argv[1])
        seedNum = int(sys.argv[2])
    else:
        print(main.__doc__)
        sys.exit()

    ### User Parameters ###
    queueName = "hagan-compute"
    msmScriptsDir = "/home/hagan/shells/msmbuilder/PythonTools_V2-mfh"
    lagTimeInterval = 20
    maxLagTime = 200
    numEigToKeep = 100
    timeStep = 10000
    numStatesScriptName = "getNumStates.py"
    genMSMInputScriptName = "genMSMInput.py"
    #######################

    assert os.path.isfile(numStatesScriptName)
    assert os.path.isfile(genMSMInputScriptName)
    

    # generate script and command to run
    s = """#!/bin/bash
# Build a Micro MSM for a range of lag times
# NOTE: you can find some of Hagan's changes to code by greping MFH in code
#       -d --> path to directory where hierarchical clustering performed (string)
#       -m --> maximum lag time for which to build an MSM
#       -s --> number of microstates
#       -t --> time step (fs) used in simulation; (Steps per Window)
#       -n --> number of largest timescales to get for each model
module load share_modules/ANACONDA/5.3_py2
./%s data-%i %i %s
cwd=`pwd`
cd data-%i
numStates=`../%s`
python %s/BuildMSMsAsVaryLagTime.py -d './' -i %i -m %i -s $numStates -t %i -n %i > runMSM.out
cd $cwd
rm -r data-%i/assignments
""" % (genMSMInputScriptName,numDirsToUse,numDirsToUse,str(seedNum),numDirsToUse,numStatesScriptName,msmScriptsDir, lagTimeInterval, maxLagTime, timeStep, numEigToKeep,numDirsToUse)

    jobName = "job-%i" % numDirsToUse
    scriptName = "run-%i.sh" % numDirsToUse
    outF = open(scriptName,"w")
    outF.write(s)
    outF.close()

    if queueName == "hagan-compute":
        cmd = "sbatch -A hagan-lab -J %s -e msm_test.err -o msm_test.out -p hagan-compute -t 60:00:00 -q medium %s" \
            % (jobName,scriptName)
    elif queueName == "hagan-gpu":
        cmd = "sbatch -A hagan-lab -J %s -p hagan-gpu -t 60:00:00 -q medium --gres=gpu:TitanX:1  %s" \
            % (jobName,scriptName)
    else:
        print("queueName not recognized!")
        sys.exit(1)

    # run
    (stdout,stderr) = runCommand(cmd)

    print(stdout)
    print(stderr)
    outF = open("submission_log.txt","a")
    outF.write("\n%s\n%s\n" % (cmd,stdout))
    outF.close()

    time.sleep(0.25)

    return


if __name__ == "__main__":
    main()
