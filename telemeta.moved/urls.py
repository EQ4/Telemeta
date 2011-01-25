# -*- coding: utf-8 -*-
# Copyright (C) 2007 Samalyse SARL
#
# Copyright (c) 2007-2009 Guillaume Pellerin <yomguy@parisson.com>

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

from django.conf.urls.defaults import *
from telemeta.models import MediaItem, MediaCollection
from telemeta.web.base import WebView
import os.path
import telemeta.config

telemeta.config.check()

# initialization
web_view = WebView()

# query sets for Django generic views
all_items = { 'queryset': MediaItem.objects.enriched(), }
all_collections = { 'queryset': MediaCollection.objects.enriched(), }

# ID's regular expressions
export_extensions = "|".join(web_view.list_export_extensions())

htdocs = os.path.dirname(__file__) + '/htdocs'

urlpatterns = patterns('',
    url(r'^$', web_view.index, name="telemeta-home"),

    # items
    url(r'^items/$', 'django.views.generic.list_detail.object_list', 
        dict(all_items, paginate_by=20, template_name="telemeta/mediaitem_list.html"),
        name="telemeta-items"),
    url(r'^items/(?P<public_id>[A-Z0-9_]+)/$', web_view.item_detail, 
        name="telemeta-item-detail"),
    url(r'^items/(?P<public_id>[A-Z0-9_]+)/dc/$', web_view.item_detail, 
        {'template': 'telemeta/mediaitem_detail_dc.html'},
        name="telemeta-item-dublincore"),
    url(r'^items/(?P<public_id>[A-Z0-9_]+)/dc/xml/$', web_view.item_detail, 
        {'format': 'dublin_core_xml'},
        name="telemeta-item-dublincore-xml"),
    url(r'^items/download/(?P<public_id>[A-Z0-9_]+)\.(?P<extension>' 
            + export_extensions + ')$', 
        web_view.item_export,
        name="telemeta-item-export"),
    url(r'^items/(?P<public_id>[A-Z0-9_]+)/visualize/(?P<visualizer_id>[0-9a-z_]+)/(?P<width>[0-9A-Z]+)x(?P<height>[0-9A-Z]+)/$', 
        web_view.item_visualize,
        name="telemeta-item-visualize"),
    url(r'^items/(?P<public_id>[A-Z0-9_]+)/analyze/(?P<analyzer_id>[0-9a-z_]+)/$', 
        web_view.item_analyze,
        name="telemeta-item-analyze"),
    url(r'^items/(?P<public_id>[A-Z0-9_]+)/item_xspf.xml$', 
        web_view.item_playlist, 
        dict(template="telemeta/mediaitem_xspf.xml", mimetype="application/xspf+xml"),
        name="telemeta-item-xspf"),

    # collections
    url(r'^collections/$', 'django.views.generic.list_detail.object_list',
        dict(all_collections, paginate_by=20, 
            template_name="telemeta/collection_list.html"),
        name="telemeta-collections"),
    url(r'^collections/?page=(?P<page>[0-9]+)$', 
        'django.views.generic.list_detail.object_list',
        dict(all_collections, paginate_by=20)),
    url(r'^collections/(?P<public_id>[A-Z0-9_]+)/$', web_view.collection_detail,
        dict(template="telemeta/collection_detail.html"), name="telemeta-collection-detail"),
    url(r'^collections/(?P<public_id>[A-Z0-9_]+)/dc/$', web_view.collection_detail,
        dict(template="telemeta/collection_detail_dc.html"), name="telemeta-collection-dublincore"),
    url(r'^collections/(?P<public_id>[A-Z0-9_]+)/collection_xspf.xml$', 
        web_view.collection_playlist, 
        dict(template="telemeta/collection_xspf.xml", mimetype="application/xspf+xml"),
        name="telemeta-collection-xspf"),
    url(r'^collections/(?P<public_id>[A-Z0-9_]+)/collection.m3u$',
        web_view.collection_playlist, 
        dict(template="telemeta/collection.m3u", mimetype="audio/mpegurl"),
        name="telemeta-collection-m3u"),

    # search
    url(r'^search/$', web_view.search, name="telemeta-search"),
    url(r'^search/collections/$', web_view.search, {'type': 'collections'}, 
        name="telemeta-search-collections"),
    url(r'^search/items/$', web_view.search, {'type': 'items'}, 
        name="telemeta-search-items"),
    url(r'^search/criteria/$', web_view.edit_search, name="telemeta-search-criteria"),
    url(r'^complete_location/$', web_view.complete_location, name="telemeta-complete-location"),

    # administration        
    url(r'^admin/$', web_view.admin_index, name="telemeta-admin"),        

    # enumerations administration
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/$', 
        web_view.edit_enumeration ,
        name="telemeta-enumeration-edit"),        
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/add/$', 
        web_view.add_to_enumeration,
        name="telemeta-enumeration-add"),        
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/update/$', 
        web_view.update_enumeration,
        name="telemeta-enumeration-update"),        
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/'
        + r'(?P<value_id>[0-9]+)/$',
        web_view.edit_enumeration_value,
        name="telemeta-enumeration-record-edit"),   
    url(r'^admin/enumerations/(?P<enumeration_id>[0-9a-z]+)/'
        + r'(?P<value_id>[0-9]+)/update/$',
        web_view.update_enumeration_value, 
        name="telemeta-enumeration-record-update"),   

    # Geographic browsing
    url(r'^geo/$', web_view.list_continents, name="telemeta-geo-continents"),
    url(r'^geo/(?P<continent>[a-z_]+)/$', web_view.list_countries, 
        name="telemeta-geo-countries"),
    url(r'^geo/collections/(?P<continent>[a-z_]+)/(?P<country>[a-z_]+)/$', 
        web_view.list_country_collections, 
        name="telemeta-geo-country-collections"),
    url(r'^geo/items/(?P<continent>[a-z_]+)/(?P<country>[a-z_]+)/$', 
        web_view.list_country_items, 
        name="telemeta-geo-country-items"),
    url(r'^geo/country_info/(?P<id>[0-9A-Z]+)/$', 
        web_view.country_info, name="telemeta-country-info"),

    # CSS+Images (FIXME: for developement only)
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/css'},
        name="telemeta-css"),
    url(r'^images/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/images'},
        name="telemeta-images"),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/js'},
        name="telemeta-js"),
    url(r'^swf/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/swf'},
        name="telemeta-swf"),
    url(r'^timeside/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': htdocs+'/timeside'},
        name="telemeta-timeside"),

    # Flat pages
    url(r'^page/(?P<path>.*)$', web_view.render_flatpage, name="telemeta-flatpage"),

    # OAI-PMH Data Provider
    url(r'^oai/.*$', web_view.handle_oai_request, name="telemeta-oai"),

    # Authentication
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'telemeta/login.html'},
        name="telemeta-login"),
    url(r'^logout/$', web_view.logout, name="telemeta-logout"),
)