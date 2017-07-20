#!/usr/bin/env python

from dwflib import *


class Device:

    def __init__(self, offset=[], rng=[], freq=[], buffer=[], verbose=[]):
        self.offset  = self.parsearg(offset,     0) # V
        self.rng     = self.parsearg(rng,       50) # V
        self.freq    = self.parsearg(freq,    20e6) # Hz
        self.buffer  = self.parsearg(buffer,     1) # sample(s)
        self.verbose = self.parsearg(verbose, True)

    def __enter__(self):
        return self

    def parsearg(sefl, arg, default):
        if isinstance(arg, list):
            if   len(arg) >  1: return arg[:2]
            elif len(arg) == 1: return 2 * arg
            else:               return 2 * [default]
        else:                   return 2 * [arg]

    def start(self):
        deviceCloseAll()
        openDevice(-1)
        for idx in [0]: #1]:
            analogInChannelConfigure(idx+1,
                                     self.offset[idx],
                                     self.rng[idx],
                                     self.freq[idx],
                                     self.buffer[idx],
                                     self.verbose[idx])

    def V1(self):
        return analogInSample(1)

    def V2(self):
        return analogInSample(2)

    def stop(self):
        deviceCloseAll()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
