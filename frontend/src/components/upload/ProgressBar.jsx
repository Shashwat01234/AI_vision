import React from 'react';
import { Loader2 } from 'lucide-react';

export const ProgressBar = ({
  progress = 0,
  status = 'Processing...',
  subtext = 'Analyzing visual & textual elements...',
  className = '',
}) => {
  return (
    <div
      role="progressbar"
      aria-valuenow={progress}
      aria-valuemin="0"
      aria-valuemax="100"
      aria-valuetext={`${status}: ${progress}%`}
      className={`bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4 ${className}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Loader2 className="w-5 h-5 text-indigo-600 animate-spin" aria-hidden="true" />
          <div>
            <h4 className="font-semibold text-slate-900 text-sm">{status}</h4>
            {subtext && <p className="text-xs text-slate-500">{subtext}</p>}
          </div>
        </div>
        <span className="text-sm font-bold text-indigo-600">{progress}%</span>
      </div>

      <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden p-0.5">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full transition-all duration-300 ease-out animate-progress-pulse"
          style={{ width: `${Math.min(Math.max(progress, 5), 100)}%` }}
        />
      </div>
    </div>
  );
};
export default ProgressBar;

