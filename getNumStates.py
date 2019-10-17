#! /usr/bin/env python
import os
import sys

sys.path.append("/work/singaram/MSM/singaram/singaram_tools")
from commonTools import tail

fileName = "mappingBinNumToVal.txt"
assert os.path.isfile(fileName)

inF = open(fileName,"r")
s = tail(inF,1)
inF.close()
numStates = int(s.split()[0]) + 1

print(numStates)

