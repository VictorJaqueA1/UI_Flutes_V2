import {
  DEFAULT_FLUTE_BASE,
  DEFAULT_FLUTE_INVERSE,
  FLUTE_KINDS,
  PARAM_DEFINITIONS,
  getAllDynamicRanges,
  getParamLabel,
} from "../domain/index.js";

const PARAM_ORDER = Object.freeze(["d", "x", "a", "y", "Dt"]);
const FLOAT_EPS = 1e-6;
const VISUALIZATION_PARAM_MODE = Object.freeze({
  FIXED: "fixed",
  VARIABLE: "variable",
});

function cloneDefaultParamModes() {
  return {
    d: VISUALIZATION_PARAM_MODE.VARIABLE,
    x: VISUALIZATION_PARAM_MODE.VARIABLE,
    a: VISUALIZATION_PARAM_MODE.VARIABLE,
    y: VISUALIZATION_PARAM_MODE.VARIABLE,
    Dt: VISUALIZATION_PARAM_MODE.VARIABLE,
  };
}

export const fluteState = {
  base: { ...DEFAULT_FLUTE_BASE },
  inverse: { ...DEFAULT_FLUTE_INVERSE },
};

const fluteCatalogState = {
  base: [],
  inverse: [],
};

const fluteSelectionState = {
  base: {
    displayInstrumentId: null,
    visualizationInstrumentId: null,
    paramModes: cloneDefaultParamModes(),
  },
  inverse: {
    displayInstrumentId: null,
    visualizationInstrumentId: null,
    paramModes: cloneDefaultParamModes(),
  },
};

function getKindByKey(fluteKey) {
  return fluteKey === "base" ? FLUTE_KINDS.BASE : FLUTE_KINDS.INVERSE;
}

function normalizeGeometry(geometry, fallbackKind) {
  return {
    kind: String(geometry.kind ?? fallbackKind),
    d: Number(geometry.d),
    x: Number(geometry.x),
    y: Number(geometry.y),
    a: Number(geometry.a),
    Dt: Number(geometry.Dt),
    L: Number(geometry.L ?? fluteState[fallbackKind].L ?? 570.0),
    Di: Number(geometry.Di ?? fluteState[fallbackKind].Di ?? 18.0),
  };
}

function normalizeCurvePoint(point) {
  return {
    cut_index: Number(point.cut_index),
    cut_length_mm: Number(point.cut_length_mm),
    f1_hz: Number(point.f1_hz),
    f2_hz: Number(point.f2_hz),
    delta_cents: Number(point.delta_cents),
  };
}

function normalizeCatalogFlute(flute, fluteKey) {
  return {
    instrument_id: Number(flute.instrument_id),
    flute_kind: String(flute.flute_kind ?? getKindByKey(fluteKey)),
    geometry: normalizeGeometry(flute.geometry ?? flute, fluteKey),
    curve_points: (flute.curve_points ?? []).map(normalizeCurvePoint),
  };
}

function almostEqual(left, right) {
  return Math.abs(Number(left) - Number(right)) <= FLOAT_EPS;
}

function compareCatalogFlutes(left, right) {
  return Number(left.instrument_id) - Number(right.instrument_id);
}

function getCatalogPool(fluteKey, excludeParamKey = null) {
  const catalog = fluteCatalogState[fluteKey];
  if (!catalog.length) {
    return [];
  }

  const currentGeometry = fluteState[fluteKey];
  const paramModes = fluteSelectionState[fluteKey].paramModes;
  const filtered = catalog.filter((flute) =>
    PARAM_ORDER.every((paramKey) => {
      if (paramKey === excludeParamKey) {
        return true;
      }

      if (paramModes[paramKey] !== VISUALIZATION_PARAM_MODE.FIXED) {
        return true;
      }

      return almostEqual(flute.geometry[paramKey], currentGeometry[paramKey]);
    })
  );

  if (filtered.length) {
    return filtered;
  }

  const currentVisualizationFlute = getCurrentVisualizationFlute(fluteKey);
  return currentVisualizationFlute ? [currentVisualizationFlute] : catalog;
}

