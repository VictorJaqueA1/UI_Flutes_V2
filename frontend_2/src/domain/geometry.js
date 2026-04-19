import { FLUTE_KINDS, NUMERICAL_GUARDS, PROJECT_CONSTANTS } from "./constants.js";

const { EPS } = NUMERICAL_GUARDS;
const { DIAMETER_INTERNAL, L_TOTAL } = PROJECT_CONSTANTS;

export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function getUpperWallY(kind, flute, x) {
  const clampedX = clamp(x, 0, L_TOTAL);

  if (kind === FLUTE_KINDS.BASE) {
    if (clampedX <= flute.a) {
      return DIAMETER_INTERNAL / 2;
    }

    const coneLength = Math.max(L_TOTAL - flute.a, EPS);
    const t = (clampedX - flute.a) / coneLength;
    const diameter = DIAMETER_INTERNAL + (flute.Dt - DIAMETER_INTERNAL) * t;
    return diameter / 2;
  }

  if (clampedX <= flute.a) {
    const coneLength = Math.max(flute.a, EPS);
    const t = clampedX / coneLength;
    const diameter = flute.Dt + (DIAMETER_INTERNAL - flute.Dt) * t;
    return diameter / 2;
  }

  return DIAMETER_INTERNAL / 2;
}

export function getDiameterAt(kind, flute, x) {
  return getUpperWallY(kind, flute, x) * 2;
}

export function getConeUpperWallLine(kind, flute) {
  if (kind === FLUTE_KINDS.BASE) {
    if (flute.a >= L_TOTAL - EPS) {
      return null;
    }

    const x1 = flute.a;
    const x2 = L_TOTAL;
    const y1 = DIAMETER_INTERNAL / 2;
    const y2 = flute.Dt / 2;
    const slope = (y2 - y1) / Math.max(x2 - x1, EPS);
    const intercept = y1 - slope * x1;

    return { x1, x2, slope, intercept };
  }

  if (flute.a <= EPS) {
    return null;
  }

  const x1 = 0;
  const x2 = flute.a;
  const y1 = flute.Dt / 2;
  const y2 = DIAMETER_INTERNAL / 2;
  const slope = (y2 - y1) / Math.max(x2 - x1, EPS);
  const intercept = y1 - slope * x1;

  return { x1, x2, slope, intercept };
}

export function getPerpendicularDistanceToConeWall(kind, flute, x) {
  const line = getConeUpperWallLine(kind, flute);

  if (!line || x < line.x1 - EPS || x > line.x2 + EPS) {
    return getDiameterAt(kind, flute, x) / 2;
  }

  const { slope, intercept } = line;
  return Math.abs(slope * x - 0 + intercept) / Math.sqrt(slope ** 2 + 1);
}

export function getDerivedCutEndDiameter(kind, flute, cutLength) {
  return getDiameterAt(kind, flute, cutLength);
}
