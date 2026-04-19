import { dom } from "../shared/dom.js";
import {
  FLUTE_KINDS,
  PROJECT_CONSTANTS,
  getDiameterAt,
} from "../domain/index.js";

const { L_TOTAL, DIAMETER_INTERNAL } = PROJECT_CONSTANTS;

function computeCanvasView(canvas) {
  const width = canvas.width;
  const height = canvas.height;
  const paddingX = 18;
  const paddingY = 12;
  const availableWidth = width - paddingX * 2;
  const availableHeight = height - paddingY * 2;
  const scaleX = availableWidth / L_TOTAL;
  const scaleY = availableHeight / (DIAMETER_INTERNAL * 2);
  const scale = Math.min(scaleX, scaleY);

  return {
    scale,
    x0: (width - scale * L_TOTAL) / 2,
    midY: height / 2,
  };
}

function getThemeColors(canvas) {
  if (canvas.id.includes("inverse")) {
    return {
      line: "#45d7ff",
      mouthGuide: "#d8e6ffcc",
      breakGuide: "#ffe066cc",
      accentFill: "rgba(69, 215, 255, 0.28)",
      accentStroke: "#8ae8ff",
    };
  }

  return {
    line: "#ff9f5a",
    mouthGuide: "#d8e6ffcc",
    breakGuide: "#ffe066cc",
    accentFill: "rgba(255, 159, 90, 0.28)",
    accentStroke: "#ffc08f",
  };
}

function getFluteConfig(canvas, geometries) {
  if (canvas.id.includes("inverse")) {
    return {
      kind: FLUTE_KINDS.INVERSE,
      flute: geometries.inverse,
    };
  }

  return {
    kind: FLUTE_KINDS.BASE,
    flute: geometries.base,
  };
}

function drawTubeSketch(canvas, geometries) {
  const ctx = canvas.getContext("2d");

  if (!ctx) {
    return;
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const { scale, x0, midY } = computeCanvasView(canvas);
  const mmToX = (mm) => x0 + mm * scale;
  const diameterToOffset = (diameter) => (diameter / 2) * scale;
  const theme = getThemeColors(canvas);
  const lineColor = theme.line;
  const mouthGuideColor = theme.mouthGuide;
  const breakGuideColor = theme.breakGuide;
  const accentFill = theme.accentFill;
  const accentStroke = theme.accentStroke;
  const { kind, flute } = getFluteConfig(canvas, geometries);
  const mouthX = flute.x;
  const splitX = flute.a;

  ctx.setLineDash([4, 6]);
  ctx.lineWidth = 1;

  const mouthGuideX = mmToX(mouthX);
  ctx.strokeStyle = mouthGuideColor;
  ctx.beginPath();
  ctx.moveTo(mouthGuideX, midY - diameterToOffset(DIAMETER_INTERNAL) - 10);
  ctx.lineTo(mouthGuideX, midY + diameterToOffset(DIAMETER_INTERNAL) + 10);
  ctx.stroke();

  const breakGuideX = mmToX(splitX);
  ctx.strokeStyle = breakGuideColor;
  ctx.beginPath();
  ctx.moveTo(breakGuideX, midY - diameterToOffset(DIAMETER_INTERNAL) - 10);
  ctx.lineTo(breakGuideX, midY + diameterToOffset(DIAMETER_INTERNAL) + 10);
  ctx.stroke();

  ctx.setLineDash([]);
  ctx.strokeStyle = lineColor;
  ctx.lineWidth = 2;

  ctx.beginPath();
  for (let mm = 0; mm <= L_TOTAL; mm += 2) {
    const x = mmToX(mm);
    const y = midY - diameterToOffset(getDiameterAt(kind, flute, mm));

    if (mm === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.stroke();

  ctx.beginPath();
  for (let mm = 0; mm <= L_TOTAL; mm += 2) {
    const x = mmToX(mm);
    const y = midY + diameterToOffset(getDiameterAt(kind, flute, mm));

    if (mm === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(mmToX(0), midY - diameterToOffset(getDiameterAt(kind, flute, 0)));
  ctx.lineTo(mmToX(0), midY + diameterToOffset(getDiameterAt(kind, flute, 0)));
  ctx.stroke();

  const chimneyHeight = flute.y * scale * 0.35;
  const chimneyWidth = 18;
  const chimneyX = mmToX(mouthX) - chimneyWidth / 2;
  const chimneyTop =
    midY - diameterToOffset(getDiameterAt(kind, flute, mouthX)) - chimneyHeight;

  ctx.fillStyle = accentFill;
  ctx.strokeStyle = accentStroke;
  ctx.fillRect(chimneyX, chimneyTop, chimneyWidth, chimneyHeight);
  ctx.strokeRect(chimneyX, chimneyTop, chimneyWidth, chimneyHeight);

  const embouchureRadius = scale * (flute.d / 2);

  ctx.beginPath();
  ctx.lineWidth = 2;
  ctx.strokeStyle = "#ffffff";
  ctx.fillStyle = "rgba(255,255,255,0.08)";
  ctx.arc(mmToX(mouthX), midY, embouchureRadius, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
}

export function renderAllFluteSketches(geometries) {
  drawTubeSketch(dom.canvases.fluteBase, geometries);
  drawTubeSketch(dom.canvases.fluteInverse, geometries);
}
