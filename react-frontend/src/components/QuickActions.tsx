'use client';

import React from 'react';
import { Card, Button, Space, Typography, Tooltip } from 'antd';
import { 
  EyeOutlined, 
  ThunderboltOutlined, 
  DownloadOutlined,
  RocketOutlined 
} from '@ant-design/icons';
import { useETLStore } from '@/store/etlStore';
import { useTheme } from '@/contexts/ThemeContext';

const { Title, Text } = Typography;

export const QuickActions: React.FC = () => {
  const {
    sessionData,
    isLoading,
    quickPreview,
    quickProcess,
    quickDownload,
    addLog
  } = useETLStore();
  const { isDark } = useTheme();

  const handleQuickPreview = async () => {
    try {
      await quickPreview();
    } catch (error) {
      addLog(error instanceof Error ? error.message : 'Quick preview failed', 'error');
    }
  };

  const handleQuickProcess = async () => {
    try {
      await quickProcess();
    } catch (error) {
      addLog(error instanceof Error ? error.message : 'Quick process failed', 'error');
    }
  };

  const handleQuickDownload = () => {
    try {
      quickDownload();
    } catch (error) {
      addLog(error instanceof Error ? error.message : 'Quick download failed', 'error');
    }
  };

  const canPreview = sessionData.fileId && sessionData.sheetNames.length >= 2;
  const canProcess = sessionData.previewData || canPreview;
  const canDownload = sessionData.lookupResult;

  if (!sessionData.fileId) {
    return null;
  }

  return (
    <Card
      size="small"
      title={
        <div className="flex items-center space-x-2">
          <RocketOutlined className={`transition-colors duration-300 ${
            isDark ? 'text-vista-400' : 'text-vista-600'
          }`} />
          <span className={`transition-colors duration-300 ${
            isDark ? 'text-vista-300' : 'text-black-600'
          }`}>Quick Actions</span>
        </div>
      }
      className="mb-4 custom-card"
    >
      <div className="space-y-3">
        <Text type="secondary" className="text-xs block">
          Streamlit-style one-click automation
        </Text>
        
        <Space direction="vertical" className="w-full">
          {/* Quick Preview */}
          <Tooltip 
            title={
              canPreview 
                ? "Auto-select first 2 sheets and preview instantly" 
                : "Upload a file with at least 2 sheets first"
            }
          >
            <Button
              type="primary"
              icon={<EyeOutlined />}
              onClick={handleQuickPreview}
              disabled={!canPreview || isLoading}
              block
              size="small"
            >
              Quick Preview
            </Button>
          </Tooltip>

          {/* Quick Process */}
          <Tooltip
            title={
              canProcess
                ? "Run complete ETL pipeline automatically"
                : "Preview sheets first"
            }
          >
            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              onClick={handleQuickProcess}
              disabled={!canProcess || isLoading}
              block
              size="small"
              className={`custom-button transition-all duration-300 ${
                isDark
                  ? 'bg-azure-500 hover:bg-azure-400 border-azure-500'
                  : 'bg-azure-600 hover:bg-azure-500 border-azure-600'
              }`}
            >
              Auto Process
            </Button>
          </Tooltip>

          {/* Quick Download */}
          <Tooltip
            title={
              canDownload
                ? "Download processed results instantly"
                : "Complete processing first"
            }
          >
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleQuickDownload}
              disabled={!canDownload || isLoading}
              block
              size="small"
              className={`custom-button transition-all duration-300 ${
                isDark
                  ? 'bg-rojo-600 hover:bg-rojo-500 border-rojo-600'
                  : 'bg-rojo-500 hover:bg-rojo-400 border-rojo-500'
              }`}
            >
              Quick Download
            </Button>
          </Tooltip>
        </Space>

        {/* Status Indicators */}
        <div className="mt-4 pt-3 border-t border-gray-200">
          <div className="space-y-1">
            <div className="flex justify-between items-center text-xs">
              <span>File:</span>
              <span className={sessionData.fileId ? 'text-green-600' : 'text-gray-400'}>
                {sessionData.fileId ? '✓' : '○'}
              </span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span>Preview:</span>
              <span className={sessionData.previewData ? 'text-green-600' : 'text-gray-400'}>
                {sessionData.previewData ? '✓' : '○'}
              </span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span>Processed:</span>
              <span className={sessionData.lookupResult ? 'text-green-600' : 'text-gray-400'}>
                {sessionData.lookupResult ? '✓' : '○'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
