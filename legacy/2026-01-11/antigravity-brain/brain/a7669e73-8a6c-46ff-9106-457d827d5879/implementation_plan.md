# Autonomax Branding & Verification Plan

This plan outlines the steps to rebrand the "YouTube AI v3.0" system to "Autonomax" and verify the AI engine's connectivity and functionality.

## Proposed Changes

### Frontend Branding

Update the application identity from "YouTube AI" to "Autonomax".

#### [MODIFY] [index.html](file:///Users/pq/_youtube_ai_app_v3.0/frontend/index.html)

- Change `<title>` to "Autonomax Platform".

#### [MODIFY] [App.tsx](file:///Users/pq/_youtube_ai_app_v3.0/frontend/src/App.tsx)

- Update Navbar/Header text to "Autonomax".

#### [MODIFY] [Dashboard.tsx](file:///Users/pq/_youtube_ai_app_v3.0/frontend/src/components/Dashboard.tsx)

- Update dashboard headers and branding elements.

#### [MODIFY] [Login.tsx](file:///Users/pq/_youtube_ai_app_v3.0/frontend/src/components/Auth/Login.tsx) & [Register.tsx](file:///Users/pq/_youtube_ai_app_v3.0/frontend/src/components/Auth/Register.tsx)

- Update auth page headers.

#### [NEW] [manifest.json](file:///Users/pq/_youtube_ai_app_v3.0/frontend/public/manifest.json)

- Create a manifest file with `short_name: "Autonomax"` as recommended.

### Backend & AI Verification

Ensure the "Brain" of the system is functional.

#### [VERIFY] `.env` Configuration

- Check for `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.
- Ensure `AI_PROVIDER` is set correctly.

#### [VERIFY] API Connectivity (Pulse Test)

- Check `http://localhost:8000/api/status` or similar endpoints.

#### [VERIFY] AI Generation (Ignition Test)

- Attempt to generate content using the backend API directly or through the UI.

## Verification Plan

### Automated Tests

- None planned; manual verification of UI and API responses.

### Manual Verification

- **Branding Check**: Verify the title and navbar in the browser.
- **Pulse Test**: Check backend health logs.
- **Ignition Test**: Trigger a generation and check for non-empty results.
