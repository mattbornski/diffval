#!/usr/bin/env python

import session
import test

import os
import sys

test_start_line = '### idlval testing begins ###'
test_end_line = '### idlval testing ends ###'
mem_start_line = '### idlval mem check begins ###'
mem_end_line = '### idlval mem check ends ###'
halting_line = '% Execution halted at: '
not_a_test_line = "% Attempt to call undefined procedure/function: 'TEST'."

def match(first, second, exact = True):
    if exact:
        if first == second:
            return True
    elif second.startswith(first):
        return True
    return False

def index(line, array, exact = True):
    if sys.hexversion >= 0x2060000:
        return next((i for i in xrange(len(array)) \
            if match(line, array[i], exact)), None)
    else:
        for i in xrange(len(array)):
            if match(line, array[i], exact):
                return i
        return None

class idlsession(session.session):
    def __init__(self, test, include = [], log = None):
        self._args = [
          '-IDL_PATH', '"+' + ':'.join(include) + '<IDL_DEFAULT>"',
          '-IDL_MORE', 'False', '-quiet'
        ]
        # The input pipe is closed after the initial communicate() call,
        # so we need to queue up everything here.  It's not a very interactive
        # process.
        self._input = [
            'PRINTF, -2, "' + test_start_line + '"',
            # Explicitly compile the file which contains the test procedure.
            # Chances are there are many test procedures in our path but
            # none of them should have test as the filename as well.  In
            # general it is good practice to make the IDL code self compiling,
            # but the test infrastructure is somewhat different.
            '.COMPILE ' + test,
            # Execute the test procedure.  This will generate (or not) stdout
            # and/or stderr output.
            'test',
            'PRINTF, -2, "' + test_end_line + '"',
            # Check heap allocations.  A well written test case should clean
            # up all its allocations, and a well written piece of code (like
            # the ones we are testing) should do so as well.  There should be
            # zero outstanding allocations at the end of the test.
            'PRINTF, -2, "' + mem_start_line + '"',
            'HELP, OUTPUT = idlval_mem_check, /HEAP',
            'PRINTF, -2, idlval_mem_check',
            'PRINTF, -2, "' + mem_end_line + '"',
            'exit']
        exe = 'idl'
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            exe += 'de'
        session.session.__init__(self, executable = exe, log = log)

class idltest(test.test):
    def __init__(self, *args, **kwargs):
        test.test.__init__(self, *args, **kwargs)

        self._expects['memcheck'] = ['Heap Variables:     # Pointer: 0     # Object : 0']
        self._results['memcheck'] = []
        self._expects['halting'] = []
        self._results['halting'] = []

    def _create(self):
        return idlsession(
          test = self._path,
          include = self._include,
          log = self._log)

    def _checksuccess(self):
        # We instrument some special handling for the stderr stream here.
        # Frequently, tests will ignore stderr because it contains system
        # dependent messages and the output is difficult to predict;
        # however, while a straight-up diff is often impractical, we can
        # still parse for some indicators of failure which may not appear
        # in the stdout.

        # Extract any indicators that the test was not, in fact, a test.
        # We do not remove them from stderr in this case since if there was a
        # .err file to compare against, it would surely be interesting to know
        # that the test failed to exist.  However, it will affect our return
        # value; we'll yield None instead of True or False in this case.
        if index(not_a_test_line, self._results['stderr']):
            # If this wasn't a test, short circuit the rest of this as it is
            # unnecessary.
            return None

        # Extract the memory leak check which we instrumented.
        # We remove them from stderr since they are not necessarily errors.
        start = index(mem_start_line, self._results['stderr'])
        end = index(mem_end_line, self._results['stderr'])

        if start != None:
            if end != None:
                self._results['memcheck'] = self._results['stderr'][start + 1:end]
                self._results['stderr'] \
                    = self._results['stderr'][0:start - 1] \
                    + self._results['stderr'][end + 1:]
            else:
                self._results['memcheck'] \
                    = self._results['stderr'][start + 1:] \
                    + ['### Session did not terminate ###']
                self._results['stderr'] \
                    = self._results['stderr'][0:start - 1]
        else:
            self._results['memcheck'] = ['### Session did not terminate ###']

        # Extract the stderr section which is a result of the test itself.
        start = index(test_start_line, self._results['stderr'])
        end = index(test_end_line, self._results['stderr'])
        if start != None:
            if end != None:
                self._results['stderr'] \
                    = self._results['stderr'][0:start - 1] \
                    + self._results['stderr'][start + 1:end - 1] \
                    + self._results['stderr'][end + 1:]
            else:
                self._results['stderr'] \
                    = self._results['stderr'][0:start - 1] \
                    + self._results['stderr'][start + 1:] \
                    + ['### Session did not terminate ###']
        else:
            self._results['stderr'] \
                = self._results['stderr'] \
                + ['### Session did not run ###']
            # Cause the error log to be displayed because there's something
            # wrong here.
            if not 'stderr' in self._expects:
                self._expects['stderr'] = []

        # Extract any indicators that the test halted.
        # We do not remove them from stderr in this case since they are
        # rightfully errors.
        start = index(halting_line, self._results['stderr'], exact = False)
        if start:
            self._results['halting'] = [self._results['stderr'][start]]
            # Cause the error log to be displayed because there's something
            # wrong here.
            if not 'stderr' in self._expects:
                self._expects['stderr'] = []
        else:
            self._results['halting'] = []

        if 'stdout' in self._results:
            if self._results['stdout'] == []:
                # One extra line generated by exiting IDL.
                self._results['stdout'] += ['']
        if 'stdout' in self._expects:
            self._expects['stdout'] += ['']

        # Having now removed anything we wanted to from the stdout and stderr,
        # and also having fabricated any other comparisons we want to make,
        # let the checks begin.
        return test.test._checksuccess(self)
