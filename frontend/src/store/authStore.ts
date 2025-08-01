import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { type User } from '../types/auth';
import authService from '../services/authService';
import userService from '../services/userService';

interface AuthStore {
  // State
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (usernameOrEmail: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, code: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  updateProfile: (data: any) => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (usernameOrEmail: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.login(usernameOrEmail, password);
          const { user, access_token, refresh_token } = response;

          // 保存token到localStorage
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || '登录失败',
          });
          throw error;
        }
      },

      register: async (username: string, email: string, password: string, code: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.register(username, email, password, code);
          const { user, access_token, refresh_token } = response;

          // 保存token到localStorage
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || '注册失败',
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await authService.logout();
        } catch (error) {
          console.warn('Logout error:', error);
        } finally {
          // 清除所有状态
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          
          // 如果没有选择记住我，也清除保存的凭据
          const rememberMe = localStorage.getItem('remember_me') === 'true';
          if (!rememberMe) {
            localStorage.removeItem('saved_username');
            localStorage.removeItem('saved_password');
            localStorage.removeItem('remember_me');
          }
          
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        try {
          const response = await authService.refreshToken(refreshToken);
          const { access_token } = response;

          localStorage.setItem('access_token', access_token);
          set({ accessToken: access_token });
        } catch (error) {
          // 刷新失败，清除认证状态
          get().logout();
          throw error;
        }
      },

      updateProfile: async (data: any) => {
        set({ isLoading: true, error: null });
        try {
          const updatedUser = await userService.updateProfile(data);
          set({
            user: updatedUser,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || '更新资料失败',
          });
          throw error;
        }
      },

      checkAuth: async () => {
        const { accessToken } = get();
        if (!accessToken) {
          return;
        }

        set({ isLoading: true });
        try {
          const user = await userService.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          // 认证失败，清除状态
          get().logout();
        }
      },

      clearError: () => {
        set({ error: null });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// 选择器函数
export const useAuth = () => {
  const store = useAuthStore();
  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    error: store.error,
    login: store.login,
    register: store.register,
    logout: store.logout,
    updateProfile: store.updateProfile,
    checkAuth: store.checkAuth,
    clearError: store.clearError,
  };
};

// 用户信息选择器
export const useUser = () => {
  return useAuthStore((state) => state.user);
};

// 认证状态选择器
export const useIsAuthenticated = () => {
  return useAuthStore((state) => state.isAuthenticated);
};

// 加载状态选择器
export const useAuthLoading = () => {
  return useAuthStore((state) => state.isLoading);
};

// 错误状态选择器
export const useAuthError = () => {
  return useAuthStore((state) => state.error);
};