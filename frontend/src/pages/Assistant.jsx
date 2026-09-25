import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowLeft,
  Send,
  Volume2,
  VolumeX,
  Sparkles,
  Camera,
  Image as ImageIcon,
  User,
  Bot,
  Loader2,
  AlertCircle,
  HelpCircle,
  Languages,
} from 'lucide-react';
import { useTranslation } from '../i18n';
import VoiceButton from '../components/voice/VoiceButton';
import ImageUploadButton from '../components/image/ImageUploadButton';
import { sendChatMessage, detectInputLanguage, analyzeCropImage } from '../services/api';
import { speakText, stopSpeaking } from '../services/voiceService';
import { useFarmerAuth } from '../context/FarmerAuthContext';

export default function Assistant({ onBack, initialQuery = '', initialImage = null, isOnline = true, onOpenLanguageModal }) {
  const { t, lang, currentLanguageInfo } = useTranslation();
  const { currentFarmer } = useFarmerAuth();
  // Persistent conversation ID across the entire multi-turn booking and chat workflow
  const [conversationId] = useState(() => 'conv_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7));
  const [messages, setMessages] = useState([
    {
      id: 'welcome-msg',
      sender: 'agent',
      text:
        lang === 'te'
          ? `నమస్కారం ${currentFarmer?.name || 'రైతు'} గారూ! నేను కిసాన్ సారథి AI. మీ పంట సమస్య, ట్రాక్టర్ బుకింగ్, పంట వ్యర్థాల నిర్వహణ లేదా భీమా గురించి మాట్లాడండి లేదా ఫోటో పంపండి.`
          : lang === 'hi'
          ? `नमस्ते ${currentFarmer?.name || 'किसान'} जी! मैं किसान सारथी AI हूँ। अपनी फसल समस्या, ट्रैक्टर बुकिंग, फसल अवशेष प्रबंधन या बीमा के बारे में बोलकर बताएं या फ़ोटो भेजें।`
          : `Namaste ${currentFarmer?.name || 'Farmer Friend'}! I am KisanSaarthi AI. Speak or send a photo about your crop issues, tractor booking, crop residue, or insurance.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [inputVal, setInputVal] = useState(initialQuery || '');
  const [isAgentResponding, setIsAgentResponding] = useState(false);
  const [agentStatusText, setAgentStatusText] = useState('');
  const [speakingMsgId, setSpeakingMsgId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isAgentResponding]);

  // Handle initial image if passed from Home camera button
  useEffect(() => {
    if (initialImage) {
      handleSendImageMessage(initialImage);
    }
  }, [initialImage]);

  // Handle initial query if passed from Home or Requests quick actions
  const initialSentRef = useRef(false);
  useEffect(() => {
    if (initialQuery && !initialSentRef.current) {
      initialSentRef.current = true;
      handleSendMessage(initialQuery);
    }
  }, [initialQuery]);

  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputVal).trim();
    if (!text) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputVal('');
    setIsAgentResponding(true);

    // Agentic status updates
    if (text.toLowerCase().includes('tractor') || text.includes('ట్రాక్టర్') || text.includes('ट्रैक्टर')) {
      setAgentStatusText(
        lang === 'te'
          ? 'సమీప ట్రాక్టర్ల లభ్యతను కిసాన్ సారథి తనిఖీ చేస్తోంది...'
          : lang === 'hi'
          ? 'किसान सारथी ट्रैक्टर उपलब्धता जांच रहा है...'
          : 'KisanSaarthi is checking tractor availability...'
      );
    } else if (text.toLowerCase().includes('leaf') || text.includes('ఆకు') || text.includes('पत्ता')) {
      setAgentStatusText(
        lang === 'te'
          ? 'పంట తెగులు సమాచారాన్ని కిసాన్ సారథి విశ్లేషిస్తోంది...'
          : lang === 'hi'
          ? 'फसल रोग के लक्षणों का विश्लेषण हो रहा है...'
          : 'KisanSaarthi is analyzing crop health symptoms...'
      );
    } else {
      setAgentStatusText(t('assistant.agentThinking'));
    }

    try {
      const inputLang = detectInputLanguage(text, lang);
      const response = await sendChatMessage(text, inputLang, currentFarmer?.id || 'F001', conversationId);
      
      let rawText = response.response || response.text || '';
      // Dual Defense Interceptor: if backend returned unverified fallback in English while UI is te or hi
      if (
        lang !== 'en' &&
        (rawText.includes("verified information to answer") ||
         rawText.includes("applicable insurer or official scheme guidance"))
      ) {
        rawText = t('assistant.unverifiedFallback');
      }

      const agentMsg = {
        id: response.id || `agent-${Date.now()}`,
        sender: 'agent',
        text: rawText,
        timestamp: response.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        agent: response.agent,
        intent: response.intent,
        status: response.status,
        options: response.options,
        confirmation_details: response.confirmation_details,
        booking: response.booking,
      };

      setMessages((prev) => [...prev, agentMsg]);
      setIsAgentResponding(false);
      setAgentStatusText('');
    } catch (err) {
      console.error('[KisanSaarthi Chat Error]', err);
      setIsAgentResponding(false);
      setAgentStatusText('');
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'agent',
          isError: true,
          text:
            lang === 'te'
              ? 'క్షమించండి, సర్వర్‌ను సంప్రదించడంలో సమస్య వచ్చింది. దయచేసి మళ్ళీ ప్రయత్నించండి.'
              : lang === 'hi'
              ? 'क्षमा करें, सर्वर से संपर्क नहीं हो पाया। कृपया पुनः प्रयास करें।'
              : 'Sorry, unable to connect to KisanSaarthi server. Please make sure the backend is running and try again.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    }
  };

  const handleSendImageMessage = async (file) => {
    if (!file) return;

    const imgUrl = URL.createObjectURL(file);
    const userImgMsg = {
      id: `img-${Date.now()}`,
      sender: 'user',
      image: imgUrl,
      fileName: file.name,
      text:
        lang === 'te'
          ? 'ఈ ఫోటోను పరిశీలించండి.'
          : lang === 'hi'
          ? 'कृपया इस फ़ोटो की जांच करें।'
          : 'Please analyze this photo.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userImgMsg]);
    setIsAgentResponding(true);
    setAgentStatusText(
      lang === 'te'
        ? 'మీ ఫోటోను కిసాన్ సారథి పరిశీలిస్తోంది...'
        : lang === 'hi'
        ? 'किसान सारथी आपकी तस्वीर का विश्लेषण कर रहा है...'
        : 'KisanSaarthi is analyzing your crop photo...'
    );

    try {
      const result = await analyzeCropImage(file, {
        language: lang,
        farmerId: currentFarmer?.id || 'F001',
      });

      setIsAgentResponding(false);
      setAgentStatusText('');

      const responseMsg = {
        id: result.request_id || `agent-img-${Date.now()}`,
        sender: 'agent',
        text: result.response || '',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        agent: result.agent || 'Crop Health Agent',
        crop_result: result,
      };

      setMessages((prev) => [...prev, responseMsg]);
    } catch (err) {
      console.error('[KisanSaarthi Crop Health Error]', err);
      setIsAgentResponding(false);
      setAgentStatusText('');
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'agent',
          isError: true,
          text:
            lang === 'te'
              ? 'క్షమించండి, పంట ఫోటోను విశ్లేషించడంలో సమస్య వచ్చింది. దయచేసి మళ్ళీ ప్రయత్నించండి.'
              : lang === 'hi'
              ? 'क्षमा करें, फसल की फ़ोटो का विश्लेषण करने में समस्या आई। कृपया पुनः प्रयास करें।'
              : 'Sorry, unable to analyze the crop photo right now. Please make sure the backend is running and try again.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    }
  };

  const handleToggleListen = (msgId, text) => {
    if (speakingMsgId === msgId) {
      stopSpeaking();
      setSpeakingMsgId(null);
    } else {
      setSpeakingMsgId(msgId);
      speakText(text, lang, () => {
        setSpeakingMsgId(null);
      });
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-lg mx-auto bg-earth-bg select-none">
      {/* Top Header */}
      <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-earth-border px-4 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onBack}
            className="p-2 -ml-1 rounded-full hover:bg-earth-subtle text-earth-text active:scale-95 transition-all"
            aria-label={t('common.back')}
          >
            <ArrowLeft className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-forest text-white flex items-center justify-center text-lg shadow-sm">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h2 className="font-bold text-earth-text text-base leading-tight">
                  {t('assistant.title')}
                </h2>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              </div>
              <p className="text-[11px] text-earth-muted font-medium">
                {t('assistant.subtitle')} • {currentLanguageInfo.nativeName}
              </p>
            </div>
          </div>
        </div>

        {/* Action Controls: Language & Connectivity */}
        <div className="flex items-center gap-2">
          {onOpenLanguageModal && (
            <button
              type="button"
              onClick={onOpenLanguageModal}
              className="flex items-center gap-1 px-2 py-1 rounded-xl bg-forest-50 hover:bg-forest-100 text-forest-dark border border-forest/20 font-medium text-xs active:scale-95 transition-all"
              aria-label={t('status.changeLanguage')}
            >
              <Languages className="w-3.5 h-3.5 text-forest" />
              <span className="font-semibold">{currentLanguageInfo.nativeName}</span>
            </button>
          )}

          {/* Connectivity pill */}
          <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold border ${isOnline ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-amber-50 text-amber-800 border-amber-300'}`}>
            {isOnline ? t('status.online') : t('status.offline')}
          </span>
        </div>
      </header>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          const isSpeaking = speakingMsgId === msg.id;

          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} animate-fadeIn`}
            >
              <div className="flex items-end gap-2 max-w-[85%]">
                {!isUser && (
                  <div className="w-7 h-7 rounded-lg bg-forest-50 text-forest flex items-center justify-center flex-shrink-0 mb-1">
                    <Sparkles className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`
                    p-3.5 sm:p-4 rounded-2xl shadow-sm text-sm sm:text-base leading-relaxed break-words
                    ${
                      isUser
                        ? 'bg-forest text-white rounded-br-none'
                        : msg.isError
                        ? 'bg-danger-light text-danger border border-danger/20 rounded-bl-none'
                        : 'bg-white text-earth-text border border-earth-border/70 rounded-bl-none'
                    }
                  `}
                >
                  {/* Attached Image preview if present */}
                  {msg.image && (
                    <div className="mb-2 rounded-xl overflow-hidden border border-white/30 max-h-48">
                      <img src={msg.image} alt="Uploaded" className="w-full h-full object-cover" />
                    </div>
                  )}

                  <p className="whitespace-pre-wrap">{msg.text}</p>

                  {/* Structured Crop Health Card if crop_result is present */}
                  {!isUser && msg.crop_result && (
                    <div className="mt-3.5 space-y-2.5 border-t border-earth-border/60 pt-3 text-xs">
                      {/* Status & Confidence badges */}
                      <div className="flex flex-wrap items-center justify-between gap-1.5 pb-1">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {msg.crop_result.crop && (
                            <span className="text-xs font-bold text-forest bg-forest-50 px-2.5 py-0.5 rounded-full border border-forest/20">
                              🌱 {msg.crop_result.crop}
                            </span>
                          )}
                          {msg.crop_result.confidence != null && (
                            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300">
                              📊 {Math.round(msg.crop_result.confidence * 100)}%
                            </span>
                          )}
                        </div>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                          msg.crop_result.status === 'completed'
                            ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                            : msg.crop_result.status === 'needs_better_image'
                            ? 'bg-amber-100 text-amber-900 border-amber-300'
                            : msg.crop_result.status === 'unsupported'
                            ? 'bg-rose-100 text-rose-800 border-rose-300'
                            : 'bg-amber-50 text-amber-800 border-amber-200'
                        }`}>
                          {msg.crop_result.status === 'completed' ? t('assistant.verifiedBadge') : msg.crop_result.status}
                        </span>
                      </div>

                      {/* Special guidance for non-completed statuses */}
                      {msg.crop_result.status === 'needs_better_image' && (
                        <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 font-medium">
                          📸 {lang === 'te'
                            ? 'దయచేసి మంచి వెలుతురులో ఆకులపై దగ్గరగా స్పష్టమైన ఫోటో తీయండి.'
                            : lang === 'hi'
                            ? 'कृपया पत्तियों की नज़दीक से साफ़ फ़ोटो अपलोड करें।'
                            : 'Please take a clearer photo of the affected leaf.'}
                        </div>
                      )}

                      {msg.crop_result.status === 'uncertain' && (
                        <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 font-medium">
                          ⚠️ {lang === 'te'
                            ? 'చిత్రం స్పష్టంగా గుర్తించబడలేదు. దయచేసి స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.'
                            : lang === 'hi'
                            ? 'फ़ोटो से समस्या की स्पष्ट पहचान नहीं हो सकी। कृपया कृषि विशेषज्ञ से सलाह लें।'
                            : 'The image could not be confidently identified. Please consult an agricultural expert.'}
                        </div>
                      )}

                      {msg.crop_result.status === 'unsupported' && (
                        <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 font-medium">
                          ℹ️ {lang === 'te'
                            ? 'ఈ పంట లేదా చిత్రం ప్రస్తుత మోడల్‌లో మద్దతు లేదు.'
                            : lang === 'hi'
                            ? 'यह फसल या चित्र वर्तमान मॉडल में समर्थित नहीं है।'
                            : 'The crop or image is currently unsupported.'}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Interactive Equipment Options Cards */}
                  {!isUser && msg.options && msg.options.length > 0 && !msg.confirmation_details && !msg.booking && (
                    <div className="mt-3.5 space-y-2 border-t border-earth-border/60 pt-3">
                      <div className="text-[11px] font-bold text-forest uppercase tracking-wider flex items-center gap-1.5">
                        <span>🚜</span> {t('assistant.availableEquipment')}
                      </div>
                      <div className="grid grid-cols-1 gap-2">
                        {msg.options.map((opt) => (
                          <div
                            key={opt.option_number}
                            className="p-3 bg-earth-subtle/70 hover:bg-emerald-50/70 border border-earth-border rounded-xl transition-all flex flex-col justify-between"
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <div className="font-bold text-earth-text text-sm flex items-center gap-1.5">
                                  <span className="w-5 h-5 rounded-full bg-forest text-white text-[11px] flex items-center justify-center font-bold">
                                    {opt.option_number}
                                  </span>
                                  {opt.name}
                                </div>
                                <div className="text-xs text-earth-muted mt-0.5">
                                  {opt.specs || opt.type} • {lang === 'te' ? `${opt.location} ${t('assistant.near')}` : lang === 'hi' ? `${opt.location} ${t('assistant.near')}` : `${t('assistant.near')} ${opt.location}`}
                                </div>
                                <div className="text-xs text-forest font-semibold mt-1">
                                  ⏱ {opt.time_slot}
                                </div>
                              </div>
                              <div className="text-right flex flex-col items-end">
                                <span className="text-sm font-bold text-forest">₹{opt.price}/hr</span>
                                <span className="text-[10px] text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded font-semibold mt-0.5">
                                  {t('assistant.available')}
                                </span>
                              </div>
                            </div>
                            <button
                              type="button"
                              data-testid={`select-option-${opt.option_number}`}
                              onClick={() => handleSendMessage(lang === 'te' ? `ఎంపిక ${opt.option_number}` : lang === 'hi' ? `विकल्प ${opt.option_number}` : `Option ${opt.option_number}`)}
                              className="mt-2.5 w-full py-1.5 px-3 bg-forest hover:bg-forest-600 text-white rounded-lg text-xs font-semibold active:scale-95 transition-all flex items-center justify-center gap-1 shadow-sm"
                            >
                              <span>{t('assistant.select')}</span>
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Interactive Farmer Profile + Booking Confirmation Review Card */}
                  {!isUser && msg.confirmation_details && !msg.booking && (
                    <div className="mt-3.5 p-3.5 bg-amber-50/90 border border-amber-200/80 rounded-xl text-earth-text space-y-3">
                      <div className="flex items-center gap-1.5 border-b border-amber-200 pb-2">
                        <span className="text-base">📋</span>
                        <h4 className="font-bold text-xs uppercase tracking-wider text-amber-950">
                          {t('assistant.confirmYourBooking')}
                        </h4>
                      </div>

                      {/* Farmer Details */}
                      <div className="bg-white/95 p-2.5 rounded-lg border border-amber-100 space-y-1 text-xs">
                        <div className="font-bold uppercase text-[10px] text-earth-muted tracking-wider">
                          {t('assistant.farmerDetails')}
                        </div>
                        <div className="flex justify-between">
                          <span className="text-earth-muted">{t('assistant.name')}</span>
                          <span className="font-semibold text-earth-text">{msg.confirmation_details.farmer_name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-earth-muted">{t('assistant.phone')}</span>
                          <span className="font-semibold text-earth-text">{msg.confirmation_details.farmer_phone}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-earth-muted">{t('assistant.village')}</span>
                          <span className="font-semibold text-earth-text">{msg.confirmation_details.village}</span>
                        </div>
                      </div>

                      {/* Booking Details */}
                      <div className="bg-white/95 p-2.5 rounded-lg border border-amber-100 space-y-1 text-xs">
                        <div className="font-bold uppercase text-[10px] text-earth-muted tracking-wider">
                          {t('assistant.bookingDetails')}
                        </div>
                        <div className="flex justify-between">
                          <span className="text-earth-muted">{t('assistant.equipment')}</span>
                          <span className="font-semibold text-earth-text">{msg.confirmation_details.equipment_name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-earth-muted">{t('assistant.date')}</span>
                          <span className="font-semibold text-earth-text">{msg.confirmation_details.date}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-earth-muted">{t('assistant.time')}</span>
                          <span className="font-semibold text-earth-text">{msg.confirmation_details.time}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-earth-muted">{t('assistant.location')}</span>
                          <span className="font-semibold text-earth-text">{msg.confirmation_details.location}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-earth-muted">{t('assistant.rate')}</span>
                          <span className="font-bold text-forest">{msg.confirmation_details.rate}</span>
                        </div>
                      </div>

                      <p className="text-xs font-semibold text-amber-900 text-center">
                        {t('assistant.isEverythingCorrect')}
                      </p>

                      <div className="flex items-center gap-2 pt-1">
                        <button
                          type="button"
                          data-testid="confirm-booking-btn"
                          onClick={() => handleSendMessage(t('assistant.confirmBooking'))}
                          className="flex-1 py-2 px-3 bg-forest hover:bg-forest-600 text-white rounded-lg text-xs font-bold active:scale-95 transition-all text-center shadow-sm"
                        >
                          {t('assistant.confirmBooking')}
                        </button>
                        <button
                          type="button"
                          data-testid="change-details-btn"
                          onClick={() => handleSendMessage(t('assistant.changeDetails'))}
                          className="py-2 px-3 bg-white border border-earth-border hover:bg-earth-subtle text-earth-text rounded-lg text-xs font-semibold active:scale-95 transition-all"
                        >
                          {t('assistant.changeDetails')}
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Confirmed Booking Card */}
                  {!isUser && msg.booking && (
                    <div className="mt-3.5 p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-earth-text space-y-2.5">
                      <div className="flex items-center justify-between border-b border-emerald-200 pb-2">
                        <div className="flex items-center gap-1.5">
                          <span className="text-base">🎉</span>
                          <h4 className="font-bold text-xs uppercase tracking-wider text-emerald-900">
                            {t('assistant.bookingConfirmed')}
                          </h4>
                        </div>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                          {t('assistant.confirmedBadge')}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="bg-white/90 p-2 rounded-lg border border-emerald-100">
                          <div className="text-[10px] text-earth-muted">{t('assistant.bookingId')}</div>
                          <div data-testid="booking-id-val" className="font-bold text-forest text-xs font-mono">{msg.booking.booking_id}</div>
                        </div>
                        <div className="bg-white/90 p-2 rounded-lg border border-emerald-100">
                          <div className="text-[10px] text-earth-muted">{t('assistant.equipmentLabel')}</div>
                          <div className="font-semibold text-earth-text text-xs">{msg.booking.equipment_name}</div>
                        </div>
                        <div className="bg-white/90 p-2 rounded-lg border border-emerald-100">
                          <div className="text-[10px] text-earth-muted">{t('assistant.farmer')}</div>
                          <div className="font-semibold text-earth-text text-xs">{msg.booking.farmer_name || t('home.farmerDefault')}</div>
                        </div>
                        <div className="bg-white/90 p-2 rounded-lg border border-emerald-100">
                          <div className="text-[10px] text-earth-muted">{t('assistant.location')}</div>
                          <div className="font-semibold text-earth-text text-xs">{msg.booking.location}</div>
                        </div>
                        <div className="bg-white/90 p-2 rounded-lg border border-emerald-100">
                          <div className="text-[10px] text-earth-muted">{t('assistant.dateTime')}</div>
                          <div className="font-semibold text-earth-text text-xs">{msg.booking.date} • {msg.booking.time}</div>
                        </div>
                        <div className="bg-white/90 p-2 rounded-lg border border-emerald-100">
                          <div className="text-[10px] text-earth-muted">{t('assistant.rateLabel')}</div>
                          <div className="font-bold text-forest text-xs">{msg.booking.rate || `₹${msg.booking.price}/hour`}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Audio read-aloud button for AI responses */}
                  {!isUser && !msg.isError && (
                    <div className="mt-2.5 pt-2 border-t border-earth-border/50 flex items-center justify-between gap-3 text-xs font-semibold text-forest">
                      <button
                        type="button"
                        onClick={() => handleToggleListen(msg.id, msg.text)}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-forest-50 hover:bg-forest-100 active:scale-95 transition-all"
                      >
                        {isSpeaking ? (
                          <>
                            <VolumeX className="w-3.5 h-3.5 text-danger" />
                            <span className="text-danger">{t('assistant.stopAudio')}</span>
                          </>
                        ) : (
                          <>
                            <Volume2 className="w-3.5 h-3.5" />
                            <span>{t('assistant.listenAudio')}</span>
                          </>
                        )}
                      </button>

                      <span className="text-[10px] text-earth-muted font-normal">
                        {msg.timestamp}
                      </span>
                    </div>
                  )}
                </div>

                {isUser && (
                  <div className="w-7 h-7 rounded-lg bg-earth-subtle text-earth-muted flex items-center justify-center flex-shrink-0 mb-1">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Agentic State Feedback Loading Indicator */}
        {isAgentResponding && (
          <div className="flex items-center gap-2 p-3 rounded-2xl bg-forest-50 border border-forest/20 text-forest-dark text-xs sm:text-sm animate-pulse max-w-[85%]">
            <Loader2 className="w-4 h-4 animate-spin text-forest" />
            <span className="font-semibold">{agentStatusText || t('assistant.agentThinking')}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Questions */}
      {messages.length <= 2 && (
        <div className="px-4 py-2 flex items-center gap-2 overflow-x-auto no-scrollbar">
          {t('assistant.suggestedQuestions').map((q, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(q)}
              className="text-xs bg-white border border-earth-border rounded-full px-3 py-1.5 text-earth-muted hover:text-earth-text hover:border-forest/40 flex-shrink-0 active:scale-95 transition-all text-left"
            >
              💬 {q}
            </button>
          ))}
        </div>
      )}

      {/* Chat Input Bar */}
      <div className="sticky bottom-0 bg-white border-t border-earth-border p-3 sm:p-4 safe-bottom shadow-lg">
        <form
          id="chat-form"
          data-testid="chat-form"
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2"
        >
          {/* 📷 In-chat Image Upload Button */}
          <ImageUploadButton
            variant="compact"
            onImageSelected={handleSendImageMessage}
          />

          {/* Text Input */}
          <div className="flex-1 relative">
            <input
              id="chat-input"
              data-testid="chat-input"
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder={t('assistant.placeholder')}
              className="w-full py-3 px-4 rounded-2xl bg-earth-subtle border border-earth-border focus:bg-white focus:border-forest text-sm text-earth-text placeholder-earth-muted focus:outline-none transition-all"
            />
          </div>

          {/* 🎤 In-chat Voice Input Button beside text input */}
          <VoiceButton
            size="compact"
            onSpeechResult={(spokenText) => {
              setInputVal(spokenText);
            }}
            onInterimResult={(interimText) => {
              setInputVal(interimText);
            }}
          />

          {/* Send button when input has text */}
          {inputVal.trim() ? (
            <button
              id="chat-send-btn"
              data-testid="chat-send-btn"
              type="submit"
              className="w-11 h-11 sm:w-12 sm:h-12 rounded-full bg-forest hover:bg-forest-600 text-white flex items-center justify-center shadow-md active:scale-95 transition-all flex-shrink-0"
              aria-label="Send message"
            >
              <Send className="w-5 h-5" />
            </button>
          ) : null}
        </form>
      </div>
    </div>
  );
}
