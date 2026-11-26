import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import Button from './Button';

export const ErrorMessage = ({
  title = 'Something went wrong',
  message,
  onRetry,
  className = '',
}) => {
  return (
    <div
      role="alert"
      className={`p-4 rounded-xl border border-red-200 bg-red-50 text-red-800 flex items-start gap-3 ${className}`}
    >
      <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5 shrink-0" aria-hidden="true" />
      <div className="flex-1">
        <h4 className="font-semibold text-red-900">{title}</h4>
        {message && <p className="text-sm text-red-700 mt-1">{message}</p>}
        {onRetry && (
          <div className="mt-3">
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              icon={RefreshCw}
              className="bg-white hover:bg-red-50 border-red-300 text-red-700 focus:ring-red-500"
            >
              Try Again
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
export default ErrorMessage;

