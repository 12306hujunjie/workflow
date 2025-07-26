# 用户模块API文档

## 概述

用户模块提供完整的用户认证、授权和个人资料管理功能，基于JWT令牌的无状态认证机制，支持角色权限控制。

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: Bearer Token (JWT)
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 认证流程

### 1. 用户注册

**端点**: `POST /users/register`

**描述**: 注册新用户账号

**请求体**:
```json
{
  "username": "string",     // 用户名，3-50字符
  "email": "string",        // 邮箱地址
  "password": "string"      // 密码，至少8字符，需包含大小写字母、数字和特殊字符
}
```

**响应示例**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "status": "active",
  "role": "user",
  "last_login_at": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "profile": {
    "display_name": null,
    "avatar_url": null,
    "bio": null,
    "timezone": "UTC",
    "language": "zh-CN",
    "notification_preferences": {}
  }
}
```

**状态码**:
- `201`: 注册成功
- `400`: 请求参数错误或用户名/邮箱已存在
- `500`: 服务器内部错误

### 2. 用户登录

**端点**: `POST /users/login`

**描述**: 用户登录获取访问令牌

**请求体**:
```json
{
  "username_or_email": "string",  // 用户名或邮箱
  "password": "string"             // 密码
}
```

**响应示例**:
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "status": "active",
    "role": "user",
    "last_login_at": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "profile": {
      "display_name": "测试用户",
      "avatar_url": "https://example.com/avatar.jpg",
      "bio": "这是我的个人简介",
      "timezone": "Asia/Shanghai",
      "language": "zh-CN",
      "notification_preferences": {
        "email_notifications": true,
        "push_notifications": false
      }
    }
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

**状态码**:
- `200`: 登录成功
- `401`: 用户名/密码错误或账号被禁用
- `500`: 服务器内部错误

### 3. 刷新令牌

**端点**: `POST /users/refresh`

**描述**: 使用刷新令牌获取新的访问令牌

**请求体**:
```json
{
  "refresh_token": "string"  // 刷新令牌
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

**状态码**:
- `200`: 刷新成功
- `401`: 刷新令牌无效或已过期

## 用户信息管理

### 4. 获取当前用户信息

**端点**: `GET /users/me`

**描述**: 获取当前登录用户的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "status": "active",
  "role": "user",
  "last_login_at": "2024-01-01T12:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "profile": {
    "display_name": "测试用户",
    "avatar_url": "https://example.com/avatar.jpg",
    "bio": "这是我的个人简介",
    "timezone": "Asia/Shanghai",
    "language": "zh-CN",
    "notification_preferences": {
      "email_notifications": true,
      "push_notifications": false
    }
  }
}
```

**状态码**:
- `200`: 获取成功
- `401`: 未认证或令牌无效
- `404`: 用户不存在

### 5. 更新用户资料

**端点**: `PUT /users/me/profile`

**描述**: 更新当前用户的个人资料

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "display_name": "string",           // 显示名称，可选，最大100字符
  "avatar_url": "string",             // 头像URL，可选，最大500字符
  "bio": "string",                    // 个人简介，可选，最大500字符
  "timezone": "string",               // 时区，可选，最大50字符
  "language": "string",               // 语言，可选，最大10字符
  "notification_preferences": {       // 通知偏好，可选
    "email_notifications": true,
    "push_notifications": false,
    "sms_notifications": false
  }
}
```

**响应示例**: 同获取用户信息接口

**状态码**:
- `200`: 更新成功
- `400`: 请求参数错误
- `401`: 未认证或令牌无效

### 6. 修改密码

**端点**: `POST /users/me/change-password`