function getSecondaryDistance(candidateGeometry, currentGeometry, movedParamKey) {
  return PARAM_ORDER.reduce((sum, paramKey) => {
    if (paramKey === movedParamKey) {
      return sum;
    }

    return sum + Math.abs(candidateGeometry[paramKey] - currentGeometry[paramKey]);
  }, 0);
}

function buildDisplayInstrumentLabel(instrumentId) {
  return instrumentId ? `ID: ${instrumentId}` : "ID: --";
}

function formatValue(value) {
  return `${Number(value).toFixed(1)} mm`;
}

function formatRange(min, max) {
  const formatPart = (value) => String(Math.round(value));

  return `Rango ${formatPart(min)} - ${formatPart(max)} mm`;
}

function getStaticRangeForParam(paramKey) {
  const definition = PARAM_DEFINITIONS[paramKey];
  return {
    min: definition.min,
    max: definition.max,
  };
}

export function getFluteGeometry(fluteKey) {
  return { ...fluteState[fluteKey] };
}

export function setFluteParam(fluteKey, paramKey, value) {
  fluteState[fluteKey] = {
    ...fluteState[fluteKey],
    [paramKey]: value,
  };
}

export function replaceFluteGeometry(fluteKey, geometry) {
  fluteState[fluteKey] = {
    ...fluteState[fluteKey],
    ...normalizeGeometry(geometry, fluteKey),
  };
}

export function getFluteInstrumentId(fluteKey) {
  return fluteSelectionState[fluteKey].displayInstrumentId;
}

export function setFluteInstrumentId(fluteKey, instrumentId) {
  fluteSelectionState[fluteKey].displayInstrumentId =
    instrumentId == null ? null : Number(instrumentId);
}

export function getVisualizationInstrumentId(fluteKey) {
  return fluteSelectionState[fluteKey].visualizationInstrumentId;
}

export function setVisualizationInstrumentId(fluteKey, instrumentId) {
  fluteSelectionState[fluteKey].visualizationInstrumentId =
    instrumentId == null ? null : Number(instrumentId);
}

export function getFluteParamMode(fluteKey, paramKey) {
  return fluteSelectionState[fluteKey].paramModes[paramKey];
}

export function setFluteParamMode(fluteKey, paramKey, mode) {
  fluteSelectionState[fluteKey].paramModes[paramKey] = mode;
}

export function setFluteCatalog(fluteKey, flutes) {
  fluteCatalogState[fluteKey] = [...flutes]
    .map((flute) => normalizeCatalogFlute(flute, fluteKey))
    .sort(compareCatalogFlutes);
}

export function getFluteCatalog(fluteKey) {
  return [...fluteCatalogState[fluteKey]];
}

export function upsertFluteCatalogFlute(fluteKey, flute) {
  const normalizedFlute = normalizeCatalogFlute(flute, fluteKey);
  const catalog = [...fluteCatalogState[fluteKey]];
  const existingIndex = catalog.findIndex(
    (candidate) => candidate.instrument_id === normalizedFlute.instrument_id
  );

  if (existingIndex >= 0) {
    catalog[existingIndex] = normalizedFlute;
  } else {
    catalog.push(normalizedFlute);
  }

  catalog.sort(compareCatalogFlutes);
  fluteCatalogState[fluteKey] = catalog;
}

export function getCatalogFluteById(fluteKey, instrumentId) {
  const normalizedId = Number(instrumentId);
  return (
    fluteCatalogState[fluteKey].find(
      (flute) => flute.instrument_id === normalizedId
    ) ?? null
  );
}

export function getCurrentVisualizationFlute(fluteKey) {
  const instrumentId = getVisualizationInstrumentId(fluteKey);
  if (instrumentId == null) {
    return null;
  }

  return getCatalogFluteById(fluteKey, instrumentId);
}

export function selectVisualizationFluteById(
  fluteKey,
  instrumentId,
  {
    updateDisplayId = true,
    updateVisualizationId = true,
  } = {}
) {
  const flute = getCatalogFluteById(fluteKey, instrumentId);
  if (!flute) {
    return null;
  }

  replaceFluteGeometry(fluteKey, flute.geometry);

  if (updateDisplayId) {
    setFluteInstrumentId(fluteKey, flute.instrument_id);
  }

  if (updateVisualizationId) {
    setVisualizationInstrumentId(fluteKey, flute.instrument_id);
  }

  return flute;
}

