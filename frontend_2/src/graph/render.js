import { dom } from "../shared/dom.js";
import { getGraphState } from "./state.js";

function createLinearTicks(start, end, count) {
  const step = (end - start) / (count - 1);
  return Array.from({ length: count }, (_, index) => start + step * index);
}

const X_AXIS = Object.freeze({
  min: 285,
  max: 570,
  ticks: Object.freeze(
    createLinearTicks(285, 570, 10).map((value) => Math.round(value))
  ),
});

const FALLBACK_Y_TICKS = Object.freeze([100, 80, 60, 40, 20, 0, -20, -40, -60, -80]);

const COLORS = Object.freeze({
  canvasBackground: "rgba(10, 15, 25, 0.94)",
  plotBackground: "rgba(15, 23, 40, 0.92)",
  plotBorder: "rgba(173, 195, 232, 0.14)",
  axis: "rgba(232, 240, 255, 0.82)",
  axisText: "#eef4ff",
  grid: "rgba(173, 195, 232, 0.08)",
  zeroGrid: "rgba(173, 195, 232, 0.18)",
  tickText: "rgba(159, 176, 203, 0.92)",
  hintText: "rgba(159, 176, 203, 0.68)",
});

function resizeCanvasToDisplaySize(canvas) {
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.floor(canvas.clientWidth * dpr));
  const height = Math.max(1, Math.floor(canvas.clientHeight * dpr));

  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }

  const ctx = canvas.getContext("2d");
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(dpr, dpr);
  return ctx;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function drawText(ctx, text, x, y, options = {}) {
  const {
    color = COLORS.axisText,
    font = "600 12px 'Segoe UI'",
    align = "left",
    baseline = "alphabetic",
    rotation = 0,
  } = options;

  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(rotation);
  ctx.fillStyle = color;
  ctx.font = font;
  ctx.textAlign = align;
  ctx.textBaseline = baseline;
  ctx.fillText(text, 0, 0);
  ctx.restore();
}

function niceNumber(value, shouldRound) {
  const exponent = Math.floor(Math.log10(value));
  const fraction = value / 10 ** exponent;
  let niceFraction;

  if (shouldRound) {
    if (fraction < 1.5) {
      niceFraction = 1;
    } else if (fraction < 3) {
      niceFraction = 2;
    } else if (fraction < 7) {
      niceFraction = 5;
    } else {
      niceFraction = 10;
    }
  } else if (fraction <= 1) {
    niceFraction = 1;
  } else if (fraction <= 2) {
    niceFraction = 2;
  } else if (fraction <= 5) {
    niceFraction = 5;
  } else {
    niceFraction = 10;
  }

  return niceFraction * 10 ** exponent;
}

function buildYScale(seriesList) {
  const values = seriesList.flatMap((series) =>
    series.points.map((point) => point.deltaCents)
  );

  if (!values.length) {
    return {
      ticks: FALLBACK_Y_TICKS,
      min: FALLBACK_Y_TICKS[FALLBACK_Y_TICKS.length - 1],
      max: FALLBACK_Y_TICKS[0],
      step: 20,
    };
  }

  let minimum = Math.min(...values);
  let maximum = Math.max(...values);

  if (minimum === maximum) {
    const padding = Math.max(Math.abs(minimum) * 0.1, 10);
    minimum -= padding;
    maximum += padding;
  } else {
    const padding = Math.max((maximum - minimum) * 0.12, 10);
    minimum -= padding;
    maximum += padding;
  }

  const roughRange = Math.max(maximum - minimum, 1);
  const roughStep = roughRange / 7;
  const step = niceNumber(roughStep, true);
  const niceMinimum = Math.floor(minimum / step) * step;
  const niceMaximum = Math.ceil(maximum / step) * step;
  const ticks = [];

  for (let value = niceMaximum; value >= niceMinimum - step * 0.25; value -= step) {
    ticks.push(Number(value.toFixed(12)));

    if (ticks.length > 24) {
      break;
    }
  }

  return {
    ticks,
    min: ticks[ticks.length - 1],
    max: ticks[0],
    step,
  };
}

function formatTickValue(value, step) {
  if (step >= 100) {
    return value.toFixed(0);
  }

  if (step >= 10) {
    return value.toFixed(0);
  }

  if (step >= 1) {
    return value.toFixed(1);
  }

  return value.toFixed(2);
}

function getXPosition(cutLengthMm, plotLeft, plotWidth) {
  const clampedCutLength = clamp(cutLengthMm, X_AXIS.min, X_AXIS.max);
  const ratio = (clampedCutLength - X_AXIS.min) / (X_AXIS.max - X_AXIS.min);
  return plotLeft + ratio * plotWidth;
}

function getYPosition(value, plotTop, plotHeight, yScale) {
  const ratio = (yScale.max - value) / Math.max(yScale.max - yScale.min, 1e-9);
  return plotTop + ratio * plotHeight;
}

