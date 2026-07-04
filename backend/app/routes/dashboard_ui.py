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
  <title>ITU AI CCTV Command Center</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #080c12;
      --bg-soft: #0e141d;
      --panel: #111924;
      --panel-2: #151f2d;
      --panel-3: #1b2736;
      --text: #edf4fb;
      --muted: #9aa8b8;
      --line: #263445;
      --line-bright: #375069;
      --accent: #20c6b7;
      --accent-2: #4da3ff;
      --accent-soft: rgba(32, 198, 183, 0.16);
      --danger: #ff5f6d;
      --danger-soft: rgba(255, 95, 109, 0.16);
      --ok: #39d98a;
      --ok-soft: rgba(57, 217, 138, 0.16);
      --warn: #ffc857;
      --warn-soft: rgba(255, 200, 87, 0.16);
      --muted-soft: rgba(154, 168, 184, 0.14);
      --shadow: 0 18px 46px rgba(0, 0, 0, 0.32);
    }

    * {
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(32, 198, 183, 0.14), transparent 30%),
        linear-gradient(180deg, #0a1018 0%, var(--bg) 42%, #070a0f 100%);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
      background-size: 48px 48px;
      mask-image: linear-gradient(to bottom, rgba(0,0,0,0.55), transparent 70%);
    }

    a {
      color: var(--accent);
      font-weight: 700;
    }

    h1, h2, h3, p {
      margin-top: 0;
    }

    .wrap {
      width: min(1280px, 100%);
      margin: 0 auto;
    }

    header {
      position: sticky;
      top: 0;
      z-index: 10;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      background: rgba(8, 12, 18, 0.88);
      backdrop-filter: blur(18px);
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: center;
      padding: 20px 16px 14px;
    }

    .title-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }

    h1 {
      margin: 0;
      font-size: clamp(26px, 4vw, 42px);
      letter-spacing: 0;
    }

    .subtitle {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 15px;
      max-width: 760px;
    }

    .header-meta {
      display: grid;
      justify-items: end;
      gap: 6px;
      color: var(--muted);
      font-size: 13px;
      text-align: right;
    }

    .live-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 24px;
      border: 1px solid rgba(57, 217, 138, 0.8);
      border-radius: 999px;
      padding: 3px 9px;
      color: #d8ffed;
      background: rgba(57, 217, 138, 0.12);
      font-size: 12px;
      font-weight: 900;
      white-space: nowrap;
      box-shadow: 0 0 18px rgba(57, 217, 138, 0.14);
    }

    .live-dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--ok);
      box-shadow: 0 0 0 0 rgba(57, 217, 138, 0.65);
      animation: livePulse 1.8s infinite;
    }

    .header-scanline {
      height: 2px;
      overflow: hidden;
      background: rgba(255,255,255,0.04);
    }

    .header-scanline::before {
      content: "";
      display: block;
      width: 42%;
      height: 100%;
      background: linear-gradient(90deg, transparent, var(--accent), transparent);
      animation: scanLine 3.2s linear infinite;
    }

    main {
      padding: 24px 16px 36px;
    }

    #summary-section,
    #health-section,
    #latest-events-section,
    #evidence-section,
    #cameras-section {
      scroll-margin-top: 126px;
    }

    .status-row {
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }

    .status-copy {
      display: grid;
      gap: 3px;
    }

    .status-text {
      color: var(--muted);
      font-size: 14px;
    }

    .quick-links {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }

    button, .quick-link {
      min-height: 38px;
      border: 1px solid var(--line-bright);
      border-radius: 8px;
      background: linear-gradient(180deg, #1b2a3a, #14202c);
      color: var(--text);
      padding: 8px 12px;
      cursor: pointer;
      font-weight: 800;
      line-height: 1.2;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.22);
    }

    button:hover, .quick-link:hover {
      border-color: var(--accent);
      background: linear-gradient(180deg, #203447, #172838);
      color: #ffffff;
      transform: translateY(-1px);
    }

    button:active, .quick-link:active {
      transform: translateY(1px);
      box-shadow: none;
    }

    button.active, .quick-link.active {
      border-color: var(--accent);
      background: var(--accent-soft);
      color: #dffefa;
      box-shadow: inset 0 0 0 1px rgba(32, 198, 183, 0.35);
    }

    button:disabled {
      cursor: wait;
      opacity: 0.72;
      transform: none;
    }

    button:focus, .quick-link:focus, a:focus {
      outline: 3px solid rgba(32, 198, 183, 0.28);
      outline-offset: 2px;
    }

    .primary-button {
      border-color: rgba(32, 198, 183, 0.7);
      background: linear-gradient(180deg, #1dd0c1, #118d85);
      color: #041013;
    }

    .grid {
      display: grid;
      gap: 14px;
    }

    .metrics {
      grid-template-columns: repeat(4, minmax(0, 1fr));
      margin-bottom: 14px;
    }

    .command-grid {
      grid-template-columns: minmax(0, 1.15fr) minmax(340px, 0.85fr);
      align-items: start;
    }

    .panel, .metric {
      background: linear-gradient(180deg, rgba(21, 31, 45, 0.96), rgba(13, 20, 29, 0.96));
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }

    .panel {
      padding: 16px;
      overflow: hidden;
    }

    .metric {
      position: relative;
      min-height: 124px;
      padding: 16px;
    }

    .metric::after {
      content: "";
      position: absolute;
      left: 16px;
      right: 16px;
      bottom: 0;
      height: 3px;
      border-radius: 999px 999px 0 0;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
    }

    .metric .label, .health-stat .label, .field-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .metric .value {
      margin-top: 10px;
      font-size: clamp(32px, 5vw, 46px);
      font-weight: 900;
      line-height: 1;
      overflow-wrap: anywhere;
    }

    .section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
    }

    .section-title h2 {
      margin: 0;
      font-size: 18px;
      letter-spacing: 0;
    }

    .section-kicker {
      color: var(--muted);
      font-size: 13px;
      margin-top: -4px;
      margin-bottom: 12px;
    }

    .list {
      display: grid;
      gap: 10px;
    }

    .item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: rgba(10, 16, 24, 0.56);
    }

    .item-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 7px;
    }

    .item-title {
      font-weight: 900;
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
      justify-content: center;
      min-height: 24px;
      border: 1px solid currentColor;
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      font-weight: 900;
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

    .badge.muted {
      color: var(--muted);
      background: var(--muted-soft);
    }

    .badge.ok::before,
    .badge.warn::before,
    .badge.danger::before {
      content: "";
      width: 7px;
      height: 7px;
      margin-right: 6px;
      border-radius: 999px;
      background: currentColor;
      box-shadow: 0 0 10px currentColor;
    }

    .badge.warn {
      box-shadow: 0 0 16px rgba(255, 200, 87, 0.11);
    }

    .badge.danger {
      box-shadow: 0 0 18px rgba(255, 95, 109, 0.13);
    }

    .health-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
    }

    .health-stat {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: rgba(255,255,255,0.035);
      min-height: 82px;
    }

    .health-stat .value {
      margin-top: 8px;
      font-size: 21px;
      font-weight: 900;
      overflow-wrap: anywhere;
    }

    .health-stat.danger {
      border-color: rgba(255, 95, 109, 0.42);
      background: var(--danger-soft);
    }

    .health-stat.warn {
      border-color: rgba(255, 200, 87, 0.42);
      background: var(--warn-soft);
    }

    .latest-event-card {
      display: grid;
      gap: 12px;
      padding: 16px;
      border: 1px solid var(--line-bright);
      border-radius: 8px;
      background: linear-gradient(135deg, rgba(32, 198, 183, 0.12), rgba(77, 163, 255, 0.08));
    }

    .latest-event-card.person-alert {
      border-color: rgba(255, 95, 109, 0.72);
      background: linear-gradient(135deg, rgba(255, 95, 109, 0.18), rgba(77, 163, 255, 0.08));
      box-shadow: 0 0 0 1px rgba(255, 95, 109, 0.22), 0 18px 48px rgba(255, 95, 109, 0.12);
      animation: alertGlow 2.4s ease-in-out infinite;
    }

    .latest-event-title {
      font-size: clamp(22px, 4vw, 34px);
      font-weight: 900;
      line-height: 1.1;
      overflow-wrap: anywhere;
    }

    .field-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .field {
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.035);
      min-width: 0;
    }

    .field-value {
      margin-top: 5px;
      font-weight: 800;
      overflow-wrap: anywhere;
    }

    .timeline {
      position: relative;
      display: grid;
      gap: 10px;
    }

    .timeline-item {
      position: relative;
      display: grid;
      grid-template-columns: 18px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: start;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: rgba(10, 16, 24, 0.56);
    }

    .timeline-dot {
      width: 12px;
      height: 12px;
      margin-top: 5px;
      border-radius: 999px;
      background: var(--accent);
      box-shadow: 0 0 0 5px var(--accent-soft);
    }

    .timeline-item.person {
      border-color: rgba(255, 95, 109, 0.46);
      background: linear-gradient(90deg, rgba(255, 95, 109, 0.13), rgba(10, 16, 24, 0.64));
      box-shadow: 0 0 22px rgba(255, 95, 109, 0.08);
    }

    .timeline-item.person .timeline-dot {
      background: var(--danger);
      box-shadow: 0 0 0 5px var(--danger-soft);
      animation: alertDot 1.7s ease-in-out infinite;
    }

    .thumb {
      width: 120px;
      height: 82px;
      object-fit: cover;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0b1119;
    }

    .thumb-link {
      display: inline-flex;
      border-radius: 8px;
    }

    .evidence-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
    }

    .evidence-note {
      margin-bottom: 10px;
      color: var(--muted);
      font-size: 13px;
      overflow-wrap: anywhere;
    }

    .evidence-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
      align-items: start;
    }

    .evidence-card {
      display: grid;
      gap: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: rgba(10, 16, 24, 0.58);
      min-width: 0;
      max-width: 100%;
      overflow: hidden;
      transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
    }

    .evidence-card:hover {
      transform: translateY(-2px);
      border-color: rgba(32, 198, 183, 0.55);
      box-shadow: 0 18px 38px rgba(0, 0, 0, 0.28), 0 0 22px rgba(32, 198, 183, 0.08);
    }

    .evidence-card.person-evidence {
      border-color: rgba(255, 95, 109, 0.32);
      box-shadow: 0 0 18px rgba(255, 95, 109, 0.06);
    }

    .evidence-card .thumb {
      width: 100%;
      max-width: 100%;
      height: 160px;
      object-fit: cover;
    }

    .evidence-card .thumb-link,
    .evidence-card .item-head,
    .evidence-card .meta {
      min-width: 0;
      max-width: 100%;
      overflow-wrap: anywhere;
    }

    .filename-compact {
      display: block;
      max-width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .camera-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .camera-card {
      display: grid;
      gap: 10px;
      min-height: 210px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 13px;
      background: rgba(10, 16, 24, 0.58);
    }

    .camera-card.offline, .camera-card.disabled {
      border-color: rgba(255, 95, 109, 0.38);
    }

    .camera-card.stale, .camera-card.no_recent_event {
      border-color: rgba(255, 200, 87, 0.36);
      box-shadow: 0 0 18px rgba(255, 200, 87, 0.07);
    }

    .camera-stats {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }

    .empty {
      padding: 14px;
      border: 1px dashed var(--line-bright);
      border-radius: 8px;
      color: var(--muted);
      background: rgba(255,255,255,0.035);
    }

    .error {
      color: var(--danger);
      font-weight: 800;
    }

    @keyframes livePulse {
      0% { box-shadow: 0 0 0 0 rgba(57, 217, 138, 0.65); }
      70% { box-shadow: 0 0 0 8px rgba(57, 217, 138, 0); }
      100% { box-shadow: 0 0 0 0 rgba(57, 217, 138, 0); }
    }

    @keyframes alertGlow {
      0%, 100% { box-shadow: 0 0 0 1px rgba(255, 95, 109, 0.18), 0 18px 48px rgba(255, 95, 109, 0.10); }
      50% { box-shadow: 0 0 0 1px rgba(255, 95, 109, 0.34), 0 18px 54px rgba(255, 95, 109, 0.19); }
    }

    @keyframes alertDot {
      0%, 100% { transform: scale(1); box-shadow: 0 0 0 5px var(--danger-soft); }
      50% { transform: scale(1.18); box-shadow: 0 0 0 8px rgba(255, 95, 109, 0.08); }
    }

    @keyframes scanLine {
      0% { transform: translateX(-100%); }
      100% { transform: translateX(260%); }
    }

    @media (prefers-reduced-motion: reduce) {
      html {
        scroll-behavior: auto;
      }

      *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001ms !important;
      }
    }

    @media (max-width: 1050px) {
      .command-grid, .camera-grid {
        grid-template-columns: 1fr;
      }

      .evidence-grid {
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      }
    }

    @media (max-width: 860px) {
      header {
        position: static;
      }

      .hero, .metrics, .health-grid, .field-grid, .evidence-grid {
        grid-template-columns: 1fr;
      }

      #summary-section,
      #health-section,
      #latest-events-section,
      #evidence-section,
      #cameras-section {
        scroll-margin-top: 16px;
      }

      .header-meta {
        justify-items: start;
        text-align: left;
      }

      .status-row {
        align-items: stretch;
      }

      .quick-links {
        justify-content: stretch;
      }

      .quick-links > * {
        flex: 1 1 140px;
        justify-content: center;
      }

      .timeline-item {
        grid-template-columns: 18px minmax(0, 1fr);
      }

      .timeline-item .thumb-link {
        grid-column: 1 / -1;
      }

      .thumb, .evidence-card .thumb {
        width: 100%;
        height: 180px;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap hero">
      <div>
        <div class="title-row">
          <h1>ITU AI CCTV Command Center</h1>
          <span class="badge neutral">Production Server</span>
          <span class="live-pill"><span class="live-dot" aria-hidden="true"></span>LIVE AI MONITORING</span>
        </div>
        <p class="subtitle">Real-time AI surveillance, evidence, health and alert monitoring</p>
      </div>
      <div class="header-meta">
        <div id="loadStatus">Loading dashboard...</div>
        <div id="refreshStatus">Next refresh in 30s</div>
      </div>
    </div>
    <div class="header-scanline" aria-hidden="true"></div>
  </header>

  <main>
    <div class="wrap">
      <div class="status-row">
        <div class="status-copy">
          <div class="status-text">Operations view from existing dashboard APIs</div>
          <div id="monitoringLine" class="status-text">AI scan status loading...</div>
        </div>
        <nav class="quick-links" aria-label="Dashboard quick links">
          <button type="button" id="refreshButton" class="primary-button">Refresh now</button>
          <button type="button" class="quick-link" data-scroll-target="summary-section">Summary</button>
          <button type="button" class="quick-link" data-scroll-target="health-section">Health</button>
          <button type="button" class="quick-link" data-scroll-target="latest-events-section">Latest events</button>
          <button type="button" class="quick-link" data-scroll-target="evidence-section">Evidence</button>
          <button type="button" class="quick-link" data-scroll-target="cameras-section">Cameras</button>
        </nav>
      </div>

      <section id="summary-section" class="grid metrics" aria-label="Dashboard totals">
        <div class="metric">
          <div class="label">Total Cameras</div>
          <div id="totalCameras" class="value">-</div>
        </div>
        <div class="metric">
          <div class="label">Enabled Cameras</div>
          <div id="enabledCameras" class="value">-</div>
        </div>
        <div class="metric">
          <div class="label">Disabled Cameras</div>
          <div id="disabledCameras" class="value">-</div>
        </div>
        <div class="metric">
          <div class="label">Latest Events Shown</div>
          <div id="latestEventsCount" class="value">-</div>
        </div>
      </section>

      <section id="health-section" class="panel" style="margin-bottom: 14px;" aria-label="Dashboard health">
        <div class="section-title">
          <h2>AI Status / Health</h2>
          <span id="healthBadge" class="badge neutral">Waiting</span>
        </div>
        <p class="section-kicker">System status, scheduler signal and camera health from the current backend dashboard data. Stale status is based on each camera stale_threshold_minutes value.</p>
        <div class="health-grid">
          <div class="health-stat">
            <div class="label">System Status</div>
            <div id="systemStatus" class="value">Loading</div>
          </div>
          <div class="health-stat">
            <div class="label">Scheduler Latest Run</div>
            <div id="schedulerLatestRunTime" class="value">-</div>
          </div>
          <div class="health-stat">
            <div class="label">Scheduler Summary</div>
            <div id="schedulerLatestSummary" class="value">-</div>
          </div>
          <div class="health-stat">
            <div class="label">Latest Event</div>
            <div id="healthLatestEventTime" class="value">-</div>
          </div>
          <div class="health-stat">
            <div class="label">Health Cameras</div>
            <div id="healthCameraTotals" class="value">-</div>
          </div>
          <div class="health-stat">
            <div class="label">Active</div>
            <div id="healthActiveCount" class="value">-</div>
          </div>
          <div class="health-stat warn">
            <div class="label">Stale / No Recent</div>
            <div id="healthStaleReviewCount" class="value">-</div>
          </div>
          <div class="health-stat danger">
            <div class="label">Offline / Disabled</div>
            <div id="healthOfflineDisabledCount" class="value">-</div>
          </div>
        </div>
      </section>

      <section class="grid command-grid">
        <div class="grid">
          <div class="panel">
            <div class="section-title">
              <h2>Latest AI Event</h2>
              <span id="latestEventBadge" class="badge neutral">Waiting</span>
            </div>
            <div id="latestEventSummary" class="empty">No latest event loaded.</div>
          </div>

          <div id="latest-events-section" class="panel">
            <div class="section-title">
              <h2>Event Timeline</h2>
            </div>
            <div id="latestEvents" class="timeline"></div>
          </div>
        </div>

        <aside class="grid">
          <div class="panel">
            <div class="section-title">
              <h2>Disabled Cameras</h2>
            </div>
            <div id="disabledCameraList" class="list"></div>
          </div>

          <div id="evidence-section" class="panel">
            <div class="section-title">
              <h2>Evidence Gallery</h2>
            </div>
            <div class="evidence-actions">
              <button type="button" id="refreshEvidenceButton">Refresh Evidence</button>
              <button type="button" id="copyEvidencePathButton">Copy Evidence Folder Path</button>
            </div>
            <div id="evidenceFolderNote" class="evidence-note">
              Evidence folder: \\\\192.168.1.254\\ituaicctv-evidence
            </div>
            <div class="evidence-note">
              Evidence images are stored on the Windows Server. Paste this path into File Explorer if browser blocks direct folder links.
            </div>
            <div id="evidenceList" class="evidence-grid"></div>
          </div>
        </aside>
      </section>

      <section id="cameras-section" class="panel" style="margin-top: 14px;">
        <div class="section-title">
          <h2>Camera Grid</h2>
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
    const evidenceFolderPath = "\\\\\\\\192.168.1.254\\\\ituaicctv-evidence";
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

    function formatConfidence(value) {
      if (value === null || value === undefined || value === "") {
        return "-";
      }

      const numberValue = Number(value);

      if (Number.isNaN(numberValue)) {
        return text(value);
      }

      return numberValue.toFixed(2);
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

      if (status === "stale" || status === "no_recent_event" || status === "warning" || status === "failing") {
        return "warn";
      }

      if (status === "failed" || status === "offline") {
        return "danger";
      }

      if (status === "disabled") {
        return "muted";
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
        return "person detected";
      }

      if (type === "no_person") {
        return "clear";
      }

      return type;
    }

    function confidenceNumber(value) {
      if (value === null || value === undefined || value === "") {
        return null;
      }

      const numberValue = Number(value);
      return Number.isNaN(numberValue) ? null : numberValue;
    }

    function maxConfidence(event) {
      const detections = event?.detections || [];
      const confidences = detections
        .map((detection) => detection?.confidence)
        .map(confidenceNumber)
        .filter((confidence) => confidence !== null);

      if (!confidences.length) {
        return confidenceNumber(event?.highest_confidence)
          ?? confidenceNumber(event?.max_confidence)
          ?? confidenceNumber(event?.confidence);
      }

      return Math.max(...confidences);
    }

    function cameraIdFromEvent(event) {
      const nestedId = event?.camera?.id || event?.camera?.camera_id || "";

      if (nestedId && nestedId !== "unknown_camera") {
        return nestedId;
      }

      return event?.camera_id || event?.camera_id_from_log || "";
    }

    function makeCameraNameMap(camerasData) {
      const map = {};
      (camerasData?.cameras || []).forEach((camera) => {
        const id = camera.camera_id || camera.id;
        const label = camera.camera_name || camera.name || id;

        if (id && label) {
          map[id] = label;
        }
      });

      return map;
    }

    function cameraNameFromEvent(event, cameraNameMap = {}) {
      const id = cameraIdFromEvent(event);
      const label = event?.camera_name
        || event?.name
        || event?.camera?.camera_name
        || event?.camera?.name
        || cameraNameMap[id]
        || id;

      return label && label !== "unknown_camera" ? label : "Unknown camera";
    }

    function preferredLatestEvent(summary, eventsData) {
      const events = eventsData?.events || [];
      return events.find((event) => event?.person_detected)
        || summary?.events?.latest_event
        || events[0]
        || null;
    }

    function updateMonitoringLine(camerasData, healthData) {
      const totals = camerasData?.totals || {};
      const scheduler = healthData?.scheduler || {};
      const summary = String(scheduler.latest_summary || "").toLowerCase();
      const schedulerLooksOk = summary.includes("status=ok") || summary.includes("ok");
      const enabledCount = text(totals.enabled, "0");
      const scanLabel = schedulerLooksOk ? "AI scan active" : "AI scan status pending";
      el("monitoringLine").textContent = `${scanLabel} | Monitoring ${enabledCount} enabled cameras`;
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

    function addField(container, label, value) {
      const field = document.createElement("div");
      field.className = "field";

      const fieldLabel = document.createElement("div");
      fieldLabel.className = "field-label";
      fieldLabel.textContent = label;

      const fieldValue = document.createElement("div");
      fieldValue.className = "field-value";
      fieldValue.textContent = text(value);

      field.append(fieldLabel, fieldValue);
      container.appendChild(field);
    }

    function renderLatestSummary(summary, eventsData, cameraNameMap) {
      const latest = preferredLatestEvent(summary, eventsData);
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
      badge.textContent = eventLabel(latest);

      const title = document.createElement("div");
      title.className = "latest-event-title";
      title.textContent = latest.person_detected ? "Person Detected" : "No Person Detected";

      const fields = document.createElement("div");
      fields.className = "field-grid";
      addField(fields, "Camera", cameraNameFromEvent(latest, cameraNameMap));
      addField(fields, "Time", formatTime(latest.timestamp));
      addField(fields, "Status", text(latest.event_type));
      addField(fields, "Severity", text(latest.severity));
      addField(fields, "Confidence", formatConfidence(maxConfidence(latest)));
      addField(fields, "Evidence", latest.evidence_path ? "Saved" : "None");

      const message = document.createElement("div");
      message.className = "meta";
      message.textContent = text(latest.message, "");

      box.className = latest.person_detected ? "latest-event-card person-alert" : "latest-event-card";
      box.append(title, fields, message);
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

        head.append(title, makeBadge("disabled", "danger"));

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `ID: ${text(camera.camera_id)} | IP: ${text(camera.camera_host)} | Channel: ${text(camera.channel)}`;

        const notes = document.createElement("div");
        notes.className = "meta";
        notes.textContent = text(camera.notes || camera.health_note, "");

        item.append(head, meta, notes);
        list.appendChild(item);
      });
    }

    function renderEvents(eventsData, cameraNameMap) {
      const list = el("latestEvents");
      clearNode(list);
      const events = eventsData?.events || [];
      el("latestEventsCount").textContent = events.length;

      if (!events.length) {
        renderEmpty(list, "No events found.");
        return;
      }

      const orderedEvents = [...events].sort((left, right) => {
        return Number(Boolean(right?.person_detected)) - Number(Boolean(left?.person_detected));
      });

      orderedEvents.forEach((event) => {
        const item = document.createElement("div");
        item.className = `timeline-item ${event?.person_detected ? "person" : ""}`;

        const dot = document.createElement("span");
        dot.className = "timeline-dot";
        dot.setAttribute("aria-hidden", "true");

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
        meta.textContent = `Camera: ${cameraNameFromEvent(event, cameraNameMap)} | Time: ${formatTime(event.timestamp)} | Confidence: ${formatConfidence(maxConfidence(event))}`;

        const message = document.createElement("div");
        message.className = "meta";
        message.textContent = text(event.message, "");

        details.append(head, meta, message);
        item.append(dot, details);

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
      const scheduler = healthData?.scheduler || {};
      const counts = {
        active: 0,
        stale: 0,
        no_recent_event: 0,
        offline: 0,
        disabled: 0
      };
      const badge = el("healthBadge");

      (healthData?.per_camera || []).forEach((camera) => {
        const status = camera.health_status || "unknown";

        if (Object.prototype.hasOwnProperty.call(counts, status)) {
          counts[status] += 1;
        }
      });

      const reviewCount = counts.stale + counts.no_recent_event;
      const unavailableCount = counts.offline + counts.disabled;
      el("healthCameraTotals").textContent = `${text(cameras.total)} total / ${text(cameras.enabled)} enabled / ${text(cameras.disabled)} disabled`;
      el("healthLatestEventTime").textContent = formatTime(events.latest_event_time);
      el("schedulerLatestRunTime").textContent = text(scheduler.latest_run_time);
      el("schedulerLatestSummary").textContent = text(scheduler.latest_summary);
      el("healthActiveCount").textContent = counts.active;
      el("healthStaleReviewCount").textContent = reviewCount;
      el("healthOfflineDisabledCount").textContent = unavailableCount;

      if (counts.offline > 0) {
        badge.className = "badge danger";
        badge.textContent = `${counts.offline} offline`;
        el("systemStatus").textContent = "Needs review";
      } else if (reviewCount > 0) {
        badge.className = "badge warn";
        badge.textContent = `${reviewCount} need review`;
        el("systemStatus").textContent = "Review";
      } else if (counts.disabled > 0) {
        badge.className = "badge muted";
        badge.textContent = `${counts.disabled} disabled`;
        el("systemStatus").textContent = "Operational";
      } else {
        badge.className = "badge ok";
        badge.textContent = "Operational";
        el("systemStatus").textContent = "Operational";
      }
    }

    function renderEvidence(evidenceData) {
      const list = el("evidenceList");
      clearNode(list);
      const evidence = evidenceData?.evidence || [];

      if (!evidence.length) {
        renderEmpty(list, "No evidence images found.");
        return;
      }

      evidence.forEach((image) => {
        const item = document.createElement("div");
        item.className = "evidence-card person-evidence";

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

        const head = document.createElement("div");
        head.className = "item-head";

        const title = document.createElement("div");
        title.className = "item-title filename-compact";
        title.textContent = text(image.filename);
        title.title = text(image.filename);
        head.append(title, makeBadge("evidence", "neutral"));

        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = `Timestamp: ${formatTime(image.modified_time)} | Size: ${text(image.size_bytes)} bytes`;

        const status = document.createElement("div");
        status.className = "meta";
        status.textContent = "Detection status: person evidence image";

        item.append(head, meta, status);
        list.appendChild(item);
      });
    }

    async function refreshEvidence() {
      const note = el("evidenceFolderNote");
      note.textContent = "Refreshing evidence...";

      try {
        renderEvidence(await getJson(endpoints.evidence));
        note.textContent = `Evidence folder: ${evidenceFolderPath}`;
      } catch (error) {
        note.textContent = `Evidence refresh failed: ${error.message}`;
      }
    }

    async function copyEvidenceFolderPath() {
      const note = el("evidenceFolderNote");

      try {
        await navigator.clipboard.writeText(evidenceFolderPath);
        note.textContent = `Copied: ${evidenceFolderPath}`;
      } catch {
        note.textContent = `Copy blocked. Evidence folder: ${evidenceFolderPath}`;
      }
    }

    function setActiveNavButton(button) {
      document.querySelectorAll(".quick-links .quick-link").forEach((navButton) => {
        navButton.classList.toggle("active", navButton === button);
      });
    }

    function scrollToSection(sectionId, button) {
      const section = el(sectionId);

      if (!section) {
        return;
      }

      setActiveNavButton(button);
      section.scrollIntoView({ behavior: "smooth", block: "start" });
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
        const status = text(health.health_status, camera.enabled ? "active" : "disabled");
        const item = document.createElement("div");
        item.className = `camera-card ${status}`;

        const head = document.createElement("div");
        head.className = "item-head";

        const title = document.createElement("div");
        title.className = "item-title";
        title.textContent = text(camera.name || camera.camera_id);

        head.append(title, makeBadge(status, healthTone(status)));

        const idMeta = document.createElement("div");
        idMeta.className = "meta";
        idMeta.textContent = `ID: ${text(camera.camera_id)} | IP: ${text(camera.ip)} | Channel: ${text(camera.channel)}`;

        const enabled = document.createElement("div");
        enabled.className = "meta";
        enabled.textContent = `Mode: ${camera.enabled ? "enabled" : "disabled"} | Last event: ${formatTime(health.last_event_time || stats?.latest_event_time)}`;

        const statsRow = document.createElement("div");
        statsRow.className = "camera-stats";
        statsRow.append(
          makeBadge(camera.enabled ? "enabled" : "disabled", camera.enabled ? "ok" : "muted"),
          makeBadge(`health ${status}`, healthTone(status)),
          makeBadge(`events ${text(stats?.total_events, "0")}`, "neutral"),
          makeBadge(`person ${text(stats?.person_events, "0")}`, stats?.person_events ? "danger" : "muted")
        );

        const freshness = document.createElement("div");
        freshness.className = "meta";
        freshness.textContent = `Stale age: ${text(health.stale_minutes, "n/a")} min (threshold ${text(health.stale_threshold_minutes, "n/a")} min) | Source: ${text(health.last_seen_source, "none")}`;

        const notes = document.createElement("div");
        notes.className = "meta";
        notes.textContent = text(health.health_note || camera.health_note || camera.notes, "");

        if (stats?.latest_evidence_url) {
          const evidenceLink = document.createElement("a");
          evidenceLink.href = stats.latest_evidence_url;
          evidenceLink.target = "_blank";
          evidenceLink.rel = "noopener";
          evidenceLink.textContent = "Latest evidence";
          statsRow.appendChild(evidenceLink);
        }

        item.append(head, idMeta, enabled, statsRow, freshness, notes);
        list.appendChild(item);
      });
    }

    async function loadDashboard() {
      if (isLoading) {
        return;
      }

      isLoading = true;
      const status = el("loadStatus");
      const refreshButton = el("refreshButton");
      status.className = "";
      status.textContent = "Loading dashboard...";
      refreshButton.disabled = true;
      refreshButton.textContent = "Refreshing...";

      try {
        const [summary, cameras, events, evidence, health] = await Promise.all([
          getJson(endpoints.summary),
          getJson(endpoints.cameras),
          getJson(endpoints.latestEvents),
          getJson(endpoints.evidence),
          getJson(endpoints.health)
        ]);

        const cameraNameMap = makeCameraNameMap(cameras);
        renderLatestSummary(summary, events, cameraNameMap);
        renderDisabled(summary);
        renderEvents(events, cameraNameMap);
        renderEvidence(evidence);
        renderHealth(health);
        updateMonitoringLine(cameras, health);
        await renderCameras(cameras, health);

        status.textContent = `Last refresh ${new Date().toLocaleString()}`;
      } catch (error) {
        status.className = "error";
        status.textContent = `Dashboard load failed: ${error.message}`;
      } finally {
        resetRefreshCountdown();
        refreshButton.disabled = false;
        refreshButton.textContent = "Refresh now";
        isLoading = false;
      }
    }

    el("refreshButton").addEventListener("click", loadDashboard);
    document.querySelectorAll("[data-scroll-target]").forEach((button) => {
      button.addEventListener("click", () => {
        scrollToSection(button.dataset.scrollTarget, button);
      });
    });
    el("refreshEvidenceButton").addEventListener("click", refreshEvidence);
    el("copyEvidencePathButton").addEventListener("click", copyEvidenceFolderPath);
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