export function selectFirstVisualizationFlute(fluteKey) {
  const [firstFlute] = fluteCatalogState[fluteKey];
  if (!firstFlute) {
    return null;
  }

  return selectVisualizationFluteById(fluteKey, firstFlute.instrument_id);
}

export function selectClosestVisualizationFlute(fluteKey, paramKey, targetValue) {
  const candidatePool = getCatalogPool(fluteKey, paramKey);
  if (!candidatePool.length) {
    return null;
  }

  const currentGeometry = fluteState[fluteKey];
  const bestCandidate = [...candidatePool].sort((left, right) => {
    const movedDiffLeft = Math.abs(left.geometry[paramKey] - targetValue);
    const movedDiffRight = Math.abs(right.geometry[paramKey] - targetValue);

    if (!almostEqual(movedDiffLeft, movedDiffRight)) {
      return movedDiffLeft - movedDiffRight;
    }

    const secondaryLeft = getSecondaryDistance(
      left.geometry,
      currentGeometry,
      paramKey
    );
    const secondaryRight = getSecondaryDistance(
      right.geometry,
      currentGeometry,
      paramKey
    );

    if (!almostEqual(secondaryLeft, secondaryRight)) {
      return secondaryLeft - secondaryRight;
    }

    return left.instrument_id - right.instrument_id;
  })[0];

  return selectVisualizationFluteById(fluteKey, bestCandidate.instrument_id);
}

export function getVisualizationParamRange(fluteKey, paramKey) {
  const candidatePool = getCatalogPool(fluteKey, paramKey);
  const values = candidatePool.map((flute) => Number(flute.geometry[paramKey]));

  if (!values.length) {
    const currentValue = Number(fluteState[fluteKey][paramKey]);
    return {
      min: currentValue,
      max: currentValue,
    };
  }

  return {
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

export function hydrateFluteControls(fluteKey, panel, options = {}) {
  const flute = fluteState[fluteKey];
  const kind = getKindByKey(fluteKey);
  const mode = options.mode ?? "calculation";
  const isVisualizationMode =
    mode === "visualization" && fluteCatalogState[fluteKey].length > 0;
  const dynamicRanges = getAllDynamicRanges(kind, flute);
  const cards = panel.querySelectorAll(".slider-card");
  const idLabel = panel.querySelector("[data-flute-id-label]");

  if (idLabel) {
    idLabel.textContent = buildDisplayInstrumentLabel(getFluteInstrumentId(fluteKey));
  }

  for (const card of cards) {
    const paramKey = card.dataset.param;
    const input = card.querySelector(".slider-input");
    const valueNode = card.querySelector(".slider-value");
    const rangeNode = card.querySelector(".slider-range");
    const titleNode = card.querySelector(".slider-title");
    const modeInputs = card.querySelectorAll(".slider-mode input");
    const staticRange = getStaticRangeForParam(paramKey);
    const activeRange = dynamicRanges[paramKey];

    titleNode.textContent = getParamLabel(paramKey, kind);
    input.min = String(staticRange.min);
    input.max = String(staticRange.max);
    input.step = paramKey === "a" ? "1" : "0.1";
    input.value = String(flute[paramKey]);
    valueNode.textContent = formatValue(flute[paramKey]);
    rangeNode.textContent = formatRange(activeRange.min, activeRange.max);

    if (modeInputs.length >= 2) {
      const paramMode = getFluteParamMode(fluteKey, paramKey);
      modeInputs[0].checked = paramMode === VISUALIZATION_PARAM_MODE.FIXED;
      modeInputs[1].checked = paramMode === VISUALIZATION_PARAM_MODE.VARIABLE;
    }
  }
}

export function hydrateAllFluteControls(panels, options = {}) {
  hydrateFluteControls("base", panels.fluteBase, options);
  hydrateFluteControls("inverse", panels.fluteInverse, options);
}

export function getFluteParamOrder() {
  return [...PARAM_ORDER];
}

export function getVisualizationParamModes() {
  return {
    base: { ...fluteSelectionState.base.paramModes },
    inverse: { ...fluteSelectionState.inverse.paramModes },
  };
}
