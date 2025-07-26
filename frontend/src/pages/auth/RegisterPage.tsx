import React, { useState } from 'react';
import {
  Form,
  Input,
  Button,
  Card,
  Typography,
  Divider,
  Space,
  Alert,
  Progress,
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  LockOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone,
  RocketOutlined,
} from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import type { RegisterFormData } from '../../types/auth';

const { Title, Text } = Typography;

/**
 * 密码强度检查
 */
const checkPasswordStrength = (password: string): { score: number; text: string; color: string } => {
  let score = 0;
  
  if (password.length >= 8) score += 25;
  if (/[a-z]/.test(password)) score += 25;
  if (/[A-Z]/.test(password)) score += 25;
  if (/[0-9]/.test(password)) score += 25;
  if (/[^A-Za-z0-9]/.test(password)) score += 25;
  
  if (score <= 25) return { score, text: '弱', color: '#ff4d4f' };
  if (score <= 50) return { score, text: '一般', color: '#faad14' };
  if (score <= 75) return { score, text: '良好', color: '#1890ff' };
  return { score, text: '强', color: '#52c41a' };
};

/**
 * 注册页面组件
 */
const RegisterPage: React.FC = () => {
  const [form] = Form.useForm();
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, text: '', color: '' });
  const { register, isLoading, error } = useAuth();
  const navigate = useNavigate();

  // 处理密码变化
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const password = e.target.value;
    setPasswordStrength(checkPasswordStrength(password));
  };

  // 处理表单提交
  const handleSubmit = async (values: RegisterFormData) => {
    try {
      await register(values.username, values.email, values.password);
      // 注册成功后重定向到仪表板
      navigate('/dashboard');
    } catch (error) {
      // 错误处理已在useAuth hook中完成
      console.error('Registration failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* 左侧品牌区域 - 只在lg及以上屏幕显示 */}
      <div className="hidden lg:flex lg:w-3/5 bg-gradient-to-br from-green-500 via-teal-500 to-cyan-600 relative overflow-hidden">
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
              开启您的智能工作之旅
            </Title>
            <Text className="text-white opacity-80 text-lg">
              加入我们，体验全新的工作流管理方式
            </Text>
          </div>
        </div>
        {/* 装饰性几何图形 */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full transform translate-x-32 -translate-y-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white opacity-10 rounded-full transform -translate-x-24 translate-y-24"></div>
      </div>

      {/* 右侧注册区域 */}
      <div className="w-full lg:w-2/5 flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-12">
        <div className="max-w-md w-full space-y-8">
          {/* 移动端品牌标识 - 只在lg以下屏幕显示 */}
          <div className="text-center lg:hidden mb-8">
            <RocketOutlined className="text-4xl text-green-600 mb-4" />
            <Title level={2} className="text-gray-900 mb-2">
              Workflow Platform
            </Title>
          </div>

          <div className="text-center">
            <Title level={2} className="text-gray-900 mb-2">
              创建新账户
            </Title>
            <Text type="secondary" className="text-base">
              欢迎加入我们！请填写以下信息完成注册
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
            name="register"
            onFinish={handleSubmit}
            layout="vertical"
            size="large"
            autoComplete="off"
          >
            <Form.Item
              name="username"
              label="用户名"
              rules={[
                {
                  required: true,
                  message: '请输入用户名！',
                },
                {
                  min: 3,
                  max: 20,
                  message: '用户名长度应在3-20个字符之间！',
                },
                {
                  pattern: /^[a-zA-Z0-9_]+$/,
                  message: '用户名只能包含字母、数字和下划线！',
                },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="请输入用户名"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="email"
              label="邮箱地址"
              rules={[
                {
                  required: true,
                  message: '请输入邮箱地址！',
                },
                {
                  type: 'email',
                  message: '请输入有效的邮箱地址！',
                },
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="请输入邮箱地址"
                autoComplete="email"
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
                {
                  min: 8,
                  message: '密码至少8个字符！',
                },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="请输入密码"
                autoComplete="new-password"
                onChange={handlePasswordChange}
                iconRender={(visible) =>
                  visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                }
              />
              {passwordStrength.score > 0 && (
                <div className="mt-2">
                  <div className="flex items-center justify-between mb-1">
                    <Text type="secondary" className="text-xs">
                      密码强度
                    </Text>
                    <Text
                      className="text-xs"
                      style={{ color: passwordStrength.color }}
                    >
                      {passwordStrength.text}
                    </Text>
                  </div>
                  <Progress
                    percent={passwordStrength.score}
                    strokeColor={passwordStrength.color}
                    showInfo={false}
                    size="small"
                  />
                </div>
              )}
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              label="确认密码"
              dependencies={['password']}
              rules={[
                {
                  required: true,
                  message: '请确认密码！',
                },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致！'));
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="请再次输入密码"
                autoComplete="new-password"
                iconRender={(visible) =>
                  visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                }
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={isLoading}
                block
                className="h-12"
              >
                {isLoading ? '注册中...' : '注册'}
              </Button>
            </Form.Item>
          </Form>

          <Divider>
            <Text type="secondary">或</Text>
          </Divider>

              <div className="text-center">
                <Space>
                  <Text type="secondary">已有账户？</Text>
                  <Link
                    to="/auth/login"
                    className="text-blue-600 hover:text-blue-500 font-medium"
                  >
                    立即登录
                  </Link>
                </Space>
              </div>
            </div>
          </Card>

          <div className="text-center">
            <Text type="secondary" className="text-xs">
              注册即表示您同意我们的
              <Link to="/terms" className="text-blue-600 hover:text-blue-500">
                服务条款
              </Link>
              和
              <Link to="/privacy" className="text-blue-600 hover:text-blue-500">
                隐私政策
              </Link>
            </Text>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;