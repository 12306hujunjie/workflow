import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Avatar,
  Upload,
  Typography,
  Row,
  Col,
  Select,
  DatePicker,
  message,
  Divider,
  Space,
  Tag,
} from 'antd';
import {
  UserOutlined,
  UploadOutlined,
  EditOutlined,
  SaveOutlined,
  CameraOutlined,
} from '@ant-design/icons';
import { useAuth, useCurrentUser } from '../../hooks/useAuth';
import userService from '../../services/userService';
import dayjs from 'dayjs';
import type { UploadFile } from 'antd';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

/**
 * 用户资料页面组件
 */
export const ProfilePage: React.FC = () => {
  const [form] = Form.useForm();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const { updateProfile } = useAuth();
  const user = useCurrentUser();

  // 初始化表单数据
  React.useEffect(() => {
    if (user) {
      // 如果用户有profile数据，拆分display_name为first_name和last_name
      let firstName = '';
      let lastName = '';
      
      if (user.profile?.display_name) {
        // 简单的拆分逻辑：假设最后一个字符是姓氏，其余是名字
        const displayName = user.profile.display_name.trim();
        if (displayName.length > 1) {
          lastName = displayName.slice(-1);
          firstName = displayName.slice(0, -1);
        } else {
          firstName = displayName;
        }
      }
      
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        first_name: firstName,
        last_name: lastName,
        timezone: user.profile?.timezone || '',
        language: user.profile?.language || '',
        bio: user.profile?.bio || '',
      });
    }
  }, [user, form]);

  // 处理头像上传
  const handleAvatarUpload = async (file: File) => {
    setAvatarLoading(true);
    try {
      await userService.uploadAvatar(file);
      message.success('头像更新成功！');
      // 这里应该重新获取用户信息
    } catch (error: any) {
      message.error(error.message || '头像上传失败');
    } finally {
      setAvatarLoading(false);
    }
  };

  // 处理表单提交
  const handleSubmit = async (values: any) => {
    setIsLoading(true);
    try {
      // 转换前端表单数据以匹配后端API schema
      const profileData: any = { ...values };
      
      // 如果有first_name和last_name，合并为display_name
      if (values.first_name || values.last_name) {
        const firstName = values.first_name || '';
        const lastName = values.last_name || '';
        profileData.display_name = `${firstName}${lastName}`.trim();
        // 移除原始的name字段，因为后端不接受这些字段
        delete profileData.first_name;
        delete profileData.last_name;
      }
      
      // 移除username和email字段，因为这些不能通过profile API更新
      delete profileData.username;
      delete profileData.email;
      
      await updateProfile(profileData);
      message.success('资料更新成功！');
      setIsEditing(false);
    } catch (error: any) {
      message.error(error.message || '更新失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 取消编辑
  const handleCancel = () => {
    form.resetFields();
    setIsEditing(false);
  };

  // 获取用户显示名称
  const getUserDisplayName = () => {
    return user?.username || '用户';
  };

  // 获取用户状态标签
  const getUserStatusTag = () => {
    if (!user) return null;
    
    const statusConfig = {
      active: { color: 'green', text: '活跃' },
      inactive: { color: 'orange', text: '非活跃' },
      banned: { color: 'red', text: '已禁用' },
    };
    
    const config = statusConfig[user.status] || statusConfig.active;
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <Title level={2}>个人资料</Title>
        {!isEditing ? (
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => setIsEditing(true)}
          >
            编辑资料
          </Button>
        ) : (
          <Space>
            <Button onClick={handleCancel}>
              取消
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={() => form.submit()}
              loading={isLoading}
            >
              保存
            </Button>
          </Space>
        )}
      </div>

      <Row gutter={[24, 24]}>
        {/* 左侧：头像和基本信息 */}
        <Col xs={24} lg={8}>
          <Card>
            <div className="text-center space-y-4">
              {/* 头像 */}
              <div className="relative inline-block">
                <Avatar
                  size={120}
                  icon={<UserOutlined />}
                />
                {isEditing && (
                  <Upload
                    accept="image/*"
                    showUploadList={false}
                    beforeUpload={(file) => {
                      handleAvatarUpload(file);
                      return false;
                    }}
                  >
                    <Button
                      type="primary"
                      shape="circle"
                      icon={<CameraOutlined />}
                      loading={avatarLoading}
                      className="absolute bottom-0 right-0"
                      size="small"
                    />
                  </Upload>
                )}
              </div>

              {/* 用户名和状态 */}
              <div>
                <Title level={4} className="mb-2">
                  {getUserDisplayName()}
                </Title>
                <Space>
                  <Text type="secondary">@{user?.username}</Text>
                  {getUserStatusTag()}
                </Space>
              </div>

              {/* 基本统计 */}
              <Divider />
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-blue-600">42</div>
                  <Text type="secondary">任务完成</Text>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">98%</div>
                  <Text type="secondary">完成率</Text>
                </div>
              </div>
            </div>
          </Card>

          {/* 账户信息 */}
          <Card title="账户信息" className="mt-6">
            <div className="space-y-3">
              <div className="flex justify-between">
                <Text type="secondary">用户ID:</Text>
                <Text>{user?.id}</Text>
              </div>
              <div className="flex justify-between">
                <Text type="secondary">注册时间:</Text>
                <Text>
                  {user?.created_at ? dayjs(user.created_at).format('YYYY-MM-DD') : '-'}
                </Text>
              </div>
              <div className="flex justify-between">
                <Text type="secondary">最后登录:</Text>
                <Text>
                  {user?.last_login_at ? dayjs(user.last_login_at).format('YYYY-MM-DD HH:mm') : '从未登录'}
                </Text>
              </div>
              <div className="flex justify-between">
                <Text type="secondary">账户状态:</Text>
                {getUserStatusTag()}
              </div>
            </div>
          </Card>
        </Col>

        {/* 右侧：详细信息表单 */}
        <Col xs={24} lg={16}>
          <Card title="详细信息">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              disabled={!isEditing}
            >
              <Row gutter={[16, 0]}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="first_name"
                    label="名字"
                    rules={[
                      {
                        max: 30,
                        message: '名字不能超过30个字符',
                      },
                    ]}
                  >
                    <Input placeholder="请输入名字" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="last_name"
                    label="姓氏"
                    rules={[
                      {
                        max: 30,
                        message: '姓氏不能超过30个字符',
                      },
                    ]}
                  >
                    <Input placeholder="请输入姓氏" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={[16, 0]}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="username"
                    label="用户名"
                    rules={[
                      {
                        required: true,
                        message: '请输入用户名',
                      },
                      {
                        min: 3,
                        max: 20,
                        message: '用户名长度应在3-20个字符之间',
                      },
                    ]}
                  >
                    <Input placeholder="请输入用户名" />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="email"
                    label="邮箱地址"
                    rules={[
                      {
                        required: true,
                        message: '请输入邮箱地址',
                      },
                      {
                        type: 'email',
                        message: '请输入有效的邮箱地址',
                      },
                    ]}
                  >
                    <Input placeholder="请输入邮箱地址" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="bio"
                label="个人简介"
                rules={[
                  {
                    max: 500,
                    message: '个人简介不能超过500个字符',
                  },
                ]}
              >
                <TextArea
                  placeholder="请输入个人简介"
                  rows={4}
                  showCount
                  maxLength={500}
                />
              </Form.Item>

              <Row gutter={[16, 0]}>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="timezone"
                    label="时区"
                  >
                    <Select placeholder="请选择时区">
                      <Option value="Asia/Shanghai">Asia/Shanghai (UTC+8)</Option>
                      <Option value="America/New_York">America/New_York (UTC-5)</Option>
                      <Option value="Europe/London">Europe/London (UTC+0)</Option>
                      <Option value="Asia/Tokyo">Asia/Tokyo (UTC+9)</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12}>
                  <Form.Item
                    name="language"
                    label="语言"
                  >
                    <Select placeholder="请选择语言">
                      <Option value="zh-CN">简体中文</Option>
                      <Option value="en-US">English</Option>
                      <Option value="ja-JP">日本語</Option>
                      <Option value="ko-KR">한국어</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
};