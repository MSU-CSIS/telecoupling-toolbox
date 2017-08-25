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
    'dojo/_base/declare',
    "dojo/_base/lang",
    'dijit/_WidgetsInTemplateMixin',
    'jimu/BaseWidgetSetting',
    'jimu/dijit/CheckBox'
  ],
  function(declare, lang, _WidgetsInTemplateMixin, BaseWidgetSetting) {
    return declare([BaseWidgetSetting, _WidgetsInTemplateMixin], {
      baseClass: 'jimu-widget-share-setting',

      postMixInProperties: function() {
        this.inherited(arguments);
        this.nls.email = window.jimuNls.shareLink.email;
        this.nls.facebook = window.jimuNls.shareLink.facebook;
        this.nls.googlePlus = window.jimuNls.shareLink.googlePlus;
        this.nls.twitter = window.jimuNls.shareLink.twitter;
      },

      startup: function() {
        this.inherited(arguments);
        if (!this.config) {
          this.config = {};
        }
        this.setConfig(this.config);
      },

      setConfig: function(config) {
        this.config = config;

        this.email.setValue(true);
        this.facebook.setValue(true);
        this.twitter.setValue(true);
        this.googlePlus.setValue(true);
        if (config.socialMedias) {
          if (false === config.socialMedias.email) {
            this.email.setValue(false);
          }
          if (false === config.socialMedias.facebook) {
            this.facebook.setValue(false);
          }
          if (false === config.socialMedias.twitter) {
            this.twitter.setValue(false);
          }
          if (false === config.socialMedias.googlePlus) {
            this.googlePlus.setValue(false);
          }
        }
      },

      getConfig: function() {
        var socialMedias = {};
        socialMedias = lang.mixin(socialMedias, this.config.socialMedias);
        if (this.email) {
          socialMedias.email = this.email.getValue();
        }
        if (this.facebook) {
          socialMedias.facebook = this.facebook.getValue();
        }
        if (this.twitter) {
          socialMedias.twitter = this.twitter.getValue();
        }
        if (this.googlePlus) {
          socialMedias.googlePlus = this.googlePlus.getValue();
        }
        this.config.socialMedias = socialMedias;
        return this.config;
      }
    });
  });