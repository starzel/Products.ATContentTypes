#  ATContentTypes http://plone.org/products/atcontenttypes/
#  Archetypes reimplementation of the CMF core types
#  Copyright (c) 2003-2006 AT Content Types development team
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

__author__ = 'Leonardo Almeida and Martin Aspeli <optilude@gmx.net>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.ATContentTypes import permission
from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault as ZopeTwoISelectableBrowserDefault
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

tests = []

# XXX: This should probably move to the new CMFDynamicViewFTI
class TestBrowserDefaultMixin(atcttestcase.ATCTSiteTestCase):
    folder_type = 'Folder'
    image_type = 'Image'
    document_type = 'Document'
    file_type = 'File'

    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.folder.invokeFactory(self.folder_type, id='af')
        # an ATCT folder
        self.af = self.folder.af
        # Needed because getFolderContents needs to clone the REQUEST
        self.app.REQUEST.set('PARENTS', [self.app])

    def test_isMixedIn(self):
        self.failUnless(isinstance(self.af, BrowserDefaultMixin),
                        "ISelectableBrowserDefault was not mixed in to ATFolder")
        self.failUnless(ZopeTwoISelectableBrowserDefault.isImplementedBy(self.af),
                        "ISelectableBrowserDefault not implemented by ATFolder instance")
        self.failUnless(ISelectableBrowserDefault.providedBy(self.af),
                        "ISelectableBrowserDefault not implemented by ATFolder instance")

    def test_defaultFolderViews(self):
        self.assertEqual(self.af.getLayout(), 'folder_listing')
        self.assertEqual(self.af.getDefaultPage(), None)
        self.assertEqual(self.af.defaultView(), 'folder_listing')
        self.assertEqual(self.af.getDefaultLayout(), 'folder_listing')
        layoutKeys = [v[0] for v in self.af.getAvailableLayouts()]
        self.failUnless('folder_listing' in layoutKeys)
        self.failUnless('atct_album_view' in layoutKeys)

        resolved = self.af.unrestrictedTraverse('folder_listing')()
        browserDefault = self.af.__browser_default__(None)[1][0]
        browserDefaultResolved = self.af.unrestrictedTraverse(browserDefault)()
        self.assertEqual(resolved, browserDefaultResolved)

    def test_canSetLayout(self):
        self.failUnless(self.af.canSetLayout())
        self.af.invokeFactory('Document', 'ad')
        self.portal.manage_permission(permission.ModifyViewTemplate, [], 0)
        self.failIf(self.af.canSetLayout()) # Not permitted

    def test_setLayout(self):
        self.af.setLayout('atct_album_view')
        self.assertEqual(self.af.getLayout(), 'atct_album_view')
        self.assertEqual(self.af.getDefaultPage(), None)
        self.assertEqual(self.af.defaultView(), 'atct_album_view')
        self.assertEqual(self.af.getDefaultLayout(), 'folder_listing')
        layoutKeys = [v[0] for v in self.af.getAvailableLayouts()]
        self.failUnless('folder_listing' in layoutKeys)
        self.failUnless('atct_album_view' in layoutKeys)

        resolved = self.af.unrestrictedTraverse('atct_album_view')()
        browserDefault = self.af.__browser_default__(None)[1][0]
        browserDefaultResolved = self.af.unrestrictedTraverse(browserDefault)()
        self.assertEqual(resolved, browserDefaultResolved)

    def test_canSetDefaultPage(self):
        self.failUnless(self.af.canSetDefaultPage())
        self.af.invokeFactory('Document', 'ad')
        self.failIf(self.af.ad.canSetDefaultPage()) # Not folderish
        self.portal.manage_permission(permission.ModifyViewTemplate, [], 0)
        self.failIf(self.af.canSetDefaultPage()) # Not permitted

    def test_setDefaultPage(self):
        self.af.invokeFactory('Document', 'ad')
        self.af.setDefaultPage('ad')
        self.assertEqual(self.af.getDefaultPage(), 'ad')
        self.assertEqual(self.af.defaultView(), 'ad')
        self.assertEqual(self.af.__browser_default__(None), (self.af, ['ad',]))

        # still have layout settings
        self.assertEqual(self.af.getLayout(), 'folder_listing')
        self.assertEqual(self.af.getDefaultLayout(), 'folder_listing')
        layoutKeys = [v[0] for v in self.af.getAvailableLayouts()]
        self.failUnless('folder_listing' in layoutKeys)
        self.failUnless('atct_album_view' in layoutKeys)

    def test_setDefaultPageUpdatesCatalog(self):
        # Ensure that Default page changes update the catalog
        cat = self.portal.portal_catalog
        self.af.invokeFactory('Document', 'ad')
        self.af.invokeFactory('Document', 'other')
        self.assertEqual(len(cat(getId=['ad','other'],is_default_page=True)), 0)
        self.af.setDefaultPage('ad')
        self.assertEqual(len(cat(getId='ad',is_default_page=True)), 1)
        self.af.setDefaultPage('other')
        self.assertEqual(len(cat(getId='other',is_default_page=True)), 1)
        self.assertEqual(len(cat(getId='ad',is_default_page=True)), 0)
        self.af.setDefaultPage(None)
        self.assertEqual(len(cat(getId=['ad','other'],is_default_page=True)), 0)
        

    def test_setLayoutUnsetsDefaultPage(self):
        layout = 'atct_album_view'
        self.af.invokeFactory('Document', 'ad')
        self.af.setDefaultPage('ad')
        self.assertEqual(self.af.getDefaultPage(), 'ad')
        self.assertEqual(self.af.defaultView(), 'ad')
        self.af.setLayout(layout)
        self.assertEqual(self.af.getDefaultPage(), None)
        self.assertEqual(self.af.defaultView(), layout)
        resolved = self.af.unrestrictedTraverse(layout)()
        browserDefault = self.af.__browser_default__(None)[1][0]
        browserDefaultResolved = self.af.unrestrictedTraverse(browserDefault)()
        self.assertEqual(resolved, browserDefaultResolved)

    def test_inherit_parent_layout(self):
        # Check to see if subobjects of the same type inherit the layout set
        # on the parent object
        af = self.af
        af.setLayout('folder_tabular_view')
        af.invokeFactory('Folder', 'subfolder', title='folder 2')
        subfolder = af.subfolder
        self.assertEqual(subfolder.getLayout(), 'folder_tabular_view')

    def test_inherit_parent_layout_if_different_type(self):
        # Objects will not inherit the layout if parent object is a different
        # type
        af = self.af
        af.setLayout('folder_tabular_view')
        # Create a subobject of a different type (need to enable LPF globally)
        lpf_fti = self.portal.portal_types['Large Plone Folder']
        lpf_fti.global_allow = 1
        af.invokeFactory('Large Plone Folder', 'subfolder', title='folder 2')
        subfolder = af.subfolder
        self.failIf(subfolder.getLayout() == 'folder_tabular_view')

tests.append(TestBrowserDefaultMixin)

import unittest
def test_suite():
    # framework.py test_suite is trying to run ATCT*TestCase
    # so we have to provide our own
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()