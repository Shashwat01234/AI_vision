import React from 'react';
import {
  Info,
  ShieldCheck,
  Eye,
  Cpu,
  BookOpen,
  Volume2,
  Layers,
  HeartHandshake,
  AlertTriangle,
} from 'lucide-react';
import DashboardLayout from '../components/layout/DashboardLayout';
import Card from '../components/common/Card';

export const About = () => {
  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in pb-12">
        {/* Header */}
        <div>
          <span className="px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-bold uppercase tracking-wider inline-block">
            Project No. 40 • CSE AIML
          </span>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mt-2">
            About AI Accessibility Assistant
          </h1>
          <p className="text-slate-600 text-base mt-1">
            An intelligent multimodal application empowering visually impaired students to understand
            photographs, campus signage, surroundings, and complex documents.
          </p>
        </div>

        {/* 1. Core Objective */}
        <Card title="Core Project Objective" icon={Eye}>
          <div className="space-y-3 text-slate-700 text-sm sm:text-base leading-relaxed">
            <p>
              Navigating university campuses and parsing educational courseware presents substantial
              accessibility barriers for students with visual impairments. Visual signage—such as
              directional arrows, department labels, emergency exits, and safety warnings—is typically
              inaccessible without sight or sighted assistance.
            </p>
            <p>
              <strong>AI Accessibility Assistant</strong> addresses this by serving as an upload-based,
              offline-capable multimodal bridge. Students upload photos of their surroundings or
              digital coursework documents, and receive context-aware written explanations paired with
              high-fidelity neural audio narration.
            </p>
          </div>
        </Card>

        {/* 2. AI Technologies Used */}
        <Card title="Multimodal AI Architecture" icon={Cpu}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
              <h4 className="font-bold text-indigo-700 flex items-center gap-2">
                <Layers className="w-4 h-4" aria-hidden="true" />
                <span>Custom Fine-Tuned YOLO</span>
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Lightweight YOLO11n object detector fine-tuned across 5 campus accessibility classes:
                directional signs, department signs, safety signs, exit signs, and information boards.
              </p>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
              <h4 className="font-bold text-indigo-700 flex items-center gap-2">
                <BookOpen className="w-4 h-4" aria-hidden="true" />
                <span>PaddleOCR Text Recognition</span>
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Robust two-stage OCR pipeline performing text detection and angle-classification to
                faithfully extract printed alphanumeric text from signs and documents.
              </p>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
              <h4 className="font-bold text-indigo-700 flex items-center gap-2">
                <Eye className="w-4 h-4" aria-hidden="true" />
                <span>Vision-Language Model (VLM)</span>
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                moondream2 edge-optimized VLM delivers contextual scene descriptions, spatial
                surroundings analysis, and answers questions regarding visual features without relying
                on external paid APIs.
              </p>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
              <h4 className="font-bold text-indigo-700 flex items-center gap-2">
                <Volume2 className="w-4 h-4" aria-hidden="true" />
                <span>Piper Neural Text-to-Speech</span>
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                High-quality offline ONNX neural TTS engine generating clear human-sounding voice
                narration with seekable audio controls and dynamic playback speeds.
              </p>
            </div>
          </div>
        </Card>

        {/* 3. Accessibility Standards */}
        <Card title="Accessibility Commitment (WCAG 2.1 AA)" icon={ShieldCheck}>
          <ul className="space-y-2 text-sm text-slate-700 list-disc list-inside">
            <li>Semantic HTML5 landmark tags (main, nav, aside, header, footer)</li>
            <li>ARIA labels and roles across all interactive controls and progress bars</li>
            <li>Visible focus rings and full keyboard-only operability without a mouse</li>
            <li>High-contrast mode and customizable base text scaling up to 22px</li>
            <li>Reduced-motion support respecting system preferences</li>
            <li>Never communicates critical information through color alone</li>
          </ul>
        </Card>

        {/* 4. Limitations & Ethical Considerations */}
        <Card title="Limitations & Responsible AI Principles" icon={AlertTriangle}>
          <div className="space-y-3 text-xs sm:text-sm text-slate-600 leading-relaxed">
            <p>
              • <strong>Upload-Based Only:</strong> This system is strictly an upload-based assistant.
              It does not perform real-time video surveillance, obstacle avoidance, or autonomous
              navigation.
            </p>
            <p>
              • <strong>No Facial Recognition:</strong> People visible in images are treated as
              generic scene elements without identifying individuals.
            </p>
            <p>
              • <strong>Uncertainty Communication:</strong> If sign detection confidence is low or text
              is blurry, the system explicitly communicates uncertainty rather than fabricating details.
            </p>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
};
export default About;

