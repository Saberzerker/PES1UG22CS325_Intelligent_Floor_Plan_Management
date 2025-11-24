// FEATURE 1A - Floor plan upload
import React, { useState } from 'react';
import { Upload, Button, message, Card, Progress } from 'antd';
import { UploadOutlined, FileImageOutlined } from '@ant-design/icons';

function FloorPlanUpload({ onUpload }) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleUpload = async (file) => {
    setUploading(true);
    setProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    try {
      // In real implementation, this would upload the file
      // For now, just simulate success
      setTimeout(() => {
        setProgress(100);
        setUploading(false);
        clearInterval(progressInterval);
        message.success('Floor plan uploaded successfully!');
        onUpload && onUpload(file);
      }, 2000);
    } catch (error) {
      setUploading(false);
      clearInterval(progressInterval);
      message.error('Upload failed');
    }

    return false; // Prevent default upload behavior
  };

  const uploadProps = {
    beforeUpload: handleUpload,
    showUploadList: false,
    accept: '.jpg,.jpeg,.png,.pdf',
    maxCount: 1,
  };

  return (
    <Card title="Upload Floor Plan" style={{ maxWidth: 400 }}>
      <Upload {...uploadProps}>
        <Button 
          icon={<UploadOutlined />} 
          loading={uploading}
          disabled={uploading}
          size="large"
        >
          {uploading ? 'Uploading...' : 'Select Floor Plan Image'}
        </Button>
      </Upload>
      
      {uploading && (
        <div style={{ marginTop: 16 }}>
          <Progress percent={progress} status="active" />
          <p style={{ marginTop: 8, textAlign: 'center' }}>
            {progress < 100 ? 'Processing...' : 'Upload complete!'}
          </p>
        </div>
      )}
      
      <div style={{ marginTop: 16, fontSize: '12px', color: '#666' }}>
        <FileImageOutlined style={{ marginRight: 8 }} />
        Supported formats: JPG, PNG, PDF (Max: 10MB)
      </div>
    </Card>
  );
}

export default FloorPlanUpload;