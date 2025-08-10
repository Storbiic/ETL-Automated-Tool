'use client';

import React from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Typography, Space, Alert } from 'antd';
import {
  DatabaseOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  DashboardOutlined
} from '@ant-design/icons';
import { useTheme } from '@/contexts/ThemeContext';

const { Title, Text } = Typography;

interface ColumnInsightsProps {
  insights: any;
}

export const ColumnInsights: React.FC<ColumnInsightsProps> = ({ insights }) => {
  const { isDark } = useTheme();

  if (!insights) {
    return (
      <Alert
        message="No Column Insights Available"
        description="Please clean your data first to generate column insights."
        type="info"
        showIcon
      />
    );
  }

  const { master_sheet_analysis, target_sheet_analysis, data_quality } = insights;

  const masterColumns = [
    {
      title: 'Column Name',
      dataIndex: 'column',
      key: 'column',
    },
    {
      title: 'Data Type',
      dataIndex: 'type',
      key: 'type',
    },
    {
      title: 'Completeness',
      dataIndex: 'completeness',
      key: 'completeness',
      render: (value: number) => (
        <Progress 
          percent={value} 
          size="small" 
          status={value > 90 ? 'success' : value > 70 ? 'normal' : 'exception'}
        />
      ),
    },
  ];

  const masterColumnData = Object.keys(master_sheet_analysis.column_types || {}).map(col => ({
    key: col,
    column: col,
    type: master_sheet_analysis.column_types[col],
    completeness: data_quality.master_completeness[col] || 0,
  }));

  const targetColumnData = Object.keys(target_sheet_analysis.column_types || {}).map(col => ({
    key: col,
    column: col,
    type: target_sheet_analysis.column_types[col],
    completeness: data_quality.target_completeness[col] || 0,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <DashboardOutlined className={`text-2xl ${isDark ? 'text-vista-400' : 'text-vista-600'}`} />
        <Title level={3} className="m-0">Column Insights</Title>
      </div>

      {/* Overview Statistics */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Master Sheet Columns"
              value={master_sheet_analysis.total_columns}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: isDark ? '#60a5fa' : '#2563eb' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Master Sheet Rows"
              value={master_sheet_analysis.total_rows}
              prefix={<InfoCircleOutlined />}
              valueStyle={{ color: isDark ? '#34d399' : '#059669' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Target Sheet Columns"
              value={target_sheet_analysis.total_columns}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: isDark ? '#fbbf24' : '#d97706' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Target Sheet Rows"
              value={target_sheet_analysis.total_rows}
              prefix={<InfoCircleOutlined />}
              valueStyle={{ color: isDark ? '#f87171' : '#dc2626' }}
            />
          </Card>
        </Col>
      </Row>

      {/* YAZAKI PN Analysis */}
      {master_sheet_analysis.yazaki_pn_column && (
        <Card title="YAZAKI PN Analysis" className="mb-6">
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={8}>
              <Statistic
                title="Unique YAZAKI PNs"
                value={master_sheet_analysis.yazaki_pn_unique_count}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col xs={24} sm={8}>
              <Statistic
                title="Missing YAZAKI PNs"
                value={master_sheet_analysis.yazaki_pn_null_count}
                prefix={<ExclamationCircleOutlined />}
                valueStyle={{ color: master_sheet_analysis.yazaki_pn_null_count > 0 ? '#ff4d4f' : '#52c41a' }}
              />
            </Col>
            <Col xs={24} sm={8}>
              <div>
                <Text strong>Data Quality</Text>
                <Progress
                  percent={Math.round(((master_sheet_analysis.total_rows - master_sheet_analysis.yazaki_pn_null_count) / master_sheet_analysis.total_rows) * 100)}
                  status={master_sheet_analysis.yazaki_pn_null_count === 0 ? 'success' : 'normal'}
                />
              </div>
            </Col>
          </Row>
        </Card>
      )}

      {/* Column Details */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Master Sheet Columns" className="h-full">
            <Table
              columns={masterColumns}
              dataSource={masterColumnData}
              pagination={{ pageSize: 10 }}
              size="small"
              scroll={{ y: 300 }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Target Sheet Columns" className="h-full">
            <Table
              columns={masterColumns}
              dataSource={targetColumnData}
              pagination={{ pageSize: 10 }}
              size="small"
              scroll={{ y: 300 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Sample Data Preview */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Master Sheet Sample" className="h-full">
            <div className={`p-3 rounded text-xs overflow-auto ${
              isDark ? 'bg-vista-100 text-vista-300' : 'bg-azure-900 text-black-600'
            }`}>
              <pre>{JSON.stringify(master_sheet_analysis.sample_data, null, 2)}</pre>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Target Sheet Sample" className="h-full">
            <div className={`p-3 rounded text-xs overflow-auto ${
              isDark ? 'bg-vista-100 text-vista-300' : 'bg-azure-900 text-black-600'
            }`}>
              <pre>{JSON.stringify(target_sheet_analysis.sample_data, null, 2)}</pre>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};
