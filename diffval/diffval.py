#!/usr/bin/env python

import optparse
import os
import sys

import idlval
import pyval

import log

def index(path, log = None, types = {'py':'python', 'pro':'idl'}, \
        verified = False):

    items = []
    if not verified:
        # Determine if the path already falls within a "tests" directory,
        # in which case we should index everything, or whether we are
        # looking for a "tests" directory.
        (head, tail) = os.path.split(path)
        while tail and (tail != 'tests'):
            (head, tail) = os.path.split(head)
        if tail == 'tests':
            verified = True

    if os.path.isdir(path):
        for child in os.listdir(path):
            items += index(path = os.path.join(path, child), \
                        log = log, types = types, verified = verified)
    elif verified:
        ext = ((os.path.splitext(path))[1])[1:]
        if ext in types:
            if log:
                log.openElement('file', {'type':types[ext], 'path':path})
            items += [path]
            if log:
                log.closeElement('file')

    return items

def validate(paths, file = sys.stdout, mailto = None):
    logger = log.log(file = file)

    logger.openElement('index')
    candidates = [os.path.abspath(path) for path in paths]
    paths = []
    for candidate in candidates:
        paths += index(path = candidate, log = logger)
    logger.openElement('result', {'success':str(len(paths) > 0)})
    logger.closeElement('result')
    logger.closeElement('index')

    logger.openElement('execute')
    succeeded = 0
    tests = len(paths)
    for path in paths:
        result = None
        ext = (os.path.splitext(path))[1]
        if ext == '.pro':
            result = idlval.idltest(path, log = logger).run()
        elif ext == '.py':
            result = pyval.pytest(path, log = logger).run()

        if result == True:
            succeeded += 1
        elif result == None:
            # Upon further inspection this did not appear to be a test.
            tests -= 1
    logger.openElement('result', {'success':str(succeeded == tests), \
        'tests':str(tests), 'failures':str(tests - succeeded)})
    logger.closeElement('result')
    logger.closeElement('execute')

    if mailto:
        import smtplib
        mailfrom = 'noreply@ssl.berkeley.edu'
        message = 'From: ' + mailfrom + '\r\n'
        message += 'To: ' + mailto + '\r\n'
        message += 'Subject: ' + 'Validation ' + str(tests - succeeded) + '/' + str(tests)+ '\r\n'
        server = smtplib.SMTP('mail.ssl.berkeley.edu')
        server.sendmail(mailfrom, mailto, message)
        server.quit()

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-t', '--mailto', dest='mailto',
        help='Send report to MAILTO', metavar = 'MAILTO',
        default=None)
    parser.add_option('-l', '--log', dest='logfile',
        help='Log results to FILE', metavar='FILE',
        default=sys.stdout)
    (options, args) = parser.parse_args()
    validate(paths = args, mailto = options.mailto, file = options.logfile)
