#!/usr/bin/env python

import datetime
import sys
import xml.sax.saxutils
import xml.sax.xmlreader

class log:
    def __init__(self, file = sys.stdout):
        self._stack = []
        if isinstance(file, str):
            self._file = open(file, 'w')
        else:
            self._file = file
        self._hightide = 0
        self._logger = xml.sax.saxutils.XMLGenerator(self._file, 'utf-8')
        self._logger.startDocument()
        self.openElement('log', {'program':sys.argv[0]}, pretty = False)
    def __del__(self):
        self.closeElement('log')
        self._logger.endDocument()
        #if self._file.isatty():
        self._file.write('\n')
        self._file.close()
    def _createAttributes(self, dict):
        vals = {}
        qnames = {}
        for attr in dict.keys():
            vals[(None, attr)] = dict[attr]
            qnames[(None, attr)] = attr
        return xml.sax.xmlreader.AttributesNSImpl(vals, qnames)
    def openElement(self, tag, attributes = {}, pretty = True):
        attributes['time'] = datetime.datetime.utcnow().isoformat()
        if pretty:
            self._file.write('\n')
            indent = len(self._stack) * 2
            if indent:
                self._file.write(' '.rjust(indent))
        self._stack = [tag] + self._stack
        self._hightide = len(self._stack)
        self._logger.startElementNS((None, tag), tag,
            self._createAttributes(dict = attributes))
        self._file.flush()
    def fillElement(self, text = None):
        if text:
            self._logger.characters(text)
            self._file.flush()
    def closeElement(self, tag = None, pretty = True):
        if pretty and (self._hightide > len(self._stack)):
            self._file.write('\n')
            indent = (len(self._stack) - 1) * 2
            if indent:
                self._file.write(' '.rjust(indent))
        last = self._stack[0]
        self._stack = self._stack[1:]
        if not tag:
            tag = last
        elif tag != last:
            print 'attempting to end element ' + tag + ' but ' \
                + last + ' should be next'
            raise Exception('MalformedOutput')
        self._logger.endElementNS((None, tag), tag)
        self._file.flush()

if __name__ == '__main__':
    logger = log()
    logger.openElement('foo')
    logger.openElement('bar')
    logger.closeElement()
    logger.closeElement('foo')
