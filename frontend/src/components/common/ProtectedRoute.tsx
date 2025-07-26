import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useRequireAuth, useCurrentUser } from '../../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

/**
 * 受保护的路由组件
 * 需要用户登录才能访问
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/auth/login',
}) => {
  const { isAuthenticated, isLoading, shouldRedirect } = useRequireAuth();
  const location = useLocation();

  // 显示加载状态
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spin size="large" />
      </div>
    );
  }

  // 未认证时重定向到登录页
  if (shouldRedirect) {
    return (
      <Navigate
        to={redirectTo}
        state={{ from: location }}
        replace
      />
    );
  }

  // 已认证，渲染子组件
  return <>{children}</>;
};

/**
 * 公开路由组件
 * 已登录用户访问时重定向到仪表板
 */
export const PublicRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/dashboard',
}) => {
  const { isAuthenticated, isLoading } = useRequireAuth();

  // 显示加载状态
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spin size="large" />
      </div>
    );
  }

  // 已认证时重定向到仪表板
  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  // 未认证，渲染子组件
  return <>{children}</>;
};

/**
 * 角色保护路由组件
 */
interface RoleProtectedRouteProps extends ProtectedRouteProps {
  requiredRole: string;
  fallbackComponent?: React.ReactNode;
}

export const RoleProtectedRoute: React.FC<RoleProtectedRouteProps> = ({
  children,
  requiredRole,
  fallbackComponent,
  redirectTo = '/unauthorized',
}) => {
  const { isAuthenticated, isLoading } = useRequireAuth();
  const user = useCurrentUser();

  // 显示加载状态
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spin size="large" />
      </div>
    );
  }

  // 未认证时重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  // 检查角色权限
  if (user?.role !== requiredRole) {
    if (fallbackComponent) {
      return <>{fallbackComponent}</>;
    }
    return <Navigate to={redirectTo} replace />;
  }

  // 有权限，渲染子组件
  return <>{children}</>;
};