/**
 * 设备ID管理工具
 */

/**
 * 获取或生成设备ID
 * @returns {string} 设备ID
 */
export function getDeviceId() {
    let deviceId = localStorage.getItem('device_id')

    if (!deviceId) {
        // 生成唯一设备ID: device_时间戳_随机字符串
        deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        localStorage.setItem('device_id', deviceId)
        console.log('📱 生成新设备ID:', deviceId)

        // 首次使用，提示用户命名设备
        initDeviceName()
    }

    return deviceId
}

/**
 * 获取设备名称
 * @returns {string} 设备名称
 */
export function getDeviceName() {
    return localStorage.getItem('device_name') || '未命名设备'
}

/**
 * 设置设备名称
 * @param {string} name - 设备名称
 */
export function setDeviceName(name) {
    localStorage.setItem('device_name', name)
    console.log('✏️ 设备名称已更新:', name)
}

/**
 * 初始化设备名称（首次使用时提示）
 */
function initDeviceName() {
    // 尝试自动识别设备类型
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)
    const defaultName = isMobile ? '我的手机' : '我的电脑'

    // 可选：显示友好提示
    setTimeout(() => {
        // 使用 window.prompt 避免构建环境报错
        const name = window.prompt(
            '🎉 欢迎使用！请为此设备命名（方便区分不同设备的阅读进度）',
            defaultName
        )
        if (name && name.trim()) {
            setDeviceName(name.trim())
        } else {
            setDeviceName(defaultName)
        }
    }, 500)
}

/**
 * 获取设备信息（用于调试）
 */
export function getDeviceInfo() {
    return {
        id: getDeviceId(),
        name: getDeviceName(),
        userAgent: navigator.userAgent
    }
}
