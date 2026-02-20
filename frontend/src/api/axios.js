import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

// Add request interceptor to include token in every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    console.log('Axios interceptor - Token from localStorage:', token ? 'EXISTS' : 'MISSING')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('Authorization header set')
    } else {
      console.warn('No token found in localStorage!')
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
