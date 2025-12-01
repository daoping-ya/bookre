import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: () => import('@/views/Home.vue')
        },
        {
            path: '/reader/:bookId',
            name: 'reader',
            component: () => import('@/views/Reader.vue'),
            props: true
        },
        {
            path: '/settings',
            name: 'settings',
            component: () => import('@/views/Settings.vue')
        }
    ]
})

export default router
