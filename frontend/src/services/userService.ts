import apiClient, { apiCall } from './api';
import {
  type User,
  type UserProfile,
  type UpdateProfileRequest,
} from '../types/auth';

class UserService {
  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    return apiCall(() => apiClient.get('/users/me'));
  }

  // 更新用户资料
  async updateProfile(profileData: UpdateProfileRequest): Promise<User> {
    return apiCall(() => apiClient.put('/users/me/profile', profileData));
  }

  // 上传头像
  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData();
    formData.append('avatar', file);
    
    return apiCall(() => apiClient.post('/users/me/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    );
  }

  // 删除头像
  async deleteAvatar(): Promise<void> {
    return apiCall(() => apiClient.delete('/users/me/avatar'));
  }

  // 获取用户登录历史
  async getLoginHistory(page = 1, limit = 20): Promise<{
    items: Array<{
      id: number;
      ip_address: string;
      user_agent: string;
      login_at: string;
      location?: string;
    }>;
    total: number;
    page: number;
    limit: number;
  }> {
    return apiCall(() => 
      apiClient.get(`/users/me/login-history?page=${page}&limit=${limit}`)
    );
  }

  // 获取活跃会话
  async getActiveSessions(): Promise<Array<{
    id: string;
    ip_address: string;
    user_agent: string;
    created_at: string;
    last_activity: string;
    is_current: boolean;
  }>> {
    return apiCall(() => apiClient.get('/auth/me/sessions'));
  }

  // 终止指定会话
  async terminateSession(sessionId: string): Promise<void> {
    return apiCall(() => apiClient.delete(`/auth/me/sessions/${sessionId}`));
  }

  // 终止所有其他会话
  async terminateAllOtherSessions(): Promise<void> {
    return apiCall(() => apiClient.delete('/auth/me/sessions/others'));
  }

  // 验证头像文件
  validateAvatarFile(file: File): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

    // 检查文件大小
    if (file.size > maxSize) {
      errors.push('文件大小不能超过5MB');
    }

    // 检查文件类型
    if (!allowedTypes.includes(file.type)) {
      errors.push('只支持 JPEG、PNG、GIF、WebP 格式的图片');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // 获取支持的时区列表
  getTimezones(): Array<{ value: string; label: string }> {
    return [
      { value: 'UTC', label: 'UTC (协调世界时)' },
      { value: 'Asia/Shanghai', label: 'Asia/Shanghai (北京时间)' },
      { value: 'Asia/Tokyo', label: 'Asia/Tokyo (东京时间)' },
      { value: 'Asia/Seoul', label: 'Asia/Seoul (首尔时间)' },
      { value: 'Asia/Hong_Kong', label: 'Asia/Hong_Kong (香港时间)' },
      { value: 'Asia/Taipei', label: 'Asia/Taipei (台北时间)' },
      { value: 'America/New_York', label: 'America/New_York (纽约时间)' },
      { value: 'America/Los_Angeles', label: 'America/Los_Angeles (洛杉矶时间)' },
      { value: 'America/Chicago', label: 'America/Chicago (芝加哥时间)' },
      { value: 'Europe/London', label: 'Europe/London (伦敦时间)' },
      { value: 'Europe/Paris', label: 'Europe/Paris (巴黎时间)' },
      { value: 'Europe/Berlin', label: 'Europe/Berlin (柏林时间)' },
      { value: 'Australia/Sydney', label: 'Australia/Sydney (悉尼时间)' },
    ];
  }

  // 获取支持的语言列表
  getLanguages(): Array<{ value: string; label: string }> {
    return [
      { value: 'zh-CN', label: '简体中文' },
      { value: 'zh-TW', label: '繁体中文' },
      { value: 'en-US', label: 'English (US)' },
      { value: 'en-GB', label: 'English (UK)' },
      { value: 'ja-JP', label: '日本語' },
      { value: 'ko-KR', label: '한국어' },
      { value: 'fr-FR', label: 'Français' },
      { value: 'de-DE', label: 'Deutsch' },
      { value: 'es-ES', label: 'Español' },
      { value: 'pt-BR', label: 'Português (Brasil)' },
      { value: 'ru-RU', label: 'Русский' },
    ];
  }

  // 格式化用户显示名称
  getDisplayName(user: User): string {
    return user.profile?.display_name || user.username;
  }

  // 获取用户头像URL
  getAvatarUrl(user: User): string | undefined {
    return user.profile?.avatar_url;
  }

  // 格式化用户状态
  formatUserStatus(status: User['status']): {
    label: string;
    color: string;
  } {
    switch (status) {
      case 'active':
        return { label: '活跃', color: 'green' };
      case 'inactive':
        return { label: '非活跃', color: 'orange' };
      case 'banned':
        return { label: '已封禁', color: 'red' };
      default:
        return { label: '未知', color: 'gray' };
    }
  }
}

// 导出单例实例
export const userService = new UserService();
export default userService;