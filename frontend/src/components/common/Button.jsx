import React from 'react';
import { Loader2 } from 'lucide-react';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  icon: Icon,
  iconPosition = 'left',
  onClick,
  type = 'button',
  className = '',
  ariaLabel,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer';

  const variants = {
    primary: 'bg-indigo-600 hover:bg-indigo-700 text-white focus:ring-indigo-500 shadow-sm',
    secondary: 'bg-slate-200 hover:bg-slate-300 text-slate-800 focus:ring-slate-400',
    outline: 'border border-slate-300 hover:bg-slate-100 text-slate-700 focus:ring-indigo-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500 shadow-sm',
    ghost: 'hover:bg-slate-100 text-slate-700 focus:ring-slate-400',
  };

  const sizes = {
    sm: 'text-sm px-3 py-1.5 gap-1.5 min-h-[36px]',
    md: 'text-base px-4 py-2.5 gap-2 min-h-[44px]',
    lg: 'text-lg px-6 py-3 gap-2.5 min-h-[50px]',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || isLoading}
      aria-label={ariaLabel}
      aria-busy={isLoading}
      className={`${baseClasses} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`}
      {...props}
    >
      {isLoading && <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />}
      {!isLoading && Icon && iconPosition === 'left' && <Icon className="w-5 h-5" aria-hidden="true" />}
      <span>{children}</span>
      {!isLoading && Icon && iconPosition === 'right' && <Icon className="w-5 h-5" aria-hidden="true" />}
    </button>
  );
};
export default Button;

