'use client';

import React from 'react';
import { Card, Row, Col, Statistic, Progress, Typography, Space, Alert, Tag, List } from 'antd';
import {
  LineChartOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  QuestionCircleOutlined,
  TrophyOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { useTheme } from '@/contexts/ThemeContext';

const { Title, Text } = Typography;

interface LookupInsightsProps {
  insights: any;
}

export const LookupInsights: React.FC<LookupInsightsProps> = ({ insights }) => {
  const { isDark } = useTheme();

  if (!insights) {
    return (
      <Alert
        message="No Lookup Insights Available"
        description="Please perform a lookup operation first to generate insights."
        type="info"
        showIcon
      />
    );
  }

  const { lookup_summary, data_quality_insights, recommendations } = insights;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'D': return '#52c41a'; // Green for active/discontinued
      case 'X': return '#faad14'; // Orange for inactive/no update
      case '0': return '#1890ff'; // Blue for status '0'/check
      case 'NOT_FOUND': return '#ff4d4f'; // Red for not found
      default: return '#d9d9d9';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'D': return <CheckCircleOutlined />;
      case 'X': return <CloseCircleOutlined />;
      case '0': return <QuestionCircleOutlined />;
      case 'NOT_FOUND': return <QuestionCircleOutlined />;
      default: return <QuestionCircleOutlined />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'D': return "Status 'D' (Active)";
      case 'X': return "Status 'X' (Inactive)";
      case '0': return "Status '0' (Check)";
      case 'NOT_FOUND': return 'Not Found';
      default: return status;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <LineChartOutlined className={`text-2xl ${isDark ? 'text-vista-400' : 'text-vista-600'}`} />
        <Title level={3} className="m-0">Lookup Insights</Title>
      </div>

      {/* Overview Statistics */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Records"
              value={lookup_summary.total_records}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: isDark ? '#60a5fa' : '#2563eb' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Match Rate"
              value={data_quality_insights.match_rate}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ 
                color: data_quality_insights.match_rate > 90 ? '#52c41a' : 
                       data_quality_insights.match_rate > 70 ? '#faad14' : '#ff4d4f' 
              }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Successful Matches"
              value={lookup_summary.successful_matches}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Failed Matches"
              value={lookup_summary.failed_matches}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Activation Status Distribution */}
      <Card title="Activation Status Distribution">
        <Row gutter={[16, 16]}>
          {Object.entries(lookup_summary.activation_status_distribution).map(([status, count]) => (
            <Col xs={24} sm={12} md={8} key={status}>
              <Card size="small" className="text-center">
                <Space direction="vertical" size="small">
                  <div style={{ color: getStatusColor(status), fontSize: '24px' }}>
                    {getStatusIcon(status)}
                  </div>
                  <Text strong>{getStatusLabel(status)}</Text>
                  <Statistic
                    value={count as number}
                    suffix={`(${lookup_summary.activation_percentages[status]}%)`}
                    valueStyle={{ 
                      color: getStatusColor(status),
                      fontSize: '16px'
                    }}
                  />
                  <Progress
                    percent={lookup_summary.activation_percentages[status]}
                    strokeColor={getStatusColor(status)}
                    size="small"
                    showInfo={false}
                  />
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* Data Quality Insights */}
      <Card title="Data Quality Analysis">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Statistic
                title="Status 'D' Parts"
                value={data_quality_insights.status_d_parts || 0}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Statistic
                title="Status 'X' Parts"
                value={data_quality_insights.status_x_parts || 0}
                prefix={<CloseCircleOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Statistic
                title="Status '0' Parts"
                value={data_quality_insights.status_0_parts || 0}
                prefix={<QuestionCircleOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <Statistic
                title="Not Found Parts"
                value={data_quality_insights.not_found_parts || 0}
                prefix={<QuestionCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
        </Row>
      </Card>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <Card 
          title={
            <Space>
              <WarningOutlined style={{ color: '#faad14' }} />
              <span>Recommendations</span>
            </Space>
          }
        >
          <List
            dataSource={recommendations}
            renderItem={(item: string, index: number) => (
              <List.Item>
                <Alert
                  message={item}
                  type="warning"
                  showIcon
                  className="w-full"
                />
              </List.Item>
            )}
          />
        </Card>
      )}

      {/* Summary Tags */}
      <Card title="Summary">
        <Space wrap>
          <Tag color={data_quality_insights.match_rate > 90 ? 'green' : data_quality_insights.match_rate > 70 ? 'orange' : 'red'}>
            Match Rate: {data_quality_insights.match_rate}%
          </Tag>
          <Tag color="blue">
            Total Records: {lookup_summary.total_records}
          </Tag>
          <Tag color="green">
            Status 'D': {data_quality_insights.status_d_parts || 0}
          </Tag>
          <Tag color="orange">
            Status 'X': {data_quality_insights.status_x_parts || 0}
          </Tag>
          <Tag color="cyan">
            Status '0': {data_quality_insights.status_0_parts || 0}
          </Tag>
          <Tag color="red">
            Not Found: {data_quality_insights.not_found_parts || 0}
          </Tag>
        </Space>
      </Card>
    </div>
  );
};
