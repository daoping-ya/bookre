<template>
  <div class="reader-app" :class="currentTheme">
    <!-- 顶部导航栏 -->
    <header class="top-bar" :class="{ 'hidden': !showControls }">
      <div class="left-actions">
        <button @click="goBack" class="btn-icon" title="返回书架">
          <span class="icon">←</span>
        </button>
        <div class="book-info">
          <h1 class="book-title">{{ currentBook?.title || '加载中...' }}</h1>
          <span class="chapter-title" v-if="currentChapterTitle">{{ currentChapterTitle }}</span>
        </div>
      </div>
      
      <div class="right-actions">
        <button @click="toggleTOC" class="btn-icon" :class="{ active: showSidebar === 'toc' }" title="目录">
          <span class="icon">📑</span>
        </button>
        <button @click="toggleVoicePanel" class="btn-icon" :class="{ active: showSidebar === 'voice' }" title="听书">
          <span class="icon">🎧</span>
        </button>
        <button @click="toggleSettings" class="btn-icon" :class="{ active: showSettings }" title="设置">
          <span class="icon">⚙️</span>
        </button>
      </div>
    </header>

    <!-- 主体区域 -->
    <div class="main-container">
      <!-- 左侧侧边栏 (目录/书签/语音) -->
      <transition name="slide-left">
        <aside v-if="showSidebar" class="sidebar">
          <!-- 目录面板 -->
          <div v-if="showSidebar === 'toc'" class="sidebar-panel toc-panel">
            <div class="panel-header">
              <h3>目录</h3>
              <button @click="closeSidebar" class="btn-close">×</button>
            </div>
            <div class="toc-list" ref="tocListRef">
              <div 
                v-for="(chapter, index) in chapters" 
                :key="index"
                class="toc-item"
                :class="{ active: currentChapter === index }"
                @click="jumpToChapter(index)"
              >
                <span class="toc-index">{{ index + 1 }}</span>
                <span class="toc-text">{{ chapter.title }}</span>
              </div>
              <div v-if="chapters.length === 0" class="empty-tip">
                暂无目录信息
              </div>
            </div>
          </div>

          <!-- 语音面板 -->
          <div v-if="showSidebar === 'voice'" class="sidebar-panel voice-panel">
            <div class="panel-header">
              <h3>语音朗读</h3>
              <button @click="closeSidebar" class="btn-close">×</button>
            </div>
            
            <div class="voice-controls-container">
              <div class="voice-status">
                <div class="status-indicator" :class="{ playing: isPlaying }"></div>
                <span>{{ isPlaying ? '正在朗读...' : '已暂停' }}</span>
              </div>

              <div class="control-group">
                <label>选择语音</label>
                <select v-model="selectedVoice" class="form-select" :disabled="isLoadingVoices || isSwitchingVoice">
                  <option v-for="voice in availableVoices" :key="voice.id" :value="voice.id">
                    {{ voice.name }}
                  </option>
                </select>
                <div v-if="isLoadingVoices" class="loading-text">加载语音列表...</div>
                <div v-if="isSwitchingVoice" class="loading-text">🔄 正在切换语音，请稍候...</div>
              </div>

              <div class="control-group">
                <label>语速: {{ voiceSpeed }}x</label>
                <input type="range" v-model.number="voiceSpeed" min="0.5" max="2.0" step="0.1" class="form-range">
              </div>

              <div class="playback-actions">
                <button @click="togglePlay" class="btn-primary btn-large">
                  {{ isPlaying ? '⏸ 暂停' : '▶ 开始朗读' }}
                </button>
                <button @click="stopVoice" class="btn-secondary">⏹ 停止</button>
              </div>
            </div>
          </div>
        </aside>
      </transition>

      <!-- 阅读区域 -->
      <main 
        class="content-area" 
        ref="contentAreaRef"
        @click="toggleControls"
        @wheel="handleWheel"
      >
        <div class="page-container" :style="pageStyle" ref="pageContainerRef">
          <div v-if="isLoading" class="loading-spinner">
            加载中...
          </div>
          <div v-else class="page-content">
            <p 
              v-for="(para, index) in currentParagraphs" 
              :key="index"
              class="reader-paragraph"
              :class="{ active: isPlaying && currentPage === playingPageIndex && currentParaIndex === index }"
            >
              {{ para }}
            </p>
          </div>
        </div>
      </main>

      <!-- 设置面板 (浮层) -->
      <transition name="fade">
        <div v-if="showSettings" class="settings-modal" @click.self="closeSettings">
          <div class="settings-card">
            <div class="settings-header">
              <h3>阅读设置</h3>
              <button @click="closeSettings" class="btn-close">×</button>
            </div>
            
            <div class="setting-item">
              <label>主题</label>
              <div class="theme-options">
                <button 
                  v-for="theme in themes" 
                  :key="theme.value"
                  class="theme-btn" 
                  :class="[theme.value, { active: currentTheme === theme.value }]"
                  @click="setTheme(theme.value)"
                >
                  Aa
                </button>
              </div>
            </div>

            <div class="setting-item">
              <label>字号: {{ fontSize }}px</label>
              <div class="stepper">
                <button @click="adjustFontSize(-1)">-</button>
                <input type="range" v-model.number="fontSize" min="12" max="36" step="1">
                <button @click="adjustFontSize(1)">+</button>
              </div>
            </div>

            <div class="setting-item">
              <label>字体</label>
              <div class="font-options">
                <button 
                  v-for="font in fonts" 
                  :key="font.value"
                  class="option-btn"
                  :class="{ active: fontFamily === font.value }"
                  @click="fontFamily = font.value"
                >
                  {{ font.label }}
                </button>
              </div>
            </div>

            <div class="setting-item">
              <label>粗细</label>
              <div class="toggle-group">
                <button 
                  class="option-btn" 
                  :class="{ active: !isBold }"
                  @click="isBold = false"
                >常规</button>
                <button 
                  class="option-btn" 
                  :class="{ active: isBold }"
                  @click="isBold = true"
                >加粗</button>
              </div>
            </div>

            <div class="setting-item">
              <label>行高: {{ lineHeight }}</label>
              <input type="range" v-model.number="lineHeight" min="1.0" max="2.5" step="0.1" class="form-range">
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 底部进度栏 -->
    <footer class="bottom-bar" :class="{ 'hidden': !showControls }">
      <button @click="prevPage" class="btn-page" :disabled="currentPage <= 0">上一页</button>
      
      <div class="progress-info">
        <span class="page-num">{{ currentPage + 1 }} / {{ totalPages }}</span>
        <div class="slider-container" @click="handleProgressClick">
          <div class="slider-track">
            <div class="slider-fill" :style="{ width: progressPercentage + '%' }"></div>
          </div>
        </div>
        <span class="percentage">{{ Math.round(progressPercentage) }}%</span>
      </div>

      <button @click="nextPage" class="btn-page" :disabled="currentPage >= totalPages - 1">下一页</button>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBooksStore } from '@/store/books'

