import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/add',
            name: 'trip_add',
            component: () => import('../views/TripAdd.vue'),
        },
        {
            path: '/trip/:id',
            name: 'trip_view',
            component: () => import('../views/TripView.vue'),
            props: true,
        },
        {
            path: '/trip/:id/edit',
            name: 'trip_edit',
            component: () => import('../views/TripEdit.vue'),
            props: true,
        },
        {
            path: '/user/:id',
            name: 'user',
            component: () => import('../views/UserView.vue'),
            props: true,
        },
        {
            path: '/user/:id/area/:area_name/todos',
            name: 'user_area_view',
            component: () => import('../views/UserAreaView.vue'),
            props: true,
        },
    ],
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return new Promise((resolve, reject) => {
                setTimeout(() => {
                    resolve(savedPosition)
                }, 250)
            })
        } else {
            return { top: 0 }
        }
    },
})

export default router
