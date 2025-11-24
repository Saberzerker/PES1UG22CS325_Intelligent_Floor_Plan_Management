import React, { useState, useEffect } from 'react';
import { 
  Layout, Card, Tabs, List, Button, Tag, Space, message, Modal, 
  Form, Input, Select, Table, Popconfirm, Statistic
} from 'antd';
import { 
  WarningOutlined, CheckCircleOutlined, ClockCircleOutlined,
  BarChartOutlined, LineChartOutlined, PieChartOutlined
} from '@ant-design/icons';
import Sidebar from './Sidebar';
import api from '../services/api';

const { Content } = Layout;
const { TabPane } = Tabs;

function AdminPanel() {
  const [conflicts, setConflicts] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchConflicts();
    fetchAnalytics();
  }, []);

  const fetchConflicts = async () => {
    try {
      const response = await api.get('/api/floors/conflicts/');
      setConflicts(response.data.results || response.data);
    } catch (error) {
      message.error('Failed to fetch conflicts');
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/api/analytics/dashboard/');
      setAnalytics(response.data);
    } catch (error) {
      message.error('Failed to fetch analytics');
    }
  };

  const handleResolveConflict = async (conflictId, manuallyResolved = false) => {
    try {
      await api.patch(`/api/floors/conflicts/${conflictId}/`, {
        manually_resolved: manuallyResolved
      });
      message.success('Conflict marked as reviewed');
      fetchConflicts();
    } catch (error) {
      message.error('Failed to update conflict');
    }
  };

  const getConflictStatus = (conflict) => {
    if (conflict.manually_resolved) {
      return <Tag color="green">Resolved</Tag>;
    }
    return <Tag color="orange">Pending</Tag>;
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      
      <Layout>
        <Content style={{ padding: '24px' }}>
          <Tabs defaultActiveKey="conflicts">
            <TabPane 
              tab={
                <span>
                  <WarningOutlined />
                  Conflicts ({conflicts.filter(c => !c.manually_resolved).length})
                </span>
              } 
              key="conflicts"
            >
              <Card title="Conflict Management">
                <List
                  dataSource={conflicts}
                  renderItem={(conflict) => (
                    <List.Item
                      actions={[
                        <Space>
                          <Button 
                            type="primary" 
                            size="small"
                            onClick={() => handleResolveConflict(conflict.id, true)}
                          >
                            Mark Reviewed
                          </Button>
                        </Space>
                      ]}
                    >
                      <List.Item.Meta
                        title={
                          <Space>
                            <span>Floor Plan: {conflict.floor_plan}</span>
                            {getConflictStatus(conflict)}
                          </Space>
                        }
                        description={
                          <div>
                            <p><strong>Users:</strong> {conflict.user_a} vs {conflict.user_b}</p>
                            <p><strong>Strategy:</strong> {conflict.resolution_strategy}</p>
                            <p><strong>Time:</strong> {new Date(conflict.created_at).toLocaleString()}</p>
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>
            </TabPane>
            
            <TabPane tab={<BarChartOutlined />} key="analytics">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
                <Card>
                  <Statistic 
                    title="Total Bookings" 
                    value={analytics.bookings_today || 0} 
                    prefix={<BarChartOutlined />} 
                  />
                </Card>
                <Card>
                  <Statistic 
                    title="Active Meetings" 
                    value={analytics.active_meetings || 0} 
                    prefix={<ClockCircleOutlined />} 
                  />
                </Card>
                <Card>
                  <Statistic 
                    title="Rooms Booked" 
                    value={analytics.rooms_booked || 0} 
                    prefix={<CheckCircleOutlined />} 
                  />
                </Card>
              </div>
            </TabPane>
            
            <TabPane tab={<LineChartOutlined />} key="monitoring">
              <Card title="System Monitoring">
                <p>API Response Time: 45ms</p>
                <p>DB Queries per Request: 8</p>
                <p>Cache Hit Rate: 87%</p>
              </Card>
            </TabPane>
          </Tabs>
        </Content>
      </Layout>
    </Layout>
  );
}

export default AdminPanel;