/*
Paste this snippet into the DevTools Console while viewing a logged-in
Machinations diagram page. It downloads a machinations-capture.json file
containing the /diagram/open response used by update_machinations_preview.py.

Expected page URL:
  https://my.machinations.io/d/<slug>/<diagram_id>
*/
(async () => {
  const match = location.pathname.match(/\/d\/[^/]+\/([a-f0-9]+)/i);
  if (!match) {
    throw new Error("Cannot find diagram id in current URL. Open a /d/<slug>/<diagram_id> page first.");
  }

  const diagramId = match[1];
  const url = `${location.origin}/diagram/open/${diagramId}`;
  const response = await fetch(url, {
    method: "GET",
    credentials: "include",
    headers: {
      accept: "application/json, text/plain, */*",
    },
  });

  const body = await response.text();
  const looksUseful = response.ok && body.includes("mxGraphModel");
  if (!looksUseful) {
    console.error("Machinations capture failed. Response preview:", body.slice(0, 500));
    throw new Error("Capture failed: diagram XML was not found. Refresh Machinations, make sure you are logged in, then run the snippet again.");
  }

  const capture = [
    {
      url,
      status: response.status,
      contentType: response.headers.get("content-type") || "",
      looksUseful,
      body,
    },
  ];

  const blob = new Blob([JSON.stringify(capture, null, 2)], {
    type: "application/json;charset=utf-8",
  });
  const downloadUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = downloadUrl;
  anchor.download = "machinations-capture.json";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(downloadUrl);

  console.log(`Downloaded machinations-capture.json from ${url}`);
})();
