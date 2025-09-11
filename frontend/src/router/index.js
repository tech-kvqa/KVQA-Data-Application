import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Dashboard from '../components/Dashboard.vue';
import Register from '../views/Register.vue';
import GeneratedFiles from '../components/GeneratedFiles.vue';

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard},
  { path: '/generated_files', name: 'GeneratedFiles', component: GeneratedFiles }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
