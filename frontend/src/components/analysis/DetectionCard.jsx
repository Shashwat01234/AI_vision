import React from 'react';
import { Compass, DoorOpen, AlertOctagon, Building, Info, Box } from 'lucide-react';

export const DetectionCard = ({ item, type = 'sign' }) => {
  const label = item.label || 'Unknown';
  const confidence = item.confidence ? Math.round(item.confidence * 100) : 0;
  const ocrText = item.ocr_text || '';

  const getSignMeta = (lbl) => {
    switch (lbl.toLowerCase()) {
      case 'directional_sign':
        return { label: 'Directional Sign', icon: Compass, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' };
      case 'exit_sign':
        return { label: 'Emergency Exit', icon: DoorOpen, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200' };
      case 'safety_sign':
        return { label: 'Safety / Caution', icon: AlertOctagon, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200' };
      case 'department_sign':
        return { label: 'Department / Room', icon: Building, color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200' };
      case 'information_sign':
        return { label: 'Information Board', icon: Info, color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-200' };
      default:
        return { label: lbl.replace(/_/g, ' '), icon: Box, color: 'text-slate-600', bg: 'bg-slate-50', border: 'border-slate-200' };
    }
  };

  const meta = getSignMeta(label);
  const Icon = meta.icon;

  return (
    <div className={`p-4 rounded-xl border ${meta.border} ${meta.bg} flex flex-col justify-between space-y-2`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <Icon className={`w-5 h-5 ${meta.color} shrink-0`} aria-hidden="true" />
          <h5 className="font-semibold text-slate-900 text-sm">{meta.label}</h5>
        </div>
        <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-white/80 border border-slate-200 text-slate-700">
          {confidence}% match
        </span>
      </div>

      {ocrText && (
        <div className="p-2.5 rounded-lg bg-white/90 border border-slate-200 text-xs text-slate-800">
          <span className="font-semibold text-slate-500 block mb-0.5">Printed Text:</span>
          <span className="font-mono text-indigo-950 font-medium">"{ocrText}"</span>
        </div>
      )}

      {item.bbox && (
        <div className="text-[10px] text-slate-400 font-mono">
          Box: [{item.bbox.join(', ')}]
        </div>
      )}
    </div>
  );
};
export default DetectionCard;

