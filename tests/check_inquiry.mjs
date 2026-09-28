import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const source = await readFile(new URL("../templates/assets/js/inquiry.js", import.meta.url));
const { buildPayload, buildMailto, submissionURL, acceptedReference, bindInquiryForm } =
  await import(`data:text/javascript;base64,${source.toString("base64")}`);
const values = { name: " Alex ", email: "alex@example.com", requirements: "100 units\nPlease send specifications.",
  company: "Buyer Ltd", quantity: "100 cartons", country: "UK", website: "" };
const payload = buildPayload(values);
assert.equal(payload.name, "Alex");
assert.equal(payload.quantity, "100 cartons");
assert.equal(Object.hasOwn(payload, "website"), false);
assert.equal(values.name, " Alex ");
for (const name of ["name", "email", "requirements"]) {
  assert.throws(() => buildPayload({ ...values, [name]: "  " }), RangeError);
}
for (const bad of [{ email: "invalid" }, { website: "bot" }, { name: "A\r\nB" }, { requirements: "x".repeat(5001) }, { company: 1 }]) {
  assert.throws(() => buildPayload({ ...values, ...bad }), RangeError);
}
const mailto = new URL(buildMailto("sales@example.com", values));
assert.equal(mailto.protocol, "mailto:");
assert.equal(decodeURIComponent(mailto.pathname), "sales@example.com");
assert.equal(mailto.searchParams.get("subject"), "B2B inquiry from Alex");
assert.match(mailto.searchParams.get("body"), /100 cartons/);
assert.throws(() => buildMailto("sales@example.com\nBcc:other@example.com", values), RangeError);
assert.throws(() => buildMailto("first,second@example.com", values), RangeError);
assert.equal(submissionURL("/api/inquiry", "http://localhost:8000/contact/"), "http://localhost:8000/api/inquiry");
assert.equal(submissionURL("https://forms.example.com/inquiry", "https://example.com/"), "https://forms.example.com/inquiry");
for (const action of ["", "javascript:alert(1)", "http://other.example.com/", "https://u:p@example.com/", "https://example.com/#x"]) {
  assert.throws(() => submissionURL(action, "https://example.com/"), RangeError);
}
assert.equal(acceptedReference({ accepted: true, reference: " REF-1 " }), "REF-1");
for (const body of [null, {}, { accepted: "true", reference: "x" }, { accepted: true }, { accepted: true, reference: " " }, { accepted: true, reference: 1 }]) {
  assert.throws(() => acceptedReference(body), RangeError);
}

// Minimal DOM doubles exercise submit transitions without making any network call.
function mockForm(mode, { requirements = values.requirements, pageURL = "http://localhost:8000/contact/" } = {}) {
  const fields = Object.fromEntries(Object.entries({ ...values, requirements }).map(([name, value]) => [name, {
    name, value, validity: { valid: true }, setCustomValidity() {}, setAttribute() {}, removeAttribute() {},
  }]));
  const status = { dataset: {}, textContent: "", setAttribute() {} };
  const button = { disabled: true, dataset: { requiresJs: "" }, textContent: "Send inquiry" };
  const events = {};
  const form = {
    dataset: { mode, recipient: "sales@example.com" },
    ownerDocument: { baseURI: pageURL, defaultView: { location: { href: pageURL, assign(url) { form.navigation = url; } } } },
    elements: { namedItem(name) { return fields[name]; } },
    querySelector(selector) { return selector === "[data-form-status]" ? status : null; },
    querySelectorAll() { return [button]; },
    getAttribute() { return "/api/inquiry"; }, setAttribute() {},
    addEventListener(name, callback) { events[name] = callback; },
    checkValidity() { return true; }, reportValidity() {},
  };
  bindInquiryForm(form);
  return { form, fields, status, button, submit: () => events.submit({ preventDefault() {} }) };
}
const originalFetch = globalThis.fetch;
try {
  let requests = 0;
  globalThis.fetch = async () => { requests++; throw new Error("Unexpected request"); };
  const productURL = "http://localhost:8000/contact/?product=" + encodeURIComponent("Pump\nSeries \u0000A" + "X".repeat(200)) + "#inquiry";
  const blank = mockForm("http", { requirements: "  ", pageURL: productURL });
  assert.match(blank.fields.requirements.value, /^I am interested in Pump Series A/);
  assert.equal(blank.fields.requirements.value.length, "I am interested in ".length + 180 + ". Please share product specifications and sourcing details.".length);
  assert.equal(/[\x00-\x1f\x7f]/.test(blank.fields.requirements.value), false);
  assert.equal(blank.form.navigation, undefined);
  assert.equal(requests, 0);
  const existing = mockForm("http", { requirements: "My own requirements", pageURL: productURL });
  assert.equal(existing.fields.requirements.value, "My own requirements");
  assert.equal(requests, 0);
  const draft = mockForm("email_draft");
  assert.equal(draft.button.disabled, false);
  await draft.submit();
  assert.equal(requests, 0);
  assert.equal(draft.button.textContent, "Open email draft");
  assert.match(draft.form.navigation, /^mailto:/);
  assert.equal(draft.status.dataset.state, "draft");
  const honeypot = mockForm("http");
  honeypot.fields.website.value = "bot";
  await honeypot.submit();
  assert.equal(requests, 0);
  assert.equal(honeypot.status.dataset.state, "invalid");
  const request = mockForm("http");
  let finish;
  globalThis.fetch = (url, options) => {
    requests++;
    assert.equal(url, "http://localhost:8000/api/inquiry");
    assert.equal(options.method, "POST");
    assert.equal(options.redirect, "error");
    assert.equal(JSON.parse(options.body).requirements, values.requirements);
    assert.ok(options.signal instanceof AbortSignal);
    return new Promise((resolve) => { finish = resolve; });
  };
  const pending = request.submit();
  assert.equal(request.button.disabled, true);
  await request.submit();
  assert.equal(requests, 1);
  finish({ ok: true, json: async () => ({ accepted: true, reference: "REF-2" }) });
  await pending;
  assert.equal(request.status.dataset.state, "accepted");
  assert.equal(request.status.textContent, "Inquiry submitted. Reference: REF-2. Keep this reference if you follow up.");
  assert.equal(request.button.disabled, false);
  assert.equal(request.button.textContent, "Send inquiry");
  await request.submit();
  assert.equal(requests, 1); // A confirmed identical inquiry is not submitted twice.
  request.fields.requirements.value = "A changed inquiry";
  globalThis.fetch = async () => { requests++; return { ok: true, json: async () => ({ accepted: false }) }; };
  await request.submit();
  assert.equal(request.status.dataset.state, "error");
  assert.equal(request.fields.requirements.value, "A changed inquiry");
  assert.equal(request.button.disabled, false);
  globalThis.fetch = async () => { requests++; const error = new Error("timeout"); error.name = "AbortError"; throw error; };
  await request.submit();
  assert.equal(request.status.textContent, "Submission could not be confirmed. Your details are kept; try again or use the email link.");
  assert.equal(request.button.disabled, false);
  globalThis.fetch = async () => { requests++; return { ok: true, json: async () => ({ accepted: true, reference: "REF-3" }) }; };
  await request.submit();
  assert.equal(request.status.dataset.state, "accepted");
  assert.equal(request.fields.requirements.value, "A changed inquiry");
} finally {
  globalThis.fetch = originalFetch;
}
console.log("Inquiry assertions passed; all HTTP responses were mocked.");
