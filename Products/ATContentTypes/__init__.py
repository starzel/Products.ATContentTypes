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
"""ATContentTypes
"""
__author__  = 'Christian Heimes <ch@comlounge.net>'
__docformat__ = 'restructuredtext'

import os.path
import sys

from zLOG import LOG, INFO

LOG('ATContentTypes',INFO, 'Installing Product')

ATCT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(3, os.path.join(ATCT_DIR, 'thirdparty'))

__version__ = open(os.path.join(__path__[0], 'version.txt')).read().strip()

from Products.ATContentTypes.config import HAS_LINGUA_PLONE
from Products.ATContentTypes.config import SKINS_DIR
from Products.ATContentTypes.config import PROJECTNAME
from Products.ATContentTypes.config import GLOBALS

if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import process_types
    from Products.LinguaPlone.public import listTypes
else:
    from Products.Archetypes.public import process_types
    from Products.Archetypes.public import listTypes

from Products.CMFCore.utils import ContentInit
from Products.CMFCore.utils import ToolInit
from Products.CMFCore.DirectoryView import registerDirectory

# first level imports: configuration and validation
import Products.ATContentTypes.configuration
import Products.ATContentTypes.lib.validators

# second leven imports: content types, criteria
# the content types are depending on the validators and configuration
import Products.ATContentTypes.content
import Products.ATContentTypes.criteria

# misc imports 
import Products.ATContentTypes.Extensions.Install
from Products.ATContentTypes import migration
from Products.ATContentTypes.tool.atct import ATCTTool

# wire the add permission after all types are registered
from Products.ATContentTypes.permission import wireAddPermissions
wireAddPermissions()

# setup module aliases for old dotted pathes
import Products.ATContentTypes.modulealiases

registerDirectory(SKINS_DIR,GLOBALS)

def initialize(context):
    # Setup migrations
    migration.executeMigrations()
    migration.registerMigrations()
    
    # process our custom types
    
    ToolInit(
        'ATContentTypes tools', 
        tools=(ATCTTool,),
        icon='tool.gif', ).initialize(context) 

    listOfTypes = listTypes(PROJECTNAME)

    content_types, constructors, ftis = process_types(
        listOfTypes,
        PROJECTNAME)

    # Assign an own permission to all content types
    # Heavily based on Bricolite's code from Ben Saller
    from Products.ATContentTypes.permission import permissions
    
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

