declare namespace Select {
  export interface SelectConfig {
    selectionColor: string;
    selectionMode: string;
    allowExport: boolean;
  }
}

declare module 'widgets/Select/layerUtil' {
  import LayerInfos = require('jimu/LayerInfos/LayerInfos');
  import LayerInfo = require('jimu/LayerInfos/LayerInfo');

  class LayerUtil {
    static getLayerInfoArray(layerInfosObject: LayerInfos): dojo.Deferred<LayerInfo[]>;
  }

  export = LayerUtil;
}

declare module 'widgets/Select/ClearSelectionAction' {
  import BaseFeatureAction = require('jimu/BaseFeatureAction');

  class ClearSelectionAction extends BaseFeatureAction {

  }

  export = ClearSelectionAction;
}
