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
  'dojo/_base/event',
  'dojo/on',
  'dojo/dom-geometry',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dojo/text!./FeatureItem.html',
  'jimu/utils',
  'jimu/symbolUtils',
  'jimu/dijit/FeatureActionPopupMenu',
  'jimu/featureActions/PanTo',
  'jimu/featureActions/ShowPopup'
], function(declare, lang, html, Event, on, domGeom, _WidgetBase, _TemplatedMixin,
template, jimuUtils, symbolUtils, PopupMenu, PanToAction, ShowPopupAction) {
  return declare([_WidgetBase, _TemplatedMixin], {
    baseClass: 'graphic-item',
    templateString: template,

    allowExport: false,

    postCreate: function() {
      this.inherited(arguments);

      // create icon
      var symbol;
      if(this.featureLayer && this.featureLayer.renderer && this.featureLayer.renderer.getSymbol) {
        symbol = this.featureLayer.renderer.getSymbol(this.graphic);
      } else if (this.graphic.symbol) {
        symbol = this.graphic.symbol;
      }

      if(symbol) {
        var iconDiv = symbolUtils.createSymbolNode(symbol, {width: 36, height: 36});
        html.place(iconDiv, this.iconNode);
      }

      this.popupMenu = PopupMenu.getInstance();
      this.nameNode.innerHTML = this.graphic.attributes[this.displayField] ||
          this.graphic.attributes[this.objectIdField];
      this.nameNode.title = this.graphic.attributes[this.displayField] ||
          this.graphic.attributes[this.objectIdField];

      this.own(on(this.actionBtn, 'click', lang.hitch(this, this._showActions)));

      this.own(on(this.iconNode, 'click', lang.hitch(this, this._highlight)));
      this.own(on(this.nameNode, 'click', lang.hitch(this, this._highlight)));
    },

    _highlight: function() {
      var featureSet = jimuUtils.toFeatureSet([this.graphic]);
      var panToAction = new PanToAction({
        map: this.map
      });
      var showPopupAction = new ShowPopupAction({
        map: this.map
      });

      showPopupAction.onExecute(featureSet);
      panToAction.onExecute(featureSet);
    },

    _showActions: function(event) {
      Event.stop(event);

      var featureSet = jimuUtils.toFeatureSet([this.graphic]);
      this.popupMenu.prepareActions(featureSet, this.allowExport).then(lang.hitch(this, function() {
        var position = domGeom.position(event.target);

        this.popupMenu.show(position);
      }));
    }
  });
});