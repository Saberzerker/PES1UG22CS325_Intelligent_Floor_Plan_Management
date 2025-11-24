import React, { useState, useEffect } from 'react';
import { 
  Layout, Card, Button, Upload, message, List, Modal, Form, Input, 
  Select, Table, Space, Popconfirm 
} from 'antd';
import { 
  UploadOutlined, EditOutlined, HistoryOutlined, DeleteOutlined 
} from '@ant-design/icons';
import Sidebar from './Sidebar';
import api from '../services/api';

const { Content } = Layout;
const { Option } = Select;

function FloorPlanManagement() {
  const [floorPlans, setFloorPlans] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFloorPlan, setSelectedFloorPlan] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRoom, setEditingRoom] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchFloorPlans();
  }, []);

  const fetchFloorPlans = async () => {
    try {
      const response = await api.get('/api/floors/floor-plans/');
      setFloorPlans(response.data.results || response.data);
    } catch (error) {
      message.error('Failed to fetch floor plans');
    }
  };

  const fetchRooms = async (floorPlanId) => {
    try {
      const response = await api.get(`/api/floors/rooms/?floor_plan_id=${floorPlanId}`);
      setRooms(response.data.results || response.data);
    } catch (error) {
      message.error('Failed to fetch rooms');
    }
  };

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('name', file.name);
    formData.append('image', file);
    formData.append('floor_number', 1); // Default

    try {
      await api.post('/api/floors/floor-plans/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      message.success('Floor plan uploaded successfully');
      fetchFloorPlans();
    } catch (error) {
      message.error('Upload failed');
    }
  };

  const handleEditRoom = (room) => {
    setEditingRoom(room);
    form.setFieldsValue(room);
    setModalVisible(true);
  };

  const handleDeleteRoom = async (roomId) => {
    try {
      await api.delete(`/api/floors/rooms/${roomId}/`);
      message.success('Room deleted');
      if (selectedFloorPlan) {
        fetchRooms(selectedFloorPlan.id);
      }
    } catch (error) {
      message.error('Delete failed');
    }
  };

  const handleSaveRoom = async (values) => {
    try {
      if (editingRoom) {
        await api.put(`/api/floors/rooms/${editingRoom.id}/`, values);
        message.success('Room updated');
      } else {
        values.floor_plan = selectedFloorPlan.id;
        await api.post('/api/floors/rooms/', values);
        message.success('Room created');
      }
      setModalVisible(false);
      form.resetFields();
      setEditingRoom(null);
      fetchRooms(selectedFloorPlan.id);
    } catch (error) {
      message.error('Save failed');
    }
  };

  const columns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Capacity', dataIndex: 'capacity', key: 'capacity' },
    { title: 'Type', dataIndex: 'room_type', key: 'room_type' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button icon={<EditOutlined />} onClick={() => handleEditRoom(record)} />
          <Popconfirm
            title="Delete this room?"
            onConfirm={() => handleDeleteRoom(record.id)}
          >
            <Button icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      
      <Layout>
        <Content style={{ padding: '24px' }}>
          <div style={{ display: 'flex', gap: '24px' }}>
            {/* Floor Plans List */}
            <Card title="Floor Plans" style={{ flex: 1 }}>
              <Upload
                beforeUpload={(file) => {
                  handleUpload(file);
                  return false;
                }}
                showUploadList={false}
              >
                <Button icon={<UploadOutlined />} style={{ marginBottom: 16 }}>
                  Upload Floor Plan
                </Button>
              </Upload>
              
              <List
                dataSource={floorPlans}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <Button onClick={() => setSelectedFloorPlan(item)}>Edit</Button>,
                      <Button icon={<HistoryOutlined />}>History</Button>
                    ]}
                  >
                    <List.Item.Meta
                      title={item.name}
                      description={`Floor ${item.floor_number}`}
                    />
                  </List.Item>
                )}
              />
            </Card>
            
            {/* Rooms Management */}
            {selectedFloorPlan && (
              <Card title={`Rooms - ${selectedFloorPlan.name}`} style={{ flex: 2 }}>
                <Button 
                  type="primary" 
                  onClick={() => {
                    setEditingRoom(null);
                    form.resetFields();
                    setModalVisible(true);
                  }}
                  style={{ marginBottom: 16 }}
                >
                  Add Room
                </Button>
                
                <Table
                  columns={columns}
                  dataSource={rooms}
                  rowKey="id"
                  loading={loading}
                />
              </Card>
            )}
          </div>
          
          {/* Room Modal */}
          <Modal
            title={editingRoom ? "Edit Room" : "Add Room"}
            open={modalVisible}
            onCancel={() => setModalVisible(false)}
            footer={null}
          >
            <Form form={form} onFinish={handleSaveRoom} layout="vertical">
              <Form.Item name="name" label="Name" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="capacity" label="Capacity" rules={[{ required: true }]}>
                <Input type="number" />
              </Form.Item>
              <Form.Item name="room_type" label="Type" rules={[{ required: true }]}>
                <Select>
                  <Option value="MEETING">Meeting</Option>
                  <Option value="CONFERENCE">Conference</Option>
                  <Option value="HUDDLE">Huddle</Option>
                </Select>
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit">Save</Button>
              </Form.Item>
            </Form>
          </Modal>
        </Content>
      </Layout>
    </Layout>
  );
}

export default FloorPlanManagement;