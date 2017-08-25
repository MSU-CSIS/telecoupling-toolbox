define([
  'dojo/_base/declare',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/dom-construct',
  'dojo/dom-style',
  'dojo/dom-attr',
  'dojo/on',
  'dojo/dom-geometry',
  'dijit/_TemplatedMixin',
  'dojo/store/Memory',
  'dgrid/OnDemandGrid',
  'dgrid/extensions/ColumnResizer',
  'jimu/dijit/FeatureActionPopupMenu',
  'jimu/LayerInfos/LayerInfos',
  'jimu/dijit/Popup',
  'dojo/text!./RecordSetRenderer.html',
  '../BaseResultRenderer'
], function(declare, lang, array, domConstruct, domStyle, domAttr, on, domGeom, _TemplatedMixin,
  Memory, OnDemandGrid, ColumnResizer,
  PopupMenu, LayerInfos, Popup, template, BaseResultRenderer){
  return declare([BaseResultRenderer, _TemplatedMixin], {
    baseClass: 'jimu-gp-resultrenderer-base jimu-gp-renderer-table',
    templateString: template,

    postCreate: function(){
      this.inherited(arguments);
      this.popupMenu = PopupMenu.getInstance();
      var fields = [];

      if(!this.value.features || this.value.features.length === 0){
        domStyle.set(this.clearNode, 'display', 'none');
        domStyle.set(this.exportNode, 'display', 'none');
        domStyle.set(this.magnifyNode, 'display', 'none');
        this.tableNode.innerHTML = this.nls.emptyResult;
        return;
      }
      domStyle.set(this.magnifyNode, 'display', '');

      if(!this.config.useDynamicSchema &&
          this.param.defaultValue &&
          this.param.defaultValue.output &&
          this.param.defaultValue.output.fields &&
          this.param.defaultValue.output.fields.length > 0){
        fields = this.param.defaultValue.output.fields;
      }else if(this.value.fields){
        fields = this.value.fields;
      }else if(this.value.features && this.value.features.length > 0){
        for(var p in this.value.features[0].attributes){
          fields.push({
            name: p
          });
        }
      }

      if(this.config.shareResults){
        //add table to the map
        var tableInfo, layerInfosObject = LayerInfos.getInstanceSync();

        var featureCollection = {
          layerDefinition: {
            'fields': fields
          },
          featureSet: this.value
        };
        tableInfo = layerInfosObject.addTable({
          featureCollectionData: featureCollection,
          title: this.param.label || this.param.name
        });

        // make clear button available
        domStyle.set(this.clearNode, 'display', '');
        domAttr.set(this.clearNode, 'title', this.nls.clear);

        this.own(on(this.clearNode, 'click', lang.hitch(this, function(){
          layerInfosObject.removeTable(tableInfo);
          domStyle.set(this.exportNode, 'display', 'none');
          domStyle.set(this.clearNode, 'display', 'none');
          domStyle.set(this.magnifyNode, 'display', 'none');
          this.labelContent.innerHTML = this.nls.cleared;
          domConstruct.empty(this.tableNode);
          if(this.table) {
            this.table.destroy();
          }
        })));
      }

      var data = array.map(this.value.features, function(feature){
        return feature.attributes;
      });

      domAttr.set(this.magnifyNode, 'title', this.nls.enlargeView);
      this.own(on(this.magnifyNode, 'click', lang.hitch(this, this.magnifyTable)));

      if (this.config.showExportButton) {
        domAttr.set(this.exportNode, 'title', this.nls.exportOutput);
        domStyle.set(this.exportNode, 'display', '');

        this.own(on(this.exportNode, 'click', lang.hitch(this, this._showActions)));
      }

      //Always creat table in output panel
      var columns = array.map(fields, function(field){
        return {
          label: field.alias || field.name,
          field: field.name
        };
      });

      var idProperty;
      array.some(this.value.fields, function(field){
        if(field.type === 'esriFieldTypeOID'){
          idProperty = field.name;
          return true;
        }
      });

      var memStore = new Memory({
        data: data,
        idProperty: idProperty
      });

      this.table = new (declare([OnDemandGrid, ColumnResizer]))({
        columns: columns,
        store: memStore
      });
      domConstruct.place(this.table.domNode, this.tableNode);
    },

    startup: function(){
      this.inherited(arguments);
      this.table.startup();
    },

    _showActions: function(event) {
      this.popupMenu.prepareActions(this.value, this.config.showExportButton).then(lang.hitch(this, function() {
        var position = domGeom.position(event.target);
        this.popupMenu.show(position);
      }));
    },

    magnifyTable: function() {
      var container = domConstruct.create('div', {
        'class': 'gp-table-magnified'
      });
      domConstruct.place(this.table.domNode, container);

      var popup = new Popup({
        content: container,
        titleLabel: this.param.tooltip || this.param.label || '',
        container: 'main-page',
        onClose: lang.hitch(this, function(){
          domConstruct.place(this.table.domNode, this.tableNode);
          this.table.resize();
        })
      });
      domStyle.set(popup.domNode, {
        top: '5%',
        left: '5%',
        width: '90%',
        height: '90%'
      });
      popup.startup();
      this.table.resize();
    }
  });
});
