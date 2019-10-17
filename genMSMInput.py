#! /usr/bin/env python2
"""
NOTE: MODIFICATIONS FOR SIZE 90 COMPLETE CAPSID -- very slight modifications for Jason


orderParameters = ("numAdsorbed","nCluster")
"""

import sys
import os
import shutil
import glob
from numpy import *

# my functions
sys.path.append("/work/singaram/MSM/singaram/singaram_tools/MSMTools")
from MSMTools import *
#from MultiSpheres import *
#from PatchySpheres import *
from Diamonds import *


def getBinBounds(orderParameters,extrema):
    """
    Returns a list of lists containing all the bin boundaries.  This is meant
        to be a highly specific function that is often modified to try new
        types of binning and different order parameters.

    Return: [ binBoundsList1, binBoundsList2, .. ]
        binBoundsList -> [ val1, val2, ... valN+1 ]
        bin1: val1 <= x < val2
        bin2: val2 <= x < val3
                    .
                    .
        binN: valN <= x < valN+1
    """
    assert len(orderParameters) == 2
    assert orderParameters[0] == "nCluster"
    assert orderParameters[1] == "numAdsorbed"

    binBounds = []

    # nCluster
    binBounds.append( [i + 0.5 for i in range(-1,max(40,int(extrema[1,0])+1))] )

    # numAdsorbed
    binBounds.append( [i + 0.5 for i in range(-1,max(40,int(extrema[1,0])+1))] )

    return binBounds


def getLumpedStates(orderParameters,mappingBinToVals):
    """
    Generate a list of bin numbers that correspond to the initial and final state.
    """
    # NOTE: This also will generally be a very specific function that is likely to
    #    change.
    assert len(orderParameters) == 2
    assert orderParameters[0] == "nCluster"
    assert orderParameters[1] == "numAdsorbed"

    nClusterIndex = 0
    nClusterStartVal = 1
    nClusterEndVal = 30

    numAdsIndex = 1
    numAdsStartVal = 0

    finalStateBins = []
    initialStateBins = []
    for i in range(len(mappingBinToVals)):
        # if final internal structure is correct
        if mappingBinToVals[i][nClusterIndex][0] <= nClusterEndVal < mappingBinToVals[i][nClusterIndex][1]:
            finalStateBins.append(i)

        # if initial internal structure AND number adsorbed onto nanosphere is correct
        elif mappingBinToVals[i][nClusterIndex][0] <= nClusterStartVal < mappingBinToVals[i][nClusterIndex][1] and \
                mappingBinToVals[i][numAdsIndex][0] <= numAdsStartVal < mappingBinToVals[i][numAdsIndex][1]:
            initialStateBins.append(i)

    assert len(finalStateBins) > 0
    assert len(initialStateBins) > 0

    return (initialStateBins, finalStateBins)


def getNonZeroBins(binCounts):
    """
    Return the "non-empty" bins.  This can be used to eliminate bins with few, but
    non zero counts.
    """
    nonZeroIndices = []
    for binNum in range(len(binCounts)):
        if binCounts[binNum] > 100:
            nonZeroIndices.append(binNum)

    return array(nonZeroIndices)
    return nonzero(binCounts)[0]


def main():
    """
    Generate the input files necessary to run MSMBuilder (v1.)

    Usage: ./genMSMInput.py dirName <numTrajsToUse> <seedNum>

    If seedNum is specified, then numTrajsToUse must be specified. A random 
        selection of numTrajsToUse will be used.  If not specified, then the 
        first numTrajsToUse trajectories will be used.
    """
    # NOTE: assumed that orderParametersToBin are all listed first, with all extra
    #   order parameters listed last
    simBaseDir = "../../"
    orderParametersToRead = ("nCluster","numAdsorbed")
    orderParametersToBin = ("nCluster","numAdsorbed")
    numOPs = len(orderParametersToRead)

    # command line args
    if len(sys.argv) == 2:
        outDir = sys.argv[1]
        numDirsToUse = -1
        seedNum = None

    elif len(sys.argv) == 3:
        outDir = sys.argv[1]
        if sys.argv[2] == "*":
            numDirsToUse = -1
        else:
            numDirsToUse = int(sys.argv[2])
        seedNum = None

    elif len(sys.argv) == 4:
        outDir = sys.argv[1]
        if sys.argv[2] == "*":
            numDirsToUse = -1
        else:
            numDirsToUse = int(sys.argv[2])
        seedNum = int(sys.argv[3])

    else:
        print(main.__doc__)
        return

    if not os.path.isdir(outDir):
        os.mkdir(outDir)


    if os.path.isdir(os.path.join(outDir,"assignments")):
        shutil.rmtree(os.path.join(outDir,"assignments"))
    os.mkdir(os.path.join(outDir,"assignments"))


    seedDirs = [d for d in glob.glob(os.path.join(simBaseDir,"seed-*")) if os.path.isdir(d)]
    seedDirs.sort(key = lambda x: int(x.split("-")[-1]))

    seedDirs = getSeedDirs(simBaseDir)

