# KisanSaarthi Crop Insurance Knowledge Base

## Overview
This directory contains the curated, domain-specific Insurance Knowledge Base for KisanSaarthi. It provides reliable, objective, and non-hallucinating information to assist farmers experiencing crop damage with insurance guidance.

## What the Knowledge Base Contains

The knowledge base is organized into four modular JSON files:

1. **`damage_types.json`**:
   - `heavy_rain`: Heavy rainfall, water submergence, and lodging guidance.
   - `flood_waterlogging`: Flood, inundation, and silt deposition assistance.
   - `drought`: Dry spell, wilting, and moisture stress guidance.
   - `hailstorm`: Mechanical injury from hail impact, punctures, and immediate evidence.
   - `storm_wind`: Gale, storm, cyclone wind damage, and lodging advice.
   - `pest_disease`: Pest outbreaks, foliar lesions, and epidemic loss assistance.

2. **`documents_guidance.json`**:
   - `documents_guidance`: Common documents that may be required (land records, Aadhaar, bank passbook, sowing certificate, premium receipt).
   - `damage_evidence`: Visual proof recommendations (geo-tagged photos, panoramic views, close-up injury details).

3. **`claim_steps.json`**:
   - `claim_process`: Overview of general loss intimation, helpline registration, and joint field inspection.
   - `safety_verification`: Anti-fraud guidance (never paying unauthorized intermediaries or middle agents; verifying surveyor identity cards).

4. **`insurance_general.json`**:
   - `general_guidance`: General explanation of how crop insurance operates and notified scheme boundaries.
   - `no_guarantee_notice`: Explicit clarification that no third-party tool or agent can guarantee claim approval or payouts.

## How Retrieval Works

The retrieval service is implemented in `backend/services/insurance_retrieval_service.py`:

1. **In-Memory Loading**: On application startup or first query, all JSON entries are loaded and indexed.
2. **Text Normalization**: Farmer queries are converted to lowercase and cleaned of punctuation.
3. **Exact Phrase & Keyword Matching**: Each topic's curated keywords and phrases are matched against the query. Exact multi-word matches (e.g., "heavy rain", "water entered my field", "guarantee") receive higher scoring weight than single tokens.
4. **Reliability Guard**: If no topic reaches a sufficient match score, the service returns `matched: false` with the fallback message:
   > *"I don't have enough verified information to answer that reliably. Please check the applicable insurer or official scheme guidance."*
5. **No Forced Matching**: The retrieval never forces a low-confidence match for out-of-domain queries (e.g., questions about tractors, cooking, or general electronics).

## How to Add Another Insurance Topic

To add a new topic (for example, *unseasonal frost / cold wave*):

1. Open `damage_types.json` (or the relevant JSON file).
2. Append a new item following the standard schema:
   ```json
   {
     "id": "cold_wave_frost",
     "topic": "Cold Wave and Frost Damage",
     "keywords": [
       "frost",
       "cold wave",
       "frost damage",
       "freezing temperatures"
     ],
     "guidance": "Frost and extreme cold can damage tender vegetative tissue and flowers...",
     "information_to_collect": [
       "Date and estimated duration of freezing temperatures",
       "Affected crop variety and flowering/fruiting stage"
     ],
     "useful_evidence": [
       "Photographs of blackened/scorched foliage and damaged buds",
       "Local meteorological minimum temperature reports"
     ],
     "general_next_steps": [
       "Notify local agriculture officers promptly",
       "Keep land records ready for surveyor assessment"
     ]
   }
   ```
3. Save the file. The retrieval service automatically reloads the updated entries upon next call.

## Important Limitations

1. **General Assistance Only**: This knowledge base does not constitute legal or binding insurance contract advice.
2. **No Guaranteed Deadlines or Payouts**: Terms, claim windows, and compensation formulas differ across states, notified crops, and seasons. Phrases like *"may be required"* and *"depending on the applicable scheme"* are deliberately used.
3. **No Claim Adjudication**: KisanSaarthi cannot submit, approve, or adjudicate actual insurance claims. Approval remains the sole legal purview of designated insurance companies and government committees.
