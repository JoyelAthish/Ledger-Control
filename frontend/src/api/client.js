import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
})

// ---- Dashboard ----
export const getDashboard = () => api.get('/api/dashboard').then((r) => r.data)

// ---- Exceptions ----
export const getExceptions = (params) =>
  api
    .get('/api/exceptions', {
      params,
      paramsSerializer: { indexes: null }, // repeat array params as risk=A&risk=B
    })
    .then((r) => r.data)

export const getExceptionDetail = (orderId) =>
  api.get(`/api/exceptions/${encodeURIComponent(orderId)}`).then((r) => r.data)

export const resolveException = (orderId, forceRegenerate = false) =>
  api
    .post(`/api/exceptions/${encodeURIComponent(orderId)}/resolve`, {
      force_regenerate: forceRegenerate,
    })
    .then((r) => r.data)

export const regenerateException = (orderId) =>
  api.post(`/api/exceptions/${encodeURIComponent(orderId)}/regenerate`).then((r) => r.data)

export const approveException = (orderId) =>
  api.post(`/api/exceptions/${encodeURIComponent(orderId)}/approve`).then((r) => r.data)

// ---- Analytics ----
export const getAnalytics = () => api.get('/api/analytics').then((r) => r.data)

// ---- Transactions ----
export const getTransactions = (source, params) =>
  api.get(`/api/transactions/${source}`, { params }).then((r) => r.data)

// ---- System ----
export const getHealth = () => api.get('/api/health').then((r) => r.data)
export const getCacheStats = () => api.get('/api/cache').then((r) => r.data)
export const clearCache = () => api.delete('/api/cache').then((r) => r.data)
