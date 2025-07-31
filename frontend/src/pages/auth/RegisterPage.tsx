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
  message,
  Row,
  Col,
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  LockOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone,
  RocketOutlined,
  LoadingOutlined,
} from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { authService } from '../../services/authService';
import type { RegisterFormData } from '../../types/auth';

const { Title, Text } = Typography;

/**
 * 密码强度检查（与后端验证规则一致）
 */
const checkPasswordStrength = (password: string): { score: number; text: string; color: string } => {
  let score = 0;
  
  if (password.length >= 8) score += 20;
  if (/[a-z]/.test(password)) score += 20;
  if (/[A-Z]/.test(password)) score += 20;
  if (/[0-9]/.test(password)) score += 20;
  if (/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) score += 20;
  
  if (score < 100) return { score, text: '不符合要求', color: '#ff4d4f' };
  return { score, text: '符合要求', color: '#52c41a' };
};

/**
 * 验证密码是否符合后端要求
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
 * 注册页面组件
 */
const RegisterPage: React.FC = () => {
  const [form] = Form.useForm();
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, text: '', color: '' });
  const [codeSent, setCodeSent] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const { register, isLoading, error } = useAuth();
  const navigate = useNavigate();


  // 发送验证码
  const handleSendCode = async () => {
    try {
      const email = form.getFieldValue('email');
      if (!email) {
        message.error('请先输入邮箱地址');
        return;
      }
      
      // 验证邮箱格式
      await form.validateFields(['email']);
      
      setSendingCode(true);
      await authService.sendVerificationCode(email, 'register');
      
      setCodeSent(true);
      message.success('验证码已发送，请查收邮件');
      
      // 开始倒计时（3分钟 = 180秒）
      setCountdown(180);
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
    } catch (error: any) {
      console.error('Send code failed:', error);
      if (error.status === 429) {
        message.error(error.message);
      } else if (error.message) {
        message.error(error.message);
      } else {
        message.error('发送验证码失败，请稍后重试');
      }
    } finally {
      setSendingCode(false);
    }
  };

  // 处理表单提交
  const handleSubmit = async (values: { username: string; email: string; password: string; confirmPassword: string; code: string }) => {
    // 检查是否已发送验证码
    if (!codeSent) {
      message.warning('请先获取邮箱验证码');
      return;
    }

    // 检查验证码是否为空
    if (!values.code || values.code.trim() === '') {
      message.warning('请输入验证码');
      return;
    }

    try {
      await register(values.username, values.email, values.password, values.code);
      message.success('注册成功！正在跳转到登录页面...');
      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        navigate('/auth/login', {
          state: {
            message: '注册成功！请使用您的账号登录'
          }
        });
      }, 1500);
    } catch (error: any) {
      console.error('Registration failed:', error);
      
      // 根据不同的错误类型显示不同的提示
      if (error.message) {
        if (error.message.includes('验证码')) {
          message.error('验证码错误或已过期，请重新获取验证码');
        } else if (error.message.includes('用户名')) {
          message.error('用户名已存在，请选择其他用户名');
        } else if (error.message.includes('邮箱')) {
          message.error('邮箱已被注册，请使用其他邮箱');
        } else if (error.message.includes('密码')) {
          message.error('密码格式不符合要求');
        } else {
          message.error(error.message);
        }
      } else {
        message.error('注册失败，请检查网络连接后重试');
      }
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
            onValuesChange={(changedValues, allValues) => {
              if (changedValues.password) {
                setPasswordStrength(checkPasswordStrength(changedValues.password));
                // 当密码字段变化时，重新验证确认密码字段
                form.validateFields(['confirmPassword']);
              }
            }}
          >
            <Form.Item
              name="username"
              label="用户名"
              htmlFor="register-username"
              rules={[
                {
                  required: true,
                  message: '请输入用户名！',
                },
                {
                  min: 3,
                  max: 50,
                  message: '用户名长度应在3-50个字符之间！',
                },
                {
                  pattern: /^[a-zA-Z0-9_]+$/,
                  message: '用户名只能包含字母、数字和下划线！',
                },
              ]}
            >
              <Input
                id="register-username"
                prefix={<UserOutlined />}
                placeholder="请输入用户名"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="email"
              label="邮箱地址"
              htmlFor="register-email"
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
                id="register-email"
                prefix={<MailOutlined />}
                placeholder="请输入邮箱地址"
                autoComplete="email"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="密码"
              htmlFor="register-password"
              rules={[
                {
                  required: true,
                  message: '请输入密码！',
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
              <div>
                <Input.Password
                  id="register-password"
                  prefix={<LockOutlined />}
                  placeholder="请输入密码"
                  autoComplete="new-password"
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
              </div>
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              label="确认密码"
              htmlFor="register-confirm-password"
              dependencies={['password']}
              rules={[
                {
                  required: true,
                  message: '请确认密码！',
                },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value) {
                      return Promise.resolve();
                    }
                    const password = getFieldValue('password');
                    console.log('Password validation:', { password, confirmPassword: value, match: password === value });
                    if (password === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致！'));
                  },
                }),
              ]}
            >
              <Input.Password
                id="register-confirm-password"
                prefix={<LockOutlined />}
                placeholder="请再次输入密码"
                autoComplete="off"
                iconRender={(visible) =>
                  visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                }
              />
            </Form.Item>

            <Form.Item
              name="code"
              label="邮箱验证码"
              htmlFor="register-verification-code"
              rules={[
                {
                  required: codeSent,
                  message: '请输入邮箱验证码！',
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
              <div>
                <Row gutter={8}>
                  <Col span={16}>
                    <Input
                      id="register-verification-code"
                      placeholder="请输入6位验证码"
                      maxLength={6}
                      disabled={!codeSent}
                      autoComplete="off"
                    />
                  </Col>
                  <Col span={8}>
                    <Button
                      type="default"
                      onClick={handleSendCode}
                      loading={sendingCode}
                      disabled={countdown > 0}
                      block
                      icon={sendingCode ? <LoadingOutlined /> : undefined}
                    >
                      {countdown > 0
                        ? `${Math.floor(countdown / 60)}:${(countdown % 60).toString().padStart(2, '0')}`
                        : codeSent
                        ? '重新发送'
                        : '发送验证码'
                      }
                    </Button>
                  </Col>
                </Row>
                {codeSent && (
                  <div className="mt-2">
                    <Text type="secondary" className="text-xs">
                      验证码已发送到您的邮箱，请查收并输入
                    </Text>
                  </div>
                )}
              </div>
            </Form.Item>

            <Form.Item>
              <div>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isLoading}
                  block
                  className="h-12"
                >
                  {isLoading ? '注册中...' : '注册'}
                </Button>
                {!codeSent && (
                  <div className="mt-2 text-center">
                    <Text type="secondary" className="text-xs">
                      请先获取邮箱验证码
                    </Text>
                  </div>
                )}
              </div>
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