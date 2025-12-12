import { defineStore } from 'pinia'
import axios from 'axios'
import { getDeviceId } from '@/utils/device'
import { IS_MOBILE, IS_PRODUCTION, MOBILE_CONFIG } from '@/utils/mobile'

const API_BASE = '/api'

// 📱 智能缓存管理（防止手机端内存溢出）
function safeSetSessionStorage(key, data) {
    try {
        const jsonStr = JSON.stringify(data)
        const sizeInBytes = new Blob([jsonStr]).size

        // 超过限制则不缓存（手机端1MB，PC端5MB）
        if (sizeInBytes > MOBILE_CONFIG.MAX_CACHE_SIZE) {
            console.warn(`⚠️ 缓存过大 (${(sizeInBytes / 1024).toFixed(0)}KB)，跳过存储以保护内存`)
            sessionStorage.removeItem(key)  // 删除旧缓存
            return false
        }

        sessionStorage.setItem(key, jsonStr)
        return true
    } catch (e) {
        console.error('缓存写入失败:', e)
        sessionStorage.clear()  // 清空所有缓存避免死循环
        return false
    }
}

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
                    let cachedBooks = JSON.parse(cached)

                    // 🛡️ 自愈逻辑：去重
                    // 如果缓存中存在 ID 重复的书籍，只保留一本
                    const uniqueBooks = []
                    const seenIds = new Set()
                    for (const book of cachedBooks) {
                        if (!seenIds.has(book.id)) {
                            seenIds.add(book.id)
                            uniqueBooks.push(book)
                        }
                    }

                    if (uniqueBooks.length !== cachedBooks.length) {
                        console.warn(`🧹 自动清理了 ${cachedBooks.length - uniqueBooks.length} 本重复书籍`)
                        safeSetSessionStorage('books_list', uniqueBooks)
                    }

                    this.books = uniqueBooks
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

                // 💾 保存到缓存（移动端优化：限制大小）
                safeSetSessionStorage('books_list', this.books)
                console.log('💾 书籍列表已缓存')
            } catch (error) {
                console.error('加载书籍列表失败:', error)
            }
        },

        /**
         * 快速上传书籍 (懒解析模式)
         * @param {File} file - 上传的文件
         * @param {Function} onProgress - 进度回调 (0-100)
         * @returns {Object} - { book_id, title, author, cover, total_chapters }
         */
        async uploadBook(file, onProgress = null) {
            const formData = new FormData()
            formData.append('file', file)

            try {
                const response = await axios.post(`${API_BASE}/books/upload`, formData, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                    onUploadProgress: (progressEvent) => {
                        if (onProgress && progressEvent.total) {
                            const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100)
                            onProgress(percent)
                        }
                    }
                })

                // 清除缓存，确保刷新
                sessionStorage.removeItem('books_list')

                console.log('✅ 上传成功:', response.data)
                return response.data

            } catch (error) {
                console.error('上传失败:', error)
                throw error
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
            this.isLoading = true
            try {
                // ⚠️ 强制从后端获取最新状态 (包括进度)，不再信任本地缓存的老旧进度
                // const existingBook = this.books.find(b => b.id === bookId)
                // if (existingBook && existingBook.chapters && existingBook.chapters.length > 0) {
                //    return existingBook
                // }

                const res = await axios.get(`${API_BASE}/books/${bookId}`)
                const remoteBook = res.data

                // 更新本地 Store
                // ⚠️ 使用弱类型比较 (==)，因为 URL 参数可能是 string，store 中可能是 number
                const index = this.books.findIndex(b => b.id == bookId)
                if (index !== -1) {
                    const localBook = this.books[index]

                    // 🧠 智能合并：保留本地已加载的章节内容 (content)，更新其他元数据
                    if (localBook.chapters && remoteBook.chapters) {
                        remoteBook.chapters = remoteBook.chapters.map((remoteChap, idx) => {
                            const localChap = localBook.chapters[idx]
                            // 如果本地有内容且 title/id 一致，保留内容
                            if (localChap && localChap.content && !localChap.content.includes('正在加载')) {
                                return { ...remoteChap, content: localChap.content }
                            }
                            return remoteChap
                        })
                    }

                    this.books[index] = { ...localBook, ...remoteBook }
                } else {
                    this.books.push(remoteBook)
                }

                // 立即更新缓存，确保最新状态被持久化（移动端优化）
                try {
                    safeSetSessionStorage('books_list', this.books)
                } catch (e) {/* ignore */ }

                return this.books[index !== -1 ? index : this.books.length - 1]
            } catch (error) {
                console.error('加载书籍内容失败:', error)
                throw error
            } finally {
                this.isLoading = false
            }
        },

        /**
         * 获取单章节内容 (按需加载)
         * 用于懒解析模式下获取章节内容
         */
        async fetchChapter(bookId, chapterIndex) {
            try {
                const res = await axios.get(`${API_BASE}/books/${bookId}/chapter/${chapterIndex}`)
                return res.data
            } catch (error) {
                console.error(`加载章节 ${chapterIndex} 失败:`, error)
                return null
            }
        },

        // 🔧 更新进度（彻底重构，修复类型匹配问题）
        async updateProgress(bookId, page, chapter = 0, relativePage = 0, scrollPercentage = 0) {
            console.log(`📝 updateProgress 被调用: bookId=${bookId}(${typeof bookId}), page=${page}, chapter=${chapter}, relativePage=${relativePage}`)
            console.log(`📚 当前books列表:`, this.books.map(b => ({ id: b.id, idType: typeof b.id, title: b.title })))

            // ⚠️ 使用弱类型比较（==）而不是严格相等（===），避免 string vs number 问题
            const book = this.books.find(b => b.id == bookId)
            if (!book) {
                console.error(`❌ 找不到书籍 ID=${bookId}，updateProgress 失败！`)
                return { success: false, location: 'none' }
            }

            console.log(`✅ 找到书籍: ${book.title}`)

            // 乐观更新本地状态
            book.progress = (page / (book.totalPages || 1)) * 100
            book.currentPage = page
            book.currentChapter = chapter

            // 关键：保存相对位置，解决懒加载导致的页码变化问题
            book.readingPosition = {
                chapterIndex: chapter,
                relativePageIndex: relativePage,
                scrollPercentage: scrollPercentage
            }

            book.lastReadAt = new Date().toISOString()

            const deviceId = getDeviceId()
            console.log(`🔐 使用设备ID: ${deviceId}`)

            // 尝试云端同步
            try {
                console.log(`☁️ 发起云端同步请求...`)
                const response = await axios.patch(`${API_BASE}/books/${bookId}`, {
                    deviceId: deviceId,
                    progress: book.progress,
                    currentPage: book.currentPage,
                    currentChapter: book.currentChapter,
                    lastReadAt: book.lastReadAt,
                    // 同步扩展数据
                    readingPosition: book.readingPosition
                }, {
                    timeout: 5000
                })

                console.log(`☁️ 云端同步响应:`, response.data)

                // 💾 同步更新 sessionStorage 缓存，防止刷新后回退（移动端优化）
                try {
                    safeSetSessionStorage('books_list', this.books)
                    console.log('💾 阅读进度已更新到本地缓存')
                } catch (e) {
                    console.warn('缓存更新失败', e)
                }

                console.log('✅ 进度已同步到云端')
                return {
                    success: true,
                    location: 'cloud',
                    savedTo: response.data?.savedTo || 'cloud'
                }

            } catch (e) {
                // 云端失败时仅本地保存，不影响用户体验
                console.warn('⚠️ 云端同步失败，已保存到本地:', e.message)
                return {
                    success: true,  // 本地已更新，算成功
                    location: 'local',
                    error: e.message
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
