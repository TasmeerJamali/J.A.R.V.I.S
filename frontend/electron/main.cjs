const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false, // For simpler IPC in this prototype
      // preload: path.join(__dirname, 'preload.js') 
    },
    frame: false, // Frameless for sci-fi look
    transparent: true, // Transparent background
    alwaysOnTop: false, // Set to true for HUD mode later
  });

  // Load the React app
  const startUrl = process.env.ELECTRON_START_URL || `file://${path.join(__dirname, '../dist/index.html')}`;
  
  // In dev, wait a bit for Vite to start
  if (process.env.ELECTRON_START_URL) {
      mainWindow.loadURL(startUrl);
      mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
      mainWindow.loadURL(startUrl);
  }

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});
