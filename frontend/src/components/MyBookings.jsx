import React, { useState, useEffect } from 'react';
import { Layout, Card, List, Tag, Button, Space, message, Popconfirm } from 'antd';
import { CalendarOutlined, DeleteOutlined } from '@ant-design/icons';
import Sidebar from './Sidebar';
import api from '../services/api';

const { Content } = Layout;

function MyBookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    try {
      const response = await api.get('/api/bookings/bookings/');
      setBookings(response.data.results || response.data);
    } catch (error) {
      message.error('Failed to fetch bookings');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (bookingId) => {
    try {
      await api.delete(`/api/bookings/bookings/${bookingId}/`);
      message.success('Booking cancelled');
      fetchBookings();
    } catch (error) {
      message.error('Failed to cancel booking');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'CONFIRMED': return 'green';
      case 'CANCELLED': return 'red';
      default: return 'blue';
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      
      <Layout>
        <Content style={{ padding: '24px' }}>
          <Card title="My Bookings">
            <List
              loading={loading}
              dataSource={bookings}
              renderItem={(booking) => (
                <List.Item
                  actions={[
                    booking.status === 'CONFIRMED' && (
                      <Popconfirm
                        title="Cancel this booking?"
                        onConfirm={() => handleCancel(booking.id)}
                      >
                        <Button icon={<DeleteOutlined />} danger size="small">
                          Cancel
                        </Button>
                      </Popconfirm>
                    )
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <span>{booking.room_name}</span>
                        <Tag color={getStatusColor(booking.status)}>{booking.status}</Tag>
                      </Space>
                    }
                    description={
                      <div>
                        <p><strong>Time:</strong> {new Date(booking.start_time).toLocaleString()} - {new Date(booking.end_time).toLocaleString()}</p>
                        <p><strong>Participants:</strong> {booking.participants_count}</p>
                        {booking.purpose && <p><strong>Purpose:</strong> {booking.purpose}</p>}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Content>
      </Layout>
    </Layout>
  );
}

export default MyBookings;