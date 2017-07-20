#!/usr/bin/env python

from daemonize import Daemon
from device import *
from time import sleep
from signal import signal, pause, getsignal, SIGUSR1, SIGUSR2
import os
from mmap import mmap, ACCESS_WRITE, ACCESS_READ


class service(Daemon):
    bufferfile = '/tmp/analog-discovery.buffer'

    def status(self, *args):
        self.allow()
        print 'Process running.'

    def run(self):
        with Device(*self.args) as self.dev:
            self.dev.start()
            # signal(SIGUSR1, self.cmd1)
            # signal(SIGUSR2, self.cmd2)
            T = 1/self.dev.freq[1]
            print 'Process initiated.'
            # while True:
            #     pause()

            # f = open(self.bufferfile, 'wb')
            # f.write(b'123')
            # f.close()
            # with open(self.bufferfile, 'wb') as f:
            with open(self.bufferfile, 'w') as f:
                # self.m = mmap(f.fileno(), 0, access=ACCESS_WRITE)
                while True:
                #     self.m.seek(0)
                #     # try:
                #     s = str(self.dev.V1()) + b'\n'
                #     print s
                #     self.m.write(s)
                #     # except ValueError:
                #     #     pass
                #     # self.m.write(self.dev.V1())
                    f.seek(0)
                    v = self.dev.V1()
                    # print str(v)
                    # f.write(str(v) + b'\n')
                    f.write(str(v))
                    sleep(.01)

    # def cmd1(self, *args):
    #     print self.dev.V1()
    #
    # def cmd2(self, *args):
    #     print self.dev.V2()

    def get(self, channel):
        self.allow()
        # if   channel == 'V1': os.kill(self.pid, SIGUSR1)
        # elif channel == 'V2': os.kill(self.pid, SIGUSR2)
        # with open(self.bufferfile, 'rb') as f:
        with open(self.bufferfile, 'r') as f:
            try:
                m = mmap(f.fileno(), 0, access=ACCESS_READ)
                for line in iter(m.readline, ''):
                    print line,
                m.close()
            except ValueError:
                pass

    def stop(self):
        print 'Stopping process...'
        super(service, self).stop()

    # def clean(self, *args):
    #     print 'Cleaning...'
    #     self.m.close()
    #     super(service, self).clean(args)


def daemon(*args):
    return service \
                (
                    pidfile = '/tmp/analog-discovery.pid',
                    stdin   = '/dev/stdin',
                    stdout  = '/dev/stdout',
                    stderr  = '/dev/stderr',
                    args    = args
                )
