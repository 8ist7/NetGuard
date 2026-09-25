const $ = (id) => document.getElementById(id);

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function setStatus(id, ok, good = "OK", bad = "FAILED") {
  const el = $(id);
  el.textContent = ok ? good : bad;
  el.className = ok ? "oktext" : "badtext";
}

function renderServices(items) {
  $("services").innerHTML = items.map((x) => `
    <div class="service">
      <span><b>${esc(x.service)}</b> : ${x.port}<small>${esc(x.result)}</small></span>
      <b class="${x.status === "OPEN" ? "open" : "closed"}">${x.status}</b>
    </div>`).join("");
}

function renderDevices(items) {
  $("deviceCount").textContent = items.length;
  $("devices").innerHTML = items.length ? items.map((x) => `
    <tr>
      <td>${esc(x.ip)}</td>
      <td>${esc(x.mac)}</td>
      <td>${esc(x.state)}${x.interface ? ` / ${esc(x.interface)}` : ""}</td>
      <td>${esc(x.vendor || "Unknown")}</td>
    </tr>`).join("") : `<tr><td colspan="4">No active local devices are currently visible.</td></tr>`;
}

function renderEvents(items) {
  $("events").innerHTML = items.length ? items.map((x) => `
    <div class="event">
      <strong class="${String(x.severity).toLowerCase()}">${esc(x.severity)}</strong>
      <b>${esc(x.event_type)}</b>
      <span>${esc(x.message)}</span>
      <time>${esc(x.created_at)}</time>
    </div>`).join("") : `<div class="event"><span>No events recorded yet.</span></div>`;
}

function renderScan(results) {
  $("scanTable").innerHTML = results.length ? results.map((x) => `
    <tr>
      <td>${x.port}</td>
      <td><b class="${x.status === "OPEN" ? "open" : "closed"}">${x.status}</b></td>
      <td>${esc(x.service || "Unknown")}</td>
      <td>${x.latency_ms} ms</td>
    </tr>`).join("") : "";
}

async function getJson(url, options = {}) {
  const response = await fetch(url, options);
  let data;
  try { data = await response.json(); } catch { data = {}; }
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

async function loadDashboard() {
  try {
    const d = await getJson("/api/dashboard");
    $("localIp").textContent = d.network.local_ip || "Unavailable";
    $("gateway").textContent = d.network.gateway || "Unavailable";
    $("dnsServer").textContent = d.network.dns_server || "Unavailable";
    $("interface").textContent = `Interface: ${d.network.interface || "Unavailable"}`;
    $("interface2").textContent = d.network.interface || "Unavailable";
    $("gateway2").textContent = d.network.gateway || "Unavailable";
    $("dns2").textContent = d.network.dns_server || "Unavailable";
    $("hostname").textContent = d.network.hostname || "Unavailable";
    $("os").textContent = d.network.os || "Unavailable";
    $("latency").textContent = d.latency_ms != null ? `${d.latency_ms} ms` : "N/A";
    $("pingTarget").textContent = `Ping target: ${d.ping_target}`;
    setStatus("internet", d.internet, "ONLINE", "OFFLINE");
    setStatus("dns", d.dns, "RESOLVING", "FAILED");
    setStatus("gatewayCheck", d.gateway?.reachable, "AVAILABLE", "NOT FOUND");

    $("connBadge").textContent = d.health;
    $("connBadge").className = `badge ${d.health === "HEALTHY" ? "ok" : d.health === "DEGRADED" ? "warn" : "bad"}`;

    renderServices(d.services);
    renderDevices(d.devices);
    renderEvents(d.events);
    $("lastUpdated").textContent = new Date().toLocaleTimeString();
    $("pingResult").textContent = d.internet
      ? `Automatic check: ${d.ping_target} → reachable in ${d.latency_ms} ms`
      : `Automatic check: ${d.ping_target} → unreachable`;
  } catch (e) {
    $("connBadge").textContent = "BACKEND OFFLINE";
    $("connBadge").className = "badge bad";
    $("lastUpdated").textContent = "Failed";
    $("pingResult").textContent = e.message;
  }
}

$("refresh").addEventListener("click", loadDashboard);

document.querySelectorAll("[data-test]").forEach((button) => {
  button.addEventListener("click", async () => {
    const kind = button.dataset.test;
    const original = button.textContent;
    button.disabled = true;
    button.textContent = "Testing...";
    try {
      const d = await getJson(`/api/test/${kind}`, {method: "POST", headers: {"Content-Type": "application/json"}});
      $("pingResult").textContent = d.reachable
        ? `${d.host || kind} reachable${d.latency_ms != null ? ` — ${d.latency_ms} ms` : ""}`
        : `${d.host || kind} test failed`;
      await loadDashboard();
    } catch (e) {
      $("pingResult").textContent = e.message;
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  });
});

$("ping").addEventListener("click", async () => {
  const host = $("host").value.trim();
  if (!host) {
    $("pingResult").textContent = "Enter a host or IP address.";
    return;
  }
  const button = $("ping");
  button.disabled = true;
  $("pingResult").textContent = `Testing ${host}...`;
  try {
    const d = await getJson("/api/ping", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({host})
    });
    $("pingResult").textContent = d.reachable
      ? `${d.host} is reachable — ${d.latency_ms} ms`
      : `${d.host} did not respond`;
    await loadDashboard();
  } catch (e) {
    $("pingResult").textContent = e.message;
  } finally {
    button.disabled = false;
  }
});

$("scan").addEventListener("click", async () => {
  const target = $("scanTarget").value.trim();
  const start_port = Number($("scanStart").value);
  const end_port = Number($("scanEnd").value);
  const button = $("scan");
  button.disabled = true;
  $("scanStatus").textContent = "SCANNING";
  $("scanResult").textContent = `Scanning ${target} ports ${start_port}-${end_port}...`;
  $("scanTable").innerHTML = "";
  try {
    const d = await getJson("/api/scan", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({target, start_port, end_port})
    });
    $("scanStatus").textContent = "COMPLETE";
    $("openCount").textContent = d.open_ports.length;
    $("closedCount").textContent = d.closed_ports.length;
    $("scanDuration").textContent = `${d.duration_ms} ms`;
    $("scanResult").textContent = `${d.target}: ${d.open_ports.length} open, ${d.closed_ports.length} closed.`;
    renderScan(d.results);
    await loadDashboard();
  } catch (e) {
    $("scanStatus").textContent = "REJECTED";
    $("scanResult").textContent = e.message;
    $("openCount").textContent = "0";
    $("closedCount").textContent = "0";
    $("scanDuration").textContent = "--";
  } finally {
    button.disabled = false;
  }
});

$("clearScan").addEventListener("click", () => {
  $("scanStatus").textContent = "READY";
  $("openCount").textContent = "0";
  $("closedCount").textContent = "0";
  $("scanDuration").textContent = "--";
  $("scanResult").textContent = "No scan run yet.";
  $("scanTable").innerHTML = "";
});

$("export").addEventListener("click", () => { window.location.href = "/api/events.csv"; });

function updateClock() {
  $("clock").textContent = new Date().toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();
loadDashboard();
setInterval(loadDashboard, 30000);
