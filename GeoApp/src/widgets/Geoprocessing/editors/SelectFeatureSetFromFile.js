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
  'dojo/dom-attr',
  'dojo/dom-style',
  'dojo/on',
  'dojo/json',
  'dojo/text!./SelectFeatureSetFromFile.html',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'esri/request',
  'esri/geometry/scaleUtils',
  'esri/InfoTemplate',
  'esri/layers/FeatureLayer',
  'esri/renderers/SimpleRenderer',
  'esri/tasks/FeatureSet',
  'jimu/dijit/Message',
  'jimu/portalUrlUtils',
  'jimu/symbolUtils',
  './BaseFeatureSetEditor',
  'dijit/form/Form',
  'dijit/form/Select'
],
function(declare, lang, domAttr, domStyle, on, JSON,
  template, _TemplatedMixin, _WidgetsInTemplateMixin, esriRequest,
  scaleUtils, InfoTemplate, FeatureLayer, SimpleRenderer, FeatureSet,
  Message, portalUrlUtils, symbolUtils, BaseFeatureSetEditor){
  return declare([BaseFeatureSetEditor, _TemplatedMixin, _WidgetsInTemplateMixin], {
    baseClass: 'jimu-gp-editor-base jimu-gp-editor-file',
    templateString: template,
    editorName: 'SelectFeatureSetFromFile',
    layer: undefined,

    constructor: function(){
      this.uniqueID = new Date().getTime();
    },

    postCreate: function(){
      this.inherited(arguments);
      domStyle.set(this.clearLink, 'display', 'none');
      domStyle.set(this.uploadStatus, 'display', 'none');
      this.uploadStatus.src = require.toUrl('jimu') + '/images/loading_circle.gif';
    },

    destroy: function(){
      this._clear();
    },

    getValue: function(){
      if(this.activeViewIndex === 0) {
        if(this.layer){
          var featureset = new FeatureSet();
          featureset.features = this.layer.graphics;
          return featureset;
        }else{
          return null;
        }
      } else {
        return this.getFeatureSet();
      }
    },

    _onUpload: function(){
      if(!domAttr.get(this.fileInput, 'value')){
        new Message({
          message:this.nls.noFileSelected
        });
        return;
      }

      var fileName = domAttr.get(this.fileInput, 'value');
      fileName = fileName.replace(/\\/g, '/');
      fileName = fileName.substr(fileName.lastIndexOf('/') + 1);
      this.fileInfo.innerHTML = fileName;
      domStyle.set(this.uploadStatus, 'display', '');
      //Define the input params for generate see the rest doc for details
      //http://www.arcgis.com/apidocs/rest/index.html?generate.html
      var params = {
        'name': fileName,
        'targetSR': this.map.spatialReference,
        'maxRecordCount': 1000,
        'enforceInputFileSizeLimit': true,
        'enforceOutputJsonSizeLimit': true
      };

      //generalize features for display. Here we generalize at 1:40,000 which is approx 10 meters
      //This should work well when using web mercator.
      var extent = scaleUtils.getExtentForScale(this.map, 40000);
      var resolution = extent.getWidth() / this.map.width;
      params.generalize = true;
      params.maxAllowableOffset = resolution;
      params.reducePrecision = true;
      params.numberOfDigitsAfterDecimal = 0;

      esriRequest({
        url: this._getPortalUrl() + '/sharing/rest/content/features/generate',
        content: {
          'filetype': 'shapefile',
          'publishParameters': JSON.stringify(params),
          'f': 'json'
        },
        form: this.fileForm.domNode,
        handleAs: 'json',
        load: lang.hitch(this, function(response){
          domStyle.set(this.uploadStatus, 'display', 'none');
          if (response.error) {
            new Message({
              message: response.error.message || response.error
            });
            return;
          }
          this.addToMap(response.featureCollection);
        }),
        error: lang.hitch(this, function(){
          domStyle.set(this.uploadStatus, 'display', 'none');
          var message = this.nls.generateShapefileError +
            this._getPortalUrl() + '/sharing/rest/content/features/generate';
          new Message({message: message});
        })
      });
    },

    addToMap: function(featureCollection){
      this._clear();

      var fsLayer = featureCollection.layers[0];
      var infoTemplate = new InfoTemplate('Details', '${*}');
      this.layer = new FeatureLayer(fsLayer, {
        infoTemplate: infoTemplate
      });
      //associate the feature with the popup on click to enable highlight and zoom to
      this.own(on(this.layer, 'click', lang.hitch(this, function (event) {
        this.map.infoWindow.setFeatures([event.graphic]);
      })));
      //change default symbol if desired. Comment this out and the layer will draw with the default symbology
      this.changeRenderer();
      var fullExtent = this.layer.fullExtent;

      this.map.addLayer(this.layer);
      this.map.setExtent(fullExtent.expand(1.25), true);

      domStyle.set(this.clearLink, 'display', '');
    },

    changeRenderer: function() {
      //change the default symbol for the feature collection for polygons and points
      var symbol = null;
      switch (this.layer.geometryType) {
      case 'esriGeometryPoint':
        symbol = symbolUtils.getDefaultMarkerSymbol();
        break;
      case 'esriGeometryPolyline':
        symbol = symbolUtils.getDefaultLineSymbol();
        break;
      case 'esriGeometryPolygon':
        symbol = symbolUtils.getDefaultFillSymbol();
        break;
      }
      if (symbol) {
        this.layer.setRenderer(new SimpleRenderer(symbol));
      }
    },

    _getPortalUrl: function(){
      return portalUrlUtils.getStandardPortalUrl(this.appConfig.portalUrl);
    },

    _clear: function(){
      if(this.layer){
        this.layer.clear();
        this.map.removeLayer(this.layer);
        this.fileInfo.innerHTML = '';
        domAttr.set(this.fileInput, 'value', '');
        domStyle.set(this.clearLink, 'display', 'none');
      }
    }
  });
});
