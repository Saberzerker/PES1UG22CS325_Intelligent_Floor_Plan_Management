import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Typography } from 'antd';
import { useAuth } from '../contexts/AuthContext';
import '../styles/LoginPage.css';

const { Title } = Typography;

function LoginPage() {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const onFinish = async (values) => {
    setLoading(true);
    const success = await login(values.username, values.password);
    setLoading(false);
    
    if (!success) {
      message.error('Invalid credentials');
    }
  };

  return (
    <div className="login-container">
      <div className="login-flash">
        <Title level={1} className="login-title">Floorings</Title>
      </div>
      
      <div className="login-content">
        <Title level={2} className="login-subtitle">Meeting & Bookings</Title>
        
        <div className="login-buttons">
          <Card className="login-card">
            <Title level={4}>Plan your floor</Title>
            <p>Manage floor plans and rooms</p>
          </Card>
          
          <Card className="login-card">
            <Title level={4}>Book Meeting Room</Title>
            <p>Find and reserve meeting spaces</p>
          </Card>
        </div>
        
        <Card className="login-form-card">
          <Form onFinish={onFinish} layout="vertical">
            <Form.Item
              name="username"
              rules={[{ required: true, message: 'Please input your username!' }]}
            >
              <Input placeholder="Username" />
            </Form.Item>
            
            <Form.Item
              name="password"
              rules={[{ required: true, message: 'Please input your password!' }]}
            >
              <Input.Password placeholder="Password" />
            </Form.Item>
            
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block>
                Login
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </div>
    </div>
  );
}

export default LoginPage;