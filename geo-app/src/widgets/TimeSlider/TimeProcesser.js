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
  'dojo/_base/array',
  'dojo/_base/config',
  'dojo/Evented',
  'dijit/_WidgetBase',
  'dojo/when',
  'dojo/promise/all',
  'dojo/Deferred',
  'esri/request',
  'moment/moment',
  'dojo/date/locale',
  'dojo/i18n',
  'esri/lang',
  'esri/TimeExtent'
],
  function (declare, lang, array, dojoConfig,
    Evented, _WidgetBase, when, all, Deferred, esriRequest,
    moment, dateLocale, i18n, esriLang, TimeExtent) {

    var clazz = declare([_WidgetBase, Evented], {
      nls: null,
      config: null,
      map: null,
      layerInfosObj: null,

      setLayerInfosObj: function (layerInfosObj) {
        this.layerInfosObj = layerInfosObj;
      },

      _getUpdatedFullTime: function () {
        var i = 0,
          len, layer, layerId;
        var defs = [];
        for (i = 0, len = this.map.layerIds.length; i < len; i++) {
          layerId = this.map.layerIds[i];
          layer = this.map.getLayer(layerId);

          defs.push(this._getUpdatedTime(layer));
        }

        for (i = 0, len = this.map.graphicsLayerIds.length; i < len; i++) {
          layerId = this.map.graphicsLayerIds[i];
          layer = this.map.getLayer(layerId);

          defs.push(this._getUpdatedTime(layer));
        }

        return all(defs).then(lang.hitch(this, function (timeExtents) {
          return this._getFullTimeExtent(timeExtents);
        }));
      },

      _getFullTimeExtent: function (timeExtents) {
        var fullTimeExtent = null;
        array.forEach(timeExtents, lang.hitch(this, function (te) {
          if (!te) {
            return;
          }

          if (!fullTimeExtent) {
            fullTimeExtent = new TimeExtent(new Date(te.startTime.getTime()),
              new Date(te.endTime.getTime()));
          } else {
            if (fullTimeExtent.startTime > te.startTime) {
              fullTimeExtent.startTime = new Date(te.startTime.getTime());
            }
            if (fullTimeExtent.endTime < te.endTime) {
              fullTimeExtent.endTime = new Date(te.endTime.getTime());
            }
          }
        }));

        return fullTimeExtent;
      },

      _getUpdatedTime: function (layer) {
        if (layer && layer.url && this.hasLiveData(layer)) {
          var timeExtent = null;
          return esriRequest({
            url: layer.url,
            callbackParamName: 'callback',
            content: {
              f: 'json',
              returnUpdates: true
            }
          }).then(lang.hitch(this, function (result) {
            if (result.timeExtent && result.timeExtent.length === 2) {
              timeExtent = new TimeExtent();
              timeExtent.startTime = new Date(result.timeExtent[0]);
              timeExtent.endTime = new Date(result.timeExtent[1]);
            }
          })).always(lang.hitch(this, function () {
            return when(timeExtent || lang.getObject('timeInfo.timeExtent', false, layer) || null);
          }));
        } else {
          return when(lang.getObject('timeInfo.timeExtent', false, layer) || null);
        }
      },

      getUpdatedFullTime: function () {
        var i = 0,
          len, layer, layerId;
        var defs = [];
        for (i = 0, len = this.map.layerIds.length; i < len; i++) {
          layerId = this.map.layerIds[i];
          layer = this.map.getLayer(layerId);

          defs.push(this._getUpdatedTime(layer));
        }

        for (i = 0, len = this.map.graphicsLayerIds.length; i < len; i++) {
          layerId = this.map.graphicsLayerIds[i];
          layer = this.map.getLayer(layerId);

          defs.push(this._getUpdatedTime(layer));
        }

        return all(defs).then(lang.hitch(this, function (timeExtents) {
          return this._getFullTimeExtent(timeExtents);
        }));
      },

      needUpdateFullTime: function () {
        var i = 0, len, layer, layerId;
        for (i = 0, len = this.map.layerIds.length; i < len; i++) {
          layerId = this.map.layerIds[i];
          layer = this.map.getLayer(layerId);

          if (this.hasLiveData(layer)) {
            return true;
          }
        }

        for (i = 0, len = this.map.graphicsLayerIds.length; i < len; i++) {
          layerId = this.map.graphicsLayerIds[i];
          layer = this.map.getLayer(layerId);

          if (this.hasLiveData(layer)) {
            return true;
          }
        }

        return false;
      },
      hasLiveData: function (layer) {
        // doesn't need to consider KMLLayers
        return layer && layer.useMapTime && layer.timeInfo && layer.timeInfo.hasLiveData;
      },

      setTimeSlider: function (timeSlider) {
        this.timeSlider = timeSlider;
      },
      _getTimeFormatLabel: function (timeExtent) {
        var label = this.nls.timeExtent;
        var start = null;
        var end = null;
        var startTime = "";
        var endTime = "";

        if (!timeExtent && this.timeSlider) {
          if (this.timeSlider.thumbCount === 2) {
            start = this.timeSlider.timeStops[0];
            end = this.timeSlider.timeStops[1];
          } else {
            start = this.timeSlider.timeStops[0];
          }
        } else if (!timeExtent && !this.timeSlider) {
          //No time-aware layers
          label = "";
          return label;
        } else {
          start = timeExtent.startTime;
          if (timeExtent.endTime.getTime() - timeExtent.startTime.getTime() > 0) {
            end = timeExtent.endTime;
          }
        }

        if (this.config.timeFormat !== "auto" &&
          !("Custom" === this.config.timeFormat && "" === this.config.customDateFormat)) {
          
          var format = ("Custom" === this.config.timeFormat ? this.config.customDateFormat : this.config.timeFormat);
          startTime = moment(start.getTime()).format(format);
          if (end) {
            endTime = moment(end.getTime()).format(format);
          }
        } else {
          //auto mode
          var datePattern = null;
          var timePattern = null;
          var formatLength = null;
          var showEndDate = false;
          var time = clazz.localeDic[dojoConfig.locale] || clazz.localeDic.en;
          if (end && start.getFullYear() === end.getFullYear()) {
            if (start.getMonth() === end.getMonth()) {
              if (start.getDate() === end.getDate()) {
                if (start.getHours() === end.getHours()) {
                  if (start.getMinutes() === end.getMinutes()) {
                    if (start.getSeconds() === end.getSeconds()) {
                      // same second
                      timePattern = time.millisecondTimePattern;
                      formatLength = "long";
                    } else { // same minute
                      timePattern = time.secondTimePattern;
                      formatLength = "long";
                    }
                  } else { // same hour
                    timePattern = time.minuteTimePattern;
                    formatLength = "long";
                  }
                } else { // same day
                  timePattern = time.minuteTimePattern; //hourTimePattern;
                  formatLength = "long";
                }
              } else { // same month
                if (end.getDate() - start.getDate() < 2) {
                  // less than 2 days
                  timePattern = time.minuteTimePattern; //hourTimePattern;
                  showEndDate = true;
                  formatLength = "long";
                } else {
                  showEndDate = true;
                  formatLength = "long";
                }
              }
            } else { // same year
              showEndDate = true;
              formatLength = "long";
            }
          } else if (end && end.getFullYear() - start.getFullYear() > 10) {
            datePattern = time.yearPattern;
            showEndDate = true;
          } else {
            showEndDate = true;
            formatLength = "long";
          }

          startTime = dateLocale.format(start, {
            datePattern: datePattern,
            formatLength: formatLength,
            selector: "date"
          });
          if (timePattern) {
            var startTime2 = dateLocale.format(start, {
              timePattern: timePattern,
              selector: "time"
            });
            var startTime3 = i18n.getLocalization("dojo.cldr", "gregorian")["dateTimeFormat-medium"]
              .replace(/\{1\}/g, startTime).replace(/\{0\}/g, startTime2);
            startTime = startTime3;
          }
          //end
          if (end) {
            if (showEndDate) {
              endTime = dateLocale.format(end, {
                datePattern: datePattern,
                formatLength: formatLength,
                selector: "date"
              });
            }
            if (timePattern) {
              var endTime2 = dateLocale.format(end, {
                timePattern: timePattern,
                selector: "time"
              });
              if (showEndDate && timePattern) {
                var endTime3 = i18n.getLocalization("dojo.cldr", "gregorian")["dateTimeFormat-medium"]
                  .replace(/\{1\}/g, endTime).replace(/\{0\}/g, endTime2);
                endTime = endTime3;
              } else {
                endTime = endTime2;
              }
            }
          }
        }

        if (end) {
          label = esriLang.substitute({
            FROMTIME: startTime,
            ENDTIME: endTime
          }, label);
        } else {
          label = startTime + "";
        }
        return label;
      },

      findDefaultInterval: function (fullTimeExtent) {
        var interval;
        var units;
        var timePerStop = (fullTimeExtent.endTime.getTime() - fullTimeExtent.startTime.getTime()) / 10;
        var century = 1000 * 60 * 60 * 24 * 30 * 12 * 100;
        if (timePerStop > century) {
          interval = Math.round(timePerStop / century);
          units = "esriTimeUnitsCenturies";
        } else {
          var decade = 1000 * 60 * 60 * 24 * 30 * 12 * 10;
          if (timePerStop > decade) {
            interval = Math.round(timePerStop / decade);
            units = "esriTimeUnitsDecades";
          } else {
            var year = 1000 * 60 * 60 * 24 * 30 * 12;
            if (timePerStop > year) {
              interval = Math.round(timePerStop / year);
              units = "esriTimeUnitsYears";
            } else {
              var month = 1000 * 60 * 60 * 24 * 30;
              if (timePerStop > month) {
                interval = Math.round(timePerStop / month);
                units = "esriTimeUnitsMonths";
              } else {
                var week = 1000 * 60 * 60 * 24 * 7;
                if (timePerStop > week) {
                  interval = Math.round(timePerStop / week);
                  units = "esriTimeUnitsWeeks";
                } else {
                  var day = 1000 * 60 * 60 * 24;
                  if (timePerStop > day) {
                    interval = Math.round(timePerStop / day);
                    units = "esriTimeUnitsDays";
                  } else {
                    var hour = 1000 * 60 * 60;
                    if (timePerStop > hour) {
                      interval = Math.round(timePerStop / hour);
                      units = "esriTimeUnitsHours";
                    } else {
                      var minute = 1000 * 60;
                      if (timePerStop > minute) {
                        interval = Math.round(timePerStop / minute);
                        units = "esriTimeUnitsMinutes";
                      } else {
                        var second = 1000;
                        if (timePerStop > second) {
                          interval = Math.round(timePerStop / second);
                          units = "esriTimeUnitsSeconds";
                        } else {
                          interval = Math.round(timePerStop);
                          units = "esriTimeUnitsMilliseconds";
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }

        return {
          interval: interval,
          units: units
        };
      },
      getPropsFromMultiLayerInfos: function (timeInfos, ref) {
        var res = {};
        if (null === ref) {
          res = timeInfos;
          res.thumbCount = 2;
          res.thumbMovingRate = 2000;
        } else {
          res = ref;

          if (timeInfos.timeExtent[0] < res.timeExtent[0]) {
            res.timeExtent[0] = timeInfos.timeExtent[0];
          }
          if (timeInfos.timeExtent[1] > res.timeExtent[1]) {
            res.timeExtent[1] = timeInfos.timeExtent[1];
          }
        }

        return res;
      },
      getTsPros: function () {
        //get all layers timeInfos
        //from min time -> max time
        //use suitable TimeInterval(method form mapViewer)
        var def = new Deferred();
        var itemInfo = this.map && this.map.itemInfo;

        var timeSliderProps = lang.getObject('itemData.widgets.timeSlider.properties',
          false, itemInfo);

        var tsProps = {};
        if (timeSliderProps) {
          //1. props from mapViwer
          tsProps = lang.clone(timeSliderProps);
          def.resolve(tsProps);
        } else {
          //2. props from map.itemInfo
          var layers = lang.getObject('itemData.operationalLayers', false, itemInfo);
          if (layers) {
            var ref = null;
            for (var i = 0, len = layers.length; i < len; i++) {
              var layer = layers[i];
              var timeInfos = lang.getObject('resourceInfo.timeInfo', false, layer);

              if (timeInfos && timeInfos.timeExtent) {
                ref = this.getPropsFromMultiLayerInfos(timeInfos, ref);
              }
            }

            if (null !== ref) {
              ref.startTime = ref.timeExtent[0];
              ref.endTime = ref.timeExtent[1];
              ref._needToFindDefaultInterval = true;

              tsProps = ref;
              def.resolve(tsProps);
            } else {
              //4. no props
              def.resolve(null);
            }
            //   //3. props from services
            // //   esriRequest({
            // //     url: layers.url,
            // //     content: {
            // //       f: 'json'
            // //     },
            // //     handleAs: 'json',
            // //     callbackParamName: 'callback'
            // //   }).then(lang.hitch(this, function (res) {

            // //   }), lang.hitch(this, function () {
            // //     //4. no props
            // //     def.resolve(null);
            // //   }));
            //  }
            //          } else {
            //4. no props
            //            return def.resolve(null);
          } else {
            def.resolve(null);
          }
        }

        return def;
      }

    });

    clazz.localeDic = {
      'ar': {
        datePattern: "dd MMMM, yyyy", // e.g. for German: "d. MMMM yyyy"
        yearPattern: "yyyy",
        hourTimePattern: "h a", // e.g. for German: "H"
        minuteTimePattern: "h:mm a", // e.g. for German: "H:mm"
        secondTimePattern: "h:mm:ss a", // e.g. for German: "H:mm:ss"
        millisecondTimePattern: "h:mm:ss:SSS a" // e.g. for German: "H:mm:ss:SSS"
      },
      'cs': {
        datePattern: "MMMM d, yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "h:mm",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'da': {
        datePattern: "d. MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "H:mm",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'de': {
        datePattern: "d. MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "H:mm",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'el': {
        datePattern: "d MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "h",
        minuteTimePattern: "hh:mm",
        secondTimePattern: "hh:mm:ss",
        millisecondTimePattern: "hh:mm:ss:SSS"
      },
      'es': {
        datePattern: "d\' de \'MMMM\' de \'yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "H:mm",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'et': {
        datePattern: "d. MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "H:mm",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'fi': {
        datePattern: "d. MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "t",
        minuteTimePattern: "t:mm a",
        secondTimePattern: "t:mm:ss",
        millisecondTimePattern: "h:mm:ss:SSS"
      },
      'fr': {
        datePattern: "d MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "HH",
        minuteTimePattern: "HH:mm",
        secondTimePattern: "HH:mm:ss",
        millisecondTimePattern: "HH:mm:ss:SSS"
      },
      'he': {
        datePattern: "d, MMMM ,yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "h a",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "h:mm:ss a",
        millisecondTimePattern: "h:mm:ss:SSS a"
      },
      'it': {
        datePattern: "d MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "H.mm",
        secondTimePattern: "H.mm.ss",
        millisecondTimePattern: "H.mm.ss.SSS"
      },
      'ja': {
        datePattern: "yyyy'年'M'月'd'日'",
        yearPattern: "yyyy'年'",
        hourTimePattern: "h a",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "h:mm:ss a",
        millisecondTimePattern: "h:mm:ss:SSS a"
      },
      'ko': {
        datePattern: "yyyy년 M월 d일",
        yearPattern: "yyyy년",
        hourTimePattern: "a h시",
        minuteTimePattern: "a h:mm",
        secondTimePattern: "a h:mm:ss",
        millisecondTimePattern: "a h:mm:ss:SSS"
      },
      'lt': {
        datePattern: "yyyy MMMM dd",
        yearPattern: "yyyy",
        hourTimePattern: "H a",
        minuteTimePattern: "HH:mm",
        secondTimePattern: "HH:mm:ss",
        millisecondTimePattern: "HH:mm:ss:SSS"
      },
      'lv': {
        datePattern: "dd.MM.yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H a",
        minuteTimePattern: "HH:mm",
        secondTimePattern: "HH:mm:ss",
        millisecondTimePattern: "HH:mm:ss:SSS"
      },
      'nb': {
        datePattern: "d. MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "H.mm",
        secondTimePattern: "H.mm.ss",
        millisecondTimePattern: "H.mm.ss.SSS"
      },
      'nl': {
        datePattern: "d. MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "H:mm",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'pl': {
        datePattern: "dd-mm-yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "hh",
        minuteTimePattern: "hh:mm",
        secondTimePattern: "hh:mm:ss",
        millisecondTimePattern: "hh:mm:ss:SSS"
      },
      'pt-br': {
        datePattern: "d\' de \'MMMM\' de \'yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'pt-pt': {
        datePattern: "d\' de \'MMMM\' de \'yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "H:mm",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'ro': {
        datePattern: "d. MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "H:mm",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'ru': {
        datePattern: "MMMM d, yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H",
        minuteTimePattern: "h:mm",
        secondTimePattern: "h:mm:ss",
        millisecondTimePattern: "h:mm:ss:SSS"
      },
      'sv': {
        datePattern: "MMMM d, yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "h a",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "h:mm:ss a",
        millisecondTimePattern: "h:mm:ss:SSS a"
      },
      'th': {
        datePattern: "d MMMM,yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "H a",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "h:mm:ss a",
        millisecondTimePattern: "h:mm:ss:SSS a"
      },
      'tr': {
        datePattern: "d MMMM yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "h a",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "h:mm:ss a",
        millisecondTimePattern: "h:mm:ss:SSS a"
      },
      'vi': {
        datePattern: "d MMMM, yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "h a",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "h:mm:ss a",
        millisecondTimePattern: "h:mm:ss:SSS a"
      },
      'zh-cn': {
        datePattern: "yyyy'年'M'月'd'日'",
        yearPattern: "yyyy'年'",
        hourTimePattern: "H",
        minuteTimePattern: "H:mm",
        secondTimePattern: "H:mm:ss",
        millisecondTimePattern: "H:mm:ss:SSS"
      },
      'zh-hk': {
        datePattern: "年月日",
        yearPattern: "yyyy",
        hourTimePattern: "h a",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "h:mm:ss a",
        millisecondTimePattern: "h:mm:ss:SSS a"
      },
      'zh-tw': {
        datePattern: "年月日",
        yearPattern: "yyyy",
        hourTimePattern: "h a",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "h:mm:ss a",
        millisecondTimePattern: "h:mm:ss:SSS a"
      },
      'en': {
        datePattern: "MMMM d, yyyy",
        yearPattern: "yyyy",
        hourTimePattern: "h a",
        minuteTimePattern: "h:mm a",
        secondTimePattern: "h:mm:ss a",
        millisecondTimePattern: "h:mm:ss:SSS a"
      }
    };

    return clazz;
  });