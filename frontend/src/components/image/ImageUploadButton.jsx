import React, { useState, useRef } from 'react';
import { Camera, Image as GalleryIcon, X, PlusCircle } from 'lucide-react';
import { useTranslation } from '../../i18n';
import { createPreviewUrl, revokePreviewUrl, validateImage } from '../../services/imageService';
import ImagePreviewModal from './ImagePreviewModal';

export default function ImageUploadButton({
  onImageSelected = () => {},
  variant = 'card', // 'card' (Home screen) | 'compact' (Chat input)
  className = '',
}) {
  const { t } = useTranslation();
  const [showOptions, setShowOptions] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [validationError, setValidationError] = useState('');

  const cameraInputRef = useRef(null);
  const galleryInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const check = validateImage(file);
    if (!check.valid) {
      setValidationError(check.error);
      return;
    }

    setValidationError('');
    setSelectedFile(file);
    const url = createPreviewUrl(file);
    setPreviewUrl(url);
    setShowOptions(false);
    setShowPreviewModal(true);

    // Reset inputs so user can choose the same file again if desired
    e.target.value = '';
  };

  const handleRetake = () => {
    revokePreviewUrl(previewUrl);
    setPreviewUrl(null);
    setSelectedFile(null);
    setShowPreviewModal(false);
    setShowOptions(true);
  };

  const handleCloseModal = () => {
    revokePreviewUrl(previewUrl);
    setPreviewUrl(null);
    setSelectedFile(null);
    setShowPreviewModal(false);
  };

  const handleConfirmUpload = async (file) => {
    await onImageSelected(file);
    // Keep modal briefly to let user see status, then close
    setTimeout(() => {
      handleCloseModal();
    }, 1200);
  };

  // Compact trigger for Chat input bar
  if (variant === 'compact') {
    return (
      <>
        {/* Hidden inputs */}
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileChange}
          className="hidden"
          aria-hidden="true"
        />
        <input
          ref={galleryInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
          aria-hidden="true"
        />

        <button
          type="button"
          onClick={() => setShowOptions(true)}
          className={`w-11 h-11 sm:w-12 sm:h-12 rounded-full border border-earth-border bg-white hover:bg-forest-50 text-forest flex items-center justify-center shadow-sm active:scale-95 transition-all ${className}`}
          aria-label="Add photo"
          title="Take or upload photo"
        >
          <Camera className="w-5 h-5" />
        </button>

        {/* Options Modal Bottom Sheet */}
        {showOptions && (
          <div
            className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/60 backdrop-blur-sm animate-fadeIn"
            role="dialog"
            aria-modal="true"
          >
            <div className="bg-white w-full max-w-sm rounded-t-3xl sm:rounded-3xl p-5 shadow-2xl border border-earth-border">
              <h4 className="font-bold text-earth-text text-base pb-3 border-b border-earth-border/60">
                {t('home.cameraCard.optionsTitle')}
              </h4>

              <div className="mt-3 space-y-2.5">
                <button
                  type="button"
                  onClick={() => cameraInputRef.current?.click()}
                  className="w-full p-4 rounded-2xl bg-forest-50 hover:bg-forest-100 text-forest-dark font-bold text-left flex items-center gap-3.5 active:scale-98 transition-all touch-target-lg"
                >
                  <Camera className="w-6 h-6 text-forest" />
                  <span>{t('home.cameraCard.takePhoto')}</span>
                </button>

                <button
                  type="button"
                  onClick={() => galleryInputRef.current?.click()}
                  className="w-full p-4 rounded-2xl bg-earth-subtle hover:bg-earth-border/50 text-earth-text font-bold text-left flex items-center gap-3.5 active:scale-98 transition-all touch-target-lg"
                >
                  <GalleryIcon className="w-6 h-6 text-earth-muted" />
                  <span>{t('home.cameraCard.chooseGallery')}</span>
                </button>
              </div>

              <button
                type="button"
                onClick={() => setShowOptions(false)}
                className="mt-3 w-full py-3 rounded-xl text-earth-muted hover:text-earth-text font-semibold text-sm"
              >
                {t('home.cameraCard.cancel')}
              </button>
            </div>
          </div>
        )}

        <ImagePreviewModal
          isOpen={showPreviewModal}
          imageFile={selectedFile}
          previewUrl={previewUrl}
          onClose={handleCloseModal}
          onRetake={handleRetake}
          onConfirmUpload={handleConfirmUpload}
        />
      </>
    );
  }

  // Large Card for Home Screen
  return (
    <>
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileChange}
        className="hidden"
        aria-hidden="true"
      />
      <input
        ref={galleryInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
        aria-hidden="true"
      />

      <div
        onClick={() => setShowOptions(true)}
        role="button"
        tabIndex={0}
        aria-label={t('home.cameraCard.title')}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setShowOptions(true);
          }
        }}
        className={`
          w-full rounded-3xl p-5 sm:p-6 bg-white border-2 border-forest/20 hover:border-forest/50
          shadow-farmer hover:shadow-farmer-lg cursor-pointer transition-all duration-200 active:scale-[0.99]
          flex items-center gap-4 sm:gap-5 ${className}
        `}
      >
        <div className="w-16 h-16 sm:w-18 sm:h-18 rounded-2xl bg-amber-50 text-harvest-dark border border-harvest/30 flex items-center justify-center flex-shrink-0 shadow-sm">
          <Camera className="w-8 h-8 sm:w-9 sm:h-9" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-lg sm:text-xl font-bold text-earth-text tracking-tight truncate">
              {t('home.cameraCard.title')}
            </h3>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-harvest-light text-amber-900 border border-harvest/30 hidden xs:inline">
              {t('imageModal.photoBadge')}
            </span>
          </div>

          <p className="text-xs sm:text-sm text-earth-muted mt-1 leading-snug line-clamp-2">
            {t('home.cameraCard.subtitle')}
          </p>

          <div className="mt-2 text-[11px] font-semibold text-forest flex items-center gap-1">
            <span>{t('home.cameraCard.examples')}</span>
          </div>
        </div>
      </div>

      {/* Options Modal Bottom Sheet */}
      {showOptions && (
        <div
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/60 backdrop-blur-sm animate-fadeIn"
          role="dialog"
          aria-modal="true"
        >
          <div className="bg-white w-full max-w-sm rounded-t-3xl sm:rounded-3xl p-5 shadow-2xl border border-earth-border">
            <h4 className="font-bold text-earth-text text-base pb-3 border-b border-earth-border/60">
              {t('home.cameraCard.optionsTitle')}
            </h4>

            <div className="mt-3 space-y-2.5">
              <button
                type="button"
                onClick={() => cameraInputRef.current?.click()}
                className="w-full p-4 rounded-2xl bg-forest-50 hover:bg-forest-100 text-forest-dark font-bold text-left flex items-center gap-3.5 active:scale-98 transition-all touch-target-lg"
              >
                <div className="w-10 h-10 rounded-xl bg-forest text-white flex items-center justify-center">
                  <Camera className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-base">{t('home.cameraCard.takePhoto')}</span>
                  <p className="text-xs text-earth-muted font-normal">{t('imageModal.useMobileCamera')}</p>
                </div>
              </button>

              <button
                type="button"
                onClick={() => galleryInputRef.current?.click()}
                className="w-full p-4 rounded-2xl bg-earth-subtle hover:bg-earth-border/50 text-earth-text font-bold text-left flex items-center gap-3.5 active:scale-98 transition-all touch-target-lg"
              >
                <div className="w-10 h-10 rounded-xl bg-earth-border text-earth-text flex items-center justify-center">
                  <GalleryIcon className="w-5 h-5 text-earth-muted" />
                </div>
                <div>
                  <span className="text-base">{t('home.cameraCard.chooseGallery')}</span>
                  <p className="text-xs text-earth-muted font-normal">{t('imageModal.selectFromDevice')}</p>
                </div>
              </button>
            </div>

            <button
              type="button"
              onClick={() => setShowOptions(false)}
              className="mt-4 w-full py-3 rounded-xl text-earth-muted hover:text-earth-text font-semibold text-sm active:scale-95 transition-all"
            >
              {t('home.cameraCard.cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Preview Confirmation Dialog */}
      <ImagePreviewModal
        isOpen={showPreviewModal}
        imageFile={selectedFile}
        previewUrl={previewUrl}
        onClose={handleCloseModal}
        onRetake={handleRetake}
        onConfirmUpload={handleConfirmUpload}
      />
    </>
  );
}
