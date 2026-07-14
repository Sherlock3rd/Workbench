const { app, BrowserWindow, dialog, ipcMain, Menu } = require('electron');
const { spawn } = require('child_process');
const fs = require('fs/promises');
const fsSync = require('fs');
const os = require('os');
const path = require('path');

const APP_TITLE = 'Beagle_MapLP';
const WINDOW_TITLE_PREFIX = 'Beagle地图点位工具';
app.setName(APP_TITLE);

const SHARED_RELATIVE_PATHS = {
  areaConfig: path.join('data', 'GameDatas', 'datas', 'area_config.xlsx'),
  interactiveObjXlsx: path.join('data', 'GameDatas', 'datas', 'InteractiveObj.xlsx'),
};

const DEFAULT_MAP_ID = 'birthProvince7Day';
const MAP_CONFIGS = {
  birthProvince7Day: {
    id: 'birthProvince7Day',
    label: '出生省7日地图',
    navmesh: path.join('data', 'GameDatas', 'map_navMesh', '40X30_7day_MainLand_navmesh.json'),
    levelpoints: path.join('UnityPrj', 'Assets', 'LevelEditorV2', 'Data', 'Level_9', 'LevelPoints.json'),
  },
  branchIsland: {
    id: 'branchIsland',
    label: '分线岛',
    navmesh: path.join('data', 'GameDatas', 'map_navMesh', '42X42_MainLand_navmesh.json'),
    levelpoints: path.join('UnityPrj', 'Assets', 'LevelEditorV2', 'Data', 'Level_7', 'LevelPoints.json'),
  },
};
const ERROR_CODES = {
  ROOT_MISSING_FILES: 'LPV-E001',
  HELPER_MISSING: 'LPV-E002',
  VIEWER_SCRIPT_MISSING: 'LPV-E003',
  HELPER_FAILED: 'LPV-E004',
  HTML_NOT_GENERATED: 'LPV-E005',
  RENDER_DIAGNOSTICS_FAILED: 'LPV-E006',
  RENDER_JS_ERROR: 'LPV-E007',
  EMPTY_NAVMESH: 'LPV-E008',
  EMPTY_LEVELPOINTS: 'LPV-E009',
  IPC_RELOAD_FAILED: 'LPV-E010',
  UNKNOWN: 'LPV-E999',
};

let mainWindow = null;
let currentSources = {
  root: null,
  mapId: DEFAULT_MAP_ID,
  mapName: MAP_CONFIGS[DEFAULT_MAP_ID].label,
  navmesh: null,
  levelpoints: null,
  areaConfig: null,
  interactiveObjXlsx: null,
};
let pendingMapSelection = null;
let currentWindowTitle = `${WINDOW_TITLE_PREFIX}——选择地图`;
let workspaceRoot = null;
let scriptsDir = null;
let tempDir = null;
let logPath = null;
let configPath = null;
let logPaths = [path.join(os.tmpdir(), 'levelpoints-viewer.log')];

function isPackaged() {
  return app.isPackaged;
}

function resolveWorkspaceRoot() {
  if (isPackaged()) {
    return path.dirname(process.execPath);
  }
  return path.resolve(__dirname, '..', '..', '..');
}

function resolveScriptsDir() {
  if (isPackaged()) {
    return path.join(process.resourcesPath, 'viewer-scripts');
  }
  return path.join(workspaceRoot, '.cursor', 'skills', 'levelpoints-navmesh-viewer', 'scripts');
}

function resolveHelperScript() {
  if (isPackaged()) {
    return path.join(process.resourcesPath, 'helper', 'build_levelpoints_payload.exe');
  }
  return path.join(workspaceRoot, 'tools', 'levelpoints-electron-viewer', 'helper', 'build_levelpoints_payload.py');
}

function mapConfig(mapId) {
  return MAP_CONFIGS[mapId] || MAP_CONFIGS[DEFAULT_MAP_ID];
}

function sourcePath(root, relativePath) {
  return path.join(root, relativePath);
}

function assetPath(fileName) {
  return path.join(__dirname, '..', 'assets', fileName);
}

function setWindowTitle(suffix) {
  currentWindowTitle = `${WINDOW_TITLE_PREFIX}——${suffix}`;
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.setTitle(currentWindowTitle);
  }
}

