function bySelector(selector) {
  const element = document.querySelector(selector);

  if (!element) {
    throw new Error(`No se encontro el elemento "${selector}".`);
  }

  return element;
}

export const dom = {
  shell: bySelector(".app-shell"),
  topLayout: bySelector(".top-layout"),
  leftStack: bySelector(".left-stack"),
  canvases: {
    fluteBase: bySelector("#flute-base-canvas"),
    fluteInverse: bySelector("#flute-inverse-canvas"),
    graph: bySelector("#inharmonicity-graph-canvas"),
  },
  panels: {
    fluteBase: bySelector('[data-panel="flute-base"]'),
    fluteInverse: bySelector('[data-panel="flute-inverse"]'),
    graph: bySelector('[data-panel="graph"]'),
    extraLeft: bySelector('[data-panel="extra-left"]'),
    extraRight: bySelector('[data-panel="extra-right"]'),
  },
  graphControls: {
    idInput: bySelector(".graph-id-input"),
    modeRadios: Array.from(document.querySelectorAll("[data-graph-mode]")),
    visualizationModeRadio: bySelector('[data-graph-mode="visualization"]'),
    calculationModeRadio: bySelector('[data-graph-mode="calculation"]'),
    calculateBaseButton: bySelector('[data-graph-action="calculate-base"]'),
    calculateInverseButton: bySelector('[data-graph-action="calculate-inverse"]'),
    searchBaseButton: bySelector('[data-graph-search="base"]'),
    searchInverseButton: bySelector('[data-graph-search="inverse"]'),
  },
  rmsePanel: {
    pairsTrigger: bySelector('[data-rmse-trigger="pairs"]'),
    pairsTriggerText: bySelector('[data-rmse-trigger-text="pairs"]'),
    pairsList: bySelector('[data-rmse-list="pairs"]'),
    rangeTrigger: bySelector('[data-rmse-trigger="range"]'),
    rangeTriggerText: bySelector('[data-rmse-trigger-text="range"]'),
    rangeList: bySelector('[data-rmse-list="range"]'),
  },
};
