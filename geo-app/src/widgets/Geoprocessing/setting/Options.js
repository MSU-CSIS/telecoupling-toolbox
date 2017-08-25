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
  'dojo/text!./Options.html',
  'dojo/_base/lang',
  'dojo/Evented',
  'dojo/on',
  'dijit/_WidgetBase',
  'dijit/_TemplatedMixin',
  'dijit/_WidgetsInTemplateMixin',
  '../utils',
  'dijit/form/TextBox',
  'jimu/dijit/CheckBox'
],
function(declare, template, lang, Evented, on, _WidgetBase, _TemplatedMixin,
  _WidgetsInTemplateMixin, gputils) {
  return declare([_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin, Evented], {
    baseClass: 'jimu-widget-setting-gp-options',
    templateString: template,

    setConfig: function(config){
      this.config = config;
      this.helpUrl.setValue(config.helpUrl);
      if(!gputils.allowShareResult(config)){
        this.shareResults.setValue(false);
        this.shareResults.setStatus(false);
      }else{
        this.shareResults.setStatus(true);
        this.shareResults.setValue(Boolean(config.shareResults));
      }

      if(config.serverInfo.hasResultMapServer){
        this.useResultMapServer.setStatus(true);
        this.useResultMapServer.setValue(Boolean(config.useResultMapServer));
        this.setUserResultMapServer(this.useResultMapServer.getValue());
        this.own(on(this.useResultMapServer, 'change', lang.hitch(this, function(checked) {
          this.setUserResultMapServer(checked);
          this.emit('result-map-service', checked);
        })));
      }else{
        this.useResultMapServer.setValue(false);
        this.useResultMapServer.setStatus(false);
      }

      this.showExport.setValue(Boolean(config.showExportButton));
      this.dynamicSchema.setValue(Boolean(config.useDynamicSchema));
    },

    setUserResultMapServer: function(checked) {
      if (checked) {
        this.shareResults.setValue(true);
        this.shareResults.setStatus(false);
      } else {
        this.shareResults.setStatus(true);
      }
    },

    acceptValue: function(){
      if(!this.config) {
        return;
      }
      this.config.helpUrl = this.helpUrl.getValue();
      if(this.useResultMapServer.status){
        this.config.useResultMapServer = this.useResultMapServer.getValue();
      }
      this.config.shareResults = this.shareResults.getValue();
      this.config.showExportButton = this.showExport.getValue();
      this.config.useDynamicSchema = this.dynamicSchema.getValue();
    }
  });
});
