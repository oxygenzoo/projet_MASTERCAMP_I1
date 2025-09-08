import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Contact from '../views/Contact.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import DashboardUser from '../views/DashboardUser.vue'
import DashboardMairie from '../views/DashboardMairie.vue'
import DashboardAdmin from '../views/DashboardAdmin.vue'
import Competition from '../views/Competition.vue'
import DashboardAccess from '../views/DashboardAccess.vue'
import AnalyseDetails from '../views/AnalyseDetails.vue'

const routes = [
  { path: '/dashboard', name:'DashboardAccess', component: DashboardAccess},
  { path: '/competition', name: 'Competition', component: Competition},
  { path: '/', name: 'Home', component: Home },
  { path: '/about', name: 'About', component: About },
  { path: '/contact', name: 'Contact', component: Contact },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/user', name: 'UserDashboard', component: DashboardUser },
  { path: '/mairie', name: 'MairieDashboard', component: DashboardMairie },
  { path: '/admin', name: 'AdminDashboard', component: DashboardAdmin },
  { path: '/admin/image/:id', name: 'AnalyseDetails', component: AnalyseDetails },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
