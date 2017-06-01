#!/usr/bin/env python

from os import system
from time import sleep
from tictoc import *
from subprocess import call


system('python service.py start')
sleep(2)
val = 0
for i in range(0, 100):
    tic()
    call(['python', 'service.py', 'read'])
    val = toc() + val
mean = val / (i + 1)
f = 1/mean
print f
system('python service.py stop')
sleep(2)
system('pgrep -f service.py')

