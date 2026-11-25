/* European Captives Map v1.2 — static GitHub Pages application; no build step. */
(() => {
  "use strict";

  const COLORS = { origin: "#176f9c", captivity: "#bd5a2b", connection: "#6f558d" };
  const MAX_LISTED_RECORDS = 250;
  const state = {
    data: null,
    map: null,
    layers: {},
    selectedLocation: null,
    lastFocus: null,
  };

  const el = (id) => document.getElementById(id);
  const controls = {
    search: el("record-search"),
    minYear: el("min-year"),
    maxYear: el("max-year"),
    minOutput: el("min-year-output"),
    maxOutput: el("max-year-output"),
    connections: el("show-connections"),
  };

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
    }[char]));
  }

  function compactNumber(value) {
    return new Intl.NumberFormat("en", {
      notation: value >= 1000 ? "compact" : "standard",
      maximumFractionDigits: 1,
    }).format(value);
  }

  function debounce(fn, wait = 120) {
    let timer;
    return (...args) => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => fn(...args), wait);
    };
  }

  function activeMode() {
    return document.querySelector('input[name="map-mode"]:checked')?.value || "both";
  }

  function initMap() {
    state.map = L.map("map", { preferCanvas: true, zoomControl: true, minZoom: 2 }).setView([40.1, -5.5], 4);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(state.map);
    L.control.scale({ imperial: false }).addTo(state.map);
    state.layers.connection = L.layerGroup().addTo(state.map);
    state.layers.marker = L.layerGroup().addTo(state.map);
    state.layers.highlight = L.layerGroup().addTo(state.map);
  }

  function normalizedYearBounds() {
    let min = Number(controls.minYear.value);
    let max = Number(controls.maxYear.value);
    if (min > max) [min, max] = [max, min];
    controls.minOutput.value = String(min);
    controls.maxOutput.value = String(max);
    return { min, max };
  }

  function baseFilteredRecords() {
    const { min, max } = normalizedYearBounds();
    const query = controls.search.value.trim().toLocaleLowerCase();
    const fullRange = min === state.data.metadata.minimum_year && max === state.data.metadata.maximum_year;
    return state.data.records.filter((record) => {
      const yearMatch = record.year === null ? fullRange : (record.year >= min && record.year <= max);
      return yearMatch && (!query || record.search_text.includes(query));
    });
  }

  function panelFilteredRecords(records) {
    if (!state.selectedLocation) return records;
    const key = state.selectedLocation.role === "origin" ? "origin_mapping_id" : "captivity_mapping_id";
    return records.filter((record) => record[key] === state.selectedLocation.mappingId);
  }

  function buildLocationCounts(records) {
    const mode = activeMode();
    const counts = new Map();
    if (mode === "no-location") return counts;
    for (const record of records) {
      if (mode !== "captivity" && record.origin_mapping_id) {
        counts.set(record.origin_mapping_id, (counts.get(record.origin_mapping_id) || 0) + 1);
      }
      if (mode !== "origin" && record.captivity_mapping_id) {
        counts.set(record.captivity_mapping_id, (counts.get(record.captivity_mapping_id) || 0) + 1);
      }
    }
    return counts;
  }

  function buildConnectionCounts(records) {
    const counts = new Map();
    for (const record of records) {
      if (!record.origin_mapping_id || !record.captivity_mapping_id) continue;
      const key = `${record.origin_mapping_id}|${record.captivity_mapping_id}`;
      counts.set(key, (counts.get(key) || 0) + 1);
    }
    return counts;
  }

  function markerRadius(count) {
    return Math.min(25, 5 + Math.sqrt(count) * 1.05);
  }

  function popupForLocation(location, count) {
    const roleLabel = location.role === "origin" ? "Origin" : "Captivity location";
    const certainty = location.certainty === "high" ? "Reviewed" : `${location.certainty} certainty`;
    return `
      <h3>${escapeHtml(location.standardized_name)}</h3>
      <div class="popup-meta"><strong>${roleLabel}</strong> · ${count.toLocaleString()} matching record${count === 1 ? "" : "s"}</div>
      <div class="popup-meta">Source label: ${escapeHtml(location.original_label)} · ${escapeHtml(certainty)}</div>
      ${location.review_note ? `<div class="popup-note">${escapeHtml(location.review_note)}</div>` : ""}`;
  }

  function renderMap(records) {
    state.layers.marker.clearLayers();
    state.layers.connection.clearLayers();
    const locationCounts = buildLocationCounts(records);
    const mode = activeMode();

    if (controls.connections.checked && mode === "both") {
      const connectionCounts = buildConnectionCounts(records);
      for (const [key, count] of connectionCounts) {
        const [originId, captivityId] = key.split("|");
        const origin = state.data.locations[originId];
        const captivity = state.data.locations[captivityId];
        if (!origin || !captivity) continue;
        const line = L.polyline(
          [[origin.latitude, origin.longitude], [captivity.latitude, captivity.longitude]],
          { color: COLORS.connection, weight: Math.min(8, 1.2 + Math.log2(count + 1)), opacity: 0.42 }
        ).addTo(state.layers.connection);
        line.bindTooltip(`${escapeHtml(origin.standardized_name)} → ${escapeHtml(captivity.standardized_name)}: ${count} record${count === 1 ? "" : "s"}<br>Documented association, not a reconstructed route.`);
      }
    }

    for (const [mappingId, count] of locationCounts) {
      const location = state.data.locations[mappingId];
      if (!location) continue;
      const marker = L.circleMarker([location.latitude, location.longitude], {
        radius: markerRadius(count),
        color: "#fffdf8",
        weight: 1.5,
        fillColor: COLORS[location.role],
        fillOpacity: 0.84,
        dashArray: location.certainty === "high" ? null : "3 2",
      }).addTo(state.layers.marker);
      marker.bindPopup(popupForLocation(location, count));
      marker.bindTooltip(`${location.standardized_name}: ${count.toLocaleString()} ${location.role} record${count === 1 ? "" : "s"}`, { sticky: true });
      marker.on("click", () => {
        state.selectedLocation = { mappingId, role: location.role };
        updateSelectionChip(`${location.role === "origin" ? "Origin" : "Captivity"}: ${location.standardized_name}`);
        renderRecordList(panelFilteredRecords(baseFilteredRecords()));
      });
    }
  }

  function modeFilteredRecords(records) {
    if (activeMode() !== "no-location") return records;
    return records.filter((record) => record.place_of_origin === "Not documented" && record.place_of_captivity === "Not documented");
  }

  function geographySummary(record) {
    const origin = record.place_of_origin || "Origin not documented";
    const captivity = record.place_of_captivity || "Captivity location not documented";
    return `${origin} → ${captivity}`;
  }

  function renderRecordList(records) {
    const container = el("record-list");
    container.replaceChildren();
    el("record-count").textContent = `${records.length.toLocaleString()} matching`;
    const limited = records.slice(0, MAX_LISTED_RECORDS);
    el("record-limit-note").textContent = records.length > MAX_LISTED_RECORDS
      ? `Showing the first ${MAX_LISTED_RECORDS.toLocaleString()} records. Refine the search, year range, or map selection to narrow the list.`
      : "Select a record to open its concise historical entry.";

    if (!records.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No records match the current filters.";
      container.append(empty);
      return;
    }

    const fragment = document.createDocumentFragment();
    for (const record of limited) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `record-card ${record.geography_status}`;
      const title = document.createElement("strong");
      title.textContent = record.name;
      const date = document.createElement("span");
      date.textContent = `${record.date || "Date not documented"} · ${record.record_id}`;
      const geo = document.createElement("span");
      geo.textContent = geographySummary(record);
      button.append(title, date, geo);
      button.addEventListener("click", () => openRecord(record, button));
      fragment.append(button);
    }
    container.append(fragment);
  }

  function updateStats(records) {
    const mode = activeMode();
    const locationIds = new Set();
    let connected = 0;
    let unmapped = 0;
    for (const record of records) {
      if (mode !== "captivity" && mode !== "no-location" && record.origin_mapping_id) locationIds.add(record.origin_mapping_id);
      if (mode !== "origin" && mode !== "no-location" && record.captivity_mapping_id) locationIds.add(record.captivity_mapping_id);
      if (record.origin_mapping_id && record.captivity_mapping_id) connected += 1;
      if (!record.origin_mapping_id && !record.captivity_mapping_id) unmapped += 1;
    }
    el("stat-records").textContent = compactNumber(records.length);
    el("stat-locations").textContent = locationIds.size.toLocaleString();
    el("stat-connections").textContent = compactNumber(connected);
    el("stat-unmapped").textContent = compactNumber(unmapped);
  }

  function updateSelectionChip(label) {
    el("selection-chip").hidden = false;
    el("selection-label").textContent = label;
  }

  function clearSelection() {
    state.selectedLocation = null;
    el("selection-chip").hidden = true;
    renderRecordList(baseFilteredRecords());
  }

  function render() {
    const records = modeFilteredRecords(baseFilteredRecords());
    renderMap(records);
    updateStats(records);
    renderRecordList(panelFilteredRecords(records));
  }

  function detailRow(label, value, alwaysShow = false, note = "") {
    if (!alwaysShow && (value === null || value === undefined || value === "" || value === "Not documented")) return null;
    const tr = document.createElement("tr");
    const th = document.createElement("th");
    th.scope = "row";
    th.textContent = label;
    const td = document.createElement("td");
    td.textContent = value || "Not documented";
    if (note) {
      const small = document.createElement("small");
      small.className = "date-method-note";
      small.textContent = note;
      td.append(small);
    }
    tr.append(th, td);
    return tr;
  }

  function openRecord(record, trigger) {
    state.lastFocus = trigger || document.activeElement;
    state.layers.highlight.clearLayers();
    const points = [];
    const origin = state.data.locations[record.origin_mapping_id];
    const captivity = state.data.locations[record.captivity_mapping_id];
    if (origin) {
      points.push([origin.latitude, origin.longitude]);
      L.circleMarker(points.at(-1), { radius: 10, color: "#fff", weight: 3, fillColor: COLORS.origin, fillOpacity: 1 }).addTo(state.layers.highlight);
    }
    if (captivity) {
      points.push([captivity.latitude, captivity.longitude]);
      L.circleMarker(points.at(-1), { radius: 10, color: "#fff", weight: 3, fillColor: COLORS.captivity, fillOpacity: 1 }).addTo(state.layers.highlight);
    }
    if (origin && captivity) {
      L.polyline(points, { color: COLORS.connection, weight: 5, opacity: 0.9, dashArray: "8 6" }).addTo(state.layers.highlight);
    }
    if (points.length === 1) state.map.setView(points[0], Math.max(state.map.getZoom(), 6));
    if (points.length > 1) state.map.fitBounds(points, { padding: [50, 50], maxZoom: 7 });

    el("detail-title").textContent = record.name;
    const content = el("detail-content");
    content.replaceChildren();
    const table = document.createElement("table");
    table.className = "detail-table";
    const fields = [
      ["Place of Origin", record.place_of_origin, true],
      ["Place of Captivity", record.place_of_captivity, true],
      ["Convert", record.convert, true],
      ["Date", record.date, true, "Filtering uses the normalized year. Most January 1 values are treated as year-level entries."],
      ["Ship Name", record.ship_name, true],
      ["Source", record.source, true],
      ["Notes", record.notes, true],
      ["Record ID", record.record_id, true],
    ];
    for (const [label, value, alwaysShow, note] of fields) {
      const row = detailRow(label, value, alwaysShow, note);
      if (row) table.append(row);
    }
    content.append(table);
    const panel = el("detail-panel");
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");
    el("close-detail").focus();
  }

  function closeDetail() {
    const panel = el("detail-panel");
    panel.classList.remove("open");
    panel.setAttribute("aria-hidden", "true");
    state.layers.highlight.clearLayers();
    if (state.lastFocus && typeof state.lastFocus.focus === "function") state.lastFocus.focus();
  }

  function openHelp() {
    const dialog = el("help-dialog");
    if (!dialog.open) dialog.showModal();
  }

  function closeHelp() {
    el("help-dialog").close();
    try { localStorage.setItem("europeanCaptivesGuideSeenV12", "yes"); } catch (_) { /* storage may be blocked */ }
  }

  function bindControls() {
    const rerender = debounce(render, 90);
    controls.search.addEventListener("input", rerender);
    controls.minYear.addEventListener("input", rerender);
    controls.maxYear.addEventListener("input", rerender);
    document.querySelectorAll('input[name="map-mode"]').forEach((input) => input.addEventListener("change", () => {
      clearSelection();
      render();
    }));
    controls.connections.addEventListener("change", render);
    el("clear-selection").addEventListener("click", clearSelection);
    el("reset-filters").addEventListener("click", () => {
      const meta = state.data.metadata;
      controls.search.value = "";
      controls.minYear.value = meta.minimum_year;
      controls.maxYear.value = meta.maximum_year;
      document.querySelector('input[name="map-mode"][value="both"]').checked = true;
      controls.connections.checked = true;
      clearSelection();
      closeDetail();
      state.map.setView([40.1, -5.5], 4);
      render();
    });
    el("close-detail").addEventListener("click", closeDetail);
    el("help-button").addEventListener("click", openHelp);
    el("close-help").addEventListener("click", closeHelp);
    el("finish-help").addEventListener("click", closeHelp);
    el("help-dialog").addEventListener("cancel", (event) => { event.preventDefault(); closeHelp(); });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && el("detail-panel").classList.contains("open")) closeDetail();
    });
  }

  async function init() {
    if (typeof L === "undefined") {
      el("loading").hidden = true;
      const box = el("map-error");
      box.hidden = false;
      box.textContent = "Leaflet could not be loaded. Check the internet connection or content-blocking settings.";
      return;
    }
    initMap();
    try {
      const response = await fetch("data/app-data.json");
      if (!response.ok) throw new Error(`Data request failed (${response.status})`);
      state.data = await response.json();
      const meta = state.data.metadata;
      for (const range of [controls.minYear, controls.maxYear]) {
        range.min = meta.minimum_year;
        range.max = meta.maximum_year;
        range.step = 1;
      }
      controls.minYear.value = meta.minimum_year;
      controls.maxYear.value = meta.maximum_year;
      bindControls();
      render();
      el("loading").hidden = true;
      try {
        if (!localStorage.getItem("europeanCaptivesGuideSeenV12")) window.setTimeout(openHelp, 400);
      } catch (_) { /* storage may be blocked */ }
    } catch (error) {
      el("loading").hidden = true;
      const box = el("map-error");
      box.hidden = false;
      box.textContent = "The map data could not be loaded. On GitHub Pages, confirm that the data folder was uploaded beside index.html. " + error.message;
      console.error(error);
    }
  }

  init();
})();
