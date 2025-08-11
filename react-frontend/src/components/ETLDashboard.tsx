'use client';

import React, { useState, useEffect } from 'react';
import { Layout, Card, Steps, Button, Alert, Spin, Typography, Space } from 'antd';
import {
  UploadOutlined,
  EyeOutlined,
  ClearOutlined,
  SearchOutlined,
  BarChartOutlined,
  SyncOutlined,
  RocketOutlined,
  DownloadOutlined,
  ThunderboltOutlined,
  BugOutlined,
  DashboardOutlined,
  CloudUploadOutlined,
  LineChartOutlined
} from '@ant-design/icons';
import { FileUpload } from './FileUpload';
import { SheetPreview } from './SheetPreview';
import { DataCleaning } from './DataCleaning';
import { LookupConfig } from './LookupConfig';
import { ResultsView } from './ResultsView';
import { MasterUpdates } from './MasterUpdates';
import { QuickActions } from './QuickActions';
import { useETLStore } from '@/store/etlStore';
import { useAPIHealth } from '@/hooks/useAPIHealth';
import { useTheme } from '@/contexts/ThemeContext';
import { ThemeToggle } from './ThemeToggle';
import { StepNavigation } from './StepNavigation';
import { APIDebugger } from './APIDebugger';
import { ColumnInsights } from './ColumnInsights';
import { LookupInsights } from './LookupInsights';
import { Dashboard } from './Dashboard';
import { BOMAnalysis } from './BOMAnalysis';

const { Header, Content, Sider } = Layout;
const { Title, Text } = Typography;

const steps = [
  {
    title: 'Upload',
    description: 'Upload your data file',
    icon: <UploadOutlined />,
  },
  {
    title: 'Preview',
    description: 'Select and preview sheets',
    icon: <EyeOutlined />,
  },
  {
    title: 'Clean',
    description: 'Clean and prepare data',
    icon: <ClearOutlined />,
  },
  {
    title: 'Column Insights',
    description: 'Analyze cleaned data',
    icon: <DashboardOutlined />,
  },
  {
    title: 'Lookup',
    description: 'Configure lookup settings',
    icon: <SearchOutlined />,
  },
  {
    title: 'Lookup Insights',
    description: 'Analyze lookup results',
    icon: <LineChartOutlined />,
  },
  {
    title: 'Results',
    description: 'View processing results',
    icon: <BarChartOutlined />,
  },
  {
    title: 'SharePoint',
    description: 'SharePoint integration',
    icon: <CloudUploadOutlined />,
  },
];

