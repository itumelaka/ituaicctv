@'
const enableNotifyBtn = document.getElementById("enableNotifyBtn");
const testAlertBtn = document.getElementById("testAlertBtn");
const eventsEl = document.getElementById("events");

function addEvent(title, message) {
  const item = document.createElement("div");
  item.className = "event";
  item.innerHTML = `
    <span class="dot"></span>
    <div>
      <strong>${title}</strong>
      <p>${message}</p>
    </div>
  `;
  eventsEl.prepend(item);
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    addEvent("PWA warning", "Service Worker tidak disokong oleh browser ini.");
    return;
  }

  try {
    await navigator.serviceWorker.register("./sw.js");
    addEvent("PWA ready", "Service Worker registered.");
  } catch (error) {
    addEvent("PWA error", error.message);
  }
}

async function requestNotificationPermission() {
  if (!("Notification" in window)) {
    addEvent("Notification error", "Browser ini tidak support Notification API.");
    return;
  }

  const permission = await Notification.requestPermission();

  if (permission === "granted") {
    addEvent("Notification enabled", "Device ini boleh terima notification.");

    new Notification("AI CCTV Detection", {
      body: "Notification enabled untuk pilot dashboard.",
      icon: "./icons/icon-192.png"
    });
  } else {
    addEvent("Notification blocked", "Permission notification tidak diberi.");
  }
}

function sendTestAlert() {
  const title = "Person detected";
  const message = "CCTV F1 detected movement at Block F staircase.";

  addEvent(title, message);

  if ("Notification" in window && Notification.permission === "granted") {
    new Notification("AI CCTV Alert", {
      body: message,
      icon: "./icons/icon-192.png",
      tag: "ai-cctv-test-alert"
    });
  }
}

enableNotifyBtn.addEventListener("click", requestNotificationPermission);
testAlertBtn.addEventListener("click", sendTestAlert);

registerServiceWorker();
'@ | Set-Content public\app.js
