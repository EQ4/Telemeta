# -*- coding: utf-8 -*-
# Copyright (C) 2007 Samalyse SARL

# This software is a computer program whose purpose is to backup, analyse,
# transcode and stream any audio content with its metadata over a web frontend.

# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
#
# Author: Olivier Guilyardi <olivier@samalyse.com>

from telemeta.models.core import Duration
from telemeta.models.media import MediaItem, MediaCollection
from django.conf import settings

class Resource(object):
    "Represent a Dublin Core resource"

    def __init__(self, *args):
        self.elements = []
        self.add(*args)

    def flatten(self):
        """Convert the resource to a dictionary with element names as keys.

        Warnings: 
        - refinements are lost during this conversion,
        - if there are several occurences of the same element, only the first is 
        used, others are lost.
        - all values are converted to strings
        """
        result = {}
        for element in self.elements:
            if not result.has_key(element.name):
                result[element.name] = unicode(element.value)
        return result

    def to_list(self):
        """Convert the resource to unqualified dublin core, as a list of the form:
           [(key, value), ...]"""
        result = []
        for element in self.elements:
            result.append((element.name, unicode(element.value)))
        return result

    def add(self, *elements):
        for e in elements:
            if isinstance(e, Element):
                if not e in self.elements:
                    self.elements.append(e)
            else:
                try:
                    iter(e)
                except TypeError: 
                    raise Exception("add() only accepts elements or sequences of elements")

                self.add(*e)

    def __unicode__(self):
        dump = u''
        for e in self.elements:
            key = unicode(e.name)
            if e.refinement:
                key += u'.' + unicode(e.refinement)
            dump += u'%s:\t%s\n' % (key, unicode(e.value))
        return dump            
            

class Element(object):
    "Represent a Dublin Core element"

    def __init__(self, name, value=None, refinement=None, related=None):
        self.name = name
        self.value = value
        self.refinement = refinement
        self.related = related

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value and self.refinement == self.refinement

    def __ne__(self, other):
        return not (self == other)

    @staticmethod
    def multiple(name, values, refinement=None):
        elements = []
        if values:
            for v in values:
                elements.append(Element(name, v, refinement))
        return elements

class Date(Element):
    "Dublin Core date element formatted according to W3C-DTF or DCMI Period"

    def __init__(self, start, end=None, refinement=None):
        value = ''
        if start:
            value = str(start) 
            if end and start != end:
                value = 'start=' + value + '; end=' + unicode(end) + ';'
        super(Date, self).__init__('date', value, refinement)            

def media_access_rights(media):
    if media.public_access == 'full':
        return 'public'
    if media.public_access == 'metadata':
        return 'restricted'
    return 'private'

def media_identifier(media):
    if media.code:
        return media.element_type + ':' + media.code
    elif media.old_code:
        return media.element_type + ':' + media.old_code
    return None

def express_collection(collection):
    "Express a collection as a Dublin Core resource"

    if collection.collector:
        creator = (Element('creator', collection.collector), 
                   Element('contributor', collection.creator))
    else:                        
        creator = Element('creator', collection.creator)

    duration = max(collection.approx_duration, collection.computed_duration())
    parts = []
    for item in collection.items.all():
        id = media_identifier(item)
        if id:
            parts.append(Element('relation', id, 'hasPart', item))

    resource = Resource(
        Element('identifier',       media_identifier(collection), related=collection),
        Element('type',             'Collection'),
        Element('title',            collection.title),
        Element('title',            collection.alt_title),
        creator,
        Element('contributor',      collection.metadata_author),
        Element.multiple('subject', settings.TELEMETA_SUBJECTS),
        Element('publisher',        collection.publisher),
        Element('publisher',        settings.TELEMETA_ORGANIZATION),
        Date(collection.recorded_from_year, collection.recorded_to_year, 'created'),
        Date(collection.year_published, refinement='issued'),
        Element('rights',           collection.legal_rights, 'license'),
        Element('rights',           media_access_rights(collection), 'accessRights'),
        Element('format',           duration, 'extent'),
        Element('format',           collection.physical_format, 'medium'),
        #FIXME: audio mime types are missing,
        parts
    )

    return resource

def express_item(item):
    "Express a media item as a Dublin Core resource"

    if item.collector:
        creator = (Element('creator', item.collector),
                   Element('contributor', item.collection.creator))
    elif item.collection.collector:                   
        creator = (Element('creator', item.collection.collector),
                   Element('contributor', item.collection.creator))
    else:
        creator = Element('creator', item.collection.creator)
       
    if item.recorded_from_date:
        date = Date(item.recorded_from_date, item.recorded_to_date, 'created')
    else:
        date = Date(item.collection.recorded_from_year, item.collection.recorded_to_year, 'created'),
        
    if item.title:
        title = item.title
    else:
        title = item.collection.title
        if item.track:
            title += u' - ' + item.track

    resource = Resource(
        Element('identifier',       media_identifier(item), related=item),
        Element('type',             'Sound'),
        Element('title',            title),
        Element('title',            item.alt_title),
        creator,
        Element('contributor',      item.collection.metadata_author),
        Element.multiple('subject', settings.TELEMETA_SUBJECTS),
        Element.multiple('subject', item.keywords()),
        Element('description',      item.context_comment, 'abstract'),
        Element('publisher',        item.collection.publisher),
        Element('publisher',        settings.TELEMETA_ORGANIZATION),
        date,
        Date(item.collection.year_published, refinement='issued'),
        Element.multiple('coverage', item.location and item.location.fullnames(), 'spatial'),
        Element('coverage',         item.location_comment, 'spatial'),
        Element('rights',           item.collection.legal_rights, 'license'),
        Element('rights',           media_access_rights(item.collection), 'accessRights'),
    
        Element('format',           max(item.approx_duration, item.computed_duration()), 'extent'),
        Element('format',           item.collection.physical_format, 'medium'),
        #FIXME: audio mime types are missing,
        Element('relation',         media_identifier(item.collection), 'isPartOf', item.collection)
    )

    return resource
    
def express_resource(res):
    if isinstance(res, MediaItem):
        return express_item(res)
    elif isinstance(res, MediaCollection):
        return express_collection(res)

    raise Exception("Invalid resource type")        

def lookup_resource(media_id):
    try:
        type, code = media_id.split(':', 1)
    except ValueError:
        raise MalformedMediaIdentifier("Media identifier must be in type:code format")
    
    if (type == 'collection'):
        try:
            return MediaCollection.objects.get(code=code)
        except MediaCollection.DoesNotExist:
            return None
    elif (type == 'item'):
        try:
            return MediaItem.objects.get(code=code)
        except MediaItem.DoesNotExist:
            try:
                return MediaItem.objects.get(old_code=code)
            except MediaItem.DoesNotExist:
                return None
    else:
        raise MalformedMediaIdentifier("No such type in media identifier: " + type)
   
class MalformedMediaIdentifier(Exception):
    pass