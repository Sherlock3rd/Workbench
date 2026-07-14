const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('levelpointsElectron', {
  selectProjectRoot: () => ipcRenderer.invoke('select-project-root'),
  selectMap: () => ipcRenderer.invoke('select-map'),
  chooseMapOnPage: (mapId) => ipcRenderer.invoke('choose-map-on-page', mapId),
  changeRootOnMapPage: () => ipcRenderer.invoke('change-root-on-map-page'),
  selectSourceFile: (kind) => ipcRenderer.invoke('select-source-file', kind),
  reloadSources: () => ipcRenderer.invoke('reload-sources'),
  getCurrentSources: () => ipcRenderer.invoke('get-current-sources'),
  getCurrentConfig: () => ipcRenderer.invoke('get-current-config'),
});
