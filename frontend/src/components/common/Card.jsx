import React from 'react';

/**
 * Farmer-friendly Card primitive
 * - High contrast
 * - Rounded corners (rounded-2xl)
 * - Soft shadow
 * - Generous touch targets
 */
export default function Card({
  children,
  className = '',
  onClick,
  interactive = false,
  role,
  ariaLabel,
  highlight = false,
}) {
  const isClickable = interactive || Boolean(onClick);

  return (
    <div
      onClick={onClick}
      role={role || (isClickable ? 'button' : undefined)}
      tabIndex={isClickable ? 0 : undefined}
      aria-label={ariaLabel}
      onKeyDown={(e) => {
        if (isClickable && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick && onClick(e);
        }
      }}
      className={`
        bg-white rounded-2xl p-4 sm:p-5 transition-all duration-200
        border ${highlight ? 'border-forest ring-2 ring-forest/20 shadow-farmer-lg' : 'border-earth-border/60 shadow-farmer'}
        ${isClickable ? 'cursor-pointer hover:border-forest/50 hover:shadow-farmer-lg active:scale-[0.98]' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
