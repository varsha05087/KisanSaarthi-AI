import React from 'react';
import { WifiOff, RefreshCw } from 'lucide-react';
import { useTranslation } from '../../i18n';

export default function OfflineBanner({ isOnline = true, pendingSyncCount = 0 }) {
  const { t } = useTranslation();

  if (isOnline) return null;

  return (
    <div
      className="bg-amber-500 text-amber-950 px-4 py-2.5 sm:px-6 text-xs sm:text-sm font-medium border-b border-amber-600/30 flex items-center justify-between gap-3 shadow-inner"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-full bg-amber-600/20 flex items-center justify-center flex-shrink-0">
          <WifiOff className="w-4 h-4 text-amber-950" />
        </div>
        <p className="leading-snug">
          {t('status.offlineMessage')}
        </p>
      </div>

      {pendingSyncCount > 0 && (
        <span className="flex-shrink-0 inline-flex items-center gap-1 text-xs bg-amber-600/20 px-2 py-1 rounded-full font-bold">
          <RefreshCw className="w-3 h-3 animate-spin" /> {pendingSyncCount} {t('offline.savedCount')}
        </span>
      )}
    </div>
  );
}
