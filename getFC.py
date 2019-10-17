#! /usr/bin/env python

import os
import sys
import glob

#sys.path.append("/home/mperkett/RESEARCH/perkett_tools/MSMTools")
sys.path.append("/work/singaram/MSM/singaram/singaram_tools/MSMTools")
from MSMTools import getMSMCompletionFrac


def getLagTimes(dirName):
    """
    Return a list of lag times found in dirName.
    """
    assert os.path.isdir(dirName)

    lagTimes = []
    fileNames = glob.glob(os.path.join(dirName,"pNt_t*.db"))
    for fileName in fileNames:
        lagTimes.append( int(fileName.split("pNt_t")[-1].split(".")[0]) )
        
    lagTimes.sort()
    return lagTimes


def main():
    """
    Usage: ./getFC.py dirName maxIndex <maxTime>
    """
    # command line arguments
    if len(sys.argv) == 3:
        dirName = sys.argv[1]
        maxIndex = int(sys.argv[2])
        maxTime = None

    elif len(sys.argv) == 4:
        dirName = sys.argv[1]
        maxIndex = int(sys.argv[2])
        maxTime = int(sys.argv[3])
        
    else:
        print(main.__doc__)
        sys.exit(1)

    assert os.path.isdir(dirName)
    ### User Parameters ###
    compTimesFileName = os.path.abspath("../completionTimes.txt")
    pwd = os.getcwd()
    #######################

    if maxTime is None:
        assert os.path.isfile(compTimesFileName)
    
    lagTimes = getLagTimes(dirName)
    print(lagTimes)
    for lagTime in lagTimes:
        inFileName = "pNt_t%i.db" % lagTime
        os.chdir(dirName)
        if maxTime is not None:
            getMSMCompletionFrac(lagTime,maxIndex,inFileName,cutoffTime=maxTime)
            print("CORRECT")
        else:
            getMSMCompletionFrac(lagTime,maxIndex,inFileName,compFileName=compTimesFileName)
        os.chdir(pwd)
    
    return 


if __name__ == "__main__":
    main()
