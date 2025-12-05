import { defineStore } from 'pinia'
import axios from 'axios'
import { getDeviceId } from '@/utils/device'

const API_BASE = '/api'

export const useBooksStore = defineStore('books', {
    state: () => ({
        books: [],
        currentBook: null,
        isLoading: false
    }),

    getters: {
        getAllBooks: (state) => () => state.books,
        getBookById: (state) => (id) => state.books.find(book => book.id === id)
    },

    actions: {
        // 加载书籍列表 (仅元数据)
        async loadBooks() {
            // 📦 优化：尝试从缓存读取
            const cached = sessionStorage.getItem('books_list')
            const deviceId = getDeviceId()

            if (cached) {
                try {
                    this.books = JSON.parse(cached)
                    console.log('📦 使用缓存的书籍列表，瞬间加载！')
                    return
                } catch (e) {
                    console.warn('缓存解析失败，重新加载', e)
                    sessionStorage.removeItem('books_list')
                }
            }

            // 🌐 从后端加载
            try {
                console.log('🌐 从后端加载书籍列表')
                const res = await axios.get(`${API_BASE}/books?deviceId=${deviceId}`)
                this.books = res.data

                // 💾 保存到缓存
                sessionStorage.setItem('books_list', JSON.stringify(this.books))
                console.log('💾 书籍列表已缓存')
            } catch (error) {
                console.error('加载书籍列表失败:', error)
            }
        },

        // 导入并保存书籍
        async importBook(fileOrPath) {
            this.isLoading = true
            try {
                const formData = new FormData()
                let fileExt = ''
                let filePath = ''

                if (fileOrPath instanceof File) {
                    formData.append('file', fileOrPath)
                    fileExt = fileOrPath.name.split('.').pop().toLowerCase()
                    filePath = fileOrPath.name
                } else {
                    console.warn('Electron路径导入暂不支持')
                    alert('Electron 模式下暂不支持，请使用 Web 模式')
                    return
                }

                let parseResult
                if (fileExt === 'epub') {
                    parseResult = await axios.post(`${API_BASE}/parse/epub`, formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    })
                } else if (fileExt === 'txt') {
                    parseResult = await axios.post(`${API_BASE}/parse/txt`, formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    })
                } else {
                    throw new Error('不支持的文件格式: ' + fileExt)
                }

                const bookData = parseResult.data
                const bookId = Date.now()

                const newBook = {
                    id: bookId,
                    title: bookData.title || filePath,
                    author: bookData.author || '未知作者',
                    filePath: filePath,
                    cover: bookData.cover,
                    format: fileExt,
                    chapters: bookData.chapters || [],
                    totalPages: bookData.total_chapters || (bookData.chapters ? bookData.chapters.length : 0),
                    progress: 0,
                    currentPage: 0,
                    currentChapter: 0,
                    createdAt: new Date().toISOString(),
                    lastReadAt: new Date().toISOString()
                }

                // 保存到后端
                await axios.post(`${API_BASE}/books/save`, newBook)

                // 添加到本地列表
                this.books.unshift(newBook)

                // 🧼 清除缓存，确保数据一致
                sessionStorage.removeItem('books_list')

                // 🪄 如果没有封面，自动尝试从网络匹配（静默执行，不阻塞）
                if (!newBook.cover) {
                    this.autoFetchCover(newBook.id, newBook.title, newBook.author)
                }

                return newBook
            } catch (error) {
                console.error('导入书籍失败:', error)
                alert('导入失败: ' + error.message)
                throw error
            } finally {
                this.isLoading = false
            }
        },

        // 自动匹配网络封面（后台静默执行）
        async autoFetchCover(bookId, title, author) {
            try {
                console.log(`🪄 正在为《${title}》自动搜索封面...`)

                const res = await axios.post(`${API_BASE}/books/${bookId}/cover/auto`)

                if (res.data && res.data.url) {
                    // 更新本地Store中的封面
                    const book = this.books.find(b => b.id === bookId)
                    if (book) {
                        book.cover = `${res.data.url}?t=${Date.now()}`
                        console.log(`✅ 封面匹配成功: ${book.title}`)
                    }

                    // 清除缓存，确保下次加载时获取最新数据
                    sessionStorage.removeItem('books_list')
                }
            } catch (e) {
                // 静默失败，不影响用户体验
                console.warn(`⚠️ 封面自动匹配失败（${title}）:`, e.response?.data?.detail || e.message)
            }
        },

        // 加载书籍完整内容 (章节)
        async fetchBookContent(bookId) {
            // 先检查本地是否已有章节数据
            const existingBook = this.books.find(b => b.id === bookId)
            if (existingBook && existingBook.chapters && existingBook.chapters.length > 0) {
                return existingBook
            }

            this.isLoading = true
            try {
                const res = await axios.get(`${API_BASE}/books/${bookId}`)
                const fullBook = res.data

                // 更新本地 Store
                const index = this.books.findIndex(b => b.id === bookId)
                if (index !== -1) {
                    // 合并数据，保留本地可能的较新状态
                    this.books[index] = { ...this.books[index], ...fullBook }
                } else {
                    this.books.push(fullBook)
                }
                return fullBook
            } catch (error) {
                console.error('加载书籍内容失败:', error)
                throw error
            } finally {
                this.isLoading = false
            }
        },

        // 更新进度 (使用 PATCH)
        async updateProgress(bookId, page, chapter = 0) {
            const book = this.books.find(b => b.id === bookId)
            if (book) {
                book.progress = (page / book.totalPages) * 100
                book.currentPage = page
                book.currentChapter = chapter
                book.lastReadAt = new Date().toISOString()

                const deviceId = getDeviceId()

                // 发送部分更新到后端
                try {
                    await axios.patch(`${API_BASE}/books/${bookId}`, {
                        deviceId: deviceId,
                        progress: book.progress,
                        currentPage: book.currentPage,
                        currentChapter: book.currentChapter,
                        lastReadAt: book.lastReadAt
                    })
                } catch (e) {
                    console.error('保存进度失败:', e)
                }
            }
        },

        async deleteBook(bookId) {
            try {
                await axios.delete(`${API_BASE}/books/${bookId}`)
                this.books = this.books.filter(book => book.id !== bookId)

                // 🧼 清除缓存
                sessionStorage.removeItem('books_list')
            } catch (e) {
                console.error('删除书籍失败:', e)
                alert('删除失败: ' + e.message)
            }
        }
    }
})
