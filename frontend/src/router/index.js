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
            path: '/trip/:id',
            name: 'trip',
            component: () => import('../views/TripAuth.vue'),
            props: true,
        },
        {
            path: '/trip/:id/:pin',
            name: 'trip_auth',
            component: () => import('../views/TripView.vue'),
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
