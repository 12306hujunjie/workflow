# 用户模块API文档

> **注意**: 本文档已整合到 [API和部署指南](./API_AND_DEPLOYMENT_GUIDE.md) 中。建议查看最新的综合文档获取完整的API信息和部署指导。

## 快速导航

- [完整API和部署指南](./API_AND_DEPLOYMENT_GUIDE.md) - 包含所有API端点、架构设计和部署说明
- [用户认证API](#用户认证api) - 用户注册、登录、令牌管理
- [用户信息管理API](#用户信息管理api) - 个人资料、密码管理
- [邮箱验证码API](#邮箱验证码api) - 验证码发送和验证

## 基础信息

- **Base URL**: `http://localhost:8001/api/v1`
- **认证方式**: Bearer Token (JWT)
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## 用户认证API

### 用户注册
**端点**: `POST /users/auth/register`

**请求体**:
```json
{
  "username": "string",
  "email": "string", 
  "password": "string",
  "verification_code": "string"
}
```

### 用户登录
**端点**: `POST /users/auth/login`

**请求体**:
```json
{
  "username_or_email": "string",
  "password": "string"
}
```

### 刷新令牌
**端点**: `POST /users/auth/refresh`

**请求体**:
```json
{
  "refresh_token": "string"
}
```

### 用户登出
**端点**: `POST /users/auth/logout`

**请求头**: `Authorization: Bearer <token>`

## 用户信息管理API

### 获取当前用户信息
**端点**: `GET /users/me`

**请求头**: `Authorization: Bearer <token>`

### 更新用户资料
**端点**: `PUT /users/me/profile`

**请求头**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "display_name": "string",
  "avatar_url": "string",
  "bio": "string",
  "timezone": "string",
  "language": "string"
}
```

### 修改密码
**端点**: `POST /users/me/change-password`

**请求头**: `Authorization: Bearer <token>`

**请求体**:
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

## 邮箱验证码API

### 发送验证码
**端点**: `POST /users/auth/send-verification-code`

**请求体**:
```json
{
  "email": "string",
  "purpose": "registration|password_reset|email_change"
}
```

### 检查用户名可用性
**端点**: `GET /users/auth/check-username?username=<username>`

### 检查邮箱可用性
**端点**: `GET /users/auth/check-email?email=<email>`

### 重置密码
**端点**: `POST /users/auth/reset-password`

**请求体**:
```json
{
  "email": "string",
  "verification_code": "string",
  "new_password": "string"
}
```

## 管理员API

### 获取用户列表
**端点**: `GET /users/admin/users`

**请求头**: `Authorization: Bearer <admin_token>`

### 更新用户状态
**端点**: `PUT /users/admin/users/{user_id}/status`

**请求头**: `Authorization: Bearer <admin_token>`

## 公开端点

### 公开发送验证码
**端点**: `POST /users/public/send-verification-code`

**请求体**:
```json
{
  "email": "string",
  "purpose": "string"
}
```

### 公开登出
**端点**: `POST /users/public/logout`

## 错误响应格式

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "错误描述信息",
  "details": {},
  "request_id": "req_123456789",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 常见错误码

- `UNAUTHORIZED`: 未认证或认证失败
- `FORBIDDEN`: 权限不足
- `VALIDATION_ERROR`: 数据验证失败
- `RATE_LIMIT_EXCEEDED`: 请求频率过快
- `USER_NOT_FOUND`: 用户不存在
- `EMAIL_ALREADY_EXISTS`: 邮箱已存在
- `USERNAME_ALREADY_EXISTS`: 用户名已存在
- `INVALID_CREDENTIALS`: 用户名或密码错误
- `CODE_INVALID`: 验证码错误
- `CODE_EXPIRED`: 验证码已过期

## 安全特性

- JWT令牌认证（访问令牌30分钟，刷新令牌7天）
- 令牌黑名单机制
- 密码强度验证
- 邮箱验证码验证
- API频率限制
- IP地址限制

## 速率限制

- **登录**: 每IP每分钟最多5次
- **注册**: 每IP每小时最多3次
- **验证码发送**: 每邮箱每分钟最多1次
- **验证码验证**: 每验证码最多3次尝试
- **其他API**: 每用户每分钟最多100次

---

**完整文档**: 请查看 [API和部署指南](./API_AND_DEPLOYMENT_GUIDE.md) 获取详细的API文档、架构设计、部署指南和示例代码。