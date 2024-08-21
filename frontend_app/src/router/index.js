import { createRouter, createWebHistory } from 'vue-router'
import MainPage from "@/pages/MainPage";
import LoginPage from "@/pages/LoginPage";
import ProfilePage from "@/pages/ProfilePage";
import MonitoringPage from "@/pages/MonitoringPage";
import MonitoringNodePage from "@/pages/MonitoringNodePage";

const routes = [
  {
    path: '/',
    name: '',
    component: MainPage
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfilePage
  },
  {
    path: '/monitoring',
    name: 'monitoring',
    component: MonitoringPage
  },
  {
    path: '/monitoring/node',
    name: 'monitoringNode',
    component: MonitoringNodePage
  },

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router