define([
  'dojo/_base/declare',
  'dijit/_WidgetBase',
  'dojo/on',
  'dojo/_base/lang',
  'dojo/_base/Color',
  'dojo/Deferred',
  'esri/graphicsUtils',
  'esri/symbols/jsonUtils',
  'esri/layers/FeatureLayer',
  'esri/graphic',
  'jimu/utils',
  'jimu/clientStatisticsUtils'
], function(declare, _WidgetBase, on, lang, Color, Deferred, graphicsUtils, symbolJsonUtils, FeatureLayer,
  Graphic, jimuUtils, clientStatisticsUtils) {

  return declare([_WidgetBase], {
    //options
    //map

    //public methods

    //getChartOption
    //getChartOptionForServer
    //getChartOptionWithData

    //getClientStatisticsData
    //bindChartEvent
    //getLoadedLayer
    //mockFeatureLayerAndChartConfigValueFieldsForServer

    postMixInProperties: function() {
      this.nls = window.jimuNls.statisticsChart;
    },

    constructor: function(options) {
      this.map = options.map;
    },

    getChartOption: function(options, chart) {
      var data = this.getClientStatisticsData(options);
      this.bindChartEvent(chart, options, data, false);
      return this.getChartOptionWithData(options, data);
    },

    getChartOptionForServer: function(options, chart) {
      var data = this.getClientStatisticsData(options, true);
      this.bindChartEvent(chart, options, data, false);
      return this.getChartOptionWithData(options, data);
    },

    /*
      featureLayerOrUrlOrLayerDefinition: a FeatureLayer instance or FeatureLayer url
      features: feature array
      config:feature mode {
        mode,
        name,
        labelField,
        valueFields,
        sortOrder,
        highLightColor,
        types: [{
          type: 'bar',
          display: {
            backgroundColor,
            colors,
            showLegend,
            legendTextColor,
            showHorizontalAxis,
            horizontalAxisTextColor,
            showVerticalAxis,
            verticalAxisTextColor
          }
        }, {
          type: 'column',
          display: {
            backgroundColor,
            colors,
            showLegend,
            legendTextColor,
            showHorizontalAxis,
            horizontalAxisTextColor,
            showVerticalAxis,
            verticalAxisTextColor
          }
        }, {
          type: 'line',
          display: {
            backgroundColor,
            colors,
            showLegend,
            legendTextColor,
            showHorizontalAxis,
            horizontalAxisTextColor,
            showVerticalAxis,
            verticalAxisTextColor
          }
        }, {
          type: 'pie',
          display: {
            backgroundColor,
            colors,
            showLegend,
            legendTextColor,
            showDataLabel,
            dataLabelColor
          }
        }]
      }
      config: category mode {
        mode,
        name,
        categoryField,
        operation,
        valueFields,
        sortOrder,
        highLightColor,
        types
      }
      config: count mode {
        mode,
        name,
        categoryField,
        sortOrder,
        highLightColor,
        types
      }
      config: field mode {
        mode,
        name,
        operation,
        valueFields,
        sortOrder,
        highLightColor,
        types
      }
      */

    //return a feature layer
    getLoadedLayer: function(featureLayerOrUrlOrLayerDefinition) {
      return this._getLoadedLayer(featureLayerOrUrlOrLayerDefinition);
    },

    //--options--

    //--options.infos--
    // "layerDefinition": null,
    // "popupFieldInfosObj": null,
    // "features": [],
    // "featureLayerForChartSymbologyChart": null

    // --options.chartConfig--

    // "mode": "feature",
    // "type": "column",
    // "labelField": "OBJECTID",
    // "valueFields": ["POP2000", "POP2007"],
    // "sortOrder": {
    //   "isAsc": true,
    //   "field": "OBJECTID",
    //   "isLabelAxis": true
    // },
    // "useLayerSymbology": true,
    // "backgroundColor": "transparent",
    // "colors": [],
    // "showLegend": false,
    // "legendTextColor": "#333333",
    // "legendTextSize": 12,
    // "stack": "percent",
    // "showHorizontalAxis": true,
    // "horizontalAxisTextColor": "#333333",
    // "horizontalAxisTextSize": 12,
    // "showVerticalAxis": true,
    // "verticalAxisTextColor": "#333333",
    // "verticalAxisTextSize": 12

    // --data--

    // [{
    //   "category": "1",
    //   "valueFields": [1211537, 1299555],
    //   "dataFeatures": [],
    //   "color": "rgba(255,222,62,1)"
    // }]

    //return --data--
    getClientStatisticsData: function(options, forServer) {
      var chartConfig = options.chartConfig;
      var mode = chartConfig.mode;

      var csuOptions = {
        forServer: forServer,
        layerDefinition: options.featureLayer,
        features: options.features
      };

      if (typeof options.popupFieldInfosObj !== 'undefined') {
        csuOptions.popupFieldInfosObj = options.popupFieldInfosObj;
      }

      if (typeof chartConfig.labelField !== 'undefined') {
        csuOptions.labelField = chartConfig.labelField;
      }

      if (typeof chartConfig.categoryField !== 'undefined') {
        csuOptions.categoryField = chartConfig.categoryField;
      }

      if (chartConfig.valueFields && typeof chartConfig.valueFields !== 'undefined') {
        csuOptions.valueFields = chartConfig.valueFields;
      }

      if (typeof chartConfig.operation !== 'undefined') {
        csuOptions.operation = chartConfig.operation;
      }

      if (typeof chartConfig.sortOrder !== 'undefined') {
        csuOptions.sortOrder = chartConfig.sortOrder;
      }

      if (typeof chartConfig.dateConfig !== 'undefined') {
        csuOptions.dateConfig = chartConfig.dateConfig;
      }

      if (typeof chartConfig.nullValue !== 'undefined') {
        csuOptions.nullValue = chartConfig.nullValue;
      }

      if (typeof chartConfig.maxLabels !== 'undefined') {
        csuOptions.maxLabels = chartConfig.maxLabels;
      }

      if (typeof chartConfig.splitField !== 'undefined') {
        csuOptions.splitField = chartConfig.splitField;
      }

      if (mode === 'feature') {
        //return [{category:'a',valueFields:[10,100,2],dataFeatures:[f1]}]
        //options: {features, categoryField, valueFields, operation, sortOrder, dateConfig/*optional*/
        //maxLabels, nullValue/*optional*/, featureLayerForChartSymbologyChart/*optional*/,
        //seriesStyle.useLayerSymbology/*optional*/, splitField, /*optional*/}
        return clientStatisticsUtils.getFeatureModeStatisticsInfo(csuOptions);
      } else if (mode === 'category') {
        //data: [{category:'a',valueFields:[10,100,2],dataFeatures:[f1]}]
        return clientStatisticsUtils.getCategoryModeStatisticsInfo(csuOptions);
      } else if (mode === 'count') {
        //return [{category:'a',valueFields:[10,100,2],dataFeatures:[f1,f2...]}]
        return clientStatisticsUtils.getCountModeStatisticsInfo(csuOptions);
      } else if (mode === 'field') {
        //return [{label:fieldName,value:,fieldValue}]
        return clientStatisticsUtils.getFieldModeStatisticsInfo(csuOptions);
      }
    },

    //get the chart option for jimu/dijit/Chart.js
    //return Chart.js's option
    getChartOptionWithData: function(options, data) {

      if (options.features) {
        // isSelectedFeatures = !!options.features.isSelectedFeatures;
        options.features = options.features.filter(lang.hitch(this, function(feature) {
          return !!feature.attributes;
        }));
        var chartConfig = options.chartConfig;
        var type = chartConfig.type;
        if (!chartConfig.backgroundColor) {
          chartConfig.backgroundColor = "transparent"; //'#ffffff';
        }
        if (!chartConfig.hasOwnProperty("showLegend")) {
          chartConfig.showLegend = false;
        }
        if (!chartConfig.legendTextColor) {
          chartConfig.legendTextColor = this.fontColor;
        }
        if (type === 'pie') {
          if (!chartConfig.hasOwnProperty("showDataLabel")) {
            chartConfig.showDataLabel = true;
          }
          if (!chartConfig.dataLabelColor) {
            chartConfig.dataLabelColor = this.fontColor;
          }
        } else {
          if (!chartConfig.hasOwnProperty("showHorizontalAxis")) {
            chartConfig.showHorizontalAxis = true;
          }
          if (!chartConfig.horizontalAxisTextColor) {
            chartConfig.horizontalAxisTextColor = this.fontColor;
          }
          if (!chartConfig.hasOwnProperty("showVerticalAxis")) {
            chartConfig.showVerticalAxis = true;
          }
          if (!chartConfig.verticalAxisTextColor) {
            chartConfig.verticalAxisTextColor = this.fontColor;
          }
        }
      }
      if (options.popupFieldInfosObj) {
        this.popupFieldInfosObj = options.popupFieldInfosObj;
      } else {
        this.popupFieldInfosObj = {};
      }
      this.featureLayer = options.featureLayer;
      this.features = options.features;

      var chartSeriesOption = this._createChartSeries(options, data);
      //TODO mixin series style
      return this._mapSettingConfigToChartOption(chartSeriesOption, options);
    },

    //bind event to eCharts
    bindChartEvent: function(chart, options, data, allowZoomToGraphic) {
      var chartConfig = options.chartConfig;
      this.highLightColor = chartConfig.highLightColor || '#00ffff';
      var mode = chartConfig.mode;
      if (!this.map) {
        return;
      }
      if (data.length === 0) {
        return;
      }
      var callback = lang.hitch(this, function(evt) {
        if (evt.componentType !== 'series') {
          return;
        }

        var features = null;

        if (mode === 'field') {
          features = this.features;
        } else {
          //category: {category,valueFields,dataFeatures:[f1,f2...]}
          //count {fieldValue:value1,count:count1,dataFeatures:[f1,f2...]}
          var a = data[evt.dataIndex];
          if (a) {
            features = a.dataFeatures;
          }
        }

        if (!features) {
          return;
        }

        if (evt.type === 'mouseover') {
          this._mouseOverChartItem(features);
        } else if (evt.type === 'mouseout') {
          this._mouseOutChartItem(features);
        } else if (evt.type === 'click') {
          if (allowZoomToGraphic) {
            this._zoomToGraphics(features);
          }
        }
      });

      var events = [{
        name: 'mouseover',
        callback: callback
      }, {
        name: 'mouseout',
        callback: callback
      }];
      if (allowZoomToGraphic) {
        events.push({
          name: 'click',
          callback: callback
        });
      }
      events.forEach(lang.hitch(this, function(event) {
        chart.chart.on(event.name, event.callback);
      }));
    },

    //mock feature layer and value fields for statis data of framework data
    mockFeatureLayerAndChartConfigValueFieldsForServer: function(options) {
      var dataSchema = options.dataSchema;
      var statisticsFeatures = options.statisticsFeatures;
      var config = options.config;

      var originalFieldInfos = dataSchema.fields;
      // var groupByFields = dataSchema.groupByFields;

      var mockDefinition = {
        type: 'Table',
        fields: [] //{name,type,alias}
      };

      var mockConfig = lang.clone(config);

      var mode = config.mode;

      if (mode === 'category') {
        /*
        dataSchema: {
          groupByFields: ['POP_CLASS'],
          fields: [{
            name: 'POP',
            type: 'esriFieldTypeInteger',
            alias: 'POP'
          }, {
            name: 'POP_RANK',
            type: 'esriFieldTypeInteger',
            alias: 'POP_RANK'
          }, {
            name: 'POP_CLASS',
            type: 'esriFieldTypeString',
            alias: 'POP_CLASS'
          }]
        }

        config: {
          mode: 'category',
          categoryField: 'POP_CLASS',
          valueFields: ['POP', 'POP_RANK'],
          operation: 'sum'
        }

        mockDefinition: {
          type: 'Table',
          fields: [{
            name: 'POP_CLASS',
            type: 'esriFieldTypeString',
            alias: 'POP_CLASS'
          }, {
            name: 'POP_sum',
            type: 'esriFieldTypeDouble',
            alias: 'POP_sum'
          }, {
            name: 'POP_RANK_sum',
            type: 'esriFieldTypeDouble',
            alias: 'POP_RANK_sum'
          }]
        }

        mockConfig: {
          mode: 'category',
          categoryField: 'POP_CLASS',
          valueFields: ['POP_sum', 'POP_RANK_sum']
        }

        mockFeatures: [{POP_CLASS,POP_sum,POP_RANK_sum},...]
        */
        mockConfig.valueFields = [];

        mockDefinition.fields = config.valueFields.map(lang.hitch(this, function(valueField) {
          var operation = config.operation;
          if (operation === 'average') {
            operation = 'avg';
          }
          var mockFieldName = valueField + "_" + operation;
          var mockFieldAlias = valueField + "_" + operation;
          mockConfig.valueFields.push(valueField);
          var mockFieldInfo = {
            name: mockFieldName,
            type: "esriFieldTypeDouble",
            alias: mockFieldAlias
          };
          return mockFieldInfo;
        }));
        originalFieldInfos.some(lang.hitch(this, function(originalFieldInfo) {
          if (originalFieldInfo.name === config.categoryField) {
            mockDefinition.fields.push(originalFieldInfo);
            return true;
          } else {
            return false;
          }
        }));
      } else if (mode === 'count') {
        /*
        dataSchema: {
          groupByFields: ['POP_CLASS'],
          fields: [{
            name: 'POP',
            type: 'esriFieldTypeInteger',
            alias: 'POP'
          }, {
            name: 'POP_RANK',
            type: 'esriFieldTypeInteger',
            alias: 'POP_RANK'
          }, {
            name: 'POP_CLASS',
            type: 'esriFieldTypeString',
            alias: 'POP_CLASS'
          }]
        }

        config: {
          mode: 'count',
          categoryField: 'POP_CLASS'
        }

        mockDefinition: {
          type: 'Table',
          fields: [{
            name: 'POP_CLASS',
            type: 'esriFieldTypeString',
            alias: 'POP_CLASS'
          }, {
            name: 'POP_count',
            type: 'esriFieldTypeInteger',
            alias: 'count'
          }]
        }

        mockConfig: {
          mode: 'feature',
          labelField: 'POP_CLASS',
          valueFields: ['POP_count']
        }

        mockFeatures: [{POP_CLASS,POP_count},...]
        */
        this._mockModeForServer = true;
        mockConfig.mode = 'feature';
        mockConfig.labelField = config.categoryField;
        var countField = "count";
        mockConfig.valueFields = [countField];

        //POP_CLASS
        originalFieldInfos.some(lang.hitch(this, function(originalFieldInfo) {
          if (originalFieldInfo.name === config.categoryField) {
            mockDefinition.fields.push(originalFieldInfo);
            return true;
          } else {
            return false;
          }
        }));
        //POP_count
        mockDefinition.fields.push({
          name: countField,
          type: 'esriFieldTypeInteger',
          alias: this.nls.count
        });
      } else if (mode === 'field') {
        /*
        dataSchema: {
          groupByFields: [],
          fields: [{
            name: 'POP_RANK',
            type: 'esriFieldTypeInteger',
            alias: 'POP_RANK'
          }, {
            name: 'LABEL_FLAG',
            type: 'esriFieldTypeInteger',
            alias: 'LABEL_FLAG'
          }]
        }

        config: {
          mode: 'field',
          valueFields: ['POP_RANK', 'LABEL_FLAG'],
          operation: 'sum'
        }

        mockDefinition: {
          type: 'Table',
          fields: [{
            name: 'POP_sum',
            type: 'esriFieldTypeDouble',//same with original
            alias: 'POP_RANK_sum'
          }, {
            name: 'POP_RANK_sum',
            type: 'esriFieldTypeDouble',//same with original
            alias: 'LABEL_FLAG_sum'
          }]
        }

        mockConfig: {
          mode: 'field',
          valueFields: ['POP_sum', 'POP_RANK_sum'],
          operation: 'sum'
        }

        mockFeatures: [{POP_RANK_sum,LABEL_FLAG_sum}]//only one feature
        */

        mockConfig.valueFields = [];

        mockDefinition.fields = config.valueFields.map(lang.hitch(this, function(valueField) {
          var operation = config.operation;
          if (operation === 'average') {
            operation = 'avg';
          }
          var mockFieldName = valueField + "_" + operation;
          var mockFieldAlias = valueField + "_" + operation;
          mockConfig.valueFields.push(valueField);
          var mockFieldInfo = {
            name: mockFieldName,
            type: "esriFieldTypeDouble",
            alias: mockFieldAlias
          };
          return mockFieldInfo;
        }));
      }

      return this._getLoadedLayer(mockDefinition).then(lang.hitch(this, function(mockFeatureLayer) {
        return {
          featureLayer: mockFeatureLayer,
          features: statisticsFeatures,
          chartConfig: mockConfig
        };
      }));
    },

    _getLoadedLayer: function(featureLayerOrUrlOrLayerDefinition) {
      var def = new Deferred();
      var featureLayer = null;
      if (typeof featureLayerOrUrlOrLayerDefinition === 'string') {
        //url
        featureLayer = new FeatureLayer(featureLayerOrUrlOrLayerDefinition);
      } else {
        if (featureLayerOrUrlOrLayerDefinition.declaredClass === "esri.layers.FeatureLayer") {
          //FeatureLayer
          featureLayer = featureLayerOrUrlOrLayerDefinition;
        } else {
          //layerDefinition
          featureLayer = new FeatureLayer({
            layerDefinition: lang.clone(featureLayerOrUrlOrLayerDefinition),
            featureSet: null
          });
        }
      }

      if (featureLayer.loaded) {
        def.resolve(featureLayer);
      } else {
        this.own(on(featureLayer, 'load', lang.hitch(this, function() {
          def.resolve(featureLayer);
        })));
      }

      return def;
    },

    //return {type: type, labels:[], series: [{type: type, data: []}]}
    _createChartSeries: function(options, data) {
      var chartConfig = options.chartConfig;
      var mode = chartConfig.mode;
      if (mode === 'feature') {
        return this._getCategoryModeChartOptionsByStatisticsInfo(options, data);
      } else if (mode === 'category') {
        return this._getCategoryModeChartOptionsByStatisticsInfo(options, data);
      } else if (mode === 'count') {
        return this._getCountModeChartOptionsByStatisticsInfo(options, data);
      } else if (mode === 'field') {
        return this._getFieldModeChartOptionByStatisticsInfo(options, data);
      }
      return null;
    },

    //generate Chart.js's option
    _mapSettingConfigToChartOption: function(chartOptions, options, theme) {
      var chartConfig = options.chartConfig;

      var type = chartConfig.type;
      var mode = chartConfig.mode;

      var mixinOptions = {
        type: type,
        dataZoom: ["inside", "slider"],
        confine: true,
        backgroundColor: chartConfig.backgroundColor,
        legend: chartConfig.showLegend,
        theme: theme || "light",
        advanceOption: function(options) {
          //legend
          if (chartConfig.showLegend) {
            if (options.legend) {
              if (!options.legend.textStyle) {
                options.legend.textStyle = {};
              }
              options.legend.textStyle.color = chartConfig.legendTextColor;
              options.legend.textStyle.fontSize = chartConfig.legendTextSize;
            }
          }

          if (type === 'pie') {
            if (options.series && options.series.length > 0) {
              options.series.forEach(lang.hitch(this, function(item) {
                if (item.type === 'pie') {
                  if (!item.label) {
                    item.label = {};
                  }
                  if (!item.label.normal) {
                    item.label.normal = {};
                  }
                  item.label.normal.show = chartConfig.showDataLabel;
                  if (!item.label.normal.textStyle) {
                    item.label.normal.textStyle = {};
                  }
                  item.label.normal.textStyle.color = chartConfig.dataLabelColor;
                  item.label.normal.textStyle.fontSize = chartConfig.dataLabelSize;
                }
              }));
            }
          } else {
            //xAxis
            if (!options.xAxis) {
              options.xAxis = {};
            }
            // options.xAxis.show = displayConfig.showHorizontalAxis;
            if (!options.xAxis.axisLabel) {
              options.xAxis.axisLabel = {};
            }
            if (!options.xAxis.axisLabel.textStyle) {
              options.xAxis.axisLabel.textStyle = {};
            }
            options.xAxis.axisLabel.textStyle.color = chartConfig.horizontalAxisTextColor;
            options.xAxis.axisLabel.textStyle.fontSize = chartConfig.horizontalAxisTextSize;

            //yAxis
            if (!options.yAxis) {
              options.yAxis = {};
            }
            // options.yAxis.show = displayConfig.showVerticalAxis;
            if (!options.yAxis.axisLabel) {
              options.yAxis.axisLabel = {};
            }
            if (!options.yAxis.axisLabel.textStyle) {
              options.yAxis.axisLabel.textStyle = {};
            }
            options.yAxis.axisLabel.textStyle.color = chartConfig.verticalAxisTextColor;
            options.yAxis.axisLabel.textStyle.fontSize = chartConfig.verticalAxisTextSize;
          }
        }
      };

      if (type === 'pie' && mode !== 'field') {
        var seriesStyle = chartConfig.seriesStyle;
        if (seriesStyle && seriesStyle.styles && seriesStyle.styles[0]) {
          var matchStyle = seriesStyle.styles[0].style;
          if (matchStyle && Array.isArray(matchStyle.color)) {
            var colors = lang.clone(matchStyle.color);
            if (colors.length === 2) {
              colors = this._getColors(lang.clone(matchStyle.color), 6);
            }
            mixinOptions.color = colors;
          }
        }
      }
      if (type === 'pie') {
        mixinOptions.innerRadius = chartConfig.innerRadius;
        mixinOptions.labelLine = !!chartConfig.showDataLabel;
      }

      var axisTypes = ['column', 'bar', 'line'];

      if (axisTypes.indexOf(type) > -1) {
        //stack
        if (!chartConfig.stack) {
          chartConfig.stack = false;
        }
        //area
        if (type === 'line' && !chartConfig.area) {
          chartConfig.area = false;
        }

        if (type === 'line') {
          mixinOptions.area = chartConfig.area;
        }

        if ((type === 'column' || type === 'bar') || (type === 'line' && chartConfig.area)) {
          mixinOptions.stack = chartConfig.stack;
        }
      }

      lang.mixin(chartOptions, mixinOptions);

      if (type !== 'pie') {
        chartOptions.axisPointer = true;
        chartOptions.scale = false;
        chartOptions.hidexAxis = !chartConfig.showHorizontalAxis;
        chartOptions.hideyAxis = !chartConfig.showVerticalAxis;
      }

      return chartOptions;
    },

    _getColors: function(originColors, count) {
      var colors = [];

      if (originColors.length === 2) {
        //gradient colors
        colors = this._createGradientColors(originColors[0],
          originColors[originColors.length - 1],
          count);
      } else {
        var a = Math.ceil(count / originColors.length);
        for (var i = 0; i < a; i++) {
          colors = colors.concat(originColors);
        }
        colors = colors.slice(0, count);
      }

      return colors;
    },

    _createGradientColors: function(firstColor, lastColor, count) {
      var colors = [];
      var c1 = new Color(firstColor);
      var c2 = new Color(lastColor);
      var deltaR = (c2.r - c1.r) / count;
      var deltaG = (c2.g - c1.g) / count;
      var deltaB = (c2.b - c1.b) / count;
      var c = new Color();
      var r = 0;
      var g = 0;
      var b = 0;
      for (var i = 0; i < count; i++) {
        r = parseInt(c1.r + deltaR * i, 10);
        g = parseInt(c1.g + deltaG * i, 10);
        b = parseInt(c1.b + deltaB * i, 10);
        c.setColor([r, g, b]);
        colors.push(c.toHex());
      }
      return colors;
    },

    _getFieldModeChartOptionByStatisticsInfo: function(options, data) {
      //data: [{label:fieldName,value:,fieldValue}]
      var chartConfig = options.chartConfig;
      var type = chartConfig.type;
      var featureLayerForChartSymbologyChart = options.featureLayerForChartSymbologyChart;
      var chartOptions = {
        type: type,
        labels: [],
        series: [{
          type: type,
          data: []
        }]
      };

      data.forEach(lang.hitch(this, function(item) {
        var _originLabel = item.label;
        var label = this._getFieldAlias(item.label);
        var value = item.value;

        chartOptions.labels.push(label);
        var itemObj = {
          item: item,
          value: value,
          label: label,
          _originLabel: _originLabel
        };
        var dataItem = this._getSerieDataItem(itemObj, chartConfig, featureLayerForChartSymbologyChart);
        chartOptions.series[0].data.push(dataItem);
      }));
      chartOptions.series = this._assignColorsToSeries(chartConfig, chartOptions.series);
      return chartOptions;
    },

    //{type:'', labels:[], series:[{type:'', data:[]}]}
    _getCountModeChartOptionsByStatisticsInfo: function(options, data) {
      //data: [{fieldValue:value1,count:count1,dataFeatures:[f1,f2...]}]
      var chartConfig = options.chartConfig;
      var type = chartConfig.type;
      var featureLayerForChartSymbologyChart = options.featureLayerForChartSymbologyChart;
      //-- if has splitField --
      var hasSplitField = false;

      if (data.length > 0) {
        hasSplitField = data.every(function(item) {
          return !!item.splitedValueFields;
        });
      }

      if (hasSplitField) {
        return this._getSplitedSeriesForCategoryOrCountMode(data, options, chartConfig);
      }
      //type: bar, line, pie, not support radar for count mode
      var chartOptions = {
        type: type,
        labels: [],
        series: [{
          type: type,
          data: []
        }]
      };

      data.forEach(lang.hitch(this, function(item) {
        var value = item.count;
        var label = item.fieldValue;
        var _originLabel = item.originValue;
        chartOptions.labels.push(label);
        var itemObj = {
          item: item,
          value: value,
          label: label,
          _originLabel: _originLabel
        };
        var dataItem = this._getSerieDataItem(itemObj, chartConfig, featureLayerForChartSymbologyChart);
        chartOptions.series[0].data.push(dataItem);
      }));
      chartOptions.series = this._assignColorsToSeries(chartConfig, chartOptions.series);
      return chartOptions;
    },

    _getCategoryModeChartOptionsByStatisticsInfo: function(options, data) {
      //data: [{category:'a',valueFields:[10,100,2],dataFeatures:[f1,f2...]}]

      var chartConfig = options.chartConfig;
      var type = chartConfig.type;
      var valueFields = chartConfig.valueFields;

      var valueAliases = this._getFieldAliasObjactArray(valueFields);
      var chartOptions = null;

      var featureLayerForChartSymbologyChart = options.featureLayerForChartSymbologyChart;
      //-- if has splitField --
      var hasSplitField = false;
      if (data.length > 0) {
        hasSplitField = data.every(function(item) {
          return !!item.splitedValueFields;
        });
      }

      if (hasSplitField) {
        return this._getSplitedSeriesForCategoryOrCountMode(data, options, chartConfig);
      }

      // --special type radar --
      if (type === 'radar') {
        var indicator = valueAliases.map(function(item) {
          return {
            name: item.alias
          };
        });
        var series = this._getSeriesOfRadar(data);
        chartOptions = {
          type: type,
          indicator: indicator,
          series: series
        };
        return chartOptions;
      }

      // --type: bar line pie--
      chartOptions = {
        type: type,
        labels: [],
        series: []
      };

      chartOptions.series = valueAliases.map(lang.hitch(this, function(valueFieldAlias) {
        var _originName = valueFieldAlias.name;

        var item = {
          name: valueFieldAlias.alias,
          _originName: _originName,
          type: type,
          data: []
        };
        return item;
      }));

      data.forEach(lang.hitch(this, function(item) {
        //item: {category:'a',valueFields:[10,100,2]
        var label = item.category;
        var _originLabel = item.originValue;
        chartOptions.labels.push(label);
        for (var i = 0; i < item.valueFields.length; i++) {
          var value = item.valueFields[i];
          var itemObj = {
            item: item,
            value: value,
            label: label,
            _originLabel: _originLabel
          };
          var dataItem = this._getSerieDataItem(itemObj, chartConfig, featureLayerForChartSymbologyChart);
          chartOptions.series[i].data.push(dataItem);
        }
      }));

      chartOptions.series = this._assignColorsToSeries(chartConfig, chartOptions.series);
      return chartOptions;
    },

    _getMatchingStyle: function(name, seriesStyle) {
      var style = null;
      var styles = seriesStyle.styles;
      if (!styles || !styles[0]) {
        return style;
      }
      if (name === '') {
        return style;
      }
      styles.forEach(function(item) {
        if (item.name === name) {
          style = item.style;
        }
      });
      return style;
    },

    _setStyleToSerieDataItem: function(matchStyle, item) {
      if (!item.itemStyle) {
        item.itemStyle = {};
      }
      if (!item.itemStyle.normal) {
        item.itemStyle.normal = {};
      }
      if (matchStyle && typeof matchStyle.color !== 'undefined') {
        if (Array.isArray(matchStyle.color)) {
          item.itemStyle.normal.color = matchStyle.color[0];
        } else {
          item.itemStyle.normal.color = matchStyle.color;
        }
      }
      if (matchStyle && typeof matchStyle.opacity !== 'undefined') {
        item.itemStyle.normal.opacity = (1 - parseFloat(matchStyle.opacity / 10));
      }
      return item;
    },

    _setStyleToSerie: function(matchStyle, serie, area) {
      if (!serie.itemStyle) {
        serie.itemStyle = {};
      }
      if (!serie.itemStyle.normal) {
        serie.itemStyle.normal = {};
      }
      if (matchStyle && typeof matchStyle.color !== 'undefined') {
        if (Array.isArray(matchStyle.color)) {
          serie.itemStyle.normal.color = matchStyle.color[0];
        } else {
          serie.itemStyle.normal.color = matchStyle.color;
        }
      }
      if (matchStyle && typeof matchStyle.opacity !== 'undefined') {
        if (area) {
          if (!serie.areaStyle) {
            serie.areaStyle = {};
          }
          if (!serie.areaStyle.normal) {
            serie.areaStyle.normal = {};
          }
          serie.areaStyle.normal.opacity = (1 - parseFloat(matchStyle.opacity / 10));
        } else {
          serie.itemStyle.normal.opacity = (1 - parseFloat(matchStyle.opacity / 10));
        }
      }
      return serie;
    },

    _assignColorsToSeries: function(chartConfig, series) {
      var seriesStyle = chartConfig.seriesStyle;
      if (!seriesStyle || !seriesStyle.styles || !seriesStyle.styles[0]) {
        return series;
      }
      var mode = chartConfig.mode;
      //when dsta source is extra static data,
      //For count mode, mock as feature mode
      if (this._mockModeForServer && mode === 'feature') {
        mode = 'count';
        this._mockModeForServer = false;
      }
      var area = chartConfig.area;
      return series.map(function(serie) {
        var matchStyle = null;
        var type = serie.type;

        if (mode === 'field') {
          if (type === 'line') {
            matchStyle = seriesStyle.styles[0].style;
            serie = this._setStyleToSerie(matchStyle, serie, area);
          } else {
            var data = serie.data;
            if (data && data[0]) {
              serie.data = data.map(function(item) {
                matchStyle = this._getMatchingStyle(item._originName, seriesStyle);
                return this._setStyleToSerieDataItem(matchStyle, item);
              }.bind(this));
            }
          }
        } else {
          if (type === 'column' || type === 'bar' || type === 'line') {
            if (mode === 'count') {
              matchStyle = seriesStyle.styles[0].style;
              serie = this._setStyleToSerie(matchStyle, serie, area);
            } else {
              if (typeof serie.name !== 'undefined') {
                matchStyle = this._getMatchingStyle(serie._originName, seriesStyle);
                if (matchStyle) {
                  serie = this._setStyleToSerie(matchStyle, serie, area);
                }
              }
            }
          }
          //else pie color array
        }
        return serie;
      }.bind(this));
    },

    _getSplitedSeriesForCategoryOrCountMode: function(data, options, chartConfig) {
      var chartType = chartConfig.type;
      var featureLayerForChartSymbologyChart = options.featureLayerForChartSymbologyChart;
      var chartOptions = {
        type: chartType,
        labels: [],
        series: []
      };
      var allSplitedFields = [];
      data.forEach(function(item) {
        var splitedValueFields = item.splitedValueFields;
        if (splitedValueFields) {
          var fields = splitedValueFields.map(function(splitedValueField) {
            return {
              field: splitedValueField.field,
              originField: splitedValueField.originField
            };
          });
          allSplitedFields = allSplitedFields.concat(fields);
        }
      });
      var uniqueSeplitedFields = this._removeDuplicateElementForObjArray(allSplitedFields);

      chartOptions.series = uniqueSeplitedFields.map(lang.hitch(this, function(uniqueSeplitedField) {
        var dataItem = [];
        for (var i = 0; i < data.length; i++) {
          dataItem[i] = null;
        }
        var item = {
          name: uniqueSeplitedField.field,
          _originName: uniqueSeplitedField.originField,
          type: chartType,
          data: dataItem
        };
        return item;
      }));

      data.forEach(lang.hitch(this, function(item, i) {
        //item: {category:'a',valueFields:[10,100,2] or {fieldValue:value1,count:count1}
        var label = '';
        if (item.category) {
          label = item.category;
        } else if (item.fieldValue) {
          label = item.fieldValue;
        }
        var _originLabel = item.originValue;

        chartOptions.labels.push(label);

        item.splitedValueFields.forEach(function(svf) {
          chartOptions.series.forEach(function(serie) {
            if (serie._originName === svf.originField) {
              var value = svf.value;
              var itemObj = {
                item: item,
                value: value,
                label: label,
                _originLabel: _originLabel
              };
              var dataItem = this._getSerieDataItem(itemObj, chartConfig,
                featureLayerForChartSymbologyChart);
              serie.data[i] = dataItem;
            }
          }.bind(this));
        }.bind(this));
      }));
      return chartOptions;
    },

    _getSeriesOfRadar: function(data) {
      data = data.map(function(item) {
        return {
          name: item.category,
          value: item.valueFields
        };
      });
      return [{
        type: 'radar',
        data: data
      }];
    },

    _getSerieDataItem: function(itemObj, chartConfig, featureLayerForChartSymbologyChart) {
      var item = itemObj.item;
      var label = itemObj.label;
      var value = itemObj.value;
      var _originLabel = itemObj._originLabel;

      var useLayerSymbology = false;
      var seriesStyle = chartConfig.seriesStyle;
      if (seriesStyle) {
        useLayerSymbology = seriesStyle.useLayerSymbology;
      }
      var color;
      if (useLayerSymbology) {
        var features = item.dataFeatures;
        color = this._getSymbolColorForDataItem(featureLayerForChartSymbologyChart, features);
      }

      var dataItem = {};
      dataItem.name = label;
      dataItem.value = value;
      dataItem._originName = _originLabel;

      if (color) {
        dataItem.itemStyle = {
          normal: {
            color: color
          },
          emphasis: {
            color: color
          }
        };
      }
      return dataItem;
    },

    _getSymbolColorForDataItem: function(featureLayer, features) {
      var color = false;
      if (!featureLayer) {
        return color;
      }
      var renderer = featureLayer.renderer;
      var feature = features[0];
      if (!feature) {
        return color;
      }
      color = this._getColorForFeature(renderer, feature);
      return color;
    },

    _getColorForFeature: function(renderer, feature) {
      var color = false;
      var visualVariables = renderer.visualVariables;
      var visVar = this._getVisualVariableByType('colorInfo', visualVariables);
      if (visVar) {
        var featureColor = renderer.getColor(feature, {
          colorInfo: visVar
        });
        if (featureColor) {
          color = this._convertToEchartsRbga(featureColor);
        }
      } else {
        var symbol = renderer.getSymbol(feature);
        if (symbol && typeof symbol.color !== 'undefined') {
          color = this._convertToEchartsRbga(symbol.color);
        }
      }
      return color;
    },

    /*handle series data color for use layer symbol*/
    _convertToEchartsRbga: function(symbolColor) {
      if (!symbolColor || typeof symbolColor.r === 'undefined') {
        return symbolColor;
      }
      symbolColor = JSON.parse(JSON.stringify(symbolColor));
      var color = 'rgba(';
      color += symbolColor.r + ',';
      color += symbolColor.g + ',';
      color += symbolColor.b + ',';
      color += symbolColor.a + ')';
      return color;
    },

    _getVisualVariableByType: function(type, visualVariables) {
      // we could also use esri.renderer.Renderer.getVisualVariablesForType for renderers
      if (visualVariables) {
        var visVars = visualVariables.filter(function(visVar) {
          return (visVar.type === type && !visVar.target);
        });
        if (visVars.length) {
          return visVars[0];
        } else {
          return null;
        }
      }
      return null;
    },

    _mouseOverChartItem: function(features) {
      this._removeTempGraphics();
      this._mouseOutChartItem(features);
      //We need to store the original feature symbol because we will use it in mouse out event.
      features.forEach(lang.hitch(this, function(feature) {
        feature._originalSymbol = feature.symbol;
      }));

      var isVisible = this.featureLayer && this.featureLayer.getMap() && this.featureLayer.visible;
      if (!isVisible) {
        return;
      }

      var geoType = jimuUtils.getTypeByGeometryType(this.featureLayer.geometryType);
      var symbol = null;
      if (geoType === 'point') {
        symbol = this._getHighLightMarkerSymbol();
        this.tempGraphics = [];
        features.forEach(lang.hitch(this, function(feature) {
          var g = new Graphic(feature.geometry, symbol);
          this.tempGraphics.push(g);
          this.featureLayer.add(g);
        }));
      } else if (geoType === 'polyline') {
        symbol = this._getHighLightLineSymbol(this.highLightColor);

        features.forEach(lang.hitch(this, function(feature) {
          feature.setSymbol(symbol);
        }));
      } else if (geoType === 'polygon') {

        var selectedFeatures = this.featureLayer.getSelectedFeatures() || [];

        features.forEach(lang.hitch(this, function(feature) {
          var isSelectedFeature = selectedFeatures.indexOf(feature) >= 0;
          var highLightSymbol = this._getHighLightFillSymbol(this.featureLayer, feature, isSelectedFeature);
          feature.setSymbol(highLightSymbol);
        }));

        //The outline of these features maybe overlapped by others,
        //so we need to put these features at the end of the featureLayer
        if (this.features.length !== features.length && geoType === 'polygon') {
          features.forEach(lang.hitch(this, function(feature) {
            this.featureLayer.remove(feature);
          }));
          features.forEach(lang.hitch(this, function(feature) {
            this.featureLayer.add(feature);
          }));
        }
      }
    },

    _mouseOutChartItem: function(features) {
      this._removeTempGraphics();

      // if(!this.featureLayer){
      //   return;
      // }

      //Restore feature's original symbol.
      features.forEach(lang.hitch(this, function(feature) {
        var _originalSymbol = feature._originalSymbol || null;
        feature.setSymbol(_originalSymbol);
      }));
    },

    _removeTempGraphics: function() {
      if (this.featureLayer && this.tempGraphics && this.tempGraphics.length > 0) {
        while (this.tempGraphics.length > 0) {
          this.featureLayer.remove(this.tempGraphics[0]);
          this.tempGraphics.splice(0, 1);
        }
      }
      this.tempGraphics = null;
    },

    _zoomToGraphics: function(features) {
      if (!this.map) {
        return;
      }

      var isVisible = this.featureLayer && this.featureLayer.visible;
      if (!isVisible) {
        return;
      }

      if (features && features.length > 0) {
        var extent = null;
        try {
          //some graphics maybe don't have geometry, so need to filter graphics here by geometry
          var fs = features.filter(function(f) {
            return !!f.geometry;
          });
          if (fs.length > 0) {
            extent = graphicsUtils.graphicsExtent(fs);
          }
        } catch (e) {
          console.error(e);
        }

        if (extent) {
          this.map.setExtent(extent.expand(1.4));
        } else {
          var firstFeature = features[0];
          var geometry = firstFeature && firstFeature.geometry;

          if (geometry) {
            var singlePointFlow = lang.hitch(this, function(centerPoint) {
              var maxLevel = this.map.getNumLevels();
              var currentLevel = this.map.getLevel();
              var level2 = Math.floor(maxLevel * 2 / 3);
              var zoomLevel = Math.max(currentLevel, level2);
              this.map.setLevel(zoomLevel).then(lang.hitch(this, function() {
                this.map.centerAt(centerPoint);
              }));
            });

            if (geometry.type === 'point') {
              singlePointFlow(geometry);
            } else if (geometry.type === 'multipoint') {
              if (geometry.points.length === 1) {
                singlePointFlow(geometry.getPoint(0));
              }
            }
          }
        }
      }
    },

    _isNumberField: function(fieldName) {
      var numberTypes = ['esriFieldTypeSmallInteger',
        'esriFieldTypeInteger',
        'esriFieldTypeSingle',
        'esriFieldTypeDouble'
      ];
      var isNumber = this.featureLayer.fields.some(lang.hitch(this, function(fieldInfo) {
        return fieldInfo.name === fieldName && numberTypes.indexOf(fieldInfo.type) >= 0;
      }));
      return isNumber;
    },

    _getHighLightMarkerSymbol: function() {
      // var sym = symbolJsonUtils.fromJson(this.config.symbol);
      // var size = Math.max(sym.size || 0, sym.width || 0, sym.height, 18);
      // size += 1;

      var size = 30;

      var symJson = {
        "color": [255, 255, 255, 0],
        "size": 18,
        "angle": 0,
        "xoffset": 0,
        "yoffset": 0,
        "type": "esriSMS",
        "style": "esriSMSSquare",
        "outline": {
          "color": [0, 0, 128, 255],
          "width": 0.75,
          "type": "esriSLS",
          "style": "esriSLSSolid"
        }
      };
      var symbol = symbolJsonUtils.fromJson(symJson);
      symbol.setSize(size);
      symbol.outline.setColor(new Color(this.highLightColor));

      return symbol;
    },

    _getHighLightLineSymbol: function( /*optional*/ highLightColor) {
      var selectedSymJson = {
        "color": [0, 255, 255, 255],
        "width": 1.5,
        "type": "esriSLS",
        "style": "esriSLSSolid"
      };
      var symbol = symbolJsonUtils.fromJson(selectedSymJson);
      symbol.setColor(new Color(highLightColor || this.highLightColor));
      return symbol;
    },

    _getDefaultHighLightFillSymbol: function() {
      var symbolJson = {
        "color": [0, 255, 255, 128],
        "outline": {
          "color": [0, 255, 255, 255],
          "width": 1.5,
          "type": "esriSLS",
          "style": "esriSLSSolid"
        },
        "type": "esriSFS",
        "style": "esriSFSSolid"
      };
      var symbol = symbolJsonUtils.fromJson(symbolJson);
      symbol.outline.setColor(new Color(this.highLightColor));
      return symbol;
    },

    _getSymbolByRenderer: function(renderer, feature) {
      var symbol = this._getDefaultHighLightFillSymbol();
      var visualVariables = renderer.visualVariables;
      var visVar = this._getVisualVariableByType('colorInfo', visualVariables);
      if (visVar) {
        var color = renderer.getColor(feature, {
          colorInfo: visVar
        });
        if (color) {
          color = lang.clone(color);
          symbol.setColor(color);
        }
      } else {
        symbol = renderer.getSymbol(feature);
      }
      return symbol;
    },

    _getHighLightFillSymbol: function(featureLayer, feature, isSelectedFeature) {
      var highLightSymbol = null;
      var currentSymbol = feature.symbol;
      var renderer = featureLayer.renderer;
      if (!currentSymbol && renderer) {
        currentSymbol = this._getSymbolByRenderer(renderer, feature);
      }
      if (currentSymbol && typeof currentSymbol.setOutline === 'function') {
        highLightSymbol = symbolJsonUtils.fromJson(currentSymbol.toJson());
        var outlineWidth = 1.5;
        if (currentSymbol.outline) {
          if (currentSymbol.outline.width > 0) {
            outlineWidth = currentSymbol.outline.width + 1;
          }
        }
        //if feature in feature selection, set red color for selected features
        //if feature is not in feature selection, set selection like symbol
        var highLightColor = isSelectedFeature ? "#ff0000" : "#00ffff";
        var outline = this._getHighLightLineSymbol(highLightColor);
        outline.setWidth(outlineWidth);
        highLightSymbol.setOutline(outline);
      } else {
        highLightSymbol = this._getDefaultHighLightFillSymbol();
      }
      return highLightSymbol;
    },

    _getFieldAliasArray: function(fieldNames) {
      var results = fieldNames.map(lang.hitch(this, function(fieldName) {
        return this._getFieldAlias(fieldName);
      }));
      return results;
    },

    _getFieldAliasObjactArray: function(fieldNames) {
      var results = fieldNames.map(lang.hitch(this, function(fieldName) {
        return {
          name: fieldName,
          alias: this._getFieldAlias(fieldName)
        };
      }));
      return results;
    },

    _getFieldAlias: function(fieldName) {
      var fieldAlias = fieldName;
      var fieldInfo = this._getFieldInfo(fieldName);
      if (fieldInfo) {
        fieldAlias = fieldInfo.alias || fieldAlias;
      }
      return fieldAlias;
    },

    _getFieldInfo: function(fieldName) {
      if (this.featureLayer) {
        var fieldInfos = this.featureLayer.fields;
        for (var i = 0; i < fieldInfos.length; i++) {
          if (fieldInfos[i].name === fieldName) {
            return fieldInfos[i];
          }
        }
      }
      return null;
    },

    //Removing duplicate elements from an object array
    _removeDuplicateElementForObjArray: function(array) {
      if (!Array.isArray(array)) {
        return array;
      }
      var n = [];
      n.push(array[0]);
      array.forEach(function(item) {
        var isInArray = n.some(function(e) {
          return jimuUtils.isEqual(e, item);
        });

        if (!isInArray) {
          n.push(item);
        }
      });

      return n;
    }
  });
});