define([
  'intern!object',
  'intern/chai!assert',
  'dojo/json',
  'widgets/Geoprocessing/LayerOrderUtil',
  'dojo/text!./config.json'
], function (registerSuite, assert, JSON, LayerOrderUtil, configStr) {
  registerSuite(function(){
    var config;
    var layerOrderUtil;

    return {
      name: 'Geoprocessing LayerOrderUtil test',

      setup: function(){
        config = JSON.parse(configStr);
        config.inputParams[1].featureSetMode = 'url';
        layerOrderUtil = new LayerOrderUtil(config, null);
      },

      'getCandidateParamNames non-orderable': function(){
        var res = layerOrderUtil.getCandidateParamNames(false);

        assert.isArray(res);
        assert.strictEqual(res.length, 4,
            "4 layers have type of GPFeatureRecordSetLayer");
        assert.strictEqual(res[0], "Output_Drive_Time_Polygons");
        assert.strictEqual(res[1], "Output_Test_Polygons");
        assert.strictEqual(res[2], "Input_Location");
        assert.strictEqual(res[3], "Test_Input_Feature");
      },

      'getCandidateParamNames orderable': function(){
        var res = layerOrderUtil.getCandidateParamNames(true);

        assert.isArray(res);
        assert.strictEqual(res.length, 3, "3 layers can be orderable");
        assert.strictEqual(res[0], "Output_Drive_Time_Polygons");
        assert.strictEqual(res[1], "Output_Test_Polygons");
        assert.strictEqual(res[2], "Input_Location");
      },

      getOrderableInput: function(){
        var res = layerOrderUtil.getOrderableInput();

        assert.isArray(res);
        assert.strictEqual(res.length, 1, "1 input layer is orderable");
        assert.strictEqual(res[0], "Input_Location");
      },

      getOrderableOutput: function(){
        var res = layerOrderUtil.getOrderableOutput();

        assert.isArray(res);
        assert.strictEqual(res.length, 2, "2 output layers are orderable");
        assert.strictEqual(res[0], "Output_Drive_Time_Polygons");
        assert.strictEqual(res[1], "Output_Test_Polygons");
      }
    };
  });
});