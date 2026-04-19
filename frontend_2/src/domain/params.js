import { FLUTE_KINDS, PROJECT_CONSTANTS } from "./constants.js";

const {
  DIAMETER_MIN,
  PARAM_MAX,
  CHIMNEY_MIN,
  CHIMNEY_MAX,
  BREAKPOINT_MIN,
  BREAKPOINT_MAX,
} = PROJECT_CONSTANTS;

export const PARAM_KEYS = Object.freeze(["d", "x", "y", "a", "Dt"]);

export const PARAM_DEFINITIONS = Object.freeze({
  d: Object.freeze({
    key: "d",
    label: "Diámetro embocadura",
    unit: "mm",
    min: DIAMETER_MIN,
    max: PARAM_MAX,
    defaultValue: 9.0,
  }),
  x: Object.freeze({
    key: "x",
    label: "Posición de embocadura",
    unit: "mm",
    min: 0,
    max: PROJECT_CONSTANTS.HALF_LENGTH,
    defaultValue: 160.0,
  }),
  y: Object.freeze({
    key: "y",
    label: "Altura de chimenea",
    unit: "mm",
    min: CHIMNEY_MIN,
    max: CHIMNEY_MAX,
    defaultValue: 6.0,
  }),
  a: Object.freeze({
    key: "a",
    label: "Breakpoint",
    unit: "mm",
    min: BREAKPOINT_MIN,
    max: BREAKPOINT_MAX,
    defaultValue: 150.0,
  }),
  Dt: Object.freeze({
    key: "Dt",
    unit: "mm",
    min: DIAMETER_MIN,
    max: PARAM_MAX,
    defaultValue: 12.0,
  }),
});

export function getDtLabel(kind) {
  if (kind === FLUTE_KINDS.BASE) {
    return "Diámetro de salida";
  }

  return "Diámetro de entrada";
}

export function getParamLabel(key, kind) {
  if (key === "Dt") {
    return getDtLabel(kind);
  }

  return PARAM_DEFINITIONS[key].label;
}
