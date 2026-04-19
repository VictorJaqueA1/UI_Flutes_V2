import { PROJECT_CONSTANTS } from "../domain/constants.js";
import { dom } from "../shared/dom.js";
import {
  getCatalogFluteById,
  getCurrentVisualizationFlute,
  getFluteGeometry,
  getVisualizationInstrumentId,
  hydrateAllFluteControls,
  selectFirstVisualizationFlute,
  selectVisualizationFluteById,
  setFluteCatalog,
  setFluteInstrumentId,
  setVisualizationInstrumentId,
  upsertFluteCatalogFlute,
} from "../flutes/state.js";
import { renderAllFluteSketches } from "../flutes/render.js";
import {
  computeFluteCurve,
  fetchFluteCatalog,
  fetchFluteVisualization,
} from "./api.js";
import { renderGraphFrame } from "./render.js";
import {
  GRAPH_MODES,
  getGraphMode,
  getGraphState,
  setGraphComputedCurve,
  setGraphMode,
  setGraphPending,
  setGraphVisualization,
  setGraphVisualizationSelection,
} from "./state.js";

let visualizationRequestVersion = 0;

function parseInstrumentId(rawValue) {
  const trimmed = rawValue.trim();

  if (!/^\d+$/.test(trimmed)) {
    return null;
  }

  const instrumentId = Number(trimmed);
  return instrumentId > 0 ? instrumentId : null;
}

function readModeFromDom() {
  const selectedMode = dom.graphControls.modeRadios.find((radio) => radio.checked);
  return selectedMode?.dataset.graphMode ?? GRAPH_MODES.VISUALIZATION;
}

function renderCurrentFluteSketches() {
  renderAllFluteSketches({
    base: getFluteGeometry("base"),
    inverse: getFluteGeometry("inverse"),
  });
}

function pickRandomItem(items) {
  if (!Array.isArray(items) || items.length === 0) {
    return null;
  }

  const index = Math.floor(Math.random() * items.length);
  return items[index] ?? null;
}

function applyVisualizationResponse(visualization) {
  const baseFlute = visualization.base_flute ?? null;
  const inverseFlute = visualization.inverse_flute ?? null;

  if (baseFlute) {
    upsertFluteCatalogFlute("base", baseFlute);
    selectVisualizationFluteById("base", baseFlute.instrument_id, {
      updateDisplayId: true,
      updateVisualizationId: true,
    });
  } else {
    setFluteInstrumentId("base", null);
    setVisualizationInstrumentId("base", null);
  }

  if (inverseFlute) {
    upsertFluteCatalogFlute("inverse", inverseFlute);
    selectVisualizationFluteById("inverse", inverseFlute.instrument_id, {
      updateDisplayId: true,
      updateVisualizationId: true,
    });
  } else {
    setFluteInstrumentId("inverse", null);
    setVisualizationInstrumentId("inverse", null);
  }

  dom.graphControls.idInput.value = String(visualization.selected_instrument_id ?? "");
  hydrateAllFluteControls(dom.panels, {
    mode: GRAPH_MODES.VISUALIZATION,
  });
  renderCurrentFluteSketches();
  setGraphVisualization(visualization);
  renderGraphFrame();
}

async function synchronizeVisualizationPairing(
  instrumentId,
  { fallbackToLocalSelection = true, showAlertOnError = false } = {}
) {
  if (instrumentId == null) {
    if (fallbackToLocalSelection) {
      syncVisualizationSelectionsToUi();
    }
    return null;
  }

  const requestVersion = ++visualizationRequestVersion;

  try {
    const visualization = await fetchFluteVisualization(instrumentId);
    if (
      requestVersion !== visualizationRequestVersion ||
      getGraphMode() !== GRAPH_MODES.VISUALIZATION
    ) {
      return null;
    }

    applyVisualizationResponse(visualization);
    return visualization;
  } catch (error) {
    if (requestVersion !== visualizationRequestVersion) {
      return null;
    }

    const message =
      error instanceof Error
        ? error.message
        : "No se pudo sincronizar la visualizacion emparejada.";

    if (fallbackToLocalSelection) {
      syncVisualizationSelectionsToUi();
    }

    if (showAlertOnError) {
      window.alert(message);
    } else {
      console.warn(message, error);
    }

    return null;
  }
}

