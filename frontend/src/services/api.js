import axios from 'axios'

// Dev: Vite proxy handles /api → localhost:5001 (vite.config.js)
// Production: VITE_API_BASE must be set to the deployed backend URL
// e.g. https://atlas-service-desk-api.onrender.com/api
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ---- Requests ----
export const getRequests = (params = {}) =>
  api.get('/requests', { params }).then(r => r.data)

export const getRequest = (id) =>
  api.get(`/requests/${id}`).then(r => r.data)

export const createRequest = (data) =>
  api.post('/requests', data).then(r => r.data)

export const updateRequest = (id, data) =>
  api.patch(`/requests/${id}`, data).then(r => r.data)

export const getDuplicateCandidates = (id) =>
  api.get(`/requests/${id}/duplicates`).then(r => r.data)

export const getPrioritySuggestion = (message) =>
  api.post('/priority-suggestion', { message }).then(r => r.data)

// ---- Technicians ----
export const getTechnicians = () =>
  api.get('/technicians').then(r => r.data)

// ---- Dashboard ----
export const getDashboard = () =>
  api.get('/dashboard').then(r => r.data)
