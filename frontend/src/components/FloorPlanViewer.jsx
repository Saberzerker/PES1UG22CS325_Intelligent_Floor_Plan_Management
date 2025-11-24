import React, { useState, useEffect } from 'react';
import { Layout, Card, List, Tag, Space } from 'antd';
import { EnvironmentOutlined, TeamOutlined } from '@ant-design/icons';
import Sidebar from './Sidebar';
import api from '../services/api';

const { Content } = Layout;

function FloorPlanViewer() {
  const [floorPlans, setFloorPlans] = useState([]);
  const [selectedFloor, setSelectedFloor] = useState(null);
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFloorPlans();
  }, []);

  const fetchFloorPlans = async () => {
    try {
      const response = await api.get('/api/floors/floor-plans/');
      setFloorPlans(response.data.results || response.data);
      if (response.data.results && response.data.results.length > 0) {
        setSelectedFloor(response.data.results[0]);
        fetchRooms(response.data.results[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch floor plans');
    } finally {
      setLoading(false);
    }
  };

  const fetchRooms = async (floorPlanId) => {
    try {
      const response = await api.get(`/api/floors/rooms/?floor_plan_id=${floorPlanId}`);
      setRooms(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch rooms');
    }
  };

  const handleFloorSelect = (floor) => {
    setSelectedFloor(floor);
    fetchRooms(floor.id);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      
      <Layout>
        <Content style={{ padding: '24px' }}>
          <div style={{ display: 'flex', gap: '24px' }}>
            <Card title="Floor Plans" style={{ flex: 1 }}>
              <List
                loading={loading}
                dataSource={floorPlans}
                renderItem={(floor) => (
                  <List.Item
                    style={{ 
                      cursor: 'pointer',
                      backgroundColor: selectedFloor?.id === floor.id ? '#00FFC8' : 'transparent'
                    }}
                    onClick={() => handleFloorSelect(floor)}
                  >
                    <List.Item.Meta
                      title={floor.name}
                      description={`Floor ${floor.floor_number}`}
                    />
                  </List.Item>
                )}
              />
            </Card>
            
            <Card title={`Rooms - ${selectedFloor?.name || 'Select Floor'}`} style={{ flex: 2 }}>
              {selectedFloor && (
                <List
                  dataSource={rooms}
                  renderItem={(room) => (
                    <List.Item>
                      <List.Item.Meta
                        title={
                          <Space>
                            <span>{room.name}</span>
                            <Tag color={room.is_active ? 'green' : 'red'}>
                              {room.is_active ? 'Active' : 'Inactive'}
                            </Tag>
                          </Space>
                        }
                        description={
                          <div>
                            <Space>
                              <span><TeamOutlined /> Capacity: {room.capacity}</span>
                              <span>Type: {room.room_type}</span>
                            </Space>
                            <div style={{ marginTop: 8 }}>
                              {room.amenities_list && room.amenities_list.map(amenity => (
                                <Tag key={amenity} size="small">{amenity.replace('_', ' ')}</Tag>
                              ))}
                            </div>
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              )}
            </Card>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

export default FloorPlanViewer;