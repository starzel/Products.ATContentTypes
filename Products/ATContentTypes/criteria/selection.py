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
""" Topic:

"""

__author__  = 'Alec Mitchell'
__docformat__ = 'restructuredtext'
__old_name__ = 'Products.ATContentTypes.types.criteria.ATSelectionCriterion'

from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import DisplayList

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.criteria import LIST_INDICES
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

from types import StringType

CompareOperators = DisplayList((
                    ('and', 'and')
                  , ('or', 'or')
    ))

ATSelectionCriterionSchema = ATBaseCriterionSchema + Schema((
    LinesField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default=[],
                vocabulary="getCurrentValues",
                widget=MultiSelectionWidget(
                    label="Value",
                    label_msgid="label_selection_criteria_value",
                    description="Existing values.",
                    description_msgid="help_selection_criteria_value",
                    i18n_domain="plone"),
                ),
    StringField('operator',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                default='or',
                vocabulary=CompareOperators,
                widget=SelectionWidget(
                    label="operator name",
                    label_msgid="label_list_criteria_operator",
                    description="Operator used to join the tests "
                    "on each value.",
                    description_msgid="help_list_criteria_operator",
                    i18n_domain="atcontenttypes"),
                ),
    ))

class ATSelectionCriterion(ATBaseCriterion):
    """A selection criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATSelectionCriterionSchema
    meta_type      = 'ATSelectionCriterion'
    archetype_name = 'Selection Criterion'
    typeDescription= ''
    typeDescMsgId  = ''

    shortDesc      = 'Select values from list'


    def getCurrentValues(self):
        catalog = getToolByName(self, 'portal_catalog')
        options = catalog.uniqueValuesFor(self.Field())
        # AT is currently broken, and does not accept ints as
        # DisplayList keys though it is supposed to (it should
        # probably accept Booleans as well) so we only accept strings
        # for now
        options = [(o.lower(),o) for o in options if type(o) is StringType]
        options.sort()
        return [o[1] for o in options]

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        # filter out empty strings
        result = []

        value = tuple([ value for value in self.Value() if value ])
        if not value:
            return ()
        result.append((self.Field(), { 'query': value, 'operator': self.getOperator()}),)

        return tuple(result)

registerCriterion(ATSelectionCriterion, LIST_INDICES)