export const ETLDashboard: React.FC = () => {
  const { currentStep, isLoading, error, sessionData, getMaxAllowedStep } = useETLStore();
  const { isHealthy, isChecking, checkHealth, retryCount } = useAPIHealth();
  const { isDark } = useTheme();
  const [showDebugger, setShowDebugger] = React.useState(false);
  const [activeSection, setActiveSection] = React.useState<'process' | 'dashboard' | 'bom'>('process');

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return <FileUpload />;
      case 1:
        return <SheetPreview />;
      case 2:
        return <DataCleaning />;
      case 3:
        return <ColumnInsights insights={sessionData.columnInsights?.insights} />;
      case 4:
        return <LookupConfig />;
      case 5:
        return <LookupInsights insights={sessionData.lookupInsights?.insights} />;
      case 6:
        return <ResultsView />;
      case 7:
        return <MasterUpdates />;
      default:
        return <FileUpload />;
    }
  };

  const renderMainContent = () => {
    switch (activeSection) {
      case 'process':
        return renderStepContent();
      case 'dashboard':
        return <Dashboard />;
      case 'bom':
        return <BOMAnalysis />;
      default:
        return renderStepContent();
    }
  };

  return (
    <Layout className={`min-h-screen transition-all duration-300 ${
      isDark
        ? 'bg-gradient-to-br from-vista-100 to-azure-100'
        : 'bg-gradient-to-br from-azure-900 to-vista-900'
    }`}>
      {/* Header */}
      <Header className={`shadow-lg border-b transition-all duration-300 ${
        isDark
          ? 'bg-vista-100 border-vista-200'
          : 'bg-white border-azure-300'
      }`}>
        <div className="flex items-center justify-between h-full">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <RocketOutlined className={`text-2xl transition-colors duration-300 ${
                isDark ? 'text-vista-400' : 'text-vista-600'
              }`} />
              <Title level={3} className={`m-0 transition-colors duration-300 ${
                isDark ? 'text-vista-300' : 'text-black-500'
              }`}>
                ETL Automation Tool
              </Title>
            </div>
            <div className="hidden md:block">
              <Text type="secondary" className="text-sm">
                v2.0 - React + Next.js Edition
              </Text>
            </div>

            {/* Navigation Menu */}
            <div className="flex items-center space-x-2 ml-8">
              <Button
                type={activeSection === 'process' ? 'primary' : 'default'}
                onClick={() => setActiveSection('process')}
                size="small"
                className={`${
                  activeSection === 'process'
                    ? ''
                    : isDark ? 'bg-vista-50 border-vista-200 text-vista-700' : 'bg-azure-50 border-azure-200 text-azure-700'
                }`}
              >
                📁 Process File
              </Button>
              <Button
                type={activeSection === 'dashboard' ? 'primary' : 'default'}
                onClick={() => setActiveSection('dashboard')}
                size="small"
                className={`${
                  activeSection === 'dashboard'
                    ? ''
                    : isDark ? 'bg-vista-50 border-vista-200 text-vista-700' : 'bg-azure-50 border-azure-200 text-azure-700'
                }`}
              >
                📊 Dashboard
              </Button>
              <Button
                type={activeSection === 'bom' ? 'primary' : 'default'}
                onClick={() => setActiveSection('bom')}
                size="small"
                className={`${
                  activeSection === 'bom'
                    ? ''
                    : isDark ? 'bg-vista-50 border-vista-200 text-vista-700' : 'bg-azure-50 border-azure-200 text-azure-700'
                }`}
              >
                🔧 BOM Analysis
              </Button>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Debug Toggle */}
            {process.env.NODE_ENV === 'development' && (
              <Button
                type="text"
                icon={<BugOutlined />}
                onClick={() => setShowDebugger(true)}
                className={`transition-all duration-300 ${
                  isDark
                    ? 'text-rojo-400 hover:text-rojo-300 hover:bg-rojo-100/10'
                    : 'text-rojo-600 hover:text-rojo-800 hover:bg-rojo-100/20'
                }`}
                size="large"
              />
            )}

            {/* Theme Toggle */}
            <ThemeToggle />
            {/* API Health Status */}
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  isChecking
                    ? (isDark ? 'bg-vista-400 animate-pulse' : 'bg-vista-600 animate-pulse')
                    : isHealthy
                    ? (isDark ? 'bg-azure-400' : 'bg-azure-600')
                    : (isDark ? 'bg-rojo-600' : 'bg-rojo-500')
                }`}
              />
              <Text type="secondary" className="text-sm">
                {isChecking
                  ? 'Connecting...'
                  : isHealthy
                  ? 'API Connected'
                  : `API Disconnected ${retryCount > 0 ? `(${retryCount} retries)` : ''}`
                }
              </Text>
              {!isHealthy && !isChecking && (
                <Button
                  type="text"
                  size="small"
                  onClick={checkHealth}
                  className="text-xs"
                >
                  Retry
                </Button>
              )}
            </div>

            {/* Performance Indicator */}
            {sessionData.fileId && (
              <div className="flex items-center space-x-2">
                <ThunderboltOutlined className={`transition-colors duration-300 ${
                  isDark ? 'text-vista-400' : 'text-vista-600'
                }`} />
                <Text type="secondary" className="text-sm">
                  Cache: {Object.keys(sessionData.cache || {}).length} items
                </Text>
              </div>
            )}
          </div>
        </div>
      </Header>

      <Layout>
        {/* Conditional Sidebar - Only show for Process File section */}
        {activeSection === 'process' && (
          <Sider
            width={320}
            className={`shadow-xl transition-all duration-300 ${
              isDark ? 'bg-vista-100' : 'bg-white'
            }`}
            breakpoint="lg"
            collapsedWidth="0"
          >
          <div className="p-6">
            {/* Progress Steps */}
            <div className="mb-6">
              <Title level={4} className="text-gray-800 mb-4">
                Progress
              </Title>
              <Steps
                direction="vertical"
                current={currentStep}
                size="small"
                items={steps.map((step, index) => {
                  const maxStep = getMaxAllowedStep();
                  return {
                    ...step,
                    status: index < currentStep ? 'finish' :
                            index === currentStep ? 'process' :
                            index <= maxStep ? 'wait' : 'wait',
                    disabled: index > maxStep,
                  };
                })}
              />
            </div>

            {/* Quick Actions */}
            <QuickActions />

            {/* Activity Log */}
            <div className="mt-6">
              <Title level={5} className="text-gray-700 mb-3">
                Activity Log
              </Title>
              <div className="bg-gray-50 rounded-lg p-3 max-h-48 overflow-y-auto">
                {sessionData.logs && sessionData.logs.length > 0 ? (
                  <div className="space-y-2">
                    {sessionData.logs.slice(-5).reverse().map((log, index) => (
                      <div key={index} className="text-xs">
                        <Text type="secondary" className="text-xs">
                          {log.timestamp}
                        </Text>
                        <div className={`text-xs ${
                          log.level === 'error' ? 'text-red-600' :
                          log.level === 'warning' ? 'text-yellow-600' :
                          log.level === 'success' ? 'text-green-600' :
                          'text-gray-600'
                        }`}>
                          {log.message}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <Text type="secondary" className="text-xs">
                    No activity yet
                  </Text>
                )}
              </div>
            </div>

            {/* Reset Button */}
            <div className="mt-6">
              <Button 
                block 
                type="default" 
                icon={<SyncOutlined />}
                onClick={() => window.location.reload()}
              >
                Reset Session
              </Button>
            </div>
          </div>
        </Sider>
        )}

        {/* Main Content */}
        <Layout className="p-6">
          <Content>
            {/* API Health Alert */}
            {!isHealthy && (
              <Alert
                message={isChecking ? "Connecting to Backend..." : "Backend API Unavailable"}
                description={
                  <div>
                    {isChecking ? (
                      <div className="flex items-center space-x-2">
                        <Spin size="small" />
                        <span>Attempting to connect to FastAPI server...</span>
                      </div>
                    ) : (
                      <div>
                        <div className="mb-2">
                          Please ensure the FastAPI server is running on http://localhost:8000
                        </div>
                        <div className="flex items-center space-x-4">
                          <Button
                            size="small"
                            onClick={checkHealth}
                            loading={isChecking}
                            type="primary"
                          >
                            Retry Connection
                          </Button>
                          {retryCount > 0 && (
                            <Text type="secondary" className="text-xs">
                              Retry attempts: {retryCount}
                            </Text>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                }
                type={isChecking ? "info" : "error"}
                showIcon
                className="mb-6"
              />
            )}

            {/* Global Error Alert */}
            {error && (
              <Alert
                message="Error"
                description={error}
                type="error"
                showIcon
                closable
                className="mb-6"
              />
            )}

            {/* Loading Overlay */}
            <Spin spinning={isLoading} tip="Processing...">
              <div className={`rounded-lg shadow-sm border min-h-[600px] transition-all duration-300 ${
                isDark
                  ? 'bg-vista-200 border-vista-300'
                  : 'bg-white border-azure-300'
              }`}>
                <div className="flex flex-col h-full">
                  {/* Main Content */}
                  <div className="flex-1">
                    {renderMainContent()}
                  </div>

                  {/* Step Navigation */}
                  <StepNavigation />
                </div>
              </div>
            </Spin>
          </Content>
        </Layout>
      </Layout>

      {/* API Debugger Modal */}
      <APIDebugger
        isVisible={showDebugger}
        onClose={() => setShowDebugger(false)}
      />
    </Layout>
  );
};