#    # MODIFICATION BELOW
#    # running jobs
#    blacklist = ['../../seed-3481', '../../seed-3515', '../../seed-3520', '../../seed-3522', '../../seed-3533', '../../seed-3535', '../../seed-3546', '../../seed-3547', '../../seed-3548', '../../seed-3553', '../../seed-3555', '../../seed-3557', '../../seed-3559', '../../seed-3561', '../../seed-3562', '../../seed-3566', '../../seed-3570', '../../seed-3571', '../../seed-3572', '../../seed-3574', '../../seed-3575', '../../seed-3578', '../../seed-3579', '../../seed-3581', '../../seed-3582', '../../seed-3583', '../../seed-3584', '../../seed-3585', '../../seed-3586', '../../seed-3587', '../../seed-3588', '../../seed-3589', '../../seed-3590', '../../seed-3591', '../../seed-3592', '../../seed-3593', '../../seed-3594', '../../seed-3595', '../../seed-3596', '../../seed-3597', '../../seed-3598', '../../seed-3599', '../../seed-3600', '../../seed-3601', '../../seed-3602', '../../seed-3603', '../../seed-3604', '../../seed-3605', '../../seed-3606', '../../seed-3607']
#
#    # remove blacklisted directories
#    counter = 0
#    for d in blacklist:
#        if d in seedDirs:
#            seedDirs.remove(d)
#
#    if counter > 0:
#        print("%i directories were removed from seedDirs because they were in the blacklist." % counter)



    # choose a random selection of seedDirs if command line argument requires it
    import random
    if (0 < numDirsToUse < len(seedDirs)) and seedNum is not None:
        random.seed(seedNum)
        print("Using a random sampling of %i of the %i trajectories available." % (numDirsToUse,len(seedDirs)))
        seedDirs = random.sample(seedDirs,numDirsToUse)

    elif (0 < numDirsToUse < len(seedDirs)) and seedNum is None:
        print("Using the first %i of the %i trajectories available." % (numDirsToUse,len(seedDirs)))
        seedDirs = seedDirs[:numDirsToUse]

    # initialize extrama
    extrema = zeros([2,numOPs])
    extrema[0] = 9999999999.99
    extrema[1] = -9999999999.99

    # read and convert trajectory information to an order parameters trajectory
    print("Reading Trajectories.")
    opTrajs = []
    counter = 0
    for seedDir in seedDirs:

        # print info
        if counter % 1 == 0:
            print("\t%s" % seedDir)
        counter += 1

        # get order parameter trajectory
        opTraj = getOrderParamsTraj(seedDir,orderParametersToRead)
        if opTraj is None or len(opTraj) == 0:
            print("Warning: opTraj is None or len(opTraj) == 0!  Skipping!")
            continue
        opTrajs.append(opTraj)

        # update extrema if necessary
        for j in range(numOPs):
            mn = opTraj[j].min()
            mx = opTraj[j].max()
            if mn < extrema[0,j]:
                #print("%s: extrema = %s" % (seedDir,extrema))
                extrema[0,j] = mn
            if mx > extrema[1,j]:
                #print("%s: extrema = %s" % (seedDir,extrema))
                extrema[1,j] = mx

        #print("extrema = %s" % extrema)
        #print("opTraj = ")
        #print(opTraj)

    # write extrema to file
    print("extrema = %s" % extrema)
    outF = open(os.path.join(outDir,"extrema.out"),"w")
    for i in range(len(extrema[0])):
        outF.write("%s\n" % orderParametersToRead[i])
        outF.write("[%s,%s]\n" % (str(extrema[0,i]),str(extrema[1,i])) )
    outF.close()
        


    # convert the order parameters trajectory to a bin number trajectory
    print("Converting Trajectories to bin numbers.")
    binBounds = getBinBounds(orderParametersToBin,extrema[:,:len(orderParametersToBin)])
    mappingBinToVals = getMappingBinToVals(binBounds)

    #for i in range(len(mappingBinToVals)):
    #    print("%i\t%s" % (i,str(mappingBinToVals[i])))

    numBins = len(mappingBinToVals)

    binCounts = zeros(numBins)
    binTrajs = []
    for opTraj in opTrajs:
        binTraj = binFunc(opTraj[:len(orderParametersToBin)],binBounds)
        binTrajs.append(binTraj)

        # keep total bin count tally
        binCount = bincount(binTraj)
        binCounts[:len(binCount)] += binCount

    # write non-mapped bin counts to file
    outF = open(os.path.join(outDir,"binCounts-non_mapped.txt"),"w")
    for binNum in range(len(binCounts)):
        outF.write("%i\t%i\n" % (binNum,binCounts[binNum]))
    outF.close()

    # set of non-zero bin numbers (sorted)
    nonzeroIndices = getNonZeroBins(binCounts)
    initialStateBins, finalStateBins = getLumpedStates(orderParametersToRead,mappingBinToVals)

    #print("initialStateBins = %s" % str(initialStateBins))
    #print("finalStateBins = %s" % str(finalStateBins))


    # correct the bin number trajectory lumping multiple bins into the initial
    convertDict, reverseConvertDict, numBins = createMapping(initialStateBins,finalStateBins,nonzeroIndices)

    # write a conversion from newBinNum to value(s)
    outF = open(os.path.join(outDir,"mappingBinNumToVal.txt"),"w")
    for i in range(numBins):
        outF.write("%i" % i)
        for index in reverseConvertDict[i]:
            outF.write("\t%s" % str(mappingBinToVals[index]) )
        outF.write("\n")
    outF.close()

    print("Re-mapping trajectory bins and writing output.")
    outTrajListF = open(os.path.join(outDir,"trajlist"),"w")
    fileNum = 1
    newBinCounts = zeros(numBins,dtype="int64")
    for binTraj in binTrajs:
        outF = open(os.path.join(outDir,"assignments","sd%i" % fileNum),"w")
        outTrajListF.write("sd%i\n" % fileNum)

        newBinTraj = []
        for i in range(len(binTraj)):
            if convertDict.has_key(binTraj[i]):
                n = convertDict[binTraj[i]]
            else:
                # if key doesn't exist, assume that it has been gotten rid of
                # TODO: NOTE: it might be better to set n to the previous value of n so that
                #       the times don't get screwed up, but this should only happen a
                #       relative handful of times, so I will ignore it for now
                continue
                #print("key error!")
                #sys.exit(1)

            # if it ends as a capsid, leave it there 200 frames
            if n == numBins - 1:
                for j in range(200):
                    outF.write("%i\n" % n)
                    newBinTraj.append(n)
                break

            else:
                outF.write("%i\n" % n)
                newBinTraj.append(n)
        else:
            print("Warning: Did not end up as a capsid!")
            print("n = %i  binTraj[i] = %s" % (n,str(binTraj[i])))

        outF.close()

        # tally bin counts in new bins
        newBinCount = bincount(array(newBinTraj))
        newBinCounts[:len(newBinCount)] += newBinCount

        fileNum += 1

    outTrajListF.close()

    # write mapped bin counts to file
    outF = open(os.path.join(outDir,"binCounts.txt"),"w")
    for binNum in range(numBins):
        outF.write("%i\t%i\n" % (binNum,newBinCounts[binNum]))
    outF.close()


    print("Done.")
    return


if __name__ == "__main__":
    main()
