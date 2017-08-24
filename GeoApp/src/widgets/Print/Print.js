define([
  'dojo/_base/declare',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  'esri/tasks/PrintTask',
  "esri/tasks/PrintParameters",
  "esri/tasks/PrintTemplate",
  "esri/request",
  'esri/lang',
  'esri/arcgis/utils',
  'dojo/_base/lang',
  'dojo/_base/array',
  'dojo/_base/html',
  'dojo/dom-style',
  'dojo/dom-construct',
  'dojo/dom-class',
  'dojo/promise/all',
  'dojo/Deferred',
  'jimu/portalUrlUtils',
  'dojo/text!./templates/Print.html',
  'dojo/text!./templates/PrintResult.html',
  'dojo/aspect',
  'dojo/query',
  'jimu/LayerInfos/LayerInfos',
  'jimu/dijit/LoadingShelter',
  'jimu/dijit/Message',
  'jimu/utils',
  'dojo/on',
  'dijit/popup',
  'dijit/form/ValidationTextBox',
  'dijit/form/Form',
  'dijit/form/Select',
  'dijit/form/NumberTextBox',
  'dijit/form/Button',
  'dijit/form/CheckBox',
  'dijit/ProgressBar',
  'dijit/form/DropDownButton',
  'dijit/TooltipDialog',
  'dijit/form/RadioButton',
  'dijit/form/SimpleTextarea',
  'esri/IdentityManager',
  'dojo/store/Memory'
], function(
  declare,
  _WidgetBase,
  _TemplatedMixin,
  _WidgetsInTemplateMixin,
  PrintTask,
  PrintParameters,
  PrintTemplate,
  esriRequest,
  esriLang,
  arcgisUtils,
  lang,
  array,
  html,
  domStyle,
  domConstruct,
  domClass,
  all,
  Deferred,
  portalUrlUtils,
  printTemplate,
  printResultTemplate,
  aspect,
  query,
  LayerInfos,
  LoadingShelter,
  Message,
  utils,
  on,
  popup,
  ValidationTextBox) {
  // Main print dijit
  var PrintDijit = declare([_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin], {
    widgetsInTemplate: true,
    templateString: printTemplate,
    map: null,
    count: 1,
    results: [],
    authorText: null,
    copyrightText: null,
    defaultTitle: null,
    defaultFormat: null,
    defaultLayout: null,
    baseClass: "gis_PrintDijit",
    pdfIcon: require.toUrl("./widgets/Print/images/pdf.png"),
    imageIcon: require.toUrl("./widgets/Print/images/image.png"),
    printTaskURL: null,
    printTask: null,
    async: false,
    // showAdvancedOption: true,
    _showSettings: false,

    _currentTemplateInfo: null,

    postCreate: function() {
      this.inherited(arguments);
      var printParams = {
        async: this.async
      };
      // var _handleAs = 'json';

      this.printTask = new PrintTask(this.printTaskURL, printParams);
      this.printparams = new PrintParameters();
      this.printparams.map = this.map;
      //fix issue #7141
      // this.printparams.outSpatialReference = this.map.spatialReference;

      this.shelter = new LoadingShelter({
        hidden: true
      });
      this.shelter.placeAt(this.domNode);
      this.shelter.startup();
      this.shelter.show();

      this.titleNode.set('value', this.defaultTitle);
      this.authorNode.set('value', this.defaultAuthor);
      this.copyrightNode.set('value', this.defaultCopyright);

      var serviceUrl = portalUrlUtils.setHttpProtocol(this.printTaskURL);
      var portalNewPrintUrl = portalUrlUtils.getNewPrintUrl(this.appConfig.portalUrl);
      this._isNewPrintUrl = serviceUrl === portalNewPrintUrl ||
        /sharing\/tools\/newPrint$/.test(serviceUrl);
      var scaleRadio = query('input', this.printWidgetMapScale.domNode)[0];
      var extentRadio = query('input', this.printWidgetMapExtent.domNode)[0];
      utils.combineRadioCheckBoxWithLabel(scaleRadio, this.printWidgetMapScaleLabel);
      utils.combineRadioCheckBoxWithLabel(extentRadio, this.printWidgetMapExtentLabel);

      if (this.defaultLayout === 'MAP_ONLY') {
        html.setStyle(this.titleTr, 'display', 'none');
      } else {
        html.setStyle(this.titleTr, 'display', '');
      }

      if (this._hasLabelLayer()) {
        html.setStyle(this.labelsFormDijit.domNode, 'display', '');
        html.setStyle(this.labelsTitleNode, 'display', '');
      } else {
        html.setStyle(this.labelsFormDijit.domNode, 'display', 'none');
        html.setStyle(this.labelsTitleNode, 'display', 'none');
      }

      LayerInfos.getInstance(this.map, this.map.itemInfo)
        .then(lang.hitch(this, function(layerInfosObj) {
          this.layerInfosObj = layerInfosObj;
          return all([this._getPrintTaskInfo(), this._getLayerTemplatesInfo()])
            .then(lang.hitch(this, function(results) {
              var taksInfo = results[0],
                templatesInfo = results[1];
              if (templatesInfo && !templatesInfo.error) {
                var parameters = templatesInfo && templatesInfo.results;
                if (parameters && parameters.length > 0) {
                  array.some(parameters, lang.hitch(this, function(p) {
                    return p && p.paramName === 'Output_JSON' ?
                      this.templateInfos = p.value : false;
                  }));
                  if (this.templateInfos && this.templateInfos.length > 0) {
                    this.templateNames = array.map(this.templateInfos, function(ti) {
                      return ti.layoutTemplate;
                    });
                  }
                }
              } else {
                console.warn('Get Layout Templates Info Error',
                  templatesInfo && templatesInfo.error);
              }
              if (!esriLang.isDefined(taksInfo) || (taksInfo && taksInfo.error)) {
                this._handleError(taksInfo.error);
              } else {
                this._handlePrintInfo(taksInfo);
              }
            }));
        })).always(lang.hitch(this, function() {
          this.shelter.hide();
        }));

      if (this.printTask._getPrintDefinition) {
        aspect.after(
          this.printTask,
          '_getPrintDefinition',
          lang.hitch(this, 'printDefInspector'),
          false);
      }
      if (this.printTask._createOperationalLayers) {
        // if opLayers contains markerSymbol of map.infoWindow, the print job will failed
        aspect.after(
          this.printTask,
          '_createOperationalLayers',
          lang.hitch(this, '_fixInvalidSymbol')
        );
        aspect.after(
          this.printTask,
          '_createOperationalLayers',
          lang.hitch(this, '_excludeInvalidLegend')
        );
      }
    },

    _hasLabelLayer: function() {
      return array.some(this.map.graphicsLayerIds, function(glid) {
        var l = this.map.getLayer(glid);
        return l && l.declaredClass === 'esri.layers.LabelLayer';
      }, this);
    },

    _getPrintTaskInfo: function() {
      // portal own print url: portalname/arcgis/sharing/tools/newPrint
      var def = new Deferred();
      if (this._isNewPrintUrl) { // portal own print url
        def.resolve({
          isGPPrint: false
        });
      } else {
        esriRequest({
          url: this.printTaskURL,
          content: {
            f: "json"
          },
          callbackParamName: "callback",
          handleAs: "json",
          timeout: 60000
        }).then(lang.hitch(this, function(data) {
            def.resolve({
              isGPPrint: true,
              data: data
            });
          }), lang.hitch(this, function(err) {
            def.resolve({
              error: err
            });
          })
        );
      }

      return def;
    },

    _getLayerTemplatesInfo: function() {
      var def = new Deferred();
      var parts = this.printTaskURL.split('/');
      var pos = parts.indexOf('GPServer');
      if (pos > -1) {
        var url = null;
        if (/Utilities\/PrintingTools\/GPServer/.test(this.printTaskURL)) {
          url = parts.slice(0, pos + 1).join('/') + '/' +
            encodeURIComponent('Get Layout Templates Info Task') + '/execute';
        } else {
          url = parts.slice(0, pos + 1).join('/') + '/' +
            encodeURIComponent('Get Layout Templates Info') + '/execute';
        }
        esriRequest({
          url: url,
          content: {
            f: "json"
          },
          callbackParamName: "callback",
          handleAs: "json",
          timeout: 60000
        }).then(lang.hitch(this, function(info) {
          def.resolve(info);
        }), lang.hitch(this, function(err) {
          def.resolve({
            error: err
          });
        }));
      } else {
        def.resolve(null);
      }

      return def;
    },

    _fixInvalidSymbol: function(opLayers) {
      array.forEach(opLayers, function(ol) {
        if (ol.id === 'map_graphics') {
          var layers = lang.getObject('featureCollection.layers', false, ol);
          if (layers && layers.length > 0) {
            array.forEach(layers, function(layer) {
              if (layer && layer.featureSet &&
                layer.featureSet.geometryType === "esriGeometryPoint") {
                array.forEach(layer.featureSet.features, function(f) {
                  if (f && f.symbol && !f.symbol.style) {
                    f.symbol.style = "esriSMSSquare";
                  }
                });
              }
            });
          }
        }
      }, this);
      return opLayers;
    },

    _excludeInvalidLegend: function(opLayers) {
      function getSubLayerIds(legendLayer) {
        return array.filter(legendLayer.subLayerIds, lang.hitch(this, function(subLayerId) {
          var subLayerInfo = this.layerInfosObj.getLayerInfoById(legendLayer.id + '_' + subLayerId);
          return subLayerInfo && subLayerInfo.getShowLegendOfWebmap();
        }));
      }

      if (this.printTask.allLayerslegend) {
        var legends = arcgisUtils.getLegendLayers({map: this.map, itemInfo: this.map.itemInfo});
        var legendLayersOfWebmap = array.map(legends, function(legend) {
          return {
            id: legend.layer.id
          };
        });

        var legendArray = this.printTask.allLayerslegend;
        var arr = [];
        for (var i = 0; i < legendArray.length; i++) {
          var legendLayer = legendArray[i];
          var layer = this.map.getLayer(legendLayer.id);
          var layerInfo = this.layerInfosObj.getLayerInfoById(legendLayer.id);
          var validLayerType = layer && layer.declaredClass &&
            layer.declaredClass !== "esri.layers.GraphicsLayer";
          var validRenderer = !layer.renderer ||
            (layer.renderer && !layer.renderer.hasVisualVariables());
          var showLegendInMap = layerInfo && layerInfo.getShowLegendOfWebmap();
          if (validLayerType && validRenderer && showLegendInMap) {
            if (legendLayer.subLayerIds) {
              legendLayer.subLayerIds = lang.hitch(this, getSubLayerIds, legendLayer)();
            }

            arr.push(legendLayer);
          }
        }

        // fix issue 6072
        array.forEach(legendLayersOfWebmap, lang.hitch(this, function(legend) {
          var inLegends = array.some(arr, lang.hitch(this, function(l) {
            return l.id === legend.id;
          }));
          var layerInfo = this.layerInfosObj.getLayerInfoById(legend.id);
          var showLegend = layerInfo && layerInfo.getShowLegendOfWebmap() &&
            layerInfo.isShowInMap();
          if (!inLegends && showLegend) {
            arr.push(legend);
          }
        }));
        this.printTask.allLayerslegend = arr;
      }
      return opLayers;
    },

    printDefInspector: function(printDef) {
      //do what you want here then return the object.
      if (this.preserve.preserveScale === 'force') {
        printDef.mapOptions.scale = this.preserve.forcedScale;
      }
      return printDef;
    },

    _handleError: function(err) {
      console.log('print widget load error: ', err);
      new Message({
        message: err.message || err
      });
    },

    onLayoutChange: function(newValue) {
      var pos = this.templateNames && this.templateNames.indexOf(newValue);
      if (pos > -1) {
        html.empty(this.customTextElementsTable);
        var templateInfo = this._currentTemplateInfo = this.templateInfos[pos];
        var customTextElements =  lang.getObject(
          "layoutOptions.customTextElements",
          false, templateInfo);
        if (customTextElements && customTextElements.length > 0) {
          var textNames = [];
          array.forEach(customTextElements, lang.hitch(this, function(cte) {
            for (var p in cte) {
              if (textNames.indexOf(p) < 0) {
                var row = this.customTextElementsTable.insertRow(-1);
                var cell0 = row.insertCell(-1);
                cell0.appendChild(html.toDom(p + ': '));
                var cell1 = row.insertCell(-1);
                cell1.appendChild((new ValidationTextBox({
                  name: p,
                  trim: true,
                  required: false,
                  value: cte[p],
                  style: 'width:100%'
                })).domNode);
                textNames.push(p);
              }
            }
          }));
        }

        var hasAuthorText = lang.getObject('layoutOptions.hasAuthorText', false, templateInfo);
        if (!hasAuthorText) {
          html.setStyle(this.authorTr, 'display', 'none');
        } else {
          html.setStyle(this.authorTr, 'display', '');
        }
        var hasCopyrightText = lang.getObject(
          'layoutOptions.hasCopyrightText', false, templateInfo);
        if (!hasCopyrightText) {
          html.setStyle(this.copyrightTr, 'display', 'none');
        } else {
          html.setStyle(this.copyrightTr, 'display', '');
        }
        var hasTitleText = lang.getObject('layoutOptions.hasTitleText', false, templateInfo);
        if (!hasTitleText) {
          html.setStyle(this.titleTr, 'display', 'none');
        } else {
          html.setStyle(this.titleTr, 'display', '');
        }
        var hasLegend = lang.getObject('layoutOptions.hasLegend', false, templateInfo);
        if (!hasLegend) {
          html.setStyle(this.legendTr, 'display', 'none');
        } else {
          html.setStyle(this.legendTr, 'display', '');
        }
      } else if (newValue === 'MAP_ONLY') {
        html.setStyle(this.authorTr, 'display', 'none');
        html.setStyle(this.copyrightTr, 'display', 'none');
        html.setStyle(this.titleTr, 'display', 'none');
        html.setStyle(this.legendTr, 'display', 'none');

        this._currentTemplateInfo = {
          layoutOptions: {
            hasTitleText: false,
            hasCopyrightText: false,
            hasAuthorText: false,
            hasLegend: false
          }
        };
      } else {
        html.setStyle(this.authorTr, 'display', '');
        html.setStyle(this.copyrightTr, 'display', '');
        html.setStyle(this.titleTr, 'display', '');
        html.setStyle(this.legendTr, 'display', '');
        this._currentTemplateInfo = {
          layoutOptions: {
            hasTitleText: true,
            hasCopyrightText: true,
            hasAuthorText: true,
            hasLegend: true
          }
        };
      }
    },

    _getMapAttribution: function() {
      var attr = this.map.attribution;
      if (attr && attr.domNode) {
        return html.getProp(attr.domNode, 'textContent');
      } else {
        return "";
      }
    },

    showSettings: function(event) {
      event.preventDefault();
      event.stopPropagation();
      if (this._showSettings) {
        popup.close(this.settingsDialog);
        this._showSettings = false;
      } else {
        popup.open({
          popup: this.settingsDialog,
          around: this.advancedButtonDijit
        });
        this._showSettings = true;
      }
    },

    _handlePrintInfo: function(rData) {
      if (!rData.isGPPrint) {
        domStyle.set(this.layoutDijit.domNode.parentNode.parentNode, 'display', 'none');
        domStyle.set(this.formatDijit.domNode.parentNode.parentNode, 'display', 'none');
        domStyle.set(this.advancedButtonDijit, 'display', 'none');
      } else {
        var data = rData.data;
        domStyle.set(this.layoutDijit.domNode.parentNode.parentNode, 'display', '');
        domStyle.set(this.formatDijit.domNode.parentNode.parentNode, 'display', '');
        domStyle.set(this.advancedButtonDijit, 'display', '');

        this.own(on(document.body, 'click', lang.hitch(this, function (event) {
          if (!this._showSettings) {
            return;
          }
          var target = event.target || event.srcElement;
          var node = this.settingsDialog.domNode;
          var isInternal = target === node || html.isDescendant(target, node);
          if (!isInternal) {
            popup.close(this.settingsDialog);
            this._showSettings = false;
          }
        })));
        // if (this.showAdvancedOption) {
        //   domStyle.set(this.advancedButtonDijit.domNode, 'display', '');
        // } else {
        //   domStyle.set(this.advancedButtonDijit.domNode, 'display', 'none');
        // }
        var Layout_Template = array.filter(data.parameters, function(param) {
          return param.name === "Layout_Template";
        });
        if (Layout_Template.length === 0) {
          console.log("print service parameters name for templates must be \"Layout_Template\"");
          return;
        }
        var layoutItems = array.map(Layout_Template[0].choiceList, function(item) {
          return {
            label: item,
            value: item
          };
        });
        layoutItems.sort(function(a, b) {
          return (a.label > b.label) ? 1 : ((b.label > a.label) ? -1 : 0);
        });
        this.layoutDijit.addOption(layoutItems);
        if (this.defaultLayout) {
          this.layoutDijit.set('value', this.defaultLayout);
        } else {
          this.layoutDijit.set('value', Layout_Template[0].defaultValue);
        }

        var Format = array.filter(data.parameters, function(param) {
          return param.name === "Format";
        });
        if (Format.length === 0) {
          console.log("print service parameters name for format must be \"Format\"");
          return;
        }
        var formatItems = array.map(Format[0].choiceList, function(item) {
          return {
            label: item,
            value: item
          };
        });
        formatItems.sort(function(a, b) {
          return (a.label > b.label) ? 1 : ((b.label > a.label) ? -1 : 0);
        });
        this.formatDijit.addOption(formatItems);
        if (this.defaultFormat) {
          this.formatDijit.set('value', this.defaultFormat);
        } else {
          this.formatDijit.set('value', Format[0].defaultValue);
        }
      }
    },

    print: function() {
      if (this.printSettingsFormDijit.isValid()) {
        var form = this.printSettingsFormDijit.get('value');
        lang.mixin(form, this.layoutMetadataDijit.get('value'));
        lang.mixin(form, this.labelsFormDijit.get('value'));
        this.preserve = this.preserveFormDijit.get('value');
        lang.mixin(form, this.preserve);
        this.layoutForm = this.layoutFormDijit.get('value');
        var mapQualityForm = this.mapQualityFormDijit.get('value');
        var mapOnlyForm = this.mapOnlyFormDijit.get('value');
        lang.mixin(mapOnlyForm, mapQualityForm);

        var elementsObj = this.customTextElementsDijit.get('value');
        var cteArray = [];
        for (var p in elementsObj) {
          var cte = {};
          cte[p] = elementsObj[p];
          cteArray.push(cte);
        }

        var templateInfo = this._currentTemplateInfo;
        var hasAuthorText = lang.getObject('layoutOptions.hasAuthorText', false, templateInfo);
        var hasCopyrightText = lang.getObject('layoutOptions.hasCopyrightText',
          false, templateInfo);
        var hasTitleText = lang.getObject('layoutOptions.hasTitleText', false, templateInfo);

        var template = new PrintTemplate();
        template.format = form.format;
        template.layout = form.layout;
        template.preserveScale = (form.preserveScale === 'true' || form.preserveScale === 'force');
        template.label = form.title;
        template.exportOptions = mapOnlyForm;
        template.showLabels = form.showLabels && form.showLabels[0];
        template.layoutOptions = {
          authorText: hasAuthorText ? form.author : "",
          copyrightText: hasCopyrightText ? (form.copyright || this._getMapAttribution()) : "",
          legendLayers: this._getLegendLayers(), // fix issue 7744
          titleText: hasTitleText ? form.title : "",
          customTextElements: cteArray
        };
        this.printparams.template = template;
        this.printparams.extraParameters = { // come from source code of jsapi
          printFlag: true
        };
        var fileHandel = this.printTask.execute(this.printparams);

        var result = new printResultDijit({
          count: this.count.toString(),
          icon: (form.format === "PDF") ? this.pdfIcon : this.imageIcon,
          docName: form.title,
          title: form.format + ', ' + form.layout,
          fileHandle: fileHandel,
          nls: this.nls
        }).placeAt(this.printResultsNode, 'last');
        result.startup();
        domStyle.set(this.clearActionBarNode, 'display', 'block');
        this.count++;
      } else {
        this.printSettingsFormDijit.validate();
      }
    },

    _getLegendLayers: function() {
      var hasLegend = lang.getObject('layoutOptions.hasLegend', false, this._currentTemplateInfo);
      var enabledLegend = this.layoutForm.legend.length > 0 && this.layoutForm.legend[0];
      if (this.printTask && !this.printTask._createOperationalLayers) {
        // if don't have _createOptionalLayers function
        var legendLayers = [];
        if (hasLegend && enabledLegend) {
          var legends = arcgisUtils.getLegendLayers({map: this.map, itemInfo: this.map.itemInfo});
          legendLayers = array.map(legends, function(legend) {
            return {
              layerId: legend.layer.id
            };
          });
        }

        return legendLayers;
      } else {
        return (hasLegend && enabledLegend) ? null : [];
      }
    },

    clearResults: function() {
      domConstruct.empty(this.printResultsNode);
      domStyle.set(this.clearActionBarNode, 'display', 'none');
      this.count = 1;
    },

    updateAuthor: function(user) {
      user = user || '';
      if (user && this.authorTB) {
        this.authorTB.set('value', user);
      }
    },

    getCurrentMapScale: function() {
      this.forceScaleNTB.set('value', this.map.getScale());
    }
  });

  // Print result dijit
  var printResultDijit = declare([_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin], {
    widgetsInTemplate: true,
    templateString: printResultTemplate,
    url: null,
    postCreate: function() {
      this.inherited(arguments);
      this.progressBar.set('label', this.nls.creatingPrint);
      this.fileHandle.then(lang.hitch(this, '_onPrintComplete'), lang.hitch(this, '_onPrintError'));
    },
    _onPrintComplete: function(data) {
      if (data.url) {
        this.url = data.url;
        html.setStyle(this.progressBar.domNode, 'display', 'none');
        html.setStyle(this.successNode, 'display', 'inline-block');
        domClass.add(this.resultNode, "printResultHover");
      } else {
        this._onPrintError(this.nls.printError);
      }
    },
    _onPrintError: function(err) {
      console.log(err);
      html.setStyle(this.progressBar.domNode, 'display', 'none');
      html.setStyle(this.errNode, 'display', 'block');
      domClass.add(this.resultNode, "printResultError");

      html.setAttr(this.domNode, 'title', err.details || err.message || "");
    },
    _openPrint: function() {
      if (this.url !== null) {
        window.open(this.url);
      }
    }
  });
  return PrintDijit;
});