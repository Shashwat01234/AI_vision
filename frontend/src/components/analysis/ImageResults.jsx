import React, { useState } from 'react';
import {
  Sparkles,
  Compass,
  FileText,
  AlertTriangle,
  Layers,
  Eye,
  CheckCircle2,
  Volume2,
} from 'lucide-react';
import Card from '../common/Card';
import DetectionCard from './DetectionCard';
import Button from '../common/Button';

export const ImageResults = ({
  results,
  imageUrl,
  onGenerateAudio,
  isAudioGenerating = false,
}) => {
  const [activeTab, setActiveTab] = useState('explanation');

  if (!results) return null;

  const {
    scene_description,
    detected_signs = [],
    detected_objects = [],
    ocr_results = [],
    explanation,
    confidence_info,
    mode = 'explain',
  } = results;

  const notes = confidence_info?.notes || [];

  return (
    <div className="space-y-6">
      {/* Primary Result Banner / Card */}
      <Card
        title="AI Accessibility Explanation"
        subtitle={`Mode: ${mode.toUpperCase()} — Generated for clear comprehension`}
        icon={Sparkles}
        badge={
          <span className="px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-bold rounded-full border border-indigo-200 uppercase">
            {mode} Mode
          </span>
        }
        actions={
          onGenerateAudio && (
            <Button
              variant="primary"
              size="sm"
              icon={Volume2}
              isLoading={isAudioGenerating}
              onClick={onGenerateAudio}
            >
              Narrate Audio
            </Button>
          )
        }
      >
        <div className="space-y-4">
          <div className="p-5 rounded-xl bg-slate-50 border border-slate-200/80 text-slate-800 leading-relaxed text-base sm:text-lg font-medium">
            {explanation || 'No explanation generated.'}
          </div>

          {/* Uncertainty / Confidence Warnings */}
          {notes.length > 0 && (
            <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 text-sm space-y-1" role="note">
              <div className="flex items-center gap-2 font-semibold">
                <AlertTriangle className="w-4 h-4 text-amber-600" aria-hidden="true" />
                <span>Accessibility Uncertainty Notice:</span>
              </div>
              <ul className="list-disc list-inside space-y-0.5 text-xs text-amber-800 pl-1">
                {notes.map((note, idx) => (
                  <li key={idx}>{note}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </Card>

      {/* Visual Context Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Image Preview + Scene Description */}
        <div className="lg:col-span-1 space-y-6">
          <Card title="Source Image" icon={Eye}>
            {imageUrl ? (
              <img
                src={imageUrl}
                alt="Uploaded source subject to accessibility analysis"
                className="w-full h-auto max-h-72 object-contain rounded-xl border border-slate-200 bg-slate-100"
              />
            ) : (
              <div className="h-48 rounded-xl bg-slate-100 flex items-center justify-center text-slate-400 text-sm">
                Image preview unavailable
              </div>
            )}

            {scene_description && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Scene Overview:
                </h5>
                <p className="text-sm text-slate-700 leading-normal">{scene_description}</p>
              </div>
            )}
          </Card>
        </div>

        {/* Right 2 Columns: Structured Breakdown (Signs, Objects, OCR) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Detected Signs */}
          <Card
            title={`Detected Signs (${detected_signs.length})`}
            subtitle="Campus navigational, safety, and departmental signage"
            icon={Compass}
          >
            {detected_signs.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {detected_signs.map((sign, idx) => (
                  <DetectionCard key={idx} item={sign} type="sign" />
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 italic py-2">
                No campus or safety signs identified in this image.
              </p>
            )}
          </Card>

          {/* OCR Extracted Text */}
          <Card
            title={`Extracted Printed Text (${ocr_results.length} blocks)`}
            subtitle="Direct text recognized via PaddleOCR"
            icon={FileText}
          >
            {ocr_results.length > 0 ? (
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {ocr_results.map((ocr, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between gap-4 text-xs"
                  >
                    <span className="font-mono text-slate-800 text-sm font-medium">"{ocr.text}"</span>
                    <span className="shrink-0 font-semibold px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                      {Math.round((ocr.confidence || 0) * 100)}% conf
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 italic py-2">
                No printed or legible text detected in this image.
              </p>
            )}
          </Card>

          {/* General Objects */}
          {detected_objects.length > 0 && (
            <Card
              title={`Visible Surroundings & Objects (${detected_objects.length})`}
              icon={Layers}
            >
              <div className="flex flex-wrap gap-2">
                {detected_objects.map((obj, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 border border-slate-200 text-slate-800 text-xs font-medium"
                  >
                    <span>{obj.label}</span>
                    <span className="text-slate-400 font-mono">({Math.round((obj.confidence || 0) * 100)}%)</span>
                  </span>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
export default ImageResults;

