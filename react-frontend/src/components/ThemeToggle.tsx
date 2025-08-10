'use client';

import React from 'react';
import { Button, Tooltip } from 'antd';
import { SunOutlined, MoonOutlined } from '@ant-design/icons';
import { useTheme } from '@/contexts/ThemeContext';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <Tooltip title={`Switch to ${isDark ? 'light' : 'dark'} mode`}>
      <Button
        type="text"
        icon={isDark ? <SunOutlined /> : <MoonOutlined />}
        onClick={toggleTheme}
        className={`
          transition-all duration-300 ease-in-out
          ${isDark 
            ? 'text-vista-300 hover:text-vista-100 hover:bg-vista-100/10' 
            : 'text-vista-600 hover:text-vista-800 hover:bg-vista-100/20'
          }
        `}
        size="large"
      />
    </Tooltip>
  );
};
