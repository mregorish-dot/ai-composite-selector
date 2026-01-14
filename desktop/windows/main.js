const { app, BrowserWindow } = require('electron');
const path = require('path');

// ЗАМЕНИТЕ НА ВАШУ ССЫЛКУ НА STREAMLIT CLOUD
const APP_URL = 'https://ВАШ_ПОЛЬЗОВАТЕЛЬ-streamlit-app-XXXXXX.streamlit.app';

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    },
    icon: path.join(__dirname, 'icon.ico'),
    title: 'AI Composite Selector'
  });

  win.loadURL(APP_URL);
  
  // Открыть DevTools в режиме разработки (закомментируйте для продакшена)
  // win.webContents.openDevTools();
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

