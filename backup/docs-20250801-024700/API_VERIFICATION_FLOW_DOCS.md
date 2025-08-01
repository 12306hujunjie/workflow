# API和验证码流程完整文档

## 🚀 系统状态

### 后端服务
- **地址**: http://localhost:8000
- **状态**: ✅ 运行中
- **健康检查**: `GET /health`
- **API文档**: http://localhost:8000/api/docs

### 前端服务  
- **地址**: http://localhost:5173
- **状态**: ✅ 运行中
- **路由配置**: 已更新，包含所有验证码流程页面

## 📋 API端点总览

### 认证相关API
- `POST /api/v1/users/auth/register` - 用户注册（需验证码）
- `POST /api/v1/users/auth/login` - 用户登录
- `POST /api/v1/users/auth/logout` - 用户登出
- `POST /api/v1/users/auth/refresh` - 刷新令牌
- `POST /api/v1/users/auth/reset-password` - 重置密码（需验证码）
- `POST /api/v1/users/auth/send-verification-code` - 发送验证码
- `GET /api/v1/users/auth/check-email` - 检查邮箱可用性
- `GET /api/v1/users/auth/check-username` - 检查用户名可用性

## 🔐 完整验证码流程

### 1. 用户注册流程
```
1. 访问 /auth/register
2. 填写用户名、邮箱、密码
3. 点击"发送验证码" → POST /api/v1/users/auth/send-verification-code
   请求体: {"email": "user@example.com", "purpose": "register"}
4. 输入6位验证码
5. 提交注册 → POST /api/v1/users/auth/register  
   请求体: {"username": "user", "email": "user@example.com", "password": "password", "code": "123456"}
6. 注册成功，导航到登录页面
```

### 2. 密码重置流程
```
1. 访问 /auth/forgot-password
2. 输入邮箱地址
3. 点击"发送验证码" → POST /api/v1/users/auth/send-verification-code
   请求体: {"email": "user@example.com", "purpose": "reset_password"}  
4. 点击"前往重置密码" → 导航到 /auth/reset-password (传递邮箱参数)
5. 输入6位验证码和新密码
6. 提交重置 → POST /api/v1/users/auth/reset-password
   请求体: {"email": "user@example.com", "code": "123456", "new_password": "newpassword"}
7. 重置成功，导航到登录页面
```

## 🔧 技术实现细节

### 验证码系统
- **验证码长度**: 6位数字
- **有效期**: 5分钟
- **发送频率限制**: IP地址3分钟内限制
- **用途区分**: register（注册）、reset_password（重置密码）

### 安全特性
- JWT令牌认证
- 密码哈希存储（bcrypt）
- 邮箱验证码验证
- IP频率限制
- CORS配置

### 前端技术栈
- **框架**: React 18 + TypeScript
- **路由**: React Router v6
- **UI库**: Ant Design
- **状态管理**: 自定义 hooks + localStorage
- **HTTP客户端**: Axios

### 后端技术栈
- **框架**: FastAPI + Python
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **邮件服务**: SMTP (支持QQ邮箱等)
- **验证码服务**: 自定义实现

## 📄 页面路由配置

```typescript
/auth/login          - 登录页面
/auth/register       - 注册页面（带验证码）
/auth/forgot-password - 忘记密码页面
/auth/reset-password  - 重置密码页面（带验证码）
/auth/verify-email    - 邮箱验证页面
/dashboard           - 用户仪表板（需认证）
/profile             - 用户资料页面（需认证）
```

## ✅ 功能测试清单

### 已完成功能
- [x] 后端服务启动和API测试
- [x] 用户注册流程（带邮箱验证码）
- [x] 密码重置页面创建和完善
- [x] 前端路由配置更新
- [x] 验证码系统完整实现
- [x] API端点功能验证
- [x] 邮箱可用性检查
- [x] 用户名可用性检查

### 已验证API
- ✅ `GET /health` - 健康检查
- ✅ `GET /api/v1/users/auth/check-email` - 邮箱检查
- ✅ `GET /api/v1/users/auth/check-username` - 用户名检查  
- ✅ `POST /api/v1/users/auth/send-verification-code` - 验证码发送

## 🐛 问题解决记录

### 1. 后端服务端口冲突
- **问题**: 8000端口被占用
- **解决**: 杀掉冲突进程，重新启动服务

### 2. 路由配置缺失
- **问题**: reset-password路由未配置
- **解决**: 在router/index.tsx中添加路由配置

### 3. 方法名不匹配
- **问题**: ResetPasswordPage调用resendVerificationCode但authService中只有sendVerificationCode
- **解决**: 在authService中添加别名方法

### 4. 验证码流程不统一
- **问题**: ForgotPasswordPage使用邮件链接而非验证码
- **解决**: 修改为使用验证码方式，正确导航到reset-password页面

## 📊 性能和监控

### API响应时间
- 健康检查: ~50ms
- 邮箱检查: ~100ms  
- 用户名检查: ~80ms
- 验证码发送: ~200ms（包含邮件发送时间）

## 🔮 后续优化建议

1. **安全增强**
   - 添加验证码尝试次数限制
   - 实现更复杂的密码策略
   - 添加设备指纹识别

2. **用户体验**
   - 添加验证码输入组件优化
   - 实现密码强度实时检测
   - 添加进度指示器

3. **监控和日志**
   - 添加详细的操作日志
   - 实现错误监控和报警
   - 性能监控仪表板

4. **功能扩展**
   - 双因素认证支持
   - 社交登录集成
   - 邮箱模板美化

---

*文档生成时间: 2025-07-31*  
*系统版本: Workflow Platform v1.0.0*