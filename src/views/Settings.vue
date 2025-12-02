<template>
  <div class="settings-page">
    <!-- 顶部导航 -->
    <header class="settings-header">
      <div class="header-inner">
        <button @click="goBack" class="btn-back">
          ← 返回
        </button>
        <h1>设置</h1>
      </div>
    </header>

    <main class="settings-content">
      <!-- 阅读设置卡片 -->
      <section class="settings-card">
        <div class="card-header">
          <span class="icon">📖</span>
          <h2>阅读设置</h2>
        </div>
        
        <div class="setting-item">
          <div class="label-row">
            <label>默认字体大小</label>
            <span class="value">{{ fontSize }}px</span>
          </div>
          <input type="range" v-model.number="fontSize" min="12" max="32" class="slider">
        </div>

        <div class="setting-item">
          <div class="label-row">
            <label>默认行间距</label>
            <span class="value">{{ lineHeight }}</span>
          </div>
          <input type="range" v-model.number="lineHeight" min="1.2" max="2.5" step="0.1" class="slider">
        </div>

        <div class="setting-item">
          <label>默认主题</label>
          <select v-model="theme" class="select-input">
            <option value="theme-light">明亮 (Light)</option>
            <option value="theme-sepia">护眼 (Sepia)</option>
            <option value="theme-dark">暗黑 (Dark)</option>
          </select>
        </div>
      </section>

      <!-- 语音设置卡片 -->
      <section class="settings-card">
        <div class="card-header">
          <span class="icon">🔊</span>
          <h2>语音设置</h2>
        </div>

        <div class="setting-item">
          <label>默认语音模型</label>
          <select v-model="voiceModel" class="select-input" :disabled="isLoadingVoices">
            <option v-for="v in voices" :key="v.id" :value="v.id">{{ v.name }}</option>
          </select>
          <div v-if="isLoadingVoices" class="helper-text">正在加载语音列表...</div>
        </div>

        <div class="setting-item">
          <div class="label-row">
            <label>默认语速</label>
            <span class="value">{{ voiceSpeed }}x</span>
          </div>
          <input type="range" v-model.number="voiceSpeed" min="0.5" max="2.0" step="0.1" class="slider">
        </div>
      </section>

      <!-- 数据管理卡片 -->
      <section class="settings-card">
        <div class="card-header">
          <span class="icon">💾</span>
          <h2>数据管理</h2>
        </div>

        <div class="setting-item">
          <label>存储位置</label>
          <div class="info-box">本地浏览器存储 (IndexedDB/LocalStorage)</div>
        </div>

        <div class="setting-actions">
          <button @click="clearCache" class="btn-danger">
            清除所有缓存数据
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 状态
const fontSize = ref(18)
const lineHeight = ref(1.6)
const theme = ref('theme-light')
const voiceModel = ref('zh-CN-XiaoxiaoNeural')
const voiceSpeed = ref(1.0)
const voices = ref([])
const isLoadingVoices = ref(false)

onMounted(async () => {
  loadSettings()
  await loadVoices()
})

function goBack() {
  router.back()
}

function loadSettings() {
  const saved = localStorage.getItem('reader_settings')
  if (saved) {
    const s = JSON.parse(saved)
    if (s.fontSize) fontSize.value = s.fontSize
    if (s.lineHeight) lineHeight.value = s.lineHeight
    if (s.theme) theme.value = s.theme
  }
  
  // 语音设置可能单独存储，这里简化处理，假设共用
}

// 自动保存
watch([fontSize, lineHeight, theme], () => {
  const settings = {
    fontSize: fontSize.value,
    lineHeight: lineHeight.value,
    theme: theme.value,
    // 保留其他可能的字段
    ...JSON.parse(localStorage.getItem('reader_settings') || '{}')
  }
  localStorage.setItem('reader_settings', JSON.stringify(settings))
})

async function loadVoices() {
  isLoadingVoices.value = true
  try {
    const res = await fetch('/api/voice/list')
    if (res.ok) {
      const data = await res.json()
      voices.value = data.voices || []
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoadingVoices.value = false
  }
}

function clearCache() {
  if (confirm('确定要清除所有书籍和阅读进度吗？此操作不可恢复。')) {
    localStorage.clear()
    alert('缓存已清除')
    router.push('/')
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background-color: #f3f4f6; /* 浅灰背景 */
  display: flex;
  flex-direction: column;
}

.settings-header {
  background: white;
  padding: 16px 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-inner {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-inner h1 {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.btn-back {
  border: 1px solid #e5e7eb;
  background: white;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.settings-content {
  flex: 1;
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.card-header .icon {
  font-size: 20px;
}

.card-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.setting-item {
  margin-bottom: 20px;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.label-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

label {
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  display: block;
  margin-bottom: 8px;
}

.value {
  font-size: 14px;
  color: #3b82f6;
  font-weight: 600;
}

/* 自定义滑块 */
.slider {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
  transition: transform 0.1s;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

/* 下拉框 */
.select-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
  color: #1f2937;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.select-input:focus {
  border-color: #3b82f6;
  background: white;
}

.info-box {
  padding: 12px;
  background: #f3f4f6;
  border-radius: 8px;
  font-size: 13px;
  color: #6b7280;
}

.helper-text {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.btn-danger {
  background: #fee2e2;
  color: #ef4444;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-danger:hover {
  background: #fecaca;
}
</style>
