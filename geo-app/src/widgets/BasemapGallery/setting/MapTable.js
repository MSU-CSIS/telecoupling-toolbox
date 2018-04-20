/*
// Copyright © 2014 - 2017 Esri. All rights reserved.

TRADE SECRETS: ESRI PROPRIETARY AND CONFIDENTIAL
Unpublished material - all rights reserved under the
Copyright Laws of the United States and applicable international
laws, treaties, and conventions.

For additional information, contact:
Attn: Contracts and Legal Department
Environmental Systems Research Institute, Inc.
380 New York Street
Redlands, California, 92373
USA

email: contracts@esri.com
*/

define([
  'dojo/_base/declare',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'dojo/text!./MapTable.html',
  'dojo/Evented',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/_base/html',
  'dojo/Deferred',
  'dojo/promise/all',
  'dojo/query',
  'dojo/on',
  'esri/request',
  'jimu/utils',
  'jimu/portalUtils',
  'jimu/portalUrlUtils',
  'jimu/dijit/LoadingIndicator',
  '../BasemapItem',
  '../utils'
], function(declare, _WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin,
  template, Evented, lang, array, html, Deferred, all, query, on, esriRequest, jimuUtils,
  portalUtils, portalUrlUtils, LoadingIndicator, BasemapItem, utils) {
  /* jshint unused: false */
  return declare([_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin, Evented], {
    templateString: template,
    baseClass: "basemap-table",
    query:null, //{q,sortField,sortOrder}
    portalUrl:null,
    nls:null,
    type: '',//Web Map or Web Scene
    multiple: false,
    map: null,
    spatialReference: null,
    basemaps: [],

    //events:
    //select return {mapTable, selectedNode}

    //public methods:
    //getSelectedMapItem

    postMixInProperties: function(){
      this.nls = lang.mixin(this.nls, window.jimuNls.itemSelector);
    },

    postCreate: function() {
      this.inherited(arguments);
      this.basemaps = [];
      if(this.portalUrl){
        this.portalUrl = portalUrlUtils.getStandardPortalUrl(this.portalUrl);
      }
      this.search();
    },

    //{q,sortField,sortOrder}
    search:function(newQuery){
      if(newQuery){
        this.query = lang.clone(newQuery);
        this.clear();
      }
      if(!this.portalUrl || !this.query){
        return;
      }

      var portal = portalUtils.getPortal(this.portalUrl);
      this.allMapsShelter.show();
      html.addClass(this.searchNoneTipSection, 'hidden');
      portal.queryItems(this.query).then(lang.hitch(this, function(response) {
        this._createMapItems(response).then(lang.hitch(this, function() {
          this.allMapsShelter.hide();
          this._filterMapCallback();
        }));
      }), lang.hitch(this, function(err) {
        console.error(err);
        if(!this.domNode){
          return;
        }
        this.allMapsShelter.hide();
        this._filterMapCallback();
      }));
    },

    _filterMapCallback: function(){
      if(this.basemaps.length > 0){
        html.removeClass(this.allMapsTableDiv, 'hidden');
        html.addClass(this.searchNoneTipSection, 'hidden');
      }else{
        html.addClass(this.allMapsTableDiv, 'hidden');
        html.removeClass(this.searchNoneTipSection, 'hidden');
      }
    },

    clear:function(){
      this.basemaps = [];
      html.empty(this.allMapsTable);
    },

    _createMapItems: function(response) {
      var _basemapAll = [], _requestAll = [], retDef = new Deferred();
      var results = response.results;
      var webMaps = array.filter(results, lang.hitch(this, function(item) {
        return item.type.toLowerCase() === this.type.toLowerCase();
      }));
      var countPerRow = 5;
      if (webMaps.length === 0) {
        retDef.resolve();
        return retDef;
      }
      array.forEach(webMaps, function(webmap) {
        _basemapAll.push(utils.getBasemapInfo(webmap.portalUrl, webmap.id));
      });

      all(_basemapAll).then(lang.hitch(this, function(basemapInfos) {
        array.forEach(basemapInfos, lang.hitch(this, function(basemap) {
          var def = new Deferred();
          utils.isBasemapCompatibleWithMap(basemap.spatialReference,
            basemap.layers, this.map).then(lang.hitch(this, function(compatible) {
              if (compatible) {
                this._createMapItem(basemap);
              }
              def.resolve();
            }));
          _requestAll.push(def);
        }));
        all(_requestAll).then(function() {
          retDef.resolve();
        });
      }));
      return retDef;
    },

    _createMapItem: function(basemap) {
      var mapItem = new BasemapItem({
        appConfig: this.appConfig,
        basemap: basemap,
        folderUrl: this.folderUrl,
        spatialReference: this.spatialReference,
        nls: this.nls,
        mode: BasemapItem.MODE_SELECT
      });

      this.basemaps.push(mapItem);
      if (this.basemaps.length % 4 === 0) {
        html.addClass(mapItem.domNode, 'no-margin');
      }
      html.place(mapItem.domNode, this.allMapsTable);
      this.own(on(mapItem, 'selected', lang.hitch(this, function(isSelected) {
        this.emit('selectionChange');
      })));
    },

    getSelectedMapItems:function(){
      return array.filter(this.basemaps, function(basemap) {
        return basemap.isSelected();
      });
    }
  });
});