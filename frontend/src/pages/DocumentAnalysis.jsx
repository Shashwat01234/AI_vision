import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { UploadCloud, ArrowLeft, Volume2, FileText, Sparkles, History as HistoryIcon, Play } from 'lucide-react';
import DashboardLayout from '../components/layout/DashboardLayout';
import DocumentResults from '../components/analysis/DocumentResults';
import AudioPlayer from '../components/audio/AudioPlayer';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import { getDocumentResult, getHistoryItem, getHistory, analyzeDocument, generateAudio, getAudioUrl } from '../services/api';

export const DocumentAnalysis = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const taskId = searchParams.get('taskId');
  const uploadId = searchParams.get('id');

  const [results, setResults] = useState(null);
  const [audioUrl, setAudioUrl] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isAudioGenerating, setIsAudioGenerating] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [uploadRecord, setUploadRecord] = useState(null);
  const [emptyState, setEmptyState] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    setErrorMessage('');
    setEmptyState(false);

    try {
      if (taskId) {
        const res = await getDocumentResult(taskId);
        setResults(res);
        if (res.audio_id) {
          setAudioUrl(getAudioUrl(res.audio_id));
        } else if (uploadId) {
          const hist = await getHistoryItem(uploadId);
          setUploadRecord(hist.upload);
          if (hist.audio?.audio_id) {
            setAudioUrl(getAudioUrl(hist.audio.audio_id));
          }
        }
      } else if (uploadId) {
        const hist = await getHistoryItem(uploadId);
        setUploadRecord(hist.upload);

        // If this upload is actually an image, redirect to ImageAnalysis
        if (hist.upload?.file_type === 'image') {
          navigate(`/image-analysis?id=${uploadId}`, { replace: true });
          return;
        }

        if (hist.document_analysis) {
          setResults({
            ...hist.document_analysis,
            upload_id: uploadId,
          });
          if (hist.document_analysis.audio_id) {
            setAudioUrl(getAudioUrl(hist.document_analysis.audio_id));
          }
        }
        if (hist.audio?.audio_id) {
          setAudioUrl(getAudioUrl(hist.audio.audio_id));
        }
      } else {
        // No taskId or uploadId specified (e.g. clicked from sidebar)
        // Automatically find the most recent analyzed document in history
        const histData = await getHistory(1, 20);
        const latestAnalyzed = histData.items?.find((item) => item.file_type === 'document' && item.has_document_result);

        if (latestAnalyzed) {
          setSearchParams({ id: latestAnalyzed.id });
          return;
        }

        // Check if there is any document upload at all
        const anyDoc = histData.items?.find((item) => item.file_type === 'document');
        if (anyDoc) {
          setSearchParams({ id: anyDoc.id });
          return;
        }

        // Truly no documents uploaded yet
        setEmptyState(true);
      }
    } catch (err) {
      console.error('Error fetching document analysis:', err);
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to load document analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [taskId, uploadId]);

  const handleStartAnalysis = async () => {
    if (!uploadId) return;
    setIsAnalyzing(true);
    setErrorMessage('');
    try {
      const taskRes = await analyzeDocument(uploadId, 'explain');
      navigate(`/document-analysis?taskId=${taskRes.task_id}&id=${uploadId}`);
    } catch (err) {
      console.error('Failed to start document analysis:', err);
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to start analysis.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGenerateAudio = async () => {
    const textToSpeak = results?.explanation || results?.summary;
    if (!textToSpeak || !uploadId) return;

    setIsAudioGenerating(true);
    setErrorMessage('');
    try {
      const audioRes = await generateAudio(uploadId, textToSpeak);
      if (audioRes.audio_id) {
        setAudioUrl(getAudioUrl(audioRes.audio_id));
      }
    } catch (err) {
      console.error('Failed to generate server audio, using browser speech:', err);
      // Silently fall back to browser Web Speech API — no blocking alert
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.rate = 1.0;
        utterance.lang = 'en-US';
        window.speechSynthesis.speak(utterance);
        // Clear any stale error since browser speech is playing
        setErrorMessage('');
      } else {
        setErrorMessage('Audio narration is unavailable. Please read the text above.');
      }
    } finally {
      setIsAudioGenerating(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
        {/* Top Navigation Row */}
        <div className="flex items-center justify-between">
          <Link to="/dashboard">
            <Button variant="ghost" size="sm" icon={ArrowLeft}>
              Back to Dashboard
            </Button>
          </Link>

          <Link to="/upload" state={{ defaultCategory: 'document' }}>
            <Button variant="outline" size="sm" icon={UploadCloud}>
              Upload Another File
            </Button>
          </Link>
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="py-24 text-center">
            <LoadingSpinner size="lg" message="Loading document analysis results..." />
          </div>
        )}

        {/* Error state */}
        {!isLoading && errorMessage && (
          <ErrorMessage
            title="Analysis Notice"
            message={errorMessage}
            onRetry={loadData}
          />
        )}

        {/* Empty State: No document uploaded yet */}
        {!isLoading && emptyState && (
          <Card className="text-center py-16 space-y-4">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center shadow-inner">
              <FileText className="w-8 h-8" aria-hidden="true" />
            </div>
            <div className="space-y-1.5 max-w-md mx-auto">
              <h3 className="text-xl font-bold text-slate-900">No Document Selected</h3>
              <p className="text-sm text-slate-500">
                You haven't uploaded a document yet. Upload a PDF, Word (DOCX), or PowerPoint (PPTX) file to extract headings, structure, and listen to spoken narration.
              </p>
            </div>
            <div className="pt-3 flex justify-center gap-3">
              <Link to="/upload" state={{ defaultCategory: 'document' }}>
                <Button icon={UploadCloud}>Upload Document Now</Button>
              </Link>
              <Link to="/history">
                <Button variant="outline" icon={HistoryIcon}>View History</Button>
              </Link>
            </div>
          </Card>
        )}

        {/* Uploaded but unanalyzed state */}
        {!isLoading && !results && uploadRecord && !emptyState && (
          <Card className="text-center py-12 space-y-4">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Sparkles className="w-7 h-7" aria-hidden="true" />
            </div>
            <div className="space-y-1 max-w-md mx-auto">
              <h3 className="text-lg font-bold text-slate-900">
                {uploadRecord.original_filename}
              </h3>
              <p className="text-sm text-slate-500">
                This document is uploaded and ready for structural extraction, AI explanations, and audio narration.
              </p>
            </div>
            <div className="pt-2">
              <Button
                icon={Play}
                isLoading={isAnalyzing}
                onClick={handleStartAnalysis}
              >
                Start AI Analysis
              </Button>
            </div>
          </Card>
        )}

        {/* Results */}
        {!isLoading && results && (
          <div className="space-y-8">
            <DocumentResults
              results={results}
              onGenerateAudio={handleGenerateAudio}
              isAudioGenerating={isAudioGenerating}
            />

            {/* Audio Player */}
            {(audioUrl || results.explanation || results.summary) && (
              <div className="pt-2">
                <AudioPlayer
                  audioUrl={audioUrl}
                  textToNarrate={results.explanation || results.summary}
                  title="Document Narration"
                />
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};
export default DocumentAnalysis;

