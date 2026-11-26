import React from 'react';

export const Card = ({
  children,
  title,
  subtitle,
  icon: Icon,
  badge,
  actions,
  className = '',
  headerClassName = '',
  bodyClassName = '',
  role = 'region',
  ariaLabel,
}) => {
  return (
    <div
      role={role}
      aria-label={ariaLabel || title}
      className={`bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden ${className}`}
    >
      {(title || subtitle || Icon || badge || actions) && (
        <div className={`px-6 py-4 border-b border-slate-100 flex items-center justify-between ${headerClassName}`}>
          <div className="flex items-center gap-3">
            {Icon && (
              <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
                <Icon className="w-5 h-5" aria-hidden="true" />
              </div>
            )}
            <div>
              {title && <h3 className="text-lg font-semibold text-slate-900">{title}</h3>}
              {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {badge}
            {actions}
          </div>
        </div>
      )}
      <div className={`p-6 ${bodyClassName}`}>{children}</div>
    </div>
  );
};
export default Card;

