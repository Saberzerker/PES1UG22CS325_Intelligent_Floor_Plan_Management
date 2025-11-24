import React, { useState, useEffect } from 'react';
import { 
  Layout, Card, Form, Input, DatePicker, TimePicker, Select, Button, 
  List, message, Checkbox, Space, Tag, Statistic
} from 'antd';
import { ClockCircleOutlined, TeamOutlined, EnvironmentOutlined } from '@ant-design/icons';
import Sidebar from './Sidebar';
import api from '../services/api';
import moment from 'moment';

const { Content } = Layout;
const { Option } = Select;
const { RangePicker } = DatePicker;

function RoomBooking() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [form] = Form.useForm();

  const amenities = [
    { label: 'Projector', value: 'projector' },
    { label: 'Whiteboard', value: 'whiteboard' },
    { label: 'Video Conference', value: 'video_conference' },
    { label: 'TV Monitor', value: 'tv_monitor' },
    { label: 'Premium Audio', value: 'premium_audio' },
    { label: 'Natural Light', value: 'natural_light' },
    { label: 'Kitchen Access', value: 'kitchen_access' },
  ];

  const handleSearch = async (values) => {
    setLoading(true);
    try {
      const startTime = values.timeRange[0].format('YYYY-MM-DDTHH:mm:ssZ');
      const endTime = values.timeRange[1].format('YYYY-MM-DDTHH:mm:ssZ');
      
      const response = await api.post('/api/bookings/recommend/', {
        participants_count: values.participants,
        start_time: startTime,
        end_time: endTime,
        required_amenities: values.amenities || [],
        preferred_floor: values.floor
      });
      
      setRecommendations(response.data);
    } catch (error) {
      message.error('Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleBook = async (room) => {
    try {
      const values = form.getFieldsValue();
      const startTime = values.timeRange[0].format('YYYY-MM-DDTHH:mm:ssZ');
      const endTime = values.timeRange[1].format('YYYY-MM-DDTHH:mm:ssZ');
      
      await api.post('/api/bookings/bookings/', {
        room: room.id,
        start_time: startTime,
        end_time: endTime,
        participants_count: values.participants,
        purpose: values.purpose
      });
      
      message.success('Room booked successfully!');
      setSelectedRoom(null);
    } catch (error) {
      message.error('Booking failed');
    }
  };

  const getAmenityTags = (room) => {
    return amenities
      .filter(amenity => room.amenities && room.amenities.includes(amenity.value))
      .map(amenity => (
        <Tag key={amenity.value} color="geekblue">{amenity.label}</Tag>
      ));
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      
      <Layout>
        <Content style={{ padding: '24px' }}>
          <Card title="Find Meeting Room" style={{ marginBottom: 24 }}>
            <Form form={form} onFinish={handleSearch} layout="vertical">
              <Form.Item 
                name="participants" 
                label="Number of Participants" 
                rules={[{ required: true }]}
              >
                <Input type="number" min={1} />
              </Form.Item>
              
              <Form.Item 
                name="timeRange" 
                label="Meeting Time" 
                rules={[{ required: true }]}
              >
                <RangePicker showTime format="YYYY-MM-DD HH:mm" />
              </Form.Item>
              
              <Form.Item name="floor" label="Preferred Floor">
                <Select allowClear>
                  <Option value={1}>Floor 1</Option>
                  <Option value={2}>Floor 2</Option>
                  <Option value={3}>Floor 3</Option>
                </Select>
              </Form.Item>
              
              <Form.Item name="amenities" label="Required Amenities">
                <Checkbox.Group options={amenities} />
              </Form.Item>
              
              <Form.Item name="purpose" label="Purpose">
                <Input.TextArea />
              </Form.Item>
              
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading}>
                  Get Recommendations
                </Button>
              </Form.Item>
            </Form>
          </Card>
          
          {recommendations.length > 0 && (
            <Card title="Recommended Rooms">
              <List
                dataSource={recommendations}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <Button 
                        type="primary" 
                        onClick={() => handleBook(item)}
                        disabled={selectedRoom && selectedRoom.id !== item.id}
                      >
                        Book Now
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      title={
                        <Space>
                          <span>{item.name}</span>
                          <Tag color="green">Floor {item.floor_number}</Tag>
                        </Space>
                      }
                      description={
                        <div>
                          <Space>
                            <Statistic 
                              title="Score" 
                              value={Math.round(item.score)} 
                              prefix={<span>⭐</span>} 
                              valueStyle={{ fontSize: '16px' }}
                            />
                            <Statistic 
                              title="Capacity" 
                              value={item.capacity} 
                              prefix={<TeamOutlined />} 
                            />
                          </Space>
                          <div style={{ marginTop: 8 }}>
                            {getAmenityTags(item)}
                          </div>
                          {item.score_breakdown && (
                            <div style={{ marginTop: 8, fontSize: '12px', color: '#666' }}>
                              <strong>Score breakdown:</strong> 
                              User pref: {item.score_breakdown.user_preference.toFixed(1)}, 
                              Capacity: {item.score_breakdown.capacity_match.toFixed(1)}, 
                              Amenities: {item.score_breakdown.amenities.toFixed(1)}
                            </div>
                          )}
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>
          )}
        </Content>
      </Layout>
    </Layout>
  );
}

export default RoomBooking;