// --- 核心状态 ---
const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()
const bookId = parseInt(route.params.bookId)

const currentBook = ref(null)
const chapters = ref([])
const pages = ref([])
const currentPage = ref(0)
const currentChapter = ref(0)
const isLoading = ref(true)
const showControls = ref(true)
const showSidebar = ref(null) // 'toc', 'voice', or null
const showSettings = ref(false)
const contentAreaRef = ref(null) // DOM 引用：阅读内容区域
const pageContainerRef = ref(null) // DOM 引用：实际滚动容器

// --- 设置状态 ---
const currentTheme = ref('theme-light')
const fontSize = ref(18)
const lineHeight = ref(1.6)
const fontFamily = ref('sans-serif')
const isBold = ref(false)

// --- 语音状态 ---
const isPlaying = ref(false)
const isLoadingVoices = ref(false)
const isSwitchingVoice = ref(false)
const availableVoices = ref([])
const selectedVoice = ref('zh-CN-YunxiNeural')
const voiceSpeed = ref(1.0)
const audioPlayer = ref(null)
const audioCache = new Map() // Map<pageIndex, BlobURL>
const preloadCount = 2 // 预加载页数（降低以减轻 EasyVoice 负载）
const currentParaIndex = ref(0) // 当前播放的段落索引
const playingPageIndex = ref(-1) // 正在播放的音频对应的页码
let currentFetchController = null // 当前请求的控制器
let isFetchingGlobal = false // 全局请求锁
let pageTurnTimer = null    // 用于滚轮翻页的冷却计时器
let scrollBoundaryCounter = 0 // 连续滚动到边界的计数器


// --- 常量定义 ---
const themes = [
  { value: 'theme-light', label: '明亮' },
  { value: 'theme-sepia', label: '护眼' },
  { value: 'theme-dark', label: '暗黑' }
]

const fonts = [
  { value: 'sans-serif', label: '黑体' },
  { value: 'serif', label: '宋体' },
  { value: '楷体', label: '楷体' }
]

// --- 计算属性 ---
const totalPages = computed(() => pages.value.length || 1)
const currentPageContent = computed(() => pages.value[currentPage.value] || '')
const progressPercentage = computed(() => ((currentPage.value + 1) / totalPages.value) * 100)

const currentChapterTitle = computed(() => {
  if (!chapters.value.length) return ''
  return chapters.value[currentChapter.value]?.title || ''
})

const pageStyle = computed(() => ({
  fontSize: `${fontSize.value}px`,
  lineHeight: lineHeight.value,
  fontFamily: fontFamily.value,
  fontWeight: isBold.value ? 'bold' : 'normal'
}))

const currentParagraphs = computed(() => {
  const content = pages.value[currentPage.value] || ''
  return content.split('\n').filter(p => p.trim())
})


