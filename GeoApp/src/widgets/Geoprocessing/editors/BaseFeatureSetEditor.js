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
  'dojo/_base/html',
  'dojo/on',
  'jimu/dijit/ViewStack',
  '../BaseEditor',
  './SelectFeatureSetFromSelection'
],
function(declare, lang, html, on, ViewStack, BaseEditor, SelectFeatureSetFromSelection) {
  var clazz = declare([BaseEditor], {
    editorName: 'BaseFeatureSetEditor',
    viewStack: null,
    activeViewIndex: 0,

    postCreate: function(){
      this.inherited(arguments);

      this.viewStack = new ViewStack({
        viewType: 'dom',
        views: [this.inputNode, this.featuresetNode]
      });
      html.place(this.viewStack.domNode, this.domNode);
      this.viewStack.startup();
      this.switchView(0);
    },

    switchView: function(idx) {
      this.activeViewIndex = idx;
      this.viewStack.switchView(idx);
    },

    setFeatureSet: function(featureset, layer) {
      //jshint unused:false
      if(featureset.features && featureset.features.length > 0) {
        html.empty(this.featuresetNode);
        this.featuresetDijit = new SelectFeatureSetFromSelection({
          featureset: featureset,
          nls: this.nls
        });
        html.place(this.featuresetDijit.domNode, this.featuresetNode);
        this.featuresetDijit.startup();

        this.own(on(this.featuresetDijit, 'close', lang.hitch(this, function(){
          this.switchView(0);
        })));

        this.switchView(1);
      }
    },

    getFeatureSet: function() {
      if(this.featuresetDijit) {
        return this.featuresetDijit.getValue();
      }
      return null;
    }
  });

  return clazz;
});
