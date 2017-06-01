#!/usr/bin/env python

from dwfconstants import *
from ctypes import *
import sys
import time


# get dwf
if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

# declare ctype variables
hdwf = c_int()

# # print DWF version
# version = create_string_buffer(16)
# dwf.FDwfGetVersion(version)
# print "DWF Version: " + version.value

# Open device
def openDevice(idx):
    dwf.FDwfDeviceOpen(c_int(idx), byref(hdwf))
    if hdwf.value == hdwfNone.value:
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print szerr.value
        print "failed to open device"
        quit()

# Enable channel
def analogInChannelEnableSet(channel, enable):
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(channel-1), c_bool(enable))

def analogInChannelOffsetSet(channel, value):
    dwf.FDwfAnalogInChannelOffsetSet(hdwf, c_int(channel-1), c_double(value))

def analogInChannelRangeSet(channel, value):
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(channel-1), c_double(value))

def analogInFrequencySet(value):
    dwf.FDwfAnalogInFrequencySet(hdwf, c_double(value))

def analogInBufferSizeSet(value):
    dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(value))

def analogInConfigure(reconfigure, start):
    dwf.FDwfAnalogInConfigure(hdwf, c_bool(reconfigure), c_bool(start))

def analogInStatus(readData):
    state = c_byte()
    dwf.FDwfAnalogInStatus(hdwf, c_bool(readData), byref(state))
    return state

def deviceCloseAll():
    dwf.FDwfDeviceCloseAll()

###########################################################################################

def analogInChannelConfigure(channel, offset, rng, freq, buffer, verbose = False):
    if verbose:
        print 'CHANNEL ' + str(channel)
        print '  - Offset:     ' + str(offset) + ' V'
        print '  - Range:      ' + str(rng) + ' V'
        print '  - Freq:       ' + str(freq)   + ' Hz'
        print '  - Buffer:     ' + str(buffer) + ' samples'
    analogInChannelEnableSet(channel, True)
    analogInChannelOffsetSet(channel, offset)
    analogInChannelRangeSet(channel, rng)
    analogInFrequencySet(freq)
    analogInBufferSizeSet(buffer)
    analogInConfigure(False, False)
    time.sleep(2)

def analogInSample(channel):
    voltage = c_double()
    analogInStatus(False)
    dwf.FDwfAnalogInStatusSample(hdwf, c_int(channel-1), byref(voltage))
    return voltage.value

def analogInStartContinuous():
    analogInConfigure(False, True)
    time.sleep(2)

def analogInSampleContinuous(channel, n):
    while True:
        status = analogInStatus(True)
        if status.value == DwfStateDone.value:
            break
        time.sleep(0.001)
    voltage = (c_double * n)()
    dwf.FDwfAnalogInStatusData(hdwf, c_int(channel-1), voltage, n)
    #voltage = sum(samples)/len(samples)
    return voltage