// --- 生命周期 ---
onMounted(async () => {
  // 确保数据已加载 (防止刷新页面丢失)
  if (booksStore.books.length === 0) {
    booksStore.loadFromLocalStorage()
  }
  
  await loadBookData()
  loadSettings()
  window.addEventListener('keydown', handleKeydown)
  loadVoices()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  saveSettings()
  stopVoice()
  clearAudioCache()
})

// --- 核心逻辑 ---
async function loadBookData() {
  isLoading.value = true
  try {
    // 从后端获取完整书籍内容 (包括章节)
    currentBook.value = await booksStore.fetchBookContent(bookId)
    console.log('当前书籍:', currentBook.value) // 调试
    
    if (!currentBook.value) {
      alert('书籍未找到')
      router.push('/')
      return
    }
    
    // 加载章节
    chapters.value = currentBook.value.chapters || []
    console.log('加载的章节数:', chapters.value.length) // 调试
    console.log('第一个章节示例:', chapters.value[0]) // 调试
    
    // 分页处理
    await paginate()
    console.log('分页后的总页数:', pages.value.length) // 调试
    
    // 恢复进度
    if (currentBook.value.currentPage) {
      currentPage.value = Math.min(currentBook.value.currentPage, totalPages.value - 1)
    }
    if (currentBook.value.currentChapter) {
      currentChapter.value = currentBook.value.currentChapter
    }
  } catch (e) {
    console.error('加载书籍失败', e)
  } finally {
    isLoading.value = false
  }
}

// 分页算法 - 恢复字符估算 (支持滚动条)
async function paginate() {
  // 恢复到简单的基于字符数的分页
  const charsPerPage = calculateCharsPerPage()
  const newPages = []
  const chapterMap = [] 

  chapters.value.forEach((chapter, cIndex) => {
    const content = chapter.content || ''
    const paras = content.split('\n')
    let currentChunk = ''

    paras.forEach(para => {
      para = para.trim()
      if (!para) return
      
      // 确保段落有缩进
      const indentPara = '　　' + para + '\n\n'
      
      // 检查当前块加上新段落是否会溢出预估的字符数
      if (currentChunk.length + indentPara.length > charsPerPage && currentChunk) {
        // 当前块已满，推入新页
        newPages.push(currentChunk)
        chapterMap.push(cIndex)
        currentChunk = indentPara // 将当前段落作为新页的开始
      } else {
        // 追加内容
        currentChunk += indentPara
      }
    })
    
    if (currentChunk) {
      newPages.push(currentChunk)
      chapterMap.push(cIndex)
    }
  })

  if (newPages.length === 0) {
    newPages.push('暂无内容')
    chapterMap.push(0)
  }

  pages.value = newPages
  window._pageToChapter = chapterMap
  await nextTick()
}



function calculateCharsPerPage() {
  // 根据字号动态估算
  // 字号越大，每页字数越少
  const baseChars = 800
  const scale = 18 / fontSize.value
  return Math.floor(baseChars * scale * scale)
}

// 监听设置变化重新分页
watch([fontSize, lineHeight, fontFamily, isBold], () => {
  // 防抖处理
  if (window._paginateTimer) clearTimeout(window._paginateTimer)
  window._paginateTimer = setTimeout(() => {
    const progress = currentPage.value / totalPages.value
    paginate().then(() => {
      // 尝试保持阅读进度
      currentPage.value = Math.floor(progress * totalPages.value)
      updateProgress()
    })
  }, 500)
})

// 监听语音切换
watch(selectedVoice, async (newVoice, oldVoice) => {
  if (!oldVoice || newVoice === oldVoice || isSwitchingVoice.value) return
  
  console.log('🔄 语音切换:', oldVoice, '->', newVoice)
  stopVoice()
  clearAudioCache()
  // 切换后不自动播放，等待用户点击
})

// 监听语速切换
watch(voiceSpeed, () => {
  if (isPlaying.value) {
    stopVoice()
    clearAudioCache()
    playVoice()
  } else {
    clearAudioCache()
  }
})

// --- 交互逻辑 ---
function toggleControls() {
  showControls.value = !showControls.value
  if (!showControls.value) {
    showSidebar.value = null
    showSettings.value = false
  }
  // 绝对禁止在此处调用播放相关函数
}

function toggleTOC() {
  showSidebar.value = showSidebar.value === 'toc' ? null : 'toc'
  showSettings.value = false
}

function toggleVoicePanel() {
  showSidebar.value = showSidebar.value === 'voice' ? null : 'voice'
  showSettings.value = false
}

function toggleSidebar(type) {
  showSidebar.value = showSidebar.value === type ? null : type
}

function closeSidebar() {
  showSidebar.value = null
}

function toggleSettings() {
  showSettings.value = !showSettings.value
  if (showSettings.value) {
    showSidebar.value = null
  }
}

function closeSettings() {
  showSettings.value = false
}

