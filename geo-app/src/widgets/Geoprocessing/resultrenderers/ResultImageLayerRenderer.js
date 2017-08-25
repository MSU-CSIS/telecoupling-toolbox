define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/dom-style',
  'dojo/on',
  'dijit/_TemplatedMixin',
  'dojo/text!./ResultImageLayerRenderer.html',
  '../BaseResultRenderer'
], function(declare, lang, domStyle, on, _TemplatedMixin, template, BaseResultRenderer){
  return declare([BaseResultRenderer, _TemplatedMixin], {
    baseClass: 'jimu-gp-resultrenderer-base jimu-gp-renderer-draw-feature',
    templateString: template,

    postCreate: function(){
      this.inherited(arguments);
      if(this.layer){
        this._displayText();
        this._addResultLayer(this.layer);
      }
    },

    destroy: function(){
      if(this.layer){
        this.map.removeLayer(this.layer);
        this.layer = null;
      }
      this.inherited(arguments);
    },

    _displayText: function(){
      domStyle.set(this.clearNode, 'display', '');

      this.own(on(this.clearNode, 'click', lang.hitch(this, function(){
        if(this.layer){
          if(this.map.infoWindow.isShowing){
            this.map.infoWindow.hide();
          }
          //remove layer so it will not displayed in Layer List or Legend widget
          this.map.removeLayer(this.layer);
          this.layer = null;
        }
        domStyle.set(this.clearNode, 'display', 'none');
        domStyle.set(this.domNode, 'display', 'none');
      })));
    },

    _addResultLayer: function(layer){
      this.map.addLayers([layer]);
    }
  });
});
