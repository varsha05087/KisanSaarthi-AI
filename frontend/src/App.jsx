import React, { useState, useEffect } from 'react';
import { LanguageProvider, useTranslation } from './i18n';
import { FarmerAuthProvider, useFarmerAuth } from './context/FarmerAuthContext';
import Header from './components/common/Header';
import BottomNav from './components/common/BottomNav';
import OfflineBanner from './components/common/OfflineBanner';
import LanguageSelectorModal from './components/common/LanguageSelectorModal';
import Onboarding from './pages/Onboarding';
import Home from './pages/Home';
import Requests from './pages/Requests';
import Profile from './pages/Profile';
import Assistant from './pages/Assistant';
import CropHealth from './pages/CropHealth';

function MainAppContent() {
  const { lang } = useTranslation();
  const { isAuthenticated } = useFarmerAuth();
  const [activeTab, setActiveTab] = useState('home');
  const [activeSubScreen, setActiveSubScreen] = useState(null); // 'assistant' | 'crop' | null
  const [initialAssistantQuery, setInitialAssistantQuery] = useState('');
  const [initialAssistantImage, setInitialAssistantImage] = useState(null);
  const [isLanguageModalOpen, setIsLanguageModalOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(() => (typeof navigator !== 'undefined' ? navigator.onLine : true));

  // Monitor network connectivity in real-time
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // If farmer is NOT authenticated, show Voice-First Farmer Identity onboarding
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-earth-bg">
        <Onboarding onFinish={() => setActiveTab('home')} />
      </div>
    );
  }

  // Full-screen Specialized Agent Sub-screens (AI Assistant / Crop Health)
  if (activeSubScreen === 'assistant') {
    return (
      <>
        <Assistant
          initialQuery={initialAssistantQuery}
          initialImage={initialAssistantImage}
          isOnline={isOnline}
          onOpenLanguageModal={() => setIsLanguageModalOpen(true)}
          onBack={() => {
            setActiveSubScreen(null);
            setInitialAssistantQuery('');
            setInitialAssistantImage(null);
          }}
        />
        <LanguageSelectorModal
          isOpen={isLanguageModalOpen}
          onClose={() => setIsLanguageModalOpen(false)}
        />
      </>
    );
  }

  if (activeSubScreen === 'crop') {
    return (
      <div className="min-h-screen bg-earth-bg flex flex-col justify-between">
        <div className="w-full max-w-lg mx-auto min-h-screen bg-earth-bg shadow-2xl relative flex flex-col border-x border-earth-border/40">
          <OfflineBanner isOnline={isOnline} />
          <Header
            isOnline={isOnline}
            onOpenLanguageModal={() => setIsLanguageModalOpen(true)}
          />
          <main className="flex-1 overflow-y-auto">
            <CropHealth
              onBack={() => setActiveSubScreen(null)}
              onOpenChatWithContext={(prompt) => {
                setInitialAssistantQuery(prompt);
                setActiveSubScreen('assistant');
              }}
            />
          </main>
          <BottomNav activeTab={activeTab} onTabChange={(tab) => { setActiveSubScreen(null); setActiveTab(tab); }} />
          <LanguageSelectorModal isOpen={isLanguageModalOpen} onClose={() => setIsLanguageModalOpen(false)} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-earth-bg flex flex-col justify-between">
      {/* Centered Desktop Frame with Mobile Proportions */}
      <div className="w-full max-w-lg mx-auto min-h-screen bg-earth-bg shadow-2xl relative flex flex-col border-x border-earth-border/40">
        {/* Offline Banner */}
        <OfflineBanner isOnline={isOnline} />

        {/* Global Farmer Header */}
        <Header
          isOnline={isOnline}
          onOpenLanguageModal={() => setIsLanguageModalOpen(true)}
        />

        {/* Dynamic Main Body Content */}
        <main className="flex-1 overflow-y-auto">
          {activeTab === 'home' && (
            <Home
              onOpenChat={() => {
                setInitialAssistantQuery('');
                setActiveSubScreen('assistant');
              }}
              onOpenAssistantWithVoice={(spokenText) => {
                setInitialAssistantQuery(spokenText);
                setActiveSubScreen('assistant');
              }}
              onOpenAssistantWithImage={(file) => {
                setInitialAssistantImage(file);
                setActiveSubScreen('assistant');
              }}
              onNavigateAction={(actionId) => {
                if (actionId === 'requests') {
                  setActiveTab('requests');
                } else if (actionId === 'crop') {
                  setActiveSubScreen('crop');
                } else if (actionId === 'chat') {
                  setInitialAssistantQuery('');
                  setActiveSubScreen('assistant');
                } else {
                  // For any other action, route into conversational AI assistant with context
                  setInitialAssistantQuery(
                    actionId === 'tractor'
                      ? (lang === 'te' ? 'నాకు ట్రాక్టర్ కావాలి' : lang === 'hi' ? 'मुझे ट्रैक्टर चाहिए' : 'I need a tractor')
                      : actionId === 'seeds'
                      ? (lang === 'te' ? 'నాకు ధృవీకరించిన విత్తనాలు కావాలి' : lang === 'hi' ? 'मुझे प्रमाणित बीज चाहिए' : 'I need certified seeds')
                      : actionId === 'insurance'
                      ? (lang === 'te' ? 'పంట నష్ట పరిహారం భీమా దరఖాస్తు' : lang === 'hi' ? 'फसल नुकसान बीमा दावा' : 'Crop damage insurance assistance')
                      : actionId === 'crop_residue' || actionId === 'residue'
                      ? (lang === 'te' ? 'పంట వ్యర్థాలు ఉన్నాయి ఏం చేయాలి?' : lang === 'hi' ? 'फसल अवशेष हैं क्या करें?' : 'I have farm waste. What can I do with it?')
                      : (lang === 'te' ? 'నాకు సహాయం కావాలి' : lang === 'hi' ? 'मुझे सहायता चाहिए' : 'I need help')
                  );
                  setActiveSubScreen('assistant');
                }
              }}
            />
          )}

          {activeTab === 'requests' && (
            <Requests
              onBackToHome={() => setActiveTab('home')}
              onOpenTractorBooking={() => {
                const query =
                  lang === 'te'
                    ? 'నాకు ట్రాక్టర్ కావాలి'
                    : lang === 'hi'
                    ? 'मुझे ट्रैक्टर चाहिए'
                    : 'I need a tractor';
                setInitialAssistantQuery(query);
                setActiveSubScreen('assistant');
              }}
              onOpenInsuranceAssistance={() => {
                const query =
                  lang === 'te'
                    ? 'పంట బీమా సహాయం కావాలి'
                    : lang === 'hi'
                    ? 'मुझे फसल बीमा सहायता चाहिए'
                    : 'How can I apply for crop insurance?';
                setInitialAssistantQuery(query);
                setActiveSubScreen('assistant');
              }}
            />
          )}

          {activeTab === 'profile' && (
            <Profile
              isOnline={isOnline}
              onOpenLanguageModal={() => setIsLanguageModalOpen(true)}
            />
          )}
        </main>

        {/* Bottom Navigation */}
        <BottomNav
          activeTab={activeTab}
          onTabChange={(tab) => {
            setActiveSubScreen(null);
            setActiveTab(tab);
          }}
        />

        {/* Language Selection Modal */}
        <LanguageSelectorModal
          isOpen={isLanguageModalOpen}
          onClose={() => setIsLanguageModalOpen(false)}
        />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <FarmerAuthProvider>
        <MainAppContent />
      </FarmerAuthProvider>
    </LanguageProvider>
  );
}
