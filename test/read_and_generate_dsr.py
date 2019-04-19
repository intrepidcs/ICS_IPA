import numpy as np
import datetime
import pprint
import enum
import sys
import os
import logging

from ICS_IPA import DataFileIOLibrary as icsFI
from ICS_IPA import DSRTools as icsDSR
from ICS_IPA import IPAInterfaceLibrary

slFilePath = "./examples/findInFiles/ConfigForSampleDataFileDemo.asl"
dbFilePaths = [
    {"path": "./examples/Data/SampleDataFiles/DataSpySampleDataFileAllSignals1.db"}]

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
handler = logging.FileHandler('IPA.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.info("Hello")

# ------------------------------------------------------------------------------------------------------------------
dsr = icsDSR.DSRFile()
# there are multiple methods to save to a dsr file.

# the loop method

for dbFilePath in dbFilePaths:
    try:
        with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:

            accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")
            transOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")

            curTimestamp = data.JumpAfterTimestamp(0)
            dataPoints = data.GetPoints()
            dsr.Begin(data)
            while curTimestamp != sys.float_info.max:
                dsr.IncludeCurrentRecord(
                    dataPoints[accelpedalPostionIndex] > 80 and dataPoints[transOutputSpeedIndex] < 1600)
                curTimestamp = data.GetNextRecord()
            dsr.End()
    except ValueError as e:
        print(str(e))

# ------------------------------------------------------------------------------------------------------------------

# the i'll do everything method

for dbFilePath in dbFilePaths:
    try:
        trigger = False
        start = 0
        with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:

            accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")
            transOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")

            curTimestamp = data.JumpAfterTimestamp(0)
            dataPoints = data.GetPoints()
            while curTimestamp != sys.float_info.max:
                query = dataPoints[accelpedalPostionIndex] > 80 and dataPoints[transOutputSpeedIndex] < 1600
                if query and not trigger:
                    trigger = not trigger
                    start = curTimestamp
                elif not query and trigger:
                    trigger = not trigger
                    dsr.IncludeHit(data, start, curTimestamp, "hit test")
                curTimestamp = data.GetNextRecord()
    except ValueError as e:
        print(str(e))

# ------------------------------------------------------------------------------------------------------------------

# the lamda method
for dbFilePath in dbFilePaths:
    try:
        with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:

            accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")
            transOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")
            # using lambdas, you can think of lambdas as functions without a name
            # the following lambda has two parameters v and t. v for values and t for time
            # the AddToDSR function takes a function with two paramaters as an argument
            # The AddToDSR calls the function for every data point it iterates though to determan if it should be included in the DSR file
            # The following two calls do the same thing in two diffrent ways the first uses a lambda

            dsr.Add(data, lambda v, t: v[accelpedalPostionIndex]
                    > 80 and v[transOutputSpeedIndex] < 1600)
    except ValueError as e:
        print(str(e))
# ------------------------------------------------------------------------------------------------------------------


class Sig:
    ''' simply passes a function '''
    TransOutputSpeed = 0
    AccelPedalPosition = -1


def checkFullThrotel(values, timestamp):
    return values[Sig.AccelPedalPosition] > 80 and values[Sig.TransOutputSpeed] < 1600


for dbFilePath in dbFilePaths:
    try:
        with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:
            dsr.Add(data, checkFullThrotel, "Full Throtel hit")

    except ValueError as e:
        print(str(e))
# ------------------------------------------------------------------------------------------------------------------


class dataCheck:
    ''' using a class '''

    def __init__(self, data):
        self.AccelPedalPositionIndex = data.indexOfSignal("AccelPedalPosition")
        self.TransOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")
        self.AccelPedalPositionMax = 80
        self.TransOutputSpeedMin = 1600

    # this is the required callback function for the class
    def __call__(self, values, timestamp):
        return values[self.AccelPedalPositionIndex] > self.AccelPedalPositionMax and values[self.TransOutputSpeedIndex] < self.TransOutputSpeedMin


for dbFilePath in dbFilePaths:
    try:
        with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:
            dc = dataCheck(data)
            dsr.Add(data, dc, hitDiscretion="Class Example hit")
    except ValueError as e:
        print(str(e))

# ------------------------------------------------------------------------------------------------------------------


class AdvancedDataCheck:


''' uses a class witch the starting point of the file is used as max trigger '''

    def __init__(self, data):
        self.AccelPedalPositionIndex = data.indexOfSignal("AccelPedalPosition")
        self.TransOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")
        self.previousAccelPedalPosition = None
        self.AccelPedalPositionMax = 80
        self.TransOutputSpeedMin = 1600

    # this is the required callback function for the class
    def __call__(self, values, timestamp):
        if self.previousAccelPedalPosition is None:
            self.previousAccelPedalPosition = values[self.AccelPedalPositionIndex]
            return True
        return values[self.AccelPedalPositionIndex] > self.AccelPedalPositionMax and values[self.TransOutputSpeedIndex] < self.TransOutputSpeedMin

for dbFilePath in dbFilePaths:
    try:
        with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:
            dc = AdvancedDataCheck(data)
            dsr.Add(data, dc, hitDiscretion="Class Example hit")
    except ValueError as e:
        print(str(e))

# ------------------------------------------------------------------------------------------------------------------
dsr.save("test.dsr")
