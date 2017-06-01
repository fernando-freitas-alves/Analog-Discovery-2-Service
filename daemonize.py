#!/usr/bin/env python

import os, sys, time, atexit
from signal import signal, SIGABRT, SIGINT, SIGTERM
from subprocess import check_output, CalledProcessError
from mmap import mmap, ACCESS_READ


class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', args=None):
        self.stdin   = stdin
        self.stdout  = stdout
        self.stderr  = stderr
        self.pidfile = pidfile
        self.args    = args

        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pm = mmap(pf.fileno(), 0, access=ACCESS_READ)
            self.pid = int(pm.read(pm.size()))
            pf.close()
        except IOError:
            self.pid = None
            # pid = -1

    def __enter__(self):
        return self

    def start(self):
        if self.isrunning():
            # message = "pidfile %s already exist. Daemon already running?\n"
            # sys.stderr.write(message % self.pidfile)
            sys.stderr.write("Proccess is already running.\n")
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def isrunning(self):
        if self.pid:
            try:
                list_pid = map(int, check_output(['pgrep', '-f', sys.argv[0]]).strip().split('\n'))
                for running_pid in list_pid:
                    if self.pid == running_pid:
                        return True
            except CalledProcessError:
                # Process not found
                pass

        return False

    def allow(self):
        if not self.isrunning():
            sys.stderr.write("Process not running.\n")
            sys.exit(1)

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            self.pid = os.fork()
            if self.pid != 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            self.pid = os.fork()
            if self.pid != 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        self.pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % self.pid)

        # flag signal
        for sig in (SIGABRT, SIGINT, SIGTERM):
            signal(sig, self.clean)

    def delpid(self):
        os.remove(self.pidfile)

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """

    def clean(self, *args):
        """
        You should override this method when you subclass Daemon and super call it again. It will be called
        before the process has been stopped by stop() or kill.
        """
        sys.exit(0)

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        self.__exit__()

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        if not self.pid:
            # message = "pidfile %s does not exist. Daemon not running?\n"
            # sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(self.pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
