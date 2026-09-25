import React, { useState } from 'react';
import { Check, RotateCcw, X, Loader2, Sparkles, Image as ImageIcon, AlertTriangle } from 'lucide-react';
import { useTranslation } from '../../i18n';
import { formatFileSize } from '../../services/imageService';

export default function ImagePreviewModal({
  isOpen,
  imageFile,
  previewUrl,
  onClose,
  onRetake,
  onConfirmUpload,
}) {
  const { t } = useTranslation();
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  if (!isOpen || !previewUrl) return null;

  const handleSend = async () => {
    setIsAnalyzing(true);
    // Invoke confirm callback, allowing parent/service to simulate or call vision API
    try {
      await onConfirmUpload(imageFile);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="preview-title"
    >
      <div className="bg-white w-full max-w-md rounded-3xl p-5 sm:p-6 shadow-2xl border border-earth-border overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-earth-border/60">
          <div className="flex items-center gap-2">
            <ImageIcon className="w-5 h-5 text-forest" />
            <h3 id="preview-title" className="font-bold text-earth-text text-base sm:text-lg">
              {t('imageModal.previewTitle')}
            </h3>
          </div>
          {!isAnalyzing && (
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-full hover:bg-earth-subtle text-earth-muted"
              aria-label={t('common.close')}
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Image Display */}
        <div className="mt-4 relative rounded-2xl overflow-hidden bg-earth-subtle border border-earth-border aspect-[4/3] flex items-center justify-center">
          <img
            src={previewUrl}
            alt="Farmer upload preview"
            className="w-full h-full object-contain"
          />

          {/* Analyzing Overlay */}
          {isAnalyzing && (
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center text-white p-4 text-center animate-fadeIn">
              <div className="w-14 h-14 rounded-2xl bg-forest flex items-center justify-center shadow-lg mb-3 animate-bounce">
                <Sparkles className="w-7 h-7 text-harvest" />
              </div>
              <h4 className="text-lg font-bold">
                {t('imageModal.analyzing')}
              </h4>
              <p className="text-xs text-white/80 mt-1 max-w-xs">
                {t('imageModal.analyzingHint')}
              </p>
              <div className="mt-3 flex items-center gap-1.5 text-xs text-harvest font-semibold">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{t('imageModal.visionAgentReady')}</span>
              </div>
            </div>
          )}
        </div>

        {/* File meta info */}
        {imageFile && !isAnalyzing && (
          <div className="mt-2.5 flex items-center justify-between text-xs text-earth-muted px-1">
            <span className="truncate max-w-[200px]">{imageFile.name}</span>
            <span>{formatFileSize(imageFile.size)}</span>
          </div>
        )}

        {/* Question Prompt */}
        {!isAnalyzing ? (
          <div className="mt-4 text-center">
            <p className="text-sm font-semibold text-earth-text">
              {t('imageModal.confirmQuestion')}
            </p>

            <div className="mt-4 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={onRetake}
                className="py-3 px-3 rounded-xl border border-earth-border hover:bg-earth-subtle text-earth-text font-bold text-sm flex items-center justify-center gap-2 active:scale-95 transition-all touch-target-lg"
              >
                <RotateCcw className="w-4 h-4 text-earth-muted" />
                <span>{t('imageModal.retake')}</span>
              </button>

              <button
                type="button"
                onClick={handleSend}
                className="py-3 px-3 rounded-xl bg-forest hover:bg-forest-600 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-md shadow-forest/20 active:scale-95 transition-all touch-target-lg"
              >
                <Check className="w-4 h-4 stroke-[3px]" />
                <span>{t('imageModal.sendPhoto')}</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="mt-4 text-center text-xs text-earth-muted">
            <span>{t('imageModal.checkingQuality')}</span>
          </div>
        )}
      </div>
    </div>
  );
}
