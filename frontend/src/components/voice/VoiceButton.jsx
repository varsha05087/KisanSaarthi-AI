import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Loader2, Volume2, AlertCircle } from 'lucide-react';
import { useTranslation } from '../../i18n';
import { createSpeechRecognizer, isSpeechRecognitionSupported } from '../../services/voiceService';

/**
 * Reusable VoiceButton with authentic state machine:
 * - idle
 * - listening
 * - processing
 * - success (speech converted)
 * - error
 */
export default function VoiceButton({
  onSpeechResult = () => {},
  onInterimResult,
  onListeningChange,
  size = 'large', // 'large' (Home card centerpiece) | 'compact' (Chat input)
  autoStart = false,
  className = '',
  onCardClick,
}) {
  const { t, lang } = useTranslation();
  const [voiceState, setVoiceState] = useState('idle'); // 'idle' | 'listening' | 'processing' | 'error'
  const [interimText, setInterimText] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const recognizerRef = useRef(null);

  const isLarge = size === 'large';
  const isSupported = isSpeechRecognitionSupported();

  const cleanupRecognizer = () => {
    if (recognizerRef.current) {
      try {
        recognizerRef.current.abort();
      } catch (e) {
        // Ignored
      }
      recognizerRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      cleanupRecognizer();
    };
  }, []);

  const handleStartListening = () => {
    if (voiceState === 'listening') {
      // Toggle off if currently listening
      cleanupRecognizer();
      setVoiceState('idle');
      if (onListeningChange) onListeningChange(false);
      return;
    }

    if (voiceState === 'error') {
      setVoiceState('idle');
    }

    if (!isSupported) {
      setVoiceState('error');
      setErrorMessage(
        lang === 'te'
          ? 'ఈ బ్రౌజర్‌లో వాయిస్ రికగ్నిషన్ సపోర్ట్ లేదు. దయచేసి Chrome ఉపయోగించండి.'
          : lang === 'hi'
          ? 'इस ब्राउज़र में वॉयस पहचान उपलब्ध नहीं है। कृपया Chrome इस्तेमाल करें।'
          : 'Voice recognition is not supported in this browser. Please use Chrome.'
      );
      return;
    }

    setErrorMessage('');
    setInterimText('');
    setVoiceState('listening');
    if (onListeningChange) onListeningChange(true);

    const recognizer = createSpeechRecognizer({
      language: lang,
      onStart: () => {
        setVoiceState('listening');
        if (onListeningChange) onListeningChange(true);
      },
      onResult: ({ final, interim }) => {
        if (interim) {
          setInterimText(interim);
          if (onInterimResult) {
            onInterimResult(interim);
          }
        }
        if (final) {
          setInterimText(final);
          if (onInterimResult) {
            onInterimResult(final);
          }
          if (isLarge) {
            setVoiceState('processing');
            setTimeout(() => {
              onSpeechResult(final);
              setVoiceState('idle');
              setInterimText('');
              if (onListeningChange) onListeningChange(false);
            }, 600);
          } else {
            // In compact / Assistant input: directly deliver speech result to input
            onSpeechResult(final);
            cleanupRecognizer();
            setVoiceState('idle');
            setInterimText('');
            if (onListeningChange) onListeningChange(false);
          }
        }
      },
      onError: (err) => {
        console.warn('Speech Error:', err);
        if (err === 'aborted' || err === 'no-speech') {
          setVoiceState('idle');
          if (onListeningChange) onListeningChange(false);
          return;
        }
        setVoiceState('error');
        if (onListeningChange) onListeningChange(false);
        if (err === 'not-allowed') {
          setErrorMessage(
            lang === 'te'
              ? 'మైక్రోఫోన్ అనుమతి నిరాకరించబడింది. దయచేసి సెట్టింగ్స్‌లో మైక్ ఆన్ చేయండి.'
              : lang === 'hi'
              ? 'माइक्रोफ़ोन की अनुमति नहीं मिली। कृपया सेटिंग्स में माइक चालू करें।'
              : 'Microphone access was denied. Please allow microphone permissions.'
          );
        } else {
          setErrorMessage(
            lang === 'te'
              ? 'వాయిస్ వినడంలో సమస్య వచ్చింది. మళ్ళీ నొక్కండి.'
              : lang === 'hi'
              ? 'आवाज़ सुनने में परेशानी हुई। पुनः प्रयास करें।'
              : 'Could not hear voice clearly. Please tap again.'
          );
        }
        setTimeout(() => {
          setVoiceState((cur) => (cur === 'error' ? 'idle' : cur));
        }, 3000);
      },
      onEnd: () => {
        setVoiceState((current) => (current === 'listening' ? 'idle' : current));
        if (onListeningChange) onListeningChange(false);
      },
    });

    if (recognizer) {
      recognizerRef.current = recognizer;
      try {
        recognizer.start();
      } catch (err) {
        console.error('Could not start recognition:', err);
        setVoiceState('error');
        if (onListeningChange) onListeningChange(false);
      }
    }
  };

  // Compact version for Chat input bar
  if (!isLarge) {
    const isListening = voiceState === 'listening';
    const label = isListening
      ? (lang === 'te' ? 'వినడం ఆపండి' : lang === 'hi' ? 'सुनना बंद करें' : 'Stop listening')
      : (lang === 'te' ? 'మాట్లాడటానికి నొక్కండి' : lang === 'hi' ? 'बोलने के लिए दबाएं' : 'Tap to speak');

    return (
      <div className="relative inline-flex items-center">
        <button
          type="button"
          id="chat-voice-btn"
          data-testid="chat-voice-btn"
          data-state={voiceState}
          onClick={handleStartListening}
          aria-label={label}
          title={label}
          className={`
            w-11 h-11 sm:w-12 sm:h-12 rounded-full flex items-center justify-center transition-all duration-200 flex-shrink-0
            ${
              isListening
                ? 'bg-danger text-white animate-record-pulse ring-4 ring-danger/30'
                : voiceState === 'processing'
                ? 'bg-amber-500 text-white'
                : voiceState === 'error'
                ? 'bg-amber-600 text-white'
                : 'bg-forest text-white hover:bg-forest-600 shadow-md shadow-forest/20 active:scale-95'
            }
            ${className}
          `}
        >
          {isListening ? (
            <span className="w-4 h-4 rounded-sm bg-white" />
          ) : voiceState === 'processing' ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Mic className="w-5 h-5" />
          )}
        </button>
      </div>
    );
  }

  // Large centerpiece version for Home Screen
  return (
    <div className={`w-full ${className}`}>
      <div
        id="talk-to-kisansaarthi"
        data-testid="talk-to-kisansaarthi"
        onClick={(e) => {
          if (onCardClick) {
            onCardClick();
          } else {
            handleStartListening();
          }
        }}
        role="button"
        tabIndex={0}
        aria-label={voiceState === 'listening' ? 'Stop listening' : t('home.voiceCard.tapToSpeak')}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            if (onCardClick) {
              onCardClick();
            } else {
              handleStartListening();
            }
          }
        }}
        className={`
          relative overflow-hidden w-full rounded-3xl p-6 sm:p-7 cursor-pointer transition-all duration-300
          border-2 text-center flex flex-col items-center justify-center select-none
          ${
            voiceState === 'listening'
              ? 'bg-rose-50 border-danger shadow-xl'
              : voiceState === 'processing'
              ? 'bg-amber-50 border-harvest shadow-lg'
              : 'bg-gradient-to-b from-forest-50/90 to-emerald-50/50 hover:to-forest-100/50 border-forest/30 hover:border-forest hover:shadow-farmer-lg active:scale-[0.99]'
          }
        `}
      >
        {/* Visual Pulse / Microphone Button */}
        <div className="relative my-2">
          {voiceState === 'listening' && (
            <div className="absolute -inset-4 rounded-full bg-danger/20 animate-ping" />
          )}

          <div
            className={`
              w-20 h-20 sm:w-24 sm:h-24 rounded-full flex items-center justify-center transition-all duration-300 shadow-lg
              ${
                voiceState === 'listening'
                  ? 'bg-danger text-white animate-record-pulse scale-110 shadow-danger/30'
                  : voiceState === 'processing'
                  ? 'bg-amber-500 text-white animate-pulse shadow-amber-500/30'
                  : 'bg-forest text-white hover:bg-forest-600 animate-wave-pulse shadow-forest/30'
              }
            `}
          >
            {voiceState === 'listening' ? (
              <span className="w-7 h-7 rounded bg-white shadow-sm" />
            ) : voiceState === 'processing' ? (
              <Loader2 className="w-9 h-9 sm:w-11 sm:h-11 animate-spin" />
            ) : (
              <Mic className="w-9 h-9 sm:w-11 sm:h-11 stroke-[2.2px]" />
            )}
          </div>
        </div>

        {/* Dynamic Status Text */}
        <div className="mt-3 space-y-1">
          <h3 className="text-xl sm:text-2xl font-bold text-earth-text tracking-tight">
            {voiceState === 'listening'
              ? t('home.voiceCard.listening')
              : voiceState === 'processing'
              ? t('home.voiceCard.processing')
              : t('home.voiceCard.title')}
          </h3>

          <p className="text-sm sm:text-base text-earth-muted font-medium max-w-sm mx-auto">
            {voiceState === 'listening'
              ? interimText || '...'
              : voiceState === 'processing'
              ? '...'
              : t('home.voiceCard.subtitle')}
          </p>

          {/* Supported Languages Label */}
          {voiceState === 'idle' && (
            <div className="pt-2 flex items-center justify-center gap-1.5 text-xs font-semibold text-forest">
              <Volume2 className="w-3.5 h-3.5" />
              <span>{t('home.voiceCard.supportedLangs')}</span>
            </div>
          )}
        </div>

        {/* Error Notification */}
        {voiceState === 'error' && errorMessage && (
          <div className="mt-3 p-3 rounded-xl bg-danger-light border border-danger/30 text-danger text-xs sm:text-sm font-medium flex items-center gap-2 max-w-md">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>
    </div>
  );
}
