import Vue from 'vue'
import VueRouter from 'vue-router'
import store from './store'

import LoginView from './views/LoginView.vue'
import AdminLayout from './views/admin/AdminLayout.vue'
import AdminUsersView from './views/admin/UsersView.vue'
import AdminPackagesView from './views/admin/PackagesView.vue'
import AdminSubscriptionsView from './views/admin/SubscriptionsView.vue'
import AdminInvoicesView from './views/admin/InvoicesView.vue'

import UserLayout from './views/user/UserLayout.vue'
import UserProfileView from './views/user/ProfileView.vue'
import UserSubscriptionsView from './views/user/SubscriptionsView.vue'
import UserInvoicesView from './views/user/InvoicesView.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', redirect: 'users' },
      { path: 'users', name: 'admin-users', component: AdminUsersView },
      { path: 'packages', name: 'admin-packages', component: AdminPackagesView },
      { path: 'subscriptions', name: 'admin-subscriptions', component: AdminSubscriptionsView },
      { path: 'invoices', name: 'admin-invoices', component: AdminInvoicesView },
    ],
  },
  {
    path: '/user',
    component: UserLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: 'profile' },
      { path: 'profile', name: 'user-profile', component: UserProfileView },
      { path: 'subscriptions', name: 'user-subscriptions', component: UserSubscriptionsView },
      { path: 'invoices', name: 'user-invoices', component: UserInvoicesView },
    ],
  },
  {
    path: '*',
    redirect: (to) => {
      if (store.getters.isAuthenticated) {
        return store.getters.isAdmin ? '/admin/users' : '/user/profile'
      }
      return '/login'
    },
  },
]

const router = new VueRouter({
  mode: 'history',
  routes,
})

router.beforeEach((to, from, next) => {
  const isAuth = store.getters.isAuthenticated
  const isAdmin = store.getters.isAdmin

  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!isAuth) {
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }
    if (to.matched.some((record) => record.meta.requiresAdmin) && !isAdmin) {
      return next('/user/profile')
    }
  }

  if (to.matched.some((record) => record.meta.guestOnly) && isAuth) {
    return next(isAdmin ? '/admin/users' : '/user/profile')
  }

  next()
})

export default router
