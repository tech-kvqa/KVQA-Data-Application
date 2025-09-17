import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import AdminDashboard from '../components/AdminDashboard.vue';
import Dashboard from '../components/Dashboard.vue';
import Register from '../views/Register.vue';
import GeneratedFiles from '../components/GeneratedFiles.vue';
import QMSDashboard from '../components/QMSDashboard.vue';
import EMSDashboard from '../components/EMSDashboard.vue';
import AdminFiles from '../components/AdminFiles.vue';
import OshasDashboard from '../components/OshasDashboard.vue';

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/admin_dashboard', name: 'AdminDashboard', component: AdminDashboard},
  { path: '/dashboard', name: 'Dashboard', component: Dashboard},
  { path: '/qms_dashboard', name: 'QMSDashboard', component: QMSDashboard},
  { path: '/ems_dashboard', name: 'EMSDashboard', component: EMSDashboard},
  { path: '/oshas_dashboard', name: 'OshasDashboard', component: OshasDashboard },
  { path: '/generated_files', name: 'GeneratedFiles', component: GeneratedFiles },
  { path: '/admin_files', name: 'AdminFiles', component: AdminFiles }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
