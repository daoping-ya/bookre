import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

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
            try {
                const res = await axios.get(`${API_BASE}/books`)
                this.books = res.data
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

                return newBook
            } catch (error) {
                console.error('导入书籍失败:', error)
                alert('导入失败: ' + error.message)
                throw error
            } finally {
                this.isLoading = false
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

                // 发送部分更新到后端
                try {
                    await axios.patch(`${API_BASE}/books/${bookId}`, {
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
            } catch (e) {
                console.error('删除书籍失败:', e)
                alert('删除失败: ' + e.message)
            }
        }
    }
})
