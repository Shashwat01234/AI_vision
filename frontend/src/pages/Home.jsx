import React from 'react';
import { Link } from 'react-router-dom';
import {
  Eye,
  FileText,
  Volume2,
  Compass,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Layers,
  Cpu,
  BookOpen,
} from 'lucide-react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import Button from '../components/common/Button';

export const Home = () => {
  const features = [
    {
      icon: Eye,
      title: 'Image & Sign Understanding',
      description:
        'Fine-tuned custom YOLO neural model identifies campus signs, safety symbols, directional indicators, and surroundings with independent PaddleOCR text recognition.',
      color: 'from-blue-600 to-indigo-600',
    },
    {
      icon: FileText,
      title: 'Multimodal Document Understanding',
      description:
        'Analyzes PDFs, DOCX, and PPTX — extracting headings, tabular data, text, and embedded diagrams & charts without silently omitting critical visuals.',
      color: 'from-indigo-600 to-purple-600',
    },
    {
      icon: Volume2,
      title: 'Neural Speech Narration',
      description:
        'Piper TTS offline speech synthesis delivers natural voice narration with seekable playback, speed control, replay, and live transcript synchronization.',
      color: 'from-purple-600 to-pink-600',
    },
  ];

  const steps = [
    {
      num: '01',
      title: 'Upload Photograph or Document',
      desc: 'Drag & drop any campus photograph, sign, assignment, or lecture slide in standard formats.',
    },
    {
      num: '02',
      title: 'Multi-Model AI Integration',
      desc: 'Simultaneous YOLO sign detection, OCR text reading, and Vision-Language scene interpretation.',
    },
    {
      num: '03',
      title: 'Understand & Listen',
      desc: 'Receive context-aware explanations in Read, Explain, or Summarize modes with immediate audio playback.',
    },
  ];

  const formats = [
    { cat: 'Images', exts: ['JPG', 'JPEG', 'PNG', 'WEBP'] },
    { cat: 'Documents', exts: ['PDF', 'DOCX', 'DOC', 'TXT'] },
    { cat: 'Presentations', exts: ['PPTX', 'PPT'] },
    { cat: 'Scanned Papers', exts: ['Scanned PDF (OCR)'] },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-white text-slate-900">
      <Navbar />

      <main id="main-content" tabIndex="-1" className="flex-1 focus:outline-none">
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-b from-indigo-50/70 via-white to-white py-20 sm:py-28">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-sm font-semibold shadow-sm animate-fade-in">
              <Sparkles className="w-4 h-4 text-indigo-600" aria-hidden="true" />
              <span>AI-Powered Accessibility Assistant for Visually Impaired Students</span>
            </div>

            <div className="space-y-4 max-w-4xl mx-auto">
              <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
                Understand the World{' '}
                <span className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 bg-clip-text text-transparent">
                  Beyond Vision.
                </span>
              </h1>
              <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
                Transform photographs, campus signage, surroundings, and complex documents into
                meaningful written explanations and natural audio narration.
              </p>
            </div>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link to="/dashboard">
                <Button size="lg" icon={ArrowRight} iconPosition="right" className="shadow-lg shadow-indigo-200">
                  Start Exploring
                </Button>
              </Link>
              <Link to="/upload">
                <Button variant="outline" size="lg">
                  Upload an Image or Document
                </Button>
              </Link>
            </div>

            {/* Trust badge */}
            <div className="pt-8 flex items-center justify-center gap-6 text-xs text-slate-500 font-medium">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-600" aria-hidden="true" /> 100% Offline Capable
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-indigo-600" aria-hidden="true" /> Screen-Reader Optimized
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-purple-600" aria-hidden="true" /> Custom Trained YOLO
              </span>
            </div>
          </div>
        </section>

        {/* 3 Core Features */}
        <section className="py-20 bg-slate-50 border-y border-slate-200/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
            <div className="text-center space-y-3 max-w-3xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-900">
                Engineered for Academic Independence
              </h2>
              <p className="text-slate-600 text-base">
                Bridging the gap between visual information and auditory comprehension through
                multimodal AI.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {features.map((f, i) => {
                const Icon = f.icon;
                return (
                  <div
                    key={i}
                    className="p-8 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow space-y-4"
                  >
                    <div
                      className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${f.color} flex items-center justify-center text-white shadow-md`}
                    >
                      <Icon className="w-7 h-7" aria-hidden="true" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900">{f.title}</h3>
                    <p className="text-sm text-slate-600 leading-relaxed">{f.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
            <div className="text-center space-y-3 max-w-2xl mx-auto">
              <span className="text-xs font-bold text-indigo-600 uppercase tracking-wider">
                Step-by-step
              </span>
              <h2 className="text-3xl font-bold text-slate-900">How the Assistant Works</h2>
              <p className="text-slate-600 text-base">
                Three effortless steps to transform any visual input into accessible knowledge.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {steps.map((s, i) => (
                <div
                  key={i}
                  className="relative p-8 rounded-2xl bg-slate-50 border border-slate-200 space-y-4"
                >
                  <span className="text-4xl font-extrabold text-indigo-200 font-mono block">
                    {s.num}
                  </span>
                  <h3 className="text-lg font-bold text-slate-900">{s.title}</h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Supported Formats */}
        <section className="py-16 bg-slate-50 border-t border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
            <h2 className="text-2xl font-bold text-slate-900">Supported Media & Document Formats</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto">
              {formats.map((fmt, i) => (
                <div key={i} className="p-4 bg-white border border-slate-200 rounded-xl space-y-2">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    {fmt.cat}
                  </span>
                  <div className="flex flex-wrap items-center justify-center gap-1.5">
                    {fmt.exts.map((e, ei) => (
                      <span
                        key={ei}
                        className="px-2 py-0.5 bg-slate-100 text-slate-700 text-xs font-bold rounded"
                      >
                        {e}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};
export default Home;