function goBack() {
  router.push('/')
}

function prevPage() {
  if (currentPage.value > 0) {
    currentPage.value--
    updateProgress()
    // 重置滚动条到顶部
    nextTick(() => {
      if (pageContainerRef.value) {
        pageContainerRef.value.scrollTop = 0
      }
    })
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++
    updateProgress()
    // 重置滚动条到顶部
    nextTick(() => {
      if (pageContainerRef.value) {
        pageContainerRef.value.scrollTop = 0
      }
    })
  }
}

function jumpToChapter(index) {
  // 找到该章节的第一页
  const targetPage = window._pageToChapter.findIndex(c => c === index)
  if (targetPage !== -1) {
    currentPage.value = targetPage
    currentChapter.value = index
    updateProgress()
    // 移动端自动关闭侧边栏
    if (window.innerWidth < 768) closeSidebar()
  }
}

function handleProgressClick(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const percent = x / rect.width
  currentPage.value = Math.floor(percent * totalPages.value)
  updateProgress()
}

function updateProgress() {
  // 更新当前章节
  if (window._pageToChapter && window._pageToChapter[currentPage.value] !== undefined) {
    currentChapter.value = window._pageToChapter[currentPage.value]
  }
  
  // 保存到 Store
  if (currentBook.value) {
    booksStore.updateProgress(bookId, currentPage.value, currentChapter.value)
  }
  
  // 不再包含任何播放逻辑 - 滚轮翻页不应影响语音播放
  // TTS 的音频切换完全由 onended 事件处理
}

function handleKeydown(e) {
  if (e.key === 'ArrowLeft') prevPage()
  if (e.key === 'ArrowRight') nextPage()
  if (e.key === ' ') {
    e.preventDefault()
    nextPage()
  }
}

function handleWheel(e) {
  const el = pageContainerRef.value
  if (!el) return

  // 1. 正常的页面拖动行为（由浏览器处理）

  // 2. 只有在滚轮到边界时，才检查翻页
  const scrolledToBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 1 // 1px 误差
  const scrolledToTop = el.scrollTop <= 1 // 1px 误差
  
  // 检查是否已经存在冷却计时器
  if (pageTurnTimer) {
    // 如果在冷却期内再次滚动到边界，重置计数器防止误触
    scrollBoundaryCounter = 0 
    return 
  }

  // 向下滚动 (滚到底部)
  if (e.deltaY > 0 && scrolledToBottom) {
    
    scrollBoundaryCounter++
    if (scrollBoundaryCounter >= 2) { // 双击翻页逻辑
      nextPage()
      
      // 翻页后，重置滚动条到顶部，并启动冷却计时
      nextTick(() => { 
        if (pageContainerRef.value) pageContainerRef.value.scrollTop = 0 
      })
      pageTurnTimer = setTimeout(() => {
        pageTurnTimer = null
        scrollBoundaryCounter = 0
      }, 500) // 0.5秒冷却期
      e.preventDefault() // 阻止浏览器滚动
    }
  } 
  // 向上滚动 (滚到顶部)
  else if (e.deltaY < 0 && scrolledToTop) {
    
    scrollBoundaryCounter++
    if (scrollBoundaryCounter >= 2) { // 双击翻页逻辑
      prevPage()
      
      // 翻页后，重置滚动条到底部，并启动冷却计时
      nextTick(() => { 
        if (pageContainerRef.value) pageContainerRef.value.scrollTop = pageContainerRef.value.scrollHeight 
      })
      pageTurnTimer = setTimeout(() => {
        pageTurnTimer = null
        scrollBoundaryCounter = 0
      }, 500)
      e.preventDefault()
    }
  } else {
    // 如果滚轮没有在边界，则重置计数器
    scrollBoundaryCounter = 0
  }
}

// 目录自动定位
const tocListRef = ref(null)
function scrollToActiveChapter() {
  nextTick(() => {
    if (!tocListRef.value) return
    const activeItem = tocListRef.value.querySelector('.toc-item.active')
    if (activeItem) {
      activeItem.scrollIntoView({ block: 'center', behavior: 'smooth' })
    }
  })
}

watch(() => showSidebar.value, (val) => {
  if (val === 'toc') {
    scrollToActiveChapter()
  }
})

// --- 设置管理 ---
function loadSettings() {
  const saved = localStorage.getItem('reader_settings')
  if (saved) {
    const s = JSON.parse(saved)
    currentTheme.value = s.theme || 'theme-light'
    fontSize.value = s.fontSize || 18
    lineHeight.value = s.lineHeight || 1.6
    fontFamily.value = s.fontFamily || 'sans-serif'
    isBold.value = s.isBold || false
  }
}

function saveSettings() {
  const settings = {
    theme: currentTheme.value,
    fontSize: fontSize.value,
    lineHeight: lineHeight.value,
    fontFamily: fontFamily.value,
    isBold: isBold.value
  }
  localStorage.setItem('reader_settings', JSON.stringify(settings))
}

