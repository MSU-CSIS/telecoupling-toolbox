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
//
///////////////////////////////////////////////////////////////////////////

define([
    'dojo/_base/declare',
    'dijit/_WidgetsInTemplateMixin',
    'jimu/BaseWidgetSetting',
    'dojo/_base/lang',
    'dojo/_base/html',
    'dojo/_base/array',
    'dojo/on',
    'dojo/keys',
    'dojo/dom-style',
    'jimu/dijit/Popup',
    'jimu/utils',
    './Edit',
    '../utils',
    './GroupSelector',
    '../BasemapItem',
    'jimu/dijit/LoadingIndicator'
  ],
  function(
    declare,
    _WidgetsInTemplateMixin,
    BaseWidgetSetting,
    lang,
    html,
    array,
    on,
    keys,
    domStyle,
    Popup,
    jimuUtils,
    Edit,
    utils,
    GroupSelector,
    BasemapItem) {
    var RESPECT_ONLINE = 1, CUSTOM_BASEMAP = 2;

    return declare([BaseWidgetSetting, _WidgetsInTemplateMixin], {
      baseClass: 'jimu-widget-basemapgallery-setting',
      basemaps: [],
      mapItems: [],
      edit: null,
      editTr: null,
      popup: null,
      editIndex: null,
      spatialRef: null,

      postMixInProperties: function(){
        this.inherited(arguments);
        lang.mixin(this.nls, window.jimuNls.common);
        this.nomapTips = this.nls.basemapTips;
        this.nomapTips = this.nomapTips.replace('${import}', '<b>' + this.nls.importBasemap + '</b>');
        this.nomapTips = this.nomapTips.replace('${createNew}', '<b>' + this.nls.createBasemap + '</b>');
      },

      postCreate: function() {
        this.inherited(arguments);
        this.basemaps = [];
        this.mapItems = [];
        this.tipsSection.innerHTML = this.nomapTips;
        jimuUtils.combineRadioCheckBoxWithLabel(this.respectOnlineRaido, this.respectOnlineLabel);
        jimuUtils.combineRadioCheckBoxWithLabel(this.customRaido, this.customLabel);

        this.own(on(this.respectOnlineRaido, 'click', lang.hitch(this, function(){
          if (this.respectOnlineRaido.checked) {
            html.setStyle(this.customBasemapSection, 'display', 'none');
            html.setStyle(this.tipsSection, 'display', 'none');
            html.addClass(this.baseMapsDiv, 'mode-online');
            this.clearBaseMapsDiv();
            this.loadDefaultBasemaps();
          }
        })));
        this.own(on(this.customRaido, 'click', lang.hitch(this, function(){
          if (this.customRaido.checked) {
            html.setStyle(this.customBasemapSection, 'display', 'block');
            html.setStyle(this.nomapTipsSection, 'display', 'none');
            html.removeClass(this.baseMapsDiv, 'mode-online');
            this.clearBaseMapsDiv();
            this._createMapItems();
          }
        })));
      },

      startup: function() {
        this.inherited(arguments);
        if (!this.map) {
          domStyle.set(this.baseMapsDiv, 'display', 'none');
          return;
        }
        if (!this.config.basemapGallery) {
          this.config.basemapGallery = {};
        }
        this.setConfig(this.config);
      },

      setConfig: function(config) {
        this.config = config;
        this.basemaps = [];
        this.mapItems = [];

        // Add custom basemaps if any
        array.forEach(config.basemapGallery.basemaps, function(basemap) {
          this.basemaps.push({
            title: basemap.title,
            thumbnailUrl: basemap.thumbnailUrl,
            layers: basemap.layers,
            spatialReference: basemap.spatialReference
          });
        }, this);

        if (config.basemapGallery.mode === CUSTOM_BASEMAP || // compatible with old version
            (!('mode' in config.basemapGallery) && this.basemaps.length > 0)) {
          this.customRaido.checked = true;
          html.removeClass(this.baseMapsDiv, 'mode-online');
          domStyle.set(this.customBasemapSection, 'display', 'block');
          this.clearBaseMapsDiv();
          this._createMapItems();
        } else {
          this.respectOnlineRaido.checked = true;
          html.addClass(this.baseMapsDiv, 'mode-online');
          domStyle.set(this.customBasemapSection, 'display', 'none');
          this.clearBaseMapsDiv();
          this.loadDefaultBasemaps();
        }
      },

      getConfig: function() {
        if (this.respectOnlineRaido.checked) {
          this.config.basemapGallery.mode = RESPECT_ONLINE;
        } else if(this.customRaido.checked) {
          this.config.basemapGallery.mode = CUSTOM_BASEMAP;
        }
        this.config.basemapGallery.basemaps = this.basemaps;
        return this.config;
      },

      onAddBaseMapClick: function() {
        this._openEdit(null);
      },

      loadDefaultBasemaps: function() {
        this.loadingShelter.show();
        utils._loadPortalBaseMaps(this.appConfig.portalUrl, this.map)
          .then(lang.hitch(this, function(basemaps) {
            if (!basemaps || basemaps.length === 0) {
              html.setStyle(this.nomapTipsSection, 'display', '');
              this.loadingShelter.hide();
              return;
            }
            html.setStyle(this.nomapTipsSection, 'display', 'none');
            array.forEach(basemaps, function(basemap) {
              this._createMapItem(basemap, BasemapItem.MODE_READONLY);
            }, this);
            this.loadingShelter.hide();
          }), lang.hitch(this, function(err) {
            console.warn(err);
            this.loadingShelter.hide();
          }));
      },

      updateBasemap: function(title, basemap) {
        var index = -1;
        array.some(this.basemaps, function(item, i) {
          if(item.title === title) {
            index = i;
            return true;
          }
        });
        if (index !== -1) {
          this.basemaps[index] = basemap;
          this.mapItems[index].updateItem(basemap);
        }
      },

      addNewBasemap: function(basemap) {
        this._createMapItem(basemap, BasemapItem.MODE_EDIT);
        this.basemaps.push(basemap);
        html.setStyle(this.tipsSection, 'display', 'none');
      },

      _createMapItems: function() {
        this.loadingShelter.show();
        if (this.basemaps.length === 0) {
          html.setStyle(this.tipsSection, 'display', '');
          this.loadingShelter.hide();
          return;
        }
        html.setStyle(this.tipsSection, 'display', 'none');
        array.forEach(this.basemaps, function(basemap) {
          this._createMapItem(basemap, BasemapItem.MODE_EDIT);
        }, this);
        this.loadingShelter.hide();
      },

      _createMapItem: function(basemap, mode) {
        var mapItem = new BasemapItem({
          appConfig: this.appConfig,
          basemap: basemap,
          folderUrl: this.folderUrl,
          nls: this.nls,
          spatialReference: this.map.spatialReference,
          mode: mode
        });
        // if ((this.mapItems.length + 1) % 6 === 0) {
        //   html.addClass(mapItem.domNode, 'no-margin');
        // }
        html.place(mapItem.domNode, this.baseMapsDiv);
        if (mode === BasemapItem.MODE_EDIT) {
          this.own(on(mapItem, 'delete', lang.hitch(this, this._onMapItemDeleteClick)));
          this.own(on(mapItem, 'edit', lang.hitch(this, this._onMapItemEditClick)));
        }
        this.own(on(mapItem, 'selected', lang.hitch(this, this._onMapItemSelectedChange)));
        this.mapItems.push(mapItem);
      },

      clearBaseMapsDiv: function() {
        array.forEach(this.mapItems, function(mapItem) {
          html.destroy(mapItem.domNode);
        }, this);
        this.mapItems = [];
      },

      _openEdit: function(mapItem) {
        var basemap = mapItem ? mapItem.basemap : null;
        /*jshint unused: false*/
        var edit = new Edit({
          nls: this.nls,
          folderUrl: this.folderUrl,
          appUrl: this.appUrl,
          //baseMapSRID: this.spatialRef
          basemap: basemap,
          basemaps: this.basemaps,
          map: this.map,
          token: utils.getToken(this.appConfig.portalUrl)
        });
        //this.edit.setConfig(basemap || {});
        this.popup = new Popup({
          titleLabel: (basemap && basemap.title) || this.nls.createBasemap,
          autoHeight: true,
          content: edit,
          container: 'main-page',
          width: 800,
          height: 600,
          buttons: [{
            label: this.nls.ok,
            key: keys.ENTER,
            disable: true,
            //onClick: lang.hitch(this, '_onEditOk')
            onClick: lang.hitch(edit, edit._onEditOk, this)
          }, {
            label: this.nls.cancel,
            classNames: ['jimu-btn-vacation'],
            key: keys.ESCAPE,
            onClose: lang.hitch(edit, edit._onEditClose, this)
          }]
        });
        edit.startup();
      },

      _onMapItemEditClick: function(mapItem) {
        this._openEdit(mapItem);
      },

      _onMapItemDeleteClick: function(mapItem) {
        this.basemaps = array.filter(this.basemaps, function(basemap) {
          return mapItem.basemap.title !== basemap.title;
        }, this);
        this.mapItems = array.filter(this.mapItems, function(item) {
          return mapItem !== item;
        }, this);
        html.destroy(mapItem.domNode);
        // this._onMapItemSelectedChange();
        if(this.mapItems.length === 0) {
          html.setStyle(this.tipsSection, 'display', '');
        }
      },

      _onMapItemSelectedChange: function() {
        var selected = array.some(this.mapItems, function(item) {
          return item.isSelected();
        }, this);
        if(selected) {
          html.setStyle(this.deleteBasemapBtn, 'display', 'block');
        } else {
          html.setStyle(this.deleteBasemapBtn, 'display', 'none');
        }
      },

      _deleteSelectedItem: function() {
        var toDeleteMapItems = array.filter(this.mapItems, function(item) {
          return item.isSelected();
        }, this);
        this.mapItems = array.filter(this.mapItems, function(item) {
          return !item.isSelected();
        }, this);
        this.basemaps = array.map(this.mapItems, function(item) {
          return item.basemap;
        }, this);
        array.forEach(toDeleteMapItems, function(item) {
          html.destroy(item.domNode);
        }, this);
        this._onMapItemSelectedChange();
      },

      onDeleteBaseMapBtnClick: function() {
        var popup = new Popup({
          width: 400,
          height: 200,
          titleLabel: this.nls.warningTitle,
          content: this.nls.confirmDelete,
          container: 'main-page',
          buttons: [{
            label: this.nls.ok,
            key: keys.ENTER,
            classNames: ['map-selector-btn-ok'],
            onClick: lang.hitch(this, function() {
              popup.close();
              this._deleteSelectedItem();
            })
          }, {
            label: this.nls.cancel,
            key: keys.ESCAPE,
            classNames: ['map-selector-btn-cancel', 'jimu-btn-vacation'],
            onClick: lang.hitch(this, function() {
              popup.close();
            })
          }]
        });
      },

      onChooseFromOnlineClick: function() {
        var itemType = window.appInfo.appType === "HTML3D" ? "Web Scene" : "Web Map";
        var groupSelector = new GroupSelector({
          appConfig: this.appConfig,
          type: itemType,
          multiple: true,
          folderUrl: this.folderUrl,
          nls: this.nls,
          map: this.map,
          spatialReference: this.map.spatialReference
        });

        var popup = new Popup({
          width: 700,
          height: 500,
          titleLabel: this.nls.importTitle,
          content: groupSelector,
          container: 'main-page',
          onClose: lang.hitch(this, function() {
            try{
              if(groupSelector && groupSelector.domNode){
                groupSelector.destroy();
              }
            }
            catch(e){
              console.error(e);
            }
            groupSelector = null;
            return true;
          }),
          buttons: [{
            label: this.nls.ok,
            key: keys.ENTER,
            disable: true,
            classNames: ['map-selector-btn-ok'],
            onClick: lang.hitch(this, function() {
              var result = groupSelector.getSelectedBasemaps();
              //popup.close();
              this._chooseMapFromWeb(result, popup);
            })
          }, {
            label: this.nls.cancel,
            key: keys.ESCAPE,
            classNames: ['map-selector-btn-cancel', 'jimu-btn-vacation'],
            onClick: lang.hitch(this, function() {
              popup.close();
            })
          }]
        });
      },

      _chooseMapFromWeb: function(basemaps, mapSelectorPopup) {
        mapSelectorPopup.close();

        if (basemaps && basemaps.length > 0) {
          html.setStyle(this.tipsSection, 'display', 'none');
        }
        array.forEach(basemaps, function(basemap){
          // Rename title if necessary
          var titles = array.map(this.basemaps, function(basemap) {
            return basemap.title;
          });
          basemap.title = utils.getUniqueTitle(basemap.title, titles);
          this._createMapItem(basemap, BasemapItem.MODE_EDIT);
          this.basemaps.push(basemap);
        }, this);
      }
    });
  });