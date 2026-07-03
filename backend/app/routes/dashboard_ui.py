from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Dashboard UI"])


@router.get("/dashboard-ui", response_class=HTMLResponse)
def dashboard_ui():
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ITU AI CCTV Dashboard</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f4f6f8;
      --panel: #ffffff;
      --text: #17212b;
      --muted: #687381;
      --line: #dbe2ea;
      --accent: #0f766e;
      --accent-soft: #d9f2ee;
      --danger: #b42318;
      --danger-soft: #fde3df;
      --ok: #157347;
      --ok-soft: #dcf7e7;
      --warn: #996a13;
      --warn-soft: #fff1cf;
      --shadow: 0 8px 24px rgba(23, 33, 43, 0.08);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }

    header {
      background: #11202d;
      color: #ffffff;
      padding: 22px 16px;
    }

    .wrap {
      width: min(1180px, 100%);
      margin: 0 auto;
    }

    h1, h2, h3, p {
      margin-top: 0;
    }

    h1 {
      margin-bottom: 4px;
      font-size: clamp(24px, 4vw, 34px);
      letter-spacing: 0;
    }

    header p {
      margin-bottom: 0;
      color: #c7d2df;
    }

    main {
      padding: 18px 16px 32px;
    }

    .status-row {
      display: flex;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }

    .status-text {
      color: var(--muted);
      font-size: 14px;
    }

    .status-copy {
      display: grid;
      gap: 2px;
    }

    .quick-links {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }

    button, .quick-link {
      min-height: 38px;
      border: 1px solid var(--accent);
      border-radius: 6px;
      background: var(--accent);
      color: #ffffff;
      padding: 8px 12px;
      cursor: pointer;
      font-weight: 700;
      line-height: 1.2;
    }

    .quick-link {
      display: inline-flex;
      align-items: center;
      text-decoration: none;
    }

    button:hover, .quick-link:hover {
      background: #0b5f59;
      color: #ffffff;
    }

    button:focus, .quick-link:focus {
      outline: 3px solid rgba(15, 118, 110, 0.25);
      outline-offset: 2px;
    }

    .grid {
      display: grid;
      gap: 14px;
    }

    .metrics {
      grid-template-columns: repeat(4, minmax(0, 1fr));
      margin-bottom: 14px;
    }

    .two-col {
      grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.7fr);
      align-items: start;
    }

    .panel, .metric {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }

    .panel {
      padding: 16px;
      overflow: hidden;
    }

    .metric {
      padding: 14px;
    }

    .metric .label {
      color: var(--muted);
      font-size: 13px;
    }

    .metric .value {
      margin-top: 4px;
      font-size: 28px;
      font-weight: 800;
    }

    .section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
    }

    .section-title h2 {
      margin-bottom: 0;
      font-size: 18px;
    }

    .list {
      display: grid;
      gap: 10px;
    }

    .item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #ffffff;
    }

    .item-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 6px;
    }

    .item-title {
      font-weight: 800;
      overflow-wrap: anywhere;
    }

    .meta {
      color: var(--muted);
      font-size: 13px;
      overflow-wrap: anywhere;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      font-weight: 800;
      white-space: nowrap;
    }

    .badge.ok {
      color: var(--ok);
      background: var(--ok-soft);
    }

    .badge.warn {
      color: var(--warn);
      background: var(--warn-soft);
    }

    .badge.danger {
      color: var(--danger);
      background: var(--danger-soft);
    }

    .badge.neutral {
      color: var(--accent);
      background: var(--accent-soft);
    }

    .event-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 86px;
      gap: 12px;
      align-items: start;
    }

    .thumb {
      width: 86px;
      height: 64px;
      object-fit: cover;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #eef2f6;
    }

    .thumb-link {
      display: inline-flex;
      border-radius: 6px;
    }

    .thumb-link:focus {
      outline: 3px solid rgba(15, 118, 110, 0.25);
      outline-offset: 2px;
    }

    .camera-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }

    .camera-stats {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 8px;
    }

    .health-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
    }

    .health-stat {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: #fbfcfd;
    }

    .health-stat .label {
      color: var(--muted);
      font-size: 13px;
    }

    .health-stat .value {
      margin-top: 4px;
      font-size: 18px;
      font-weight: 800;
      overflow-wrap: anywhere;
    }

    a {
      color: var(--accent);
      font-weight: 700;
    }

    .empty {
      padding: 14px;
      border: 1px dashed var(--line);
      border-radius: 8px;
      color: var(--muted);
      background: #fbfcfd;
    }

    .error {
      color: var(--danger);
      font-weight: 700;
    }

    @media (max-width: 860px) {
      .metrics, .two-col, .camera-grid, .health-grid {
        grid-template-columns: 1fr;
      }

      .status-row {
        align-items: stretch;
      }

      .quick-links {
        justify-content: stretch;
      }

      .quick-links > * {
        flex: 1 1 145px;
        justify-content: center;
      }

      .event-row {
        grid-template-columns: 1fr;
      }

      .thumb {
        width: 100%;
        height: 150px;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>ITU AI CCTV Dashboard</h1>
      <p>Camera and event overview from existing dashboard data.</p>
    </div>
  </header>

  <main>
    <div class="wrap">
      <div class="status-row">
        <div class="status-copy">
          <div id="loadStatus" class="status-text">Loading dashboard...</div>
          <div id="refreshStatus" class="status-text">Next refresh in 30s</div>
        </div>
        <nav class="quick-links" aria-label="Dashboard quick links">
          <button type="button" id="refreshButton">Refresh now</button>
          <a class="quick-link" href="/dashboard/summary" target="_blank" rel="noopener">Summary</a>
          <a class="quick-link" href="/dashboard/cameras" target="_blank" rel="noopener">Cameras</a>
          <a class="quick-link" href="/dashboard/events/latest" target="_blank" rel="noopener">Latest events</a>
          <a class="quick-link" href="/dashboard/evidence" target="_blank" rel="noopener">Evidence</a>
          <a class="quick-link" href="/dashboard/health" target="_blank" rel="noopener">Health</a>
        </nav>
      </div>

      <section class="grid metrics" aria-label="Dashboard totals">
        <div class="metric">
          <div class="label">Total cameras</div>
          <div id="totalCameras" class="value">-</div>
        </div>
        <div class="metric">
          <div class="label">Enabled</div>
          <div id="enabledCameras" class="value">-</div>
        </div>
        <div class="metric">
          <div class="label">Disabled</div>
          <div id="disabledCameras" class="value">-</div>
        </div>
        <div class="metric">
          <div class="label">Latest events shown</div>
          <div id="latestEventsCount" class="value">-</div>
        </div>
      </section>

      <section class="panel" style="margin-bottom: 14px;" aria-label="Dashboard health">
        <div class="section-title">
          <h2>Health</h2>
          <span id="healthBadge" class="badge neutral">Waiting</span>
        </div>
        <div class="health-grid">
          <div class="health-stat">
            <div class="label">Total cameras</div>
            <div id="healthTotalCameras" class="value">-</div>
          </div>
          <div class="health-stat">
            <div class="label">Enabled</div>
            <div id="healthEnabledCameras" class="value">-</div>
          </div>
          <div class="health-stat">
            <div class="label">Disabled</div>
            <div id="healthDisabledCameras" class="value">-</div>
          </div>
          <div class="health-stat">
            <div class="label">Latest event</div>
            <div id="healthLatestEventTime" class="value">-</div>
          </div>
        </div>
      </section>

      <section class="grid two-col">
        <div class="grid">
          <div class="panel">
            <div class="section-title">
              <h2>Latest Event</h2>
              <span id="latestEventBadge" class="badge neutral">Waiting</span>
            </div>
            <div id="latestEventSummary" class="empty">No latest event loaded.</div>
          </div>

          <div class="panel">
            <div class="section-title">
              <h2>Latest 10 Events</h2>
            </div>
            <div id="latestEvents" class="list"></div>
          </div>
        </div>

        <aside class="grid">
          <div class="panel">
            <div class="section-title">
              <h2>Disabled Cameras</h2>
            </div>
            <div id="disabledCameraList" class="list"></div>
          </div>

          <div class="panel">
            <div class="section-title">
              <h2>Recent Evidence</h2>
            </div>
            <div id="evidenceList" class="list"></div>
          </div>
        </aside>
      </section>

      <section class="panel" style="margin-top: 14px;">
        <div class="section-title">
          <h2>Cameras</h2>
        </div>
        <div id="cameraList" class="camera-grid"></div>
      </section>
    </div>
  </main>

  <script>
    const endpoints = {
      summary: "/dashboard/summary",
      cameras: "/dashboard/cameras",
      latestEvents: "/dashboard/events/latest?limit=10",
      evidence: "/dashboard/evidence?limit=8",
      health: "/dashboard/health"
    };
    const refreshIntervalSeconds = 30;
    let nextRefreshAt = Date.now() + refreshIntervalSeconds * 1000;
    let isLoading = false;

    const el = (id) => document.getElementById(id);

    function clearNode(node) {
      while (node.firstChild) {
        node.removeChild(node.firstChild);
      }
    }

    function text(value, fallback = "-") {
      if (value === null || value === undefined || value === "") {
        return fallback;
      }
      return String(value);
    }

    function formatTime(value) {
      if (!value) {
        return "-";
      }

      const date = new Date(value);

      if (Number.isNaN(date.getTime())) {
        return value;
      }

      return date.toLocaleString();
    }

    function makeBadge(label, tone) {
      const badge = document.createElement("span");
      badge.className = `badge ${tone || "neutral"}`;
      badge.textContent = label;
      return badge;
    }

    function healthTone(status) {
      if (status === "active") {
        return "ok";
      }

      if (status === "disabled" || status === "warning" || status === "failing") {
        return "warn";
      }

      if (status === "failed") {
        return "danger";
      }

      return "neutral";
    }

    function eventTone(event) {
      const type = String(event?.event_type || "").toLowerCase();

      if (event?.person_detected || type === "person" || type === "person_detected") {
        return "danger";
      }

      if (type === "no_person") {
        return "ok";
      }

      return "neutral";
    }

    function eventLabel(event) {
      const type = text(event?.event_type, event?.person_detected ? "person" : "no_person");

      if (event?.person_detected || type === "person_detected" || type === "person") {
        return "person";
      }

      if (type === "no_person") {
        return "clear";
      }

      return type;
    }

    function cameraIdFromEvent(event) {
      return event?.camera?.id || event?.camera_id || "unknown_camera";
    }

    function evidenceUrlFromImage(image) {
      if (image?.url) {
        return image.url;
      }

      if (image?.filename) {
        return `/events/evidence/${encodeURIComponent(image.filename)}`;
      }

      return "";
    }

    function resetRefreshCountdown() {
      nextRefreshAt = Date.now() + refreshIntervalSeconds * 1000;
      updateRefreshStatus();
    }

    function updateRefreshStatus() {
      const remaining = Math.max(0, Math.ceil((nextRefreshAt - Date.now()) / 1000));
      el("refreshStatus").textContent = `Next refresh in ${remaining}s`;
    }

    function renderEmpty(container, message) {
      clearNode(container);
      const node = document.createElement("div");
      node.className = "empty";
      node.textContent = message;
      container.appendChild(node);
    }

    async function getJson(url) {
      const response = await fetch(url, { cache: "no-store" });

      if (!response.ok) {
        throw new Error(`${url} returned ${response.status}`);
      }

      return response.json();
    }

    function renderLatestSummary(summary) {
      const latest = summary?.events?.latest_event;
      const box = el("latestEventSummary");
      const badge = el("latestEventBadge");
      clearNode(box);
      box.className = "empty";
      badge.className = "badge neutral";
      badge.textContent = "No event";

      if (!latest) {
        box.textContent = "No latest event is available yet.";
        return;
      }

      badge.className = `badge ${eventTone(latest)}`;
      badge.textContent = latest.event_type || "event";

      const title = document.createElement("div");
      title.className = "item-title";
      title.textContent = latest.person_detected ? "Person detected" : "No person detected";

      const meta = document.createElement("div");
      meta.className = "meta";
      meta.textContent = `Time: ${formatTime(latest.timestamp)} | Severity: ${text(latest.severity)}`;

      box.className = "item";
      box.append(title, meta);
    }

    function renderDisabled(summary) {
      const list = el("disabledCameraList");
      clearNode(list);
      const cameras = summary?.disabled_cameras || [];

      if (!cameras.length) {
        renderEmpty(list, "No disabled cameras.");
        return;
      }

      cameras.forEach((camera) => {
        const item = document.createElement("div");
        item.className = "item";

        const head = document.createElement("div");
        head.className = "item-head";

        const title = document.createElement("div");
        title.className = "item-title";
        title.textContent = text(camera.camera_name || camera.camera_id);

        head.append(title, makeBadge("disabled", "warn"));

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `ID: ${text(camera.camera_id)} | IP: ${text(camera.camera_host)} | Channel: ${text(camera.channel)}`;

        const notes = document.createElement("div");
        notes.className = "meta";
        notes.textContent = text(camera.notes, "");

        item.append(head, meta, notes);
        list.appendChild(item);
      });
    }

    function renderEvents(eventsData) {
      const list = el("latestEvents");
      clearNode(list);
      const events = eventsData?.events || [];
      el("latestEventsCount").textContent = events.length;

      if (!events.length) {
        renderEmpty(list, "No events found.");
        return;
      }

      events.forEach((event) => {
        const item = document.createElement("div");
        item.className = "item event-row";

        const details = document.createElement("div");
        const head = document.createElement("div");
        head.className = "item-head";

        const title = document.createElement("div");
        title.className = "item-title";
        title.textContent = text(event.event_type, "event");

        const badge = makeBadge(eventLabel(event), eventTone(event));
        head.append(title, badge);

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `Camera: ${cameraIdFromEvent(event)} | Time: ${formatTime(event.timestamp)}`;

        const message = document.createElement("div");
        message.className = "meta";
        message.textContent = text(event.message, "");

        details.append(head, meta, message);
        item.appendChild(details);

        if (event.evidence_url) {
          const link = document.createElement("a");
          link.className = "thumb-link";
          link.href = event.evidence_url;
          link.target = "_blank";
          link.rel = "noopener";
          link.setAttribute("aria-label", "Open evidence image");
          const img = document.createElement("img");
          img.className = "thumb";
          img.alt = "Evidence image";
          img.src = event.evidence_url;
          link.appendChild(img);
          item.appendChild(link);
        }

        list.appendChild(item);
      });
    }

    function renderHealth(healthData) {
      const cameras = healthData?.cameras || {};
      const events = healthData?.events || {};
      const badge = el("healthBadge");

      el("healthTotalCameras").textContent = text(cameras.total);
      el("healthEnabledCameras").textContent = text(cameras.enabled);
      el("healthDisabledCameras").textContent = text(cameras.disabled);
      el("healthLatestEventTime").textContent = formatTime(events.latest_event_time);

      badge.className = cameras.disabled ? "badge warn" : "badge ok";
      badge.textContent = cameras.disabled ? `${cameras.disabled} disabled` : "ok";
    }

    function renderEvidence(evidenceData) {
      const list = el("evidenceList");
      clearNode(list);
      const evidence = evidenceData?.evidence || [];

      if (!evidence.length) {
        renderEmpty(list, "No evidence images found.");
        return;
      }

      evidence.slice(0, 4).forEach((image) => {
        const item = document.createElement("div");
        item.className = "item event-row";

        const details = document.createElement("div");
        const title = document.createElement("div");
        title.className = "item-title";
        title.textContent = text(image.filename);

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `Modified: ${formatTime(image.modified_time)} | Size: ${text(image.size_bytes)} bytes`;

        details.append(title, meta);
        item.appendChild(details);

        const imageUrl = evidenceUrlFromImage(image);
        if (imageUrl) {
          const link = document.createElement("a");
          link.className = "thumb-link";
          link.href = imageUrl;
          link.target = "_blank";
          link.rel = "noopener";
          link.setAttribute("aria-label", `Open evidence ${text(image.filename)}`);
          const img = document.createElement("img");
          img.className = "thumb";
          img.alt = "Evidence thumbnail";
          img.src = imageUrl;
          link.appendChild(img);
          item.appendChild(link);
        }

        list.appendChild(item);
      });
    }

    async function renderCameras(camerasData, healthData) {
      const list = el("cameraList");
      clearNode(list);
      const cameras = camerasData?.cameras || [];
      const totals = camerasData?.totals || {};
      const healthByCamera = {};
      (healthData?.per_camera || []).forEach((camera) => {
        healthByCamera[camera.camera_id] = camera;
      });
      el("totalCameras").textContent = text(totals.total);
      el("enabledCameras").textContent = text(totals.enabled);
      el("disabledCameras").textContent = text(totals.disabled);

      if (!cameras.length) {
        renderEmpty(list, "No configured cameras found.");
        return;
      }

      const statsResults = await Promise.all(
        cameras.map(async (camera) => {
          try {
            return await getJson(`/dashboard/cameras/${encodeURIComponent(camera.camera_id)}/stats`);
          } catch {
            return null;
          }
        })
      );

      cameras.forEach((camera, index) => {
        const stats = statsResults[index];
        const health = healthByCamera[camera.camera_id] || {};
        const item = document.createElement("div");
        item.className = "item";

        const head = document.createElement("div");
        head.className = "item-head";

        const title = document.createElement("div");
        title.className = "item-title";
        title.textContent = text(camera.name || camera.camera_id);

        head.append(title, makeBadge(camera.enabled ? "enabled" : "disabled", camera.enabled ? "ok" : "danger"));

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `ID: ${text(camera.camera_id)} | IP: ${text(camera.ip)} | Channel: ${text(camera.channel)}`;

        const notes = document.createElement("div");
        notes.className = "meta";
        notes.textContent = text(camera.notes, "");

        const statsRow = document.createElement("div");
        statsRow.className = "camera-stats";
        statsRow.append(
          makeBadge(text(health.health_status, "unknown"), healthTone(health.health_status)),
          makeBadge(`events ${text(stats?.total_events, "0")}`, "neutral"),
          makeBadge(`person ${text(stats?.person_events, "0")}`, "danger")
        );

        if (stats?.latest_evidence_url) {
          const evidenceLink = document.createElement("a");
          evidenceLink.href = stats.latest_evidence_url;
          evidenceLink.target = "_blank";
          evidenceLink.rel = "noopener";
          evidenceLink.textContent = "Latest evidence";
          statsRow.appendChild(evidenceLink);
        }

        item.append(head, meta, notes, statsRow);
        list.appendChild(item);
      });
    }

    async function loadDashboard() {
      if (isLoading) {
        return;
      }

      isLoading = true;
      const status = el("loadStatus");
      status.className = "status-text";
      status.textContent = "Loading dashboard...";

      try {
        const [summary, cameras, events, evidence, health] = await Promise.all([
          getJson(endpoints.summary),
          getJson(endpoints.cameras),
          getJson(endpoints.latestEvents),
          getJson(endpoints.evidence),
          getJson(endpoints.health)
        ]);

        renderLatestSummary(summary);
        renderDisabled(summary);
        renderEvents(events);
        renderEvidence(evidence);
        renderHealth(health);
        await renderCameras(cameras, health);

        status.textContent = `Last updated ${new Date().toLocaleString()}`;
      } catch (error) {
        status.className = "status-text error";
        status.textContent = `Dashboard load failed: ${error.message}`;
      } finally {
        resetRefreshCountdown();
        isLoading = false;
      }
    }

    el("refreshButton").addEventListener("click", loadDashboard);
    setInterval(() => {
      updateRefreshStatus();

      if (Date.now() >= nextRefreshAt) {
        loadDashboard();
      }
    }, 1000);
    loadDashboard();
  </script>
</body>
</html>
"""
