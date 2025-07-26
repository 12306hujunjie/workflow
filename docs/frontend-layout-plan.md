# 前端布局设计计划

## 概述

基于用户模块API设计现代化、响应式的前端界面，采用组件化架构，提供优秀的用户体验。设计遵循Material Design 3.0和现代Web设计原则。

## 技术栈选型

### 核心框架
- **React 18+** / **Vue 3+** / **Angular 15+** - 主流前端框架任选
- **TypeScript** - 类型安全和更好的开发体验
- **Vite** / **Webpack** - 现代化构建工具

### UI组件库
- **Ant Design** / **Material-UI** / **Element Plus** - 企业级UI组件
- **Tailwind CSS** - 原子化CSS框架
- **Styled Components** / **Emotion** - CSS-in-JS解决方案

### 状态管理
- **Redux Toolkit** / **Zustand** / **Pinia** - 全局状态管理
- **React Query** / **SWR** - 服务端状态管理
- **Formik** / **React Hook Form** - 表单状态管理

### 路由和认证
- **React Router** / **Vue Router** / **Angular Router** - 客户端路由
- **JWT** - 令牌认证
- **Route Guards** - 路由守卫

## 整体布局架构

### 1. 应用结构

```
src/
├── components/           # 通用组件
│   ├── common/          # 基础组件
│   ├── forms/           # 表单组件
│   ├── layout/          # 布局组件
│   └── ui/              # UI组件
├── pages/               # 页面组件
│   ├── auth/            # 认证相关页面
│   ├── dashboard/       # 仪表板
│   ├── profile/         # 用户资料
│   └── settings/        # 设置页面
├── hooks/               # 自定义Hooks
├── services/            # API服务
├── store/               # 状态管理
├── utils/               # 工具函数
├── types/               # TypeScript类型定义
└── styles/              # 样式文件
```

### 2. 主布局设计

#### 2.1 应用外壳 (App Shell)

```typescript
// Layout组件结构
interface AppLayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
  showHeader?: boolean;
}

const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  showSidebar = true,
  showHeader = true
}) => {
  return (
    <div className="app-layout">
      {showHeader && <Header />}
      <div className="app-content">
        {showSidebar && <Sidebar />}
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};
```

#### 2.2 响应式设计

```scss
// 响应式断点
$breakpoints: (
  mobile: 320px,
  tablet: 768px,
  desktop: 1024px,
  wide: 1440px
);

// 布局网格
.app-layout {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 100vh;
  
  .app-content {
    display: grid;
    grid-template-columns: 280px 1fr;
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
}
```

## 用户认证模块设计

### 1. 登录页面 (Login Page)

#### 1.1 页面布局

```typescript
interface LoginPageProps {}

const LoginPage: React.FC<LoginPageProps> = () => {
  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <Logo />
          <h1>欢迎回来</h1>
          <p>登录您的账户以继续使用服务</p>
        </div>
        
        <LoginForm />
        
        <div className="auth-footer">
          <Link to="/register">还没有账户？立即注册</Link>
          <Link to="/forgot-password">忘记密码？</Link>
        </div>
      </div>
      
      <div className="auth-background">
        <IllustrationComponent />
      </div>
    </div>
  );
};
```

#### 1.2 登录表单组件

```typescript
interface LoginFormData {
  usernameOrEmail: string;
  password: string;
  rememberMe: boolean;
}

const LoginForm: React.FC = () => {
  const [form] = Form.useForm<LoginFormData>();
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  
  const handleSubmit = async (values: LoginFormData) => {
    setLoading(true);
    try {
      await login(values.usernameOrEmail, values.password);
      // 登录成功后重定向
    } catch (error) {
      // 错误处理
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      className="login-form"
    >
      <Form.Item
        name="usernameOrEmail"
        label="用户名或邮箱"
        rules={[
          { required: true, message: '请输入用户名或邮箱' },
          { min: 3, message: '至少3个字符' }
        ]}
      >
        <Input
          prefix={<UserOutlined />}
          placeholder="请输入用户名或邮箱"
          size="large"
        />
      </Form.Item>
      
      <Form.Item
        name="password"
        label="密码"
        rules={[
          { required: true, message: '请输入密码' }
        ]}
      >
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="请输入密码"
          size="large"
        />
      </Form.Item>
      
      <Form.Item name="rememberMe" valuePropName="checked">
        <Checkbox>记住我</Checkbox>
      </Form.Item>
      
      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          loading={loading}
          size="large"
          block
        >
          登录
        </Button>
      </Form.Item>
    </Form>
  );
};
```