async function imageDataUri(fileName) {
  const imagePath = assetPath(fileName);
  const data = await fs.readFile(imagePath);
  const ext = path.extname(fileName).toLowerCase();
  const mime = ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg' : 'image/png';
  return `data:${mime};base64,${data.toString('base64')}`;
}

function fileExists(filePath) {
  return fs.access(filePath).then(() => true).catch(() => false);
}

function codedError(code, message, cause = null) {
  const detail = cause ? `${message}\n${cause.stack || cause.message || cause}` : message;
  const error = new Error(`[${code}] ${detail}`);
  error.code = code;
  error.cause = cause;
  return error;
}

function errorCode(error) {
  return error && error.code ? error.code : ERROR_CODES.UNKNOWN;
}

function errorDetail(error) {
  return error && (error.stack || error.message) ? (error.stack || error.message) : String(error);
}

async function initPaths() {
  workspaceRoot = resolveWorkspaceRoot();
  scriptsDir = resolveScriptsDir();
  tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'levelpoints-viewer-'));
  configPath = path.join(app.getPath('userData'), 'config.json');
  logPaths = Array.from(new Set([
    path.join(app.getPath('userData'), 'beagle-maplp.log'),
    path.join(path.dirname(app.getPath('exe')), 'beagle-maplp.log'),
    path.join(path.dirname(process.execPath), 'beagle-maplp.log'),
    path.join(process.cwd(), 'beagle-maplp.log'),
    path.join(os.tmpdir(), 'beagle-maplp.log'),
  ]));
  logPath = logPaths[0];
  await appendLog(`LOG_PATHS ${logPaths.join(' | ')}`);
  await appendLog(`APP title=${APP_TITLE} packaged=${isPackaged()} exe=${app.getPath('exe')} cwd=${process.cwd()} resources=${process.resourcesPath || ''} config=${configPath}`);
}

async function readAppConfig() {
  try {
    const text = await fs.readFile(configPath, 'utf8');
    const parsed = JSON.parse(text);
    return {
      root: typeof parsed.root === 'string' ? parsed.root : null,
      mapId: MAP_CONFIGS[parsed.mapId] ? parsed.mapId : null,
    };
  } catch (_error) {
    return { root: null, mapId: null };
  }
}

async function writeAppConfig(nextConfig) {
  const safeConfig = {
    root: nextConfig.root || null,
    mapId: MAP_CONFIGS[nextConfig.mapId] ? nextConfig.mapId : DEFAULT_MAP_ID,
  };
  await fs.mkdir(path.dirname(configPath), { recursive: true });
  await fs.writeFile(configPath, JSON.stringify(safeConfig, null, 2), 'utf8');
  await appendLog(`CONFIG_SAVED ${JSON.stringify(safeConfig)}`);
  return safeConfig;
}

async function appendLog(message) {
  const line = `[${new Date().toISOString()}] ${message}\n`;
  for (const target of logPaths) {
    try {
      fsSync.mkdirSync(path.dirname(target), { recursive: true });
      fsSync.appendFileSync(target, line, 'utf8');
    } catch (_error) {
      // Logging must never block the viewer.
    }
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[ch]));
}

