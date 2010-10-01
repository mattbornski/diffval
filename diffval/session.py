#!/usr/bin/env python

import os
import signal
import subprocess
import sys
import tempfile

class session:
    def __init__(self, executable, log = None, env = None):
        self._code = None
        self._stdout = []
        self._stderr = []
        self._log = log
        if self._log:
            self._log.openElement('session', {'program':executable})
        signal.signal(signal.SIGTERM, self.cancel)
        try:
            windows = (sys.platform == 'win32' or sys.platform == 'cygwin')
            self._session = subprocess.Popen(['env', executable] + self._args,
              stdin = subprocess.PIPE,
              stdout = subprocess.PIPE,
              stderr = subprocess.PIPE,
              # Experimenting on my Vista box - stdout/stderr don't
              # seem to be captured well, so perhaps this will help.
              shell = windows,
              close_fds = not windows,
              env = env)
            input = None
            if self._input:
                input = '\n'.join(self._input)
            try:
                [out, err] = self._session.communicate(input = input)
                if out:
                    self._stdout += out.split('\n')
                if err:
                    self._stderr += err.split('\n')
            except ValueError:
                # Generated when the pipes are empty.
                pass
            except OSError:
                # Bad things.
                self._stderr.append('<< Session terminated unexpectedly >>')
        except KeyboardInterrupt:
            self.cancel()
        if self._log:
            self._log.closeElement('session')
    def slurp(self):
        # Don't check whether the session has been killed.  That's irrelevant
        # since there could still be data in the pipes.
        try:
            while self._session:
                [out, err] = self._session.communicate()
                if out:
                    self._stdout += out.split('\n')
                if err:
                    self._stderr += err.split('\n')
        except ValueError:
            # Generated when the pipes are empty.
            pass
        except OSError:
            # Bad things.
            self._stderr.append('<< Session terminated unexpectedly >>')
        if self._session.returncode is not None:
            self._code = self._session.returncode
    def cancel(self):
        try:
            if self._session:
                os.kill(self._session.pid, signal.SIGTERM)
        except:
            pass
    def output(self):
        self.slurp()
        out = self._stdout
        self._stdout = []
        return out
    def errors(self):
        self.slurp()
        err = self._stderr
        self._stderr = []
        return err
