# 验证码API使用指南

## 🎉 系统升级完成

验证码邮件系统已成功升级，现在支持**6位数字验证码**，替代了原来的链接验证方式。

---

## 📧 邮件格式变更

### ✅ 新格式（验证码邮件）
- **邮件标题**: "邮箱验证码 - 智能工作流管理平台" / "密码重置验证码 - 智能工作流管理平台"
- **验证方式**: 6位数字验证码 (如: 123456)
- **有效期**: 5分钟
- **使用次数**: 一次性使用
- **存储方式**: Redis存储，自动过期删除

### ❌ 旧格式（已弃用但保持兼容）
- **邮件标题**: 包含验证链接
- **验证方式**: URL链接点击
- **有效期**: 24小时（注册）/ 1小时（重置密码）

---

## 🔧 API接口更新

### 1. 用户注册 `/register`
**行为变化**: 注册成功后自动发送验证码邮件

```http
POST /api/v1/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "545512690@qq.com",
  "password": "Test123!@#"
}
```

**响应**:
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "545512690@qq.com",
    "status": "PENDING_VERIFICATION"
  }
}
```

### 2. 新增：邮箱验证码验证 `/verify-email-code`
**用途**: 使用验证码验证邮箱

```http
POST /api/v1/verify-email-code
Content-Type: application/json

{
  "email": "545512690@qq.com",
  "code": "123456"
}
```

**响应**:
```json
{
  "success": true,
  "message": "邮箱验证成功"
}
```

### 3. 忘记密码 `/forgot-password`
**行为变化**: 现在发送验证码邮件而非重置链接

```http
POST /api/v1/forgot-password
Content-Type: application/json

{
  "email": "545512690@qq.com"
}
```

**响应**:
```json
{
  "success": true,
  "message": "重置密码验证码已发送，请查收"
}
```

### 4. 新增：验证码重置密码 `/reset-password-code`
**用途**: 使用验证码重置密码

```http
POST /api/v1/reset-password-code
Content-Type: application/json

{
  "email": "545512690@qq.com",
  "code": "654321",
  "new_password": "NewPass123!@#"
}
```

**响应**:
```json
{
  "success": true,
  "message": "密码重置成功"
}
```

### 5. 新增：重新发送验证码 `/resend-verification-code`
**用途**: 重新发送验证码（会覆盖旧的验证码）

```http
POST /api/v1/resend-verification-code
Content-Type: application/json

{
  "email": "545512690@qq.com",
  "purpose": "register"  // 或 "reset_password"
}
```

**响应**:
```json
{
  "success": true,
  "message": "验证码已重新发送，请查收"
}
```

---

## 🔄 兼容性说明

### 保持兼容的旧接口
以下接口仍然可用，但建议迁移到新的验证码方式：

- `POST /verify-email` - 使用token验证邮箱
- `POST /reset-password` - 使用token重置密码
- `POST /resend-verification` - 重新发送验证邮件（需要登录）

### 建议的迁移路径
1. **前端**: 更新UI收集验证码而非处理邮件链接
2. **API调用**: 使用新的 `-code` 后缀接口
3. **用户引导**: 告知用户查收验证码邮件

---

## 📱 前端集成示例

### React 注册流程
```javascript
// 1. 用户注册
const register = async (userData) => {
  const response = await fetch('/api/v1/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  
  if (response.ok) {
    // 显示验证码输入界面
    showVerificationCodeInput(userData.email);
  }
};

// 2. 验证码验证
const verifyCode = async (email, code) => {
  const response = await fetch('/api/v1/verify-email-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code })
  });
  
  if (response.ok) {
    // 验证成功，跳转到登录或主页
    window.location.href = '/login';
  }
};

