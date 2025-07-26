import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Avatar,
  Space,
  Button,
  Divider,
  List,
  Tag,
} from 'antd';
import {
  UserOutlined,
  SettingOutlined,
  BellOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useCurrentUser } from '../../hooks/useAuth';

const { Title, Text } = Typography;

/**
 * 仪表板页面组件
 */
export const DashboardPage: React.FC = () => {
  const user = useCurrentUser();
  const navigate = useNavigate();

  // 模拟数据
  const stats = [
    {
      title: '总任务数',
      value: 42,
      suffix: '个',
      valueStyle: { color: '#3f8600' },
    },
    {
      title: '已完成',
      value: 28,
      suffix: '个',
      valueStyle: { color: '#1890ff' },
    },
    {
      title: '进行中',
      value: 10,
      suffix: '个',
      valueStyle: { color: '#faad14' },
    },
    {
      title: '待处理',
      value: 4,
      suffix: '个',
      valueStyle: { color: '#ff4d4f' },
    },
  ];

  const recentActivities = [
    {
      id: 1,
      title: '完成了任务：用户注册功能开发',
      time: '2小时前',
      type: 'success',
      icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
    },
    {
      id: 2,
      title: '更新了个人资料',
      time: '4小时前',
      type: 'info',
      icon: <UserOutlined style={{ color: '#1890ff' }} />,
    },
    {
      id: 3,
      title: '新任务分配：API文档编写',
      time: '6小时前',
      type: 'warning',
      icon: <ExclamationCircleOutlined style={{ color: '#faad14' }} />,
    },
    {
      id: 4,
      title: '参加了团队会议',
      time: '1天前',
      type: 'info',
      icon: <ClockCircleOutlined style={{ color: '#1890ff' }} />,
    },
  ];

  const quickActions = [
    {
      title: '编辑个人资料',
      description: '更新您的个人信息和偏好设置',
      action: () => navigate('/profile'),
      icon: <UserOutlined />,
    },
    {
      title: '系统设置',
      description: '管理您的账户和应用程序设置',
      action: () => navigate('/settings'),
      icon: <SettingOutlined />,
    },
    {
      title: '通知中心',
      description: '查看最新的通知和消息',
      action: () => navigate('/notifications'),
      icon: <BellOutlined />,
    },
  ];

  // 获取用户显示名称
  const getUserDisplayName = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user?.username || '用户';
  };

  // 获取问候语
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return '早上好';
    if (hour < 18) return '下午好';
    return '晚上好';
  };

  return (
    <div className="space-y-6">
      {/* 欢迎区域 */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Avatar
              size={64}
              src={user?.avatar}
              icon={<UserOutlined />}
            />
            <div>
              <Title level={3} className="mb-1">
                {getGreeting()}，{getUserDisplayName()}！
              </Title>
              <Text type="secondary">
                欢迎回到您的工作台，今天也要加油哦！
              </Text>
            </div>
          </div>
          <Button
            type="primary"
            icon={<SettingOutlined />}
            onClick={() => navigate('/profile')}
          >
            编辑资料
          </Button>
        </div>
      </Card>

      {/* 统计数据 */}
      <Row gutter={[16, 16]}>
        {stats.map((stat, index) => (
          <Col xs={24} sm={12} md={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                suffix={stat.suffix}
                valueStyle={stat.valueStyle}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]}>
        {/* 快速操作 */}
        <Col xs={24} lg={12}>
          <Card title="快速操作" extra={<Button type="link">查看更多</Button>}>
            <List
              dataSource={quickActions}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button
                      key="action"
                      type="primary"
                      size="small"
                      onClick={item.action}
                    >
                      前往
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Avatar icon={item.icon} />}
                    title={item.title}
                    description={item.description}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 最近活动 */}
        <Col xs={24} lg={12}>
          <Card title="最近活动" extra={<Button type="link">查看全部</Button>}>
            <List
              dataSource={recentActivities}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={item.icon}
                    title={item.title}
                    description={
                      <Space>
                        <ClockCircleOutlined />
                        <Text type="secondary">{item.time}</Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* 系统状态 */}
      <Card title="系统状态">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <div className="text-center">
              <div className="text-2xl mb-2">🟢</div>
              <Text strong>系统运行正常</Text>
              <br />
              <Text type="secondary">所有服务运行稳定</Text>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div className="text-center">
              <div className="text-2xl mb-2">📊</div>
              <Text strong>性能良好</Text>
              <br />
              <Text type="secondary">响应时间 &lt; 100ms</Text>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div className="text-center">
              <div className="text-2xl mb-2">🔒</div>
              <Text strong>安全状态</Text>
              <br />
              <Text type="secondary">无安全威胁</Text>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
};