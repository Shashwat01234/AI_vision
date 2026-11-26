import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, XCircle, Loader2 } from 'lucide-react';

export const StatusBadge = ({ status }) => {
  const normStatus = (status || '').toLowerCase();

  const configs = {
    completed: {
      label: 'Completed',
      bg: 'bg-emerald-50',
      text: 'text-emerald-700',
      border: 'border-emerald-200',
      icon: CheckCircle2,
    },
    processing: {
      label: 'Processing',
      bg: 'bg-indigo-50',
      text: 'text-indigo-700',
      border: 'border-indigo-200',
      icon: Loader2,
      spin: true,
    },
    generating_explanation: {
      label: 'Explaining',
      bg: 'bg-blue-50',
      text: 'text-blue-700',
      border: 'border-blue-200',
      icon: Loader2,
      spin: true,
    },
    generating_audio: {
      label: 'Audio Narration',
      bg: 'bg-purple-50',
      text: 'text-purple-700',
      border: 'border-purple-200',
      icon: Loader2,
      spin: true,
    },
    uploaded: {
      label: 'Uploaded',
      bg: 'bg-slate-50',
      text: 'text-slate-700',
      border: 'border-slate-200',
      icon: Clock,
    },
    validating: {
      label: 'Validating',
      bg: 'bg-amber-50',
      text: 'text-amber-700',
      border: 'border-amber-200',
      icon: Clock,
    },
    failed: {
      label: 'Failed',
      bg: 'bg-red-50',
      text: 'text-red-700',
      border: 'border-red-200',
      icon: XCircle,
    },
  };

  const config = configs[normStatus] || {
    label: status || 'Unknown',
    bg: 'bg-slate-50',
    text: 'text-slate-700',
    border: 'border-slate-200',
    icon: Clock,
  };

  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${config.bg} ${config.text} ${config.border}`}
      role="status"
    >
      <Icon className={`w-3.5 h-3.5 ${config.spin ? 'animate-spin' : ''}`} aria-hidden="true" />
      <span>{config.label}</span>
    </span>
  );
};
export default StatusBadge;

