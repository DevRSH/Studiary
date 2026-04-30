/**
 * Studiary API Client — Tarea 4.4 del Sprint 0.
 *
 * Axios instance with JWT interceptors, base URL from env,
 * and automatic 401 redirect to /login.
 */

import axios, { type AxiosError, type AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const AUTH_TOKEN_KEY = 'studiary_auth_token';

class ApiClient {
  private readonly client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: { 'Content-Type': 'application/json' },
      timeout: 10_000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request — attach Bearer token if present
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem(AUTH_TOKEN_KEY);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: unknown) => Promise.reject(error)
    );

    // Response — handle global 401
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem(AUTH_TOKEN_KEY);
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  public getInstance(): AxiosInstance {
    return this.client;
  }
}

export const apiClient = new ApiClient().getInstance();
export { AUTH_TOKEN_KEY };
