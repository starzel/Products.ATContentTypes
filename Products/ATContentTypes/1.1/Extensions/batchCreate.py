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

__author__  = 'Christian Heimes <tiran@cheimes.de>'
__docformat__ = 'restructuredtext'

import transaction

DEPTH=10
OBJ_PER_FOLDER=5
id = 'batch_%(type)s_%(no)d'
description = 'batch test'
text = """Lorem ipsum dolor sit amet
==========================

consectetuer adipiscing elit, sed diam
nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit 
lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure 
dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore
eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim 
qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla
facilisi.Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam 
nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. 
Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit
lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure 
dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore
eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim.
"""
content_type = 'text/x-rst'


def batchCreate(self):
    """Creates a bunch of objects for testing purpose
    """
    base = self
    for fno in range(DEPTH):
        fid = id % { 'type' : 'Folder', 'no' : fno }
        base.invokeFactory('Folder', fid)
        folder = getattr(base, fid)
        #folder.edit(description=description, title=fid)
        folder.setDescription(description)
        folder.setTitle(fid)
        for dno in range(OBJ_PER_FOLDER):
            did = id % { 'type' : 'Document', 'no' : dno }
            folder.invokeFactory('Document', did)
            document = getattr(folder, did)
            #document.edit(description=description, title=did, text=text)
            #document.setContentType(content_type)
            document.setTitle(did)
            document.setDescription(description)
            document.edit(text, content_type)
            print fno, dno
        transaction.commit(1)
        print fno
        base = folder