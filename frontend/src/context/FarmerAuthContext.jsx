import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  getCurrentFarmer,
  saveFarmerProfile,
  clearCurrentFarmer,
  createDefaultDeviceFarmer,
} from '../services/farmerAuth';
import { useTranslation } from '../i18n';

const FarmerAuthContext = createContext();

export function FarmerAuthProvider({ children }) {
  const { lang, setLang } = useTranslation();
  const [currentFarmer, setCurrentFarmer] = useState(() => getCurrentFarmer());
  const [isLoading, setIsLoading] = useState(false);

  const isAuthenticated = Boolean(currentFarmer && currentFarmer.name);

  // Sync translation language with farmer's preferred language on mount / change
  useEffect(() => {
    if (currentFarmer && currentFarmer.language && currentFarmer.language !== lang) {
      setLang(currentFarmer.language);
    }
  }, [currentFarmer]);

  /**
   * Log in or register a new farmer with voice credentials
   */
  const loginFarmer = (profileData) => {
    const saved = saveFarmerProfile({
      ...profileData,
      language: profileData.language || lang,
    });
    setCurrentFarmer(saved);
    if (saved.language) {
      setLang(saved.language);
    }
    return saved;
  };

  /**
   * Log out or change farmer on this device
   */
  const logoutFarmer = () => {
    clearCurrentFarmer();
    setCurrentFarmer(null);
  };

  /**
   * Quick "Continue with this phone" identity flow
   */
  const loginWithDevice = (preferredLang) => {
    const profile = createDefaultDeviceFarmer(preferredLang || lang);
    setCurrentFarmer(profile);
    return profile;
  };

  /**
   * Update farmer's profile language
   */
  const updateFarmerLanguage = (newLang) => {
    setLang(newLang);
    if (currentFarmer) {
      const updated = saveFarmerProfile({
        ...currentFarmer,
        language: newLang,
      });
      setCurrentFarmer(updated);
    }
  };

  return (
    <FarmerAuthContext.Provider
      value={{
        currentFarmer,
        isAuthenticated,
        isLoading,
        loginFarmer,
        logoutFarmer,
        loginWithDevice,
        updateFarmerLanguage,
      }}
    >
      {children}
    </FarmerAuthContext.Provider>
  );
}

export function useFarmerAuth() {
  const context = useContext(FarmerAuthContext);
  if (!context) {
    throw new Error('useFarmerAuth must be used within a FarmerAuthProvider');
  }
  return context;
}
