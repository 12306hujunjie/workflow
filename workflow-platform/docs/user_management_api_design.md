# 用户管理模块 API 设计规范

## 1. 概述

用户管理模块负责处理用户认证、授权、个人信息管理等核心功能。本文档定义了完整的RESTful API设计规范。

### 1.1 设计原则

- **RESTful设计**: 遵循REST架构风格
- **版本控制**: 使用URL路径版本控制 `/api/v1`
- **统一响应**: 标准化的响应格式
- **安全优先**: JWT认证 + 权限控制
- **职责分离**: 认证API与用户管理API分离

### 1.2 API 基础路径

```
基础URL: /api/v1
认证相关: /api/v1/auth
用户管理: /api/v1/users
管理员功能: /api/v1/admin/users
```

## 2. 认证 API (/auth)

### 2.1 用户注册

```http
POST /api/v1/auth/register
```

**请求体:**
```json
{
  "username": "string (3-50字符)",
  "email": "string (邮箱格式)",
  "password": "string (8+字符，包含大小写字母、数字、特殊字符)"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "status": "pending_verification",
      "role": "user",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "profile": null
    }
  },
  "message": "注册成功，请查收验证邮件"
}
```

### 2.2 用户登录

```http
POST /api/v1/auth/login
```

**请求体:**
```json
{
  "username_or_email": "string",
  "password": "string"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "status": "active",
      "role": "user",
      "last_login_at": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "profile": {
        "display_name": "Test User",
        "avatar_url": null,
        "bio": null,
        "timezone": "UTC",
        "language": "zh-CN"
      }
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 1800
  }
}
```

### 2.3 刷新令牌

```http
POST /api/v1/auth/refresh
```

**请求体:**
```json
{
  "refresh_token": "string"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 1800
  }
}
```

### 2.4 用户登出

```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

**请求体:**
```json
{
  "refresh_token": "string (可选)"
}
```

**响应:**
```json
{
  "success": true,
  "message": "登出成功"
}
```

### 2.5 忘记密码

```http
POST /api/v1/auth/forgot-password
```

**请求体:**
```json
{
  "email": "string"
}
```

**响应:**
```json
{
  "success": true,
  "message": "密码重置邮件已发送"
}
```

### 2.6 重置密码

```http
POST /api/v1/auth/reset-password
```

**请求体:**
```json
{
  "token": "string (重置令牌)",
  "new_password": "string"
}
```

**响应:**
```json
{
  "success": true,
  "message": "密码重置成功"
}
```

### 2.7 邮箱验证

```http
POST /api/v1/auth/verify-email
```

**请求体:**
```json
{
  "token": "string (验证令牌)"
}
```

**响应:**
```json
{
  "success": true,
  "message": "邮箱验证成功"
}
```

## 3. 用户管理 API (/users)

### 3.1 获取当前用户信息

```http
GET /api/v1/users/me
Authorization: Bearer {access_token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "status": "active",
    "role": "user",
    "last_login_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "profile": {
      "display_name": "Test User",
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
}
```

### 3.2 更新用户资料

```http
PUT /api/v1/users/me/profile
Authorization: Bearer {access_token}
```

**请求体:**
```json
{
  "display_name": "string (可选)",
  "avatar_url": "string (可选)",
  "bio": "string (可选)",
  "timezone": "string (可选)",
  "language": "string (可选)",
  "notification_preferences": {
    "email_notifications": true,
    "push_notifications": false
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "status": "active",
    "role": "user",
    "last_login_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "profile": {
      "display_name": "Updated Name",
      "avatar_url": "https://example.com/new-avatar.jpg",
      "bio": "更新后的个人简介",
      "timezone": "Asia/Shanghai",
      "language": "zh-CN",
      "notification_preferences": {
        "email_notifications": true,
        "push_notifications": false
      }
    }
  },
  "message": "资料更新成功"
}
```

### 3.3 修改密码

```http
POST /api/v1/users/me/change-password
Authorization: Bearer {access_token}
```

**请求体:**
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

**响应:**
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

### 3.4 更新邮箱

```http
POST /api/v1/users/me/change-email
Authorization: Bearer {access_token}
```

**请求体:**
```json
{
  "new_email": "string",
  "password": "string (当前密码确认)"
}
```

**响应:**
```json
{
  "success": true,
  "message": "邮箱更新请求已发送，请查收验证邮件"
}
```

### 3.5 获取用户会话列表

```http
GET /api/v1/users/me/sessions
Authorization: Bearer {access_token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "session_id_1",
        "device_info": "Chrome on Windows",
        "ip_address": "192.168.1.1",
        "location": "北京, 中国",
        "created_at": "2024-01-01T00:00:00Z",
        "last_activity": "2024-01-01T12:00:00Z",
        "is_current": true
      }
    ],
    "total": 1
  }
}
```

### 3.6 撤销用户会话

```http
DELETE /api/v1/users/me/sessions/{session_id}
Authorization: Bearer {access_token}
```

**响应:**
```json
{
  "success": true,
  "message": "会话已撤销"
}
```

### 3.7 获取登录历史

```http
GET /api/v1/users/me/login-history
Authorization: Bearer {access_token}
```

**查询参数:**
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 20, 最大: 100)
- `start_date`: 开始日期 (ISO 8601格式)
- `end_date`: 结束日期 (ISO 8601格式)

**响应:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "location": "北京, 中国",
        "success": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20,
    "total_pages": 3
  }
}
```

### 3.8 删除账户

```http
DELETE /api/v1/users/me
Authorization: Bearer {access_token}
```

**请求体:**
```json
{
  "password": "string (当前密码确认)",
  "confirmation": "DELETE_MY_ACCOUNT"
}
```

**响应:**
```json
{
  "success": true,
  "message": "账户删除成功"
}
```

## 4. 管理员 API (/admin/users)

> 需要管理员权限 (role: admin)

### 4.1 获取用户列表

```http
GET /api/v1/admin/users
Authorization: Bearer {admin_access_token}
```

**查询参数:**
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 20, 最大: 100)
- `search`: 搜索关键词 (用户名、邮箱)
- `status`: 用户状态筛选
- `role`: 用户角色筛选
- `sort_by`: 排序字段 (created_at, updated_at, last_login_at)
- `sort_order`: 排序方向 (asc, desc)

**响应:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "status": "active",
        "role": "user",
        "last_login_at": "2024-01-01T00:00:00Z",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "profile": {
          "display_name": "Test User",
          "avatar_url": null
        }
      }
    ],
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5
  }
}
```

### 4.2 获取用户详情

```http
GET /api/v1/admin/users/{user_id}
Authorization: Bearer {admin_access_token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "status": "active",
    "role": "user",
    "last_login_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "profile": {
      "display_name": "Test User",
      "avatar_url": "https://example.com/avatar.jpg",
      "bio": "用户简介",
      "timezone": "Asia/Shanghai",
      "language": "zh-CN"
    },
    "statistics": {
      "login_count": 50,
      "last_login_ip": "192.168.1.1",
      "registration_ip": "192.168.1.1"
    }
  }
}
```

### 4.3 更新用户状态

```http
PATCH /api/v1/admin/users/{user_id}/status
Authorization: Bearer {admin_access_token}
```

**请求体:**
```json
{
  "status": "active|inactive|suspended|banned",
  "reason": "string (可选，状态变更原因)"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "testuser",
    "status": "suspended",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "message": "用户状态更新成功"
}
```

### 4.4 更新用户角色

```http
PATCH /api/v1/admin/users/{user_id}/role
Authorization: Bearer {admin_access_token}
```

**请求体:**
```json
{
  "role": "user|admin|moderator"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "testuser",
    "role": "moderator",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "message": "用户角色更新成功"
}
```

### 4.5 重置用户密码

```http
POST /api/v1/admin/users/{user_id}/reset-password
Authorization: Bearer {admin_access_token}
```

**请求体:**
```json
{
  "new_password": "string (可选，不提供则生成随机密码)",
  "send_email": true
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "temporary_password": "TempPass123!" // 仅当send_email为false时返回
  },
  "message": "密码重置成功"
}
```

### 4.6 获取用户会话列表

```http
GET /api/v1/admin/users/{user_id}/sessions
Authorization: Bearer {admin_access_token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "session_id_1",
        "device_info": "Chrome on Windows",
        "ip_address": "192.168.1.1",
        "location": "北京, 中国",
        "created_at": "2024-01-01T00:00:00Z",
        "last_activity": "2024-01-01T12:00:00Z"
      }
    ],
    "total": 3
  }
}
```

### 4.7 撤销用户会话

```http
DELETE /api/v1/admin/users/{user_id}/sessions/{session_id}
Authorization: Bearer {admin_access_token}
```

**响应:**
```json
{
  "success": true,
  "message": "用户会话已撤销"
}
```

### 4.8 撤销用户所有会话

```http
DELETE /api/v1/admin/users/{user_id}/sessions
Authorization: Bearer {admin_access_token}
```

**响应:**
```json
{
  "success": true,
  "message": "用户所有会话已撤销"
}
```

## 5. 统一响应格式

### 5.1 成功响应

```json
{
  "success": true,
  "data": {}, // 响应数据
  "message": "string (可选)" // 成功消息
}
```

### 5.2 错误响应

```json
{
  "success": false,
  "error": "ERROR_CODE", // 错误代码
  "message": "string", // 错误消息
  "details": {} // 详细错误信息 (可选)
}
```

### 5.3 分页响应

```json
{
  "success": true,
  "data": {
    "items": [], // 数据列表
    "total": 100, // 总数量
    "page": 1, // 当前页码
    "per_page": 20, // 每页数量
    "total_pages": 5 // 总页数
  }
}
```

## 6. 错误代码定义

### 6.1 认证相关错误

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `INVALID_CREDENTIALS` | 401 | 用户名或密码错误 |
| `ACCOUNT_NOT_VERIFIED` | 401 | 账户未验证 |
| `ACCOUNT_SUSPENDED` | 401 | 账户已暂停 |
| `ACCOUNT_BANNED` | 401 | 账户已封禁 |
| `TOKEN_EXPIRED` | 401 | 令牌已过期 |
| `TOKEN_INVALID` | 401 | 令牌无效 |
| `INSUFFICIENT_PERMISSIONS` | 403 | 权限不足 |

### 6.2 验证相关错误

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `VALIDATION_ERROR` | 400 | 请求参数验证失败 |
| `USERNAME_TAKEN` | 400 | 用户名已被占用 |
| `EMAIL_TAKEN` | 400 | 邮箱已被注册 |
| `WEAK_PASSWORD` | 400 | 密码强度不足 |
| `INVALID_EMAIL_FORMAT` | 400 | 邮箱格式无效 |

### 6.3 资源相关错误

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `USER_NOT_FOUND` | 404 | 用户不存在 |
| `SESSION_NOT_FOUND` | 404 | 会话不存在 |
| `RESOURCE_NOT_FOUND` | 404 | 资源不存在 |

### 6.4 系统相关错误

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `INTERNAL_SERVER_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务不可用 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |

## 7. 安全考虑

### 7.1 认证安全

- **JWT令牌**: 使用HS256算法签名
- **令牌过期**: 访问令牌30分钟，刷新令牌7天
- **令牌撤销**: 支持令牌黑名单机制
- **密码加密**: 使用bcrypt加密，rounds=12

### 7.2 API安全

- **HTTPS**: 生产环境强制使用HTTPS
- **CORS**: 配置允许的源域名
- **速率限制**: 防止API滥用
- **输入验证**: 严格验证所有输入参数

### 7.3 数据安全

- **敏感信息**: 密码、令牌等敏感信息不记录到日志
- **数据脱敏**: 日志中的邮箱、IP等信息进行脱敏
- **审计日志**: 记录重要操作的审计日志

## 8. 实现建议

### 8.1 API路由组织

建议将认证相关API独立为 `auth_routes.py`，与用户管理API分离：

```python
# auth_routes.py - 认证相关API
router = APIRouter(prefix="/auth", tags=["authentication"])

# user_routes.py - 用户管理API  
router = APIRouter(prefix="/users", tags=["users"])

# admin_routes.py - 管理员API
router = APIRouter(prefix="/admin/users", tags=["admin"])
```

### 8.2 权限控制

```python
# 权限装饰器
@require_permission("admin")
async def admin_only_endpoint():
    pass

@require_permission("user")
async def user_endpoint():
    pass
```

### 8.3 响应格式统一

```python
# 统一响应格式化
class APIResponse:
    @staticmethod
    def success(data=None, message=None):
        return {"success": True, "data": data, "message": message}
    
    @staticmethod
    def error(error_code, message, details=None):
        return {"success": False, "error": error_code, "message": message, "details": details}
```

### 8.4 异常处理

```python
# 自定义异常
class UserManagementException(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code

# 全局异常处理器
@app.exception_handler(UserManagementException)
async def user_management_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(exc.error_code, exc.message)
    )
```

## 9. 测试建议

### 9.1 单元测试

- 测试所有API端点
- 测试各种错误场景
- 测试权限控制
- 测试输入验证

### 9.2 集成测试

- 测试完整的用户注册登录流程
- 测试令牌刷新机制
- 测试管理员功能
- 测试并发访问

### 9.3 安全测试

- 测试SQL注入防护
- 测试XSS防护
- 测试CSRF防护
- 测试权限绕过

---

本文档将随着项目发展持续更新，确保API设计的一致性和完整性。