(function () {
  const container = document.getElementById("classifier-training-status");
  if (!container) {
    return;
  }

  const statusUrl = container.dataset.statusUrl;
  const terminalStatuses = (container.dataset.terminalStatuses || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  async function refreshStatus() {
    const currentStatus = container
      .querySelector(".classifier-status")
      ?.className
      .split(" ")
      .find((className) => className.startsWith("classifier-status--"))
      ?.replace("classifier-status--", "");

    if (terminalStatuses.includes(currentStatus)) {
      return;
    }

    try {
      const response = await fetch(statusUrl, {
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!response.ok) {
        return;
      }
      container.innerHTML = await response.text();
    } catch (error) {
      return;
    }

    window.setTimeout(refreshStatus, 5000);
  }

  window.setTimeout(refreshStatus, 5000);
})();
