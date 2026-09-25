/**
 * Voice Service for KisanSaarthi AI
 *
 * Implements real browser SpeechRecognition and SpeechSynthesis,
 * with structured hooks for FastAPI audio streaming.
 */

export const BROWSER_LANG_CODES = {
  te: 'te-IN',
  hi: 'hi-IN',
  en: 'en-IN',
};

/**
 * Check if the browser supports Speech Recognition
 */
export function isSpeechRecognitionSupported() {
  return typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);
}

/**
 * Check if the browser supports Speech Synthesis (Audio response playback)
 */
export function isSpeechSynthesisSupported() {
  return typeof window !== 'undefined' && 'speechSynthesis' in window;
}

/**
 * Initialize Speech Recognition instance
 */
export function createSpeechRecognizer({
  language = 'te',
  onResult = () => {},
  onError = () => {},
  onStart = () => {},
  onEnd = () => {},
}) {
  if (!isSpeechRecognitionSupported()) {
    console.warn('SpeechRecognition is not supported in this browser.');
    return null;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognizer = new SpeechRecognition();

  recognizer.continuous = false;
  recognizer.interimResults = true;
  recognizer.lang = BROWSER_LANG_CODES[language] || 'te-IN';

  recognizer.onstart = () => {
    onStart();
  };

  recognizer.onresult = (event) => {
    let interimTranscript = '';
    let finalTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      } else {
        interimTranscript += event.results[i][0].transcript;
      }
    }

    onResult({
      final: finalTranscript,
      interim: interimTranscript,
      isFinal: finalTranscript.length > 0,
    });
  };

  recognizer.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    onError(event.error);
  };

  recognizer.onend = () => {
    onEnd();
  };

  return recognizer;
}

/**
 * Play farmer-friendly audio response via Text-to-Speech
 */
export function speakText(text, language = 'te', onFinished = () => {}) {
  if (!isSpeechSynthesisSupported()) {
    console.warn('SpeechSynthesis is not supported.');
    onFinished();
    return;
  }

  // Cancel any ongoing speech
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = BROWSER_LANG_CODES[language] || 'te-IN';
  utterance.rate = 0.95; // Slightly slower pace for clarity
  utterance.pitch = 1.0;

  utterance.onend = () => {
    onFinished();
  };

  utterance.onerror = (e) => {
    console.warn('SpeechSynthesis error:', e);
    onFinished();
  };

  window.speechSynthesis.speak(utterance);
}

/**
 * Stop any current audio playback
 */
export function stopSpeaking() {
  if (isSpeechSynthesisSupported()) {
    window.speechSynthesis.cancel();
  }
}
