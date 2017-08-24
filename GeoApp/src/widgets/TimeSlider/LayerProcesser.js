///////////////////////////////////////////////////////////////////////////
// Copyright © 2014 - 2016 Esri. All Rights Reserved.
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

define(['dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/Evented',
  'dijit/_WidgetBase'
],
  function (declare, lang, array,
    Evented, _WidgetBase) {

    var clazz = declare([_WidgetBase, Evented], {
      nls: null,
      map: null,
      layerInfosObj: null,

      setLayerInfosObj: function (layerInfosObj) {
        this.layerInfosObj = layerInfosObj;
      },

      processTimeDisableLayer: function () {
        var i = 0,
          len, layer, layerId;
        for (i = 0, len = this.map.layerIds.length; i < len; i++) {
          layerId = this.map.layerIds[i];
          layer = this.map.getLayer(layerId);

          this._processTimeUpdate(layer);
        }

        for (i = 0, len = this.map.graphicsLayerIds.length; i < len; i++) {
          layerId = this.map.graphicsLayerIds[i];
          layer = this.map.getLayer(layerId);

          this._processTimeUpdate(layer);
        }
      },
      _processTimeUpdate: function (layer) {
        var _layerInfo = null;
        var timeAnimation = true;
        _layerInfo = this.layerInfosObj.getLayerInfoById(layer.id);
        timeAnimation = _layerInfo && _layerInfo.originOperLayer &&
          (_layerInfo.originOperLayer.timeAnimation !== false);
        if (!timeAnimation && 'setUseMapTime' in layer) {
          layer.setUseMapTime(false);
        }
      },

      hasVisibleTemporalLayer: function () {
        var i = 0,
          len, layer, layerId;
        for (i = 0, len = this.map.layerIds.length; i < len; i++) {
          layerId = this.map.layerIds[i];
          layer = this.map.getLayer(layerId);

          if (this._isTimeTemporalLayer(layer, true)) {
            return true;
          }
        }

        for (i = 0, len = this.map.graphicsLayerIds.length; i < len; i++) {
          layerId = this.map.graphicsLayerIds[i];
          layer = this.map.getLayer(layerId);

          if (this._isTimeTemporalLayer(layer, true)) {
            return true;
          }
        }

        return false;
      },
      _isTimeTemporalLayer: function (layer, mustVisible) {
        var _hasValidTime = layer && layer.timeInfo && layer.useMapTime;
        var _layerInfo = this.layerInfosObj.getLayerInfoById(layer.id);
        var timeAnimation = _layerInfo && _layerInfo.originOperLayer &&
          (_layerInfo.originOperLayer.timeAnimation !== false);
        var condition = _hasValidTime && timeAnimation && (mustVisible ? layer.visible : true);

        if (condition) {
          var layerType = layer.declaredClass;
          if (layerType === "esri.layers.KMLLayer") {
            var internalLayers = layer.getLayers();
            var some = array.some(internalLayers, function (kLayer) {
              if (kLayer.timeInfo && kLayer.timeInfo.timeExtent) {
                return true;
              }
              return false;
            });
            if (some) {
              return true;
            }
          } else if (layer.timeInfo && layer.timeInfo.timeExtent) {
            return true;
          }
        }

        return false;
      },

      _getVisibleTemporalLayerNames: function () {
        var i = 0,
          len, layer, layerId;
        var ids = [];
        for (i = 0, len = this.map.layerIds.length; i < len; i++) {
          layerId = this.map.layerIds[i];
          layer = this.map.getLayer(layerId);

          if (this._isTimeTemporalLayer(layer, true)) {
            ids.push(layer.id);
          }
        }

        for (i = 0, len = this.map.graphicsLayerIds.length; i < len; i++) {
          layerId = this.map.graphicsLayerIds[i];
          layer = this.map.getLayer(layerId);

          if (this._isTimeTemporalLayer(layer, true)) {
            ids.push(layer.id);
          }
        }

        var names = array.map(ids, lang.hitch(this, function (id) {
          var info = this.layerInfosObj.getLayerInfoById(id);
          return info.title || "";
        }));

        return names;
      },

      _onLayerInfosIsShowInMapChanged: function (changedLayerInfos) {
        var timeTemporalLayerChanged = array.some(
          changedLayerInfos,
          lang.hitch(this, function (layerInfo) {
            var _layer = null;
            while (!_layer) {
              _layer = this.map.getLayer(layerInfo.id);
              layerInfo = layerInfo.parentLayerInfo;
            }

            return this.layerProcesser._isTimeTemporalLayer(_layer);
          }));

        if (timeTemporalLayerChanged) {
          lang.hitch(this, function () {
            this.layerProcesser._onTimeTemportalLayerChanged();
          });
        }
      },

      _onLayerInfosChanged: function (layerInfo, changedType, layerInfoSelf) {
        /* jshint unused:true */
        if (changedType === 'added') {
          var _layer = this.map.getLayer(layerInfoSelf.id);
          var visibleTimeTemporalLayerChanged = this.layerProcesser._isTimeTemporalLayer(_layer, true);

          if (visibleTimeTemporalLayerChanged) {
            lang.hitch(this, function () {
              this.layerProcesser._onTimeTemportalLayerChanged();
            });
          }
        } else if (changedType === 'removed') {
          lang.hitch(this, function () {
            this.layerProcesser._onTimeTemportalLayerChanged();
          });
        }
      },

      _onTimeTemportalLayerChanged: function () {
        if (this.state !== 'closed') {
          if (this.layerProcesser.hasVisibleTemporalLayer()) {
            if (this.timeSlider) {
              this.updateLayerLabel();
            } else {
              this.showTimeSlider();
            }
          } else {
            if (this.timeSlider) {
              this.closeTimeSlider();
            }
          }
        }
      }
    });

    return clazz;
  });