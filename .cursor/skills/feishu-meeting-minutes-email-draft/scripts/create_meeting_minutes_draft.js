const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

function fail(message) {
  console.error(message);
  process.exit(1);
}

const payloadPath = process.argv[2];
if (!payloadPath) fail("Usage: node create_meeting_minutes_draft.js <payload.json>");

const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
const required = ["subject", "to", "html"];
for (const key of required) {
  if (!payload[key] || (Array.isArray(payload[key]) && payload[key].length === 0)) {
    fail(`Missing required payload field: ${key}`);
  }
}

const appData = process.env.APPDATA || path.join(process.env.USERPROFILE, "AppData", "Roaming");
const larkCliEntry = path.join(appData, "npm", "node_modules", "@larksuite", "cli", "scripts", "run.js");
let tempIndex = 0;

function tempJson(value) {
  const relativePath = `.lark_meeting_mail_${process.pid}_${tempIndex++}.json`;
  fs.writeFileSync(relativePath, JSON.stringify(value), "utf8");
  return relativePath;
}

function runLark(args, options = {}) {
  const fullArgs = [...args];
  if (options.params) fullArgs.push("--params", `@${tempJson(options.params)}`);
  if (options.data) fullArgs.push("--data", `@${tempJson(options.data)}`);
  const result = spawnSync(process.execPath, [larkCliEntry, ...fullArgs], {
    encoding: "utf8",
    windowsHide: true,
  });
  if (result.status !== 0) {
    fail((result.stderr || result.stdout || `lark-cli failed: ${fullArgs.join(" ")}`).trim());
  }
  return result.stdout ? JSON.parse(result.stdout) : {};
}

function encodeHeader(value) {
  return `=?UTF-8?B?${Buffer.from(value, "utf8").toString("base64")}?=`;
}

function wrapBase64(value) {
  return value.match(/.{1,76}/g).join("\r\n");
}

function base64Url(value) {
  return Buffer.from(value, "utf8")
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function addressList(value) {
  return Array.isArray(value) ? value.join(", ") : String(value);
}

function buildRawEml() {
  const from = payload.from || (payload.mailbox && payload.mailbox !== "me" ? payload.mailbox : "sunqihao@legoutech.com");
  const headers = [
    `From: ${from}`,
    `To: ${addressList(payload.to)}`,
    `Subject: ${encodeHeader(payload.subject)}`,
    "MIME-Version: 1.0",
    "Content-Type: text/html; charset=UTF-8",
    "Content-Transfer-Encoding: base64",
  ];
  if (payload.cc && payload.cc.length) headers.splice(2, 0, `Cc: ${addressList(payload.cc)}`);
  else headers.splice(2, 0, "Cc:");
  const body = wrapBase64(Buffer.from(payload.html, "utf8").toString("base64"));
  return `${headers.join("\r\n")}\r\n\r\n${body}`;
}

function createDraft() {
  const create = runLark([
    "mail",
    "+send",
    "--to",
    addressList(payload.to),
    "--subject",
    payload.subject,
    "--body",
    payload.html,
  ]);
  const draftId = create.data && create.data.draft_id;
  if (!draftId) fail(`Draft create response did not include draft_id: ${JSON.stringify(create)}`);

  const raw = base64Url(buildRawEml());
  const update = runLark(["mail", "user_mailbox.drafts", "update"], {
    params: {
      user_mailbox_id: payload.mailbox || "me",
      draft_id: draftId,
    },
    data: { raw },
  });
  console.log(JSON.stringify({
    ok: true,
    draft_id: draftId,
    reference: (update.data && update.data.reference) || (create.data && create.data.reference) || "",
    subject: payload.subject,
    to: payload.to,
    cc: payload.cc || [],
  }, null, 2));
}

try {
  createDraft();
} finally {
  for (const file of fs.readdirSync(process.cwd())) {
    if (file.startsWith(".lark_meeting_mail_") && file.endsWith(".json")) {
      try {
        fs.unlinkSync(file);
      } catch {}
    }
  }
}
