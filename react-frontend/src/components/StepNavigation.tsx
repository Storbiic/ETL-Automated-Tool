'use client';

import React from 'react';
import { Button, Space, Tooltip } from 'antd';
import {
  LeftOutlined,
  RightOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useETLStore } from '@/store/etlStore';
import { useTheme } from '@/contexts/ThemeContext';

const stepNames = [
  'Upload',
  'Preview', 
  'Clean',
  'Lookup',
  'Results',
  'Updates'
];

export const StepNavigation: React.FC = () => {
  const { 
    currentStep, 
    previousStep, 
    nextStep, 
    goToStep, 
    resetSession,
    getMaxAllowedStep,
    isLoading 
  } = useETLStore();
  const { isDark } = useTheme();

  const maxStep = getMaxAllowedStep();
  const canGoBack = currentStep > 0;
  const canGoForward = currentStep < maxStep;

  return (
    <div className={`flex items-center justify-between p-4 border-t transition-all duration-300 ${
      isDark ? 'border-vista-300 bg-vista-200/50' : 'border-azure-300 bg-azure-900/30'
    }`}>
      {/* Left side - Back button */}
      <div>
        <Tooltip title={canGoBack ? `Go back to ${stepNames[currentStep - 1]}` : 'Already at first step'}>
          <Button
            icon={<LeftOutlined />}
            onClick={previousStep}
            disabled={!canGoBack || isLoading}
            className={`custom-button transition-all duration-300 ${
              isDark 
                ? 'hover:bg-vista-300/20 border-vista-400' 
                : 'hover:bg-azure-800/20 border-azure-400'
            }`}
          >
            Back
          </Button>
        </Tooltip>
      </div>

      {/* Center - Current step info */}
      <div className="flex items-center space-x-4">
        <div className={`text-center transition-colors duration-300 ${
          isDark ? 'text-vista-300' : 'text-black-600'
        }`}>
          <div className="text-sm font-medium">
            Step {currentStep + 1} of {stepNames.length}
          </div>
          <div className="text-xs opacity-75">
            {stepNames[currentStep]}
          </div>
        </div>

        {/* Step indicators */}
        <div className="flex space-x-1">
          {stepNames.map((_, index) => (
            <Tooltip key={index} title={`${stepNames[index]} ${index <= maxStep ? '(Available)' : '(Locked)'}`}>
              <button
                onClick={() => index <= maxStep ? goToStep(index) : null}
                disabled={index > maxStep || isLoading}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  index === currentStep
                    ? (isDark ? 'bg-vista-400 scale-125' : 'bg-vista-600 scale-125')
                    : index <= maxStep
                    ? (isDark ? 'bg-vista-600 hover:bg-vista-500' : 'bg-vista-800 hover:bg-vista-700')
                    : (isDark ? 'bg-vista-800' : 'bg-azure-400')
                } ${index <= maxStep ? 'cursor-pointer' : 'cursor-not-allowed'}`}
              />
            </Tooltip>
          ))}
        </div>
      </div>

      {/* Right side - Forward/Reset buttons */}
      <div>
        <Space>
          {/* Reset button */}
          <Tooltip title="Reset and start over">
            <Button
              icon={<ReloadOutlined />}
              onClick={resetSession}
              disabled={isLoading}
              size="small"
              className={`custom-button transition-all duration-300 ${
                isDark 
                  ? 'hover:bg-rojo-600/20 border-rojo-600 text-rojo-400' 
                  : 'hover:bg-rojo-500/20 border-rojo-500 text-rojo-600'
              }`}
            >
              Reset
            </Button>
          </Tooltip>

          {/* Forward button */}
          <Tooltip title={canGoForward ? `Continue to ${stepNames[currentStep + 1]}` : 'Complete current step first'}>
            <Button
              icon={<RightOutlined />}
              onClick={nextStep}
              disabled={!canGoForward || isLoading}
              type="primary"
              className="custom-button"
            >
              Next
            </Button>
          </Tooltip>
        </Space>
      </div>
    </div>
  );
};
