const { contextBridge, ipcRenderer } = require('electron');

// Expose JARVIS API to renderer process
contextBridge.exposeInMainWorld('jarvis', {
    platform: process.platform,
    versions: {
        node: process.versions.node,
        chrome: process.versions.chrome,
        electron: process.versions.electron,
    },

    // Window controls
    minimize: () => ipcRenderer.send('window-minimize'),
    maximize: () => ipcRenderer.send('window-maximize'),
    close: () => ipcRenderer.send('window-close'),
    toggleAlwaysOnTop: () => ipcRenderer.send('window-always-on-top'),

    // Events from main process
    onSystemEvent: (callback) => {
        ipcRenderer.on('system-event', (_event, data) => callback(data));
    },
});
