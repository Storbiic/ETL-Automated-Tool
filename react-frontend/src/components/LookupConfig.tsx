'use client';

import React, { useState } from 'react';
import { Card, Select, Button, Typography, Alert } from 'antd';
import { SearchOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useETLStore } from '@/store/etlStore';

const { Title, Text } = Typography;
const { Option } = Select;

export const LookupConfig: React.FC = () => {
  const { performLookup, isLoading, sessionData, nextStep } = useETLStore();
  const [selectedColumn, setSelectedColumn] = useState<string>('');

  const handleLookup = async () => {
    if (selectedColumn) {
      await performLookup(selectedColumn);
    }
  };

  const handleNext = () => {
    if (sessionData.lookupResult) {
      nextStep();
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Title level={2} className="text-gray-800 mb-2">
            Lookup Configuration
          </Title>
          <Text type="secondary" className="text-lg">
            Select the column to use for lookup operations
          </Text>
        </div>

        <Card className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lookup Column
              </label>
              <Select
                placeholder="Select lookup column"
                value={selectedColumn}
                onChange={setSelectedColumn}
                className="w-full"
                size="large"
              >
                {sessionData.availableColumns.map((column) => (
                  <Option key={column} value={column}>
                    {column}
                  </Option>
                ))}
              </Select>
            </div>

            <div>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleLookup}
                loading={isLoading}
                disabled={!selectedColumn}
                size="large"
                className="w-full"
              >
                Perform Lookup
              </Button>
            </div>
          </div>
        </Card>

        {sessionData.lookupResult && (
          <Alert
            message="Lookup completed successfully!"
            type="success"
            action={
              <Button
                type="primary"
                icon={<ArrowRightOutlined />}
                onClick={handleNext}
                size="small"
              >
                View Results
              </Button>
            }
          />
        )}
      </div>
    </div>
  );
};