async function showStatusPage(title, message, detail = '') {
  const codeMatch = String(detail || message || title).match(/LPV-E\d{3}|LPV-E999/);
  const codeBlock = codeMatch ? `<p class="code">错误码：${escapeHtml(codeMatch[0])}</p>` : '';
  const spinnerBlock = codeMatch ? '' : '<div class="spinner"></div>';
  const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>${escapeHtml(title)}</title>
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#eef3f8;color:#1f2937;font-family:"Segoe UI","Microsoft YaHei",Arial,sans-serif}
.card{width:min(720px,86vw);background:#fff;border:1px solid #d8e2ee;border-radius:14px;box-shadow:0 12px 40px rgba(15,23,42,.12);padding:28px}
h1{font-size:22px;margin:0 0 12px}
p{line-height:1.7;margin:8px 0;color:#475569}
pre{white-space:pre-wrap;word-break:break-word;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;max-height:320px;overflow:auto}
.code{display:inline-block;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;border-radius:999px;padding:5px 10px;font-weight:700}
.spinner{width:28px;height:28px;border:3px solid #bfdbfe;border-top-color:#2563eb;border-radius:50%;animation:spin .8s linear infinite;margin-bottom:14px}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body><div class="card">${spinnerBlock}<h1>${escapeHtml(title)}</h1>${codeBlock}<p>${escapeHtml(message)}</p>${detail ? `<pre>${escapeHtml(detail)}</pre>` : ''}</div></body>
</html>`;
  await mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 940,
    minWidth: 1100,
    minHeight: 720,
    title: currentWindowTitle,
    icon: assetPath('appicon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  mainWindow.maximize();

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  mainWindow.webContents.on('console-message', (_event, level, message, line, sourceId) => {
    appendLog(`RENDER_CONSOLE level=${level} ${message} @ ${sourceId}:${line}`);
  });

  mainWindow.webContents.on('did-fail-load', (_event, errorCode, errorDescription, validatedURL) => {
    appendLog(`DID_FAIL_LOAD ${errorCode} ${errorDescription} ${validatedURL}`);
  });

  mainWindow.webContents.on('page-title-updated', (event) => {
    event.preventDefault();
    mainWindow.setTitle(currentWindowTitle);
  });
}

function createMenu() {
  const template = [
    {
      label: '文件',
      submenu: [
        { label: '设置根目录...', click: () => safeRun('设置根目录', () => selectProjectRootAndReload()) },
        { label: '切换地图...', click: () => safeRun('切换地图', () => selectMapAndReload()) },
        { type: 'separator' },
        { label: '刷新重新加载', click: () => safeRun('刷新重新加载', () => loadViewer()) },
        { type: 'separator' },
        { role: 'quit', label: '退出' },
      ],
    },
    {
      label: '视图',
      submenu: [
        { role: 'reload', label: '重新载入窗口' },
        { role: 'toggleDevTools', label: '开发者工具' },
        { type: 'separator' },
        { role: 'resetZoom', label: '重置缩放' },
        { role: 'zoomIn', label: '放大' },
        { role: 'zoomOut', label: '缩小' },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

async function safeRun(title, action) {
  try {
    await action();
  } catch (error) {
    await handleFatalError(title, error, false);
  }
}

async function chooseProjectRoot() {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: '选择 Beagle / 工程根目录',
    properties: ['openDirectory'],
  });
  if (result.canceled || !result.filePaths.length) {
    return null;
  }
  return result.filePaths[0];
}

async function chooseMapId(defaultMapId = currentSources.mapId) {
  return showMapSelectionPage(defaultMapId);
}

async function showMapSelectionPage(defaultMapId = currentSources.mapId) {
  setWindowTitle('选择地图');
  const backgroundImage = await imageDataUri('map-select-background.png');
  const maps = Object.values(MAP_CONFIGS).map((item) => ({
    id: item.id,
    label: item.label,
    navmesh: item.navmesh,
    levelpoints: item.levelpoints,
  }));
  const initialMapId = MAP_CONFIGS[defaultMapId] ? defaultMapId : DEFAULT_MAP_ID;
  const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>${escapeHtml(currentWindowTitle)}</title>
<style>
:root{--bg:#07111f;--panel:rgba(15,23,42,.82);--panel2:rgba(30,41,59,.72);--text:#e5eefb;--muted:#9fb0c7;--line:rgba(148,163,184,.24);--blue:#38bdf8;--blue2:#2563eb;--green:#34d399}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;overflow:hidden;background:#111827;color:var(--text);font-family:"Segoe UI","Microsoft YaHei",Arial,sans-serif}
.bg-art{position:fixed;inset:0;width:100vw;height:100vh;object-fit:cover;object-position:center bottom;filter:saturate(1.08) contrast(1.03);transform:translateZ(0);z-index:0}
.bg-shade{position:fixed;inset:0;background:linear-gradient(90deg,rgba(7,17,31,.74),rgba(7,17,31,.46) 48%,rgba(7,17,31,.28)),linear-gradient(0deg,rgba(7,17,31,.62),rgba(7,17,31,.08));z-index:1}
.shell{position:relative;z-index:2;min-height:100vh;display:grid;place-items:center;padding:48px}
.panel{width:min(1180px,92vw);border:1px solid var(--line);border-radius:28px;background:linear-gradient(180deg,var(--panel),rgba(15,23,42,.68));box-shadow:0 28px 90px rgba(0,0,0,.38);backdrop-filter:blur(20px);padding:38px}
.eyebrow{letter-spacing:.18em;text-transform:uppercase;color:var(--blue);font-size:12px;font-weight:800;margin-bottom:14px}
.head{display:block;margin-bottom:22px}
h1{font-size:42px;line-height:1.08;margin:0 0 12px;font-weight:800}
.sub{margin:0;color:var(--muted);font-size:15px;line-height:1.7}
.root{display:flex;align-items:center;gap:14px;margin:22px 0 0;border:1px solid rgba(148,163,184,.22);border-radius:16px;background:rgba(15,23,42,.50);padding:12px 14px;color:var(--muted);font-size:13px;line-height:1.5;word-break:break-all}
.root strong{flex:0 0 auto;color:#dbeafe}
.root-path{min-width:0;flex:1;color:#b6c6dc}
.root-change{flex:0 0 auto;border:1px solid rgba(125,211,252,.38);border-radius:999px;background:rgba(14,165,233,.14);color:#bae6fd;padding:8px 13px;font-size:12px;font-weight:800;cursor:pointer}.root-change:hover{background:rgba(14,165,233,.24)}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.card{position:relative;display:flex;min-height:246px;text-align:left;border:1px solid var(--line);border-radius:22px;background:linear-gradient(145deg,rgba(30,41,59,.84),rgba(15,23,42,.72));color:var(--text);padding:24px;cursor:pointer;overflow:hidden;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease,background .18s ease}
.card:hover{transform:translateY(-4px);border-color:rgba(56,189,248,.75);box-shadow:0 20px 54px rgba(14,165,233,.20);background:linear-gradient(145deg,rgba(30,64,175,.42),rgba(15,23,42,.78))}
.card.selected{border-color:rgba(52,211,153,.88);box-shadow:0 0 0 1px rgba(52,211,153,.28),0 20px 58px rgba(16,185,129,.16)}
.card:before{content:"";position:absolute;inset:auto -54px -72px auto;width:190px;height:190px;border-radius:999px;background:rgba(56,189,248,.13)}
.card:nth-child(2):before{background:rgba(52,211,153,.14)}
.content{position:relative;display:flex;flex-direction:column;width:100%;z-index:1}
h2{font-size:28px;margin:0 0 12px}
.desc{color:var(--muted);line-height:1.65;font-size:14px;margin:0 0 22px}
.paths{margin-top:auto;border-top:1px solid var(--line);padding-top:16px;color:#a8bbd4;font-size:12px;line-height:1.75}
.paths div{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cta{display:flex;align-items:center;justify-content:space-between;margin-top:28px;color:var(--muted);font-size:13px}
.hint{display:flex;gap:8px;align-items:center}
.dot{width:8px;height:8px;border-radius:999px;background:var(--green);box-shadow:0 0 18px rgba(52,211,153,.9)}
.confirm{border:0;border-radius:999px;background:linear-gradient(135deg,#38bdf8,#2563eb);color:#fff;padding:13px 24px;font-size:15px;font-weight:800;cursor:pointer;box-shadow:0 18px 38px rgba(37,99,235,.28);transition:transform .16s ease,box-shadow .16s ease}
.confirm:hover{transform:translateY(-2px);box-shadow:0 22px 48px rgba(56,189,248,.32)}
@media(max-width:860px){.root{display:block}.root-change{margin-top:10px}.cards{grid-template-columns:1fr}.shell{padding:24px}.panel{padding:26px}h1{font-size:32px}}
</style>
</head>
<body>
<img class="bg-art" src="${backgroundImage}" alt="">
<div class="bg-shade"></div>
<main class="shell">
  <section class="panel">
    <div class="head">
      <div class="eyebrow">Beagle MapLP</div>
      <h1>选择要加载的地图</h1>
      <p class="sub">每次进入应用都会先确认地图。选择后会读取对应的 NavMesh 与 LevelPoints 并生成预览。</p>
      <div class="root"><strong>当前工作目录</strong><span id="root-value" class="root-path">${escapeHtml(currentSources.root || '尚未设置')}</span><button id="change-root" class="root-change" type="button">更改根目录</button></div>
    </div>
    <div class="cards" id="cards"></div>
    <div class="cta">
      <div class="hint"><span class="dot"></span>先选择地图，再点击确认加载</div>
      <button class="confirm" id="confirm" type="button">确认加载</button>
    </div>
  </section>
</main>
<script>
const maps=${JSON.stringify(maps)};
let selected=${JSON.stringify(initialMapId)};
const cards=document.getElementById('cards');
const confirm=document.getElementById('confirm');
const rootValue=document.getElementById('root-value');
const changeRoot=document.getElementById('change-root');
function pathText(value){return String(value).replace(/\\\\/g,'/')}
function updateCards(){
  for(const card of cards.querySelectorAll('.card')){
    const active=card.dataset.mapId===selected;
    card.classList.toggle('selected',active);
  }
}
for(const map of maps){
  const button=document.createElement('button');
  button.className='card'+(map.id===selected?' selected':'');
  button.dataset.mapId=map.id;
  button.type='button';
  button.innerHTML='<div class="content">'
    + '<h2>'+map.label+'</h2>'
    + '<p class="desc">加载此地图对应的导航网格和 Unity LevelEditor 点位数据。</p>'
    + '<div class="paths"><div>NavMesh：'+pathText(map.navmesh)+'</div><div>LevelPoints：'+pathText(map.levelpoints)+'</div></div>'
    + '</div>';
  button.addEventListener('click',()=>{
    selected=map.id;
    updateCards();
  });
  cards.appendChild(button);
}
confirm.addEventListener('click',async()=>{
  confirm.textContent='正在加载...';
  confirm.disabled=true;
  await window.levelpointsElectron.chooseMapOnPage(selected);
});
changeRoot.addEventListener('click',async()=>{
  changeRoot.textContent='选择中...';
  changeRoot.disabled=true;
  try{
    const result=await window.levelpointsElectron.changeRootOnMapPage();
    if(result&&result.ok){
      rootValue.textContent=result.root||'尚未设置';
    }else if(result&&result.error){
      rootValue.textContent=result.error;
    }
  }finally{
    changeRoot.textContent='更改根目录';
    changeRoot.disabled=false;
  }
});
</script>
</body>
</html>`;

  await mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
  return new Promise((resolve) => {
    pendingMapSelection = resolve;
  });
}

async function applySources(root, mapId) {
  const selectedMap = mapConfig(mapId);
  currentSources.root = root;
  currentSources.mapId = selectedMap.id;
  currentSources.mapName = selectedMap.label;
  currentSources.navmesh = sourcePath(root, selectedMap.navmesh);
  currentSources.levelpoints = sourcePath(root, selectedMap.levelpoints);
  currentSources.areaConfig = sourcePath(root, SHARED_RELATIVE_PATHS.areaConfig);
  currentSources.interactiveObjXlsx = sourcePath(root, SHARED_RELATIVE_PATHS.interactiveObjXlsx);
}

async function validateRootDirectory(root) {
  if (!root || !(await fileExists(root))) {
    throw codedError(ERROR_CODES.ROOT_MISSING_FILES, `路径获取失败：工作目录不存在或未设置。\n当前路径：${root || '(empty)'}`);
  }
}

async function validateSources(root, mapId) {
  await validateRootDirectory(root);
  const selectedMap = mapConfig(mapId);
  const required = [
    [`${selectedMap.label} NavMesh`, sourcePath(root, selectedMap.navmesh)],
    [`${selectedMap.label} LevelPoints`, sourcePath(root, selectedMap.levelpoints)],
    ['area_config', sourcePath(root, SHARED_RELATIVE_PATHS.areaConfig)],
    ['InteractiveObj', sourcePath(root, SHARED_RELATIVE_PATHS.interactiveObjXlsx)],
  ];
  const missing = [];
  for (const [label, filePath] of required) {
    if (!(await fileExists(filePath))) {
      missing.push(`${label}: ${path.relative(root, filePath)}`);
    }
  }
  if (missing.length) {
    throw codedError(
      ERROR_CODES.ROOT_MISSING_FILES,
      `路径获取失败：${selectedMap.label} 缺少必要文件。\n工作目录：${root}\n地图配置：${selectedMap.label}\n\n缺失文件：\n${missing.join('\n')}\n\n请重新设置目录或切换地图。`,
    );
  }
}

async function applyProjectRoot(root, mapId = currentSources.mapId) {
  await applySources(root, mapId);
}

async function ensureInitialSources() {
  const savedConfig = await readAppConfig();
  let root = rootFromArgs() || savedConfig.root;
  let mapId = savedConfig.mapId || DEFAULT_MAP_ID;

  while (true) {
    if (!root) {
      await showStatusPage('首次设置工作目录', '请选择 Beagle / 工程根目录。此路径会被保存，之后启动将自动使用。');
      root = await chooseProjectRoot();
      if (!root) {
        app.quit();
        return false;
      }
    }

    try {
      await validateRootDirectory(root);
      currentSources.root = root;
      currentSources.mapId = mapId;
      currentSources.mapName = mapConfig(mapId).label;
    } catch (error) {
      await showStatusPage('路径获取失败', '保存的工作目录不可用，请重新设置目录。', errorDetail(error));
      root = await chooseProjectRoot();
      if (!root) {
        app.quit();
        return false;
      }
      continue;
    }

    const selected = await chooseMapId(mapId);
    root = selected.root || currentSources.root || root;
    mapId = selected.mapId;

    try {
      await validateSources(root, mapId);
      await applyProjectRoot(root, mapId);
      await writeAppConfig({ root, mapId });
      return true;
    } catch (error) {
      await showStatusPage('路径获取失败', '当前工作目录或地图配置不可用，请重新设置目录后再选择地图。', errorDetail(error));
      const selected = await chooseProjectRoot();
      if (!selected) {
        app.quit();
        return false;
      }
      root = selected;
    }
  }
}

function rootFromArgs() {
  const args = process.argv.slice(1);
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '--root' && args[i + 1]) {
      return path.resolve(args[i + 1]);
    }
    if (args[i].startsWith('--root=')) {
      return path.resolve(args[i].slice('--root='.length));
    }
  }
  return null;
}

function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    appendLog(`RUN ${command} ${args.join(' ')}`);
    const child = spawn(command, args, {
      cwd: options.cwd || workspaceRoot,
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });
    child.on('error', (error) => {
      reject(codedError(ERROR_CODES.HELPER_FAILED, `无法启动地图生成 helper：${command}`, error));
    });
    child.on('close', (code) => {
      if (stdout.trim()) {
        appendLog(`STDOUT ${stdout.trim()}`);
      }
      if (stderr.trim()) {
        appendLog(`STDERR ${stderr.trim()}`);
      }
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        reject(codedError(
          ERROR_CODES.HELPER_FAILED,
          `地图生成 helper 执行失败，退出码 ${code}。\n命令：${command} ${args.join(' ')}\n${stderr || stdout}`,
        ));
      }
    });
  });
}

