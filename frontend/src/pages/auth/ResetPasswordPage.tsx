import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Button,
  Card,
  Typography,
  Alert,
  Space,
  message,
} from 'antd';
import {
  LockOutlined,
  SafetyOutlined,
  ClockCircleOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone,
} from '@ant-design/icons';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../../services/authService';

const { Title, Text } = Typography;

/**
 * 验证密码是否符合后端要求（与RegisterPage保持一致）
 */
const validatePasswordStrength = (password: string): string | null => {
  if (password.length < 8) {
    return '密码长度至少需要8个字符';
  }
  if (!/[A-Z]/.test(password)) {
    return '密码需要包含至少一个大写字母';
  }
  if (!/[a-z]/.test(password)) {
    return '密码需要包含至少一个小写字母';
  }
  if (!/[0-9]/.test(password)) {
    return '密码需要包含至少一个数字';
  }
  if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
    return '密码需要包含至少一个特殊字符';
  }
  return null;
};

/**
 * 密码重置页面组件
 */
const ResetPasswordPage: React.FC = () => {
  const [form] = Form.useForm();
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [canResend, setCanResend] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // 从路由state中获取邮箱地址
  const email = (location.state as any)?.email || '';

  useEffect(() => {
    if (!email) {
      // 如果没有邮箱信息，重定向到忘记密码页面
      navigate('/auth/forgot-password');
    }
  }, [email, navigate]);

  // 60秒后允许重新发送
  useEffect(() => {
    const timer = setTimeout(() => {
      setCanResend(true);
    }, 60000);

    return () => clearTimeout(timer);
  }, []);

  // 处理重置密码提交
  const handleSubmit = async (values: { code: string; password: string }) => {
    setIsLoading(true);
    setError(null);

    try {
      await authService.resetPasswordWithCode(email, values.code, values.password);
      message.success('密码重置成功！');
      navigate('/auth/login', { 
        state: { 
          message: '密码重置成功，请使用新密码登录' 
        }
      });
    } catch (error: any) {
      setError(error.message || '重置失败，请检查验证码是否正确');
    } finally {
      setIsLoading(false);
    }
  };

  // 重新发送验证码
  const handleResend = async () => {
    setIsResending(true);
    setError(null);

    try {
      await authService.resendVerificationCode(email, 'reset_password');
      message.success('验证码已重新发送，请查收邮件');
      setCanResend(false);
      // 60秒后重新允许发送
      setTimeout(() => {
        setCanResend(true);
      }, 60000);
    } catch (error: any) {
      setError(error.message || '重新发送失败，请稍后再试');
    } finally {
      setIsResending(false);
    }
  };

  if (!email) {
    return null; // 等待重定向
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <SafetyOutlined className="text-5xl text-red-600 mb-4" />
          <Title level={2} className="text-gray-900 mb-2">
            重置密码
          </Title>
          <Text type="secondary" className="text-base">
            我们已向 <Text strong>{email}</Text> 发送了6位数字验证码
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
              name="reset-password"
              onFinish={handleSubmit}
              layout="vertical"
              size="large"
              autoComplete="off"
            >
              <Form.Item
                name="code"
                label="6位验证码"
                rules={[
                  {
                    required: true,
                    message: '请输入验证码！',
                  },
                  {
                    len: 6,
                    message: '验证码必须是6位数字！',
                  },
                  {
                    pattern: /^[0-9]{6}$/,
                    message: '验证码只能包含数字！',
                  },
                ]}
              >
                <Input
                  placeholder="请输入6位验证码"
                  className="text-center text-2xl font-mono tracking-widest"
                  maxLength={6}
                  autoComplete="off"
                />
              </Form.Item>

              <Form.Item
                name="password"
                label="新密码"
                rules={[
                  {
                    required: true,
                    message: '请输入新密码！',
                  },
                  {
                    validator: (_, value) => {
                      if (!value) return Promise.resolve();
                      const error = validatePasswordStrength(value);
                      return error ? Promise.reject(new Error(error)) : Promise.resolve();
                    },
                  },
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="请输入新密码"
                  autoComplete="new-password"
                  iconRender={(visible) =>
                    visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                  }
                />
              </Form.Item>

              <Form.Item
                name="confirmPassword"
                label="确认新密码"
                dependencies={['password']}
                rules={[
                  {
                    required: true,
                    message: '请确认新密码！',
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
                  placeholder="请再次输入新密码"
                  autoComplete="new-password"
                  iconRender={(visible) =>
                    visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                  }
                />
              </Form.Item>

              <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center space-x-2 text-yellow-700">
                  <ClockCircleOutlined />
                  <Text className="text-sm">
                    验证码有效期为5分钟，请及时使用
                  </Text>
                </div>
              </div>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isLoading}
                  block
                  className="h-12"
                  danger
                >
                  {isLoading ? '重置中...' : '重置密码'}
                </Button>
              </Form.Item>
            </Form>

            <div className="text-center space-y-4">
              <div>
                <Text type="secondary">没有收到验证码？</Text>
              </div>
              
              <Button
                type="link"
                onClick={handleResend}
                loading={isResending}
                disabled={!canResend}
                className="p-0"
                danger
              >
                {isResending
                  ? '发送中...'
                  : canResend
                  ? '重新发送验证码'
                  : '60秒后可重新发送'
                }
              </Button>

              <div className="pt-4 border-t border-gray-200">
                <Space>
                  <Text type="secondary">需要修改邮箱？</Text>
                  <Link
                    to="/auth/forgot-password"
                    className="text-blue-600 hover:text-blue-500 font-medium"
                  >
                    返回上一步
                  </Link>
                </Space>
              </div>
            </div>
          </div>
        </Card>

        <div className="text-center">
          <Text type="secondary" className="text-sm">
            请检查您的邮箱（包括垃圾邮件文件夹）
          </Text>
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordPage;