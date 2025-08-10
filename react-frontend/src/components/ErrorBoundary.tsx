'use client';

import React from 'react';
import { Result, Button } from 'antd';
import { ReloadOutlined, BugOutlined } from '@ant-design/icons';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ETL App Error:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-azure-900 to-vista-900">
          <div className="max-w-md w-full mx-4">
            <Result
              status="error"
              icon={<BugOutlined className="text-rojo-500" />}
              title="Something went wrong"
              subTitle="The ETL application encountered an unexpected error. Please try refreshing the page."
              extra={[
                <Button 
                  key="refresh" 
                  type="primary" 
                  icon={<ReloadOutlined />}
                  onClick={this.handleReset}
                  className="custom-button"
                >
                  Refresh Page
                </Button>
              ]}
            />
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mt-6 p-4 bg-black-100 rounded-lg border border-rojo-500">
                <h4 className="text-rojo-500 font-semibold mb-2">Error Details (Development)</h4>
                <pre className="text-xs text-white-300 overflow-auto max-h-40">
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
