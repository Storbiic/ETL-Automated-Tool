'use client';

import React, { useState } from 'react';
import { Card, Button, Input, Select, Typography, Space, Alert, Collapse } from 'antd';
import { 
  BugOutlined, 
  SendOutlined, 
  CopyOutlined,
  EyeOutlined,
  EyeInvisibleOutlined 
} from '@ant-design/icons';
import { useTheme } from '@/contexts/ThemeContext';

const { TextArea } = Input;
const { Option } = Select;
const { Text, Title } = Typography;
const { Panel } = Collapse;

interface APIDebuggerProps {
  isVisible: boolean;
  onClose: () => void;
}

export const APIDebugger: React.FC<APIDebuggerProps> = ({ isVisible, onClose }) => {
  const { isDark } = useTheme();
  const [endpoint, setEndpoint] = useState('/');
  const [method, setMethod] = useState('GET');
  const [requestBody, setRequestBody] = useState('{}');
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const commonEndpoints = [
    { value: '/', label: 'Health Check (GET)' },
    { value: '/upload', label: 'Upload File (POST)' },
    { value: '/preview', label: 'Preview Sheets (POST)' },
    { value: '/clean', label: 'Clean Data (POST)' },
    { value: '/get-lookup-columns', label: 'Get Lookup Columns (POST)' },
    { value: '/lookup', label: 'Perform Lookup (POST)' },
    { value: '/process-updates', label: 'Process Updates (POST)' },
  ];

  const handleSendRequest = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const options: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (method !== 'GET' && requestBody.trim()) {
        try {
          JSON.parse(requestBody); // Validate JSON
          options.body = requestBody;
        } catch (e) {
          throw new Error('Invalid JSON in request body');
        }
      }

      const res = await fetch(`http://localhost:8000${endpoint}`, options);
      const data = await res.json();
      
      setResponse({
        status: res.status,
        statusText: res.statusText,
        headers: Object.fromEntries(res.headers.entries()),
        data,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card
        title={
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <BugOutlined className={isDark ? 'text-vista-400' : 'text-vista-600'} />
              <Title level={4} className="m-0">API Debugger</Title>
            </div>
            <Button onClick={onClose} type="text">×</Button>
          </div>
        }
        className={`w-full max-w-4xl max-h-[90vh] overflow-auto ${
          isDark ? 'bg-vista-200' : 'bg-white'
        }`}
      >
        <Space direction="vertical" className="w-full" size="large">
          {/* Request Configuration */}
          <div>
            <Title level={5}>Request Configuration</Title>
            <Space direction="vertical" className="w-full">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Text strong>Method</Text>
                  <Select
                    value={method}
                    onChange={setMethod}
                    className="w-full"
                  >
                    <Option value="GET">GET</Option>
                    <Option value="POST">POST</Option>
                    <Option value="PUT">PUT</Option>
                    <Option value="DELETE">DELETE</Option>
                  </Select>
                </div>
                
                <div className="md:col-span-2">
                  <Text strong>Endpoint</Text>
                  <Select
                    value={endpoint}
                    onChange={setEndpoint}
                    className="w-full"
                    showSearch
                    allowClear
                  >
                    {commonEndpoints.map(ep => (
                      <Option key={ep.value} value={ep.value}>
                        {ep.label}
                      </Option>
                    ))}
                  </Select>
                </div>
              </div>

              {method !== 'GET' && (
                <div>
                  <Text strong>Request Body (JSON)</Text>
                  <TextArea
                    value={requestBody}
                    onChange={(e) => setRequestBody(e.target.value)}
                    placeholder='{"key": "value"}'
                    rows={4}
                    className="font-mono"
                  />
                </div>
              )}

              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSendRequest}
                loading={loading}
                className="custom-button"
              >
                Send Request
              </Button>
            </Space>
          </div>

          {/* Error Display */}
          {error && (
            <Alert
              message="Request Error"
              description={error}
              type="error"
              showIcon
            />
          )}

          {/* Response Display */}
          {response && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <Title level={5}>Response</Title>
                <Button
                  icon={<CopyOutlined />}
                  onClick={() => copyToClipboard(JSON.stringify(response, null, 2))}
                  size="small"
                >
                  Copy
                </Button>
              </div>

              <Collapse>
                <Panel
                  header={
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded text-xs font-mono ${
                        response.status >= 200 && response.status < 300
                          ? 'bg-azure-500 text-white'
                          : 'bg-rojo-500 text-white'
                      }`}>
                        {response.status}
                      </span>
                      <span>{response.statusText}</span>
                    </div>
                  }
                  key="response"
                >
                  <div className="space-y-4">
                    <div>
                      <Text strong>Headers</Text>
                      <pre className={`mt-2 p-3 rounded text-xs overflow-auto ${
                        isDark ? 'bg-vista-100 text-vista-300' : 'bg-azure-900 text-black-600'
                      }`}>
                        {JSON.stringify(response.headers, null, 2)}
                      </pre>
                    </div>

                    <div>
                      <Text strong>Response Data</Text>
                      <pre className={`mt-2 p-3 rounded text-xs overflow-auto ${
                        isDark ? 'bg-vista-100 text-vista-300' : 'bg-azure-900 text-black-600'
                      }`}>
                        {JSON.stringify(response.data, null, 2)}
                      </pre>
                    </div>
                  </div>
                </Panel>
              </Collapse>
            </div>
          )}

          {/* Quick Test Buttons */}
          <div>
            <Title level={5}>Quick Tests</Title>
            <Space wrap>
              <Button
                size="small"
                onClick={() => {
                  setEndpoint('/');
                  setMethod('GET');
                  setRequestBody('{}');
                }}
              >
                Health Check
              </Button>
              <Button
                size="small"
                onClick={() => {
                  setEndpoint('/preview');
                  setMethod('POST');
                  setRequestBody('{"master_sheet": "Sheet1", "target_sheet": "Sheet2"}');
                }}
              >
                Test Preview
              </Button>
              <Button
                size="small"
                onClick={() => {
                  setEndpoint('/clean');
                  setMethod('POST');
                  setRequestBody('{}');
                }}
              >
                Test Clean
              </Button>
            </Space>
          </div>
        </Space>
      </Card>
    </div>
  );
};
