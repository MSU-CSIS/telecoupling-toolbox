///////////////////////////////////////////////////////////////////////////
// Copyright © 2014 - 2017 Esri. All Rights Reserved.
//
// Licensed under the Apache License Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
///////////////////////////////////////////////////////////////////////////

define([
    'dojo/_base/declare',
    'dijit/_WidgetsInTemplateMixin',
    "dojo/Deferred",
    'jimu/BaseWidget',
    'jimu/portalUtils',
    'jimu/PanelManager',
    'jimu/portalUrlUtils',
    'jimu/utils',
    "esri/dijit/Basemap",
    "esri/dijit/BasemapLayer",
    'esri/dijit/BasemapGallery',
    'dojo/_base/lang',
    'dojo/_base/array',
    "dojo/_base/html",
    "dojo/query",
    'dojo/on',
    'dojo/promise/all',
    './utils',
    'jimu/dijit/LoadingIndicator'
  ],
  function(
    declare,
    _WidgetsInTemplateMixin,
    Deferred,
    BaseWidget,
    portalUtils,
    PanelManager,
    portalUrlUtils,
    jimuUtils,
    Basemap,
    BasemapLayer,
    BasemapGallery,
    lang,
    array,
    html,
    query,
    on,
    all,
    utils) {
    var clazz = declare([BaseWidget, _WidgetsInTemplateMixin], {

      name: 'BasemapGallery',
      baseClass: 'jimu-widget-basemapgallery',
      basemapGallery: null,
      spatialRef: null,

      startup: function() {
        /*jshint unused: false*/
        this.inherited(arguments);
        this.initBasemaps();
      },

      resize: function() {
        this._responsive();
      },

      _responsive: function() {
        // the default width of esriBasemapGalleryNode is 85px,
        // margin-left is 10px, margin-right is 10px;
        setTimeout(lang.hitch(this, function() {
          var paneNode = query('#' + this.id)[0];
          var width = html.getStyle(paneNode, 'width');
          var column      = parseInt(width / 105, 10);
          if (column > 0) {
            var margin      = width % 105;
            var addWidth    = parseInt(margin / column, 10);
            query('.esriBasemapGalleryNode', this.id).forEach(function(node) {
              html.setStyle(node, 'width', 85 + addWidth + 'px');
            });
          }
        }), 100);
      },

      initBasemaps: function() {
        var basemapsDef;
        var portalSelfDef;
        var config = lang.clone(this.config.basemapGallery);

        this.loadingShelter.show();
        //load form portal or config file.
        if (config.mode === 1) {
          basemapsDef = utils._loadPortalBaseMaps(this.appConfig.portalUrl, this.map);
        } else {
          basemapsDef = new Deferred();
          basemapsDef.resolve(config.basemaps);
        }

        var portal = portalUtils.getPortal(this.appConfig.portalUrl);
        portalSelfDef = portal.loadSelfInfo();
        all({
          'portalSelf': portalSelfDef,
          'basemaps': basemapsDef
        }).then(lang.hitch(this, function(result) {
          var basemaps = result.basemaps;
          var basemapObjs = [];
          var i = 0;
          var webmapBasemap = this._getWebmapBasemap();

          basemaps = array.filter(basemaps, function(basemap) {
            if(!basemap || !basemap.title) {
              return false;
            }
            var bingKeyResult;
            // first, filter bingMaps
            if(!utils.isBingMap(basemap)) {
              // do not have bingKey and basemap is not bingMap.
              bingKeyResult = true;
            } else if(result.portalSelf.bingKey) {
              // has bingKey, can add any bing map or not;
              bingKeyResult = true;
            } else {
              // do not show basemap if do not has bingKey as well as basemap is bingMap.
              bingKeyResult = false;
            }

            // basemap does not have title means basemap load failed.
            return basemap.title && bingKeyResult;
          }, this);

          // if basemap of current webmap is not include, so add it.
          for(i = 0; i < basemaps.length; i++) {
            if (utils.compareSameBasemapByOrder(basemaps[i], webmapBasemap)) {
              break;
            }
          }
          if(i === basemaps.length) {
            basemaps.push(webmapBasemap);
          }

          for (i = 0; i < basemaps.length; i++) {
            var n = basemaps[i].layers.length;
            var layersArray = [];
            for (var j = 0; j < n; j++) {
              layersArray.push(new BasemapLayer(basemaps[i].layers[j]));
            }
            basemaps[i].layers = layersArray;
            if (!basemaps[i].thumbnailUrl) {
              basemaps[i].thumbnailUrl = this.folderUrl + "images/default.jpg";
            } else {
              var reg = /^(https?:)?\/\//;
              if (reg.test(basemaps[i].thumbnailUrl)) {
                basemaps[i].thumbnailUrl = basemaps[i].thumbnailUrl +
                                           utils.getToken(this.appConfig.portalUrl);
              } else {
                basemaps[i].thumbnailUrl =
                  jimuUtils.processUrlInWidgetConfig(basemaps[i].thumbnailUrl, this.folderUrl);
              }
              // else if(basemaps[i].thumbnailUrl.startWith('/') ||
              //   basemaps[i].thumbnailUrl.startWith('data')){
              //   basemaps[i].thumbnailUrl = basemaps[i].thumbnailUrl;
              // }else{
              //   //if path is relative, relative to widget's folder
              //   basemaps[i].thumbnailUrl = this.appUrl + basemaps[i].thumbnailUrl;
              // }
            }
            basemapObjs.push(new Basemap(basemaps[i]));
          }

          config.map = this.map;
          if (this.appConfig.portalUrl) {
            config.portalUrl = this.appConfig.portalUrl;
          }
          config.basemaps = basemapObjs;
          config.showArcGISBasemaps = false;
          config.bingMapsKey = result.portalSelf.bingKey;
          this.basemapGallery = new BasemapGallery(config, this.basemapGalleryDiv);
          this.basemapGallery.startup();
          this.own(on(this.basemapGallery,
                      "selection-change",
                      lang.hitch(this, this.selectionChange)));
          this._responsive();

          this.loadingShelter.hide();
        })).otherwise(lang.hitch(this, function() {
          this.loadingShelter.hide();
        }));
      },

      _getWebmapBasemap: function() {
        var thumbnailUrl;
        if (this.map.itemInfo.item.thumbnail) {
          thumbnailUrl = portalUrlUtils.getItemUrl(this.appConfig.portalUrl,
                         this.map.itemInfo.item.id) + "/info/" + this.map.itemInfo.item.thumbnail;
        } else {
          thumbnailUrl = null;
        }
        return {
          title: this.map.itemInfo.itemData.baseMap.title,
          thumbnailUrl: thumbnailUrl,
          layers: this.map.itemInfo.itemData.baseMap.baseMapLayers,
          spatialReference: this.map.spatialReference
        };
      },

      selectionChange: function() {
        this.updateExtent();

        if (this.gid === 'widgetOnScreen') {
          PanelManager.getInstance().closePanel(this.id + '_panel');
        }
      },

      updateExtent: function() {
        if (this.map.getNumLevels() > 0) {
          // Set scale to nearest level of current basemap layer
          var basemap = this.basemapGallery.getSelected();
          var layers = basemap.getLayers();
          var currentLod = this.map.__tileInfo.lods[this.map.getLevel()];
          var layer, tileInfo;

          if (layers.length > 0) {
            layer = layers[0];
            tileInfo = layer.tileInfo ||
              (layer.serviceInfoResponse && layer.serviceInfoResponse.tileInfo);
            if (tileInfo && currentLod) {
              // normalize scale
              var mapScale = currentLod.scale / this.map.__tileInfo.dpi;
              var bestScale;
              array.forEach(tileInfo.lods, function(lod) {
                var scale = lod.scale / tileInfo.dpi;
                if (!bestScale || Math.abs(scale - mapScale) < Math.abs(bestScale - mapScale)){
                  bestScale = scale;
                }
              });
              if (Math.abs(bestScale - mapScale) / mapScale > (1 / this.map.width)) {
                this.map.setScale(bestScale * tileInfo.dpi);
              }
            }
          }
        }
      }
    });

    return clazz;
  });