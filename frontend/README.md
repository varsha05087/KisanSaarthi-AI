# KisanSaarthi AI (కిసాన్ సారథి AI / किसान सारथी AI)
> **Tagline:** “Talk. Show. Get help.”  
> **UX Philosophy:** *“Don’t make the farmer learn the app. Make the app understand the farmer.”*

---

## 🌟 Hackathon Features Implemented (Part 1 Foundation)

1. **Farmer-First Visual Identity:**
   - Forest Green (`#2E7D32`), Leaf Green (`#66BB6A`), Harvest Yellow (`#F9A825`), Warm Off-white (`#FAF8F2`)
   - High-contrast typography supporting **Telugu**, **Hindi/Devanagari**, and **English**
   - 56px–64px minimum touch targets, soft cards, zero complex enterprise menus.

2. **Multilingual i18n Architecture (`src/i18n/`):**
   - Authentic, conversational translations for **Telugu (తెలుగు)**, **Hindi (हिन्दी)**, and **English**.
   - Language selector always accessible in header with native script titles and voice greeting previews.

3. **Visually Prominent Voice Centerpiece (`VoiceButton.jsx`):**
   - Animated ripple & pulse state machine:
     - 🎤 *Idle:* "మాట్లాడండి" (Tap to speak)
     - 🔴 *Listening:* "వింటున్నాను... ఇప్పుడు మాట్లాడండి" (Listening... Please speak now)
     - ⏳ *Processing:* "అర్థం చేసుకుంటున్నాను..." (Understanding...)
   - Real browser Speech Recognition (`webkitSpeechRecognition`/`SpeechRecognition`) with graceful error prompts.
   - Text-to-speech audio feedback (`SpeechSynthesis`).

4. **Instant Camera / Image Upload Flow (`ImageUploadButton.jsx`, `ImagePreviewModal.jsx`):**
   - 📷 Take Photo & 🖼 Choose from Gallery picker.
   - Image confirmation prompt: *"Is this the photo you want to send?"* with [Send Photo] and [Retake].
   - Non-fake loading state: *"Analyzing your photo..."* prepared for FastAPI vision agent.

5. **Quick Agriculture Action Cards (4 Core Services):**
   - 🌱 **Crop Problem:** Leaf spots, pests, diseases
   - 🚜 **Tractor Booking:** Ploughing, harvesting, transport
   - 🌾 **Seeds & Inputs:** Certified seeds & availability
   - 🛡 **Crop Insurance:** PMFBY help & damage claim preparation

6. **Offline-First Resilience:**
   - Real-time online/offline network detection with warm reassurance banner:
     *"Internet is unavailable. Your request will be saved and synced."*

---

## 🚀 How to Run the Project

### Option A: Instant Browser Preview (Zero Installation)
Simply open `preview.html` directly in Google Chrome or Microsoft Edge:
```bash
# In your browser, open file:
C:\Users\hi\.gemini\antigravity\scratch\kisansaarthi-ai\preview.html
```

### Option B: Modern Vite Development Server
Once Node.js is installed on your system:
```bash
cd C:\Users\hi\.gemini\antigravity\scratch\kisansaarthi-ai
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📁 Project Structure

```
kisansaarthi-ai/
├── index.html
├── preview.html              # Instant zero-dependency browser preview
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── src/
│   ├── index.css             # Tailwind base + custom voice animations
│   ├── main.jsx              # React DOM entry
│   ├── App.jsx               # Centered responsive container & routing
│   ├── i18n/
│   │   ├── index.jsx         # LanguageContext & useTranslation hook
│   │   ├── te.js             # Telugu translations
│   │   ├── hi.js             # Hindi translations
│   │   └── en.js             # English translations
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.jsx    # Logo, language trigger, online/offline pill
│   │   │   ├── BottomNav.jsx # 3-tab accessible navigation
│   │   │   ├── Card.jsx      # Accessible card primitive
│   │   │   ├── LanguageSelectorModal.jsx # Multilingual modal
│   │   │   └── OfflineBanner.jsx         # Connection loss reassurance
│   │   ├── voice/
│   │   │   └── VoiceButton.jsx           # Real Web Speech API + animated ripples
│   │   └── image/
│   │       ├── ImageUploadButton.jsx     # Camera/Gallery trigger
│   │       └── ImagePreviewModal.jsx     # Preview, retake & analyze modal
│   ├── pages/
│   │   ├── Onboarding.jsx    # Welcoming 1st-time language selection
│   │   ├── Home.jsx          # Farmer centerpiece dashboard
│   │   ├── Requests.jsx      # My requests & status tracking
│   │   └── Profile.jsx       # Farmer profile & voice settings
│   └── services/
│       ├── api.js            # FastAPI ready API client + mock fallback
│       ├── voiceService.js   # Browser SpeechRecognition & synthesis
│       └── imageService.js   # Preview URL creation & image validation
```

---

## 🔌 FastAPI Backend Readiness
All API service functions are isolated in [`src/services/api.js`](src/services/api.js):
- `sendChatMessage()`
- `sendVoiceAudio()`
- `uploadImage()`
- `analyzeCrop()`
- `findTractors()`
- `bookTractor()`
- `cancelBooking()`
- `findAlternative()`
- `getInsuranceChecklist()`
- `findSeedOptions()`

No backend logic is mixed into UI components. To connect your live FastAPI backend, set `IS_MOCK_MODE = false` and update `VITE_API_BASE_URL` in `.env`.