async function runPython(script, args) {
  if (isPackaged() && path.extname(script).toLowerCase() === '.exe') {
    return runCommand(script, args);
  }

  const pyArgs = ['-3', script, ...args];
  try {
    return await runCommand('py', pyArgs);
  } catch (error) {
    return runCommand('python', [script, ...args]);
  }
}

async function generateHtml() {
  const htmlPath = path.join(tempDir, 'levelpoints_navmesh.html');
  const analysisPath = path.join(tempDir, 'levelpoints_navmesh_analysis.json');
  const issuesPath = path.join(tempDir, 'levelpoints_navmesh_issues.csv');
  const script = resolveHelperScript();
  const labels = path.join(scriptsDir, 'default_point_labels.json');

  if (!(await fileExists(script))) {
    throw codedError(ERROR_CODES.HELPER_MISSING, `找不到地图生成 helper：${script}`);
  }
  for (const requiredScript of ['visualize_levelpoints_navmesh.py', 'analyze_levelpoints_against_navmesh.py', 'default_point_labels.json']) {
    const requiredPath = path.join(scriptsDir, requiredScript);
    if (!(await fileExists(requiredPath))) {
      throw codedError(ERROR_CODES.VIEWER_SCRIPT_MISSING, `找不到 Viewer 资源文件：${requiredPath}`);
    }
  }

  await runPython(script, [
    '--scripts-dir',
    scriptsDir,
    '--navmesh',
    currentSources.navmesh,
    '--levelpoints',
    currentSources.levelpoints,
    '--labels',
    labels,
    '--interactive-obj-xlsx',
    currentSources.interactiveObjXlsx,
    '--area-config',
    currentSources.areaConfig,
    '--analysis',
    analysisPath,
    '--issues-csv',
    issuesPath,
    '--output',
    htmlPath,
  ]);

  if (!(await fileExists(htmlPath))) {
    throw codedError(ERROR_CODES.HTML_NOT_GENERATED, `helper 未生成 HTML：${htmlPath}`);
  }

  return htmlPath;
}

