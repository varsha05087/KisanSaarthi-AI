import React from 'react';
import { Check, X, Volume2, Globe } from 'lucide-react';
import { useTranslation, SUPPORTED_LANGUAGES } from '../../i18n';
import { speakText } from '../../services/voiceService';

export default function LanguageSelectorModal({ isOpen, onClose }) {
  const { lang, setLang, t } = useTranslation();

  if (!isOpen) return null;

  const handleSelect = (code) => {
    setLang(code);
  };

  const handlePlaySample = (e, language) => {
    e.stopPropagation();
    speakText(language.sampleGreeting, language.code);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/60 backdrop-blur-sm animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="lang-modal-title"
    >
      <div className="bg-white w-full max-w-lg rounded-t-3xl sm:rounded-3xl p-5 sm:p-6 shadow-2xl border border-earth-border max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-earth-border/60">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-forest-50 text-forest flex items-center justify-center">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <h2 id="lang-modal-title" className="text-lg font-bold text-earth-text">
                {t('status.changeLanguage')}
              </h2>
              <p className="text-xs text-earth-muted">
                తెలుగు • हिन्दी • English
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-full hover:bg-earth-subtle text-earth-muted hover:text-earth-text active:scale-95 transition-all"
            aria-label={t('common.close')}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Language Cards */}
        <div className="mt-4 space-y-3">
          {SUPPORTED_LANGUAGES.map((language) => {
            const isSelected = lang === language.code;

            return (
              <div
                key={language.code}
                onClick={() => handleSelect(language.code)}
                className={`
                  flex items-center justify-between p-4 rounded-2xl border-2 cursor-pointer transition-all duration-150
                  ${
                    isSelected
                      ? 'border-forest bg-forest-50/50 shadow-sm'
                      : 'border-earth-border hover:border-forest/40 hover:bg-earth-bg/50'
                  }
                `}
                role="button"
                tabIndex={0}
                aria-pressed={isSelected}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleSelect(language.code);
                  }
                }}
              >
                <div className="flex items-center gap-3.5">
                  <span className="text-2xl" role="img" aria-label={language.englishName}>
                    {language.flag}
                  </span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold text-earth-text">
                        {language.nativeName}
                      </span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-earth-subtle text-earth-muted">
                        {language.englishName}
                      </span>
                    </div>
                    <p className="text-xs text-forest font-medium mt-0.5">
                      "{language.sampleGreeting}"
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {/* Audio preview button */}
                  <button
                    type="button"
                    onClick={(e) => handlePlaySample(e, language)}
                    className="p-2 rounded-xl text-forest hover:bg-forest-100/60 active:scale-90 transition-all"
                    title={`Listen in ${language.englishName}`}
                    aria-label={`Listen greeting in ${language.englishName}`}
                  >
                    <Volume2 className="w-5 h-5" />
                  </button>

                  {/* Radio Indicator */}
                  <div
                    className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                      isSelected ? 'border-forest bg-forest text-white' : 'border-earth-muted/40'
                    }`}
                  >
                    {isSelected && <Check className="w-4 h-4 stroke-[3px]" />}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Action Button */}
        <div className="mt-6 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="w-full py-3.5 px-4 rounded-xl bg-forest hover:bg-forest-600 active:scale-[0.99] text-white font-bold text-base shadow-md shadow-forest/20 transition-all touch-target-lg flex items-center justify-center gap-2"
          >
            {t('common.done')}
          </button>
        </div>
      </div>
    </div>
  );
}