**描述**: 修改当前用户密码

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "old_password": "string",  // 原密码
  "new_password": "string"   // 新密码，至少8字符，需包含大小写字母、数字和特殊字符
}
```

**响应示例**:
```json
{
  "message": "密码修改成功"
}
```

**状态码**:
- `200`: 修改成功
- `400`: 原密码错误或新密码不符合要求
- `401`: 未认证或令牌无效

## 邮箱验证码

### 7. 发送验证码

**端点**: `POST /auth/send-verification-code`

**描述**: 发送邮箱验证码

**请求体**:
```json
{
  "email": "string",    // 邮箱地址
  "purpose": "string"   // 验证目的: registration, password_reset, email_change, sensitive_operation
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "验证码已发送到您的邮箱",
  "data": {
    "expires_in": 300  // 过期时间（秒）
  },
  "request_id": "req_123456789"
}
```

**错误响应示例**:
```json
{
  "success": false,
  "message": "发送验证码失败",
  "errors": [
    {
      "code": "RATE_LIMIT_EXCEEDED",
      "message": "发送频率过快，请稍后再试",
      "details": {
        "retry_after": 60
      }
    }
  ],
  "request_id": "req_123456789"
}
```

**状态码**:
- `200`: 发送成功
- `400`: 请求参数错误
- `422`: 邮箱格式错误或验证目的无效
- `429`: 发送频率过快
- `500`: 服务器内部错误

### 8. 验证验证码

**端点**: `POST /auth/verify-code`

**描述**: 验证邮箱验证码

**请求体**:
```json
{
  "email": "string",    // 邮箱地址
  "code": "string",     // 6位数字验证码
  "purpose": "string"   // 验证目的，必须与发送时一致
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "验证码验证成功",
  "data": {
    "verified": true,
    "verification_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // 验证成功后的临时令牌
  },
  "request_id": "req_123456789"
}
```

**错误响应示例**:
```json
{
  "success": false,
  "message": "验证码验证失败",
  "errors": [
    {
      "code": "CODE_INVALID",
      "message": "验证码错误",
      "details": {
        "remaining_attempts": 2
      }
    }
  ],
  "request_id": "req_123456789"
}
```

**状态码**:
- `200`: 验证成功
- `400`: 请求参数错误
- `422`: 验证码格式错误或验证失败
- `429`: 验证尝试次数过多
- `500`: 服务器内部错误

## 密码重置

### 9. 忘记密码

**端点**: `POST /users/forgot-password`

**描述**: 发送密码重置邮件（已集成验证码功能）

**请求体**:
```json
{
  "email": "string"  // 注册邮箱
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "如果该邮箱存在，重置密码邮件已发送",
  "data": {
    "expires_in": 300
  },
  "request_id": "req_123456789"
}
```

**状态码**:
- `200`: 邮件发送成功（无论邮箱是否存在都返回成功，防止邮箱枚举）
- `400`: 请求参数错误
- `429`: 发送频率过快

### 10. 重置密码

**端点**: `POST /users/reset-password`

**描述**: 使用验证码重置密码

**请求体**:
```json
{
  "email": "string",           // 邮箱地址
  "code": "string",            // 6位数字验证码
  "new_password": "string"     // 新密码
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "密码重置成功",
  "request_id": "req_123456789"
}
```

**状态码**:
- `200`: 重置成功
- `400`: 验证码无效或已过期，或新密码不符合要求
- `422`: 参数验证失败

## 错误响应格式

所有错误响应都遵循统一格式：

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "错误描述信息",
  "details": {  // 可选，详细错误信息
    "field": "具体字段错误"
  }
}
```

## 常见错误码

### 通用错误码
- `BAD_REQUEST`: 请求参数错误
- `UNAUTHORIZED`: 未认证或认证失败
- `FORBIDDEN`: 权限不足
- `NOT_FOUND`: 资源不存在
- `CONFLICT`: 资源冲突（如用户名已存在）
- `VALIDATION_ERROR`: 数据验证失败
- `INTERNAL_SERVER_ERROR`: 服务器内部错误

### 邮箱验证码错误码
- `RATE_LIMIT_EXCEEDED`: 发送频率过快
- `EMAIL_SEND_FAILED`: 邮件发送失败
- `INVALID_EMAIL_FORMAT`: 邮箱格式无效
- `CODE_NOT_FOUND`: 验证码不存在
- `CODE_EXPIRED`: 验证码已过期
- `CODE_INVALID`: 验证码错误
- `MAX_ATTEMPTS_EXCEEDED`: 验证尝试次数超限
- `REDIS_CONNECTION_ERROR`: Redis连接错误
- `SMTP_CONNECTION_ERROR`: SMTP连接错误

## 认证说明

### JWT令牌结构

访问令牌包含以下信息：
```json
{
  "user_id": 1,
  "username": "testuser",
  "role": "user",
  "type": "access",
  "exp": 1640995200,  // 过期时间戳
  "iat": 1640991600,  // 签发时间戳
  "nbf": 1640991600   // 生效时间戳
}
```

### 令牌使用

1. **访问令牌**: 用于API调用认证，有效期30分钟
2. **刷新令牌**: 用于获取新的访问令牌，有效期7天
3. **令牌传递**: 在请求头中使用 `Authorization: Bearer <token>`

### 安全建议

1. 访问令牌应存储在内存中，不要持久化
2. 刷新令牌可以安全存储（如HttpOnly Cookie）
3. 定期刷新访问令牌以保持会话活跃
4. 登出时清除所有令牌
5. 检测到令牌泄露时立即撤销

## 速率限制

为防止滥用，部分端点实施速率限制：

- **登录**: 每IP每分钟最多5次尝试
- **注册**: 每IP每小时最多3次注册
- **密码重置**: 每邮箱每小时最多1次请求
- **邮箱验证码发送**: 
  - 每邮箱每分钟最多1次
  - 每IP每小时最多10次
  - 系统每分钟最多100次
