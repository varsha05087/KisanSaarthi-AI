import React, { useState } from 'react';
import {
  User,
  Languages,
  Volume2,
  Wifi,
  Shield,
  LogOut,
  ChevronRight,
  Check,
  Phone,
  Hash,
  Sparkles,
} from 'lucide-react';
import { useTranslation } from '../i18n';
import { useFarmerAuth } from '../context/FarmerAuthContext';
import { formatPhoneNumber } from '../services/farmerAuth';
import ConfirmDialog from '../components/common/ConfirmDialog';

export default function Profile({ onOpenLanguageModal, isOnline = true }) {
  const { t, currentLanguageInfo } = useTranslation();
  const { currentFarmer, logoutFarmer } = useFarmerAuth();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleConfirmLogout = () => {
    setShowLogoutConfirm(false);
    logoutFarmer();
  };

  return (
    <div className="pb-28 pt-4 px-4 sm:px-6 space-y-5 max-w-2xl mx-auto animate-fadeIn select-none">
      {/* Title */}
      <h2 className="text-2xl font-bold text-earth-text tracking-tight">
        {t('nav.profile')}
      </h2>

      {/* Current Farmer Identity Card */}
      <div className="p-5 rounded-3xl bg-white border-2 border-forest/30 shadow-farmer space-y-3">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-forest-50 border-2 border-forest/30 flex items-center justify-center text-3xl flex-shrink-0">
            {currentFarmer?.avatar || '👨‍🌾'}
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="font-black text-xl text-earth-text truncate">
              {currentFarmer?.name || t('profile.defaultFarmerName')}
            </h3>

            <div className="flex items-center gap-2 text-xs text-earth-muted font-medium mt-0.5">
              <Phone className="w-3.5 h-3.5 text-forest" />
              <span className="font-mono font-bold tracking-wider text-earth-text">
                {formatPhoneNumber(currentFarmer?.phone) || '98765 43210'}
              </span>
            </div>

            <div className="flex items-center gap-2 text-xs text-earth-muted mt-0.5">
              <Hash className="w-3.5 h-3.5 text-forest" />
              <span className="font-mono text-[11px]">{currentFarmer?.id || 'farmer_001'}</span>
            </div>
          </div>
        </div>

        <div className="pt-2 border-t border-earth-border/60 flex items-center justify-between text-xs">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-forest-50 text-forest font-bold">
            <span className="w-2 h-2 rounded-full bg-forest animate-pulse" />
            <span>{t('profile.verifiedVoiceIdentity')}</span>
          </div>

          <span className="text-earth-muted font-medium">
            🌐 {currentLanguageInfo.nativeName}
          </span>
        </div>
      </div>

      {/* Settings Options */}
      <div className="space-y-3">
        {/* Language Selection Setting */}
        <div
          onClick={onOpenLanguageModal}
          role="button"
          tabIndex={0}
          className="p-4 rounded-2xl bg-white border border-earth-border hover:border-forest/40 shadow-sm flex items-center justify-between cursor-pointer transition-all active:scale-98"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest flex items-center justify-center">
              <Languages className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm sm:text-base text-earth-text">
                {t('status.changeLanguage')}
              </h4>
              <p className="text-xs text-earth-muted">
                {t('profile.currentLangPrefix')}{' '}
                <span className="font-bold text-forest">{currentLanguageInfo.nativeName}</span>
              </p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-earth-muted" />
        </div>

        {/* Network & Offline Status */}
        <div className="p-4 rounded-2xl bg-white border border-earth-border shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                isOnline ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
              }`}
            >
              <Wifi className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm sm:text-base text-earth-text">{t('profile.networkStatus')}</h4>
              <p className="text-xs text-earth-muted">
                {isOnline ? t('profile.connectedInternet') : t('profile.offlineMode')}
              </p>
            </div>
          </div>
          <span
            className={`text-xs font-bold px-2.5 py-1 rounded-full border ${
              isOnline
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : 'bg-amber-50 text-amber-800 border-amber-300'
            }`}
          >
            {isOnline ? t('status.online') : t('status.offline')}
          </span>
        </div>

        {/* Voice Feedback Audio Speed */}
        <div className="p-4 rounded-2xl bg-white border border-earth-border shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center">
              <Volume2 className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm sm:text-base text-earth-text">{t('profile.voiceSpeed')}</h4>
              <p className="text-xs text-earth-muted">{t('profile.voiceToneDesc')}</p>
            </div>
          </div>
          <span className="text-xs font-bold text-forest bg-forest-50 px-3 py-1 rounded-full">
            {t('profile.standardSpeed')}
          </span>
        </div>

        {/* Privacy & Safety */}
        <div className="p-4 rounded-2xl bg-white border border-earth-border shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm sm:text-base text-earth-text">{t('profile.privacySecurity')}</h4>
              <p className="text-xs text-earth-muted">{t('profile.privacyDesc')}</p>
            </div>
          </div>
          <Check className="w-5 h-5 text-forest" />
        </div>

        {/* Change Farmer / Logout Button */}
        <div
          onClick={() => setShowLogoutConfirm(true)}
          role="button"
          tabIndex={0}
          className="p-4 rounded-2xl bg-rose-50/70 border border-rose-200 hover:border-danger hover:bg-rose-50 shadow-sm flex items-center justify-between cursor-pointer transition-all active:scale-98"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-100 text-danger flex items-center justify-center">
              <LogOut className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-sm sm:text-base text-danger">
                {t('identity.changeFarmer')}
              </h4>
              <p className="text-xs text-earth-muted">
                {t('identity.logoutBtn')}
              </p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-danger" />
        </div>
      </div>

      {/* Confirmation Dialog for Change Farmer */}
      <ConfirmDialog
        isOpen={showLogoutConfirm}
        title={t('identity.changeFarmerTitle')}
        message={t('identity.changeFarmerConfirm')}
        confirmLabel={t('identity.logoutBtn')}
        cancelLabel={t('common.close')}
        isDestructive={true}
        icon={LogOut}
        onConfirm={handleConfirmLogout}
        onCancel={() => setShowLogoutConfirm(false)}
      />

      {/* Tagline Footer */}
      <div className="pt-6 text-center text-xs text-earth-muted space-y-1">
        <p className="font-bold text-forest">KisanSaarthi AI v1.0.0</p>
        <p>“Don’t make the farmer learn the app. Make the app understand the farmer.”</p>
      </div>
    </div>
  );
}