// 3. 重新发送验证码
const resendCode = async (email) => {
  const response = await fetch('/api/v1/resend-verification-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      email, 
      purpose: 'register' 
    })
  });
};
```

### React 密码重置流程
```javascript
// 1. 请求重置密码
const requestReset = async (email) => {
  const response = await fetch('/api/v1/forgot-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  
  if (response.ok) {
    // 显示验证码和新密码输入界面
    showResetPasswordForm(email);
  }
};

// 2. 验证码重置密码
const resetPasswordWithCode = async (email, code, newPassword) => {
  const response = await fetch('/api/v1/reset-password-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      email, 
      code, 
      new_password: newPassword 
    })
  });
  
  if (response.ok) {
    // 重置成功，跳转到登录页
    window.location.href = '/login';
  }
};
```

---

## 🎨 邮件模板设计

### 邮件特点
- **专业外观**: 品牌标识和统一视觉风格
- **清晰验证码**: 大字体、蓝色、等宽字体显示
- **安全提醒**: 有效期和一次性使用说明
- **响应式设计**: 适配各种邮件客户端
- **双格式支持**: HTML和纯文本版本

### 邮件内容结构
```
智能工作流管理平台
─────────────────────
注册账户验证码

尊敬的 用户名，

您正在注册账户，请使用以下验证码完成注册：

    ┌─────────────┐
    │   123456    │  ← 6位数字验证码
    └─────────────┘

安全提醒：
• 验证码有效期为 5分钟
• 验证码仅可使用 一次
• 请勿向他人泄露验证码

如果您没有进行此操作，请忽略此邮件。

© 2024 智能工作流管理平台
```

---

## 📊 系统特性

### ✅ 验证码特性
- **长度**: 6位数字
- **字符集**: 0-9 数字
- **有效期**: 5分钟
- **存储**: Redis自动过期
- **唯一性**: 每次生成都是随机的
- **覆盖性**: 新验证码会覆盖旧的

### ✅ 安全特性
- **一次性使用**: 验证成功后立即删除
- **自动过期**: 5分钟后自动失效
- **邮箱绑定**: 验证码与特定邮箱和用途绑定
- **防暴力破解**: 可扩展添加频率限制
- **日志记录**: 完整的操作日志

### ✅ 用户体验
- **简单输入**: 只需输入6位数字
- **快速验证**: 无需点击邮件链接
- **重发机制**: 支持重新发送验证码
- **清晰提示**: 详细的错误信息和引导

---

## 🔧 运维配置

### Redis配置
```bash
# 确保Redis正在运行
redis-server

# 验证连接
redis-cli ping
```

### 环境变量
```bash
# 邮件配置（已配置完成）
EMAIL_USE_MOCK=false
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=545512690@qq.com
SMTP_PASSWORD=qaiagzjdrnkrbehf
SMTP_USE_TLS=true
FROM_EMAIL=545512690@qq.com
FROM_NAME=智能工作流管理平台

# Redis配置
REDIS_URL=redis://localhost:6379/0
```

### 监控指标
- 验证码生成成功率
- 邮件发送成功率
- 验证码验证成功率
- 验证码过期率
- 用户完成验证率

---

## 🚀 部署清单

### ✅ 已完成
- [x] 验证码服务实现
- [x] 邮件模板更新
- [x] API接口扩展
- [x] Redis集成
- [x] 真实邮件测试
- [x] 兼容性处理

### 📋 部署步骤
1. **确保Redis运行**: `redis-server`
2. **重启应用服务器**: 应用新的验证码功能
3. **测试邮件发送**: 使用测试脚本验证
4. **更新前端界面**: 集成验证码输入
5. **用户通知**: 告知用户新的验证方式

---

## 📞 技术支持

### 常见问题
1. **验证码收不到**: 检查垃圾邮件文件夹
2. **验证码过期**: 重新发送新的验证码
3. **验证码错误**: 确保输入6位数字
4. **Redis连接失败**: 确认Redis服务状态

### 测试工具
- `test_verification_code_system.py` - 系统功能测试
- `test_real_verification_code.py` - 真实邮件测试

---

**状态**: 🟢 已上线并测试完成  
**更新时间**: 2024-01-XX  
**技术负责**: Claude Code AI