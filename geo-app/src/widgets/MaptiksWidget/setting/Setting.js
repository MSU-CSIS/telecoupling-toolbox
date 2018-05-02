define([
  'dojo/_base/declare',
  'jimu/BaseWidgetSetting'
],
function(declare, BaseWidgetSetting) {

  return declare([BaseWidgetSetting], {
    baseClass: 'maptiks-widget-setting',

    postCreate: function(){
      this.setConfig(this.config);
    },

    setConfig: function(config){
      this.maptiksTrackcode.value = config.maptiksTrackcode;
      this.maptiksId.value = config.maptiksId;
    },

    getConfig: function(){
      return {
        maptiksTrackcode: this.maptiksTrackcode.value,
        maptiksId: this.maptiksId.value
      };
    }
  });
});