async function loadViewer() {
  let htmlPath = null;
  try {
    setWindowTitle(currentSources.mapName || '地图预览');
    await showStatusPage('正在生成地图预览', `正在读取 ${currentSources.mapName || ''} 的 NavMesh、LevelPoints 和配置表。大地图首次加载可能需要几十秒，请稍等。`);
    await appendLog(`LOAD root=${currentSources.root || ''} mapId=${currentSources.mapId || ''} mapName=${currentSources.mapName || ''}`);
    htmlPath = await generateHtml();
    const htmlStat = await fs.stat(htmlPath);
    await appendLog(`LOAD_HTML path=${htmlPath} size=${htmlStat.size}`);
    await mainWindow.loadFile(htmlPath);
    setWindowTitle(currentSources.mapName || '地图预览');
    try {
      const diagnostics = await mainWindow.webContents.executeJavaScript(
        'window.__viewerDiagnostics ? window.__viewerDiagnostics() : {title: document.title, bodyText: document.body.innerText.slice(0, 500), missingDiagnostics: true}',
      );
      await appendLog(`VIEWER_DIAGNOSTICS ${JSON.stringify(diagnostics)}`);
      if (diagnostics.missingDiagnostics) {
        throw codedError(ERROR_CODES.RENDER_DIAGNOSTICS_FAILED, `页面缺少渲染诊断函数。HTML：${htmlPath}`);
      }
      if (diagnostics.errors && diagnostics.errors.length) {
        throw codedError(ERROR_CODES.RENDER_JS_ERROR, `页面 JavaScript 报错：\n${diagnostics.errors.join('\n')}`);
      }
      if (!diagnostics.polygonCount) {
        throw codedError(ERROR_CODES.EMPTY_NAVMESH, `页面没有加载出 NavMesh polygon。HTML：${htmlPath}\nNavMesh：${currentSources.navmesh}`);
      }
      if (!diagnostics.pointCount) {
        throw codedError(ERROR_CODES.EMPTY_LEVELPOINTS, `页面没有加载出任何 LevelPoints 点位。HTML：${htmlPath}\nLevelPoints：${currentSources.levelpoints}`);
      }
    } catch (diagnosticError) {
      await appendLog(`VIEWER_DIAGNOSTICS_ERROR ${diagnosticError.stack || diagnosticError.message}`);
      throw diagnosticError.code ? diagnosticError : codedError(ERROR_CODES.RENDER_DIAGNOSTICS_FAILED, '无法读取页面渲染诊断。', diagnosticError);
    }
  } catch (error) {
    await handleFatalError('生成地图预览失败', error, true);
  }
}

