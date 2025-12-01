import { contextBridge, ipcRenderer } from 'electron'

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
    // 文件操作
    openFileDialog: () => ipcRenderer.invoke('dialog:openFile'),
    getAppPath: (name) => ipcRenderer.invoke('app:getPath', name),

    // 未来扩展：Python后端通信
    callPythonAPI: (endpoint, data) => ipcRenderer.invoke('python:call', endpoint, data)
})

console.log('🔒 Preload脚本加载成功')
