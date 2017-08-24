define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/dom-style',
  'dojo/dom-attr',
  'dojo/on',
  'dojo/dom-geometry',
  'dijit/_TemplatedMixin',
  'esri/layers/GraphicsLayer',
  'esri/layers/FeatureLayer',
  'esri/graphicsUtils',
  'esri/renderers/SimpleRenderer',
  'esri/renderers/jsonUtils',
  'esri/InfoTemplate',
  'jimu/dijit/FeatureActionPopupMenu',
  'dojo/text!./FeatureSetRenderer.html',
  '../BaseResultRenderer',
  '../LayerOrderUtil',
  './defaultSymbol'
], function(declare, lang, array, domStyle, domAttr, on, domGeom, _TemplatedMixin, GraphicsLayer,
  FeatureLayer, graphicsUtils, SimpleRenderer, rendererUtils, InfoTemplate,
  PopupMenu, template, BaseResultRenderer, LayerOrderUtil, defaultSymbol){
  return declare([BaseResultRenderer, _TemplatedMixin], {
    baseClass: 'jimu-gp-resultrenderer-base jimu-gp-renderer-draw-feature',
    templateString: template,

    postCreate: function(){
      this.inherited(arguments);
      this.popupMenu = PopupMenu.getInstance();
      if(this.value.features && this.value.features.length > 0){
        this._displayText();
        this._drawResultFeature(this.param, this.value);
      }else{
        domStyle.set(this.clearNode, 'display', 'none');
        domStyle.set(this.exportNode, 'display', 'none');
        this.labelContent.innerHTML = this.nls.emptyResult;
      }
    },

    destroy: function(){
      if(this.resultLayer){
        this.map.removeLayer(this.resultLayer);
      }
      this.inherited(arguments);
    },

    _displayText: function(){
      domStyle.set(this.clearNode, 'display', '');
      domAttr.set(this.clearNode, 'title', this.nls.clear);

      this.own(on(this.clearNode, 'click', lang.hitch(this, function(){
        if(this.resultLayer){
          if(this.map.infoWindow.isShowing){
            this.map.infoWindow.hide();
          }
          this.resultLayer.clear();
          //remove layer so it will not displayed in Layer List or Legend widget
          this.map.removeLayer(this.resultLayer);
        }
        domStyle.set(this.exportNode, 'display', 'none');
        domStyle.set(this.clearNode, 'display', 'none');
        this.labelContent.innerHTML = this.nls.cleared;
      })));

      domStyle.set(this.exportNode, 'display', '');
      domAttr.set(this.exportNode, 'title', this.nls.exportOutput);

      this.own(on(this.exportNode, 'click', lang.hitch(this, this._showActions)));
    },

    _showActions: function(event) {
      this.popupMenu.prepareActions(this.value, this.config.showExportButton).then(lang.hitch(this, function() {
        var position = domGeom.position(event.target);
        this.popupMenu.show(position);
      }));
    },

    _drawResultFeature: function(param, featureset){
      var infoTemplate;
      if(!param.popup){
        param.popup = {
          enablePopup: true,
          title: '',
          fields: []
        };
      }
      if(param.popup.enablePopup){
        //Use param.popup.title or a non-exist field name as the title of popup window.
        infoTemplate = new InfoTemplate(param.popup.title || '${Non-Exist-Field}',
            this._generatePopupContent(featureset));
      }
      if(this.config.shareResults && !this.config.useDynamicSchema){
        if(!param.defaultValue || !param.defaultValue.geometryType){
          throw Error('Output parameter default value does not provide enough information' +
            ' to draw feature layer.');
        }
        param.defaultValue.name = param.name;
        var featureCollection = {
          layerDefinition: param.defaultValue,
          featureSet: null
        };
        this.resultLayer =  new FeatureLayer(featureCollection, {
          id: this.widgetUID + param.name,
          infoTemplate: infoTemplate
        });
      }else{
        this.resultLayer =  new GraphicsLayer({
          id: this.widgetUID + param.name,
          infoTemplate: infoTemplate
        });
      }
      array.forEach(featureset.features, function(feature){
        this.resultLayer.add(feature);
      }, this);
      this.resultLayer.title = param.label || param.name;

      var renderer = param.renderer;
      if(this.config.useDynamicSchema || !renderer){
        if(featureset.geometryType === 'esriGeometryPoint' ||
            featureset.geometryType === 'esriGeometryMultipoint'){
          renderer = new SimpleRenderer(defaultSymbol.pointSymbol);
        }else if(featureset.geometryType === 'esriGeometryPolyline'){
          renderer = new SimpleRenderer(defaultSymbol.lineSymbol);
        }else if(featureset.geometryType === 'esriGeometryPolygon'){
          renderer = new SimpleRenderer(defaultSymbol.polygonSymbol);
        }
      }else{
        renderer = rendererUtils.fromJson(renderer);
      }
      this.resultLayer.setRenderer(renderer);
      this._addResultLayer(param.name);

      try{
        if (featureset.features && featureset.features.length > 0 &&
          featureset.features[0].geometry) {
          var extent = graphicsUtils.graphicsExtent(featureset.features);
          if(extent){
            this.resultLayer.fullExtent = extent.expand(1.4);
            this.map.setExtent(this.resultLayer.fullExtent);
          }
        }
      }
      catch(e){
        console.error(e);
      }
    },

    _addResultLayer: function(paramName){
      var layerOrderUtil = new LayerOrderUtil(this.config, this.map);
      try{
        layerOrderUtil.calculateLayerIndex(paramName, this.widgetUID).then(
            lang.hitch(this, function(layerIndex){
          if(layerIndex !== -1){
            this.map.addLayer(this.resultLayer, layerIndex);
          }else{
            this.map.addLayer(this.resultLayer);
          }
        }));
      }catch(err){
        console.error(err.message);
        console.warn('Draw result feature set on the top of map');
        this.map.addLayer(this.resultLayer);
      }
    },

    _generatePopupContent: function(featureset){
      var str = '<div class="geoprocessing-popup">' +
          '<table class="geoprocessing-popup-table" ' +
          'cellpadding="0" cellspacing="0">' + '<tbody>';
      var rowStr = '';
      var fields;

      if(!this.config.useDynamicSchema &&
          this.param.popup.fields &&
          this.param.popup.fields.length > 0){
        fields = this.param.popup.fields;
      }else{
        fields = featureset.fields;
      }

      array.forEach(fields, function(field){
        var row = '<tr valign="top">' +
            '<td class="attr-name">' + field.alias + '</td>' +
            '<td class="attr-value">${' + field.name + '}</td>' +
            '</tr>';
        rowStr += row;
      });
      return str + rowStr + '</tbody></table></div>';
    }
  });
});
