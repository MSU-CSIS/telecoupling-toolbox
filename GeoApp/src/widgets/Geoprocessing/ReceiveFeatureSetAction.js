
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

define([
  'dojo/_base/declare',
  'dojo/Deferred',
  'jimu/BaseFeatureAction',
  'jimu/WidgetManager',
  'jimu/utils'
], function(declare, Deferred, BaseFeatureAction, WidgetManager, utils){
  var clazz = declare(BaseFeatureAction, {
    map: null,
    iconClass: 'icon-set-as-input',

    constructor: function(){
      this.label = this.label + this.appConfig.getConfigElementById(this.widgetId).label;
    },

    isFeatureSupported: function(featureSet){
      var gpConfig = this.appConfig.getConfigElementById(this.widgetId).config;
      if(!gpConfig || !gpConfig.inputParams || gpConfig.inputParams.length === 0){
        return false;
      }

      return gpConfig.inputParams.filter(function(param){
        return param.dataType === 'GPFeatureRecordSetLayer' && param.defaultValue &&
          utils.getTypeByGeometryType(param.defaultValue.geometryType) === featureSet.geometryType;
      }).length > 0;
    },

    onExecute: function(featureSet, layer){
      //jshint unused:false
      var def = new Deferred();
      WidgetManager.getInstance().triggerWidgetOpen(this.widgetId)
      .then(function(widget) {
        widget.useSelectionAsInput(featureSet, layer);
        def.resolve();
      });

      return def.promise;
    }
  });
  return clazz;
});
