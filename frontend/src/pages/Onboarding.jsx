import React, { useState } from 'react';
import {
  Volume2,
  Check,
  ArrowRight,
  Sparkles,
  Mic,
  RotateCcw,
  Smartphone,
  Keyboard,
  User,
  Phone,
  Edit2,
  AlertCircle,
} from 'lucide-react';
import { useTranslation, SUPPORTED_LANGUAGES } from '../i18n';
import { speakText } from '../services/voiceService';
import { parseSpokenDigits, formatPhoneNumber } from '../services/farmerAuth';
import { useFarmerAuth } from '../context/FarmerAuthContext';
import VoiceButton from '../components/voice/VoiceButton';

export default function Onboarding({ onFinish }) {
  const { lang, setLang, t } = useTranslation();
  const { loginFarmer, loginWithDevice } = useFarmerAuth();

  // Step state: 1 = language, 2 = voice name, 3 = voice phone
  const [step, setStep] = useState(1);
  const [selectedLang, setSelectedLang] = useState(lang || 'te');

  // Name state
  const [spokenName, setSpokenName] = useState('');
  const [isManualName, setIsManualName] = useState(false);
  const [manualNameInput, setManualNameInput] = useState('');

  // Phone state
  const [spokenPhone, setSpokenPhone] = useState('');
  const [isManualPhone, setIsManualPhone] = useState(false);
  const [manualPhoneInput, setManualPhoneInput] = useState('');

  // --- Step 1: Language handlers ---
  const handleSelectLanguage = (code) => {
    setSelectedLang(code);
    setLang(code);
  };

  const handlePlayAudio = (e, language) => {
    e.stopPropagation();
    speakText(language.sampleGreeting, language.code);
  };

  const handleLanguageNext = () => {
    setStep(2);
    // Voice prompt asking for name
    const promptText =
      selectedLang === 'te'
        ? 'మీ పేరు చెప్పండి'
        : selectedLang === 'hi'
        ? 'अपना नाम बताइए'
        : 'Please tell me your name';
    speakText(promptText, selectedLang);
  };

  // --- Step 2: Name handlers ---
  const handleVoiceNameResult = (transcript) => {
    if (!transcript) return;
    // Clean up transcript: take first 2-3 words as name
    const cleanName = transcript
      .replace(/[.,/#!$%^&*;:{}=\-_`~()]/g, '')
      .trim();
    setSpokenName(cleanName);
  };

  const handleConfirmName = () => {
    const finalName = isManualName ? manualNameInput.trim() : spokenName.trim();
    if (!finalName) return;
    setSpokenName(finalName);
    setStep(3);
    // Voice prompt asking for phone
    const promptText =
      selectedLang === 'te'
        ? 'మీ ఫోన్ నంబర్ చెప్పండి'
        : selectedLang === 'hi'
        ? 'अपना फ़ोन नंबर बताइए'
        : 'Please tell me your phone number';
    speakText(promptText, selectedLang);
  };

  const handleResetName = () => {
    setSpokenName('');
    setIsManualName(false);
    setManualNameInput('');
  };

  // --- Step 3: Phone handlers ---
  const handleVoicePhoneResult = (transcript) => {
    if (!transcript) return;
    const digits = parseSpokenDigits(transcript);
    if (digits) {
      setSpokenPhone(digits);
    } else {
      // In case simple speech captured standard numbers e.g. "9876543210"
      const rawNumbers = transcript.replace(/\D/g, '');
      setSpokenPhone(rawNumbers.slice(0, 10));
    }
  };

  const handleConfirmPhone = () => {
    const finalPhone = isManualPhone
      ? manualPhoneInput.replace(/\D/g, '').slice(0, 10)
      : spokenPhone.replace(/\D/g, '').slice(0, 10);

    const validPhone = finalPhone.length === 10 ? finalPhone : '9876543210';
    const finalName = spokenName || (selectedLang === 'te' ? 'రాము' : selectedLang === 'hi' ? 'रामू' : 'Ramu');

    // Complete onboarding & create farmer profile
    loginFarmer({
      name: finalName,
      phone: validPhone,
      language: selectedLang,
    });

    if (onFinish) onFinish();
  };

  const handleResetPhone = () => {
    setSpokenPhone('');
    setIsManualPhone(false);
    setManualPhoneInput('');
  };

  // --- Quick "Continue with this phone" handler ---
  const handleQuickDeviceLogin = () => {
    loginWithDevice(selectedLang);
    if (onFinish) onFinish();
  };

  return (
    <div className="min-h-screen bg-earth-bg flex flex-col justify-between p-4 sm:p-6 max-w-lg mx-auto select-none">
      {/* Top Brand Header */}
      <div className="pt-4 text-center">
        <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-forest mx-auto flex items-center justify-center text-white shadow-xl shadow-forest/25 mb-2.5">
          <span className="text-2xl sm:text-3xl" role="img" aria-label="Sprout">
            🌱
          </span>
        </div>

        <div className="inline-flex items-center gap-1 px-3 py-0.5 rounded-full bg-forest-50 text-forest text-xs font-bold border border-forest/20 mb-1">
          <Sparkles className="w-3 h-3 text-harvest" /> {t('identity.title')}
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mt-2">
          <span className={`h-1.5 rounded-full transition-all ${step === 1 ? 'w-8 bg-forest' : 'w-2 bg-earth-border'}`} />
          <span className={`h-1.5 rounded-full transition-all ${step === 2 ? 'w-8 bg-forest' : 'w-2 bg-earth-border'}`} />
          <span className={`h-1.5 rounded-full transition-all ${step === 3 ? 'w-8 bg-forest' : 'w-2 bg-earth-border'}`} />
        </div>
      </div>

      {/* ================= STEP 1: LANGUAGE SELECTION ================= */}
      {step === 1 && (
        <div className="my-6 space-y-4 animate-fadeIn">
          <div className="text-center">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-earth-text tracking-tight">
              {t('onboarding.chooseLanguage')}
            </h2>
            <p className="text-xs sm:text-sm text-earth-muted mt-1">
              {t('onboarding.selectPrompt')}
            </p>
          </div>

          <div className="space-y-3 pt-2">
            {SUPPORTED_LANGUAGES.map((language) => {
              const isSelected = selectedLang === language.code;

              return (
                <div
                  key={language.code}
                  onClick={() => handleSelectLanguage(language.code)}
                  className={`
                    p-4 rounded-2xl border-2 cursor-pointer transition-all duration-200 flex items-center justify-between
                    ${
                      isSelected
                        ? 'border-forest bg-white shadow-farmer-lg ring-2 ring-forest/20'
                        : 'border-earth-border/80 bg-white/70 hover:bg-white hover:border-forest/40'
                    }
                  `}
                  role="button"
                  tabIndex={0}
                  aria-pressed={isSelected}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleSelectLanguage(language.code);
                    }
                  }}
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-11 h-11 rounded-xl bg-earth-subtle flex items-center justify-center text-2xl flex-shrink-0">
                      {language.flag}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-bold text-earth-text">
                          {language.nativeName}
                        </h3>
                        <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-earth-subtle text-earth-muted">
                          {language.englishName}
                        </span>
                      </div>
                      <p className="text-xs text-forest font-medium mt-0.5">
                        "{language.sampleGreeting}"
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={(e) => handlePlayAudio(e, language)}
                      className="p-2 rounded-xl text-forest hover:bg-forest-50 active:scale-90 transition-all"
                      title="Listen sample"
                      aria-label={`Listen greeting in ${language.englishName}`}
                    >
                      <Volume2 className="w-5 h-5" />
                    </button>
                    <div
                      className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                        isSelected ? 'border-forest bg-forest text-white' : 'border-earth-border'
                      }`}
                    >
                      {isSelected && <Check className="w-3.5 h-3.5 stroke-[3px]" />}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <button
            type="button"
            onClick={handleLanguageNext}
            className="w-full py-4 px-6 rounded-2xl bg-forest hover:bg-forest-600 text-white font-bold text-base shadow-farmer-lg shadow-forest/25 flex items-center justify-center gap-2 active:scale-98 transition-all touch-target-lg mt-4"
          >
            <span>{t('onboarding.continueBtn')}</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* ================= STEP 2: ASK NAME BY VOICE ================= */}
      {step === 2 && (
        <div className="my-6 space-y-4 animate-fadeIn text-center">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-forest bg-forest-50 px-3 py-1 rounded-full mb-2">
              <User className="w-3.5 h-3.5" /> 1 / 2 {t('identity.title')}
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-earth-text tracking-tight">
              {t('identity.askName')}
            </h2>
            <p className="text-xs sm:text-sm text-earth-muted mt-1 font-medium">
              {t('identity.nameHelper')}
            </p>
          </div>

          {/* Voice Microphone Centerpiece */}
          {!spokenName && !isManualName && (
            <div className="py-2">
              <VoiceButton
                size="large"
                onSpeechResult={handleVoiceNameResult}
              />
            </div>
          )}

          {/* Recognized Name Display & Confirmation */}
          {spokenName && !isManualName && (
            <div className="p-5 rounded-3xl bg-white border-2 border-forest shadow-farmer-lg space-y-4 animate-fadeIn">
              <span className="text-xs font-bold text-forest uppercase tracking-wider">
                {t('identity.nameRecognized')}
              </span>
              <div className="text-3xl font-black text-earth-text tracking-tight">
                "{spokenName}"
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleResetName}
                  className="py-3 px-3 rounded-xl border border-earth-border hover:bg-earth-subtle text-earth-muted font-bold text-sm flex items-center justify-center gap-1.5 active:scale-95"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>{t('identity.sayAgain')}</span>
                </button>

                <button
                  type="button"
                  onClick={handleConfirmName}
                  className="py-3 px-4 rounded-xl bg-forest hover:bg-forest-600 text-white font-bold text-sm flex items-center justify-center gap-1.5 shadow-md shadow-forest/20 active:scale-95"
                >
                  <Check className="w-4 h-4 stroke-[3px]" />
                  <span>{t('identity.yesConfirm')}</span>
                </button>
              </div>
            </div>
          )}

          {/* Manual Type fallback if needed */}
          {isManualName && (
            <div className="p-5 rounded-3xl bg-white border border-earth-border shadow-farmer space-y-3">
              <input
                type="text"
                autoFocus
                value={manualNameInput}
                onChange={(e) => setManualNameInput(e.target.value)}
                placeholder={t('identity.enterNameManual')}
                className="w-full py-3.5 px-4 rounded-2xl bg-earth-subtle border border-earth-border text-center text-lg font-bold text-earth-text focus:outline-none focus:border-forest"
              />
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setIsManualName(false)}
                  className="py-3 rounded-xl border border-earth-border text-xs font-bold"
                >
                  {t('common.back')}
                </button>
                <button
                  type="button"
                  disabled={!manualNameInput.trim()}
                  onClick={handleConfirmName}
                  className="py-3 rounded-xl bg-forest text-white text-xs font-bold disabled:opacity-50"
                >
                  {t('common.confirm')}
                </button>
              </div>
            </div>
          )}

          {/* Small secondary button to switch to manual typing */}
          {!spokenName && !isManualName && (
            <button
              type="button"
              onClick={() => setIsManualName(true)}
              className="inline-flex items-center gap-1.5 text-xs text-earth-muted hover:text-forest font-semibold underline pt-2"
            >
              <Keyboard className="w-3.5 h-3.5" />
              <span>{t('identity.typeManually')}</span>
            </button>
          )}
        </div>
      )}

      {/* ================= STEP 3: ASK PHONE NUMBER BY VOICE ================= */}
      {step === 3 && (
        <div className="my-6 space-y-4 animate-fadeIn text-center">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-bold text-forest bg-forest-50 px-3 py-1 rounded-full mb-2">
              <Phone className="w-3.5 h-3.5" /> 2 / 2 {t('identity.title')}
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-earth-text tracking-tight">
              {t('identity.askPhone')}
            </h2>
            <p className="text-xs sm:text-sm text-earth-muted mt-1 font-medium">
              {t('identity.phoneHelper')}
            </p>
          </div>

          {/* Voice Microphone Centerpiece */}
          {!spokenPhone && !isManualPhone && (
            <div className="py-2">
              <VoiceButton
                size="large"
                onSpeechResult={handleVoicePhoneResult}
              />
            </div>
          )}

          {/* Large Formatted Number Display & Confirmation */}
          {spokenPhone && !isManualPhone && (
            <div className="p-5 rounded-3xl bg-white border-2 border-forest shadow-farmer-lg space-y-4 animate-fadeIn">
              <span className="text-xs font-bold text-forest uppercase tracking-wider">
                {t('identity.phoneConfirm')}
              </span>
              <div className="text-4xl font-black text-earth-text tracking-widest font-mono">
                {formatPhoneNumber(spokenPhone)}
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleResetPhone}
                  className="py-3 px-3 rounded-xl border border-earth-border hover:bg-earth-subtle text-earth-muted font-bold text-sm flex items-center justify-center gap-1.5 active:scale-95"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>{t('identity.sayAgain')}</span>
                </button>

                <button
                  type="button"
                  onClick={handleConfirmPhone}
                  className="py-3 px-4 rounded-xl bg-forest hover:bg-forest-600 text-white font-bold text-sm flex items-center justify-center gap-1.5 shadow-md shadow-forest/20 active:scale-95"
                >
                  <Check className="w-4 h-4 stroke-[3px]" />
                  <span>{t('identity.yesConfirm')}</span>
                </button>
              </div>
            </div>
          )}

          {/* Manual Phone Fallback */}
          {isManualPhone && (
            <div className="p-5 rounded-3xl bg-white border border-earth-border shadow-farmer space-y-3">
              <input
                type="tel"
                maxLength={10}
                autoFocus
                value={manualPhoneInput}
                onChange={(e) => setManualPhoneInput(e.target.value.replace(/\D/g, ''))}
                placeholder={t('identity.enterPhoneManual')}
                className="w-full py-3.5 px-4 rounded-2xl bg-earth-subtle border border-earth-border text-center text-2xl font-black font-mono tracking-wider text-earth-text focus:outline-none focus:border-forest"
              />
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setIsManualPhone(false)}
                  className="py-3 rounded-xl border border-earth-border text-xs font-bold"
                >
                  {t('common.back')}
                </button>
                <button
                  type="button"
                  disabled={manualPhoneInput.length < 10}
                  onClick={handleConfirmPhone}
                  className="py-3 rounded-xl bg-forest text-white text-xs font-bold disabled:opacity-50"
                >
                  {t('common.confirm')}
                </button>
              </div>
            </div>
          )}

          {/* Small secondary button to switch to manual typing */}
          {!spokenPhone && !isManualPhone && (
            <button
              type="button"
              onClick={() => setIsManualPhone(true)}
              className="inline-flex items-center gap-1.5 text-xs text-earth-muted hover:text-forest font-semibold underline pt-2"
            >
              <Keyboard className="w-3.5 h-3.5" />
              <span>{t('identity.typeManually')}</span>
            </button>
          )}
        </div>
      )}

      {/* ================= BOTTOM BAR: CONTINUE WITH THIS PHONE ================= */}
      <div className="pb-4 pt-2 text-center space-y-2">
        <button
          type="button"
          onClick={handleQuickDeviceLogin}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-forest bg-forest-50 hover:bg-forest-100 active:scale-95 transition-all"
        >
          <Smartphone className="w-3.5 h-3.5" />
          <span>{t('identity.continueWithPhone')}</span>
        </button>

        <p className="text-[11px] text-earth-muted">
          {t('appName')} • “{t('tagline')}”
        </p>
      </div>
    </div>
  );
}
