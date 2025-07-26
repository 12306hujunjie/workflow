import axios, { type AxiosInstance, type AxiosResponse, AxiosError } from 'axios';
import { type ApiResponse, type ApiError } from '../types/auth';

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理token刷新
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // 重试原始请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // 刷新失败，清除token并跳转到登录页
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// API响应处理函数
const handleApiResponse = <T>(response: AxiosResponse<ApiResponse<T>>): T => {
  if (response.data.data !== undefined) {
    return response.data.data;
  }
  return response.data as T;
};

// API错误处理函数
const handleApiError = (error: AxiosError): ApiError => {
  if (error.response?.data) {
    const errorData = error.response.data as any;
    return {
      message: errorData.message || errorData.detail || '请求失败',
      errors: errorData.errors,
      status: error.response.status,
    };
  }
  
  if (error.request) {
    return {
      message: '网络连接失败，请检查网络设置',
      status: 0,
    };
  }
  
  return {
    message: error.message || '未知错误',
  };
};

// 通用API调用函数
export const apiCall = async <T>(
  apiFunction: () => Promise<AxiosResponse<ApiResponse<T>>>
): Promise<T> => {
  try {
    const response = await apiFunction();
    return handleApiResponse(response);
  } catch (error) {
    throw handleApiError(error as AxiosError);
  }
};

// 导出axios实例供其他服务使用
export default apiClient;

// 工具函数
export const setAuthToken = (token: string) => {
  localStorage.setItem('access_token', token);
};

export const removeAuthToken = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export const getAuthToken = () => {
  return localStorage.getItem('access_token');
};

export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp < currentTime;
  } catch {
    return true;
  }
};