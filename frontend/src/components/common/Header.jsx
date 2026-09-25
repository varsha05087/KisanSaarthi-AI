import React from 'react';
import { Languages, Wifi, WifiOff, Sparkles } from 'lucide-react';
import { useTranslation } from '../../i18n';

export default function Header({ isOnline = true, onOpenLanguageModal }) {
  const { t, currentLanguageInfo } = useTranslation();

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-earth-border/70 px-4 py-3 sm:px-6 transition-colors">
      <div className="flex items-center justify-between gap-2 max-w-2xl mx-auto">
        {/* Brand identity */}
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-forest flex items-center justify-center text-white shadow-md shadow-forest/20 flex-shrink-0">
            <span className="text-xl sm:text-2xl" role="img" aria-label="Sprout">🌱</span>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="text-lg sm:text-xl font-bold tracking-tight text-earth-text leading-tight">
                {t('appName')}
              </h1>
              <span className="inline-flex items-center gap-0.5 text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-full bg-forest-50 text-forest border border-forest/20">
                <Sparkles className="w-2.5 h-2.5" /> AI
              </span>
            </div>
            <p className="text-xs text-earth-muted font-medium">
              {t('tagline')}
            </p>
          </div>
        </div>

        {/* Action Controls: Language & Connectivity */}
        <div className="flex items-center gap-2">
          {/* Online / Offline status badge */}
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs font-semibold border transition-all ${
              isOnline
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : 'bg-amber-50 text-amber-800 border-amber-300'
            }`}
            title={isOnline ? t('status.online') : t('status.offline')}
            aria-label={isOnline ? t('status.online') : t('status.offline')}
          >
            {isOnline ? (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
                <span className="hidden xs:inline">{t('status.online')}</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3.5 h-3.5 text-amber-700" />
                <span className="hidden xs:inline">{t('status.offline')}</span>
              </>
            )}
          </div>

          {/* Language Selector Button */}
          <button
            type="button"
            onClick={onOpenLanguageModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-forest-50 hover:bg-forest-100 text-forest-dark border border-forest/20 font-medium text-xs sm:text-sm active:scale-95 transition-all touch-target-lg sm:min-h-0"
            aria-label={t('status.changeLanguage')}
          >
            <Languages className="w-4 h-4 text-forest" />
            <span className="font-semibold">{currentLanguageInfo.nativeName}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