### 2. 注册页面 (Register Page)

#### 2.1 注册表单设计

```typescript
interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

const RegisterForm: React.FC = () => {
  const [form] = Form.useForm<RegisterFormData>();
  const [passwordStrength, setPasswordStrength] = useState(0);
  
  const validatePassword = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^\w\s]/.test(password)) strength++;
    return strength;
  };
  
  return (
    <Form form={form} layout="vertical" className="register-form">
      <Form.Item
        name="username"
        label="用户名"
        rules={[
          { required: true, message: '请输入用户名' },
          { min: 3, max: 50, message: '用户名长度为3-50个字符' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '只能包含字母、数字和下划线' }
        ]}
      >
        <Input
          prefix={<UserOutlined />}
          placeholder="请输入用户名"
          size="large"
        />
      </Form.Item>
      
      <Form.Item
        name="email"
        label="邮箱地址"
        rules={[
          { required: true, message: '请输入邮箱地址' },
          { type: 'email', message: '请输入有效的邮箱地址' }
        ]}
      >
        <Input
          prefix={<MailOutlined />}
          placeholder="请输入邮箱地址"
          size="large"
        />
      </Form.Item>
      
      <Form.Item
        name="password"
        label="密码"
        rules={[
          { required: true, message: '请输入密码' },
          { min: 8, message: '密码至少8个字符' },
          {
            validator: (_, value) => {
              const strength = validatePassword(value || '');
              if (strength < 4) {
                return Promise.reject('密码强度不够，需包含大小写字母、数字和特殊字符');
              }
              return Promise.resolve();
            }
          }
        ]}
      >
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="请输入密码"
          size="large"
          onChange={(e) => setPasswordStrength(validatePassword(e.target.value))}
        />
      </Form.Item>
      
      <PasswordStrengthIndicator strength={passwordStrength} />
      
      <Form.Item
        name="confirmPassword"
        label="确认密码"
        dependencies={['password']}
        rules={[
          { required: true, message: '请确认密码' },
          ({ getFieldValue }) => ({
            validator(_, value) {
              if (!value || getFieldValue('password') === value) {
                return Promise.resolve();
              }
              return Promise.reject('两次输入的密码不一致');
            },
          }),
        ]}
      >
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="请再次输入密码"
          size="large"
        />
      </Form.Item>
      
      <Form.Item
        name="agreeToTerms"
        valuePropName="checked"
        rules={[
          {
            validator: (_, value) =>
              value ? Promise.resolve() : Promise.reject('请同意服务条款'),
          },
        ]}
      >
        <Checkbox>
          我已阅读并同意 <Link to="/terms">服务条款</Link> 和 <Link to="/privacy">隐私政策</Link>
        </Checkbox>
      </Form.Item>
      
      <Form.Item>
        <Button type="primary" htmlType="submit" size="large" block>
          注册账户
        </Button>
      </Form.Item>
    </Form>
  );
};
```

### 3. 密码重置流程

#### 3.1 忘记密码页面

```typescript
const ForgotPasswordPage: React.FC = () => {
  const [step, setStep] = useState<'email' | 'sent'>('email');
  const [email, setEmail] = useState('');
  
  if (step === 'sent') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="success-message">
            <CheckCircleOutlined className="success-icon" />
            <h2>邮件已发送</h2>
            <p>我们已向 {email} 发送了密码重置链接</p>
            <p>请检查您的邮箱（包括垃圾邮件文件夹）</p>
            <Button type="link" onClick={() => setStep('email')}>
              使用其他邮箱
            </Button>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>重置密码</h1>
          <p>输入您的邮箱地址，我们将发送重置链接</p>
        </div>
        
        <ForgotPasswordForm
          onSuccess={(email) => {
            setEmail(email);
            setStep('sent');
          }}
        />
        
        <div className="auth-footer">
          <Link to="/login">返回登录</Link>
        </div>
      </div>
    </div>
  );
};
```