async function handleFatalError(title, error, showDialog) {
  const code = errorCode(error);
  const detail = `${errorDetail(error)}\n\n日志位置：\n${logPaths.join('\n')}`;
  await appendLog(`ERROR ${title} ${code}: ${errorDetail(error)}`);
  if (mainWindow && !mainWindow.isDestroyed()) {
    await showStatusPage(`${title} (${code})`, `错误码：${code}。请按错误详情检查根目录、文件路径或生成日志。`, detail);
  }
  if (showDialog && mainWindow && !mainWindow.isDestroyed()) {
    await dialog.showMessageBox(mainWindow, {
      type: 'error',
      title: `${title} (${code})`,
      message: `${title} (${code})`,
      detail,
    });
  }
}

async function readJsonSource(filePath) {
  const text = await fs.readFile(filePath, 'utf8');
  return JSON.parse(text.replace(/^\uFEFF/, ''));
}

async function selectProjectRoot() {
  const root = await chooseProjectRoot();
  if (!root) {
    return null;
  }
  currentSources.root = root;
  const selected = await chooseMapId(currentSources.mapId);
  if (!selected) {
    return null;
  }
  const selectedRoot = selected.root || currentSources.root || root;
  const mapId = selected.mapId;
  await validateSources(selectedRoot, mapId);
  await applyProjectRoot(selectedRoot, mapId);
  await writeAppConfig({ root: selectedRoot, mapId });
  return reloadSources();
}

