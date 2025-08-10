'use client';

import React, { useState } from 'react';
import { Card, Select, Button, Table, Typography, Space, Alert, Tabs } from 'antd';
import { EyeOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useETLStore } from '@/store/etlStore';

const { Title, Text } = Typography;
const { Option } = Select;

export const SheetPreview: React.FC = () => {
  const { 
    sessionData, 
    isLoading, 
    previewSheets, 
    setCurrentStep,
    addLog 
  } = useETLStore();

  const [selectedMaster, setSelectedMaster] = useState<string>(sessionData.masterSheet || '');
  const [selectedTarget, setSelectedTarget] = useState<string>(sessionData.targetSheet || '');

  const handlePreview = async () => {
    if (!selectedMaster || !selectedTarget) {
      addLog('Please select both Master and Target sheets', 'warning');
      return;
    }

    if (selectedMaster === selectedTarget) {
      addLog('Master and Target sheets must be different', 'warning');
      return;
    }

    await previewSheets(selectedMaster, selectedTarget);
  };

  const handleNext = () => {
    if (sessionData.previewData) {
      setCurrentStep(2);
    }
  };

  const createTableColumns = (data: any[]) => {
    if (!data || data.length === 0) return [];
    
    const firstRow = data[0];
    return Object.keys(firstRow).slice(0, 8).map((key) => ({
      title: key,
      dataIndex: key,
      key,
      width: 150,
      ellipsis: true,
      render: (text: any) => (
        <span className="text-sm">
          {text !== null && text !== undefined ? String(text) : '-'}
        </span>
      ),
    }));
  };

  const createTableData = (data: any[]) => {
    if (!data || data.length === 0) return [];
    
    return data.slice(0, 10).map((row, index) => ({
      ...row,
      key: index,
    }));
  };

  const tabItems = sessionData.previewData ? [
    {
      key: sessionData.masterSheet || 'master',
      label: (
        <span>
          <EyeOutlined />
          {sessionData.masterSheet} ({sessionData.previewData[sessionData.masterSheet!]?.length || 0} rows)
        </span>
      ),
      children: (
        <Table
          columns={createTableColumns(sessionData.previewData[sessionData.masterSheet!] || [])}
          dataSource={createTableData(sessionData.previewData[sessionData.masterSheet!] || [])}
          pagination={false}
          scroll={{ x: 1200, y: 400 }}
          size="small"
          bordered
        />
      ),
    },
    {
      key: sessionData.targetSheet || 'target',
      label: (
        <span>
          <EyeOutlined />
          {sessionData.targetSheet} ({sessionData.previewData[sessionData.targetSheet!]?.length || 0} rows)
        </span>
      ),
      children: (
        <Table
          columns={createTableColumns(sessionData.previewData[sessionData.targetSheet!] || [])}
          dataSource={createTableData(sessionData.previewData[sessionData.targetSheet!] || [])}
          pagination={false}
          scroll={{ x: 1200, y: 400 }}
          size="small"
          bordered
        />
      ),
    },
  ] : [];

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Title level={2} className="text-gray-800 mb-2">
            Select and Preview Sheets
          </Title>
          <Text type="secondary" className="text-lg">
            Choose your Master BOM and Target sheets to preview the data
          </Text>
        </div>

        {/* Sheet Selection */}
        <Card className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Master BOM Sheet
              </label>
              <Select
                placeholder="Select Master BOM sheet"
                value={selectedMaster}
                onChange={setSelectedMaster}
                className="w-full"
                size="large"
              >
                {sessionData.sheetNames.map((sheet) => (
                  <Option key={sheet} value={sheet}>
                    {sheet}
                  </Option>
                ))}
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Sheet
              </label>
              <Select
                placeholder="Select Target sheet"
                value={selectedTarget}
                onChange={setSelectedTarget}
                className="w-full"
                size="large"
              >
                {sessionData.sheetNames.map((sheet) => (
                  <Option key={sheet} value={sheet}>
                    {sheet}
                  </Option>
                ))}
              </Select>
            </div>

            <div>
              <Button
                type="primary"
                icon={<EyeOutlined />}
                onClick={handlePreview}
                loading={isLoading}
                disabled={!selectedMaster || !selectedTarget || selectedMaster === selectedTarget}
                size="large"
                className="w-full"
              >
                Preview Sheets
              </Button>
            </div>
          </div>

          {selectedMaster === selectedTarget && selectedMaster && (
            <Alert
              message="Master and Target sheets must be different"
              type="warning"
              className="mt-4"
            />
          )}
        </Card>

        {/* Preview Results */}
        {sessionData.previewData && (
          <Card 
            title={
              <div className="flex items-center justify-between">
                <span>Sheet Preview</span>
                <Button
                  type="primary"
                  icon={<ArrowRightOutlined />}
                  onClick={handleNext}
                  size="small"
                >
                  Continue to Cleaning
                </Button>
              </div>
            }
            className="mb-6"
          >
            <Alert
              message="Preview loaded successfully!"
              description={`Showing first 10 rows and 8 columns of each sheet for performance.`}
              type="success"
              className="mb-4"
            />

            <Tabs
              items={tabItems}
              size="small"
              className="preview-tabs"
            />
          </Card>
        )}

        {/* Instructions */}
        {!sessionData.previewData && (
          <Card title="Instructions" className="bg-gray-50">
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                  1
                </div>
                <div>
                  <Text strong>Select Master BOM Sheet</Text>
                  <div className="text-gray-600 text-sm">
                    Choose the sheet containing your master Bill of Materials
                  </div>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                  2
                </div>
                <div>
                  <Text strong>Select Target Sheet</Text>
                  <div className="text-gray-600 text-sm">
                    Choose the sheet you want to update with Master BOM data
                  </div>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                  3
                </div>
                <div>
                  <Text strong>Preview Data</Text>
                  <div className="text-gray-600 text-sm">
                    Click "Preview Sheets" to see a sample of your data before processing
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
