/**
 * Created by wangjian on 16/1/7.
 */
define([
  'intern!object',
  'intern/chai!assert',
  'widgets/Geoprocessing/editors/DataFileEditor',
  'sinonFakeServer!createFakeServer',
  'dojo/json',
  'dojo/text!../config.json',
  '../../../globals'
], function(registerSuite, assert, DataFileEditor, createFakeServer, JSON, configStr) {
  'use strict';
  var config = JSON.parse(configStr);
  var options = {
    param: {
      name: 'Test_DataFile',
      dataType: 'GPDataFile',
      defaultValue: 'url:http://esridevbeijing.maps.arcgis.com/',
      category: '',
      label: 'Test DataFile',
      visible: true,
      required: false,
      tooltip: 'Test DataFile'
    },
    widgetUID: 'uid',
    config: config,
    nls: {
      useUrlForGPInput: 'url',
      useUploadForGPInput: 'file',
      selectFileToUpload: 'select file'
    },
    context: 'setting'
  };
  var editor, server;

  registerSuite({
    name: 'Test DataFileEditor',

    'setting - enable upload and default value is url': {
      setup: function() {
        config.serverInfo.supportsUpload = true;
        options.value = options.param.defaultValue;
        editor = new DataFileEditor(options);
      },

      teardown: function() {
        config.serverInfo.supportsUpload = false;
        options.value = undefined;
        editor.destroy();
        editor = null;
      },

      'it should be url mode when default value is url': function() {
        assert.strictEqual(editor.mode, 'url');
      },

      'modeSelection should be visible': function() {
        assert.strictEqual(editor.modeSelection.style.display, '');
      },

      'value should be set': function() {
        assert.strictEqual(editor.getValue(), 'url:http://esridevbeijing.maps.arcgis.com/');
      },

      'change mode to upload': {
        setup: function() {
          editor._onItemModeSelect();
        },

        'it should be item mode': function() {
          assert.strictEqual(editor.mode, 'item');
        },

        'url input should be hidden': function() {
          assert.strictEqual(editor.urlNode.style.display, 'none');
        },

        'value should be an empty item': function() {
          assert.strictEqual(editor.getValue(), 'itemID:');
        }
      }
    },

    'setting - enable upload and default value is itemID': {
      setup: function() {
        config.serverInfo.supportsUpload = true;
        options.param.defaultValue = 'itemID:abc123';
        options.value = options.param.defaultValue;
        editor = new DataFileEditor(options);
      },

      teardown: function() {
        config.serverInfo.supportsUpload = false;
        options.value = undefined;
        editor.destroy();
        editor = null;
      },

      'it should be item mode when default value is item': function() {
        assert.strictEqual(editor.mode, 'item');
      },

      'modeSelection should be visible': function() {
        assert.strictEqual(editor.modeSelection.style.display, '');
      },

      'value should be an empty item': function() {
        assert.strictEqual(editor.getValue(), 'itemID:');
      },

      'change mode to url': {
        setup: function() {
          editor._onUrlModeSelect();
        },

        'it should be item mode': function() {
          assert.strictEqual(editor.mode, 'url');
        },

        'url input should show': function() {
          assert.notStrictEqual(editor.urlNode.style.display, 'none');
        },

        'value should be an empty url': function() {
          assert.strictEqual(editor.getValue(), 'url:');
        }
      }
    },

    'setting - disable upload': {
      setup: function() {
        config.serverInfo.supportsUpload = false;
        options.param.defaultValue = 'itemID:abc123';
        options.value = options.param.defaultValue;
        editor = new DataFileEditor(options);
      },

      teardown: function() {
        config.serverInfo.supportsUpload = false;
        options.value = undefined;
        editor.destroy();
        editor = null;
      },

      'it should be url mode even default value is item': function() {
        assert.strictEqual(editor.mode, 'url');
      },

      'modeSelection should be hidden': function() {
        assert.strictEqual(editor.modeSelection.style.display, 'none');
      },

      'value should be an empty url': function() {
        assert.strictEqual(editor.getValue(), 'url:');
      }
    },

    'running - enable upload and with url mode': {
      setup: function() {
        options.context = 'widget';
        config.serverInfo.supportsUpload = true;
        options.param.defaultValue = 'url:http://esridevbeijing.maps.arcgis.com/';
        options.value = options.param.defaultValue;
        editor = new DataFileEditor(options);
      },

      teardown: function() {
        options.context = 'setting';
        config.serverInfo.supportsUpload = false;
        options.value = undefined;
        editor.destroy();
        editor = null;
      },

      'value should be set': function() {
        assert.strictEqual(editor.getValue(), 'url:http://esridevbeijing.maps.arcgis.com/');
      },

      'GPValue should return valid value': function() {
        var dfd = this.async(1000);
        editor.getGPValue().then(dfd.callback(function(gpData) {
          assert.strictEqual(gpData.url, 'http://esridevbeijing.maps.arcgis.com/');
        }), function() {
          dfd.reject();
        });
      }
    },

    'running - enable upload and with item mode': {
      setup: function() {
        /* global esri*/
        esri.config.defaults.io.proxyUrl = 'http://localhost:9000/';

        options.context = 'widget';
        config.serverInfo.supportsUpload = true;
        options.param.defaultValue = 'itemID:';
        options.value = options.param.defaultValue;
        editor = new DataFileEditor(options);
      },

      teardown: function() {
        options.context = 'setting';
        options.param.defaultValue = 'url:http://esridevbeijing.maps.arcgis.com/';
        config.serverInfo.supportsUpload = false;
        options.value = undefined;
        editor.destroy();
        editor = null;
      },

      beforeEach: function() {
        server = createFakeServer();
      },

      afterEach: function() {
        server.restore();
      },

      'fileNode should be visible': function() {
        assert.notStrictEqual(editor.fileNode.style.display, 'none');
        assert.strictEqual(editor.urlNode.style.display, 'none');
      },

      'upload file': function() {
        var dfd = this.async(10000);
        server.respondWith('POST',
          /\/uploads\/upload/,
          [200, {'Content-Type': 'application/json'}, '{"success": true, "item": {"itemID": "abc"}}']);

        editor._doUpload().then(function() {
          editor.getGPValue().then(dfd.callback(function(gpData) {
            assert.strictEqual(gpData.itemID, 'abc');
          }), function() {
            dfd.reject();
          });
        });

        server.respond();
      },

      'upload file failed': function() {
        var dfd = this.async(10000);
        server.respondWith('POST',
          /\/uploads\/upload/,
          [404, {'Content-Type': 'application/json'}, '{"message": "Internal error: hard coded"}']);

        editor._doUpload().then(function() {
          // should not be invoked
        }, dfd.callback(function(error) {
          assert.include(error.message, 'status: 404');
        }));

        server.respond();
      }
    }
  });
});
