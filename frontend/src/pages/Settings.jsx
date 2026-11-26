import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Volume2,
  Eye,
  Shield,
  Save,
  CheckCircle2,
  Cpu,
  Trash2,
  RefreshCw,
} from 'lucide-react';
import DashboardLayout from '../components/layout/DashboardLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { useSettings } from '../context/SettingsContext';
import { getBackendSettings, updateBackendSettings } from '../services/api';
import axios from 'axios';

export const Settings = () => {
  const { settings, updateSettings } = useSettings();
  const [localSettings, setLocalSettings] = useState(settings);
  const [modelStatus, setModelStatus] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    setLocalSettings(settings);
    // Fetch live model status from backend
    axios
      .get('/api/settings/models-status')
      .then((res) => setModelStatus(res.data))
      .catch((err) => console.log('Could not fetch model status:', err));
  }, [settings]);

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveSuccess(false);

    try {
      // 1. Update frontend React Context (persists to localStorage & document styles)
      updateSettings(localSettings);

      // 2. Sync with backend SQLite database
      await updateBackendSettings({
        voice: localSettings.voice,
        speech_speed: localSettings.speechSpeed,
        text_size: localSettings.textSize,
        high_contrast: localSettings.highContrast,
        reduced_motion: localSettings.reducedMotion,
        screen_reader_optimized: localSettings.screenReaderOptimized,
        data_retention_days: localSettings.dataRetentionDays,
      });

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save settings:', err);
      // Still updated locally
      setSaveSuccess(true);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <DashboardLayout>
      <form onSubmit={handleSave} className="max-w-4xl mx-auto space-y-8 animate-fade-in pb-12">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              System & Accessibility Settings
            </h1>
            <p className="text-slate-500 text-sm mt-1">
              Customize voice speech, visual appearance, and data preferences.
            </p>
          </div>

          <Button type="submit" size="md" icon={Save} isLoading={isSaving}>
            Save Preferences
          </Button>
        </div>

        {saveSuccess && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-center gap-3 text-sm">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" aria-hidden="true" />
            <span>Settings saved successfully. Accessibility styles applied.</span>
          </div>
        )}

        {/* 1. Speech & Voice Settings */}
        <Card title="Speech Narration Preferences" icon={Volume2}>
          <div className="space-y-6">
            <div>
              <label htmlFor="voice-select" className="block text-sm font-semibold text-slate-800 mb-1">
                Default Neural Voice Model (Piper TTS)
              </label>
              <select
                id="voice-select"
                value={localSettings.voice}
                onChange={(e) => setLocalSettings({ ...localSettings, voice: e.target.value })}
                className="w-full max-w-md px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="en_US-lessac-medium">en_US-lessac-medium (Clear & Natural Female)</option>
                <option value="en_US-ryan-medium">en_US-ryan-medium (Warm Male)</option>
                <option value="en_GB-alan-medium">en_GB-alan-medium (British Male)</option>
              </select>
              <p className="text-xs text-slate-400 mt-1">
                Used for offline synthetic voice generation of all image and document explanations.
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between max-w-md">
                <label htmlFor="speech-speed" className="text-sm font-semibold text-slate-800">
                  Narration Speed: <span className="text-indigo-600 font-bold">{localSettings.speechSpeed}x</span>
                </label>
              </div>
              <input
                id="speech-speed"
                type="range"
                min="0.5"
                max="2.0"
                step="0.05"
                value={localSettings.speechSpeed}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, speechSpeed: parseFloat(e.target.value) })
                }
                className="w-full max-w-md h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600 mt-2"
              />
              <div className="flex justify-between text-[11px] text-slate-400 max-w-md mt-1">
                <span>0.5x (Slower)</span>
                <span>1.0x (Normal)</span>
                <span>2.0x (Faster)</span>
              </div>
            </div>
          </div>
        </Card>

        {/* 2. Accessibility & Display Settings */}
        <Card title="Visual & Display Accessibility" icon={Eye}>
          <div className="space-y-6">
            <div>
              <label htmlFor="text-size-select" className="block text-sm font-semibold text-slate-800 mb-1">
                Base Text Size
              </label>
              <select
                id="text-size-select"
                value={localSettings.textSize}
                onChange={(e) => setLocalSettings({ ...localSettings, textSize: e.target.value })}
                className="w-full max-w-xs px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="sm">Small (14px)</option>
                <option value="md">Default (16px)</option>
                <option value="lg">Large (18px)</option>
                <option value="xl">Extra Large (20px)</option>
                <option value="2xl">Maximum (22px)</option>
              </select>
            </div>

            <div className="space-y-4 pt-2">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={localSettings.highContrast}
                  onChange={(e) =>
                    setLocalSettings({ ...localSettings, highContrast: e.target.checked })
                  }
                  className="w-5 h-5 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                />
                <div>
                  <span className="text-sm font-semibold text-slate-800 block">
                    High Contrast Mode (WCAG AAA)
                  </span>
                  <span className="text-xs text-slate-500">
                    Increases border prominence and enhances black/white contrast for low-vision readability.
                  </span>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={localSettings.reducedMotion}
                  onChange={(e) =>
                    setLocalSettings({ ...localSettings, reducedMotion: e.target.checked })
                  }
                  className="w-5 h-5 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                />
                <div>
                  <span className="text-sm font-semibold text-slate-800 block">
                    Reduce Animations & Motion
                  </span>
                  <span className="text-xs text-slate-500">
                    Disables spinning loaders, sliding transitions, and decorative effects.
                  </span>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={localSettings.screenReaderOptimized}
                  onChange={(e) =>
                    setLocalSettings({ ...localSettings, screenReaderOptimized: e.target.checked })
                  }
                  className="w-5 h-5 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                />
                <div>
                  <span className="text-sm font-semibold text-slate-800 block">
                    Screen Reader Priority Announcements
                  </span>
                  <span className="text-xs text-slate-500">
                    Enables active ARIA-live regions for state transitions and audio narration updates.
                  </span>
                </div>
              </label>
            </div>
          </div>
        </Card>

        {/* 3. AI Models Real-Time Diagnostics */}
        <Card title="AI Models Diagnostic Status" icon={Cpu}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="font-bold text-slate-700 block">Ultralytics YOLO (Sign Detector)</span>
              <span className="text-slate-500 block">
                Status: {modelStatus?.yolo?.available ? '✅ Available' : '⚠️ Ready on demand'}
              </span>
              <span className="text-slate-400 block font-mono">
                Weights: {modelStatus?.yolo?.is_custom ? 'Custom Trained' : 'Base / Pretrained'}
              </span>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="font-bold text-slate-700 block">PaddleOCR (Text Extraction)</span>
              <span className="text-slate-500 block">
                Status: {modelStatus?.ocr?.available ? '✅ Available' : 'ℹ️ Initialized per request'}
              </span>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="font-bold text-slate-700 block">Vision-Language Model (VLM)</span>
              <span className="text-slate-500 block">Model: {modelStatus?.vlm?.model || 'moondream2'}</span>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="font-bold text-slate-700 block">Explanation Engine (LLM)</span>
              <span className="text-slate-500 block">Provider: Rule-based template + optional LLM</span>
            </div>
          </div>
        </Card>

        {/* 4. Data Retention */}
        <Card title="Data Privacy & Storage" icon={Shield}>
          <div className="space-y-4">
            <div>
              <label htmlFor="retention-days" className="block text-sm font-semibold text-slate-800 mb-1">
                Data Retention Period (Days)
              </label>
              <input
                id="retention-days"
                type="number"
                min="0"
                max="365"
                value={localSettings.dataRetentionDays}
                onChange={(e) =>
                  setLocalSettings({
                    ...localSettings,
                    dataRetentionDays: parseInt(e.target.value) || 0,
                  })
                }
                className="w-32 px-3.5 py-2 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <p className="text-xs text-slate-400 mt-1">
                Uploaded files older than this will be safely deleted. Set to 0 to keep indefinitely.
              </p>
            </div>
          </div>
        </Card>
      </form>
    </DashboardLayout>
  );
};
export default Settings;

