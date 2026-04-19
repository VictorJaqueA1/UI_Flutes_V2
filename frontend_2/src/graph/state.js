export const GRAPH_MODES = Object.freeze({
  VISUALIZATION: "visualization",
  CALCULATION: "calculation",
});

const GRAPH_SERIES_META = Object.freeze({
  base: Object.freeze({
    key: "base",
    label: "Base",
    color: "#ff9f5a",
  }),
  inverse: Object.freeze({
    key: "inverse",
    label: "Inversa",
    color: "#45d7ff",
  }),
});

const DEFAULT_MESSAGE =
  "Busca una flauta por ID para cargar curvas reales.";

const graphState = {
  mode: GRAPH_MODES.VISUALIZATION,
  pending: false,
  message: DEFAULT_MESSAGE,
  selectedInstrumentId: null,
  selectedFluteKind: null,
  pairing: null,
  series: {
    base: null,
    inverse: null,
  },
};

function normalizeCurvePoints(curvePoints = []) {
  return [...curvePoints]
    .map((point) => ({
      cutIndex: Number(point.cut_index),
      cutLengthMm: Number(point.cut_length_mm),
      deltaCents: Number(point.delta_cents),
      f1Hz: Number(point.f1_hz),
      f2Hz: Number(point.f2_hz),
    }))
    .filter(
      (point) =>
        Number.isFinite(point.cutLengthMm) && Number.isFinite(point.deltaCents)
    )
    .sort((left, right) => left.cutLengthMm - right.cutLengthMm);
}

function buildSeries(flute, seriesKey) {
  if (!flute) {
    return null;
  }

  const meta = GRAPH_SERIES_META[seriesKey];
  return {
    key: meta.key,
    label: meta.label,
    color: meta.color,
    instrumentId: Number(flute.instrument_id),
    points: normalizeCurvePoints(flute.curve_points),
  };
}

export function getGraphState() {
  return graphState;
}

export function getGraphMode() {
  return graphState.mode;
}

export function setGraphMode(mode) {
  graphState.mode = mode;
}

export function setGraphPending(pending) {
  graphState.pending = pending;
}

export function resetGraphState() {
  graphState.mode = GRAPH_MODES.VISUALIZATION;
  graphState.pending = false;
  graphState.message = DEFAULT_MESSAGE;
  graphState.selectedInstrumentId = null;
  graphState.selectedFluteKind = null;
  graphState.pairing = null;
  graphState.series = {
    base: null,
    inverse: null,
  };
}

export function setGraphVisualization(visualization) {
  graphState.message = null;
  graphState.selectedInstrumentId = Number(visualization.selected_instrument_id);
  graphState.selectedFluteKind = visualization.selected_flute_kind ?? null;
  graphState.pairing = visualization.pairing ?? null;
  graphState.series = {
    base: buildSeries(visualization.base_flute, "base"),
    inverse: buildSeries(visualization.inverse_flute, "inverse"),
  };
}

export function setGraphVisualizationSelection({
  baseFlute = null,
  inverseFlute = null,
} = {}) {
  const nextBaseSeries = buildSeries(baseFlute, "base");
  const nextInverseSeries = buildSeries(inverseFlute, "inverse");

  graphState.message =
    nextBaseSeries || nextInverseSeries ? null : DEFAULT_MESSAGE;
  graphState.selectedInstrumentId = null;
  graphState.selectedFluteKind = null;
  graphState.pairing = null;
  graphState.series = {
    base: nextBaseSeries,
    inverse: nextInverseSeries,
  };
}

export function setGraphComputedCurve(curveResponse) {
  const fluteKind = String(curveResponse.flute_kind);
  const seriesKey = fluteKind === "inverse" ? "inverse" : "base";

  graphState.message = null;
  graphState.selectedInstrumentId = Number(curveResponse.instrument_id);
  graphState.selectedFluteKind = fluteKind;
  graphState.pairing = null;
  graphState.series = {
    base: null,
    inverse: null,
  };
  graphState.series[seriesKey] = buildSeries(
    {
      instrument_id: curveResponse.instrument_id,
      curve_points: curveResponse.curve_points,
    },
    seriesKey
  );
}
