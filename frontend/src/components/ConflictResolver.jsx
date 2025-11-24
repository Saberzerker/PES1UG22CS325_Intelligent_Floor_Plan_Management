// FEATURE 1B - Conflict resolver
import React, { useState } from 'react';
import { Modal, Button, List, Tag, Space, Typography } from 'antd';
import { WarningOutlined, CheckCircleOutlined } from '@ant-design/icons';

const { Text } = Typography;

function ConflictResolver({ visible, conflicts, onResolve, onCancel }) {
  const [resolving, setResolving] = useState(false);

  const handleResolve = async (strategy) => {
    setResolving(true);
    try {
      await onResolve(strategy);
    } finally {
      setResolving(false);
    }
  };

  const renderConflictDetails = (conflict) => (
    <div>
      <p><Text strong>Conflict in field:</Text> {conflict.field}</p>
      <p><Text type="danger">Your version:</Text> {conflict.yours}</p>
      <p><Text type="success">Server version:</Text> {conflict.theirs}</p>
      <p><Text>Base version:</Text> {conflict.base}</p>
    </div>
  );

  return (
    <Modal
      title={
        <Space>
          <WarningOutlined style={{ color: '#FFD700' }} />
          Version Conflict Detected
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      width={600}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
        <Button 
          key="server" 
          onClick={() => handleResolve('USE_SERVER')}
          loading={resolving}
        >
          Use Server Version
        </Button>,
        <Button 
          key="mine" 
          type="primary" 
          onClick={() => handleResolve('USE_MINE')}
          loading={resolving}
        >
          Use My Version
        </Button>,
      ]}
      centered
    >
      <div>
        <p>A conflict occurred while saving your changes. Choose how to resolve it:</p>
        
        {conflicts && conflicts.length > 0 && (
          <List
            dataSource={conflicts}
            renderItem={(conflict) => (
              <List.Item>
                <List.Item.Meta
                  title={<Tag color="orange">Field: {conflict.field}</Tag>}
                  description={renderConflictDetails(conflict)}
                />
              </List.Item>
            )}
          />
        )}
      </div>
    </Modal>
  );
}

export default ConflictResolver;