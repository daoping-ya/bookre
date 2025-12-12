// 移动端性能优化配置
export const IS_MOBILE = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
export const IS_PRODUCTION = import.meta.env.MODE === 'production'

// 🔧 生产环境禁用所有console.log
if (IS_PRODUCTION) {
    console.log = () => { }
    console.warn = () => { }
    console.error = (...args) => {
        // 只保留critical错误上报
        if (window.__errorHandler) {
            window.__errorHandler(...args)
        }
    }
}

// 📱 移动端内存限制配置
export const MOBILE_CONFIG = {
    // sessionStorage 最大字节数（5MB → 1MB for mobile）
    MAX_CACHE_SIZE: IS_MOBILE ? 1024 * 1024 : 5 * 1024 * 1024,

    // 最多缓存章节数
    MAX_CACHED_CHAPTERS: IS_MOBILE ? 3 : 10,

    // 预加载章节数
    PRELOAD_COUNT: IS_MOBILE ? 1 : 3,

    // 音频缓存数
    MAX_AUDIO_CACHE: IS_MOBILE ? 2 : 5,

    // 启用虚拟滚动阈值（章节数）
    VIRTUAL_SCROLL_THRESHOLD: IS_MOBILE ? 50 : 200
}