## 用户资料管理模块

### 1. 用户资料页面

#### 1.1 页面布局

```typescript
const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('basic');
  
  return (
    <div className="profile-page">
      <div className="profile-header">
        <div className="profile-avatar">
          <Avatar
            size={120}
            src={user?.profile?.avatar_url}
            icon={<UserOutlined />}
          />
          <Button type="link" className="change-avatar-btn">
            更换头像
          </Button>
        </div>
        
        <div className="profile-info">
          <h1>{user?.profile?.display_name || user?.username}</h1>
          <p className="profile-email">{user?.email}</p>
          <Tag color={user?.status === 'active' ? 'green' : 'red'}>
            {user?.status === 'active' ? '活跃' : '非活跃'}
          </Tag>
        </div>
      </div>
      
      <div className="profile-content">
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'basic',
              label: '基本信息',
              children: <BasicInfoForm />
            },
            {
              key: 'security',
              label: '安全设置',
              children: <SecuritySettings />
            },
            {
              key: 'notifications',
              label: '通知设置',
              children: <NotificationSettings />
            },
            {
              key: 'privacy',
              label: '隐私设置',
              children: <PrivacySettings />
            }
          ]}
        />
      </div>
    </div>
  );
};
```

#### 1.2 基本信息表单

```typescript
const BasicInfoForm: React.FC = () => {
  const { user, updateProfile } = useAuth();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    if (user?.profile) {
      form.setFieldsValue({
        display_name: user.profile.display_name,
        bio: user.profile.bio,
        timezone: user.profile.timezone,
        language: user.profile.language
      });
    }
  }, [user, form]);
  
  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      await updateProfile(values);
      message.success('资料更新成功');
    } catch (error) {
      message.error('更新失败，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      className="basic-info-form"
    >
      <Row gutter={24}>
        <Col span={12}>
          <Form.Item
            name="display_name"
            label="显示名称"
            rules={[
              { max: 100, message: '显示名称不能超过100个字符' }
            ]}
          >
            <Input placeholder="请输入显示名称" />
          </Form.Item>
        </Col>
        
        <Col span={12}>
          <Form.Item
            name="timezone"
            label="时区"
          >
            <Select
              placeholder="选择时区"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={[
                { value: 'UTC', label: 'UTC (协调世界时)' },
                { value: 'Asia/Shanghai', label: 'Asia/Shanghai (北京时间)' },
                { value: 'America/New_York', label: 'America/New_York (纽约时间)' },
                // 更多时区选项...
              ]}
            />
          </Select>
        </Form.Item>
        </Col>
      </Row>
      
      <Form.Item
        name="bio"
        label="个人简介"
        rules={[
          { max: 500, message: '个人简介不能超过500个字符' }
        ]}
      >
        <Input.TextArea
          rows={4}
          placeholder="介绍一下自己吧..."
          showCount
          maxLength={500}
        />
      </Form.Item>
      
      <Form.Item
        name="language"
        label="语言偏好"
      >
        <Select
          placeholder="选择语言"
          options={[
            { value: 'zh-CN', label: '简体中文' },
            { value: 'zh-TW', label: '繁体中文' },
            { value: 'en-US', label: 'English' },
            { value: 'ja-JP', label: '日本語' },
            { value: 'ko-KR', label: '한국어' }
          ]}
        />
      </Form.Item>
      
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading}>
          保存更改
        </Button>
      </Form.Item>
    </Form>
  );
};
```

### 2. 安全设置

