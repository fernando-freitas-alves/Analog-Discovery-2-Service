#!/usr/bin/env python

import time

__tic_time = 0


def tic():
    global __tic_time
    __tic_time = time.time()


def toc():
    global __tic_time
    return time.time() - __tic_time
