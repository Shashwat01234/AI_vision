import React from 'react';
import { Image as ImageIcon, FileText, Trash2, BookOpen, Lightbulb, ListFilter } from 'lucide-react';
import Button from '../common/Button';

export const FilePreview = ({
  file,
  previewUrl,
  selectedMode,
  onModeChange,
  onRemove,
  isProcessing = false,
}) => {
  if (!file) return null;

  const isImage = file.type?.startsWith('image/') || /\.(jpg|jpeg|png|webp)$/i.test(file.name);
  const sizeMb = (file.size / (1024 * 1024)).toFixed(2);

  const modes = [
    {
      id: 'explain',
      label: 'Explain',
      icon: Lightbulb,
      description: 'Simplified explanation in friendly, everyday language.',
    },
    {
      id: 'read',
      label: 'Read',
      icon: BookOpen,
      description: 'Faithful, comprehensive narration of all visible content.',
    },
    {
      id: 'summarize',
      label: 'Summarize',
      icon: ListFilter,
      description: 'Key takeaways, critical signs, dates, and conclusions.',
    },
  ];

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
      {/* File Info Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div className="flex items-center gap-4 min-w-0">
          {isImage && previewUrl ? (
            <img
              src={previewUrl}
              alt="Uploaded file preview"
              className="w-16 h-16 object-cover rounded-xl border border-slate-200 shadow-sm"
            />
          ) : (
            <div className="w-16 h-16 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              {isImage ? (
                <ImageIcon className="w-8 h-8" aria-hidden="true" />
              ) : (
                <FileText className="w-8 h-8" aria-hidden="true" />
              )}
            </div>
          )}

          <div className="min-w-0">
            <h4 className="font-semibold text-slate-900 truncate text-base">{file.name}</h4>
            <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
              <span className="uppercase font-medium px-2 py-0.5 bg-slate-100 rounded">
                {file.name.split('.').pop()}
              </span>
              <span>•</span>
              <span>{sizeMb} MB</span>
              <span>•</span>
              <span className="text-emerald-600 font-medium">Ready for analysis</span>
            </div>
          </div>
        </div>

        {!isProcessing && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onRemove}
            icon={Trash2}
            className="text-red-600 hover:bg-red-50 hover:text-red-700"
            ariaLabel="Remove selected file"
          >
            Remove
          </Button>
        )}
      </div>

      {/* Accessibility Mode Selector */}
      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-slate-900">
          Select Accessibility Output Mode:
        </legend>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {modes.map((mode) => {
            const Icon = mode.icon;
            const isSelected = selectedMode === mode.id;

            return (
              <label
                key={mode.id}
                className={`relative flex flex-col p-4 rounded-xl border-2 transition-all cursor-pointer focus-within:ring-2 focus-within:ring-indigo-500 ${
                  isSelected
                    ? 'border-indigo-600 bg-indigo-50/50 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                } ${isProcessing ? 'opacity-60 cursor-not-allowed' : ''}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-semibold text-slate-900 text-sm">
                    <Icon
                      className={`w-4 h-4 ${isSelected ? 'text-indigo-600' : 'text-slate-400'}`}
                      aria-hidden="true"
                    />
                    <span>{mode.label}</span>
                  </div>
                  <input
                    type="radio"
                    name="analysisMode"
                    value={mode.id}
                    checked={isSelected}
                    onChange={(e) => onModeChange(e.target.value)}
                    disabled={isProcessing}
                    className="w-4 h-4 text-indigo-600 border-slate-300 focus:ring-indigo-500"
                  />
                </div>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed">{mode.description}</p>
              </label>
            );
          })}
        </div>
      </fieldset>
    </div>
  );
};
export default FilePreview;

