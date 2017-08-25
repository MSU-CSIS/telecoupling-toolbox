define(
  ["dojo/_base/declare",
    "dojo/_base/lang",
    "dojo/_base/array",
    'dojo/_base/html',
    "dojo/on",
    "dojo/query",
    'dojo/Deferred',
    "dijit/_WidgetsInTemplateMixin",
    "dijit/registry",
    "jimu/BaseWidgetSetting",
    'jimu/dijit/ImageChooser',
    "dojo/text!./Edit.html",
    "jimu/dijit/ServiceURLInput",
    "jimu/SpatialReference/wkidUtils",
    'jimu/utils',
    "../utils"
  ],
  function(
    declare,
    lang,
    array,
    html,
    on,
    query,
    Deferred,
    _WidgetsInTemplateMixin,
    registry,
    BaseWidgetSetting,
    ImageChooser,
    template,
    ServiceURLInput,
    SRUtils,
    jimuUtils,
    utils) {
    return declare([BaseWidgetSetting, _WidgetsInTemplateMixin], {
      baseClass: "jimu-basemapgallery-Edit",
      ImageChooser: null,
      templateString: template,
      validUrl: false,
      mapName: null,
      subLayerUrlNum: 0,
      urlInputS: [],
      baseMapSRID: null,
      spatialReference: null,

      postCreate: function() {
        this.inherited(arguments);

        this.imageChooser = new ImageChooser({
          cropImage: true,
          defaultSelfSrc: this.folderUrl + "images/default.jpg",
          showSelfImg: true,
          format: [ImageChooser.GIF, ImageChooser.JPEG, ImageChooser.PNG],
          goldenWidth: 84,
          goldenHeight: 67
        });

        html.addClass(this.imageChooser.domNode, 'img-chooser');
        html.place(this.imageChooser.domNode, this.imageChooserBase, 'replace');

        this.own(on(this.url, 'Change', lang.hitch(this, '_onServiceUrlChange')));
        this.title.proceedValue = false;
        this.own(on(this.title, 'Change', lang.hitch(this, '_onBaseMapTitleChange')));
        this.url.proceedValue = false;
        this.url.setProcessFunction(lang.hitch(this, '_onServiceFetch', this.url),
          lang.hitch(this, '_onServiceFetchError'));
      },

      startup: function() {
        var thumbnailUrl, reg = /data:image/;
        if (this.basemap && this.basemap.title) {
          this.title.set('value', this.basemap.title);
        }
        if (this.basemap && this.basemap.thumbnailUrl) {
          if (reg.test(this.basemap.thumbnailUrl)) {
            thumbnailUrl = this.basemap.thumbnailUrl;
          } else if (this.basemap.thumbnailUrl.indexOf('//') === 0) {
            thumbnailUrl = this.basemap.thumbnailUrl;
          } else {
            thumbnailUrl = jimuUtils.processUrlInWidgetConfig(this.basemap.thumbnailUrl,
              this.folderUrl);
          }
        } else {
          thumbnailUrl = this.folderUrl + "images/default.jpg";
        }
        this.imageChooser.setDefaultSelfSrc(thumbnailUrl);

        if (this.basemap && this.basemap.layers) {
          if (utils.isNoUrlLayerMap(this.basemap.layers)) {
            html.destroy(this.urlPart);
            query(".delete-layer-url", this.urlEditSection).forEach(lang.hitch(this, function(dom) {
              html.addClass(dom, 'invisible');
            }));
            query(".add-layer-url", this.urlEditSection).forEach(lang.hitch(this, function(dom) {
              html.addClass(dom, 'invisible');
            }));
          } else {
            var numLayer = this.basemap.layers.length;
            if (this.basemap.layers[0] && this.basemap.layers[0].url) {
              this.url.set('value', this.basemap.layers[0].url);
            }
            for (var j = 1; j < numLayer; j++) {
              this.addLayerUrl(this.basemap.layers[j].url);
            }
          }
        }
      },

      _onServiceUrlChange: function() {
        this.popup.disableButton(0);
      },

      _checkTitle: function(title) {
        var validTitle = true;
        for (var i = 0; i < this.basemaps.length; i++) {
          if (this.basemaps[i].title === title) {
            if (this.basemap && this.basemap.title === title) {
              validTitle = true;
            } else {
              validTitle = false;
            }
          }
        }
        return validTitle;
      },

      _onBaseMapTitleChange: function(title) {
        // this._checkRequiredField();
        var validTitle = this._checkTitle(title);
        var errorMessage = null;
        if (!title) {
          this.title.proceedValue = false;
        } else if (validTitle) {
          this.title.proceedValue = true;
        } else {
          this.title.proceedValue = false;
          errorMessage = this.nls.invalidTitle1 + title + this.nls.invalidTitle2;
        }
        this._checkProceed(errorMessage);
      },

      _checkProceed: function(errorMessage) {
        var canProceed = true;
        var urlDijits = [];
        html.setAttr(this.errorMassage, 'innerHTML', '');
        if (this.title.proceedValue) {
          urlDijits = this._getUrlDijits();
          for (var i = 0; i < urlDijits.length; i++) {
            canProceed = canProceed && urlDijits[i].proceedValue;
          }
        } else {
          canProceed = false;
        }
        if (canProceed) {
          this.popup.enableButton(0);
        } else {
          this.popup.disableButton(0);
          if (errorMessage) {
            html.setAttr(this.errorMassage, 'innerHTML', errorMessage);
          }
        }
      },

      _onServiceFetch: function(urlDijit, evt) {
        var result = false;
        var errorMessage = null;
        var url = evt.url.replace(/\/*$/g, '');
        var wider = (this.map.width > this.map.height) ? this.map.width : this.map.height;
        if (this._isStringEndWith(url, '/MapServer') ||
          this._isStringEndWith(url, '/ImageServer')) {
          var curMapSpatialRefObj = this.map.spatialReference;
          var basemapSpatialRefObj = evt.data.spatialReference ||
            evt.data.extent.spatialReference ||
            evt.data.initialExtent.spatialReference ||
            evt.data.fullExtent.spatialReference;
          if (curMapSpatialRefObj &&
              basemapSpatialRefObj &&
              SRUtils.isSameSR(curMapSpatialRefObj.wkid, basemapSpatialRefObj.wkid) &&
              utils.tilingSchemeCompatible(this.map.__tileInfo, evt.data.tileInfo, wider)) {
            urlDijit.proceedValue = true;
            result = true;
          } else {
            urlDijit.proceedValue = false;
            result = false;
            errorMessage = this.nls.invalidBasemapUrl2;
          }
        } else {
          urlDijit.proceedValue = false;
          result = false;
          errorMessage = this.nls.invalidBasemapUrl1;
        }

        this._checkProceed(errorMessage);
        return result;
      },

      _isStringEndWith: function(s, endS) {
        return (s.lastIndexOf(endS) + endS.length === s.length);
      },

      _onServiceFetchError: function() {},

      onAddLayerUrl: function() {
        this.addLayerUrl();
      },

      addLayerUrl: function(url) {
        /*jshint unused: false*/
        var urlDom = html.create('div', {'class': 'input-url'}, this.urlEditSection);

        var urlInput = new ServiceURLInput({
          placeHolder: this.nls.urlPH,
          required: true,
          proceedValue: 0,
          style: {
            width: "95%"
          }
        }).placeAt(urlDom);
        html.addClass(urlInput.domNode, "url_field_dom");

        if (url) {
          urlInput.set('value', url);
        }

        var deleteSpanDom = html.create('div', {
          'class': 'delete-layer-url'
        }, urlDom);
        this.own(on(deleteSpanDom, 'click', lang.hitch(this, '_onDeleteClick', urlDom)));

        urlInput.setProcessFunction(lang.hitch(this, '_onServiceFetch', urlInput),
          lang.hitch(this, '_onServiceFetchError'));

        this._checkProceed();
      },

      _onDeleteClick: function(urlDom) {
        html.destroy(urlDom);
        this._checkProceed();
      },

      _getUrlDijits: function() {
        var urlDijits = [];
        query(".url_field_dom", this.urlEditSection).forEach(lang.hitch(this, function(urlDom) {
          urlDijits.push(registry.byNode(urlDom));
        }));
        return urlDijits;
      },

      _getEditedBaseMap: function() {
        var def = new Deferred(), reg = /data:image/;

        var basemap = {
          title: jimuUtils.stripHTML(this.title.value),
          layers: [],
          spatialReference: (this.basemap && this.basemap.spatialReference) ||
            this.map.spatialReference
        };

        // do not update basmaps if map is bingMap or openstreetMap
        if (utils.isNoUrlLayerMap(this.basemap ? this.basemap.layers : [])) {
          basemap.layers = this.basemap.layers;
        } else {
          array.forEach(this._getUrlDijits(), function(urlDijit) {
            basemap.layers.push({
              url: urlDijit.value
            });
          }, this);
        }

        if (reg.test(this.imageChooser.imageData)) {
          basemap.thumbnailUrl = this.imageChooser.imageData;
          def.resolve(basemap);
        } else {
          jimuUtils.getBase64Data(utils.getStanderdUrl(this.imageChooser.imageData))
          .then(lang.hitch(this, function(data) {
            if (data) {
              basemap.thumbnailUrl = data;
            } else {
              basemap.thumbnailUrl = this.folderUrl + "images/default.jpg";
            }
            def.resolve(basemap);
          }));
        }

        return def;
      },

      _onEditOk: function(settingWidget) {
        if (this.basemap) {
          //this.basemap = this._getEditedBaseMap();
          this._getEditedBaseMap().then(lang.hitch(this, function(basemap) {
            settingWidget.updateBasemap(this.basemap.title, basemap);
          }));
        } else {
          this._getEditedBaseMap().then(lang.hitch(this, function(basemap) {
            settingWidget.addNewBasemap(basemap);
          }));
        }
        settingWidget.popup.close();
      },

      _onEditClose: function(settingWidget) {
        if (settingWidget.popup) {
          settingWidget.popup.close();
        }
        this.destroy();
      }

    });
  });