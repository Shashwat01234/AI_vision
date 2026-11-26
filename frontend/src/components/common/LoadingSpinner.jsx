import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ size = 'md', message = 'Loading...', className = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`flex flex-col items-center justify-center p-6 text-slate-500 gap-3 ${className}`} role="status">
      <Loader2 className={`${sizes[size] || sizes.md} animate-spin text-indigo-600`} aria-hidden="true" />
      {message && <span className="text-sm font-medium text-slate-600">{message}</span>}
      <span className="sr-only">{message}</span>
    </div>
  );
};
export default LoadingSpinner;

