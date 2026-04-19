import { FLUTE_KINDS } from "./constants.js";

const DEFAULT_VALUES = Object.freeze({
  d: 9.0,
  x: 160.0,
  y: 6.0,
  a: 150.0,
  Dt: 12.0,
});

export function createDefaultFluteGeometry(kind) {
  return {
    kind,
    ...DEFAULT_VALUES,
  };
}

export const DEFAULT_FLUTE_BASE = Object.freeze(
  createDefaultFluteGeometry(FLUTE_KINDS.BASE)
);

export const DEFAULT_FLUTE_INVERSE = Object.freeze(
  createDefaultFluteGeometry(FLUTE_KINDS.INVERSE)
);
