/** Optional inquiry enhancement. Load with type="module"; importing never sends a request. */
const limits = { name: 120, email: 254, requirements: 5000, company: 160, quantity: 80, country: 120 };
const emailPattern = /^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}$/;

export function buildPayload(values = {}) {
  const payload = {};
  const errors = {};
  for (const [name, limit] of Object.entries(limits)) {
    const value = values[name] ?? "";
    payload[name] = typeof value === "string" ? value.trim() : "";
    if (typeof value !== "string" || payload[name].length > limit) {
      errors[name] = `Enter ${name} as text with no more than ${limit} characters.`;
    } else if (/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/.test(value)
        || (name !== "requirements" && /[\r\n\t]/.test(value))) {
      errors[name] = `Remove unsupported control characters from ${name}.`;
    }
  }
  for (const name of ["name", "email", "requirements"]) {
    if (!payload[name]) errors[name] = `Enter your ${name}.`;
  }
  if (payload.email && !emailPattern.test(payload.email)) errors.email = "Enter a valid email address.";
  if (values.website !== undefined && values.website !== "") errors.website = "Unable to process this inquiry.";
  if (Object.keys(errors).length) {
    const error = new RangeError("Review the highlighted fields.");
    error.fields = errors;
    throw error;
  }
  return payload;
}

export function buildMailto(recipient, values) {
  if (typeof recipient !== "string" || recipient.length > 254 || !emailPattern.test(recipient)
      || /[\r\n\x00-\x1f\x7f]/.test(recipient)) {
    throw new RangeError("A valid single recipient email address is required.");
  }
  const payload = buildPayload(values);
  const subject = `B2B inquiry from ${payload.name}`;
  const body = [`Name: ${payload.name}`, `Email: ${payload.email}`, `Company: ${payload.company}`,
    `Country: ${payload.country}`, `Quantity: ${payload.quantity}`, "", "Requirements:", payload.requirements].join("\r\n");
  return `mailto:${encodeURIComponent(recipient)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

export function submissionURL(action, baseURL) {
  if (typeof action !== "string" || !action.trim()) throw new RangeError("No submission endpoint is configured.");
  const base = new URL(baseURL);
  const target = new URL(action, base);
  if (target.username || target.password || target.hash
      || (target.protocol !== "https:" && !(target.protocol === "http:" && target.origin === base.origin))) {
    throw new RangeError("The configured endpoint must use HTTPS or the page's HTTP origin.");
  }
  return target.href;
}

export function acceptedReference(body) {
  if (!body || body.accepted !== true || typeof body.reference !== "string" || !body.reference.trim()) {
    throw new RangeError("The server did not confirm acceptance with a reference.");
  }
  return body.reference.trim();
}

export function bindInquiryForm(form) {
  const requirements = form.elements.namedItem("requirements");
  const product = new URL(form.ownerDocument.defaultView.location.href || form.ownerDocument.baseURI).searchParams.get("product") || "";
  const productName = [...product.replace(/[\x00-\x1f\x7f]/g, " ").replace(/\s+/g, " ").trim()].slice(0, 180).join("");
  if (requirements && !requirements.value.trim() && productName) {
    requirements.value = `I am interested in ${productName}. Please share product specifications and sourcing details.`;
  }
  const status = form.querySelector("[data-form-status]")
    || form.appendChild(form.ownerDocument.createElement("p"));
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  status.setAttribute("aria-atomic", "true");
  const buttons = [...form.querySelectorAll('button[type="submit"]')];
  buttons.forEach((button) => { if (button.dataset.requiresJs !== undefined) button.disabled = false; });
  const mode = form.dataset.mode;
  if (mode === "email_draft") buttons.forEach((button) => { button.textContent = "Open email draft"; });
  const labels = buttons.map((button) => button.textContent);
  let pending = false;
  let lastAccepted = null;
  form.noValidate = true; // Keep native validity checks while providing persistent inline errors.

  const show = (state, message) => {
    status.dataset.state = state;
    status.textContent = message;
  };
  const fieldError = (name, message) => {
    const field = form.elements.namedItem(name);
    const output = form.querySelector(`[data-error-for="${name}"]`);
    if (output) output.textContent = message;
    if (field) {
      field.setCustomValidity(message);
      if (message) field.setAttribute("aria-invalid", "true");
      else field.removeAttribute("aria-invalid");
    }
  };
  form.addEventListener("input", (event) => {
    if (Object.hasOwn(limits, event.target.name)) fieldError(event.target.name, "");
    if (!pending) show("idle", "");
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (pending) return;
    const values = {};
    for (const name of [...Object.keys(limits), "website"]) {
      values[name] = form.elements.namedItem(name)?.value ?? "";
      if (name !== "website") fieldError(name, "");
    }
    let payload;
    try {
      payload = buildPayload(values);
    } catch (error) {
      if (error.fields?.website) {
        show("invalid", "Unable to process this inquiry. Review your entries and try again.");
        return;
      }
      for (const [name, message] of Object.entries(error.fields || {})) fieldError(name, message);
      show("invalid", "Review the highlighted fields. Your entries have been kept.");
      form.reportValidity();
      return;
    }
    if (!form.checkValidity()) {
      for (const name of Object.keys(limits)) {
        const field = form.elements.namedItem(name);
        if (field && !field.validity.valid) fieldError(name, field.validationMessage);
      }
      show("invalid", "Review the highlighted fields. Your entries have been kept.");
      form.reportValidity();
      return;
    }
    if (mode === "email_draft") {
      try {
        const mailto = buildMailto(form.dataset.recipient, payload);
        show("draft", "Email draft requested. Review it in your email app and send it yourself. This page has not sent your inquiry.");
        form.ownerDocument.defaultView.location.assign(mailto);
      } catch {
        show("error", "The email draft could not be opened. Your entries are kept; use the contact email on this page.");
      }
      return;
    }
    if (mode !== "http") {
      show("error", "Please use the email link to send your inquiry. Your details are kept.");
      return;
    }
    let endpoint;
    try {
      endpoint = submissionURL(form.getAttribute("action"), form.ownerDocument.baseURI);
    } catch {
      show("error", "Submission could not be confirmed. Your details are kept; try again or use the email link.");
      return;
    }
    const signature = JSON.stringify(payload);
    if (lastAccepted?.signature === signature) {
      show("accepted", `This inquiry has already been submitted. Reference: ${lastAccepted.reference}. Keep this reference if you follow up.`);
      return;
    }
    pending = true;
    form.setAttribute("aria-busy", "true");
    const disabled = buttons.map((button) => button.disabled);
    buttons.forEach((button) => { button.disabled = true; button.textContent = "Submitting…"; });
    show("pending", "Submitting your inquiry…");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(endpoint, {
        method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: signature, credentials: "same-origin", redirect: "error", signal: controller.signal,
      });
      if (!response.ok) throw new Error("Unconfirmed response");
      const reference = acceptedReference(await response.json());
      lastAccepted = { signature, reference };
      show("accepted", `Inquiry submitted. Reference: ${reference}. Keep this reference if you follow up.`);
    } catch {
      show("error", "Submission could not be confirmed. Your details are kept; try again or use the email link.");
    } finally {
      clearTimeout(timeout);
      pending = false;
      form.setAttribute("aria-busy", "false");
      buttons.forEach((button, index) => { button.disabled = disabled[index]; button.textContent = labels[index]; });
    }
  });
}

if (typeof document !== "undefined") {
  const bind = () => document.querySelectorAll("form[data-inquiry-form]").forEach(bindInquiryForm);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind, { once: true });
  else bind();
}
