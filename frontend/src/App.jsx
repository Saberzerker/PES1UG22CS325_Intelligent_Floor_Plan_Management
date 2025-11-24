// Main App component
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Spin } from 'antd';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import FloorPlanManagement from './components/FloorPlanManagement';
import RoomBooking from './components/RoomBooking';
import AdminPanel from './components/AdminPanel';
import MyBookings from './components/MyBookings';
import FloorPlanViewer from './components/FloorPlanViewer';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

const { Content } = Layout;

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#000000' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <Layout style={{ minHeight: '100vh', backgroundColor: '#000000' }}>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/floor-plans" element={<FloorPlanManagement />} />
        <Route path="/booking" element={<RoomBooking />} />
        <Route path="/admin" element={<AdminPanel />} />
        <Route path="/my-bookings" element={<MyBookings />} />
        <Route path="/view-floor-plan" element={<FloorPlanViewer />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;