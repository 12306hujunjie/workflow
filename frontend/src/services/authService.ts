import apiClient, { apiCall } from './api';
import { validatePasswordForService, getPasswordStrengthLevel } from '../utils/passwordValidation';
import {
  type LoginRequest,
  type LoginResponse,
  type RegisterRequest,
  type RegisterResponse,
  type RefreshTokenRequest,
  type RefreshTokenResponse,
  type ChangePasswordRequest,
  type ForgotPasswordRequest,
  type ResetPasswordRequest,
  type User,
} from '../types/auth';

class AuthService {
  // 用户登录
  async login(usernameOrEmail: string, password: string): Promise<LoginResponse> {
    const loginData: LoginRequest = {
      username_or_email: usernameOrEmail,
      password,
    };
    
    return apiCall(() => apiClient.post('/users/auth/login', loginData));
  }

  // 用户注册（现在需要验证码）
  async register(username: string, email: string, password: string, code: string): Promise<RegisterResponse> {
    return this.registerWithCode(username, email, password, code);
  }

  // 刷新访问令牌
  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    const refreshData: RefreshTokenRequest = {
      refresh_token: refreshToken,
    };
    
    return apiCall(() => apiClient.post('/users/auth/refresh', refreshData));
  }

  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    return apiCall(() => apiClient.get('/users/me'));
  }

  // 修改密码
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    const changePasswordData: ChangePasswordRequest = {
      old_password: currentPassword,
      new_password: newPassword,
    };
    
    return apiCall(() => apiClient.post('/users/me/change-password', changePasswordData));
  }

  // 忘记密码
  async forgotPassword(email: string): Promise<void> {
    const forgotPasswordData: ForgotPasswordRequest = {
      email,
    };
    
    return apiCall(() => apiClient.post('/users/auth/forgot-password', forgotPasswordData));
  }

  // 重置密码
  async resetPassword(token: string, newPassword: string): Promise<void> {
    const resetPasswordData: ResetPasswordRequest = {
      token,
      new_password: newPassword,
    };
    
    return apiCall(() => apiClient.post('/users/auth/reset-password', resetPasswordData));
  }

  // 发送验证码 - 支持 AbortController
  async sendVerificationCode(email: string, purpose: 'register' | 'reset_password', options?: { signal?: AbortSignal }): Promise<void> {
    const sendData = {
      email,
      purpose,
    };
    
    return apiCall(() => apiClient.post('/users/auth/send-verification-code', sendData, {
      signal: options?.signal
    }));
  }

  // 重新发送验证码（别名方法，兼容不同调用方式）
  async resendVerificationCode(email: string, purpose: 'register' | 'reset_password', options?: { signal?: AbortSignal }): Promise<void> {
    return this.sendVerificationCode(email, purpose, options);
  }

  // 用户注册（包含验证码）
  async registerWithCode(username: string, email: string, password: string, code: string): Promise<RegisterResponse> {
    const registerData = {
      username,
      email,
      password,
      code,
    };
    
    return apiCall(() => apiClient.post('/users/auth/register', registerData));
  }

  // 重置密码（包含验证码）
  async resetPasswordWithCode(email: string, code: string, newPassword: string): Promise<void> {
    const resetData = {
      email,
      code,
      new_password: newPassword,
    };
    
    return apiCall(() => apiClient.post('/users/auth/reset-password', resetData));
  }

  // 退出登录
  async logout(): Promise<void> {
    try {
      await apiCall(() => apiClient.post('/users/auth/logout', {}));
    } catch (error) {
      // 即使后端退出失败，也要清除本地token
      console.warn('Backend logout failed:', error);
    } finally {
      // 清除本地存储的token
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  // 检查用户名是否可用
  async checkUsernameAvailability(username: string): Promise<{ available: boolean }> {
    return apiCall(() => apiClient.get(`/users/auth/check-username?username=${encodeURIComponent(username)}`));
  }

  // 检查邮箱是否可用
  async checkEmailAvailability(email: string): Promise<{ available: boolean }> {
    return apiCall(() => apiClient.get(`/users/auth/check-email?email=${encodeURIComponent(email)}`));
  }

  // 验证密码强度（使用统一工具函数，与后端完全一致）
  validatePasswordStrength(password: string): {
    score: number;
    feedback: string[];
    isValid: boolean;
  } {
    return validatePasswordForService(password);
  }

  // 获取密码强度等级（使用统一工具函数）
  getPasswordStrengthLevel(score: number): {
    level: 'weak' | 'fair' | 'good' | 'strong';
    label: string;
    color: string;
  } {
    return getPasswordStrengthLevel(score);
  }
}

// 导出单例实例
export const authService = new AuthService();
export default authService;