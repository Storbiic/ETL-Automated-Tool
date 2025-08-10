'use client';

import React from 'react';
import { Card, Button, Typography, Alert } from 'antd';
import { SyncOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useETLStore } from '@/store/etlStore';

const { Title, Text } = Typography;

export const MasterUpdates: React.FC = () => {
  const { processUpdates, isLoading, sessionData } = useETLStore();

  const handleUpdate = async () => {
    await processUpdates();
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Title level={2} className="text-gray-800 mb-2">
            Master BOM Updates
          </Title>
          <Text type="secondary" className="text-lg">
            Apply updates to the Master BOM
          </Text>
        </div>

        <Card className="mb-6">
          <div className="text-center py-8">
            <Button
              type="primary"
              icon={<SyncOutlined />}
              onClick={handleUpdate}
              loading={isLoading}
              size="large"
            >
              Process Updates
            </Button>
          </div>
        </Card>

        {sessionData.updateResult && (
          <Alert
            message="Updates completed successfully!"
            type="success"
            icon={<CheckCircleOutlined />}
          />
        )}
      </div>
    </div>
  );
};