```typescript
const SecuritySettings: React.FC = () => {
  return (
    <div className="security-settings">
      <Card title="密码设置" className="setting-card">
        <ChangePasswordForm />
      </Card>
      
      <Card title="登录会话" className="setting-card">
        <SessionManagement />
      </Card>
      
      <Card title="两步验证" className="setting-card">
        <TwoFactorAuth />
      </Card>
      
      <Card title="登录历史" className="setting-card">
        <LoginHistory />
      </Card>
    </div>
  );
};
```

## 通用组件设计

### 1. 头部导航 (Header)

```typescript
const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [notificationCount, setNotificationCount] = useState(0);
  
  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        <Link to="/profile">个人资料</Link>
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        <Link to="/settings">设置</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={logout}>
        退出登录
      </Menu.Item>
    </Menu>
  );
  
  return (
    <Header className="app-header">
      <div className="header-left">
        <Logo />
        <Navigation />
      </div>
      
      <div className="header-right">
        <Space size="middle">
          <Badge count={notificationCount}>
            <Button
              type="text"
              icon={<BellOutlined />}
              onClick={() => {/* 打开通知面板 */}}
            />
          </Badge>
          
          <Dropdown overlay={userMenu} placement="bottomRight">
            <div className="user-dropdown">
              <Avatar
                size="small"
                src={user?.profile?.avatar_url}
                icon={<UserOutlined />}
              />
              <span className="username">{user?.username}</span>
              <DownOutlined />
            </div>
          </Dropdown>
        </Space>
      </div>
    </Header>
  );
};
```

### 2. 侧边栏导航 (Sidebar)

```typescript
const Sidebar: React.FC = () => {
  const location = useLocation();
  const { user } = useAuth();
  
  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表板',
    },
    {
      key: '/xiaohongshu',
      icon: <InstagramOutlined />,
      label: '小红书',
      children: [
        { key: '/xiaohongshu/accounts', label: '账号管理' },
        { key: '/xiaohongshu/content', label: '内容采集' },
        { key: '/xiaohongshu/analytics', label: '数据分析' },
      ]
    },
    {
      key: '/qidian',
      icon: <BookOutlined />,
      label: '起点',
      children: [
        { key: '/qidian/novels', label: '小说监控' },
        { key: '/qidian/rankings', label: '排行榜' },
        { key: '/qidian/authors', label: '作者信息' },
      ]
    },
    {
      key: '/subscription',
      icon: <CrownOutlined />,
      label: '订阅管理',
    },
    {
      key: '/workflows',
      icon: <NodeIndexOutlined />,
      label: '工作流',
    },
  ];
  
  return (
    <Sider className="app-sidebar" width={280}>
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        defaultOpenKeys={['/xiaohongshu', '/qidian']}
        items={menuItems}
      />
    </Sider>
  );
};
```

## 状态管理设计

### 1. 认证状态管理

```typescript
// 使用Zustand的认证store
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  login: (usernameOrEmail: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  checkAuth: () => Promise<void>;
}

const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  isAuthenticated: false,
  isLoading: false,
  
  login: async (usernameOrEmail: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authAPI.login(usernameOrEmail, password);
      const { user, access_token, refresh_token } = response;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      set({
        user,
        accessToken: access_token,
        refreshToken: refresh_token,
        isAuthenticated: true,
        isLoading: false
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false
    });
  },
  
  refreshAccessToken: async () => {
    const { refreshToken } = get();
    if (!refreshToken) throw new Error('No refresh token');
    
    try {
      const response = await authAPI.refreshToken(refreshToken);
      const { access_token } = response;
      
      localStorage.setItem('access_token', access_token);
      set({ accessToken: access_token });
    } catch (error) {
      get().logout();
      throw error;
    }
  },
  
  updateProfile: async (data: Partial<UserProfile>) => {
    const response = await userAPI.updateProfile(data);
    set({ user: response });
  },
  
  checkAuth: async () => {
    const { accessToken } = get();
    if (!accessToken) return;
    
    try {
      const user = await userAPI.getCurrentUser();
      set({ user, isAuthenticated: true });
    } catch (error) {
      get().logout();
    }
  }
}));
```