async function selectSourceFile() {
  return selectProjectRoot();
}

async function selectMap() {
  if (!currentSources.root) {
    return selectProjectRoot();
  }
  const selected = await chooseMapId(currentSources.mapId);
  if (!selected) {
    return null;
  }
  const root = selected.root || currentSources.root;
  const mapId = selected.mapId;
  await validateSources(root, mapId);
  await applyProjectRoot(root, mapId);
  await writeAppConfig({ root, mapId });
  return reloadSources();
}

async function selectProjectRootAndReload() {
  const selected = await selectProjectRoot();
  if (selected) {
    await loadViewer();
  }
}

async function selectMapAndReload() {
  const selected = await selectMap();
  if (selected) {
    await loadViewer();
  }
}

async function selectSourceFileAndReload() {
  const selected = await selectProjectRoot();
  if (selected) {
    await loadViewer();
  }
}

async function sourcePayload(kind) {
  const filePath = currentSources[kind];
  const json = await readJsonSource(filePath);
  return {
    kind,
    path: filePath,
    name: filePath,
    json,
  };
}

async function reloadSources() {
  if (!currentSources.navmesh && !currentSources.levelpoints) {
    throw codedError(ERROR_CODES.IPC_RELOAD_FAILED, '尚未选择 NavMesh 或 LevelPoints 文件。');
  }
  const result = {};
  if (currentSources.navmesh) {
    result.navmesh = await sourcePayload('navmesh');
  }
  if (currentSources.levelpoints) {
    result.levelpoints = await sourcePayload('levelpoints');
  }
  result.root = currentSources.root;
  result.mapId = currentSources.mapId;
  result.mapName = currentSources.mapName;
  return result;
}

