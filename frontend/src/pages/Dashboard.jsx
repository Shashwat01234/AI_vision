import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Image as ImageIcon,
  FileText,
  Clock,
  Sparkles,
  ArrowRight,
  TrendingUp,
  History,
  CheckCircle2,
} from 'lucide-react';
import DashboardLayout from '../components/layout/DashboardLayout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import DropZone from '../components/upload/DropZone';
import StatusBadge from '../components/common/StatusBadge';
import { getHistory, uploadFile } from '../services/api';

export const Dashboard = () => {
  const navigate = useNavigate();
  const [historyItems, setHistoryItems] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  // Time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  useEffect(() => {
    const fetchRecentHistory = async () => {
      try {
        const data = await getHistory(1, 5);
        setHistoryItems(data.items || []);
      } catch (err) {
        console.error('Failed to load recent history:', err);
      } finally {
        setIsLoadingHistory(false);
      }
    };
    fetchRecentHistory();
  }, []);

  const handleQuickUpload = (file) => {
    // Navigate to /upload with file state or pass file
    navigate('/upload', { state: { quickFile: file } });
  };

  const imageCount = historyItems.filter((i) => i.file_type === 'image').length;
  const docCount = historyItems.filter((i) => i.file_type === 'document').length;

  return (
    <DashboardLayout>
      <div className="space-y-8 animate-fade-in">
        {/* Welcome Banner */}
        <div className="p-8 rounded-3xl bg-gradient-to-r from-indigo-900 via-indigo-800 to-indigo-900 text-white shadow-md relative overflow-hidden">
          <div className="relative z-10 max-w-2xl space-y-3">
            <span className="px-3 py-1 rounded-full bg-white/10 text-indigo-200 text-xs font-semibold backdrop-blur-sm border border-white/10 inline-block">
              {getGreeting()}, Student
            </span>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              AI Accessibility Assistant
            </h1>
            <p className="text-indigo-200 text-sm sm:text-base leading-relaxed">
              Upload photographs, classroom signs, lecture presentations, or research documents to
              receive clear, spoken explanations and summaries.
            </p>
          </div>
          <Sparkles
            className="absolute right-6 -bottom-6 w-48 h-48 text-white/5 pointer-events-none"
            aria-hidden="true"
          />
        </div>

        {/* Quick Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            to="/upload"
            state={{ defaultCategory: 'image' }}
            className="group block p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:border-indigo-400 transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <div className="flex items-start justify-between">
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                <ImageIcon className="w-6 h-6" aria-hidden="true" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" aria-hidden="true" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mt-4">Analyze Image or Sign</h3>
            <p className="text-sm text-slate-500 mt-1">
              Detect campus signs, room labels, hazards, and understand surroundings with audio narration.
            </p>
          </Link>

          <Link
            to="/upload"
            state={{ defaultCategory: 'document' }}
            className="group block p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:border-indigo-400 transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <div className="flex items-start justify-between">
              <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                <FileText className="w-6 h-6" aria-hidden="true" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" aria-hidden="true" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mt-4">Analyze Document</h3>
            <p className="text-sm text-slate-500 mt-1">
              Extract text, tables, and embedded diagrams from PDFs, Word docs, and slides.
            </p>
          </Link>
        </div>

        {/* Quick Upload DropZone */}
        <Card title="Quick File Upload" subtitle="Drag or browse a file to begin instant analysis">
          <DropZone onFileSelected={handleQuickUpload} />
        </Card>

        {/* Recent Activity */}
        <Card
          title="Recent Activity"
          subtitle="Your recently analyzed images and documents"
          icon={Clock}
          actions={
            <Link to="/history">
              <Button variant="ghost" size="sm" icon={History}>
                View All History
              </Button>
            </Link>
          }
        >
          {isLoadingHistory ? (
            <div className="py-8 text-center text-slate-400 text-sm">Loading recent activity...</div>
          ) : historyItems.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {historyItems.map((item) => (
                <div
                  key={item.id}
                  className="py-3 flex items-center justify-between gap-4 hover:bg-slate-50/60 p-2 rounded-xl transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 rounded-lg bg-slate-100 text-slate-600 shrink-0">
                      {item.file_type === 'image' ? (
                        <ImageIcon className="w-5 h-5" aria-hidden="true" />
                      ) : (
                        <FileText className="w-5 h-5" aria-hidden="true" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <h4 className="font-semibold text-slate-900 text-sm truncate">
                        {item.original_filename}
                      </h4>
                      <p className="text-xs text-slate-500">
                        {new Date(item.upload_time).toLocaleDateString()} •{' '}
                        {(item.file_size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <StatusBadge status={item.status} />
                    <Link
                      to={
                        item.file_type === 'image'
                          ? `/image-analysis?id=${item.id}`
                          : `/document-analysis?id=${item.id}`
                      }
                    >
                      <Button variant="outline" size="sm">
                        View
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-10 space-y-2">
              <p className="text-sm text-slate-500">No documents or images analyzed yet.</p>
              <Link to="/upload">
                <Button size="sm" icon={Sparkles}>
                  Analyze Your First File
                </Button>
              </Link>
            </div>
          )}
        </Card>
      </div>
    </DashboardLayout>
  );
};
export default Dashboard;