function drawCurve(ctx, series, plotLeft, plotTop, plotWidth, plotHeight, yScale) {
  if (!series.points.length) {
    return;
  }

  ctx.save();
  ctx.strokeStyle = series.color;
  ctx.lineWidth = 2.4;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  ctx.beginPath();

  series.points.forEach((point, index) => {
    const x = getXPosition(point.cutLengthMm, plotLeft, plotWidth);
    const y = getYPosition(point.deltaCents, plotTop, plotHeight, yScale);

    if (index === 0) {
      ctx.moveTo(x, y);
      return;
    }

    ctx.lineTo(x, y);
  });

  ctx.stroke();

  series.points.forEach((point) => {
    const x = getXPosition(point.cutLengthMm, plotLeft, plotWidth);
    const y = getYPosition(point.deltaCents, plotTop, plotHeight, yScale);

    ctx.beginPath();
    ctx.fillStyle = COLORS.plotBackground;
    ctx.strokeStyle = series.color;
    ctx.lineWidth = 1.8;
    ctx.arc(x, y, 3.6, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  });

  ctx.restore();
}

function drawLegend(ctx, items, x, y) {
  let cursorX = x;
  const font = "600 11.5px 'Segoe UI'";

  ctx.save();
  ctx.font = font;

  items.forEach((item) => {
    ctx.fillStyle = item.color;
    ctx.fillRect(cursorX, y - 5, 10, 10);
    ctx.strokeStyle = item.color;
    ctx.lineWidth = 1;
    ctx.strokeRect(cursorX, y - 5, 10, 10);

    drawText(ctx, item.label, cursorX + 16, y, {
      color: item.color,
      font,
      align: "left",
      baseline: "middle",
    });

    cursorX += 16 + ctx.measureText(item.label).width + 24;
  });

  ctx.restore();
}

function drawEmptyMessage(ctx, plotLeft, plotTop, plotWidth, plotHeight, message) {
  if (!message) {
    return;
  }

  drawText(ctx, message, plotLeft + plotWidth / 2, plotTop + plotHeight / 2, {
    color: COLORS.hintText,
    font: "600 13px 'Segoe UI'",
    align: "center",
    baseline: "middle",
  });
}

export function renderGraphFrame() {
  const canvas = dom.canvases.graph;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;

  if (!width || !height) {
    return;
  }

  const { message, series } = getGraphState();
  const visibleSeries = Object.values(series).filter(Boolean);
  const yScale = buildYScale(visibleSeries);
  const ctx = resizeCanvasToDisplaySize(canvas);

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = COLORS.canvasBackground;
  ctx.fillRect(0, 0, width, height);

  const margin = {
    top: 42,
    right: 18,
    bottom: 58,
    left: 60,
  };

  const plotLeft = margin.left;
  const plotTop = margin.top;
  const plotRight = width - margin.right;
  const plotBottom = height - margin.bottom;
  const plotWidth = plotRight - plotLeft;
  const plotHeight = plotBottom - plotTop;

  ctx.fillStyle = COLORS.plotBackground;
  ctx.fillRect(plotLeft, plotTop, plotWidth, plotHeight);
  ctx.strokeStyle = COLORS.plotBorder;
  ctx.lineWidth = 1;
  ctx.strokeRect(plotLeft, plotTop, plotWidth, plotHeight);

  yScale.ticks.forEach((tick) => {
    const y = getYPosition(tick, plotTop, plotHeight, yScale);
    const isZero = Math.abs(tick) < Math.max(yScale.step * 0.001, 1e-9);

    ctx.strokeStyle = isZero ? COLORS.zeroGrid : COLORS.grid;
    ctx.lineWidth = isZero ? 1.2 : 1;
    ctx.beginPath();
    ctx.moveTo(plotLeft, y);
    ctx.lineTo(plotRight, y);
    ctx.stroke();

    drawText(ctx, formatTickValue(tick, yScale.step), plotLeft - 12, y, {
      color: COLORS.tickText,
      font: "600 11.5px 'Segoe UI'",
      align: "right",
      baseline: "middle",
    });
  });

  X_AXIS.ticks.forEach((tick) => {
    const x = getXPosition(tick, plotLeft, plotWidth);

    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, plotTop);
    ctx.lineTo(x, plotBottom);
    ctx.stroke();

    ctx.strokeStyle = COLORS.axis;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, plotBottom);
    ctx.lineTo(x, plotBottom + 8);
    ctx.stroke();

    drawText(ctx, String(tick), x, plotBottom + 14, {
      color: COLORS.tickText,
      font: "600 11.5px 'Segoe UI'",
      align: "center",
      baseline: "top",
    });
  });

  visibleSeries.forEach((currentSeries) => {
    drawCurve(ctx, currentSeries, plotLeft, plotTop, plotWidth, plotHeight, yScale);
  });

  ctx.strokeStyle = COLORS.axis;
  ctx.lineWidth = 1.4;
  ctx.beginPath();
  ctx.moveTo(plotLeft, plotTop);
  ctx.lineTo(plotLeft, plotBottom);
  ctx.lineTo(plotRight, plotBottom);
  ctx.stroke();

  drawText(ctx, "Inarmonicidad (cents)", plotLeft - 42, plotTop - 22, {
    color: COLORS.axisText,
    font: "700 12px 'Segoe UI'",
    align: "left",
    baseline: "middle",
  });

  drawText(ctx, "Longitud de corte (mm)", plotLeft + plotWidth / 2, height - 18, {
    color: COLORS.axisText,
    font: "700 12px 'Segoe UI'",
    align: "center",
    baseline: "middle",
  });

  if (visibleSeries.length) {
    drawLegend(ctx, visibleSeries, 16, height - 18);
  } else {
    drawEmptyMessage(ctx, plotLeft, plotTop, plotWidth, plotHeight, message);
  }
}
