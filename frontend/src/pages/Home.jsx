import React, { useState, useEffect } from 'react';
import {
  Sprout,
  Tractor,
  ShieldCheck,
  Recycle,
  Sparkles,
  ArrowRight,
  Clock,
  ChevronRight,
  AlertCircle,
  MessageSquare,
} from 'lucide-react';
import { useTranslation } from '../i18n';
import VoiceButton from '../components/voice/VoiceButton';
import ImageUploadButton from '../components/image/ImageUploadButton';
import Card from '../components/common/Card';
import { getRequests } from '../services/api';
import { useFarmerAuth } from '../context/FarmerAuthContext';

export default function Home({ onNavigateAction, onOpenAssistantWithVoice, onOpenAssistantWithImage, onOpenChat }) {
  const { t, lang } = useTranslation();
  const { currentFarmer } = useFarmerAuth();
  const [recentRequests, setRecentRequests] = useState([]);
  const [isLoadingRequests, setIsLoadingRequests] = useState(true);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        const reqs = await getRequests(currentFarmer?.id);
        if (isMounted) {
          setRecentRequests(reqs);
          setIsLoadingRequests(false);
        }
      } catch (err) {
        if (isMounted) setIsLoadingRequests(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [currentFarmer]);

  const handleVoiceResult = (spokenText) => {
    setNotification({
      type: 'voice',
      text: spokenText,
    });
    // Trigger callback to assistant if provided
    if (onOpenAssistantWithVoice) {
      onOpenAssistantWithVoice(spokenText);
    }
  };

  const handleImageUploaded = async (file) => {
    setNotification({
      type: 'image',
      text: lang === 'te' ? `ఎంచుకున్న ఫోటో: ${file.name}` : lang === 'hi' ? `फ़ोटो चयनित: ${file.name}` : `Photo selected: ${file.name}`,
    });
    if (onOpenAssistantWithImage) {
      onOpenAssistantWithImage(file);
    }
  };

  const quickActions = [
    {
      id: 'crop',
      title: t('home.actions.cropProblem.title'),
      desc: t('home.actions.cropProblem.desc'),
      icon: Sprout,
      color: 'bg-emerald-500',
      bgLight: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      tag: lang === 'te' ? 'AI పరిశీలన' : lang === 'hi' ? 'AI जांच' : 'AI Vision',
    },
    {
      id: 'tractor',
      title: t('home.actions.tractor.title'),
      desc: t('home.actions.tractor.desc'),
      icon: Tractor,
      color: 'bg-amber-600',
      bgLight: 'bg-amber-50 text-amber-900 border-amber-200',
      tag: lang === 'te' ? 'బుకింగ్' : lang === 'hi' ? 'बुकिंग' : 'Booking',
    },
    {
      id: 'crop_residue',
      title: t('home.actions.cropResidue.title') || 'Crop Residue',
      desc: t('home.actions.cropResidue.desc') || 'AgriCycle & residue utilization',
      icon: Recycle,
      color: 'bg-teal-600',
      bgLight: 'bg-teal-50 text-teal-800 border-teal-200',
      tag: lang === 'te' ? 'వ్యవసాయ వ్యర్థాలు' : lang === 'hi' ? 'फसल अवशेष' : 'AgriCycle',
    },
    {
      id: 'insurance',
      title: t('home.actions.insurance.title'),
      desc: t('home.actions.insurance.desc'),
      icon: ShieldCheck,
      color: 'bg-blue-600',
      bgLight: 'bg-blue-50 text-blue-900 border-blue-200',
      tag: 'PMFBY',
    },
  ];

  return (
    <div className="pb-28 pt-4 px-4 sm:px-6 space-y-6 max-w-2xl mx-auto">
      {/* Dynamic Voice/Action Alert Toast */}
      {notification && (
        <div className="p-3.5 rounded-2xl bg-forest text-white shadow-lg flex items-center justify-between gap-3 animate-fadeIn">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-5 h-5 text-harvest flex-shrink-0 animate-pulse" />
            <p className="text-xs sm:text-sm font-medium">
              <span className="font-bold">{lang === 'te' ? 'గుర్తించబడింది: ' : lang === 'hi' ? 'पहचाना गया: ' : 'Recognized: '}</span>"{notification.text}"
            </p>
          </div>
          <button
            type="button"
            onClick={() => setNotification(null)}
            className="text-xs font-bold underline px-2 py-1"
          >
            {t('common.close')}
          </button>
        </div>
      )}

      {/* 1. Welcoming Farmer Section */}
      <div className="space-y-1">
        <p className="text-sm sm:text-base font-semibold text-forest flex items-center gap-1.5">
          <span>🙏</span>
          {currentFarmer?.name
            ? lang === 'te'
              ? `నమస్కారం ${currentFarmer.name} 👋`
              : lang === 'hi'
              ? `नमस्ते ${currentFarmer.name} 👋`
              : `Hello ${currentFarmer.name} 👋`
            : t('home.greeting')}
        </p>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-earth-text tracking-tight">
          {t('home.howCanIHelp')}
        </h2>
      </div>

      {/* 2. Large Voice Interaction Card (Centerpiece) */}
      <section aria-label="Voice Assistant Interaction">
        <VoiceButton
          size="large"
          onSpeechResult={handleVoiceResult}
          onCardClick={() => {
            if (onOpenChat) {
              onOpenChat();
            } else if (onNavigateAction) {
              onNavigateAction('chat');
            }
          }}
        />
      </section>

      {/* 3. "Show Your Problem" Section (Large Camera / Image Upload) */}
      <section aria-label="Camera Image Upload">
        <ImageUploadButton
          variant="card"
          onImageSelected={handleImageUploaded}
        />
      </section>

      {/* 4. Quick Action Cards Grid (4 Core Capabilities) */}
      <section aria-label="Quick Agricultural Actions">
        <div className="flex items-center justify-between mb-3 px-1">
          <h3 className="text-lg font-bold text-earth-text tracking-tight">
            {t('home.quickActionsTitle')}
          </h3>
          <span className="text-xs text-forest font-bold bg-forest-50 px-2.5 py-0.5 rounded-full border border-forest/20">
            {lang === 'hi' ? '4 मुख्य सेवाएँ' : lang === 'te' ? '4 ముఖ్య సేవలు' : '4 Core Services'}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <div
                key={action.id}
                data-testid={`action-${action.id}`}
                onClick={() => onNavigateAction && onNavigateAction(action.id)}
                role="button"
                tabIndex={0}
                aria-label={action.title}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onNavigateAction && onNavigateAction(action.id);
                  }
                }}
                className="group p-4 sm:p-5 rounded-2xl bg-white border border-earth-border/80 shadow-farmer hover:shadow-farmer-lg hover:border-forest/40 transition-all duration-200 active:scale-95 cursor-pointer flex flex-col justify-between min-h-[140px] sm:min-h-[150px]"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className={`w-11 h-11 sm:w-12 sm:h-12 rounded-2xl ${action.color} text-white flex items-center justify-center shadow-md group-hover:scale-105 transition-transform`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md border ${action.bgLight}`}>
                    {action.tag}
                  </span>
                </div>

                <div className="mt-3">
                  <h4 className="font-bold text-earth-text text-sm sm:text-base leading-snug group-hover:text-forest transition-colors line-clamp-1">
                    {action.title}
                  </h4>
                  <p className="text-xs text-earth-muted mt-0.5 line-clamp-2 leading-tight">
                    {action.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 5. Agentic AI Positioning Banner */}
      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-forest to-emerald-800 text-white shadow-lg relative overflow-hidden">
        <div className="relative z-10 space-y-1.5">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-white/20 text-harvest-light backdrop-blur-sm">
            <Sparkles className="w-3.5 h-3.5 text-harvest" />
            {t('home.agentBanner.tag')}
          </div>
          <h4 className="text-base sm:text-lg font-bold leading-snug">
            {t('home.agentBanner.title')}
          </h4>
          <p className="text-xs sm:text-sm text-white/90 leading-relaxed max-w-lg">
            {t('home.agentBanner.desc')}
          </p>
        </div>
        <div className="absolute right-[-15px] bottom-[-20px] opacity-15 text-white pointer-events-none">
          <Tractor className="w-36 h-36" />
        </div>
      </div>

      {/* 6. Recent Requests Section */}
      <section aria-label="Recent Requests">
        <div className="flex items-center justify-between mb-3 px-1">
          <h3 className="text-lg font-bold text-earth-text tracking-tight flex items-center gap-2">
            <Clock className="w-4 h-4 text-forest" />
            {t('home.recentRequestsTitle')}
          </h3>
          <button
            type="button"
            onClick={() => onNavigateAction && onNavigateAction('requests')}
            className="text-xs font-bold text-forest hover:text-forest-dark flex items-center gap-0.5"
          >
            <span>{t('home.viewAll')}</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {recentRequests.length === 0 ? (
          <div className="p-6 rounded-2xl bg-white border border-dashed border-earth-border text-center text-earth-muted text-xs sm:text-sm">
            {t('home.noRecentRequests')}
          </div>
        ) : (
          <div className="space-y-2.5">
            {recentRequests.map((req) => (
              <div
                key={req.id}
                onClick={() => onNavigateAction && onNavigateAction('requests')}
                role="button"
                tabIndex={0}
                className="p-3.5 sm:p-4 rounded-2xl bg-white border border-earth-border/80 shadow-sm hover:shadow-farmer flex items-center justify-between gap-3 cursor-pointer transition-all active:scale-[0.99]"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest flex items-center justify-center flex-shrink-0">
                    {req.type === 'tractor' ? <Tractor className="w-5 h-5" /> : <Sprout className="w-5 h-5" />}
                  </div>
                  <div className="min-w-0">
                    <h5 className="font-bold text-earth-text text-sm truncate">
                      {req.title}
                    </h5>
                    <p className="text-xs text-earth-muted mt-0.5">
                      {req.date} • ID: {req.id}
                    </p>
                  </div>
                </div>

                <span className={`text-xs font-bold px-2.5 py-1 rounded-full border flex-shrink-0 ${req.statusColor}`}>
                  {req.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