function setTheme(theme) {
  currentTheme.value = theme
}

function adjustFontSize(delta) {
  const newVal = fontSize.value + delta
  if (newVal >= 12 && newVal <= 36) {
    fontSize.value = newVal
  }
}

// --- 语音功能 ---
async function loadVoices() {
  isLoadingVoices.value = true
  try {
    const res = await fetch('/api/voice/list')
    if (res.ok) {
      const data = await res.json()
      availableVoices.value = data.voices || []
      
      // 检查当前选中的语音是否有效
      if (availableVoices.value.length > 0) {
        const isValid = availableVoices.value.some(v => v.ShortName === selectedVoice.value)
        if (!isValid) {
          console.warn(`⚠️ 当前语音 ${selectedVoice.value} 无效，重置为默认`)
          selectedVoice.value = availableVoices.value[0].ShortName
        }
      }
    }
  } catch (e) {
    console.error('语音列表加载失败', e)
  } finally {
    isLoadingVoices.value = false
  }
}

async function togglePlay() {
  if (isPlaying.value) {
    stopVoice()
  } else {
    playVoice()
  }
}

// 高亮状态
const highlightStyle = ref({
  display: 'none',
  top: '0px',
  left: '0px',
  width: '0px',
  height: '0px'
})

// 核心播放入口 (整页模式 + SSML 高亮)
async function playVoice() {
  console.log('=== 开始 TTS 播放流程 (SSML) ===')
  if (!currentPageContent.value) return
  
  // 【关键修复】移动端音频解锁
  // 必须在用户点击事件的同步堆栈中立即创建/恢复 AudioContext 或 Audio 对象
  if (!audioPlayer.value) {
    audioPlayer.value = new Audio()
  }
  
  // 播放一段极短的静音来解锁音频引擎
  // 这是一个 base64 编码的 0.1秒静音 WAV 文件
  const silentWav = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA'
  audioPlayer.value.src = silentWav
  try {
    await audioPlayer.value.play()
    console.log('🔊 音频引擎解锁成功')
  } catch (e) {
    console.warn('⚠️ 音频引擎解锁失败 (可能需要用户交互)', e)
  }

  isPlaying.value = true
  playingPageIndex.value = currentPage.value // 记录当前播放的页码
  
  try {
    // 1. 获取音频和元数据
    const { url, metadata } = await fetchAudioPage(currentPage.value)
    
    if (!isPlaying.value) return // 可能在请求中被停止

    // 复用已解锁的 audioPlayer
    audioPlayer.value.src = url
    
    // 2. 设置段落高亮 - 基于时间的粗略估算
    audioPlayer.value.onloadedmetadata = () => {
      const totalDuration = audioPlayer.value.duration
      const paragraphs = currentParagraphs.value
      
      if (paragraphs.length > 0 && totalDuration > 0) {
        // 计算总字符数
        const totalChars = paragraphs.reduce((sum, p) => sum + p.length, 0)
        let currentTime = 0
        const timingData = []
        
        // 为每个段落计算时间范围
        paragraphs.forEach(p => {
          const duration = (p.length / totalChars) * totalDuration
          timingData.push({
            start: currentTime,
            end: currentTime + duration
          })
          currentTime += duration
        })
        
        // 监听播放进度并更新高亮
        audioPlayer.value.ontimeupdate = () => {
          // 【关键修复】防止播放器销毁后的残留事件触发
          const el = audioPlayer.value
          if (!el) return
          
          const current = el.currentTime
          const activeIndex = timingData.findIndex(t => current >= t.start && current < t.end)
          
          if (activeIndex !== -1 && activeIndex !== currentParaIndex.value) {
            currentParaIndex.value = activeIndex
            // 只在播放页等于当前页时滚动
            if (currentPage.value === playingPageIndex.value) {
              scrollToParagraph(activeIndex)
            }
          }
        }
      }
    }
    
    // 3. 启动 SSML 高亮同步循环（如果有元数据）
    if (metadata && metadata.length > 0) {
      startHighlightLoop(metadata)
    }

    audioPlayer.value.onended = () => {
      console.log('✅ 本页播放结束，自动翻页')
      stopHighlightLoop()
      currentParaIndex.value = -1
      
      if (currentPage.value < totalPages.value - 1) {
        // TTS 自动翻页 - 这是唯一会触发音频切换的地方
        currentPage.value++
        updateProgress() // 只更新进度，不触发播放
        playingPageIndex.value = currentPage.value // 更新播放页码
        
        // 递归调用 playVoice，这在移动端可能也会被拦截，但通常连续播放是被允许的
        // 只要第一个 play 是由用户触发的
        setTimeout(() => playVoice(), 500) 
      } else {
        // 最后一页播放完毕
        isPlaying.value = false
        playingPageIndex.value = -1
      }
    }
    
    await audioPlayer.value.play()
    
    // 预加载下一页
    preloadNextPage()

  } catch (e) {
    console.error('❌ 播放失败', e)
    isPlaying.value = false
    playingPageIndex.value = -1
    alert('播放失败: ' + e.message)
  }
}

