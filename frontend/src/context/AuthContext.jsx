import { createContext, useState, useContext, useEffect } from 'react'
import api from '../api/axios'

const AuthContext = createContext()

export const useAuth = () => useContext(AuthContext)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    try {
      const params = new URLSearchParams()
      params.append('username', email)   // MUST be username
      params.append('password', password)

      const response = await api.post(
        '/auth/login',
        params,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      )

      const { access_token } = response.data

      localStorage.setItem('token', access_token)
      setToken(access_token)

      return response.data

    } catch (error) {
      throw error
    }
  }

  const register = async (name, email, password) => {
    const response = await api.post('/auth/register', {
      name,
      email,
      password
    })
    return response.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{ user, token, login, register, logout, loading }}
    >
      {children}
    </AuthContext.Provider>
  )
}
