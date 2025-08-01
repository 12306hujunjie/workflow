# API Documentation

> **重要**: API文档已整合到综合指南中，请查看最新文档获取完整信息。

## 📚 文档导航

### 主要文档
- **[API和部署指南](../API_AND_DEPLOYMENT_GUIDE.md)** - 🔥 **推荐** 完整的API文档、架构设计和部署指南
- [用户模块API](../user-module-api.md) - 用户认证和管理API（简化版）

### 专项文档
- [邮箱验证码API指南](./VERIFICATION_CODE_API_GUIDE.md) - 验证码系统详细说明
- [API验证流程文档](./API_VERIFICATION_FLOW_DOCS.md) - 验证流程设计文档

## 🚀 快速开始

### API基础信息
- **Base URL**: `http://localhost:8001/api/v1`
- **认证方式**: Bearer Token (JWT)
- **内容类型**: `application/json`

### 核心API端点

#### 用户认证
```bash
# 用户登录
POST /users/auth/login

# 用户注册
POST /users/auth/register

# 刷新令牌
POST /users/auth/refresh

# 用户登出
POST /users/auth/logout
```

#### 用户管理
```bash
# 获取当前用户信息
GET /users/me

# 更新用户资料
PUT /users/me/profile

# 修改密码
POST /users/me/change-password
```

#### 验证码系统
```bash
# 发送验证码
POST /users/auth/send-verification-code

# 重置密码
POST /users/auth/reset-password
```

### 示例请求

```bash
# 用户登录
curl -X POST http://localhost:8001/api/v1/users/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "user@example.com",
    "password": "password123"
  }'

# 获取用户信息
curl -X GET http://localhost:8001/api/v1/users/me \
  -H "Authorization: Bearer <your_token>"
```

## 📖 详细文档

如需查看完整的API文档、架构设计、部署指南和示例代码，请访问：

**👉 [API和部署指南](../API_AND_DEPLOYMENT_GUIDE.md)**

该文档包含：
- 🏛️ 完整的系统架构设计
- 🔌 详细的API端点说明
- 🚀 生产环境部署指南
- 🐳 Docker容器化部署
- ☸️ Kubernetes部署配置
- 📊 监控和日志管理
- 🔒 安全配置最佳实践
- 🛠️ 故障排除指南
- 💻 完整的示例代码
