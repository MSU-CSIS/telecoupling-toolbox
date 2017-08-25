/**
 * Created by wangjian on 16/1/2.
 */
define([
  'intern!object',
  'intern/chai!assert',
  'widgets/Geoprocessing/utils',
  'sinonFakeServerIntern!createFakeServer'
], function(registerSuite, assert, gputils, createFakeServer) {
  'use strict';
  var serverInfo = {
      url: 'http://sample.com/arcgis/rest/services/Elevation/GPServer/',
      currentVersion: undefined
    }, server;

  registerSuite({
    name: 'Geoprocessing utils test',

    'should return empty string if url is not a gp task': function() {
      var url = 'http://services.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer';

      assert.strictEqual(gputils.getGPServerUrl(url), '');
    },

    'should return result map server url if given url is a gpserver url': function() {
      var url = 'http://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/GPServer';
      var mapUrl = 'http://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer';
      assert.strictEqual(gputils.getResultMapServerUrl(url, '911CallsHotspot'), mapUrl);
    },

    'should return result map server url if given url is a task url': function() {
      var url = 'http://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/GPServer/911%20Calls%20Hotspot';
      var mapUrl = 'http://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer';
      assert.strictEqual(gputils.getResultMapServerUrl(url, '911CallsHotspot'), mapUrl);
    },

    'should return result map server url if given url is a task url 2': function() {
      var url = 'http://iceboat.esri.com/arcgis/rest/services/test/ExportFeatureAndTable/GPServer/Export%20Feature%20And%20Table';
      var mapUrl = 'http://iceboat.esri.com/arcgis/rest/services/test/ExportFeatureAndTable/MapServer';
      assert.strictEqual(gputils.getResultMapServerUrl(url, 'test/ExportFeatureAndTable'), mapUrl);
    },

    'should return gp server url': function() {
      var url = 'http://sample.com/arcgis/rest/services/Elevation/GPServer/Viewshed';

      assert.strictEqual(gputils.getGPServerUrl(url),
        'http://sample.com/arcgis/rest/services/Elevation/GPServer/'
      );
    },

    'sub suite - get service info': {
      setup: function() {
        /* global esri*/
        esri.config.defaults.io.proxyUrl = 'http://localhost:9000/';
      },

      beforeEach: function() {
        server = createFakeServer();
      },

      afterEach: function() {
        server.restore();
      },

      'should return {supportsUpload:false} if version less than 10.1': function() {
        serverInfo.currentVersion = 10;

        var dfd = this.async(10000);

        gputils.uploadSupported(serverInfo).then(dfd.callback(function(result) {
          assert.isFalse(result.supportsUpload);
        }));
      },

      'should return maxUploadFileSize if version >= 10.1 and response received': function() {
        serverInfo.currentVersion = 10.3;

        var dfd = this.async(10000);
        server.respondWith('GET',
          /\/uploads\/info/,
          [200, {'Content-Type': 'application/json'}, '{"maxUploadFileSize": 1024}']);

        gputils.uploadSupported(serverInfo).then(dfd.callback(function(result) {
          assert.strictEqual(result.maxUploadFileSize, 1024);
          assert.isTrue(result.supportsUpload);
        }));

        server.respond();
      },

      'should fail if version >= 10.1 but request for upload info throws exception': function() {
        serverInfo.currentVersion = 10.3;

        var dfd = this.async(10000);

        gputils.uploadSupported(serverInfo).then(dfd.callback(function(result) {
          assert.isFalse(result.supportsUpload);
        }));
      }
    }
  });
});
