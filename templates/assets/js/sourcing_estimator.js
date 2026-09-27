/**
 * Optional capacity estimator. Supply verified packed-unit volume/weight and
 * usable container volume/payload in consistent units; no assumed defaults.
 * Load in the browser with <script type="module">.
 */
export function estimateLoad({ quantity, unitVolumeM3, unitWeightKg, usableVolumeM3, payloadKg }) {
  if (!Number.isSafeInteger(quantity) || quantity < 0) {
    throw new RangeError("quantity must be a non-negative safe integer.");
  }
  for (const [name, value] of Object.entries({ unitVolumeM3, unitWeightKg, usableVolumeM3, payloadKg })) {
    if (!Number.isFinite(value) || value <= 0) {
      throw new RangeError(`${name} must be a finite positive number.`);
    }
  }
  const totalVolumeM3 = quantity * unitVolumeM3;
  const totalWeightKg = quantity * unitWeightKg;
  const volumeRatio = totalVolumeM3 / usableVolumeM3;
  const weightRatio = totalWeightKg / payloadKg;
  const volumeFillPercent = volumeRatio * 100;
  const weightFillPercent = weightRatio * 100;
  const containers = Math.ceil(Math.max(volumeRatio, weightRatio));
  if (![totalVolumeM3, totalWeightKg, volumeFillPercent, weightFillPercent].every(Number.isFinite)
      || (quantity > 0 && (volumeRatio === 0 || weightRatio === 0))
      || !Number.isSafeInteger(containers)) {
    throw new RangeError("Calculation exceeds the supported numeric range.");
  }
  // ponytail: aggregate capacity lower bound; use a stowage planner for geometry and load distribution.
  return { totalVolumeM3, totalWeightKg, volumeFillPercent, weightFillPercent, containers };
}

const limitation = "Capacity lower bound only; not a 3D packing plan, load-distribution assessment, or freight quote.";

function bindEstimators() {
  document.querySelectorAll("form[data-load-estimator]").forEach((form) => {
    const output = form.querySelector("output") || form.appendChild(document.createElement("output"));
    output.setAttribute("aria-live", "polite");
    output.setAttribute("aria-atomic", "true");
    const recalculate = () => {
      try {
        const inputs = {};
        for (const name of ["quantity", "unitVolumeM3", "unitWeightKg", "usableVolumeM3", "payloadKg"]) {
          const value = form.elements.namedItem(name)?.value?.trim();
          if (!value) throw new RangeError(`Enter ${name}; no assumed value is used.`);
          inputs[name] = Number(value);
        }
        const result = estimateLoad(inputs);
        output.textContent = `Volume: ${result.totalVolumeM3} m³. Weight: ${result.totalWeightKg} kg. `
          + `Single-container volume utilization: ${result.volumeFillPercent}%. `
          + `Single-container payload utilization: ${result.weightFillPercent}%. `
          + `Minimum containers by aggregate capacity: ${result.containers}. ${limitation}`;
      } catch (error) {
        output.textContent = `${error.message} ${limitation}`;
      }
    };
    form.addEventListener("input", recalculate);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      recalculate();
    });
    recalculate();
  });
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindEstimators, { once: true });
  } else {
    bindEstimators();
  }
}
