#!/usr/bin/env python

from daemonize import Daemon
from device import *
from time import sleep
from signal import signal, pause, getsignal, SIGUSR1, SIGUSR2
import os


class service(Daemon):

    def status(self, *args):
        self.allow()
        print 'Process running.'

    def run(self):
        with Device(*self.args) as self.dev:
            self.dev.start()
            signal(SIGUSR1, self.cmd1)
            signal(SIGUSR2, self.cmd2)
            print 'Process initiated.'
            while True:
                pause()

    def cmd1(self, *args):
        print self.dev.V1()

    def cmd2(self, *args):
        print self.dev.V2()

    def get(self, channel):
        self.allow()
        if   channel == 'V1': os.kill(self.pid, SIGUSR1)
        elif channel == 'V2': os.kill(self.pid, SIGUSR2)

    def stop(self):
        print 'Stopping process...'
        super(service, self).stop()


def daemon(*args):
    return service \
                (
                    pidfile = '/tmp/analog-discovery.pid',
                    stdin   = '/dev/stdin',
                    stdout  = '/dev/stdout',
                    stderr  = '/dev/stderr',
                    args    = args
                )