function seedRandomVisualizationSelection(catalog) {
  const baseCatalog = catalog.base_flutes ?? [];
  const inverseCatalog = catalog.inverse_flutes ?? [];
  const randomBase = pickRandomItem(baseCatalog);

  if (!randomBase) {
    const fallbackInverse = pickRandomItem(inverseCatalog);
    if (fallbackInverse) {
      setVisualizationInstrumentId("inverse", fallbackInverse.instrument_id);
    }
    return fallbackInverse?.instrument_id ?? null;
  }

  setVisualizationInstrumentId("base", randomBase.instrument_id);
  return randomBase.instrument_id;
}

function refreshGraphFromVisualizationSelection() {
  setGraphVisualizationSelection({
    baseFlute: getCurrentVisualizationFlute("base"),
    inverseFlute: getCurrentVisualizationFlute("inverse"),
  });
  renderGraphFrame();
}

function syncVisualizationSelectionsToUi() {
  const baseFlute =
    selectVisualizationFluteById("base", getCurrentVisualizationFlute("base")?.instrument_id, {
      updateDisplayId: true,
      updateVisualizationId: true,
    }) ?? selectFirstVisualizationFlute("base");

  const inverseFlute =
    selectVisualizationFluteById(
      "inverse",
      getCurrentVisualizationFlute("inverse")?.instrument_id,
      {
        updateDisplayId: true,
        updateVisualizationId: true,
      }
    ) ?? selectFirstVisualizationFlute("inverse");

  hydrateAllFluteControls(dom.panels, {
    mode: GRAPH_MODES.VISUALIZATION,
  });
  renderCurrentFluteSketches();
  setGraphVisualizationSelection({
    baseFlute,
    inverseFlute,
  });
  renderGraphFrame();
}

function setControlsAvailability() {
  const mode = getGraphMode();
  const { pending } = getGraphState();
  const {
    idInput,
    modeRadios,
    calculateBaseButton,
    calculateInverseButton,
    searchBaseButton,
    searchInverseButton,
  } = dom.graphControls;

  const isVisualization = mode === GRAPH_MODES.VISUALIZATION;
  const disableSearch = pending || !isVisualization;
  const disableCalculation = pending || isVisualization;

  idInput.disabled = disableSearch;
  searchBaseButton.disabled = disableSearch;
  searchInverseButton.disabled = disableSearch;
  calculateBaseButton.disabled = disableCalculation;
  calculateInverseButton.disabled = disableCalculation;

  modeRadios.forEach((radio) => {
    radio.disabled = pending;
  });

  document.querySelectorAll(".slider-input, .slider-mode input").forEach((input) => {
    input.disabled = pending;
  });
}

function getPreferredVisualizationInstrumentId(previousMode) {
  const { selectedInstrumentId } = getGraphState();

  if (
    previousMode === GRAPH_MODES.CALCULATION &&
    selectedInstrumentId != null
  ) {
    return selectedInstrumentId;
  }

  return (
    selectedInstrumentId ??
    getVisualizationInstrumentId("base") ??
    getVisualizationInstrumentId("inverse")
  );
}

function updateModeFromDom() {
  const previousMode = getGraphMode();
  const nextMode = readModeFromDom();
  setGraphMode(nextMode);

  if (nextMode === GRAPH_MODES.VISUALIZATION) {
    const preferredInstrumentId =
      getPreferredVisualizationInstrumentId(previousMode);
    void synchronizeVisualizationPairing(preferredInstrumentId);
  } else {
    visualizationRequestVersion += 1;
    hydrateAllFluteControls(dom.panels, {
      mode: GRAPH_MODES.CALCULATION,
    });
    renderCurrentFluteSketches();
  }

  setControlsAvailability();
}

function buildComputePayload(fluteKey) {
  const flute = getFluteGeometry(fluteKey);

  return {
    kind: flute.kind,
    d: Number(flute.d),
    x: Number(flute.x),
    y: Number(flute.y),
    a: Number(flute.a),
    Dt: Number(flute.Dt),
    L: Number(flute.L ?? PROJECT_CONSTANTS.L_TOTAL),
    Di: Number(flute.Di ?? PROJECT_CONSTANTS.DIAMETER_INTERNAL),
  };
}

function syncComputedFluteToCatalog(fluteKey, payload, curveResponse) {
  upsertFluteCatalogFlute(fluteKey, {
    instrument_id: curveResponse.instrument_id,
    flute_kind: payload.kind,
    geometry: payload,
    curve_points: curveResponse.curve_points,
  });
  setFluteInstrumentId(fluteKey, curveResponse.instrument_id);
  setVisualizationInstrumentId(fluteKey, curveResponse.instrument_id);
}

