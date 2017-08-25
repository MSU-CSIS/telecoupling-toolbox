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

define([
  'dojo/_base/array',
  'dojo/promise/all',
  'dojo/Deferred'
], function(array, all, Deferred) {
  var mo = {};

  mo.getLayerInfoArray = function(layerInfosObject){
    var retDef = new Deferred();

    var layerInfos = [];
    layerInfosObject.traversal(function(layerInfo){
      layerInfos.push(layerInfo);
    });

    var defs = array.map(layerInfos, function(layerInfo){
      return layerInfo.getLayerType();
    });

    all(defs).then(function(layerTypes){
      var resultArray = [];
      array.forEach(layerTypes, function(layerType, i){
        if((layerType === 'FeatureLayer')) {
          resultArray.push(layerInfos[i]);
        }
      });
      retDef.resolve(resultArray);
    });

    return retDef;
  };

  return mo;
});
