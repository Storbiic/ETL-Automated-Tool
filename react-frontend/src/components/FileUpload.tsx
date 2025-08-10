'use client';

import React, { useCallback } from 'react';
import { Card, Typography, Button, Alert, Progress } from 'antd';
import { UploadOutlined, InboxOutlined, FileExcelOutlined } from '@ant-design/icons';
import { useDropzone } from 'react-dropzone';
import { useETLStore } from '@/store/etlStore';
import { useTheme } from '@/contexts/ThemeContext';

const { Title, Text } = Typography;

export const FileUpload: React.FC = () => {
  const { uploadFile, isLoading, sessionData, addLog } = useETLStore();
  const { isDark } = useTheme();

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        await uploadFile(file);
      }
    },
    [uploadFile]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024, // 100MB
    disabled: isLoading,
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 slide-up">
          <Title level={2} className={`mb-2 transition-colors duration-300 ${
            isDark ? 'text-vista-300' : 'text-black-600'
          }`}>
            Upload Your Data File
          </Title>
          <Text type="secondary" className="text-lg">
            Upload your CSV or Excel file to begin the automated ETL process
          </Text>
        </div>

        {/* Upload Area */}
        <Card className="mb-6 custom-card">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all duration-300
              ${isDragActive && !isDragReject
                ? (isDark ? 'border-vista-400 bg-vista-100/20' : 'border-vista-600 bg-vista-900/10')
                : ''
              }
              ${isDragReject
                ? (isDark ? 'border-rojo-600 bg-rojo-100/20' : 'border-rojo-500 bg-rojo-900/10')
                : ''
              }
              ${!isDragActive
                ? (isDark
                    ? 'border-azure-300 hover:border-vista-400 hover:bg-vista-100/10'
                    : 'border-azure-400 hover:border-vista-600 hover:bg-azure-900/5'
                  )
                : ''
              }
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} />
            
            <div className="flex flex-col items-center space-y-4">
              {isDragActive ? (
                <>
                  <InboxOutlined className={`text-6xl transition-colors duration-300 ${
                    isDark ? 'text-vista-400' : 'text-vista-600'
                  }`} />
                  <Title level={4} className={`m-0 transition-colors duration-300 ${
                    isDark ? 'text-vista-300' : 'text-vista-700'
                  }`}>
                    Drop your file here
                  </Title>
                </>
              ) : (
                <>
                  <FileExcelOutlined className={`text-6xl transition-colors duration-300 ${
                    isDark ? 'text-azure-400' : 'text-azure-500'
                  }`} />
                  <Title level={4} className={`m-0 transition-colors duration-300 ${
                    isDark ? 'text-vista-300' : 'text-black-600'
                  }`}>
                    Drag & Drop your file here
                  </Title>
                  <Text type="secondary" className="text-base">
                    or click to browse
                  </Text>
                  <Button
                    type="primary"
                    icon={<UploadOutlined />}
                    size="large"
                    disabled={isLoading}
                    className="custom-button"
                  >
                    Choose File
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* File Info */}
          <div className="mt-4 text-center">
            <Text type="secondary" className="text-sm">
              <InboxOutlined className="mr-1" />
              Supported formats: CSV, Excel (.xls, .xlsx) • Max size: 100MB
            </Text>
          </div>
        </Card>

        {/* Upload Progress */}
        {isLoading && (
          <Card className="mb-6">
            <div className="text-center">
              <Title level={4} className="text-gray-700 mb-4">
                Uploading File...
              </Title>
              <Progress 
                percent={100} 
                status="active" 
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
              <Text type="secondary" className="mt-2 block">
                Processing your file and analyzing sheets...
              </Text>
            </div>
          </Card>
        )}

        {/* Success State */}
        {sessionData.fileId && !isLoading && (
          <Alert
            message="File Uploaded Successfully!"
            description={
              <div>
                <div className="mb-2">
                  <strong>File:</strong> {sessionData.filename}
                </div>
                <div className="mb-2">
                  <strong>Sheets found:</strong> {sessionData.sheetNames.length}
                </div>
                <div>
                  <strong>Sheets:</strong> {sessionData.sheetNames.join(', ')}
                </div>
              </div>
            }
            type="success"
            showIcon
            className="mb-6"
          />
        )}

        {/* Instructions */}
        <Card title="Instructions" className="bg-gray-50">
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                1
              </div>
              <div>
                <Text strong>Upload your data file</Text>
                <div className="text-gray-600 text-sm">
                  Choose a CSV or Excel file containing your data sheets
                </div>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                2
              </div>
              <div>
                <Text strong>File requirements</Text>
                <div className="text-gray-600 text-sm">
                  • Must contain at least 2 sheets (Master BOM and Target sheet)
                  <br />
                  • Supported formats: .csv, .xls, .xlsx
                  <br />
                  • Maximum file size: 100MB
                </div>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                3
              </div>
              <div>
                <Text strong>What happens next</Text>
                <div className="text-gray-600 text-sm">
                  After upload, you'll be able to preview sheets, clean data, and perform automated lookups
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
