/**
 * Interactive Sourcing & Container Freight Estimator
 * Zero-dependency real-time CBM, Gross Weight & Container Fill Rate calculation.
 */
document.addEventListener("DOMContentLoaded", () => {
  const quantityInput = document.getElementById("orderQty");
  const containerSelect = document.getElementById("containerType");
  const skuSelect = document.getElementById("targetSku");

  if (!quantityInput || !containerSelect) return;

  function recalculate() {
    const qty = parseInt(quantityInput.value, 10) || 1000;
    const container = containerSelect.value; // '20GP' or '40HQ'
    
    // Read dynamic dataset attributes from sku option or fallback defaults
    const activeOption = skuSelect ? skuSelect.options[skuSelect.selectedIndex] : null;
    const unitCbm = activeOption && activeOption.dataset.cbm ? parseFloat(activeOption.dataset.cbm) : 0.015;
    const unitWeightKg = activeOption && activeOption.dataset.weight ? parseFloat(activeOption.dataset.weight) : 1.2;

    const totalCbm = (qty * unitCbm).toFixed(2);
    const totalWeightKg = (qty * unitWeightKg).toFixed(1);
    const totalWeightLbs = (totalWeightKg * 2.20462).toFixed(1);

    const containerCbmCapacity = container === "20GP" ? 28.0 : 68.0;
    const maxWeightCapacityKg = container === "20GP" ? 18000 : 26000;

    const fillRateVol = Math.min(100, Math.round((totalCbm / containerCbmCapacity) * 100));
    const fillRateWeight = Math.min(100, Math.round((totalWeightKg / maxWeightCapacityKg) * 100));
    const maxFillRate = Math.max(fillRateVol, fillRateWeight);

    const estContainers = (totalCbm / containerCbmCapacity).toFixed(1);

    // Update DOM fields
    const resCbm = document.getElementById("resCbm");
    const resWeight = document.getElementById("resWeight");
    const resFill = document.getElementById("resFill");
    const resContainers = document.getElementById("resContainers");

    if (resCbm) resCbm.textContent = `${totalCbm} m³ (${(totalCbm * 35.3147).toFixed(1)} cu ft)`;
    if (resWeight) resWeight.textContent = `${totalWeightKg} kg (${totalWeightLbs} lbs)`;
    if (resFill) resFill.textContent = `${maxFillRate}% Capacity`;
    if (resContainers) resContainers.textContent = `${estContainers} × ${container}`;
  }

  quantityInput.addEventListener("input", recalculate);
  containerSelect.addEventListener("change", recalculate);
  if (skuSelect) skuSelect.addEventListener("change", recalculate);

  recalculate();
});
