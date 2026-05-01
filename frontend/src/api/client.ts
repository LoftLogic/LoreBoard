import axios, { type AxiosError } from 'axios'

/**
 * Axios instance pre-configured for the FastAPI backend.
 * In development the Vite proxy forwards /api → localhost:8000,
 * so VITE_API_URL is only needed for non-local deployments.
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api/v1',
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError<{ detail: string }>) => {
    const message = err.response?.data?.detail ?? err.message
    return Promise.reject(new Error(message))
  },
)
