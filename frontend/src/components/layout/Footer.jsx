import React from 'react';
import { Heart, ShieldCheck, Eye } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-white border-t border-slate-200 mt-auto py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-center md:text-left">
          <div className="flex items-center gap-2 text-slate-700 font-semibold text-sm">
            <Eye className="w-4 h-4 text-indigo-600" aria-hidden="true" />
            <span>AI Accessibility Assistant for Visually Impaired Students</span>
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-500">
            <span>WCAG 2.1 AA Compliant</span>
            <span>•</span>
            <span>Offline-First AI</span>
            <span>•</span>
            <span>Piper TTS Narration</span>
          </div>

          <div className="text-xs text-slate-400">
            CSE AIML Major Project &copy; {new Date().getFullYear()}
          </div>
        </div>
      </div>
    </footer>
  );
};
export default Footer;