### 2. 自定义Hooks

```typescript
// useAuth Hook
export const useAuth = () => {
  const authStore = useAuthStore();
  
  useEffect(() => {
    authStore.checkAuth();
  }, []);
  
  return authStore;
};

// useRequireAuth Hook - 路由守卫
export const useRequireAuth = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);
  
  return { isAuthenticated, isLoading };
};

// useApiWithAuth Hook - 自动处理认证的API调用
export const useApiWithAuth = () => {
  const { accessToken, refreshAccessToken } = useAuth();
  
  const apiCall = useCallback(async (apiFunction: Function, ...args: any[]) => {
    try {
      return await apiFunction(...args);
    } catch (error: any) {
      if (error.response?.status === 401) {
        try {
          await refreshAccessToken();
          return await apiFunction(...args);
        } catch (refreshError) {
          throw refreshError;
        }
      }
      throw error;
    }
  }, [accessToken, refreshAccessToken]);
  
  return { apiCall };
};
```

## 样式设计系统

### 1. 设计令牌 (Design Tokens)

```scss
// 颜色系统
:root {
  // 主色调
  --primary-50: #f0f9ff;
  --primary-100: #e0f2fe;
  --primary-500: #0ea5e9;
  --primary-600: #0284c7;
  --primary-700: #0369a1;
  
  // 中性色
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-500: #6b7280;
  --gray-700: #374151;
  --gray-900: #111827;
  
  // 语义色
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;
  
  // 间距
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
  
  // 圆角
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  
  // 阴影
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  
  // 字体
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  // 字号
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
}
```

### 2. 组件样式

```scss
// 认证页面样式
.auth-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
  
  .auth-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: var(--spacing-2xl);
    max-width: 400px;
    margin: 0 auto;
    
    .auth-header {
      text-align: center;
      margin-bottom: var(--spacing-xl);
      
      h1 {
        font-size: var(--text-2xl);
        font-weight: 600;
        color: var(--gray-900);
        margin-bottom: var(--spacing-sm);
      }
      
      p {
        color: var(--gray-500);
        font-size: var(--text-sm);
      }
    }
    
    .auth-footer {
      margin-top: var(--spacing-lg);
      text-align: center;
      
      a {
        color: var(--primary-600);
        text-decoration: none;
        font-size: var(--text-sm);
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
  
  .auth-background {
    background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
    display: flex;
    align-items: center;
    justify-content: center;
    
    @media (max-width: 768px) {
      display: none;
    }
  }
}

// 用户资料页面样式
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-xl);
  
  .profile-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
    padding: var(--spacing-xl);
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    
    .profile-avatar {
      position: relative;
      
      .change-avatar-btn {
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        font-size: var(--text-xs);
      }
    }
    
    .profile-info {
      h1 {
        font-size: var(--text-2xl);
        font-weight: 600;
        margin-bottom: var(--spacing-xs);
      }
      
      .profile-email {
        color: var(--gray-500);
        margin-bottom: var(--spacing-sm);
      }
    }
  }
  
  .profile-content {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
  }
}
```

## 响应式设计

### 1. 移动端适配

```scss
// 移动端导航
@media (max-width: 768px) {
  .app-layout {
    .app-header {
      padding: 0 var(--spacing-md);
      
      .header-left {
        .navigation {
          display: none;
        }
      }
    }
    
    .app-sidebar {
      position: fixed;
      top: 0;
      left: -280px;
      height: 100vh;
      z-index: 1000;
      transition: left 0.3s ease;
      
      &.open {
        left: 0;
      }
    }
    
    .main-content {
      margin-left: 0;
    }
  }
  
  // 移动端表单
  .auth-card {
    padding: var(--spacing-lg);
    
    .login-form,
    .register-form {
      .ant-form-item {
        margin-bottom: var(--spacing-md);
      }
    }
  }
  
  // 移动端用户资料
  .profile-page {
    padding: var(--spacing-md);
    
    .profile-header {
      flex-direction: column;
      text-align: center;
      gap: var(--spacing-md);
    }
  }
}
```

