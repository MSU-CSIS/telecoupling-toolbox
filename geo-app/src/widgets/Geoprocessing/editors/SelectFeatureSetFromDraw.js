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
  'dojo/_base/html',
  'dijit/_TemplatedMixin',
  'jimu/dijit/DrawBox',
  'esri/symbols/jsonUtils',
  'esri/tasks/FeatureSet',
  'esri/geometry/Polygon',
  'esri/graphic',
  'esri/graphicsUtils',
  './BaseFeatureSetEditor',
  'dojo/text!./SelectFeatureSetFromDraw.html',
  '../LayerOrderUtil'
],
function(declare, lang, array, html, _TemplatedMixin, DrawBox, symbolUtils,
  FeatureSet, Polygon, Graphic, graphicsUtils, BaseFeatureSetEditor,
  template, LayerOrderUtil) {
  //from url
  var clazz = declare([BaseFeatureSetEditor, _TemplatedMixin], {
    editorName: 'SelectFeatureSetFromDraw',
    templateString: template,

    constructor: function(options){
      this.inherited(arguments);
      this.paramName = options.param.name;
      this.drawLayerId = options.widgetUID + options.param.name;
    },

    postCreate: function(){
      this.inherited(arguments);
      html.addClass(this.domNode, 'jimu-gp-editor-draw');
      html.addClass(this.domNode, 'jimu-gp-editor-base');

      var drawOptions = {
        types: this.types,
        drawLayerId: this.drawLayerId,
        showClear: this.showClear,
        map: this.map
      };
      if(this.param.symbol) {
        drawOptions[this.types[0] + 'Symbol'] = symbolUtils.fromJson(this.param.symbol);
      }

      this.drawBox = new DrawBox(drawOptions);
      html.place(this.drawBox.domNode, this.inputNode);
      this.drawBox.startup();

      try{
        var layerOrderUtil = new LayerOrderUtil(this.config, this.map);
        layerOrderUtil.calculateLayerIndex(this.paramName, this.widgetUID).then(
            lang.hitch(this, function(layerIndex){
          if(layerIndex !== -1){
            this.map.reorderLayer(this.drawBox.drawLayer, layerIndex);
          }
        }));
      }catch(err){
        console.error(err.message);
      }

      this.startup();
    },

    getValue: function(){
      if(this.activeViewIndex === 0) {
        if(this.drawBox.drawLayer && this.drawBox.drawLayer.graphics.length > 0){
          return this._createFeatureSet(this.drawBox.drawLayer.graphics);
        }else{
          return null;
        }
      } else {
        return this.getFeatureSet();
      }
    },

    _createFeatureSet: function(graphics){
      var featureset = new FeatureSet();
      var features = [];
      var geometries = graphicsUtils.getGeometries(graphics);

      array.forEach(geometries, function(geom){
        var graphic;
        if(geom.type === 'extent'){
          graphic = new Graphic(Polygon.fromExtent(geom));
        }else{
          graphic = new Graphic(geom);
        }
        features.push(graphic);
      });
      featureset.features = features;
      return featureset;
    }
  });

  return clazz;
});
