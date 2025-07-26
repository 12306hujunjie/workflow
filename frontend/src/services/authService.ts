import apiClient, { apiCall } from './api';
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
    
    return apiCall(() => apiClient.post('/auth/login', loginData));
  }

  // 用户注册
  async register(username: string, email: string, password: string): Promise<RegisterResponse> {
    const registerData: RegisterRequest = {
      username,
      email,
      password,
    };
    
    return apiCall(() => apiClient.post('/auth/register', registerData));
  }

  // 刷新访问令牌
  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    const refreshData: RefreshTokenRequest = {
      refresh_token: refreshToken,
    };
    
    return apiCall(() => apiClient.post('/auth/refresh', refreshData));
  }

  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    return apiCall(() => apiClient.get('/users/me'));
  }

  // 修改密码
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    const changePasswordData: ChangePasswordRequest = {
      current_password: currentPassword,
      new_password: newPassword,
    };
    
    return apiCall(() => apiClient.post('/users/me/change-password', changePasswordData));
  }

  // 忘记密码
  async forgotPassword(email: string): Promise<void> {
    const forgotPasswordData: ForgotPasswordRequest = {
      email,
    };
    
    return apiCall(() => apiClient.post('/auth/forgot-password', forgotPasswordData));
  }

  // 重置密码
  async resetPassword(token: string, newPassword: string): Promise<void> {
    const resetPasswordData: ResetPasswordRequest = {
      token,
      new_password: newPassword,
    };
    
    return apiCall(() => apiClient.post('/auth/reset-password', resetPasswordData));
  }

  // 退出登录
  async logout(): Promise<void> {
    try {
      await apiCall(() => apiClient.post('/auth/logout'));
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
    return apiCall(() => apiClient.get(`/auth/check-username?username=${encodeURIComponent(username)}`));
  }

  // 检查邮箱是否可用
  async checkEmailAvailability(email: string): Promise<{ available: boolean }> {
    return apiCall(() => apiClient.get(`/auth/check-email?email=${encodeURIComponent(email)}`));
  }

  // 验证密码强度
  validatePasswordStrength(password: string): {
    score: number;
    feedback: string[];
    isValid: boolean;
  } {
    const feedback: string[] = [];
    let score = 0;

    // 长度检查
    if (password.length >= 8) {
      score += 1;
    } else {
      feedback.push('密码至少需要8个字符');
    }

    // 大写字母
    if (/[A-Z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('需要包含大写字母');
    }

    // 小写字母
    if (/[a-z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('需要包含小写字母');
    }

    // 数字
    if (/\d/.test(password)) {
      score += 1;
    } else {
      feedback.push('需要包含数字');
    }

    // 特殊字符
    if (/[^\w\s]/.test(password)) {
      score += 1;
    } else {
      feedback.push('需要包含特殊字符');
    }

    return {
      score,
      feedback,
      isValid: score >= 4,
    };
  }

  // 获取密码强度等级
  getPasswordStrengthLevel(score: number): {
    level: 'weak' | 'fair' | 'good' | 'strong';
    label: string;
    color: string;
  } {
    if (score <= 2) {
      return { level: 'weak', label: '弱', color: '#ef4444' };
    } else if (score === 3) {
      return { level: 'fair', label: '一般', color: '#f59e0b' };
    } else if (score === 4) {
      return { level: 'good', label: '良好', color: '#10b981' };
    } else {
      return { level: 'strong', label: '强', color: '#059669' };
    }
  }
}

// 导出单例实例
export const authService = new AuthService();
export default authService;