### 2. 平板端适配

```scss
@media (min-width: 769px) and (max-width: 1024px) {
  .app-sidebar {
    width: 240px;
  }
  
  .profile-page {
    .basic-info-form {
      .ant-col {
        span: 24;
      }
    }
  }
}
```

## 性能优化

### 1. 代码分割

```typescript
// 路由懒加载
const LoginPage = lazy(() => import('../pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('../pages/auth/RegisterPage'));
const DashboardPage = lazy(() => import('../pages/dashboard/DashboardPage'));
const ProfilePage = lazy(() => import('../pages/profile/ProfilePage'));

// 路由配置
const AppRoutes: React.FC = () => {
  return (
    <Suspense fallback={<PageLoading />}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      </Routes>
    </Suspense>
  );
};
```

### 2. 图片优化

```typescript
// 头像组件优化
const OptimizedAvatar: React.FC<{ src?: string; size?: number }> = ({ src, size = 40 }) => {
  const [imageSrc, setImageSrc] = useState<string | undefined>(src);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (src) {
      const img = new Image();
      img.onload = () => {
        setImageSrc(src);
        setLoading(false);
      };
      img.onerror = () => {
        setImageSrc(undefined);
        setLoading(false);
      };
      img.src = src;
    } else {
      setLoading(false);
    }
  }, [src]);
  
  if (loading) {
    return <Skeleton.Avatar size={size} />;
  }
  
  return (
    <Avatar
      size={size}
      src={imageSrc}
      icon={<UserOutlined />}
    />
  );
};
```

## 可访问性 (Accessibility)

### 1. 键盘导航

```typescript
// 键盘快捷键支持
const useKeyboardShortcuts = () => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + K 打开搜索
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        // 打开搜索模态框
      }
      
      // Escape 关闭模态框
      if (event.key === 'Escape') {
        // 关闭当前模态框
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
};
```

### 2. 屏幕阅读器支持

```typescript
// 可访问性增强的表单组件
const AccessibleFormItem: React.FC<{
  label: string;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
}> = ({ label, required, error, children }) => {
  const id = useId();
  const errorId = `${id}-error`;
  
  return (
    <div className="form-item">
      <label htmlFor={id} className={required ? 'required' : ''}>
        {label}
        {required && <span aria-label="必填">*</span>}
      </label>
      
      {React.cloneElement(children as React.ReactElement, {
        id,
        'aria-describedby': error ? errorId : undefined,
        'aria-invalid': !!error
      })}
      
      {error && (
        <div id={errorId} role="alert" className="error-message">
          {error}
        </div>
      )}
    </div>
  );
};
```

## 国际化 (i18n)

```typescript
// 国际化配置
const i18nConfig = {
  lng: 'zh-CN',
  fallbackLng: 'en-US',
  resources: {
    'zh-CN': {
      translation: {
        'auth.login': '登录',
        'auth.register': '注册',
        'auth.logout': '退出登录',
        'profile.basic_info': '基本信息',
        'profile.security': '安全设置',
        // 更多翻译...
      }
    },
    'en-US': {
      translation: {
        'auth.login': 'Login',
        'auth.register': 'Register',
        'auth.logout': 'Logout',
        'profile.basic_info': 'Basic Information',
        'profile.security': 'Security Settings',
        // 更多翻译...
      }
    }
  }
};

// 使用翻译
const LoginPage: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('auth.login')}</h1>
      {/* 其他内容 */}
    </div>
  );
};
```

## 开发和部署

### 1. 开发环境配置

```json
// package.json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "storybook": "storybook dev -p 6006"
  }
}
```

### 2. 构建优化

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          antd: ['antd'],
          utils: ['lodash', 'dayjs']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'antd']
  }
});
```

这个前端布局计划提供了完整的用户模块界面设计，包括认证流程、用户资料管理、响应式设计、性能优化和可访问性支持。可以根据具体的技术栈和设计需求进行调整和扩展。