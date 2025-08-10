'use client';

import React from 'react';
import { Card, Button, Typography, Alert } from 'antd';
import { ClearOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useETLStore } from '@/store/etlStore';

const { Title, Text } = Typography;

export const DataCleaning: React.FC = () => {
  const { cleanData, isLoading, sessionData, nextStep } = useETLStore();

  const handleClean = async () => {
    await cleanData();
  };

  const handleNext = () => {
    if (sessionData.cleanResult) {
      nextStep();
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Title level={2} className="text-gray-800 mb-2">
            Data Cleaning
          </Title>
          <Text type="secondary" className="text-lg">
            Clean and prepare your data for processing
          </Text>
        </div>

        <Card className="mb-6">
          <div className="text-center py-8">
            <Button
              type="primary"
              icon={<ClearOutlined />}
              onClick={handleClean}
              loading={isLoading}
              size="large"
            >
              Clean Data
            </Button>
          </div>
        </Card>

        {sessionData.cleanResult && (
          <Alert
            message="Data cleaned successfully!"
            type="success"
            action={
              <Button
                type="primary"
                icon={<ArrowRightOutlined />}
                onClick={handleNext}
                size="small"
              >
                Continue to Lookup
              </Button>
            }
          />
        )}
      </div>
    </div>
  );
};
