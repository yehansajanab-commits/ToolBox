const apiBase = window.API_BASE || "http://localhost:5000";

function $(selector) {
  return document.querySelector(selector);
}

function createElement(tag, attrs = {}, text = "") {
  const el = document.createElement(tag);
  Object.entries(attrs).forEach(([key, value]) => {
    if (key === "class") {
      el.className = value;
    } else if (key.startsWith("data-")) {
      el.setAttribute(key, value);
    } else {
      el[key] = value;
    }
  });
  if (text) el.textContent = text;
  return el;
}

function showSection(id) {
  document.querySelectorAll(".panel").forEach((section) => {
    section.classList.toggle("active", section.id === id);
  });
  document.querySelectorAll("nav button").forEach((button) => {
    button.classList.toggle("active", button.dataset.section === id);
  });
}

async function fetchJson(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || response.statusText || "Request failed");
  }
  return response.json();
}

function renderResult(container, data) {
  container.innerHTML = "";

  if (data.error) {
    container.appendChild(createElement("p", {}, `Error: ${data.error}`));
    return;
  }

  const details = createElement("div");
  if (data.box_no) {
    details.appendChild(createElement("p", {}, `Box: ${data.box_no}`));
  }
  if (data.items) {
    details.appendChild(createElement("p", {}, `Items: ${data.items.join(", ")}`));
  }
  if (data.missing) {
    details.appendChild(createElement("p", {}, `Missing: ${data.missing.length ? data.missing.join(", ") : "None"}`));
  }
  if (data.cleared !== undefined) {
    details.appendChild(createElement("p", {}, `Cleared: ${data.cleared ? "Yes" : "No"}`));
  }
  container.appendChild(details);

  if (data.segmented_url) {
    const image = createElement("img", { src: data.segmented_url, alt: "Segmented result" });
    container.appendChild(image);
  }
}

async function submitImage(formEl, endpoint, resultEl) {
  const submitButton = formEl.querySelector("button[type='submit']");
  const formData = new FormData(formEl);

  submitButton.disabled = true;
  resultEl.innerHTML = "<p>Processing image…</p>";

  try {
    const result = await fetchJson(endpoint, { method: "POST", body: formData });
    renderResult(resultEl, result);
    await loadStats();
    if (document.querySelector("#inventory")) {
      await loadInventory();
    }
  } catch (error) {
    resultEl.innerHTML = `<p class="error">${error.message}</p>`;
  } finally {
    submitButton.disabled = false;
  }
}

async function loadStats() {
  try {
    const data = await fetchJson("/api/boxes");
    $("#boxCount").textContent = data.box_count;
    $("#itemCount").textContent = data.item_count;
  } catch (error) {
    $("#boxCount").textContent = "—";
    $("#itemCount").textContent = "—";
  }
}

async function loadInventory() {
  const list = $("#inventoryList");
  list.innerHTML = "<p>Loading inventory…</p>";

  try {
    const data = await fetchJson("/api/inventory");
    list.innerHTML = "";

    if (!Object.keys(data).length) {
      list.appendChild(createElement("p", {}, "No boxes available yet."));
      return;
    }

    Object.entries(data).forEach(([boxNo, items]) => {
      const card = createElement("div", { class: "inventory-card" });
      card.appendChild(createElement("h3", {}, `Box ${boxNo}`));
      card.appendChild(createElement("p", {}, `Items (${items.length}):`));
      const itemList = createElement("ul");

      items.forEach((item) => {
        itemList.appendChild(createElement("li", {}, item));
      });

      card.appendChild(itemList);
      const clearButton = createElement("button", { class: "clear-button" }, "Clear box");
      clearButton.addEventListener("click", () => clearBox(boxNo));
      card.appendChild(clearButton);
      list.appendChild(card);
    });
  } catch (error) {
    list.innerHTML = `<p class="error">${error.message}</p>`;
  }
}

async function clearBox(boxNo) {
  if (!confirm(`Clear inventory for box ${boxNo}?`)) {
    return;
  }

  try {
    await fetchJson("/api/clear_box", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ box_no: boxNo }),
    });
    await loadStats();
    await loadInventory();
  } catch (error) {
    alert(`Unable to clear box: ${error.message}`);
  }
}

function setupNavigation() {
  document.querySelectorAll("nav button").forEach((button) => {
    button.addEventListener("click", () => {
      showSection(button.dataset.section);
    });
  });
}

function setupForms() {
  const handoverForm = $("#handoverForm");
  const receiveForm = $("#receiveForm");
  const handoverResult = $("#handoverResult");
  const receiveResult = $("#receiveResult");

  handoverForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submitImage(handoverForm, "/api/handover", handoverResult);
  });

  receiveForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submitImage(receiveForm, "/api/receive", receiveResult);
  });
}

window.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupForms();
  loadStats();
  loadInventory();
});
