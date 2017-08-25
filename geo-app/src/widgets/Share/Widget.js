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
    'dojo/_base/lang',
    'jimu/BaseWidget',
    'jimu/portalUrlUtils',
    'jimu/shareUtils',
    "jimu/dijit/ShareLink",
    "jimu/utils",
    'jimu/dijit/LoadingShelter',
    "jimu/dijit/Message"
  ],
  function(declare, lang, BaseWidget, portalUrlUtils, shareUtils, ShareLink, jimuUtils,LoadingShelter, Message) {

    return declare([BaseWidget], {
      name: 'Share',
      baseClass: 'jimu-widget-share share-container',
      _isShowFindLocation: true,

      onOpen: function() {
        this.widgetManager.activateWidget(this);
        shareUtils.getItemShareInfo(this.appConfig.portalUrl).then(lang.hitch(this, function(shareInfo) {
          var isSharedToPublic = shareUtils.isSharedToPublic(shareInfo);
          if (this.shareLink && this.shareLink.onShareToPublicChanged && true === this.shareLink.HAS_INIT_URL) {
            this.shareLink.onShareToPublicChanged(isSharedToPublic);
          }
        }));
      },

      onClose: function () {
        if (this.shareLink) {
          this.shareLink.onCloseContainer();
        }
      },

      onDeActive: function() {
        //this._hide();
        //this._deactivateDirections();
        //this._enableWebMapPopup();
      },

      _disableWebMapPopup: function() {
      },

      _enableWebMapPopup: function() {
      },

      postCreate: function() {
        this.inherited(arguments);
        //LoadingShelter
        this.shelter = new LoadingShelter({
          hidden: true
        });
        this.shelter.placeAt(this.domNode);
        this.shelter.startup();
        //TODO can't get evet
        // this.own(topic.subscribe("builder/SharePluginOnClickEveryone",
        //   lang.hitch(this, function(isEveryoneChecked) {
        //     this.shareLink.onShareToEveryoneCheck(isEveryoneChecked);
        //   })));
      },

      startup: function() {
        this.inherited(arguments);
        this.shelter.show();
        this._isShowFindLocation = this._findSearchWidget(this.appConfig);

        shareUtils.getItemShareInfo(this.appConfig.portalUrl).then(lang.hitch(this, function(result) {
          var shareInfo = result;

          this.shareLink = new ShareLink({
            portalUrl: this.appConfig.portalUrl,
            appTitle: this.appConfig.title,
            isOnline: portalUrlUtils.isOnline(jimuUtils.getAppHref()/*this.appConfig.portalUrl*/),
            isShowSocialMediaLinks: true,//shareUtils.isShowSocialMediaLinks(shareInfo),
            isSharedToPublic: shareUtils.isSharedToPublic(shareInfo),
            isShowBackBtn: true,
            config: this.config,
            isShowFindLocation: this._isShowFindLocation
          });
          this.shareLink.placeAt(this.container);
        }), lang.hitch(this, function(err) {
          new Message({
            message: err.message
          });
        })).always(lang.hitch(this, function() {
          this.shelter.hide();
        }));
      },
      // _hide: function() {
      //
      // },
      //
      // _show: function() {
      //
      // }
      onAppConfigChanged: function(appConfig) {
        this._isShowFindLocation = this._findSearchWidget(appConfig);
        if (this.shareLink && this.shareLink.updateShareLinkOptionsUI) {
          this.shareLink.updateShareLinkOptionsUI({isShowFindLocation: this._isShowFindLocation});
        }
      },
      _findSearchWidget: function(appConfig) {
        var findWidgets = appConfig.getConfigElementsByName("Search");
        return findWidgets.length > 0 && findWidgets[0].visible;
      }
    });
  });