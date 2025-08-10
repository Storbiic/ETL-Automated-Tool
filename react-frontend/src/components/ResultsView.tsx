'use client';

import React from 'react';
import { Card, Button, Typography, Alert, Statistic, Row, Col } from 'antd';
import { BarChartOutlined, DownloadOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useETLStore } from '@/store/etlStore';

const { Title, Text } = Typography;

export const ResultsView: React.FC = () => {
  const { sessionData, nextStep, quickDownload } = useETLStore();

  const handleNext = () => {
    nextStep();
  };

  const handleDownload = () => {
    quickDownload();
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Title level={2} className="text-gray-800 mb-2">
            Processing Results
          </Title>
          <Text type="secondary" className="text-lg">
            Review the results of your ETL processing
          </Text>
        </div>

        {sessionData.lookupResult && (
          <>
            <Card className="mb-6">
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="Records Processed"
                    value={sessionData.lookupResult.total_records || 0}
                    prefix={<BarChartOutlined />}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Successful Matches"
                    value={sessionData.lookupResult.successful_matches || 0}
                    valueStyle={{ color: '#3f8600' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Failed Matches"
                    value={sessionData.lookupResult.failed_matches || 0}
                    valueStyle={{ color: '#cf1322' }}
                  />
                </Col>
              </Row>
            </Card>

            <Card className="mb-6">
              <div className="flex justify-between items-center">
                <div>
                  <Title level={4}>Download Results</Title>
                  <Text type="secondary">
                    Download the processed data file
                  </Text>
                </div>
                <div className="space-x-4">
                  <Button
                    type="primary"
                    icon={<DownloadOutlined />}
                    onClick={handleDownload}
                    size="large"
                  >
                    Download
                  </Button>
                  <Button
                    type="primary"
                    icon={<ArrowRightOutlined />}
                    onClick={handleNext}
                    size="large"
                  >
                    Continue to Updates
                  </Button>
                </div>
              </div>
            </Card>
          </>
        )}

        {!sessionData.lookupResult && (
          <Alert
            message="No results available"
            description="Complete the lookup process to view results"
            type="info"
          />
        )}
      </div>
    </div>
  );
};
