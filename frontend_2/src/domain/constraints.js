import { NUMERICAL_GUARDS, PROJECT_CONSTANTS } from "./constants.js";
import { DEFAULT_CUT_PROTOCOL } from "./cuts.js";
import { PARAM_DEFINITIONS, PARAM_KEYS } from "./params.js";
import {
  clamp,
  getDerivedCutEndDiameter,
  getDiameterAt,
  getPerpendicularDistanceToConeWall,
} from "./geometry.js";

const { EPS } = NUMERICAL_GUARDS;
const {
  HALF_LENGTH,
  L_TOTAL,
  DIAMETER_MIN,
  PARAM_MAX,
  CHIMNEY_MIN,
  CHIMNEY_MAX,
} = PROJECT_CONSTANTS;

function minimizeValidValue(min, max, isValid, iterations = 50) {
  let lo = min;
  let hi = max;

  if (isValid(lo)) {
    return lo;
  }

  if (!isValid(hi)) {
    return max;
  }

  for (let index = 0; index < iterations; index += 1) {
    const mid = (lo + hi) / 2;

    if (isValid(mid)) {
      hi = mid;
    } else {
      lo = mid;
    }
  }

  return hi;
}

function maximizeValidValue(min, max, isValid, iterations = 50) {
  let lo = min;
  let hi = max;

  if (!isValid(lo)) {
    return min;
  }

  if (isValid(hi)) {
    return hi;
  }

  for (let index = 0; index < iterations; index += 1) {
    const mid = (lo + hi) / 2;

    if (isValid(mid)) {
      lo = mid;
    } else {
      hi = mid;
    }
  }

  return lo;
}

export function getPhysicalXRange(flute) {
  return {
    min: flute.d / 2,
    max: HALF_LENGTH - flute.d / 2,
  };
}

export function validatePrimaryRanges(flute) {
  return {
    d: flute.d >= DIAMETER_MIN - EPS && flute.d <= PARAM_MAX + EPS,
    Dt: flute.Dt >= DIAMETER_MIN - EPS && flute.Dt <= PARAM_MAX + EPS,
    y: flute.y >= CHIMNEY_MIN - EPS && flute.y <= CHIMNEY_MAX + EPS,
    a: flute.a >= -EPS && flute.a <= L_TOTAL + EPS,
  };
}

export function validateEmbouchureWithinPlayableHalf(flute) {
  const range = getPhysicalXRange(flute);
  return flute.x >= range.min - EPS && flute.x <= range.max + EPS;
}

export function validateEmbouchureCenterDiameter(kind, flute) {
  return flute.d <= getDiameterAt(kind, flute, flute.x) + EPS;
}

export function validateEmbouchureConeClearance(kind, flute) {
  return getPerpendicularDistanceToConeWall(kind, flute, flute.x) >= flute.d / 2 - EPS;
}

export function validateDerivedCutDiameters(kind, flute, cuts = DEFAULT_CUT_PROTOCOL) {
  return cuts.every((cutLength) => getDerivedCutEndDiameter(kind, flute, cutLength) > EPS);
}

export function validateFluteGeometry(kind, flute, cuts = DEFAULT_CUT_PROTOCOL) {
  const primaryRanges = validatePrimaryRanges(flute);
  const embouchureWithinPlayableHalf = validateEmbouchureWithinPlayableHalf(flute);
  const embouchureCenterDiameter = validateEmbouchureCenterDiameter(kind, flute);
  const embouchureConeClearance = validateEmbouchureConeClearance(kind, flute);
  const positiveCutDiameters = validateDerivedCutDiameters(kind, flute, cuts);

  return {
    ok:
      Object.values(primaryRanges).every(Boolean) &&
      embouchureWithinPlayableHalf &&
      embouchureCenterDiameter &&
      embouchureConeClearance &&
      positiveCutDiameters,
    checks: {
      primaryRanges,
      embouchureWithinPlayableHalf,
      embouchureCenterDiameter,
      embouchureConeClearance,
      positiveCutDiameters,
    },
  };
}

export function sanitizeGeometry(kind, flute) {
  const next = { ...flute };

  next.d = clamp(next.d, DIAMETER_MIN, PARAM_MAX);
  next.Dt = clamp(next.Dt, DIAMETER_MIN, PARAM_MAX);
  next.y = clamp(next.y, CHIMNEY_MIN, CHIMNEY_MAX);
  next.a = clamp(next.a, 0, L_TOTAL);

  const xRange = getPhysicalXRange(next);
  next.x = clamp(next.x, xRange.min, xRange.max);

  return next;
}

export function getDynamicParamRange(kind, flute, paramKey) {
  const staticRange = PARAM_DEFINITIONS[paramKey];
  const currentValue = flute[paramKey];

  const isValidCandidate = (candidateValue) => {
    const candidate = {
      ...flute,
      [paramKey]: candidateValue,
    };

    return validateFluteGeometry(kind, candidate).ok;
  };

  const min = minimizeValidValue(
    staticRange.min,
    currentValue,
    isValidCandidate
  );

  const max = maximizeValidValue(
    currentValue,
    staticRange.max,
    isValidCandidate
  );

  return { min, max };
}

export function getAllDynamicRanges(kind, flute) {
  return PARAM_KEYS.reduce((ranges, key) => {
    ranges[key] = getDynamicParamRange(kind, flute, key);
    return ranges;
  }, {});
}
