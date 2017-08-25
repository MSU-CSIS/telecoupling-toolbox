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
    'dojo/_base/array',
    'dojo/Evented',
    'dijit/_WidgetBase',
    'dijit/_TemplatedMixin',
    'dijit/_WidgetsInTemplateMixin',
    'dojo/text!./SpeedMenu.html',
    'dojo/on',
    'dojo/query'
  ],
  function (declare, lang, html, array,
    Evented, _WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin, template,
    on, query) {
    // box of speed-menu

    var clazz = declare([_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin, Evented], {
      baseClass: 'speed-container',
      templateString: template,
      nls: null,
      menuBox : {
        w: 75,
        h: 120
      },

      postCreate: function() {
        this.inherited(arguments);
        //init speed meun
        this._initSpeedMenu();
      },

      startup: function() {
        this.inherited(arguments);
      },

      destroy: function(){
        this.inherited(arguments);
      },

      _initSpeedMenu: function(){
        this.own(on(this.domNode, 'click', lang.hitch(this, this._closeSpeedMenu)));
        this._checks = query(".check", this.speedMenu);

        //init display
        on.emit(this.initSpeedItem, 'click', { cancelable: false, bubbles: true });
      },

      _onSelectSpeedItem: function(evt) {
        array.map(this._checks, lang.hitch(this, function (check) {
          html.addClass(check, 'hide');
        }));

        if (evt.target) {
          var rateStr = html.getAttr(evt.target, 'speed');
          var check = query(".check", evt.target)[0];
          html.removeClass(check, 'hide');

          this.speedLabelNode.innerHTML = evt.target.innerText;

          this.emit("selected", rateStr);
        }
      },
      //speed menu
      _setMenuPosition: function() {
        var sPosition = html.position(this.speedLabelNode);
        if (sPosition.y - this.menuBox.h - 2 < 0) {
          html.setStyle(this.speedMenu, {
            top: '27px',
            bottom: 'auto'
          });
        }

        var layoutBox = html.getMarginBox(this.domNode);
        if (window.isRTL) {
          if (sPosition.x - this.menuBox.w < 0) {
            html.setStyle(this.speedMenu, {
              left: 0
            });
          }
        } else {
          if (sPosition.x + this.menuBox.w > layoutBox.w) {
            html.setStyle(this.speedMenu, {
              right: 0
            });
          }
        }
      },

      _onSpeedLabelClick: function(evt) {
        evt.stopPropagation();
        evt.preventDefault();

        if(html.hasClass(this.speedMenu, "hide")){
          this._setMenuPosition();
          this._showSpeedMenu();
        } else {
          this._closeSpeedMenu();
        }
      },

      _showSpeedMenu: function() {
        html.removeClass(this.speedMenu, "hide");
        this.emit("open");
      },

      _closeSpeedMenu: function() {
        html.addClass(this.speedMenu, "hide");
        this.emit("close");
      }

    });
    return clazz;
  });