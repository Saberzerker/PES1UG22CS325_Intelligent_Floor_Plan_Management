// FEATURE 3 - Room recommendations
import React, { useState, useEffect } from 'react';
import { Card, List, Tag, Space, Statistic } from 'antd';
import { TeamOutlined } from '@ant-design/icons';

function RoomRecommendations({ recommendations, onBook }) {
  const amenities = [
    { label: 'Projector', value: 'projector' },
    { label: 'Whiteboard', value: 'whiteboard' },
    { label: 'Video Conference', value: 'video_conference' },
    { label: 'TV Monitor', value: 'tv_monitor' },
    { label: 'Premium Audio', value: 'premium_audio' },
    { label: 'Natural Light', value: 'natural_light' },
    { label: 'Kitchen Access', value: 'kitchen_access' },
  ];

  const getAmenityTags = (room) => {
    return amenities
      .filter(amenity => room.amenities && room.amenities.includes(amenity.value))
      .map(amenity => (
        <Tag key={amenity.value} color="geekblue">{amenity.label}</Tag>
      ));
  };

  if (!recommendations || recommendations.length === 0) {
    return <Card title="Recommended Rooms">No recommendations available</Card>;
  }

  return (
    <Card title="Recommended Rooms">
      <List
        dataSource={recommendations}
        renderItem={(item) => (
          <List.Item
            actions={[
              <button 
                className="book-button"
                onClick={() => onBook && onBook(item)}
              >
                Book Now
              </button>
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
  );
}

export default RoomRecommendations;