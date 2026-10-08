# Legal, Regulatory & Compliance Framework

> [!NOTE]
> This document provides engineering compliance guidance and implementation standards, not formal legal advice.

## 1. Digital Personal Data Protection Act 2023 (DPDP Act, India)
- **Notice and Consent**: Clear, bilingual (Tamil & English) notices explaining data collected, purpose (rain alerts and marketplace listing), and third parties involved.
- **Data Minimization**: Precise farmer coordinates are stored internally with PostGIS; the public marketplace shows only village/taluk level. Raw mobile numbers are never displayed publicly.
- **Right to Erasure & Export**: `DELETE /farmers/me` triggers account de-identification and soft/hard delete of personal contact data.

## 2. TRAI Telecom Commercial Communications Customer Preference Regulations (TCCCPR)
- **DLT Registration**: Entity registration, Principal Entity ID, registered Header / Sender ID, and pre-approved SMS content templates.
- **UCS-2 Unicode Segmenting**: Tamil text requires UCS-2 encoding (70 characters per segment instead of 160 GSM-7 characters). Alert copy must be optimized to prevent excessive segment splits.
- **Opt-Out**: Every notification includes an explicit STOP/opt-out mechanism.

## 3. WhatsApp Business Policy
- Outbound proactive notifications use Meta pre-approved message templates.
- Explicit opt-in captured during registration.
- Respect customer care 24-hour service window.

## 4. Forecast Disclaimers & Honesty
- Forecasts are inherently uncertain and probabilistic.
- UI and notifications use phrasing like "likely" ("வாய்ப்பு உள்ளது") rather than absolute certainty ("will rain").
