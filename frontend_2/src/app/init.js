import { dom } from "../shared/dom.js";
import { bindFluteEvents } from "../flutes/events.js";
import { renderAllFluteSketches } from "../flutes/render.js";
import { bindGraphEvents } from "../graph/events.js";
import { renderGraphFrame } from "../graph/render.js";
import { getFluteGeometry, hydrateAllFluteControls } from "../flutes/state.js";
import { bindRmseEvents } from "../graph/rmse-events.js";

function init() {
  dom.shell.dataset.ready = "true";
  hydrateAllFluteControls(dom.panels);
  bindFluteEvents();
  bindGraphEvents();
  bindRmseEvents();
  renderAllFluteSketches({
    base: getFluteGeometry("base"),
    inverse: getFluteGeometry("inverse"),
  });
  renderGraphFrame();
  window.addEventListener("resize", () => {
    renderAllFluteSketches({
      base: getFluteGeometry("base"),
      inverse: getFluteGeometry("inverse"),
    });
    renderGraphFrame();
  });
  console.info("frontend_2 listo: estructura base creada.");
}

init();
