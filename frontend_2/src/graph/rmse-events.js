import { fetchRmseRanking } from "./api.js";
import { dom } from "../shared/dom.js";

let pairsData = [];
let currentLimit = Infinity;

// ── utilidades ────────────────────────────────────────

function formatRmse(value) {
  return value.toFixed(4);
}

function buildRangeOptions(total) {
  if (total <= 0) return [];
  if (total <= 50) return [total];
  const options = [];
  let step = 50;
  while (step < total) {
    options.push(step);
    step += 50;
  }
  options.push(step);
  return options;
}

// ── dropdown de pares ─────────────────────────────────

function buildPairsListItems(pairs) {
  const { pairsList } = dom.rmsePanel;
  const visible = currentLimit === Infinity ? pairs : pairs.slice(0, currentLimit);

  pairsList.innerHTML = "";

  for (const pair of visible) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "rmse-floating-list-item";
    button.dataset.baseId = pair.base_instrument_id;
    button.dataset.inverseId = pair.inverse_instrument_id;
    button.dataset.anchorId = pair.anchor_instrument_id;
    button.textContent =
      `${pair.rank}° — Base ${pair.base_instrument_id} · Inv ${pair.inverse_instrument_id} · RMSE: ${formatRmse(pair.rmse)}`;
    pairsList.appendChild(button);
  }
}

function openPairsList() {
  const { pairsTrigger, pairsList } = dom.rmsePanel;
  pairsList.removeAttribute("hidden");
  pairsTrigger.setAttribute("aria-expanded", "true");
}

function closePairsList() {
  const { pairsTrigger, pairsList } = dom.rmsePanel;
  pairsList.setAttribute("hidden", "");
  pairsTrigger.setAttribute("aria-expanded", "false");
}

function isPairsListOpen() {
  return !dom.rmsePanel.pairsList.hasAttribute("hidden");
}

function onPairsTriggerClick() {
  if (isPairsListOpen()) {
    closePairsList();
  } else {
    openPairsList();
  }
}

function onPairsListClick(event) {
  const item = event.target.closest(".rmse-floating-list-item");
  if (!item) return;

  const anchorId = Number(item.dataset.anchorId);
  closePairsList();

  window.dispatchEvent(
    new CustomEvent("flute-visualization-change", {
      detail: { instrumentId: anchorId },
    })
  );
}

// ── dropdown de rango ─────────────────────────────────

function buildRangeListItems(total) {
  const { rangeList, rangeTriggerText } = dom.rmsePanel;
  const options = buildRangeOptions(total);

  rangeList.innerHTML = "";

  for (const limit of options) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "rmse-floating-list-item";
    button.dataset.limit = limit;
    button.textContent = `1 – ${limit}`;
    rangeList.appendChild(button);
  }

  const defaultLimit = options[options.length - 1] ?? total;
  currentLimit = defaultLimit;
  rangeTriggerText.textContent = `1 – ${defaultLimit}`;
}

function openRangeList() {
  const { rangeTrigger, rangeList } = dom.rmsePanel;
  rangeList.removeAttribute("hidden");
  rangeTrigger.setAttribute("aria-expanded", "true");
}

function closeRangeList() {
  const { rangeTrigger, rangeList } = dom.rmsePanel;
  rangeList.setAttribute("hidden", "");
  rangeTrigger.setAttribute("aria-expanded", "false");
}

function isRangeListOpen() {
  return !dom.rmsePanel.rangeList.hasAttribute("hidden");
}

function onRangeTriggerClick() {
  if (isRangeListOpen()) {
    closeRangeList();
  } else {
    openRangeList();
  }
}

function onRangeListClick(event) {
  const item = event.target.closest(".rmse-floating-list-item");
  if (!item) return;

  const limit = Number(item.dataset.limit);
  currentLimit = limit;
  dom.rmsePanel.rangeTriggerText.textContent = `1 – ${limit}`;
  buildPairsListItems(pairsData);
  closeRangeList();
}

// ── handlers de documento (compartidos) ───────────────

function onDocumentClick(event) {
  const { pairsTrigger, pairsList, rangeTrigger, rangeList } = dom.rmsePanel;

  if (
    isPairsListOpen() &&
    !pairsTrigger.contains(event.target) &&
    !pairsList.contains(event.target)
  ) {
    closePairsList();
  }

  if (
    isRangeListOpen() &&
    !rangeTrigger.contains(event.target) &&
    !rangeList.contains(event.target)
  ) {
    closeRangeList();
  }
}

function onDocumentKeydown(event) {
  if (event.key !== "Escape") return;

  if (isPairsListOpen()) {
    closePairsList();
    dom.rmsePanel.pairsTrigger.focus();
  }

  if (isRangeListOpen()) {
    closeRangeList();
    dom.rmsePanel.rangeTrigger.focus();
  }
}

// ── carga inicial ─────────────────────────────────────

async function loadRmseRanking() {
  try {
    const response = await fetchRmseRanking();
    pairsData = response.pairs ?? [];
    buildRangeListItems(pairsData.length);
    buildPairsListItems(pairsData);
  } catch (error) {
    console.error("No se pudo cargar el ranking RMSE:", error);
  }
}

export async function bindRmseEvents() {
  const { pairsTrigger, pairsList, rangeTrigger, rangeList } = dom.rmsePanel;

  await loadRmseRanking();

  pairsTrigger.addEventListener("click", onPairsTriggerClick);
  pairsList.addEventListener("click", onPairsListClick);
  rangeTrigger.addEventListener("click", onRangeTriggerClick);
  rangeList.addEventListener("click", onRangeListClick);
  document.addEventListener("click", onDocumentClick, { capture: true });
  document.addEventListener("keydown", onDocumentKeydown);
}