// 停止播放
function stopVoice() {
  if (audioPlayer.value) {
    audioPlayer.value.pause()
    audioPlayer.value = null
  }
  stopHighlightLoop()
  isPlaying.value = false
  playingPageIndex.value = -1
  highlightStyle.value.display = 'none'
  currentParaIndex.value = -1
  if (currentFetchController) {
    currentFetchController.abort()
    currentFetchController = null
  }
}

// 自动滚动到指定段落
function scrollToParagraph(index) {
  const el = contentAreaRef.value
  if (!el) return
  
  const paragraphs = el.querySelectorAll('.reader-paragraph')
  const target = paragraphs[index]
  
  if (target) {
    target.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

// ... (上文代码)

// 高亮同步逻辑
let highlightRafId = null

function startHighlightLoop(metadata) {
  if (!metadata || metadata.length === 0) return
  
  // 预计算段落偏移量映射
  // 必须使用与 TTS 发送时完全一致的文本进行计算
  const fullText = pages.value[currentPage.value] || ''
  const paras = currentParagraphs.value // 这是渲染用的段落数组
  
  // 构建映射：渲染段落索引 -> 在 fullText 中的起始位置
  // 注意：currentParagraphs 是 split('\n').filter(...) 后的结果
  // 这意味着我们需要在 fullText 中查找这些段落的位置
  const paraMap = []
  let searchIndex = 0
  
  paras.forEach((paraText, index) => {
    const foundIndex = fullText.indexOf(paraText, searchIndex)
    if (foundIndex !== -1) {
      paraMap.push({
        index: index,
        start: foundIndex,
        end: foundIndex + paraText.length,
        text: paraText
      })
      searchIndex = foundIndex + paraText.length
    }
  })

  const update = () => {
    if (!audioPlayer.value || audioPlayer.value.paused) return
    
    // Edge TTS 的时间戳单位通常是 100ns (ticks)，后端除以 10000 转成了 ms
    // audioPlayer.currentTime 是秒
    const currentTime = audioPlayer.value.currentTime * 1000
    
    const item = metadata.find(m => currentTime >= m.start && currentTime <= m.end)
    
    if (item) {
      renderHighlight(item, paraMap)
    } else {
      highlightStyle.value.display = 'none'
    }
    
    highlightRafId = requestAnimationFrame(update)
  }
  
  highlightRafId = requestAnimationFrame(update)
}

function stopHighlightLoop() {
  if (highlightRafId) {
    cancelAnimationFrame(highlightRafId)
    highlightRafId = null
  }
}


function renderHighlight(item, paraMap) {
  // item.charOffset 是在 fullText 中的偏移量
  const globalOffset = item.charOffset
  
  // 1. 找到所属段落
  const paraInfo = paraMap.find(p => globalOffset >= p.start && globalOffset < p.end)
  
  if (!paraInfo) {
    // 可能匹配到了被过滤掉的空行，或者标点符号
    highlightStyle.value.display = 'none'
    return
  }
  
  // 2. 计算段落内偏移
  const localOffset = globalOffset - paraInfo.start
  const length = item.part.length
  
  // 3. 获取 DOM 节点
  // 假设 .reader-paragraph 按照顺序渲染
  const paraNodes = document.querySelectorAll('.reader-paragraph')
  const targetNode = paraNodes[paraInfo.index]
  
  if (!targetNode || !targetNode.firstChild) return
  
  try {
    const range = document.createRange()
    // 注意：targetNode 可能包含多个子节点（如果以后加了格式），目前假设只有文本节点
    // 安全起见，使用 TreeWalker 或简单假设
    const textNode = targetNode.firstChild
    
    // 边界检查
    const safeStart = Math.min(localOffset, textNode.length)
    const safeEnd = Math.min(localOffset + length, textNode.length)
    
    range.setStart(textNode, safeStart)
    range.setEnd(textNode, safeEnd)
    
    const rect = range.getBoundingClientRect()
    const containerRect = contentAreaRef.value.getBoundingClientRect()
    
    // 4. 更新高亮框 (相对于 content-area)
    // 需要加上 scrollTop，因为 content-area 是滚动的
    highlightStyle.value = {
      display: 'block',
      top: `${rect.top - containerRect.top + contentAreaRef.value.scrollTop}px`,
      left: `${rect.left - containerRect.left}px`,
      width: `${rect.width}px`,
      height: `${rect.height}px`
    }
    
    // 自动滚动：如果高亮框跑出可视区域，自动滚动
    // 简单的可视区域检查
    const relativeTop = rect.top - containerRect.top
    if (relativeTop > containerRect.height - 100 || relativeTop < 50) {
      targetNode.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
    
  } catch (e) {
    console.warn('Highlight error', e)
    highlightStyle.value.display = 'none'
  }
}


function playParagraph(index) {
  if (!isPlaying.value) {
    playVoice()
  } else {
    console.log('Jump to paragraph', index)
  }
}

async function fetchAudioPage(pageIndex) {
  const content = pages.value[pageIndex]
  if (!content) throw new Error('内容为空')
  
  const fullText = content
  const currentVoice = selectedVoice.value
  const currentSpeed = voiceSpeed.value
  const rateStr = currentSpeed >= 1 
    ? `+${Math.round((currentSpeed - 1) * 100)}%` 
    : `${Math.round((currentSpeed - 1) * 100)}%`
  
  const cacheKey = `${pageIndex}_${currentVoice}_${rateStr}_full`
  
  if (audioCache.has(cacheKey)) {
    return audioCache.get(cacheKey)
  }

  while (isFetchingGlobal) {
    await new Promise(r => setTimeout(r, 100))
  }
  
  currentFetchController = new AbortController()
  isFetchingGlobal = true
  
  try {
    const response = await fetch('http://localhost:8000/api/voice/synthesize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: fullText,
        voice_model: currentVoice,
        rate: rateStr,
        stream: false
      }),
      signal: currentFetchController.signal
    })
    
    if (!response.ok) throw new Error(await response.text())
    
    const data = await response.json()
    console.log('🔍 TTS 响应数据:', data) // 调试日志
    
    // 检查数据结构并适配
    let audioBlobUrl, metadata
    
    // 新版后端返回 Base64 数据 (data.audio_base64)
    if (data.data && data.data.audio_base64) {
      const base64 = data.data.audio_base64
      const binaryString = window.atob(base64)
      const len = binaryString.length
      const bytes = new Uint8Array(len)
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      const blob = new Blob([bytes], { type: 'audio/mpeg' })
      audioBlobUrl = URL.createObjectURL(blob)
      metadata = data.data.metadata || []
      console.log('✅ 已将 Base64 转换为 Blob URL')
    } 
    // 兼容旧版 URL 方式 (以防后端回滚)
    else if (data.data && data.data.audio_url) {
      audioBlobUrl = data.data.audio_url
      if (audioBlobUrl.startsWith('/')) {
        audioBlobUrl = 'http://localhost:8000' + audioBlobUrl
      }
      metadata = data.data.metadata || []
    } else {
      // 尝试其他可能的字段
      const url = data.audio_url || data.audio || (data.data && data.data.audio)
      if (url) {
        audioBlobUrl = url
        if (audioBlobUrl.startsWith('/')) {
          audioBlobUrl = 'http://localhost:8000' + audioBlobUrl
        }
        metadata = data.metadata || data.timing_metadata || (data.data && data.data.metadata) || []
      } else {
        console.error('❌ 不支持的响应格式:', data)
        throw new Error('TTS 响应格式错误，未找到音频数据')
      }
    }
    
    const result = {
      url: audioBlobUrl,
      metadata: metadata,
      isBlob: audioBlobUrl.startsWith('blob:')
    }
    
    // 如果旧缓存存在且是 Blob，先释放
    if (audioCache.has(cacheKey)) {
      const old = audioCache.get(cacheKey)
      if (old.isBlob) URL.revokeObjectURL(old.url)
    }

    audioCache.set(cacheKey, result)
    
    // 内存保护：限制缓存大小 (LRU)
    // Map 保持插入顺序，keys().next().value 是最早插入的
    if (audioCache.size > 5) {
      const oldestKey = audioCache.keys().next().value
      const oldItem = audioCache.get(oldestKey)
      if (oldItem && oldItem.isBlob) {
        URL.revokeObjectURL(oldItem.url)
        console.log(`🧹 释放旧缓存页: ${oldestKey}`)
      }
      audioCache.delete(oldestKey)
    }

    return result
    
  } finally {
    isFetchingGlobal = false
    currentFetchController = null
  }
}

