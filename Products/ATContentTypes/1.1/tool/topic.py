from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.criteria import _criterionRegistry
from AccessControl import ClassSecurityInfo
import Persistence
from OFS.SimpleItem import SimpleItem
from ExtensionClass import Base
from Acquisition import aq_base

from Products.CMFCore.permissions import ManagePortal
from Products.ATContentTypes.interfaces import IATCTTopicsTool

from Products.Archetypes.public import DisplayList
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ATContentTypes.config import TOOLNAME

from Products.ATContentTypes.configuration import zconf

tool_config = zconf.atct_tool.topic_tool

# A couple of fields just don't make sense to sort (for a user),
# some are just doubles.
# Is this dangerous for migration?  What if these fields were used in a CMF Topic,
# should the fields themselves be migrated?
IGNORED_FIELDS = ('Date', 'allowedRolesAndUsers', 'id', 'in_reply_to',
    'meta_type',
    # 'portal_type' # portal type and Type might differ!
    )
# Favor ISO dates from DublinCore over actual DateTime
IGNORED_COLUMNS = IGNORED_FIELDS + ('effective', 'expires', 'created', 'modified',
    'getRemoteUrl', 'getIcon')

class TopicIndex(SimpleItem, Persistence.Persistent):

    def __init__(self, index, friendlyName='', description='', enabled=False, criteria=()):
        self.index = index
        self.friendlyName=friendlyName
        self.description = description
        self.enabled=enabled
        self.criteria=tuple(criteria)


