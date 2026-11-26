import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import DashboardLayout from '../components/layout/DashboardLayout';
import DropZone from '../components/upload/DropZone';
import FilePreview from '../components/upload/FilePreview';
import ProgressBar from '../components/upload/ProgressBar';
import Button from '../components/common/Button';
import ErrorMessage from '../components/common/ErrorMessage';
import {
  uploadFile,
  analyzeImage,
  analyzeDocument,
  getImageResult,
  getDocumentResult,
} from '../services/api';

export const Upload = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [selectedMode, setSelectedMode] = useState('explain');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [processingProgress, setProcessingProgress] = useState(30);
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileSelected = useCallback((file) => {
    setSelectedFile(file);
    setErrorMessage('');
    if (file.type?.startsWith('image/') || /\.(jpg|jpeg|png|webp)$/i.test(file.name)) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl('');
    }
  }, []);

  // Handle file passed from Dashboard quick upload
  useEffect(() => {
    if (location.state?.quickFile) {
      handleFileSelected(location.state.quickFile);
    }
  }, [location.state, handleFileSelected]);

  const handleRemoveFile = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl('');
    setUploadProgress(0);
    setIsUploading(false);
    setIsProcessing(false);
    setErrorMessage('');
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(10);
    setProcessingStatus('Uploading file to server...');
    setErrorMessage('');

    try {
      // 1. Upload file
      const uploadRes = await uploadFile(selectedFile, (progress) => {
        setUploadProgress(Math.min(progress, 90));
      });

      setUploadProgress(100);
      setIsUploading(false);
      setIsProcessing(true);
      setProcessingStatus('Initializing multimodal AI models...');

      const uploadId = uploadRes.upload_id;
      const fileType = uploadRes.file_type;

      // 2. Start analysis
      let taskRes;
      if (fileType === 'image') {
        taskRes = await analyzeImage(uploadId, selectedMode);
      } else {
        taskRes = await analyzeDocument(uploadId, selectedMode);
      }

      const taskId = taskRes.task_id;
      setProcessingStatus(`Analyzing ${fileType}...`);

      // 3. Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const result =
            fileType === 'image'
              ? await getImageResult(taskId)
              : await getDocumentResult(taskId);

          if (result.status === 'completed') {
            clearInterval(pollInterval);
            setProcessingProgress(100);
            setProcessingStatus('Analysis complete! Redirecting...');
            setTimeout(() => {
              if (fileType === 'image') {
                navigate(`/image-analysis?taskId=${taskId}&id=${uploadId}`);
              } else {
                navigate(`/document-analysis?taskId=${taskId}&id=${uploadId}`);
              }
            }, 600);
          } else if (result.status === 'failed') {
            clearInterval(pollInterval);
            setIsProcessing(false);
            setErrorMessage(result.error_message || 'Analysis processing failed.');
          } else {
            setProcessingProgress((prev) => Math.min(prev + 8, 92));
            setProcessingStatus(`Processing: ${result.status.replace(/_/g, ' ')}...`);
          }
        } catch (pollErr) {
          console.error('Polling error:', pollErr);
        }
      }, 2000);
    } catch (err) {
      console.error('Upload / Analysis error:', err);
      setIsUploading(false);
      setIsProcessing(false);
      const detail = err.response?.data?.detail || err.message || 'An error occurred during upload.';
      setErrorMessage(detail);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Upload & Analyze Visual Content
          </h1>
          <p className="text-slate-500 text-sm sm:text-base mt-1">
            Submit a photograph or educational document to generate accessible spoken explanations.
          </p>
        </div>

        {/* Error notification */}
        {errorMessage && (
          <ErrorMessage
            title="Analysis Notice"
            message={errorMessage}
            onRetry={handleStartAnalysis}
          />
        )}

        {/* Upload DropZone or FilePreview */}
        {!selectedFile ? (
          <DropZone onFileSelected={handleFileSelected} />
        ) : (
          <div className="space-y-6">
            <FilePreview
              file={selectedFile}
              previewUrl={previewUrl}
              selectedMode={selectedMode}
              onModeChange={setSelectedMode}
              onRemove={handleRemoveFile}
              isProcessing={isUploading || isProcessing}
            />

            {(isUploading || isProcessing) && (
              <ProgressBar
                progress={isUploading ? uploadProgress : processingProgress}
                status={isUploading ? 'Uploading file...' : processingStatus}
                subtext="Extracting structured document content, tables, and generating spoken narration."
              />
            )}

            {!isUploading && !isProcessing && (
              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={handleRemoveFile}>
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="lg"
                  icon={Sparkles}
                  onClick={handleStartAnalysis}
                >
                  Start AI Analysis
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};
export default Upload;