function preloadNextPage() {
  if (currentPage.value < totalPages.value - 1) {
    fetchAudioPage(currentPage.value + 1).catch(e => console.log('预加载失败', e))
  }
}

function clearAudioCache() {
  audioCache.forEach(item => {
    if (item.isBlob && item.url) {
      URL.revokeObjectURL(item.url)
    }
  })
  audioCache.clear()
  console.log('🧹 音频缓存已清理')
}
</script>

<style scoped>
/* 基础布局 */
.reader-app {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  transition: background-color 0.3s, color 0.3s;
}

/* 主题配色 */
.theme-light {
  background-color: #ffffff;
  color: #333333;
  --bg-panel: #f8f9fa;
  --border-color: #e9ecef;
  --accent-color: #4dabf7;
}

.theme-sepia {
  background-color: #f4ecd8;
  color: #5c4b37;
  --bg-panel: #eaddcf;
  --border-color: #d3c4b1;
  --accent-color: #d08770;
}

.theme-dark {
  background-color: #2d3748;
  color: #e2e8f0;
  --bg-panel: #1a202c;
  --border-color: #4a5568;
  --accent-color: #63b3ed;
}

/* 顶部导航 */
.top-bar {
  height: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  background-color: var(--bg-panel);
  border-bottom: 1px solid var(--border-color);
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  transition: transform 0.3s ease;
}