class ATTopicsTool(Base):
    """ This tool makes it possible to manage the indexes that are used
        inside topics and allows you to enter a friendly name instead of
        cryptic indexes """

    __implements__ = (IATCTTopicsTool,)

    security       = ClassSecurityInfo()

    # is used in ATPortalTypeCriterion to control which types are allowed to search with
    # until this is fixed in CMF or whatever, this is the way to go.
    allowed_portal_types = []

    id = TOOLNAME
    meta_type= 'ATTopics Tool'
    title = 'ATTopics Tool'
    plone_tool = 1

    def __init__(self):
        self.topic_indexes = {}
        self.topic_metadata = {}
        self.allowed_portal_types = []

    def _initializeTopicTool(self):
        """Helper method to initialize the topic tool
        """
        metadata = getattr(aq_base(self), 'topic_metadata', None)
        #test if metadata is empty or non existant, if so reinit.
        if not metadata:
            self.topic_indexes = {}
            self.topic_metadata = {}
            self.allowed_portal_types = []
            self.createInitialIndexes()
            self.createInitialMetadata()
            for index in tool_config.indexes:
                fn = getattr(index,'friendlyName',None)
                desc = getattr(index,'description',None)
                enabled = getattr(index,'enabled',None)
                criteria = getattr(index,'criteria',None)
                self.updateIndex(index.name, fn, desc, enabled, criteria)
            for meta in tool_config.metadata:
                fn = getattr(meta,'friendlyName',None)
                desc = getattr(meta,'description',None)
                enabled = getattr(meta,'enabled',None)
                self.updateMetadata(meta.name, fn, desc, enabled)
            return True
        else:
            return False

    def getCriteriaForIndex(self, index, as_dict=False):
        """ Returns the valid criteria for a given index """
        catalog_tool = getToolByName(self, CatalogTool.id)
        try:
            indexObj = catalog_tool.Indexes[index]
        except KeyError:
            return ()
        criteria = tuple(_criterionRegistry.criteriaByIndex(indexObj.meta_type))
        search_criteria = _criterionRegistry.listSearchTypes()
        if as_dict:
            criteria = [{'name': a, 'description': _criterionRegistry[a].shortDesc}
                                for a in criteria if a in search_criteria]
        else:
            criteria = [a for a in criteria if a in search_criteria]
        criteria.sort()
        return criteria


    security.declareProtected(ManagePortal,'addIndex')
    def addIndex(self, index, friendlyName='', description='', enabled=False, criteria=None):
        """ Add a new index along with descriptive information to the index
            registry """
        if criteria is None: criteria = self.getCriteriaForIndex(index)
        if self.topic_indexes.has_key(index):
            objIndex = self.topic_indexes[index]
            objIndex.friendlyName=friendlyName
            objIndex.description=description
            objIndex.enabled=enabled
            objIndex.criteria=tuple(criteria)
        else:
            objIndex = TopicIndex(index, friendlyName, description, enabled, criteria)

        self.topic_indexes[index]=objIndex
        self._p_changed=1

    security.declareProtected(ManagePortal,'addMetadata')
    def addMetadata(self, metadata, friendlyName='', description='', enabled=False):
        """ Add a new metadata field along with descriptive information to the
            metadata registry """
        if self.topic_metadata.has_key(metadata):
            objMeta = self.topic_metadata[metadata]
            objMeta.friendlyName=friendlyName
            objMeta.description=description
            objMeta.enabled=enabled
        else:
            objMeta = TopicIndex(metadata, friendlyName, description, enabled)

        self.topic_metadata[metadata]=objMeta
        self._p_changed=1


    security.declareProtected(ManagePortal,'updateIndex')
    def updateIndex(self, index, friendlyName=None, description=None, enabled=None, criteria=None):
        """ Updates an existing index in the registry, unrecognized values are
            added """
        indexes = self.topic_indexes
        if friendlyName == None:
            friendlyName = indexes[index].friendlyName
        if description == None:
            description = indexes[index].description
        if enabled == None:
            enabled = indexes[index].enabled
        if criteria == None:
            criteria = indexes[index].criteria

        self.addIndex(index, friendlyName, description, enabled, criteria)

    security.declareProtected(ManagePortal,'updateMetadata')
    def updateMetadata(self, metadata, friendlyName=None, description=None, enabled=None):
        """ Updates an existing metadata field in the registry, unrecognized values are
            added """
        meta = self.topic_metadata
        if friendlyName == None:
            friendlyName = meta[metadata].friendlyName
        if description == None:
            description = meta[metadata].description
        if enabled == None:
            enabled = meta[metadata].enabled
        self.addMetadata(metadata, friendlyName, description, enabled)


    security.declareProtected(ManagePortal,'removeIndex')
    def removeIndex(self, index):
        """ Removes an existing index from the registry """
        if self.topic_indexes.has_key(index):
            del self.topic_indexes[index]
            self._p_changed=1

    security.declareProtected(ManagePortal,'removeMetadata')
    def removeMetadata(self, metadata):
        """ Removes an existing metadata field from the registry """
        if self.topic_metadata.has_key(metadata):
            del self.topic_metadata[metadata]
            self._p_changed=1


    security.declareProtected(ManagePortal,'createInitialIndexes')
    def createInitialIndexes(self):
        """ create indexes for all indexes in the catalog """
        indexes = self.listCatalogFields()
        for i in indexes:
            if not self.topic_indexes.has_key(i):
                enabled = False
                self.addIndex(i, friendlyName='', enabled=enabled)
        return True

    security.declareProtected(ManagePortal,'createInitialMetadata')
    def createInitialMetadata(self):
        """ create metadata for all indexes in the catalog """
        metas = self.listCatalogMetadata()

        for i in metas:
            if not self.topic_metadata.has_key(i):
                enabled = False
                self.addMetadata(i, friendlyName='', enabled=enabled)
        return True


    security.declareProtected(ManagePortal,'updateIndexesFromCatalog')
    def updateIndexesFromCatalog(self):
        """ check if there are new indexes or if indexes must be removed from
            the collection because they do no longer exist in the catalog """

        indexes = self.listCatalogFields()
        configured_indexes = {}
        for index in tool_config.indexes:
            configured_indexes[index.name]=(getattr(index,'friendlyName',None),
                                            getattr(index,'description',None),
                                            getattr(index,'enabled',None),
                                            getattr(index,'criteria',None))

        # first add new indexes
        for i in indexes:
            if not self.topic_indexes.has_key(i):
                enabled = False
                defaults = (configured_indexes.has_key(i) and
                                        configured_indexes[i]) or ('','',enabled,None)
                self.addIndex(i, friendlyName=defaults[0],
                              description=defaults[1], enabled=defaults[2],
                              criteria=defaults[3])

        # now check the other way round
        keys = self.topic_indexes.keys()
        for k in keys:
            if k not in indexes:
                self.removeIndex(k)

    security.declareProtected(ManagePortal,'updateMetadataFromCatalog')
    def updateMetadataFromCatalog(self):
        """ check if there are new metadata fields or if fields must be
            removed from the collection because they do no longer exist in the
            catalog """

        metas = self.listCatalogMetadata()
        configured_metadata = {}
        for meta in tool_config.metadata:
            configured_metadata[meta.name]=(getattr(meta,'friendlyName',None),
                                            getattr(meta,'description',None),
                                            getattr(meta,'enabled',None))

        # first add new indexes
        for i in metas:
            if not self.topic_metadata.has_key(i):
                enabled = False
                defaults = (configured_metadata.has_key(i) and
                                        configured_metadata[i]) or ('','',enabled)
                self.addMetadata(i, friendlyName=defaults[0],
                                 description=defaults[1], enabled=defaults[2])

        # now check the other way round
        keys = self.topic_metadata.keys()
        for k in keys:
            if k not in metas:
                self.removeMetadata(k)


    security.declarePrivate('listCatalogFields')
    def listCatalogFields(self):
        """ Return a list of fields from portal_catalog. """
        pcatalog = getToolByName( self,  CatalogTool.id )
        available = pcatalog.indexes()
        val = [ field for field in available ]
        val.sort()
        return val

    security.declarePrivate('listCatalogMetadata')
    def listCatalogMetadata(self):
        """ Return a list of columns from portal_catalog. """
        pcatalog = getToolByName( self,  CatalogTool.id )
        available = pcatalog.schema()
        val = [ field for field in available ]
        val.sort()
        return val


    def getAllPortalTypes(self):
        """ returns a list of (id, title)-tuples for each type """
        types_tool = getToolByName(self, 'portal_types')
        types = types_tool.listTypeInfo()

        all_types=[(t.id, t.title or t.id) for t in types]
        return all_types

    def getAllowedPortalTypes(self, populate_for_end_usage=1):
        """ Return all portal_types as an (id,title) tuple that are allowed
            to search with """
        all_types = self.getAllPortalTypes()

        if populate_for_end_usage==0:
            # return whatever is in self.allowed_portal_types and make it a (id, title) tuple
            return [t for t in all_types if t[0] in self.allowed_portal_types]

        if self.allowed_portal_types==[]:
            filtered_types = all_types
        else:
            filtered_types = [type for type in all_types if type[0] in self.allowed_portal_types]

        return filtered_types


    def getEnabledIndexes(self):
        """ Returns all TopicIndex objects for enabled indexes """
        # first resync with the catalog
        self.updateIndexesFromCatalog()

        indexes = self.topic_indexes
        results = [i for i in indexes.values() if i.enabled]

        return results

    def getEnabledMetadata(self):
        """ Returns all TopicIndex objects for enabled metadata """
        # first resync with the catalog
        self.updateMetadataFromCatalog()

        meta = self.topic_metadata
        results = [i for i in meta.values() if i.enabled]

        return results


    def getIndexDisplay(self, enabled=True):
        """ Return DisplayList of Indexes and their friendly names """
        if enabled:
            index_names = self.getIndexes(True)
        else:
            index_names = self.getIndexes()
        index_dict = self.topic_indexes
        indexes = [index_dict[i] for i in index_names]

        field_list=[(f.index, f.friendlyName or f.index) for f in indexes]

        return DisplayList(field_list)

    def getMetadataDisplay(self, enabled=True):
        """ Return DisplayList of Metadata and their friendly names """
        if enabled:
            meta_names = self.getAllMetadata(True)
        else:
            meta_names = self.getAllMetadata()
        meta_dict = self.topic_metadata
        meta = [meta_dict[i] for i in meta_names]

        field_list=[(f.index, f.friendlyName or f.index) for f in meta]

        return DisplayList(field_list)


    def getEnabledFields(self):
        """ Returns a list of tuples containing the index name, friendly name,
            and description for each enabled index. """
        enabledIndexes = self.getEnabledIndexes()

        dec_fields = [(i.friendlyName.lower() or i.index.lower(), i.index, i.friendlyName or i.index, i.description) for i in enabledIndexes]

        dec_fields.sort()

        fields = [(a[1],a[2],a[3]) for a in dec_fields]

        return fields


    def getFriendlyName(self, index):
        """ Returns the friendly name for a given index name, or the given
            index if the firendlyname is empty or the index is not recognized
        """
        if self.topic_indexes.has_key(index):
            return self.getIndex(index).friendlyName or index
        else:
            return index


    security.declareProtected(ManagePortal,'getIndexes')
    def getIndexes(self, enabledOnly=False):
        """ Returns the full list of available indexes, optionally filtering
            out those that are not marked enabled """
        # first resync with the catalog
        if  enabledOnly:
            indexes_dec = [(i.index.lower(), i.index) for i in self.getEnabledIndexes()]
        else:
            self.updateIndexesFromCatalog()
            indexes_dec = [(i.lower(), i) for i in self.topic_indexes.keys()]

        indexes_dec.sort()
        indexes = [i[1] for i in indexes_dec]
        return indexes

    security.declareProtected(ManagePortal,'getAllMetadata')
    def getAllMetadata(self, enabledOnly=False):
        """ Returns the full list of available metadata fields, optionally
            filtering out those that are not marked enabled """
        # first resync with the catalog
        self.updateMetadataFromCatalog()
        if enabledOnly:
            meta_dec = [(i.index.lower(), i.index) for i in self.getEnabledMetadata()]
        else:
            meta_dec = [(i.lower(), i) for i in self.topic_metadata.keys()]

        meta_dec.sort()
        metadata = [i[1] for i in meta_dec]
        return metadata


    def getIndex(self, index):
        """ Returns the TopicIndex object for a given index name """
        self.updateIndexesFromCatalog()
        if self.topic_indexes.has_key(index):
            return self.topic_indexes[index]
        else:
            raise AttributeError('Index ' + str(index) + ' not found')

    def getMetadata(self, metadata):
        """ Returns the TopicIndex object for a given metadata name """
        self.updateMetadataFromCatalog()
        if self.topic_metadata.has_key(metadata):
            return self.topic_metadata[metadata]
        else:
            raise AttributeError('Metadata ' + str(metadata) + ' not found')


    security.declareProtected(ManagePortal,'manage_saveTopicSetup')
    def manage_saveTopicSetup(self, REQUEST=None):
        """ Set indexes and metadata from form """
        if REQUEST==None:
            return  'Nothing saved.'

        data = REQUEST.get('index', [])
        for index in data:
            enabled = index.has_key('enabled')
            criteria = index.get('criteria', ())
            self.updateIndex(index['index'], index['friendlyName'], index['description'], enabled, criteria)

        meta = REQUEST.get('metadata', [])
        for metadata in meta:
            enabled = metadata.has_key('enabled')
            self.updateMetadata(metadata['index'], metadata['friendlyName'], metadata['description'], enabled)

        return 1

    security.declareProtected(ManagePortal,'manage_saveTopicSetupTypes')
    def manage_saveTopicSetupTypes(self, REQUEST=None):
        """ Set portal types from form """
        if REQUEST==None:
            return  'Nothing saved.'

        self.allowed_portal_types = REQUEST.get('allowed_types', [])

        return 1

InitializeClass(ATTopicsTool)
