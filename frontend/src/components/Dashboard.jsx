import React, { useState, useEffect } from 'react';
import { Layout, Row, Col, Card, Statistic, Typography, Carousel, Avatar, Dropdown } from 'antd';
import { 
  CalendarOutlined, 
  TeamOutlined, 
  WarningOutlined, 
  ClockCircleOutlined,
  UserOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import Sidebar from './Sidebar';
import '../styles/Dashboard.css';

const { Header, Content } = Layout;
const { Title } = Typography;

function Dashboard() {
  const [metrics, setMetrics] = useState({});
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await api.get('/api/analytics/dashboard/');
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const menuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: logout,
    },
  ];

  const MetricCard = ({ title, value, icon, warning, onClick }) => (
    <Card 
      className="metric-card" 
      onClick={onClick}
      hoverable
    >
      {warning && <WarningOutlined className="warning-icon" />}
      <Statistic
        title={title}
        value={value}
        prefix={icon}
        valueStyle={{ color: '#00FFC8' }}
      />
    </Card>
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      
      <Layout>
        <Header className="dashboard-header">
          <div className="header-left">
            <Title level={3} style={{ color: '#FFFFFF', margin: 0 }}>Floorings</Title>
          </div>
          <div className="header-right">
            <div className="status-indicator">
              <span className="status-dot online"></span>
              Online
            </div>
            <Dropdown menu={{ items: menuItems }} trigger={['click']}>
              <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
            </Dropdown>
          </div>
        </Header>
        
        <Content className="dashboard-content">
          <div className="welcome-section">
            <Title level={2} style={{ color: '#FFFFFF' }}>Welcome, {user?.username}</Title>
          </div>
          
          <Row gutter={[24, 24]} className="metrics-row">
            {user?.is_staff ? (
              <>
                <Col xs={24} sm={12} lg={6}>
                  <MetricCard
                    title="Rooms Booked"
                    value={metrics.rooms_booked || 0}
                    icon={<TeamOutlined />}
                    onClick={() => window.location.href = '/booking'}
                  />
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <MetricCard
                    title="Bookings Today"
                    value={metrics.bookings_today || 0}
                    icon={<CalendarOutlined />}
                    onClick={() => window.location.href = '/booking'}
                  />
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <MetricCard
                    title="Conflicts Pending"
                    value={metrics.conflicts_pending || 0}
                    icon={<WarningOutlined />}
                    warning={metrics.conflicts_pending > 0}
                    onClick={() => window.location.href = '/admin'}
                  />
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <MetricCard
                    title="Active Meetings"
                    value={metrics.active_meetings || 0}
                    icon={<ClockCircleOutlined />}
                    onClick={() => window.location.href = '/booking'}
                  />
                </Col>
              </>
            ) : (
              <>
                <Col xs={24} sm={12} lg={6}>
                  <MetricCard
                    title="Meetings Booked"
                    value={metrics.meetings_booked || 0}
                    icon={<CalendarOutlined />}
                    onClick={() => window.location.href = '/my-bookings'}
                  />
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <MetricCard
                    title="Available Meeting Rooms"
                    value={metrics.available_rooms || 0}
                    icon={<TeamOutlined />}
                    onClick={() => window.location.href = '/booking'}
                  />
                </Col>
              </>
            )}
          </Row>
          
          <div className="trusted-by-section">
            <Title level={4} style={{ color: '#FFFFFF', textAlign: 'center' }}>Trusted By</Title>
            <Carousel autoplay className="trusted-carousel">
              <div className="carousel-item">
                <Title level={3} style={{ color: '#C0C0C0' }}>MoveInSync</Title>
              </div>
              <div className="carousel-item">
                <Title level={3} style={{ color: '#C0C0C0' }}>MoveInSync</Title>
              </div>
              <div className="carousel-item">
                <Title level={3} style={{ color: '#C0C0C0' }}>MoveInSync</Title>
              </div>
            </Carousel>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

export default Dashboard;