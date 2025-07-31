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
  Statistic,
} from 'antd';
import {
  MailOutlined,
  SafetyOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../../services/authService';

const { Title, Text } = Typography;
const { Countdown } = Statistic;

/**
 * 邮箱验证页面组件
 */
const VerifyEmailPage: React.FC = () => {
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
      // 如果没有邮箱信息，重定向到注册页面
      navigate('/auth/register');
    }
  }, [email, navigate]);

  // 60秒后允许重新发送
  useEffect(() => {
    const timer = setTimeout(() => {
      setCanResend(true);
    }, 60000);

    return () => clearTimeout(timer);
  }, []);

  // 处理验证码提交
  const handleSubmit = async (values: { code: string }) => {
    setIsLoading(true);
    setError(null);

    try {
      await authService.verifyEmailCode(email, values.code);
      message.success('邮箱验证成功！');
      navigate('/auth/login', { 
        state: { 
          message: '邮箱验证成功，请登录您的账户' 
        }
      });
    } catch (error: any) {
      setError(error.message || '验证失败，请检查验证码是否正确');
    } finally {
      setIsLoading(false);
    }
  };

  // 重新发送验证码
  const handleResend = async () => {
    setIsResending(true);
    setError(null);

    try {
      await authService.resendVerificationCode(email, 'register');
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
          <SafetyOutlined className="text-5xl text-blue-600 mb-4" />
          <Title level={2} className="text-gray-900 mb-2">
            验证您的邮箱
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
              name="verify-email"
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

              <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center space-x-2 text-yellow-700">
                  <ClockCircleOutlined />
                  <Text className="text-sm">
                    验证码有效期为5分钟，请及时验证
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
                >
                  {isLoading ? '验证中...' : '验证邮箱'}
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
                    to="/auth/register"
                    className="text-blue-600 hover:text-blue-500 font-medium"
                  >
                    返回注册
                  </Link>
                </Space>
              </div>
            </div>
          </div>
        </Card>

        <div className="text-center">
          <Text type="secondary" className="text-sm">
            <MailOutlined className="mr-1" />
            请检查您的邮箱（包括垃圾邮件文件夹）
          </Text>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmailPage;