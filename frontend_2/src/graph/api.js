const BACKEND_PORT = "8000";

function getBackendBaseUrl() {
  const protocol = window.location.protocol === "file:" ? "http:" : window.location.protocol;
  const hostname = window.location.hostname || "127.0.0.1";
  return `${protocol}//${hostname}:${BACKEND_PORT}/api`;
}

async function buildError(response) {
  try {
    const payload = await response.json();

    if (typeof payload?.detail === "string" && payload.detail.trim()) {
      return payload.detail;
    }
  } catch (error) {
    console.debug("No se pudo parsear el error JSON del backend.", error);
  }

  return `${response.status} ${response.statusText}`.trim();
}

export async function fetchFluteVisualization(instrumentId) {
  const response = await fetch(
    `${getBackendBaseUrl()}/flutes/${instrumentId}/visualization`
  );

  if (!response.ok) {
    throw new Error(await buildError(response));
  }

  return response.json();
}

export async function fetchFluteCatalog() {
  const response = await fetch(`${getBackendBaseUrl()}/flutes/catalog`);

  if (!response.ok) {
    throw new Error(await buildError(response));
  }

  return response.json();
}

export async function fetchRmseRanking() {
  const response = await fetch(`${getBackendBaseUrl()}/flutes/rmse-ranking`);

  if (!response.ok) {
    throw new Error(await buildError(response));
  }

  return response.json();
}

export async function computeFluteCurve(payload) {
  const response = await fetch(`${getBackendBaseUrl()}/flutes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await buildError(response));
  }

  return response.json();
}