async function applyVisualizationSearch(fluteKey) {
  if (getGraphMode() !== GRAPH_MODES.VISUALIZATION) {
    window.alert("Cambia a modo Visualizacion para buscar curvas por ID.");
    return;
  }

  const instrumentId = parseInstrumentId(dom.graphControls.idInput.value);
  if (!instrumentId) {
    window.alert("Ingresa un ID numerico valido para buscar una flauta.");
    return;
  }

  const selectedFlute = selectVisualizationFluteById(fluteKey, instrumentId);
  if (!selectedFlute) {
    window.alert(`No existe una flauta ${fluteKey} con ID ${instrumentId} en el catalogo cargado.`);
    return;
  }

  await synchronizeVisualizationPairing(selectedFlute.instrument_id, {
    fallbackToLocalSelection: true,
    showAlertOnError: true,
  });
}

async function initializeVisualizationCatalog() {
  try {
    const catalog = await fetchFluteCatalog();
    setFluteCatalog("base", catalog.base_flutes ?? []);
    setFluteCatalog("inverse", catalog.inverse_flutes ?? []);
    const initialInstrumentId = seedRandomVisualizationSelection(catalog);
    await synchronizeVisualizationPairing(initialInstrumentId);
    setControlsAvailability();
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "No se pudo cargar el catalogo de visualizacion.";

    window.alert(`No se pudo cargar el catalogo inicial: ${message}`);
  }
}

async function computeCurve(fluteKey) {
  if (getGraphMode() !== GRAPH_MODES.CALCULATION) {
    window.alert("Cambia a modo Calculo de geometria para calcular una curva.");
    return;
  }

  const payload = buildComputePayload(fluteKey);
  const fluteLabel = fluteKey === "base" ? "base" : "inversa";

  setGraphPending(true);
  setControlsAvailability();

  try {
    const curveResponse = await computeFluteCurve(payload);
    syncComputedFluteToCatalog(fluteKey, payload, curveResponse);
    hydrateAllFluteControls(dom.panels, {
      mode: GRAPH_MODES.CALCULATION,
    });
    setGraphComputedCurve(curveResponse);
    dom.graphControls.idInput.value = String(curveResponse.instrument_id);
    renderGraphFrame();
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "No se pudo calcular la curva solicitada.";

    window.alert(`No se pudo calcular la flauta ${fluteLabel}: ${message}`);
  } finally {
    setGraphPending(false);
    setControlsAvailability();
  }
}

function handleSearchEnter(event) {
  if (event.key !== "Enter") {
    return;
  }

  event.preventDefault();
  const instrumentId = parseInstrumentId(dom.graphControls.idInput.value);

  if (instrumentId == null) {
    void applyVisualizationSearch("base");
    return;
  }

  if (getCatalogFluteById("base", instrumentId)) {
    void applyVisualizationSearch("base");
    return;
  }

  if (getCatalogFluteById("inverse", instrumentId)) {
    void applyVisualizationSearch("inverse");
    return;
  }

  void applyVisualizationSearch("base");
}

export function bindGraphEvents() {
  const {
    idInput,
    modeRadios,
    calculateBaseButton,
    calculateInverseButton,
    searchBaseButton,
    searchInverseButton,
  } = dom.graphControls;

  updateModeFromDom();
  void initializeVisualizationCatalog();

  modeRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      updateModeFromDom();
    });
  });

  searchBaseButton.addEventListener("click", () => {
    void applyVisualizationSearch("base");
  });
  searchInverseButton.addEventListener("click", () => {
    void applyVisualizationSearch("inverse");
  });
  idInput.addEventListener("keydown", handleSearchEnter);

  calculateBaseButton.addEventListener("click", () => {
    void computeCurve("base");
  });
  calculateInverseButton.addEventListener("click", () => {
    void computeCurve("inverse");
  });
  window.addEventListener("flute-visualization-change", (event) => {
    if (getGraphMode() !== GRAPH_MODES.VISUALIZATION) {
      return;
    }

    const instrumentId = event.detail?.instrumentId;

    if (instrumentId == null) {
      refreshGraphFromVisualizationSelection();
      return;
    }

    void synchronizeVisualizationPairing(instrumentId);
  });
}