.top-bar.hidden {
  transform: translateY(-100%);
}

.left-actions, .right-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.book-info {
  margin-left: 12px;
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 14px;
  font-weight: bold;
  margin: 0;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chapter-title {
  font-size: 10px;
  opacity: 0.7;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  color: inherit;
}

.btn-icon:hover, .btn-icon.active {
  background-color: rgba(0,0,0,0.1);
}

/* 主容器 */
.main-container {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
  margin-top: 50px; /* 留出顶部空间 */
  margin-bottom: 50px; /* 留出底部空间 */
}

/* 侧边栏 */
.sidebar {
  width: 300px;
  background-color: var(--bg-panel);
  border-right: 1px solid var(--border-color);
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
  z-index: 90;
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
}

.sidebar-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: inherit;
}

.toc-list {
  flex: 1;
  overflow-y: auto;
}

.toc-item {
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  gap: 8px;
}

.toc-item:hover {
  background-color: rgba(0,0,0,0.05);
}

.toc-item.active {
  background-color: var(--accent-color);
  color: white;
}

.toc-index {
  opacity: 0.6;
  font-size: 0.9em;
}

/* 语音面板样式 */
.voice-controls-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.voice-status {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
  padding: 10px;
  background: rgba(0,0,0,0.05);
  border-radius: 8px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #ccc;
}

.status-indicator.playing {
  background-color: #48bb78;
  box-shadow: 0 0 8px #48bb78;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-select, .form-range {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.playback-actions {
  display: flex;
  gap: 10px;
}

.btn-primary {
  flex: 2;
  background-color: var(--accent-color);
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
}

.btn-secondary {
  flex: 1;
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: inherit;
  border-radius: 6px;
  cursor: pointer;
}

/* 内容区域 */
.content-area {
  flex: 1;
  height: 100%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  position: relative;
}

.page-container {
  width: 100%;
  max-width: 800px;
  height: 100%;
  padding: 40px;
  overflow-y: auto; /* 允许内容内部滚动 */
  box-sizing: border-box;
}

.page-content {
  white-space: pre-wrap;
  text-align: justify;
}

/* 设置弹窗 */
.settings-modal {
  position: absolute;
  top: 60px;
  right: 20px;
  z-index: 110;
}

.settings-card {
  width: 300px;
  background-color: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  padding: 16px;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 8px;
}

.setting-item {
  margin-bottom: 16px;
}

.setting-item label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: bold;
}

.theme-options, .font-options, .toggle-group {
  display: flex;
  gap: 8px;
}

.theme-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.theme-btn.active {
  border-color: var(--accent-color);
}

.theme-light { background: #fff; color: #333; }
.theme-sepia { background: #f4ecd8; color: #5c4b37; }
.theme-dark { background: #2d3748; color: #fff; }

.option-btn {
  flex: 1;
  padding: 6px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: inherit;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.option-btn.active {
  background-color: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.stepper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stepper button {
  width: 30px;
  height: 30px;
  border: 1px solid var(--border-color);
  background: transparent;
  cursor: pointer;
  color: inherit;
}

/* 底部栏 */
.bottom-bar {
  height: 50px;
  background-color: var(--bg-panel);
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  transition: transform 0.3s ease;
}

.bottom-bar.hidden {
  transform: translateY(100%);
}

.progress-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 20px;
}

.slider-container {
  flex: 1;
  height: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.slider-track {
  width: 100%;
  height: 4px;
  background-color: rgba(0,0,0,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.slider-fill {
  height: 100%;
  background-color: var(--accent-color);
}

.btn-page {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  color: inherit;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 动画 */
.slide-left-enter-active, .slide-left-leave-active {
  transition: transform 0.3s;
}
.slide-left-enter-from, .slide-left-leave-to {
  transform: translateX(-100%);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.reader-paragraph {
  margin-bottom: 1em;
  cursor: pointer;
  transition: color 0.3s, background-color 0.3s;
  padding: 4px;
  border-radius: 4px;
}

.reader-paragraph:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.reader-paragraph.active {
  color: #d32f2f; /* 高亮颜色 */
  background-color: rgba(211, 47, 47, 0.1);
  font-weight: bold;
}

/* 暗黑模式适配 */
.theme-dark .reader-paragraph.active {
  color: #ff8a80;
  background-color: rgba(255, 138, 128, 0.1);
}

.theme-dark .reader-paragraph:hover {
  background-color: rgba(255, 255, 255, 0.05);
}
</style>
