#  ATContentTypes http://sf.net/projects/collective/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2005 AT Content Types development team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
"""

__author__ = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase
from Acquisition import aq_base

from Products.Archetypes.public import *

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.interfaces import IATFolder
from Products.Five.traversable import FakeRequest
from Products.ATContentTypes.tests.utils import FakeRequestSession

from Products.ATContentTypes.interface.image import IPhotoAlbum
from Products.ATContentTypes.interface.image import IPhotoAlbumAble
from Products.ATContentTypes.interface.archive import IArchiver
from Products.ATContentTypes.interface.archive import IArchivable
from Products.ATContentTypes.interface.archive import IDataExtractor
from Products.ATContentTypes.adapters.document import DocumentDataExtractor
from Products.ATContentTypes.adapters.document import DocumentRawDataExtractor
from Products.ATContentTypes.interface.archive import IArchiveAccumulator
from Products.ATContentTypes.adapters.archive import ZipAccumulator

from Products.ATContentTypes.adapters.image import PhotoAlbum
from Products.ATContentTypes.adapters.archive import FolderishArchiver

from Products.ATContentTypes.browser.archive import ArchiveView

from zope.interface.verify import verifyClass
from zipfile import ZipFile
from cStringIO import StringIO

tests = []

class TestAccumulator(atcttestcase.ATCTSiteTestCase):

    def test_adapter(self):
        verifyClass(IArchiveAccumulator, ZipAccumulator)

tests.append(TestAccumulator)

class TestDataExtractors(atcttestcase.ATCTSiteTestCase):
    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.folder.invokeFactory('Document', 'd1', title='doc 1')
        self.docobj = self.folder.d1

    def test_adapter(self):
        IDataExtractor.implementedBy(DocumentDataExtractor)
        IDataExtractor.implementedBy(DocumentRawDataExtractor)

tests.append(TestDataExtractors)


class TestSitePhotoAlbumSupport(atcttestcase.ATCTSiteTestCase):
    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.folder.invokeFactory('Folder', 'fobj', title='folder 1')
        self.fobj = self.folder.fobj

    def test_implements(self):
        self.failUnless(IPhotoAlbumAble.providedBy(self.fobj))

    def test_adapter(self):
        verifyClass(IPhotoAlbum,PhotoAlbum)

    def test_SymbolicPhoto(self):
        adapted = IPhotoAlbum(self.fobj)

tests.append(TestSitePhotoAlbumSupport)

class TestFolderishArchiver(atcttestcase.ATCTSiteTestCase):
    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.folder.invokeFactory('Folder', 'fobj', title='folder 1')
        self.fobj = self.folder.fobj
        self.fobj.invokeFactory('Document','doc1',title='document 1')
        self.fobj.doc1.setText("A nice text")

    def test_implements(self):
        archiver = IArchiver(self.fobj)
        self.failUnless(IArchiver.providedBy(archiver))

    def test_adapter(self):
        verifyClass(IArchiver,FolderishArchiver)

tests.append(TestFolderishArchiver)


if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite
