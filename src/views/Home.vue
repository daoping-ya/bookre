<template>
  <div class="home-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration"></div>

    <!-- 主卡片容器 -->
    <div class="main-card">
      <!-- 顶部栏 -->
      <header class="header">
        <div class="brand">
          <span class="logo-icon">📚</span>
          <h1 class="logo-text">BookRe 阅读器</h1>
          <span class="status-dot" :class="{ online: isBackendOnline }" :title="isBackendOnline ? '服务正常' : '服务离线'"></span>
        </div>
        
        <div class="actions">
          <button @click="triggerFileInput" class="btn-primary">
            <span class="icon">＋</span> 导入书籍
          </button>
          <button @click="goToSettings" class="btn-icon" title="设置">
            ⚙️
          </button>
        </div>
        
        <!-- 隐藏的文件输入 -->
        <input 
          type="file" 
          ref="fileInput" 
          style="display: none" 
          accept=".epub,.txt"
          @change="handleFileSelect"
          multiple
        >
      </header>

      <!-- 内容区域 -->
      <main class="content">
        <div class="section-header">
          <h2>我的书架</h2>
          <span class="book-count">{{ books.length }} 本书</span>
        </div>

        <div v-if="books.length > 0" class="books-grid">
          <div 
            v-for="book in books" 
            :key="book.id"
            class="book-item"
            @click="openBook(book.id)"
          >
            <div class="cover-wrapper">
              <img 
                v-if="book.cover" 
                :src="book.cover" 
                class="cover-img" 
                loading="lazy"
                @error="handleImageError"
              />
              <div v-else class="cover-placeholder" :style="getGradient(book.id)">
                <span class="placeholder-icon">📖</span>
              </div>
              
              <div v-if="book.progress > 0" class="progress-bar">
                <div class="progress-fill" :style="{ width: book.progress + '%' }"></div>
              </div>
              
              <!-- 删除按钮 -->
              <button 
                class="delete-btn" 
                @click.stop="showDeleteConfirm(book)"
                title="删除书籍"
              >
                🗑️
              </button>
            </div>
            
            <div class="book-info">
              <h3 class="book-title">{{ book.title }}</h3>
              <p class="book-author">{{ book.author || '未知作者' }}</p>
              <div class="book-meta">
                <span class="badge">{{ book.format?.toUpperCase() }}</span>
                <span class="read-status" v-if="book.progress > 0">{{ Math.round(book.progress) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-illustration">📚</div>
          <h3>开始您的阅读之旅</h3>
          <p>拖拽文件到这里，或点击右上角导入书籍</p>
          <button @click="triggerFileInput" class="btn-outline">
            立即导入
          </button>
        </div>
      </main>
    </div>

    <!-- 删除确认对话框 -->
    <transition name="modal">
      <div v-if="deleteDialog.show" class="modal-overlay" @click="cancelDelete">
        <div class="modal-card" @click.stop>
          <div class="modal-header">
            <h3>确认删除</h3>
            <button @click="cancelDelete" class="btn-close">×</button>
          </div>
          <div class="modal-body">
            <p>确定要删除《{{ deleteDialog.book?.title }}》吗？</p>
            <p class="warning-text">此操作不可恢复！</p>
          </div>
          <div class="modal-footer">
            <button @click="cancelDelete" class="btn-secondary">取消</button>
            <button @click="confirmDelete" class="btn-danger">确定删除</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBooksStore } from '@/store/books'

const router = useRouter()
const booksStore = useBooksStore()
const books = ref([])
const fileInput = ref(null)
const isBackendOnline = ref(false)

onMounted(async () => {
  checkBackendStatus()
  await booksStore.loadBooks()
  await loadBooks()
})

async function loadBooks() {
  books.value = await booksStore.getAllBooks()
}

async function checkBackendStatus() {
  try {
    const res = await fetch('http://localhost:8000/health')
    isBackendOnline.value = res.ok
  } catch (e) {
    isBackendOnline.value = false
  }
}

function triggerFileInput() {
  if (window.electronAPI) {
    handleElectronImport()
  } else {
    fileInput.value.click()
  }
}

async function handleElectronImport() {
  if (!isBackendOnline.value) {
    alert('请确保后端服务已启动')
    await checkBackendStatus()
    if (!isBackendOnline.value) return
  }
  
  const paths = await window.electronAPI.openFileDialog()
  if (paths && paths.length) {
    for (const p of paths) {
      await booksStore.importBook(p)
    }
    await loadBooks()
  }
}

async function handleFileSelect(e) {
  const files = e.target.files
  if (!files.length) return
  
  try {
    for (const file of files) {
      await booksStore.importBook(file)
    }
    await loadBooks()
    e.target.value = ''
  } catch (err) {
    alert('导入失败: ' + err.message)
  }
}

function openBook(id) {
  router.push({ name: 'reader', params: { bookId: id } })
}

function goToSettings() {
  router.push('/settings')
}

function handleImageError(e) {
  e.target.style.display = 'none'
  e.target.nextElementSibling.style.display = 'flex' // Show placeholder
}

// 生成随机渐变色
function getGradient(id) {
  const gradients = [
    'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
    'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)',
    'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%)',
    'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)'
  ]
  return { background: gradients[id % gradients.length] }
}

// 删除功能
const deleteDialog = ref({
  show: false,
  book: null
})

function showDeleteConfirm(book) {
  deleteDialog.value = {
    show: true,
    book: book
  }
}

function cancelDelete() {
  deleteDialog.value = {
    show: false,
    book: null
  }
}

async function confirmDelete() {
  if (deleteDialog.value.book) {
    await booksStore.deleteBook(deleteDialog.value.book.id)
    await loadBooks()
    cancelDelete()
  }
}
</script>

<style scoped>
.home-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4c1d95 0%, #3b82f6 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰光晕 */
.bg-decoration {
  position: absolute;
  top: -20%;
  left: -10%;
  width: 50%;
  height: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
  border-radius: 50%;
  filter: blur(60px);
  pointer-events: none;
}

.main-card {
  width: 90%;
  max-width: 1200px;
  height: 90vh;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 头部 */
.header {
  padding: 24px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ef4444;
  transition: background-color 0.3s;
}

.status-dot.online {
  background-color: #22c55e;
  box-shadow: 0 0 8px #22c55e;
}

.actions {
  display: flex;
  gap: 16px;
}

.btn-primary {
  background: #6366f1;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.btn-icon:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

/* 内容区 */
.content {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.book-count {
  color: #64748b;
  font-size: 14px;
}

/* 书籍网格 */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 32px;
}

.book-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.book-item:hover {
  transform: translateY(-6px);
}

.cover-wrapper {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
  margin-bottom: 16px;
  position: relative;
  background: #f1f5f9;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  font-size: 48px;
  opacity: 0.5;
  color: white;
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: rgba(0,0,0,0.2);
}

.progress-fill {
  height: 100%;
  background: #22c55e;
}

.book-info {
  padding: 0 4px;
}

.book-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-author {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 8px 0;
}

.book-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badge {
  font-size: 10px;
  padding: 2px 6px;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 4px;
  font-weight: 600;
}

.read-status {
  font-size: 11px;
  color: #64748b;
}

/* 空状态 */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.empty-illustration {
  font-size: 64px;
  margin-bottom: 24px;
  opacity: 0.5;
}

.btn-outline {
  margin-top: 24px;
  padding: 10px 32px;
  border: 2px solid #6366f1;
  color: #6366f1;
  background: transparent;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: #eff6ff;
}

/* 删除按钮 */
.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  color: white;
  font-size: 16px;
  cursor: pointer;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.2s;
  z-index: 10;
}

.book-item:hover .delete-btn {
  opacity: 1;
  transform: scale(1);
}

.delete-btn:hover {
  background: #ef4444;
  transform: scale(1.1);
}

/* 模态对话框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.btn-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.modal-body {
  padding: 24px;
}

.modal-body p {
  margin: 0 0 12px 0;
  color: #475569;
  font-size: 15px;
}

.warning-text {
  color: #ef4444;
  font-weight: 600;
  font-size: 14px !important;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
}

.btn-secondary {
  flex: 1;
  padding: 10px 20px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn-danger {
  flex: 1;
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  background: #ef4444;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* 模态对话框动画 */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-card,
.modal-leave-active .modal-card {
  transition: transform 0.3s;
}

.modal-enter-from .modal-card,
.modal-leave-to .modal-card {
  transform: scale(0.9);
}
</style>
