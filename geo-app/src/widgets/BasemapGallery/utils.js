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
  'dojo/_base/lang',
  'dojo/Deferred',
  'dojo/json',
  'dojo/_base/array',
  'dojo/promise/all',
  'esri/SpatialReference',
  'jimu/portalUtils',
  'jimu/shared/basePortalUrlUtils',
  'esri/request',
  'dojo/text!./esri_tileinfo.json'
], function(lang, Deferred, JSON, array, all, SpatialReference, portalUtils,
  basePortalUrlUtils, esriRequest, esriTileInfoText) {
  var mo = {};
  var esriTileInfo = JSON.parse(esriTileInfoText);
  mo._loadPortalBaseMaps = function(portalUrl, map) {
    var defRet = new Deferred();
    var deferreds = [];
    getWebMapsFromBasemapGalleryGroup(portalUrl).then(function(response) {
      var basemapItems = response.results;
      array.forEach(basemapItems, function(basemapItem) {
        var def = new Deferred();
        var thumbnailUrl = _getStanderdUrl(basemapItem.thumbnailUrl);

        deferreds.push(def);
        basemapItem.getItemData().then(function(basemapItemData) {
          mo._getBasemapSpatialReference(basemapItem, basemapItemData)
            .then(lang.hitch(this, function(basemapSpatialRef) {
              var basemapLayers = basemapItemData.baseMap.baseMapLayers;
              mo.isBasemapCompatibleWithMap(basemapSpatialRef, basemapLayers, map)
                .then(lang.hitch(this, function(compatible) {
                  if (compatible) {
                    def.resolve({
                      layers: basemapLayers,
                      title: basemapItem.title || basemapItemData.baseMap.title,
                      thumbnailUrl: thumbnailUrl,
                      spatialReference: basemapSpatialRef
                    });
                  } else {
                    def.resolve({});
                  }
                }));
            }));
        });
      });

      all(deferreds).then(function(basemaps) {
        var filteredBasemaps = array.filter(basemaps, function(basemap) {
          if (basemap && basemap.title) {
            return true;
          } else {
            return false;
          }
        }, this);
        defRet.resolve(filteredBasemaps);
      });
    }, function(err) {
      defRet.reject(err);
    });
    return defRet;
  };

  mo.isBasemapCompatibleWithMap = function(basemapSR, basemapLayers, map) {
    var def = new Deferred();
    var mapSR = map.spatialReference;
    var wider = (map.width > map.height) ? map.width : map.height;

    // 1. check whether spatial references are compatible
    if (!mapSR || !basemapLayers || basemapLayers.length <= 0 ||
        !basemapSR || !mapSR.equals(new SpatialReference(+basemapSR.wkid))) {
      def.resolve(false);
      return def;
    }

    // 2. check whether tiling schemes are compatible
    if (map.getNumLevels() === 0) { // current map is dynamic
      if(basemapLayers[0].layerType === "OpenStreetMap" ||
        (basemapLayers[0].layerType && basemapLayers[0].layerType.indexOf("BingMaps") > -1) ||
        basemapLayers[0].layerType === "WebTiledLayer" ||
        basemapLayers[0].layerType === "VectorTileLayer" ||
        basemapLayers[0].layerType === "ArcGISImageServiceVectorLayer" ||
        basemapLayers[0].layerType === 'ArcGISTiledImageServiceLayer') {
        def.resolve(false);
      } else {
        def.resolve(true);
      }
    } else { // current map is tiled map service
      if(basemapLayers[0].layerType && basemapLayers[0].layerType.indexOf('ArcGIS') === 0 &&
      basemapLayers[0].url) {
        // can switch to arcgis dynamic services with Map capability
        getServiceInfo(basemapLayers[0].url).then(function(res) {
          basemapLayers[0].serviceInfoResponse = res;
          if (res && res.tileInfo) { // tiled
            def.resolve(mo.tilingSchemeCompatible(map.__tileInfo, res.tileInfo, wider));
          } else if (res && res.capabilities &&
            (res.capabilities.indexOf('Map') >= 0 || res.capabilities.indexOf('Image') >= 0)) {
            // dynamic map/image service
            def.resolve(true);
          } else {
            def.resolve(false);
          }
        });
      } else if(basemapLayers[0].layerType === 'WMS') { // wms layer
        def.resolve(true);
      } else if(mo.isNoUrlLayerMap(basemapLayers) || basemapLayers[0].layerType === 'VectorTileLayer') {
        // BingMap, OpenStreetMap or VectorTileLayer, compare tiling scheme
        def.resolve(mo.tilingSchemeCompatible(map.__tileInfo, esriTileInfo, wider));
      } else { // WebTiledLayer, WMTSLayer and other tiled map service layer
        def.resolve(mo.tilingSchemeCompatible(map.__tileInfo, basemapLayers[0].tileInfo, wider));
      }
    }

    return def;
  };

  mo.tilingSchemeCompatible = function(mapTileInfo, tileInfo, wider) {
    if (mapTileInfo && tileInfo) { // both are tiled
      return compareTilingScheme(mapTileInfo, tileInfo, wider);
    }
    return true;
  };

  /**
   * check whether two basemap layers are the same.
   * custom basemap may have no layerType.
   *
   * possible basemapLayers：
   * ArcGIS:
   * Image Service Vector Layer (ArcGISImageServiceVectorLayer)
   * Tiled Image Service Layer (ArcGISTiledImageServiceLayer)
   * Tiled Map Service Layer (ArcGISTiledMapServiceLayer)
   * Map Service Layer (ArcGISMapServiceLayer)
   * Image Service Layer (ArcGISImageServiceLayer)
   *
   * Third party:
   * Bing layer (bingLayer)
   * OpenStreetMap Layer (OpenStreetMap)
   * WebTiledLayer (WebTiledLayer)
   * Vector Tile Layer (VectorTileLayer)
   * WMS Layer (WMS)
   */
  mo.isSameBasemapLayer = function(layer1, layer2) {
    var url1, url2;
    if (layer1.layerType && layer2.layerType) {
      if (layer1.layerType !== layer2.layerType) {
        return false;
      }
      // ArcGIS web service
      if (layer1.layerType === 'ArcGISImageServiceVectorLayer' ||
        layer1.layerType === 'ArcGISTiledImageServiceLayer' ||
        layer1.layerType === 'ArcGISTiledMapServiceLayer' ||
        layer1.layerType === 'ArcGISMapServiceLayer' ||
        layer1.layerType === 'ArcGISImageServiceLayer') {
        url1 = _getStanderdUrl(layer1.url || "");
        url2 = _getStanderdUrl(layer2.url || "");
        return url1.toLowerCase() === url2.toLowerCase();
      }
      if (layer1.layerType === 'BingMapsAerial' ||
        layer1.layerType === 'BingMapsRoad' ||
        layer1.layerType === 'BingMapsHybrid' ||
        layer1.layerType === 'OpenStreetMap') {
        return true; // layerType must be same
      }
      if (layer1.layerType === 'VectorTileLayer') {
        url1 = _getStanderdUrl(layer1.styleUrl || "");
        url2 = _getStanderdUrl(layer2.styleUrl || "");
        return url1.toLowerCase() === url2.toLowerCase();
      }
      if (layer1.layerType === 'WMS') {
        url1 = _getStanderdUrl(layer1.mapUrl || "");
        url2 = _getStanderdUrl(layer2.mapUrl || "");
        return url1.toLowerCase() === url2.toLowerCase();
      }
      if (layer1.layerType === 'WebTiledLayer') {
        if(layer1.templateUrl && layer2.templateUrl) {
          url1 = _getStanderdUrl(layer1.templateUrl || "");
          url2 = _getStanderdUrl(layer2.templateUrl || "");
          return url1.toLowerCase() === url2.toLowerCase();
        } else if (layer1.wmtsInfo && layer2.wmtsInfo) {
          url1 = _getStanderdUrl(layer1.wmtsInfo.url || "");
          url2 = _getStanderdUrl(layer2.wmtsInfo.url || "");
          return url1.toLowerCase() === url2.toLowerCase();
        }
      }
    } else {
      // At least one of the layer's layerType parameter is missing,
      // compare the url directly.
      url1 = _getStanderdUrl(layer1.url || "");
      url2 = _getStanderdUrl(layer2.url || "");
      return url1.toLowerCase() === url2.toLowerCase();
    }

    return false;
  };

  mo.compareSameBasemapByOrder = function(basemap, webmapBasemap) {
    var basemapLayers = basemap.layers,
      webmapLayers = webmapBasemap.layers;
    if (basemapLayers.length !== webmapLayers.length) {
      return false;
    }
    for (var i = 0; i < basemapLayers.length; i++) {
      if (!mo.isSameBasemapLayer(basemapLayers[i], webmapLayers[i])) {
        return false;
      }
    }
    return true;
  };

  mo.isBingMap = function(basemap) {
    if (!basemap || !basemap.layers) {
      return false;
    }
    for (var i = 0; i < basemap.layers.length; i++) {
      if (basemap.layers[i].type === "BingMapsAerial" ||
        basemap.layers[i].type === "BingMapsRoad" ||
        basemap.layers[i].type === "BingMapsHybrid") {
        return true;
      }
    }
    return false;
  };

  mo.isNoUrlLayerMap = function(basemapLayers) {
    for (var i = 0; i < basemapLayers.length; i++) {
      if (basemapLayers[i].type === "BingMapsAerial" ||
        basemapLayers[i].type === "BingMapsRoad" ||
        basemapLayers[i].type === "BingMapsHybrid" ||
        basemapLayers[i].type === "OpenStreetMap") {
        return true;
      }
    }
    return false;
  };

  mo.getToken = function(portalUrl) {
    var portal = portalUtils.getPortal(portalUrl);
    portal.updateCredential();
    return portal.credential ? "?token=" + portal.credential.token : "";
  };

  mo.removeUrlQuery = function(url) {
    return _removeUrlQurey(url);
  };

  mo.getStanderdUrl = function(url) {
    return _getStanderdUrl(url);
  };

  mo.getUniqueTitle = function(title, titleArray) {
    if (!titleArray || titleArray.length === 0) {
      return title;
    }
    var sameTitles = array.filter(titleArray, function(t) {
      if (t === title) {
        return true;
      }
      if (t.indexOf(title) === 0) {
        var suffix = t.substr(title.length + 1);
        return !isNaN(+suffix);
      }
      return false;
    });
    if (sameTitles.length === 0) {
      return title;
    }
    var ids = array.map(sameTitles, function(t) {
      if (t === title) {
        return 0;
      } else {
        var suffix = t.substr(title.length + 1);
        return +suffix;
      }
    });
    ids = ids.sort();
    return title + ' ' + (ids[ids.length - 1] + 1);
  };

  mo.getBasemapInfo = function(portalUrl, itemId) {
    var portal = portalUtils.getPortal(portalUrl);
    var basemapItem, data;
    return portal.getItemById(itemId).then(function(portalItem) {
      basemapItem = portalItem;
      return portalItem.getItemData();
    }).then(function(itemData) {
      data = itemData;
      return mo._getBasemapSpatialReference(basemapItem, itemData);
    }).then(function(sf) {
      return {
        thumbnailUrl: basemapItem.thumbnailUrl,
        title: basemapItem.title || data.baseMap.title,
        layers: data.baseMap.baseMapLayers,
        spatialReference: new SpatialReference(sf)
      };
    });
  };

  mo.getBasemapGalleryGroup = function(portalUrl, groupQueryString) {
    var def = new Deferred();
    var portal = portalUtils.getPortal(portalUrl);
    //title:"ArcGIS Online Basemaps" AND owner:esri_en
    var ownerIndex = groupQueryString.indexOf('esri_');
    if (ownerIndex >= 0) {
      /*global dojoConfig*/
      var oldOwner = groupQueryString.slice(ownerIndex, ownerIndex + 7);
      var newOwner = 'esri_' + dojoConfig.locale.slice(0, 2);
      groupQueryString = groupQueryString.replace(oldOwner, newOwner);
    }
    portal.queryGroups({
      f: 'json',
      q: groupQueryString
    }).then(lang.hitch(this, function(response) {
      if (response.results.length > 0) {
        var group = response.results[0];
        def.resolve(group);
      } else {
        def.reject();
      }
    }), lang.hitch(this, function() {
      def.reject();
    }));
    return def;
  };

  mo._getBasemapSpatialReference = function(basemapItem, basemapItemData) {
    var basemapSpatialRef = null, async = false;
    var spatialRefDef = new Deferred();
    if ((basemapItem.owner && basemapItem.owner.indexOf("esri_") === 0) ||
      mo.isNoUrlLayerMap(basemapItemData.baseMap.baseMapLayers)) {
      basemapSpatialRef = {
        wkid: "102100"
      };
    } else if (basemapItemData.spatialReference || basemapItem.spatialReference) {
      basemapSpatialRef = basemapItemData.spatialReference || basemapItem.spatialReference;
    } else if (basemapItemData.baseMap.baseMapLayers && basemapItemData.baseMap.baseMapLayers[0]) {
      var lyr = basemapItemData.baseMap.baseMapLayers[0];
      if(lyr.url && lyr.url.indexOf('rest/services') > 0) {
        async = true;
        getServiceInfo(basemapItemData.baseMap.baseMapLayers[0].url)
        .then(lang.hitch(this, function(res) {
          if (res && res.spatialReference) {
            basemapSpatialRef = res.spatialReference;
          }
          spatialRefDef.resolve(basemapSpatialRef);
        }), function(err) {
          console.error(err);
          spatialRefDef.resolve(null);
        });
      } else if (lyr.layerType === 'VectorTileLayer') {
        basemapSpatialRef = {
          wkid: "102100"
        };
      } else {
        // WebTiledLayer, OGC layer, etc.
        var extent = lyr.fullExtent || lyr.initialExtent;
        if (extent) {
          basemapSpatialRef = extent.spatialReference;
        }
      }
    }
    if (!async) {
      spatialRefDef.resolve(basemapSpatialRef);
    }
    return spatialRefDef;
  };

  // remove url query and delete the last '/'.
  function _removeUrlQurey(url) {
    if (!url) {
      return null;
    }
    var queryIndex = url.indexOf('?');
    var httpIndex = url.search(/http|\/\//);
    if (httpIndex === 0 && queryIndex !== -1) {
      return url.slice(0, queryIndex).replace(/\/*$/g, '');
    } else {
      return url;
    }
  }

  // standerd url
  //   * no protocol
  //   * no query
  function _getStanderdUrl(url) {
    if (!url) {
      return "";
    } else {
      return basePortalUrlUtils.removeProtocol(_removeUrlQurey(url));
    }
  }

  function getWebMapsFromBasemapGalleryGroup(portalUrl) {
    var def = new Deferred();
    //var portalUrl = this.appConfig.portalUrl;
    portalUtils.getPortalSelfInfo(portalUrl).then(lang.hitch(this, function(portalSelf) {
      //title:"ArcGIS Online Basemaps" AND owner:esri_en
      var groupQueryString = portalSelf.basemapGalleryGroupQuery;
      if (portalSelf.useVectorBasemaps === true && portalSelf.vectorBasemapGalleryGroupQuery) {
        // Use vector basemap
        groupQueryString = portalSelf.vectorBasemapGalleryGroupQuery;
      }
      mo.getBasemapGalleryGroup(portalUrl, groupQueryString).then(lang.hitch(this, function(group) {
        var queryStr = portalUtils.webMapQueryStr;
        group.queryItems({
          start: 1,
          num: 100,
          f: 'json',
          q: queryStr
        }).then(lang.hitch(this, function(searchResponse) {
          def.resolve(searchResponse);
        }), lang.hitch(this, function() {
          def.reject();
        }));
      }), lang.hitch(this, function() {
        def.reject();
      }));
    }));

    return def;
  }

  /**
   * Check whether tileInfo1 is compatible with tileInfo2
   * Copy from esri/dijit/BasemapGallery
   */
  function compareTilingScheme(tileInfo1, tileInfo2, wider) {
    var matchOne = false;
    var matchSecond = false;
    var i, k;
    for (i = 0; i < tileInfo1.lods.length; i++) {
      var scale1 = tileInfo1.lods[i].scale;
      if (tileInfo1.dpi !== tileInfo2.dpi) {
        // normalize scale
        scale1 = tileInfo1.lods[i].scale / tileInfo1.dpi;
      }
      for (k = 0; k < tileInfo2.lods.length; k++) {
        var scale2 = tileInfo2.lods[k].scale;
        if (tileInfo1.dpi !== tileInfo2.dpi) {
          // normalize scale
          scale2 = tileInfo2.lods[k].scale / tileInfo2.dpi;
        }
        if ((Math.abs(scale2 - scale1) / scale2) < (1 / wider)) {
          if (!matchOne) {
            matchOne = true;
          } else {
            matchSecond = true;
            break;
          }
        }
        if (scale2 < scale1) {
          // nothing below here will fit anyway
          break;
        }
      }
      if (matchSecond) {
        break;
      }
    }

    if (matchSecond) {
      return true;
    } else if (matchOne) {
      // maybe one tileInfo has only one level
      if (tileInfo1.lods.length === 1 || tileInfo2.lods.length === 1) {
        return true;
      }
    }
    return false;
  }

  function getServiceInfo(url) {
    return esriRequest({
      url: url,
      content: {f: 'json'},
      handleAs: 'json',
      callbackParamName: "callback"
    }).then(function (response) {
      return response;
    }, function () {
      return null;
    });
  }

  return mo;
});