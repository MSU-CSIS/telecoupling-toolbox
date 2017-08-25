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

define(['dojo/_base/html', 'dojo/dom-geometry'],
  function (html, domGeometry) {

    var mo = {};

    mo.initPositionForTheme = {
      "DartTheme": {
        bottom: 140
      },
      'LaunchpadTheme': {
        bottom: 120
      }
    };

    mo.isRunInMobile = function () {
      return window.appInfo.isRunInMobile;
    };

    mo.initPosition = function(map,domNode,position){
      var appConfig = window.getAppConfig();
      var theme;
      if(appConfig && appConfig.theme && appConfig.theme.name){
        theme = appConfig.theme.name;
      }

      var top = mo.getInitTop(map, domNode, theme);
      var left = mo.getInitLeft(map, domNode, theme);
      position.top = top;
      position.left = left;
      html.setStyle(domNode, 'top', position.top + 'px');
      html.setStyle(domNode, 'left', position.left + 'px');
    };
    mo.getInitTop = function (map, domNode, theme) {
      var top = 0;
      var containerBox = domGeometry.getMarginBox(map.root);
      var sliderContentBox = html.getContentBox(domNode);
      var popupHeight = sliderContentBox.h;

      var marginBottom = mo.initPositionForTheme[theme] ? mo.initPositionForTheme[theme].bottom : 60;
      top = containerBox.h - marginBottom - popupHeight;

      return top;
    };
    mo.getInitLeft = function (map, domNode/*, theme*/) {
      var left = 0;
      var containerBox = domGeometry.getMarginBox(map.root);
      var sliderContentBox = html.getContentBox(domNode);

      var middleOfScreenWidth = containerBox.w / 2;
      var middleOfPopupWidth = sliderContentBox.w / 2;
      left = middleOfScreenWidth - middleOfPopupWidth;

      return left;
    };


    return mo;
  });