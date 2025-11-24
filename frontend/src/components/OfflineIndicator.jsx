// FEATURE 2 - Offline indicator
import React, { useState, useEffect } from 'react';
import { Modal, Button } from 'antd';
import { WifiOutlined, ExclamationCircleOutlined } from '@ant-design/icons';

function OfflineIndicator({ isOnline, pendingChanges, onReload, onContinueOffline }) {
  const [showOfflineModal, setShowOfflineModal] = useState(false);

  useEffect(() => {
    if (!isOnline && !showOfflineModal) {
      setShowOfflineModal(true);
    }
  }, [isOnline, showOfflineModal]);

  const handleReload = () => {
    setShowOfflineModal(false);
    onReload && onReload();
  };

  const handleContinueOffline = () => {
    setShowOfflineModal(false);
    onContinueOffline && onContinueOffline();
  };

  return (
    <>
      {/* Status Indicator */}
      <div className="status-indicator">
        {isOnline ? (
          <>
            <span className="status-dot online"></span>
            Online
          </>
        ) : (
          <>
            <span className="status-dot offline"></span>
            Offline {pendingChanges > 0 && `(${pendingChanges} pending)`}
          </>
        )}
      </div>

      {/* Offline Modal */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ExclamationCircleOutlined style={{ color: '#FFD700' }} />
            You're Offline
          </div>
        }
        open={showOfflineModal}
        onCancel={handleContinueOffline}
        footer={[
          <Button key="reload" onClick={handleReload}>
            Reload Page
          </Button>,
          <Button key="continue" type="primary" onClick={handleContinueOffline}>
            Continue Offline
          </Button>,
        ]}
        centered
      >
        <p>The server is unreachable. You can:</p>
        <ul>
          <li>Continue working (changes saved locally and will sync when online)</li>
          <li>Reload the page to try reconnecting</li>
        </ul>
      </Modal>
    </>
  );
}

export default OfflineIndicator;