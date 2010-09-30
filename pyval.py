#!/usr/bin/env python

import glob
import os
import shutil
import tempfile

import session
import test

class pysession(session.session):
    def __init__(self, test, log = None):
        # Prep a temporary working directory.
        _pop = os.getcwd()
        src = os.path.dirname(test)
        dst = tempfile.mkdtemp()
        search = os.path.join(src, os.path.splitext(os.path.basename(test))[0])
        for file in glob.glob(search + '*'):
            shutil.copy(
              os.path.join(src, file),
              os.path.join(dst, os.path.basename(file)))
        self._args = [os.path.join(dst, os.path.basename(test))]
        os.chdir(dst)
        self._input = None
        # We need to initialize Python with the correct path.  We'll be
        # running the test itself quite explicitly, but presumably there
        # are things which the test is testing that exist outside of the test.
        # The structure we implicitly require is this:
        # Some path +
        #           |
        #           +-- foo.py
        #           |
        #           +-- bar.py
        #           |
        #           +-- tests +
        #                     |
        #                     +-- no_snafus_please.py
        #                     |
        #                     +-- no_snafus_please.out
        #
        # The key here is that the "tests" directory lives within some larger
        # directory, and it is understood that all tests in this directory are
        # designed to test things in that larger directory, therefore the
        # larger directory will be included in PYTHONPATH.
        path = os.path.abspath(test)
        (path, tail) = os.path.split(path)
        while tail and (tail != 'tests'):
            (path, tail) = os.path.split(path)
        env = os.environ
        env['PYTHONPATH'] = path
        session.session.__init__(self, executable = 'python', log = log)
        shutil.rmtree(dst)
        os.chdir(_pop)

class pytest(test.test):
    def __init__(self, path, log = None):
        test.test.__init__(self, path = path, log = log)

    def _create(self):
        return pysession(test = self._path, log = self._log)

    def _checksuccess(self):
        if 'stdout' in self._results:
            if self._results['stdout'] == []:
                # One extra line generated by exiting Python.
                self._results['stdout'] += ['']
        if 'stdout' in self._expects:
            self._expects['stdout'] += ['']

        return test.test._checksuccess(self)