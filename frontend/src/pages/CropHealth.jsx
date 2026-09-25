import React, { useState } from 'react';
import {
  ArrowLeft,
  Sprout,
  Camera,
  Mic,
  AlertTriangle,
  CheckCircle,
  ChevronRight,
  Loader2,
  Sparkles,
  Volume2,
  ShieldCheck,
  Eye,
  PhoneCall,
  RefreshCw,
} from 'lucide-react';
import { useTranslation } from '../i18n';
import VoiceButton from '../components/voice/VoiceButton';
import ImageUploadButton from '../components/image/ImageUploadButton';
import Card from '../components/common/Card';
import { analyzeCropImage, saveDiagnosisRequest } from '../services/api';
import { speakText } from '../services/voiceService';
import { useFarmerAuth } from '../context/FarmerAuthContext';

export default function CropHealth({ onBack, onOpenChatWithContext }) {
  const { t, lang } = useTranslation();
  const { currentFarmer } = useFarmerAuth();
  const [step, setStep] = useState('input'); // 'input' | 'analyzing' | 'result'
  const [symptomText, setSymptomText] = useState('');
  const [uploadedImage, setUploadedImage] = useState(null);
  const [selectedImageFile, setSelectedImageFile] = useState(null);
  const [diagnosisData, setDiagnosisData] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const crops = [
    { id: 'paddy', name: t('cropHealth.crops.paddy'), icon: '🌾' },
    { id: 'cotton', name: t('cropHealth.crops.cotton'), icon: '🌱' },
    { id: 'chilli', name: t('cropHealth.crops.chilli'), icon: '🌶️' },
    { id: 'maize', name: t('cropHealth.crops.maize'), icon: '🌽' },
  ];
  const [selectedCrop, setSelectedCrop] = useState(crops[0].id);

  const startAnalysis = async () => {
    setErrorMessage(null);
    setStep('analyzing');
    try {
      const cropObj = crops.find((c) => c.id === selectedCrop);
      const cropName = cropObj ? cropObj.name : 'Paddy';
      const res = await analyzeCropImage(selectedImageFile, {
        cropName: selectedCrop,
        message: symptomText,
        language: lang,
        farmerId: currentFarmer?.id || 'F001',
      });
      setDiagnosisData(res);
      const savedCrop = res.crop || cropName;
      const savedIssue = res.possible_issue || res.possible_problem || 'Crop Health Check';
      await saveDiagnosisRequest(savedCrop, savedIssue, currentFarmer);
      setStep('result');
    } catch (err) {
      console.error('[Crop Health Error]', err);
      setErrorMessage(
        lang === 'te'
          ? 'క్షమించండి, పంట విశ్లేషణను పూర్తి చేయడంలో సమస్య ఏర్పడింది. దయచేసి మళ్ళీ ప్రయత్నించండి.'
          : lang === 'hi'
          ? 'क्षमा करें, फसल विश्लेषण पूरा करने में समस्या आई। कृपया पुनः प्रयास करें।'
          : 'Sorry, unable to complete crop analysis right now. Please make sure the backend is running and try again.'
      );
      setStep('input');
    }
  };

  const handleVoiceInput = (text) => {
    setSymptomText(text);
  };

  const handleImageUploaded = (file) => {
    setSelectedImageFile(file);
    setUploadedImage(URL.createObjectURL(file));
  };

  const handleRetry = () => {
    setStep('input');
    setErrorMessage(null);
  };

  const detectedCrop = diagnosisData?.crop || diagnosisData?.cropIdentified || crops.find((c) => c.id === selectedCrop)?.name;
  const possibleIssue = diagnosisData?.possible_issue || diagnosisData?.possible_problem || diagnosisData?.possibleIssue || (diagnosisData?.status === 'needs_image' ? t('cropHealth.photoRequired') : t('cropHealth.cropObservation'));
  const confidencePercent = diagnosisData?.confidence != null ? `${Math.round(diagnosisData.confidence * 100)}%` : null;
  const symptomsList = diagnosisData?.visible_symptoms || diagnosisData?.evidence || diagnosisData?.observations || [];
  const safeStepsList = diagnosisData?.safe_next_steps || diagnosisData?.recommendedNextSteps || diagnosisData?.recommendations || [];
  const preventionList = diagnosisData?.prevention || [];
  const expertAdvisory = diagnosisData?.when_to_contact_expert;
  const warningText = diagnosisData?.warning || t('cropHealth.disclaimer');
  const speechText = diagnosisData?.response || `${possibleIssue}. ${safeStepsList.join('. ')}`;

  return (
    <div className="pb-28 pt-4 px-4 sm:px-6 space-y-5 max-w-lg mx-auto animate-fadeIn select-none">
      {/* Header */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onBack}
          className="p-2 -ml-1 rounded-full hover:bg-earth-subtle text-earth-text active:scale-95"
          aria-label={t('common.back')}
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-xl font-bold text-earth-text tracking-tight flex items-center gap-1.5">
            <Sprout className="w-5 h-5 text-forest" />
            {t('cropHealth.title')}
          </h2>
          <p className="text-xs text-earth-muted">
            {t('cropHealth.subtitle')}
          </p>
        </div>
      </div>

      {/* Step 1: Input Flow */}
      {step === 'input' && (
        <div className="space-y-4">
          {/* Error Message if previous attempt failed */}
          {errorMessage && (
            <div className="p-3.5 rounded-2xl bg-danger-light border border-danger/20 text-danger text-xs flex items-center justify-between gap-2 animate-fadeIn">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                <span>{errorMessage}</span>
              </div>
              <button
                type="button"
                onClick={() => setErrorMessage(null)}
                className="font-bold underline text-xs px-1"
              >
                {t('cropHealth.dismiss')}
              </button>
            </div>
          )}

          {/* Crop Selector Buttons */}
          <div>
            <label className="text-xs font-bold text-earth-muted uppercase tracking-wider block mb-2">
              {t('cropHealth.selectCrop')}
            </label>
            <div className="grid grid-cols-2 gap-2.5">
              {crops.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => setSelectedCrop(c.id)}
                  className={`p-3 rounded-2xl border-2 font-bold text-xs sm:text-sm flex items-center gap-2 transition-all ${
                    selectedCrop === c.id
                      ? 'border-forest bg-forest-50 text-forest-dark shadow-sm'
                      : 'border-earth-border bg-white text-earth-text hover:bg-earth-subtle'
                  }`}
                >
                  <span className="text-xl">{c.icon}</span>
                  <span>{c.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Voice Input Section */}
          <div className="p-4 rounded-2xl bg-white border border-earth-border shadow-sm space-y-2">
            <label className="text-xs font-bold text-earth-muted uppercase tracking-wider block">
              {t('cropHealth.tellInYourWords')}
            </label>
            <p className="text-xs text-earth-text font-medium">
              "{t('cropHealth.prompt')}"
            </p>
            <VoiceButton size="large" onSpeechResult={handleVoiceInput} />
            {symptomText && (
              <div className="p-2.5 rounded-xl bg-forest-50 text-forest-dark text-xs font-semibold border border-forest/20">
                ✅ {t('cropHealth.spokenPrefix')}: "{symptomText}"
              </div>
            )}
          </div>

          {/* Camera Upload Section */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-earth-muted uppercase tracking-wider block">
              {t('cropHealth.takeOrShowPhoto')}
            </label>
            <ImageUploadButton variant="card" onImageSelected={handleImageUploaded} />
            {uploadedImage && (
              <div className="relative rounded-2xl overflow-hidden aspect-video border-2 border-forest">
                <img src={uploadedImage} alt="Crop" className="w-full h-full object-cover" />
                <span className="absolute top-2 right-2 px-2 py-1 rounded bg-black/60 text-white text-[10px] font-bold">
                  {t('cropHealth.photoAttached')}
                </span>
              </div>
            )}
          </div>

          {/* Start Analysis Button */}
          <button
            type="button"
            onClick={startAnalysis}
            className="w-full py-4 rounded-2xl bg-forest hover:bg-forest-600 text-white font-bold text-base shadow-farmer-lg shadow-forest/25 flex items-center justify-center gap-2 active:scale-98 transition-all touch-target-lg"
          >
            <Sparkles className="w-5 h-5 text-harvest" />
            <span>{t('cropHealth.analyzeBtn')}</span>
          </button>
        </div>
      )}

      {/* Step 2: Analyzing State */}
      {step === 'analyzing' && (
        <div className="py-16 text-center space-y-4">
          <div className="w-20 h-20 rounded-3xl bg-forest-50 border-2 border-forest text-forest mx-auto flex items-center justify-center shadow-lg animate-bounce">
            <Sprout className="w-10 h-10" />
          </div>
          <h3 className="text-xl font-bold text-earth-text">
            {t('cropHealth.analyzing')}
          </h3>
          <p className="text-xs text-earth-muted max-w-xs mx-auto">
            {t('cropHealth.comparingResearch')}
          </p>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-800 text-xs font-semibold border border-amber-200">
            <Loader2 className="w-3.5 h-3.5 animate-spin" /> {t('cropHealth.preliminaryDiagnosis')}
          </div>
        </div>
      )}

      {/* Step 3: Result & Treatment Steps */}
      {step === 'result' && diagnosisData && (
        <div className="space-y-4 animate-fadeIn">
          {/* Status Guard Banners */}
          {diagnosisData.status === 'needs_better_image' && (
            <div className="p-4 rounded-2xl bg-amber-50 border-2 border-amber-300 text-amber-900 text-xs sm:text-sm space-y-1.5">
              <div className="flex items-center gap-2 font-bold text-amber-950">
                <Camera className="w-5 h-5 text-amber-700 flex-shrink-0" />
                <span>
                  {lang === 'te'
                    ? 'మంచి వెలుతురులో స్పష్టమైన ఫోటో తీయండి'
                    : lang === 'hi'
                    ? 'कृपया पत्तियों की नज़दीक से साफ़ फ़ोटो अपलोड करें'
                    : 'Please take a clearer photo of the affected leaf.'}
                </span>
              </div>
              <p className="text-xs text-amber-800 leading-relaxed">
                {diagnosisData.next_question ||
                  (lang === 'te'
                    ? 'దయచేసి పగటి వెలుతురులో, ఆకులపై దగ్గరగా (close-up) స్పష్టమైన ఫోటో తీసి మళ్లీ పంపండి.'
                    : lang === 'hi'
                    ? 'फ़ोटो पूरी तरह स्पष्ट नहीं है। दिन की रोशनी में पत्तियों की साफ़ फ़ोटो लें।'
                    : 'The photo is blurry or unclear. Please take a closer, well-lit photo of the leaf in daylight.')}
              </p>
            </div>
          )}

          {diagnosisData.status === 'uncertain' && (
            <div className="p-4 rounded-2xl bg-amber-50 border-2 border-amber-300 text-amber-900 text-xs sm:text-sm space-y-1.5">
              <div className="flex items-center gap-2 font-bold text-amber-950">
                <AlertTriangle className="w-5 h-5 text-amber-700 flex-shrink-0" />
                <span>
                  {lang === 'te'
                    ? 'సమస్య స్పష్టంగా నిర్ధారించబడలేదు'
                    : lang === 'hi'
                    ? 'फ़ोटो से समस्या की स्पष्ट पहचान नहीं हो सकी'
                    : 'Image could not be confidently identified'}
                </span>
              </div>
              <p className="text-xs text-amber-800 leading-relaxed">
                {lang === 'te'
                  ? 'చిత్రం స్పష్టంగా పంటను సూచించడం లేదు. దయచేసి పంట ఆకుల స్పష్టమైన ఫోటోను అందించండి లేదా స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.'
                  : lang === 'hi'
                  ? 'चित्र में फसल या पत्ती स्पष्ट नहीं है। कृपया स्पष्ट फ़ोटो अपलोड करें या स्थानीय कृषि विशेषज्ञ से संपर्क करें।'
                  : 'The image could not be confidently identified. Please take a clear photo of an affected leaf or consult your local agricultural expert.'}
              </p>
            </div>
          )}

          {diagnosisData.status === 'unsupported' && (
            <div className="p-4 rounded-2xl bg-amber-50 border-2 border-amber-300 text-amber-900 text-xs sm:text-sm space-y-1.5">
              <div className="flex items-center gap-2 font-bold text-amber-950">
                <AlertTriangle className="w-5 h-5 text-amber-700 flex-shrink-0" />
                <span>
                  {lang === 'te'
                    ? 'ఈ పంట ప్రస్తుతం మోడల్‌లో మద్దతు లేదు'
                    : lang === 'hi'
                    ? 'यह फसल वर्तमान मॉडल में समर्थित नहीं है'
                    : 'Crop or image is currently unsupported'}
                </span>
              </div>
              <p className="text-xs text-amber-800 leading-relaxed">
                {diagnosisData.warning ||
                  'Supported crops: Tomato, Corn, Potato, Grape, Pepper, Apple, Peach, Strawberry, Cherry, Squash, Cotton, Paddy.'}
              </p>
            </div>
          )}

          {/* Preliminary Result Card */}
          <div className="p-5 rounded-3xl bg-white border-2 border-forest shadow-farmer-lg space-y-3">
            <div className="flex items-center justify-between">
              {detectedCrop && (
                <span className="text-xs font-bold uppercase tracking-wider text-forest bg-forest-50 px-2.5 py-1 rounded-full border border-forest/20">
                  🌱 {detectedCrop}
                </span>
              )}
              {confidencePercent && (
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300">
                  {t('cropHealth.confidence')}: {confidencePercent}
                </span>
              )}
            </div>

            <h3 className="text-xl font-black text-earth-text">
              {possibleIssue}
            </h3>

            {/* Read-aloud button */}
            <button
              type="button"
              onClick={() => speakText(speechText, lang)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-forest text-white text-xs font-bold active:scale-95 shadow-sm"
            >
              <Volume2 className="w-4 h-4" />
              <span>{t('cropHealth.listen')}</span>
            </button>
          </div>

          {/* Visual Symptoms Observed */}
          {symptomsList.length > 0 && (
            <div className="p-5 rounded-3xl bg-white border border-earth-border shadow-farmer space-y-2.5">
              <h4 className="font-bold text-earth-text text-sm sm:text-base flex items-center gap-2">
                <Eye className="w-5 h-5 text-forest" />
                <span>{t('cropHealth.observedSymptoms')}</span>
              </h4>
              <div className="space-y-1.5">
                {symptomsList.map((sym, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs sm:text-sm text-earth-text">
                    <span className="text-forest font-bold">•</span>
                    <span>{sym}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Safe Next Steps */}
          {safeStepsList.length > 0 && (
            <div className="p-5 rounded-3xl bg-white border border-earth-border shadow-farmer space-y-3">
              <h4 className="font-bold text-earth-text text-sm sm:text-base flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-forest" />
                {t('cropHealth.treatment')}
              </h4>

              <div className="space-y-2">
                {safeStepsList.map((stepItem, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 p-3 rounded-xl bg-earth-subtle text-xs sm:text-sm font-medium text-earth-text">
                    <span className="w-5 h-5 rounded-full bg-forest text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <span>{stepItem}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Long-term Prevention */}
          {preventionList.length > 0 && (
            <div className="p-5 rounded-3xl bg-white border border-earth-border shadow-farmer space-y-2.5">
              <h4 className="font-bold text-earth-text text-sm sm:text-base flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-forest" />
                <span>{t('cropHealth.prevention')}</span>
              </h4>
              <div className="space-y-1.5">
                {preventionList.map((prevItem, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs sm:text-sm text-earth-text">
                    <span className="text-forest font-bold">✓</span>
                    <span>{prevItem}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* When to Contact Expert Advisory */}
          {expertAdvisory && (
            <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200 text-blue-950 text-xs sm:text-sm space-y-1">
              <div className="flex items-center gap-2 font-bold text-blue-900">
                <PhoneCall className="w-4 h-4 text-blue-700 flex-shrink-0" />
                <span>
                  {lang === 'te' ? 'అధికారి సంప్రదింపు' : lang === 'hi' ? 'कृषि अधिकारी से सलाह' : 'Expert Advisory'}
                </span>
              </div>
              <p className="text-xs text-blue-900 leading-relaxed">
                {expertAdvisory}
              </p>
            </div>
          )}

          {/* Crucial Ethical AI Disclaimer */}
          <div className="p-4 rounded-2xl bg-amber-50 border border-amber-300 text-amber-900 text-xs flex items-start gap-2.5">
            <AlertTriangle className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              {warningText}
            </p>
          </div>

          {/* Actions: Re-analyze or Ask AI Assistant */}
          <div className="space-y-2">
            <button
              type="button"
              onClick={() => onOpenChatWithContext && onOpenChatWithContext(
                lang === 'te'
                  ? `${detectedCrop || ''} పంటలో ${possibleIssue || ''} సమస్యకు తదుపరి సలహా ఇవ్వండి.`
                  : lang === 'hi'
                  ? `${detectedCrop || ''} फसल में ${possibleIssue || ''} समस्या के लिए सलाह दें।`
                  : `I received diagnosis for ${detectedCrop || 'crop'} (${possibleIssue || 'issue'}). What should I do next?`
              )}
              className="w-full py-3.5 rounded-2xl bg-forest-50 hover:bg-forest-100 text-forest-dark border border-forest/30 font-bold text-sm flex items-center justify-center gap-2 active:scale-98 transition-all"
            >
              <span>{t('cropHealth.askAiMore')}</span>
              <ChevronRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={handleRetry}
              className="w-full py-2.5 rounded-2xl bg-white border border-earth-border hover:bg-earth-subtle text-earth-muted hover:text-earth-text font-semibold text-xs flex items-center justify-center gap-1.5 active:scale-98 transition-all"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>{t('cropHealth.checkAnotherPhoto')}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
