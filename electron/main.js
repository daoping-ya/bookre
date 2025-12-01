import { app, BrowserWindow, ipcMain, dialog } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

let mainWindow

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1024,
        minHeight: 768,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true
        },
        frame: true,
        backgroundColor: '#667eea',
        show: false
    })

    // 开发模式加载Vite服务器，生产模式加载构建文件
    const isDev = process.env.NODE_ENV === 'development'

    if (isDev) {
        mainWindow.loadURL('http://localhost:5173')
        mainWindow.webContents.openDevTools()
    } else {
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
    }

    // 窗口准备好后显示，避免白屏
    mainWindow.once('ready-to-show', () => {
        mainWindow.show()
    })

    mainWindow.on('closed', () => {
        mainWindow = null
    })
}

app.whenReady().then(() => {
    createWindow()

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow()
        }
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

// IPC处理器 - 文件选择对话框
ipcMain.handle('dialog:openFile', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: '电子书', extensions: ['epub', 'txt'] },
            { name: 'EPUB文件', extensions: ['epub'] },
            { name: 'TXT文件', extensions: ['txt'] },
            { name: '所有文件', extensions: ['*'] }
        ]
    })

    return result.filePaths
})

// 获取应用路径
ipcMain.handle('app:getPath', (event, name) => {
    return app.getPath(name)
})

console.log('📚 BookRe阅读器启动成功！')
