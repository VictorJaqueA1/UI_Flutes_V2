import { PROJECT_CONSTANTS } from "./constants.js";

const { CUT_COUNT, L_TOTAL, HALF_LENGTH } = PROJECT_CONSTANTS;

export function generateCutProtocol(count = CUT_COUNT) {
  if (count <= 1) {
    return [L_TOTAL];
  }

  const step = (L_TOTAL - HALF_LENGTH) / (count - 1);
  const cuts = [];

  for (let index = 0; index < count; index += 1) {
    cuts.push(L_TOTAL - step * index);
  }

  return cuts;
}

export const DEFAULT_CUT_PROTOCOL = Object.freeze(generateCutProtocol());
