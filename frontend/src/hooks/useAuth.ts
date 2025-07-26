import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { message } from 'antd';

/**
 * 认证相关的自定义hook
 */
export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    updateProfile,
    checkAuth,
    clearError,
  } = useAuthStore();

  // 处理错误消息
  useEffect(() => {
    if (error) {
      message.error(error);
      clearError();
    }
  }, [error, clearError]);

  // 页面加载时检查认证状态
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && !isAuthenticated) {
      checkAuth();
    }
  }, [isAuthenticated, checkAuth]);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    updateProfile,
    checkAuth,
    clearError,
  };
};

/**
 * 需要认证的页面hook
 */
export const useRequireAuth = () => {
  const { isAuthenticated, isLoading } = useAuth();
  
  return {
    isAuthenticated,
    isLoading,
    shouldRedirect: !isLoading && !isAuthenticated,
  };
};

/**
 * 获取当前用户信息
 */
export const useCurrentUser = () => {
  const user = useAuthStore((state) => state.user);
  return user;
};

/**
 * 检查用户权限
 */
export const usePermissions = () => {
  const user = useCurrentUser();
  
  const hasRole = (role: string) => {
    return user?.role === role;
  };
  
  const hasPermission = (permission: string) => {
    // 这里可以根据实际的权限系统来实现
    return user?.permissions?.includes(permission) || false;
  };
  
  const isAdmin = () => {
    return hasRole('admin');
  };
  
  const isModerator = () => {
    return hasRole('moderator') || isAdmin();
  };
  
  return {
    hasRole,
    hasPermission,
    isAdmin,
    isModerator,
  };
};