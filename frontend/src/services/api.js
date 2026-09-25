/**
 * KisanSaarthi AI - API Base Service
 *
 * Designed to connect to a Python FastAPI backend (e.g., http://localhost:8000/api).
 * In development or standalone mode without a live backend, it cleanly provides
 * clearly labeled mock data responses to demonstrate agentic behavior.
 */

// Configure base URL from environment or fallback to relative '/api' (proxied via Vite)
// with direct fallback to local FastAPI ports (127.0.0.1:8000 and localhost:8000)
export const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || '/api';

// Connect directly to live FastAPI backend (with graceful offline fallback)
export const IS_MOCK_MODE = false;

/**
 * Base fetch helper with timeouts, error handling, and JSON parsing
 */
async function fetchClient(endpoint, options = {}) {
  if (IS_MOCK_MODE) {
    console.info(`[FastAPI Service MOCK] Calling: ${endpoint}`, options);
    // Simulate network latency (400ms - 800ms) for realistic UX state testing
    await new Promise((resolve) => setTimeout(resolve, 600));
  }

  const candidateBases = [
    API_BASE_URL,
    '/api',
    'http://127.0.0.1:8000/api',
    'http://localhost:8000/api',
  ];
  const uniqueBases = [...new Set(candidateBases.filter(Boolean))];

  for (const base of uniqueBases) {
    const url = `${base.replace(/\/$/, '')}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      if (!IS_MOCK_MODE) {
        const res = await fetch(url, config);
        if (res.ok) {
          return await res.json();
        }
      }
    } catch (error) {
      // try next candidate
    }
  }

  return null;
}

// ----------------------------------------------------
// AI Chat & Agentic Interaction Endpoints
// ----------------------------------------------------

/**
 * Detects the language of a text based on Unicode character ranges.
 * Keeps user message language independent of selected UI language.
 */
export function detectInputLanguage(text, fallbackLang = 'en') {
  if (!text) return fallbackLang;
  for (const ch of text) {
    const code = ch.charCodeAt(0);
    // Telugu Unicode block (0x0C00 - 0x0C7F)
    if (code >= 0x0c00 && code <= 0x0c7f) {
      return 'te';
    }
    // Devanagari / Hindi Unicode block (0x0900 - 0x097F)
    if (code >= 0x0900 && code <= 0x097f) {
      return 'hi';
    }
  }
  return fallbackLang;
}

export async function sendChatMessage(message, language = 'en', farmerId = 'F001', conversationId = 'default') {
  const payload = {
    message,
    language,
    farmer_id: farmerId,
    conversation_id: conversationId,
  };

  // Multiple candidate endpoints for maximum resilience across environments:
  // 1. Relative '/api/chat' (Vite proxy - eliminates CORS and port mismatch)
  // 2. Direct 'http://127.0.0.1:8000/api/chat'
  // 3. Direct 'http://localhost:8000/api/chat'
  const candidateUrls = [];
  if (API_BASE_URL) {
    candidateUrls.push(`${API_BASE_URL.replace(/\/$/, '')}/chat`);
  }
  if (!candidateUrls.includes('/api/chat')) {
    candidateUrls.push('/api/chat');
  }
  candidateUrls.push('http://127.0.0.1:8000/api/chat');
  candidateUrls.push('http://localhost:8000/api/chat');

  const uniqueUrls = [...new Set(candidateUrls)];
  let lastError = null;

  for (const url of uniqueUrls) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        return await response.json();
      }

      // If server responded with an error, extract detail
      let errDetail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const data = await response.json();
        errDetail = data.detail || data.message || errDetail;
      } catch (_) {}

      // If relative proxy returned 404, continue to next direct candidate
      if (response.status === 404 && url.startsWith('/')) {
        continue;
      }

      lastError = new Error(`Chat API error: ${errDetail}`);
      throw lastError;
    } catch (err) {
      lastError = err;
      // Continue to next candidate URL
    }
  }

  console.error('[KisanSaarthi] Chat request failed on all candidate endpoints:', lastError);
  throw lastError || new Error('Unable to connect to KisanSaarthi chat API.');
}

export async function sendVoiceAudio(audioBlob, language = 'te') {
  console.info(`[FastAPI Service] Voice audio blob ready for upload (${audioBlob.size} bytes, lang: ${language})`);
  await new Promise((resolve) => setTimeout(resolve, 700));

  return {
    isMock: true,
    transcript: language === 'te' ? 'మా వరి చేనులో ఆకులు పసుపు రంగులోకి మారుతున్నాయి' : 'मेरे धान के खेत में पत्तियां पीली पड़ रही हैं',
    confidence: 0.94,
    detectedLanguage: language,
  };
}

export async function uploadImage(imageFile, context = 'crop') {
  console.info(`[FastAPI Service] Uploading image (${imageFile.name}, size: ${imageFile.size}, context: ${context})`);
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return {
    isMock: true,
    imageUrl: URL.createObjectURL(imageFile),
    filename: imageFile.name,
    uploadId: `up-${Date.now()}`,
    status: 'uploaded',
  };
}

// ----------------------------------------------------
// Real Crop Health Diagnostic Service
// ----------------------------------------------------

/**
 * Analyzes a crop leaf photo using the real Crop Health backend (MobileNetV2 + ICAR knowledge).
 * Endpoint: POST /api/crop/health
 */
export async function analyzeCropImage(imageFile, {
  cropName,
  message,
  language = 'te',
  farmerId = 'F001',
} = {}) {
  const formData = new FormData();
  if (imageFile) {
    formData.append('image', imageFile, imageFile.name || 'crop_image.jpg');
  }
  formData.append('farmer_id', farmerId || 'F001');
  formData.append('language', language || 'te');
  if (cropName) {
    formData.append('crop_name', cropName);
  }
  if (message) {
    formData.append('message', message);
  }

  const candidateUrls = [];
  if (API_BASE_URL) {
    candidateUrls.push(`${API_BASE_URL.replace(/\/$/, '')}/crop/health`);
  }
  if (!candidateUrls.includes('/api/crop/health')) {
    candidateUrls.push('/api/crop/health');
  }
  candidateUrls.push('http://127.0.0.1:8000/api/crop/health');
  candidateUrls.push('http://localhost:8000/api/crop/health');

  const uniqueUrls = [...new Set(candidateUrls)];
  let lastError = null;

  for (const url of uniqueUrls) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        return await response.json();
      }

      let errDetail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const data = await response.json();
        errDetail = data.detail || data.message || errDetail;
      } catch (_) {}

      if (response.status === 404 && url.startsWith('/')) {
        continue;
      }

      lastError = new Error(`Crop Health API error: ${errDetail}`);
      throw lastError;
    } catch (err) {
      lastError = err;
    }
  }

  console.error('[KisanSaarthi] Crop Health request failed on all candidate endpoints:', lastError);
  throw lastError || new Error('Unable to connect to KisanSaarthi crop health API.');
}

export async function analyzeCrop(uploadId, notes = '') {
  await new Promise((resolve) => setTimeout(resolve, 1200));
  return {
    isMock: true,
    confidence: 'medium', // Clearly non-guaranteed
    cropIdentified: 'Paddy / వరి',
    possibleIssue: 'Bacterial Leaf Blight / ఆకు ఎండు తెగులు',
    recommendedNextSteps: [
      'తక్షణమే పొలంలో నీటిని తగ్గించండి',
      'నత్రజని ఎరువుల వాడకం తాత్కాలికంగా ఆపండి',
      'సమీప వ్యవసాయ అధికారిని సంప్రదించండి',
    ],
  };
}

export async function findTractors(location, operation = 'ploughing') {
  await new Promise((resolve) => setTimeout(resolve, 800));
  return {
    isMock: true,
    tractors: [
      { id: 't1', model: 'Mahindra 575 DI (45 HP)', provider: 'శ్రీనివాస్ రెడ్డి (Srinivas)', distanceKm: 2.8, pricePerHour: 850, rating: 4.8, available: true },
      { id: 't2', model: 'John Deere 5050 D (50 HP)', provider: 'రమేష్ యాదవ్ (Ramesh)', distanceKm: 4.5, pricePerHour: 900, rating: 4.9, available: true },
    ],
  };
}

const REQUESTS_STORAGE_KEY = 'kisansaarthi_all_requests';

/**
 * Helper to get all stored requests across farmers
 */
function getStoredRequests() {
  try {
    const raw = localStorage.getItem(REQUESTS_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    // Purge any legacy fake/demo requests
    const cleaned = parsed.filter((r) => !['REQ-101', 'REQ-102', 'TRK-8921', 'DIA-4819'].includes(r.id));
    if (cleaned.length !== parsed.length) {
      localStorage.setItem(REQUESTS_STORAGE_KEY, JSON.stringify(cleaned));
    }
    return cleaned;
  } catch {
    return [];
  }
}

/**
 * Helper to save all requests
 */
function setStoredRequests(requests) {
  try {
    localStorage.setItem(REQUESTS_STORAGE_KEY, JSON.stringify(requests));
  } catch (e) {
    console.error('Failed to persist requests:', e);
  }
}

export async function bookTractor(tractorId, bookingDetails = {}, farmer = null) {
  await new Promise((resolve) => setTimeout(resolve, 600));

  const bookingId = `TRK-${Date.now().toString().slice(-6)}`;
  const farmerId = farmer?.id || 'farmer_001';
  const lang = farmer?.language || 'te';
  const defaultFarmerName = lang === 'hi' ? 'किसान भाई' : lang === 'te' ? 'రైతు మిత్రుడు' : 'Farmer Friend';
  const farmerName = farmer?.name || defaultFarmerName;
  const farmerPhone = farmer?.phone || '9876543210';
  const model = bookingDetails.model || 'Mahindra 575 DI (45 HP)';

  const localizedTitle = lang === 'hi'
    ? `ट्रैक्टर बुकिंग (${model})`
    : lang === 'te'
    ? `ట్రాక్టర్ బుకింగ్ (${model})`
    : `Tractor Booking (${model})`;

  const localizedWorkType = lang === 'hi'
    ? 'जुताई कार्य'
    : lang === 'te'
    ? 'దుక్కి దున్నడం'
    : 'Ploughing / Land Prep';

  const localizedStatus = lang === 'hi'
    ? 'कन्फर्म'
    : lang === 'te'
    ? 'నిర్ధారించబడింది'
    : 'Confirmed';

  const newBooking = {
    id: bookingId,
    farmerId,
    farmerName,
    farmerPhone,
    type: 'tractor',
    title: localizedTitle,
    date: lang === 'hi' ? 'अभी-अभी' : lang === 'te' ? 'ఇప్పుడే' : 'Just now',
    status: localizedStatus,
    statusColor: 'bg-green-100 text-forest-dark border-green-300',
    details: {
      tractorId,
      model,
      workType: bookingDetails.workType || localizedWorkType,
      bookedAt: new Date().toISOString(),
      pricePerHour: bookingDetails.pricePerHour || 850,
    },
  };

  // Add to persistent requests store
  const allReqs = getStoredRequests();
  allReqs.unshift(newBooking);
  setStoredRequests(allReqs);

  return {
    isMock: true,
    bookingId,
    status: 'Confirmed',
    farmerId,
    farmerName,
    farmerPhone,
    tractorId,
    bookedAt: newBooking.details.bookedAt,
  };
}

export async function cancelBooking(bookingId) {
  await new Promise((resolve) => setTimeout(resolve, 400));
  const allReqs = getStoredRequests();
  const updated = allReqs.map((r) =>
    r.id === bookingId
      ? { ...r, status: 'Cancelled', statusColor: 'bg-rose-100 text-danger border-rose-300' }
      : r
  );
  setStoredRequests(updated);

  return {
    isMock: true,
    bookingId,
    status: 'Cancelled',
  };
}

export async function findAlternative(bookingId) {
  await new Promise((resolve) => setTimeout(resolve, 900));
  return {
    isMock: true,
    alternativeTractor: {
      id: 't3',
      model: 'Swaraj 744 FE',
      provider: 'వేణుగోపాల్ (Venugopal)',
      distanceKm: 3.2,
      pricePerHour: 860,
      availableImmediately: true,
    },
  };
}

export async function getInsuranceChecklist(cropName) {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return {
    isMock: true,
    crop: cropName || 'Paddy',
    requiredDocs: [
      { name: 'Pattadar Passbook / ల్యాండ్ రికార్డు', status: 'available' },
      { name: 'Crop Sowing Certificate / విత్తిన ధృవీకరణ', status: 'available' },
      { name: 'Geo-tagged field photos / నష్టపోయిన చేను ఫోటోలు', status: 'missing' },
      { name: 'Aadhaar Card copy', status: 'available' },
    ],
  };
}

export async function createInsuranceDraft(claimData, farmer = null) {
  await new Promise((resolve) => setTimeout(resolve, 700));
  const draftId = `INS-${Date.now().toString().slice(-6)}`;
  const farmerId = farmer?.id || 'farmer_001';
  const lang = farmer?.language || 'te';
  const defaultFarmerName = lang === 'hi' ? 'किसान भाई' : lang === 'te' ? 'రైతు మిత్రుడు' : 'Farmer Friend';

  const localizedTitle = lang === 'hi'
    ? 'फसल बीमा क्लेम ड्राफ्ट'
    : lang === 'te'
    ? 'పంట భీమా క్లెయిమ్ దరఖాస్తు'
    : 'Crop Insurance Draft';

  const localizedStatus = lang === 'hi' ? 'ड्राफ्ट तैयार' : lang === 'te' ? 'డ్రాఫ్ట్ సిద్ధమైంది' : 'Draft Prepared';

  const newDraft = {
    id: draftId,
    farmerId,
    farmerName: farmer?.name || defaultFarmerName,
    farmerPhone: farmer?.phone || '9876543210',
    type: 'insurance',
    title: localizedTitle,
    date: lang === 'hi' ? 'अभी-अभी' : lang === 'te' ? 'ఇప్పుడే' : 'Just now',
    status: localizedStatus,
    statusColor: 'bg-purple-100 text-purple-900 border-purple-300',
    details: claimData,
  };

  const allReqs = getStoredRequests();
  allReqs.unshift(newDraft);
  setStoredRequests(allReqs);

  return {
    isMock: true,
    draftId,
    status: localizedStatus,
    notice: 'Assistance tool only. Final claim approval rests with PMFBY portal.',
  };
}

export async function saveDiagnosisRequest(cropName, issue, farmer = null) {
  const diagId = `DIA-${Date.now().toString().slice(-6)}`;
  const farmerId = farmer?.id || 'farmer_001';
  const lang = farmer?.language || 'te';
  const defaultFarmerName = lang === 'hi' ? 'किसान भाई' : lang === 'te' ? 'రైతు మిత్రుడు' : 'Farmer Friend';

  const localizedTitle = lang === 'hi'
    ? `फसल रोग जांच (${cropName})`
    : lang === 'te'
    ? `పంట వ్యాధి నిర్ధారణ (${cropName})`
    : `Crop Diagnosis (${cropName})`;

  const localizedStatus = lang === 'hi' ? 'रिपोर्ट तैयार' : lang === 'te' ? 'రిపోర్ట్ సిద్ధమైంది' : 'Diagnosed';

  const newRequest = {
    id: diagId,
    farmerId,
    farmerName: farmer?.name || defaultFarmerName,
    farmerPhone: farmer?.phone || '9876543210',
    type: 'crop',
    title: localizedTitle,
    date: lang === 'hi' ? 'अभी-अभी' : lang === 'te' ? 'ఇప్పుడే' : 'Just now',
    status: localizedStatus,
    statusColor: 'bg-emerald-100 text-emerald-900 border-emerald-300',
    details: { issue, cropName, date: new Date().toISOString() },
  };

  const allReqs = getStoredRequests();
  allReqs.unshift(newRequest);
  setStoredRequests(allReqs);
  return newRequest;
}

export async function requestSeeds(seedItem, farmer = null) {
  await new Promise((resolve) => setTimeout(resolve, 600));
  const seedReqId = `SED-${Date.now().toString().slice(-6)}`;
  const farmerId = farmer?.id || 'farmer_001';
  const lang = farmer?.language || 'te';
  const defaultFarmerName = lang === 'hi' ? 'किसान भाई' : lang === 'te' ? 'రైతు మిత్రుడు' : 'Farmer Friend';

  const localizedTitle = lang === 'hi'
    ? `बीज अनुरोध (${seedItem?.name || 'धान'})`
    : lang === 'te'
    ? `విత్తనాల అభ్యర్థన (${seedItem?.name || 'వరి'})`
    : `Seed Request (${seedItem?.name || 'Paddy'})`;

  const localizedStatus = lang === 'hi' ? 'स्वीकृत' : lang === 'te' ? 'స్వీకరించబడింది' : 'Received';

  const newRequest = {
    id: seedReqId,
    farmerId,
    farmerName: farmer?.name || defaultFarmerName,
    farmerPhone: farmer?.phone || '9876543210',
    type: 'seeds',
    title: localizedTitle,
    date: lang === 'hi' ? 'अभी-अभी' : lang === 'te' ? 'ఇప్పుడే' : 'Just now',
    status: localizedStatus,
    statusColor: 'bg-amber-100 text-amber-900 border-amber-300',
    details: seedItem,
  };

  const allReqs = getStoredRequests();
  allReqs.unshift(newRequest);
  setStoredRequests(allReqs);

  return {
    isMock: true,
    requestId: seedReqId,
    status: localizedStatus,
  };
}

export async function findSeedOptions(crop) {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return {
    isMock: true,
    seeds: [
      { id: 's1', name: 'BPT 5204 (Samba Mahsuri)', supplier: 'Rythu Seva Kendra', quantityAvailable: '45 Bags (25kg)', pricePerBag: 950 },
      { id: 's2', name: 'MTU 1010 (Cottondora Sannalu)', supplier: 'National Seeds Corp', quantityAvailable: '30 Bags (25kg)', pricePerBag: 920 },
    ],
  };
}

export async function getAgentActivity(requestId) {
  await new Promise((resolve) => setTimeout(resolve, 400));
  return {
    isMock: true,
    steps: [
      { id: 1, title: 'Request received', status: 'done', time: 'Just now' },
      { id: 2, title: 'Language detected: Telugu', status: 'done', time: 'Just now' },
      { id: 3, title: 'Intent identified', status: 'done', time: 'Just now' },
      { id: 4, title: 'Checking resources & database', status: 'in_progress', time: 'Processing...' },
    ],
  };
}

/**
 * Get requests strictly filtered by current farmer's ID
 */
export async function getRequests(farmerId = null) {
  await new Promise((resolve) => setTimeout(resolve, 200));

  const allReqs = getStoredRequests();

  // Strictly filter by farmerId if provided; NO demo requests seeded
  if (farmerId) {
    return allReqs.filter((r) => r.farmerId === farmerId);
  }

  return allReqs;
}
