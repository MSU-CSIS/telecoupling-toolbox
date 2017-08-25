define([
  'intern!object',
  'intern/chai!assert',
  'widgets/Geoprocessing/resultrenderers/defaultSymbol'
], function (registerSuite, assert, defaultSymbol) {
  registerSuite(function(){
    return {
      name: 'default symbol test',

      'get property from defaultSymbol': function(){
        assert.strictEqual(typeof defaultSymbol.pointSymbol, 'object');
      },

      'symbol parse': function(){
        assert.strictEqual(defaultSymbol.pointSymbol.type, 'picturemarkersymbol');
        assert.strictEqual(defaultSymbol.lineSymbol.type, 'simplelinesymbol');
        assert.strictEqual(defaultSymbol.polygonSymbol.type, 'simplefillsymbol');
      }
    };
  });
});