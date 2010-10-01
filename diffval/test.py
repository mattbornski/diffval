#!/usr/bin/env python

import difflib
import os

def diff(left, right, log = None):
    if log:
        log.openElement('diff')

    diff_output = difflib.unified_diff(left, right)
    diff_output = list(diff_output)
    success = (len(diff_output) == 0)

    if log:
        log.openElement('result', {'success':str(success)})
        log.fillElement('\n'.join(diff_output))
        log.closeElement('result')

        log.closeElement('diff')

    return success

class test:
    def __init__(self, path = '', log = None):
        self._log = log
        self._path = path
        self._session = None
        self._expects = {'stdout':[], 'stderr':[]}
        self._results = {'stdout':[], 'stderr':[]}

        base = (os.path.splitext(self._path))[0]
        if os.path.isfile(base + '.out'):
            self._stdout = base + '.out'
            file = open(self._stdout, 'r')
            self._expects['stdout'] = [line.strip() for line in file.readlines()]
            file.close()
        else:
            self._stdout = None
            del self._expects['stdout']

        if os.path.isfile(base + '.err'):
            self._stderr = base + '.err'
            file = open(self._stderr, 'r')
            self._expects['stderr'] = [line.strip() for line in file.readlines()]
            file.close()
        else:
            self._stderr = None
            del self._expects['stderr']

    def _create(self):
        pass

    def cancel(self):
        if self._session:
            self._session.cancel()

    def timeout(self):
        if self._session:
            self._session.cancel()

    def run(self):
        if self._log:
            self._log.openElement('test', {'file':self._path})

        self._session = self._create()

        if self._session:
            self._results['stdout'] = self._session.output()
            self._results['stderr'] = self._session.errors()
            if self._session._code != 0:
                if not 'stdout' in self._expects:
                    self._expects['stdout'] = []
                if not 'stderr' in self._expects:
                    self._expects['stderr'] = []
                if self._session._code is not None: 
                    self._results['stderr'] \
                      += ['<<< Session exited with code ' \
                        + str(self._session._code) + ' >>>']
                else:
                    self._results['stderr'] \
                      += ['<<< Session canceled by user >>>']

        success = self._checksuccess()

        if self._log:
            self._log.openElement('result', {'success':str(success)})
            self._log.closeElement('result')
            self._log.closeElement('test')

        return success

    def _checksuccess(self):
        ok = True
        for pair in self._expects.keys():
            if not diff(self._expects[pair], self._results[pair],
                        log = self._log):
                ok = False
        return ok
