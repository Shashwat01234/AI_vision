import React, { createContext, useContext, useState, useEffect } from 'react';

const SettingsContext = createContext();

export const DEFAULT_SETTINGS = {
  voice: 'en_US-lessac-medium',
  speechSpeed: 1.0,
  textSize: 'md', // sm, md, lg, xl, 2xl
  highContrast: false,
  reducedMotion: false,
  screenReaderOptimized: true,
  dataRetentionDays: 30,
};

export const SettingsProvider = ({ children }) => {
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem('ai_assistant_settings');
      return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS;
    } catch {
      return DEFAULT_SETTINGS;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('ai_assistant_settings', JSON.stringify(settings));
    } catch (e) {
      console.error('Failed to save settings to localStorage:', e);
    }

    // Apply document-level classes for accessibility
    const root = document.documentElement;
    if (settings.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    if (settings.reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }

    // Text size
    const sizeMap = {
      sm: '14px',
      md: '16px',
      lg: '18px',
      xl: '20px',
      '2xl': '22px'
    };
    root.style.setProperty('--font-size-base', sizeMap[settings.textSize] || '16px');
  }, [settings]);

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const updateSettings = (newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS);
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSetting, updateSettings, resetSettings }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

