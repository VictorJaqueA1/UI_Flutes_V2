import { dom } from "../shared/dom.js";
import {
  getFluteGeometry,
  getVisualizationInstrumentId,
  hydrateFluteControls,
  selectClosestVisualizationFlute,
  setFluteInstrumentId,
  setFluteParam,
  setFluteParamMode,
} from "./state.js";
import {
  FLUTE_KINDS,
  clamp,
  getDynamicParamRange,
} from "../domain/index.js";
import { renderAllFluteSketches } from "./render.js";
import { GRAPH_MODES, getGraphMode } from "../graph/state.js";

function getFluteKeyFromPanel(panel) {
  return panel.dataset.panel === "flute-base" ? "base" : "inverse";
}

function getFluteKind(fluteKey) {
  return fluteKey === "base" ? FLUTE_KINDS.BASE : FLUTE_KINDS.INVERSE;
}

function dispatchVisualizationSelectionChanged(detail = {}) {
  window.dispatchEvent(new CustomEvent("flute-visualization-change", { detail }));
}

function renderCurrentFlutes() {
  renderAllFluteSketches({
    base: getFluteGeometry("base"),
    inverse: getFluteGeometry("inverse"),
  });
}

function bindPanelInputs(panel) {
  const fluteKey = getFluteKeyFromPanel(panel);
  const inputs = panel.querySelectorAll(".slider-input");

  for (const input of inputs) {
    input.addEventListener("input", (event) => {
      const paramKey = event.currentTarget.dataset.param;
      const nextValue = Number(event.currentTarget.value);
      const mode = getGraphMode();

      if (mode === GRAPH_MODES.VISUALIZATION) {
        const previousInstrumentId = getVisualizationInstrumentId(fluteKey);
        const selectedFlute = selectClosestVisualizationFlute(
          fluteKey,
          paramKey,
          nextValue
        );

        if (!selectedFlute) {
          hydrateFluteControls(fluteKey, panel, { mode });
          return;
        }

        hydrateFluteControls(fluteKey, panel, { mode });
        renderCurrentFlutes();
        if (selectedFlute.instrument_id !== previousInstrumentId) {
          dispatchVisualizationSelectionChanged({
            fluteKey,
            instrumentId: selectedFlute.instrument_id,
          });
        }
        return;
      }

      const currentFlute = getFluteGeometry(fluteKey);
      const kind = getFluteKind(fluteKey);
      const dynamicRange = getDynamicParamRange(kind, currentFlute, paramKey);
      const clampedValue = clamp(nextValue, dynamicRange.min, dynamicRange.max);

      setFluteParam(fluteKey, paramKey, clampedValue);
      setFluteInstrumentId(fluteKey, null);
      hydrateFluteControls(fluteKey, panel, { mode });
      renderCurrentFlutes();
    });
  }
}

function bindPanelModeToggles(panel) {
  const fluteKey = getFluteKeyFromPanel(panel);
  const cards = panel.querySelectorAll(".slider-card");

  for (const card of cards) {
    const paramKey = card.dataset.param;
    const modeInputs = card.querySelectorAll(".slider-mode input");

    modeInputs.forEach((input, index) => {
      input.addEventListener("change", () => {
        const paramMode = index === 0 ? "fixed" : "variable";
        setFluteParamMode(fluteKey, paramKey, paramMode);
        hydrateFluteControls(fluteKey, panel, { mode: getGraphMode() });
      });
    });
  }
}

export function bindFluteEvents() {
  bindPanelInputs(dom.panels.fluteBase);
  bindPanelInputs(dom.panels.fluteInverse);
  bindPanelModeToggles(dom.panels.fluteBase);
  bindPanelModeToggles(dom.panels.fluteInverse);
}
