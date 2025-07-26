import React, { useState } from 'react';
import {
  Form,
  Input,
  Button,
  Card,
  Typography,
  Alert,
  Space,
  Result,
} from 'antd';
import {
  MailOutlined,
  ArrowLeftOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import authService from '../../services/authService';

const { Title, Text } = Typography;

/**
 * 忘记密码页面组件
 */
const ForgotPasswordPage: React.FC = () => {
  const [form] = Form.useForm();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEmailSent, setIsEmailSent] = useState(false);
  const [email, setEmail] = useState('');

  // 处理表单提交
  const handleSubmit = async (values: { email: string }) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await authService.forgotPassword(values.email);
      setEmail(values.email);
      setIsEmailSent(true);
    } catch (error: any) {
      setError(error.message || '发送重置邮件失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 重新发送邮件
  const handleResendEmail = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      await authService.forgotPassword(email);
      // 可以显示成功消息
    } catch (error: any) {
      setError(error.message || '重新发送邮件失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 如果邮件已发送，显示成功页面
  if (isEmailSent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <Card className="shadow-lg">
            <Result
              status="success"
              title="重置邮件已发送"
              subTitle={`我们已向 ${email} 发送了密码重置链接，请检查您的邮箱并按照邮件中的说明重置密码。`}
              extra={[
                <Button
                  key="resend"
                  type="primary"
                  onClick={handleResendEmail}
                  loading={isLoading}
                >
                  重新发送邮件
                </Button>,
                <Link key="back" to="/auth/login">
                  <Button>
                    返回登录
                  </Button>
                </Link>,
              ]}
            />
            
            {error && (
              <Alert
                message={error}
                type="error"
                showIcon
                className="mt-4"
              />
            )}
            
            <div className="text-center mt-6">
              <Text type="secondary" className="text-sm">
                没有收到邮件？请检查垃圾邮件文件夹，或者
                <Button
                  type="link"
                  onClick={handleResendEmail}
                  loading={isLoading}
                  className="p-0 h-auto"
                >
                  重新发送
                </Button>
              </Text>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex">
      {/* 左侧品牌区域 - 只在lg及以上屏幕显示 */}
      <div className="hidden lg:flex lg:w-3/5 bg-gradient-to-br from-yellow-400 via-orange-500 to-red-600 relative overflow-hidden">
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
              找回您的账户
            </Title>
            <Text className="text-white opacity-80 text-lg">
              别担心，我们会帮助您重新获得账户访问权限
            </Text>
          </div>
        </div>
        {/* 装饰性几何图形 */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full transform translate-x-32 -translate-y-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white opacity-10 rounded-full transform -translate-x-24 translate-y-24"></div>
      </div>

      {/* 右侧重置密码区域 */}
      <div className="w-full lg:w-2/5 flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-12">
        <div className="max-w-md w-full space-y-8">
          {/* 移动端品牌标识 - 只在lg以下屏幕显示 */}
          <div className="text-center lg:hidden mb-8">
            <RocketOutlined className="text-4xl text-orange-600 mb-4" />
            <Title level={2} className="text-gray-900 mb-2">
              Workflow Platform
            </Title>
          </div>

          <div className="text-center">
            <Title level={2} className="text-gray-900 mb-2">
              重置密码
            </Title>
            <Text type="secondary" className="text-base">
              输入您的邮箱地址，我们将发送重置密码的链接
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
                name="forgotPassword"
                onFinish={handleSubmit}
                layout="vertical"
                size="large"
                autoComplete="off"
              >
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
                    placeholder="请输入您的邮箱地址"
                    autoComplete="email"
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
                    {isLoading ? '发送中...' : '发送重置链接'}
                  </Button>
                </Form.Item>
              </Form>

              <div className="text-center mt-4">
                <Link
                  to="/auth/login"
                  className="text-blue-600 hover:text-blue-500 inline-flex items-center"
                >
                  <ArrowLeftOutlined className="mr-1" />
                  返回登录
                </Link>
              </div>
            </div>
          </Card>

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
      </div>
    </div>
  );
};

export default ForgotPasswordPage;