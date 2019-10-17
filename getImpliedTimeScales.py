#! /usr/bin/env python
"""
Get information about implied timescales from MSM data.
"""

import os
import sys
import glob
from numpy import *

sys.path.append("/work/singaram/MSM/singaram/singaram_tools/MSMTools")
from MSMTools import getImpliedTimeScales


def main():
    """
    Usage: ./getImpliedTimeScales.py dirName

    Writes "impliedTimeScales-%i.txt" % numDirs for all MSM lag times found in
        dirName.
    """
    ### User Parameters ###
    numToKeep = 10
    #######################

    # command line args
    if len(sys.argv) != 2:
        print(main.__doc__)
        sys.exit(1)

    dirName = sys.argv[1]
    assert os.path.isdir(dirName)

    fileNames = [f for f in glob.glob(os.path.join(dirName,"pNt_t*.db")) if os.path.isfile(f)]

    if len(fileNames) == 0:
        print("ERROR!  No file names matching pattern were found!")
        sys.exit(1)

    getNumDirs = lambda f: int(f.split("data-")[-1].split("/")[0])
    getLagTime = lambda f: int(f.split("pNt_t")[-1].split(".db")[0])

    numDirs = getNumDirs(dirName)
    outF = open("impliedTimeScales-%i.txt" % numDirs,"w")
    fileNames.sort(key = getLagTime)
    for fileName in fileNames:
        #print("%s\t%i" % (fileName,getNumDirs(fileName)))

        impTimes = getImpliedTimeScales(fileName,numToKeep)
        #print(impTimes)
        
        # caste array into reals
        impTimes = real(impTimes)

        # format: lagTime \t impliedTime_0 \t impliedTime_1 \t .. \t impliedTime_numToKeep
        lagTime = getLagTime(fileName)
        outF.write("%i" % lagTime)
        for val in impTimes:
            outF.write("\t%f" % val)
        outF.write("\n")
        
    outF.close()

    return


if __name__ == "__main__":
    main()
