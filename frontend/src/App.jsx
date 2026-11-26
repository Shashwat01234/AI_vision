import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SettingsProvider } from './context/SettingsContext';

// Pages
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import ImageAnalysis from './pages/ImageAnalysis';
import DocumentAnalysis from './pages/DocumentAnalysis';
import History from './pages/History';
import Settings from './pages/Settings';
import About from './pages/About';

export const App = () => {
  return (
    <SettingsProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/image-analysis" element={<ImageAnalysis />} />
          <Route path="/document-analysis" element={<DocumentAnalysis />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/about" element={<About />} />
          {/* Fallback to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </SettingsProvider>
  );
};
export default App;
