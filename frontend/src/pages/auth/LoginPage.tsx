import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Button,
  Card,
  Typography,
  Divider,
  Space,
  Checkbox,
  Alert,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone,
  RocketOutlined,
} from '@ant-design/icons';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import type { LoginFormData } from '../../types/auth';

const { Title, Text } = Typography;

/**
 * 登录页面组件
 */
const LoginPage: React.FC = () => {
  const [form] = Form.useForm();
  const [rememberMe, setRememberMe] = useState(false);
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // 获取重定向路径
  const from = (location.state as any)?.from?.pathname || '/dashboard';

  // 页面加载时恢复记住我状态和保存的凭据
  useEffect(() => {
    const savedRememberMe = localStorage.getItem('remember_me') === 'true';
    setRememberMe(savedRememberMe);
    
    if (savedRememberMe) {
      const savedUsername = localStorage.getItem('saved_username');
      const savedPassword = localStorage.getItem('saved_password');
      
      if (savedUsername && savedPassword) {
        form.setFieldsValue({
          usernameOrEmail: savedUsername,
          password: savedPassword,
        });
      }
    }
  }, [form]);

  // 处理表单提交
  const handleSubmit = async (values: LoginFormData) => {
    try {
      await login(values.usernameOrEmail, values.password);
      
      // 如果选择记住我，保存凭据和状态
      if (rememberMe) {
        localStorage.setItem('remember_me', 'true');
        localStorage.setItem('saved_username', values.usernameOrEmail);
        localStorage.setItem('saved_password', values.password);
      } else {
        localStorage.removeItem('remember_me');
        localStorage.removeItem('saved_username');
        localStorage.removeItem('saved_password');
      }
      
      // 登录成功后重定向
      navigate(from, { replace: true });
    } catch (error) {
      // 错误处理已在useAuth hook中完成
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* 左侧品牌区域 - 只在lg及以上屏幕显示 */}
      <div className="hidden lg:flex lg:w-3/5 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 relative overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="relative z-10 flex flex-col justify-center items-center text-white p-12">
          <div className="mb-8">
            <RocketOutlined className="text-6xl mb-4" />
            <Title level={1} className="text-white mb-0">
              Workflow Platform
            </Title>
          </div>
          <div className="text-center max-w-md">
            <Title level={3} className="text-white opacity-90 mb-4">
              智能工作流管理平台
            </Title>
            <Text className="text-white opacity-80 text-lg">
              提升团队协作效率，让工作更简单、更智能
            </Text>
          </div>
        </div>
        {/* 装饰性几何图形 */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full transform translate-x-32 -translate-y-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white opacity-10 rounded-full transform -translate-x-24 translate-y-24"></div>
      </div>

      {/* 右侧登录区域 */}
      <div className="w-full lg:w-2/5 flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-12">
        <div className="max-w-md w-full space-y-8">
          {/* 移动端品牌标识 - 只在lg以下屏幕显示 */}
          <div className="text-center lg:hidden mb-8">
            <RocketOutlined className="text-4xl text-blue-600 mb-4" />
            <Title level={2} className="text-gray-900 mb-2">
              Workflow Platform
            </Title>
            <Text type="secondary" className="text-base">
              智能工作流管理平台
            </Text>
          </div>

          <div className="text-center">
            <Title level={2} className="text-gray-900 mb-2">
              欢迎回来
            </Title>
            <Text type="secondary" className="text-base">
              登录您的账户以继续使用
            </Text>
          </div>

          <Card className="shadow-xl border-0 rounded-2xl overflow-hidden">
            <div className="p-8">
          {error && (
            <Alert
              message={error}
              type="error"
              showIcon
              className="mb-4"
            />
          )}

          <Form
            form={form}
            name="login"
            onFinish={handleSubmit}
            layout="vertical"
            size="large"
            autoComplete="off"
          >
            <Form.Item
              name="usernameOrEmail"
              label="用户名或邮箱"
              rules={[
                {
                  required: true,
                  message: '请输入用户名或邮箱！',
                },
                {
                  min: 3,
                  message: '用户名至少3个字符！',
                },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="请输入用户名或邮箱"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="密码"
              rules={[
                {
                  required: true,
                  message: '请输入密码！',
                },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="请输入密码"
                autoComplete="current-password"
                iconRender={(visible) =>
                  visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                }
              />
            </Form.Item>

            <Form.Item>
              <div className="flex items-center justify-between">
                <Checkbox
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                >
                  记住我
                </Checkbox>
                <Link
                  to="/auth/forgot-password"
                  className="text-blue-600 hover:text-blue-500"
                >
                  忘记密码？
                </Link>
              </div>
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={isLoading}
                block
                className="h-12"
              >
                {isLoading ? '登录中...' : '登录'}
              </Button>
            </Form.Item>
          </Form>

          <Divider>
            <Text type="secondary">或</Text>
          </Divider>

              <div className="text-center">
                <Space>
                  <Text type="secondary">还没有账户？</Text>
                  <Link
                    to="/auth/register"
                    className="text-blue-600 hover:text-blue-500 font-medium"
                  >
                    立即注册
                  </Link>
                </Space>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;