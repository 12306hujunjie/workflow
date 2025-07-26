import React from 'react';
import { Navigate } from 'react-router-dom';
import { Spin } from 'antd';
import { useRequireAuth } from '../../hooks/useAuth';

/**
 * 根路径重定向组件
 * 根据用户认证状态决定重定向到dashboard还是login页面
 */
export const RootRedirect: React.FC = () => {
  const { isAuthenticated, isLoading } = useRequireAuth();

  // 显示加载状态
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spin size="large" />
      </div>
    );
  }

  // 根据认证状态重定向
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  } else {
    return <Navigate to="/auth/login" replace />;
  }
};