ipcMain.handle('select-source-file', async (_event, kind) => selectSourceFile(kind));
ipcMain.handle('select-project-root', async () => selectProjectRoot());
ipcMain.handle('select-map', async () => selectMap());
ipcMain.handle('change-root-on-map-page', async () => {
  const root = await chooseProjectRoot();
  if (!root) {
    return { ok: false };
  }
  try {
    await validateRootDirectory(root);
    currentSources.root = root;
    return { ok: true, root };
  } catch (error) {
    return { ok: false, error: errorDetail(error) };
  }
});
ipcMain.handle('choose-map-on-page', async (_event, mapId) => {
  if (!MAP_CONFIGS[mapId]) {
    return { ok: false, error: `未知地图配置：${mapId}` };
  }
  if (pendingMapSelection) {
    const resolve = pendingMapSelection;
    pendingMapSelection = null;
    resolve({ root: currentSources.root, mapId });
  }
  return { ok: true };
});
ipcMain.handle('reload-sources', async () => reloadSources());
ipcMain.handle('get-current-sources', async () => ({ ...currentSources }));
ipcMain.handle('get-current-config', async () => ({ root: currentSources.root, mapId: currentSources.mapId, mapName: currentSources.mapName }));

process.on('uncaughtException', (error) => {
  appendLog(`UNCAUGHT_EXCEPTION ${error.stack || error.message}`);
});

process.on('unhandledRejection', (reason) => {
  appendLog(`UNHANDLED_REJECTION ${reason && reason.stack ? reason.stack : reason}`);
});

app.whenReady().then(async () => {
  try {
    await initPaths();
    createWindow();
    createMenu();
    const ok = await ensureInitialSources();
    if (ok) {
      await loadViewer();
    }
  } catch (error) {
    await handleFatalError('启动失败', error, true);
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
      safeRun('重新打开窗口', async () => {
        const ok = await ensureInitialSources();
        if (ok) {
          await loadViewer();
        }
      });
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
