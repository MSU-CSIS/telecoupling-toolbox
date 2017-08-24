define([
  'intern!object',
  'intern/chai!assert',
  'dojo/json',
  'widgets/Geoprocessing/setting/LayerOrder',
  'dojo/text!../config.json'
], function (registerSuite, assert, JSON, LayerOrder, configStr) {
  registerSuite(function(){
    var config;
    var layerOrder;

    return {
      name: 'Geoprocessing LayerOrder test',

      setup: function(){
        config = JSON.parse(configStr);
        layerOrder = new LayerOrder({
          nls:{
            layer: "layer"
          }
        });
        layerOrder.setConfig(config);
      },

      'default acceptValue': function(){
        var res, rows;
        layerOrder.acceptValue();
        res = config.layerOrder;
        rows = layerOrder.table.getRows();

        assert.isArray(res);
        assert.strictEqual(res.length, 4, "4 layers can be added to layerOrder");
        assert.strictEqual(res[0], "Output_Drive_Time_Polygons");
        assert.strictEqual(res[1], "Output_Test_Polygons");
        assert.strictEqual(res[2], "Input_Location");
        assert.strictEqual(res[3], "Test_Input_Feature");

        assert.isArray(rows);
        assert.strictEqual(rows.length, 4, "4 layers can be added to table");
      },

      'change featureSetMode': function(){
        var res, rows;
        config.inputParams[1].featureSetMode = 'url';

        layerOrder.setConfig(config);
        layerOrder.acceptValue();
        res = config.layerOrder;
        rows = layerOrder.table.getRows();

        assert.isArray(res);
        assert.strictEqual(res.length, 4, "4 layers can be added to layerOrder");
        assert.strictEqual(res[0], "Output_Drive_Time_Polygons");
        assert.strictEqual(res[1], "Output_Test_Polygons");
        assert.strictEqual(res[2], "Input_Location");
        assert.strictEqual(res[3], "Test_Input_Feature");

        assert.isArray(rows);
        assert.strictEqual(rows.length, 3,
            "3 layers can be added to table after change");
      }
    };
  });
});