import React from 'react';
import { AlertCircle, X, Check } from 'lucide-react';
import { useTranslation } from '../../i18n';

export default function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel,
  cancelLabel,
  onConfirm,
  onCancel,
  isDestructive = false,
  icon: Icon = AlertCircle,
}) {
  const { t } = useTranslation();

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
    >
      <div className="bg-white w-full max-w-sm rounded-3xl p-5 sm:p-6 shadow-2xl border border-earth-border select-none">
        {/* Header Icon & Title */}
        <div className="flex flex-col items-center text-center">
          <div
            className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-3 shadow-sm ${
              isDestructive
                ? 'bg-rose-50 text-danger border border-rose-200'
                : 'bg-forest-50 text-forest border border-forest/20'
            }`}
          >
            <Icon className="w-7 h-7" />
          </div>

          <h3 id="confirm-dialog-title" className="text-lg font-bold text-earth-text">
            {title}
          </h3>

          <p className="text-xs sm:text-sm text-earth-muted mt-1.5 leading-relaxed">
            {message}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="py-3 px-4 rounded-xl border border-earth-border hover:bg-earth-subtle text-earth-text font-bold text-sm active:scale-95 transition-all touch-target-lg"
          >
            {cancelLabel || t('common.close')}
          </button>

          <button
            type="button"
            onClick={onConfirm}
            className={`py-3 px-4 rounded-xl text-white font-bold text-sm flex items-center justify-center gap-1.5 shadow-md active:scale-95 transition-all touch-target-lg ${
              isDestructive
                ? 'bg-danger hover:bg-red-700 shadow-danger/25'
                : 'bg-forest hover:bg-forest-600 shadow-forest/25'
            }`}
          >
            <Check className="w-4 h-4 stroke-[3px]" />
            <span>{confirmLabel || t('common.confirm')}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
