// 用户相关类型定义
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  avatar?: string;
  is_active: boolean;
  date_joined: string;
  last_login?: string;
  timezone?: string;
  language?: string;
  status: 'active' | 'inactive' | 'banned';
  created_at: string;
  updated_at: string;
  last_login_at?: string;
  profile?: UserProfile;
  role?: string;
  permissions?: string[];
}

export interface UserProfile {
  id: number;
  user_id: number;
  display_name?: string;
  bio?: string;
  avatar_url?: string;
  timezone?: string;
  language?: string;
  created_at: string;
  updated_at: string;
}

// 认证相关类型
export interface LoginRequest {
  username_or_email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface RegisterResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface UpdateProfileRequest {
  display_name?: string;
  avatar_url?: string;
  bio?: string;
  timezone?: string;
  language?: string;
  notification_preferences?: Record<string, any>;
}

// API响应类型
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status?: number;
}

// 表单类型
export interface LoginFormData {
  usernameOrEmail: string;
  password: string;
  rememberMe: boolean;
}

export interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

export interface ChangePasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface ProfileFormData {
  display_name?: string;
  bio?: string;
  timezone?: string;
  language?: string;
}

// 状态类型
export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}