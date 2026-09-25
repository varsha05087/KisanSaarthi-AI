/**
 * Farmer Authentication & Identity Service
 *
 * Voice-First Farmer Identity: Name + Phone + Language
 * Stores identity locally in demo mode; structured to connect
 * seamlessly to future FastAPI authentication endpoints:
 * POST /auth/register
 * POST /auth/login
 * GET  /farmer/me
 */

const STORAGE_KEYS = {
  CURRENT_FARMER: 'kisansaarthi_current_farmer',
  FARMERS_STORE: 'kisansaarthi_registered_farmers',
  ONBOARDED: 'kisansaarthi_onboarded',
};

/**
 * Generate a clean farmer ID (e.g. farmer_849)
 */
export function generateFarmerId() {
  const rand = Math.floor(100 + Math.random() * 900);
  return `farmer_${rand}`;
}

/**
 * Format raw 10-digit phone number into readable format (e.g. "98765 43210")
 */
export function formatPhoneNumber(phone) {
  if (!phone) return '';
  const cleaned = phone.toString().replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
  }
  return cleaned;
}

/**
 * Normalize spoken numbers or text into digits (e.g. "nine eight seven" -> "987")
 */
export function parseSpokenDigits(text) {
  if (!text) return '';
  
  const wordMap = {
    // English
    zero: '0', one: '1', two: '2', three: '3', four: '4', five: '5', six: '6', seven: '7', eight: '8', nine: '9',
    // Telugu
    సున్నా: '0', ఒకటి: '1', రెండు: '2', మూడు: '3', నాలుగు: '4', ఐదు: '5', ఆరు: '6', ఏడు: '7', ఎనిమిది: '8', తొమ్మిది: '9',
    // Hindi
    शून्य: '0', एक: '1', दो: '2', तीन: '3', चार: '4', पांच: '5', पाँच: '5', छह: '6', सात: '7', आठ: '8', नौ: '9',
  };

  // Replace recognized words with digits
  let normalized = text.toLowerCase();
  Object.keys(wordMap).forEach((word) => {
    const reg = new RegExp(word, 'g');
    normalized = normalized.replace(reg, wordMap[word]);
  });

  // Extract only digits
  return normalized.replace(/\D/g, '').slice(0, 10);
}

/**
 * Retrieve current logged-in farmer profile from storage
 */
export function getCurrentFarmer() {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.CURRENT_FARMER);
    return data ? JSON.parse(data) : null;
  } catch (e) {
    console.error('Failed to read farmer from storage:', e);
    return null;
  }
}

/**
 * Save / Login a farmer profile
 */
export function saveFarmerProfile(farmer) {
  try {
    const lang = farmer.language || 'te';
    const defaultName = lang === 'hi' ? 'किसान भाई' : lang === 'en' ? 'Farmer Friend' : 'రైతు మిత్రుడు';

    const profile = {
      id: farmer.id || generateFarmerId(),
      name: farmer.name?.trim() || defaultName,
      phone: farmer.phone?.replace(/\D/g, '') || '9876543210',
      language: lang,
      createdAt: farmer.createdAt || new Date().toISOString(),
      avatar: farmer.avatar || '👨‍🌾',
    };

    // Save active session
    localStorage.setItem(STORAGE_KEYS.CURRENT_FARMER, JSON.stringify(profile));
    localStorage.setItem(STORAGE_KEYS.ONBOARDED, 'true');

    // Also persist in local registry of known farmers on this device
    const allFarmers = getAllFarmers();
    const existingIndex = allFarmers.findIndex((f) => f.phone === profile.phone || f.id === profile.id);
    if (existingIndex >= 0) {
      allFarmers[existingIndex] = profile;
    } else {
      allFarmers.push(profile);
    }
    localStorage.setItem(STORAGE_KEYS.FARMERS_STORE, JSON.stringify(allFarmers));

    return profile;
  } catch (e) {
    console.error('Failed to save farmer profile:', e);
    return farmer;
  }
}

/**
 * Retrieve all registered farmers on this device
 */
export function getAllFarmers() {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.FARMERS_STORE);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    return [];
  }
}

/**
 * Clear current farmer session (Logout / Change Farmer)
 * Does NOT delete the farmer's requests or records.
 */
export function clearCurrentFarmer() {
  try {
    localStorage.removeItem(STORAGE_KEYS.CURRENT_FARMER);
    localStorage.removeItem(STORAGE_KEYS.ONBOARDED);
  } catch (e) {
    console.error('Failed to clear current farmer session:', e);
  }
}

/**
 * Create a quick default demo farmer using the current device
 * For "ఈ ఫోన్తో కొనసాగండి" (Continue with this phone)
 */
export function createDefaultDeviceFarmer(lang = 'te') {
  const defaultNames = {
    te: 'రైతు మిత్రుడు',
    hi: 'किसान भाई',
    en: 'Farmer Friend',
  };

  return saveFarmerProfile({
    id: generateFarmerId(),
    name: defaultNames[lang] || 'రైతు మిత్రుడు',
    phone: '9876543210',
    language: lang,
    isDeviceQuickProfile: true,
  });
}
