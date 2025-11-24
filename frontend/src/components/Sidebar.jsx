import React, { useState, useEffect } from 'react';
import { Layout, Menu, Badge } from 'antd';
import { 
  AppstoreOutlined, 
  CalendarOutlined, 
  SettingOutlined,
  BookOutlined,
  EnvironmentOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const { Sider } = Layout;

function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [conflictsCount, setConflictsCount] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  useEffect(() => {
    if (user?.is_staff) {
      fetchConflictsCount();
    }
  }, [user]);

  const fetchConflictsCount = async () => {
    try {
      const response = await api.get('/api/analytics/dashboard/');
      setConflictsCount(response.data.conflicts_pending || 0);
    } catch (error) {
      console.error('Failed to fetch conflicts:', error);
    }
  };

  const menuItems = user?.is_staff ? [
    {
      key: '/floor-plans',
      icon: <AppstoreOutlined />,
      label: 'Floor Plan',
    },
    {
      key: '/booking',
      icon: <CalendarOutlined />,
      label: 'Book Meeting Room',
    },
    {
      key: '/admin',
      icon: <SettingOutlined />,
      label: (
        <span>
          Admin Panel
          {conflictsCount > 0 && <Badge count={conflictsCount} style={{ marginLeft: 8 }} />}
        </span>
      ),
    },
  ] : [
    {
      key: '/booking',
      icon: <CalendarOutlined />,
      label: 'Book Meeting Room',
    },
    {
      key: '/my-bookings',
      icon: <BookOutlined />,
      label: 'My Bookings',
    },
    {
      key: '/view-floor-plan',
      icon: <EnvironmentOutlined />,
      label: 'View Floor Plan',
    },
  ];

  return (
    <Sider 
      collapsible 
      collapsed={collapsed} 
      onCollapse={setCollapsed}
      className="sidebar"
      theme="dark"
    >
      <Menu
        theme="dark"
        mode="vertical"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        className="sidebar-menu"
      />
      
      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot online"></span>
          Online
        </div>
      </div>
    </Sider>
  );
}

export default Sidebar;