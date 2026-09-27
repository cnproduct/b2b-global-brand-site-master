import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import { readFile } from "node:fs/promises";

// Pass the installed module path as argv[2], or run against the adjacent file.
const moduleURL = process.argv[2]
  ? pathToFileURL(process.argv[2])
  : new URL("../templates/assets/js/sourcing_estimator.js", import.meta.url);
// The browser consumes this .js as an ES module; retain that mode on Node 18 too.
const { estimateLoad } = await import(`data:text/javascript;base64,${(await readFile(moduleURL)).toString("base64")}`);
const inputs = { quantity: 10, unitVolumeM3: 2, unitWeightKg: 100, usableVolumeM3: 50, payloadKg: 400 };

assert.deepEqual(estimateLoad({ ...inputs, quantity: 0 }), {
  totalVolumeM3: 0, totalWeightKg: 0, volumeFillPercent: 0, weightFillPercent: 0, containers: 0,
});
assert.deepEqual(estimateLoad(inputs), {
  totalVolumeM3: 20, totalWeightKg: 1000, volumeFillPercent: 40, weightFillPercent: 250, containers: 3,
});
assert.equal(estimateLoad({ ...inputs, unitVolumeM3: 20 }).containers, 4);
assert.equal(estimateLoad({ ...inputs, unitVolumeM3: 20 }).volumeFillPercent, 400);
for (const value of [-1, undefined, Infinity, NaN, 1.5, Number.MAX_SAFE_INTEGER + 1, "10", null]) {
  assert.throws(() => estimateLoad({ ...inputs, quantity: value }), RangeError);
}
for (const name of ["unitVolumeM3", "unitWeightKg", "usableVolumeM3", "payloadKg"]) {
  for (const value of [-1, 0, undefined, Infinity, NaN, "1", null]) {
    assert.throws(() => estimateLoad({ ...inputs, [name]: value }), RangeError);
  }
}
assert.throws(() => estimateLoad({ ...inputs, unitVolumeM3: Number.MAX_VALUE }), RangeError);
assert.throws(() => estimateLoad({ ...inputs, usableVolumeM3: Number.MIN_VALUE }), RangeError);
assert.throws(() => estimateLoad({ ...inputs, unitVolumeM3: Number.MIN_VALUE, usableVolumeM3: Number.MAX_VALUE }), RangeError);
console.log("Estimator assertions passed.");
