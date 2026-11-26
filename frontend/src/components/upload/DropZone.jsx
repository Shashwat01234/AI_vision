import React, { useRef, useState } from 'react';
import { UploadCloud, Image, FileText, AlertCircle } from 'lucide-react';

const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.pdf', '.docx', '.doc', '.pptx', '.ppt', '.txt'];
const MAX_FILE_SIZE_MB = 50;

export const DropZone = ({ onFileSelected, disabled = false }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);

  const validateAndHandle = (file) => {
    setErrorMessage('');
    if (!file) return;

    // Check size
    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > MAX_FILE_SIZE_MB) {
      setErrorMessage(`File is too large (${sizeMb.toFixed(1)}MB). Max allowed size is ${MAX_FILE_SIZE_MB}MB.`);
      return;
    }

    // Check extension
    const name = file.name.toLowerCase();
    const hasValidExt = ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext));
    if (!hasValidExt) {
      setErrorMessage(`Unsupported format. Please upload: JPG, PNG, WEBP, PDF, DOCX, PPTX, or TXT.`);
      return;
    }

    onFileSelected(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndHandle(e.dataTransfer.files[0]);
    }
  };

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleKeyDown = (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <div className="w-full">
      <div
        role="button"
        tabIndex={disabled ? -1 : 0}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        aria-label="Upload file drop zone. Click to browse files or drag and drop here."
        aria-disabled={disabled}
        className={`relative border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-all cursor-pointer focus:outline-none focus:ring-4 focus:ring-indigo-400/30 ${
          isDragOver
            ? 'border-indigo-600 bg-indigo-50/70 scale-[1.01]'
            : 'border-slate-300 hover:border-indigo-400 bg-white hover:bg-slate-50/60'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ALLOWED_EXTENSIONS.join(',')}
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              validateAndHandle(e.target.files[0]);
            }
          }}
          disabled={disabled}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center shadow-inner">
            <UploadCloud className="w-8 h-8" aria-hidden="true" />
          </div>

          <div className="space-y-1">
            <h3 className="text-lg font-semibold text-slate-800">
              Drag & drop your file here, or{' '}
              <span className="text-indigo-600 underline font-bold">browse</span>
            </h3>
            <p className="text-sm text-slate-500">
              Supports Images (JPG, PNG, WEBP) & Documents (PDF, DOCX, PPTX, TXT) up to 50MB
            </p>
          </div>

          <div className="flex items-center gap-6 pt-2 text-xs text-slate-400 font-medium">
            <span className="flex items-center gap-1.5">
              <Image className="w-4 h-4 text-slate-500" aria-hidden="true" /> Images for sign & scene analysis
            </span>
            <span className="flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-slate-500" aria-hidden="true" /> Documents for text & visual extraction
            </span>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="mt-3 flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-200" role="alert">
          <AlertCircle className="w-5 h-5 shrink-0" aria-hidden="true" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
export default DropZone;

