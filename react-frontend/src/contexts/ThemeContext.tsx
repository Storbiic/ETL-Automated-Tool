'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { ConfigProvider, theme } from 'antd';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState<Theme>('light');

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('etl-theme') as Theme;
    if (savedTheme) {
      setCurrentTheme(savedTheme);
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setCurrentTheme(prefersDark ? 'dark' : 'light');
    }
  }, []);

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    if (currentTheme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('etl-theme', currentTheme);
  }, [currentTheme]);

  const toggleTheme = () => {
    setCurrentTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const isDark = currentTheme === 'dark';

  // Ant Design theme configuration
  const antdTheme = {
    algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorPrimary: isDark ? '#7f9ec3' : '#537cae', // vista blue
      colorSuccess: isDark ? '#98bfcb' : '#5d9bad', // azure
      colorWarning: '#e97979', // rojo light
      colorError: '#d82423', // rojo
      colorInfo: '#7f9ec3', // vista blue
      
      // Background colors
      colorBgContainer: isDark ? '#1e343b' : '#ffffff',
      colorBgElevated: isDark ? '#293e57' : '#f6fafb',
      colorBgLayout: isDark ? '#151f2c' : '#f6fafb',
      
      // Text colors
      colorText: isDark ? '#e5ebf3' : '#060505',
      colorTextSecondary: isDark ? '#ccd8e7' : '#736060',
      colorTextTertiary: isDark ? '#b2c4db' : '#a49292',
      
      // Border colors
      colorBorder: isDark ? '#3e5d83' : '#d3e4e9',
      colorBorderSecondary: isDark ? '#293e57' : '#e5eff2',
      
      // Component specific
      borderRadius: 8,
      borderRadiusLG: 12,
      borderRadiusSM: 6,
      
      // Spacing
      padding: 16,
      paddingLG: 24,
      paddingSM: 12,
      paddingXS: 8,
      
      // Font
      fontSize: 14,
      fontSizeLG: 16,
      fontSizeSM: 12,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    },
    components: {
      Layout: {
        headerBg: isDark ? '#151f2c' : '#ffffff',
        siderBg: isDark ? '#1e343b' : '#ffffff',
        bodyBg: isDark ? '#151f2c' : '#f6fafb',
      },
      Card: {
        colorBgContainer: isDark ? '#1e343b' : '#ffffff',
        colorBorderSecondary: isDark ? '#3e5d83' : '#e5eff2',
      },
      Button: {
        colorPrimary: isDark ? '#7f9ec3' : '#537cae',
        colorPrimaryHover: isDark ? '#98b1cf' : '#7f9ec3',
        colorPrimaryActive: isDark ? '#537cae' : '#3e5d83',
      },
      Table: {
        colorBgContainer: isDark ? '#1e343b' : '#ffffff',
        colorFillAlter: isDark ? '#293e57' : '#f6fafb',
      },
      Steps: {
        colorPrimary: isDark ? '#7f9ec3' : '#537cae',
      },
      Alert: {
        colorSuccessBg: isDark ? '#1e343b' : '#f6fafb',
        colorInfoBg: isDark ? '#1e343b' : '#f6fafb',
        colorWarningBg: isDark ? '#2b0707' : '#f8d2d2',
        colorErrorBg: isDark ? '#2b0707' : '#f8d2d2',
      },
    },
  };

  return (
    <ThemeContext.Provider value={{ theme: currentTheme, toggleTheme, isDark }}>
      <ConfigProvider theme={antdTheme}>
        {children}
      </ConfigProvider>
    </ThemeContext.Provider>
  );
};
