import React, { createContext, useContext, useState, useEffect } from 'react';
import en from './en';
import te from './te';
import hi from './hi';

const translations = {
  en,
  te,
  hi,
};

export const SUPPORTED_LANGUAGES = [
  {
    code: 'te',
    nativeName: 'తెలుగు',
    englishName: 'Telugu',
    flag: '🌾',
    badge: 'మాట్లాడండి',
    sampleGreeting: 'మీకు ఎలా సహాయం చేయాలి?',
  },
  {
    code: 'hi',
    nativeName: 'हिन्दी',
    englishName: 'Hindi',
    flag: '🌻',
    badge: 'बोलिए',
    sampleGreeting: 'मैं आपकी क्या सहायता करूँ?',
  },
  {
    code: 'en',
    nativeName: 'English',
    englishName: 'English',
    flag: '🌱',
    badge: 'Speak',
    sampleGreeting: 'How can I help you today?',
  },
];

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  // Default to Telugu as per farmer-first spec, or retrieve persisted selection
  const [lang, setLangState] = useState(() => {
    try {
      const saved = localStorage.getItem('kisansaarthi_lang');
      return saved && translations[saved] ? saved : 'te';
    } catch {
      return 'te';
    }
  });

  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(() => {
    try {
      return localStorage.getItem('kisansaarthi_onboarded') === 'true';
    } catch {
      return false;
    }
  });

  const setLang = (newLang) => {
    if (translations[newLang]) {
      setLangState(newLang);
      try {
        localStorage.setItem('kisansaarthi_lang', newLang);
        document.documentElement.lang = newLang;
      } catch (e) {
        console.warn('Storage error:', e);
      }
    }
  };

  const completeOnboarding = (chosenLang) => {
    if (chosenLang) setLang(chosenLang);
    setHasCompletedOnboarding(true);
    try {
      localStorage.setItem('kisansaarthi_onboarded', 'true');
    } catch (e) {
      console.warn('Storage error:', e);
    }
  };

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  // Safe nested translation lookup: t('home.voiceCard.title')
  const t = (path) => {
    const keys = path.split('.');
    let current = translations[lang];

    for (const key of keys) {
      if (current && current[key] !== undefined) {
        current = current[key];
      } else {
        // Fallback to English
        let fallback = translations.en;
        for (const fKey of keys) {
          if (fallback && fallback[fKey] !== undefined) {
            fallback = fallback[fKey];
          } else {
            return path; // Return key path if not found
          }
        }
        return fallback;
      }
    }
    return current;
  };

  return (
    <LanguageContext.Provider
      value={{
        lang,
        setLang,
        t,
        languages: SUPPORTED_LANGUAGES,
        currentLanguageInfo: SUPPORTED_LANGUAGES.find((l) => l.code === lang) || SUPPORTED_LANGUAGES[0],
        hasCompletedOnboarding,
        completeOnboarding,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useTranslation() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
}
