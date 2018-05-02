define(['dojo/_base/declare', 'jimu/BaseWidget'],
function(declare, BaseWidget) {

  return declare([BaseWidget], {

    baseClass: 'maptiks-widget',

    postCreate: function() {
      
      this.inherited(arguments);

      require(["//cdn.maptiks.com/esri3/mapWrapper.js"], (mapWrapper) => {
        var container = this.map.container;
        var maptiksMapOptions = {
          maptiks_trackcode: this.config.maptiksTrackcode,
          maptiks_id: this.config.maptiksId
        };
        mapWrapper(container, maptiksMapOptions, this.map);
      });
    }
  });
});