- **邮箱验证码验证**: 每验证码最多3次尝试
- **其他API**: 每用户每分钟最多100次请求

超出限制时返回 `429 Too Many Requests` 状态码。

## 示例代码

### JavaScript/TypeScript

```typescript
// 用户登录
async function login(usernameOrEmail: string, password: string) {
  const response = await fetch('/api/v1/users/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username_or_email: usernameOrEmail,
      password: password,
    }),
  });
  
  if (response.ok) {
    const data = await response.json();
    // 存储令牌
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  } else {
    throw new Error('登录失败');
  }
}

// 获取用户信息
async function getCurrentUser() {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/api/v1/users/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  if (response.ok) {
    return await response.json();
  } else if (response.status === 401) {
    // 令牌过期，尝试刷新
    await refreshToken();
    return getCurrentUser(); // 重试
  } else {
    throw new Error('获取用户信息失败');
  }
}

// 刷新令牌
async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  const response = await fetch('/api/v1/users/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh_token: refreshToken,
    }),
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data;
  } else {
    // 刷新失败，需要重新登录
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }
}

// 发送验证码
async function sendVerificationCode(email: string, purpose: string) {
  const response = await fetch('/api/v1/auth/send-verification-code', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
      purpose: purpose,
    }),
  });
  
  const data = await response.json();
  if (data.success) {
    return data;
  } else {
    throw new Error(data.message || '发送验证码失败');
  }
}

// 验证验证码
async function verifyCode(email: string, code: string, purpose: string) {
  const response = await fetch('/api/v1/auth/verify-code', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
      code: code,
      purpose: purpose,
    }),
  });
  
  const data = await response.json();
  if (data.success) {
    return data;
  } else {
    throw new Error(data.message || '验证码验证失败');
  }
}

// 使用验证码重置密码
async function resetPasswordWithCode(email: string, code: string, newPassword: string) {
  const response = await fetch('/api/v1/users/reset-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
      code: code,
      new_password: newPassword,
    }),
  });
  
  const data = await response.json();
  if (data.success) {
    return data;
  } else {
    throw new Error(data.message || '密码重置失败');
  }
}
```

### Python

```python
import requests
from typing import Optional, Dict, Any

class UserAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def login(self, username_or_email: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        response = requests.post(
            f"{self.base_url}/users/login",
            json={
                "username_or_email": username_or_email,
                "password": password,
            }
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        return data
    
    def get_current_user(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        if not self.access_token:
            raise ValueError("未登录")
        
        response = requests.get(
            f"{self.base_url}/users/me",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        if response.status_code == 401:
            # 尝试刷新令牌
            self.refresh_access_token()
            return self.get_current_user()  # 重试
        
        response.raise_for_status()
        return response.json()
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """刷新访问令牌"""
        if not self.refresh_token:
            raise ValueError("无刷新令牌")
        
        response = requests.post(
            f"{self.base_url}/users/refresh",
            json={"refresh_token": self.refresh_token}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        return data
    
    def send_verification_code(self, email: str, purpose: str) -> Dict[str, Any]:
        """发送验证码"""
        response = requests.post(
            f"{self.base_url}/auth/send-verification-code",
            json={
                "email": email,
                "purpose": purpose,
            }
        )
        response.raise_for_status()
        return response.json()
    
    def verify_code(self, email: str, code: str, purpose: str) -> Dict[str, Any]:
        """验证验证码"""
        response = requests.post(
            f"{self.base_url}/auth/verify-code",
            json={
                "email": email,
                "code": code,
                "purpose": purpose,
            }
        )
        response.raise_for_status()
        return response.json()
    
    def reset_password_with_code(self, email: str, code: str, new_password: str) -> Dict[str, Any]:
        """使用验证码重置密码"""
        response = requests.post(
            f"{self.base_url}/users/reset-password",
            json={
                "email": email,
                "code": code,
                "new_password": new_password,
            }
        )
        response.raise_for_status()
        return response.json()
```

## 测试

### 使用curl测试

```bash
# 注册用户
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test@123456"
  }'

# 用户登录
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "testuser",
    "password": "Test@123456"
  }'

# 获取用户信息（需要替换实际的token）
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 发送验证码
curl -X POST http://localhost:8000/api/v1/auth/send-verification-code \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "purpose": "registration"
  }'

# 验证验证码
curl -X POST http://localhost:8000/api/v1/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456",
    "purpose": "registration"
  }'

# 使用验证码重置密码
curl -X POST http://localhost:8000/api/v1/users/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456",
    "new_password": "NewPassword@123"
  }'
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基础用户认证功能
- 支持JWT令牌认证
- 实现用户资料管理
- 支持密码重置功能