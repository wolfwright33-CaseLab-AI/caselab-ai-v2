# CaseLab AI v2.17 — deployable hosted-avatar demo

This is an intentionally scoped interim build to get CaseLab's 5-stage experience and hosted LiveAvatar ONLINE.

WORKING IN CODE (requires your real paid API credentials to live-test):
- Secure server-generated hosted LiveAvatar embed (`POST /v2/embeddings`)
- Return from Stage 4 to Stage 5 after clicking End consultation
- AI evidence-based assessment of a manually supplied, genuine labelled transcript
- Browser Print / Save as PDF; JSON export
- Single-container Docker deployment (FastAPI serves the built React site)

NOT IMPLEMENTED:
- Custom push-to-talk (hosted iframe owns microphone)
- Automatic extraction of hosted interview transcript
- One-click feedback directly from the hosted conversation
- Real SSO

LOCAL START:
1. Copy an existing **private** .env from your prior CaseLab project into this project's root. Never commit it.
2. In project root: `python -m pip install -r requirements_v2.txt`
3. Terminal A (project root): `python -m uvicorn server:app --host 127.0.0.1 --port 8765`
4. Terminal B (project root): `cd live-client`, `npm.cmd install`, `npm.cmd run dev`
5. Open Vite localhost URL and work through 5 stages.

DEPLOY USING RENDER:
1. Create a **NEW PRIVATE GitHub repo** called e.g. `caselab-v2-demo` (do not overwrite the old Streamlit app).
2. Upload THIS project excluding .env, .streamlit/secrets.toml, node_modules, __pycache__, etc.
3. At render.com choose New -> Web Service -> connect the NEW repo.
4. Select Docker runtime; Dockerfile in project root. No build/start commands required.
5. Environment variables, configured in Render (not committed to GitHub):
   CASELAB_DEMO_PASSCODE, LIVEAVATAR_API_KEY, LIVEAVATAR_AVATAR_ID,
   LIVEAVATAR_CONTEXT_ID, LIVEAVATAR_VOICE_ID, LIVEAVATAR_MAX_SECONDS,
   MAX_DEMO_SESSIONS, OPENAI_API_KEY, OPENAI_FEEDBACK_MODEL.
6. Deploy. Open Render URL and verify both hosted avatar and manually submitted assessment.
7. Be aware in-memory session counts reset on container restart and do not cap cost across restarts/users.

IMPORTANT: Render is the host for this React + FastAPI service, not Streamlit Community Cloud.
The older Streamlit site remains separate and unaffected. A new Streamlit entrypoint won't automatically serve a React application.

To achieve TRUE PTT and AUTO transcript feedback use LiveAvatar FULL Mode session SDK with `interactivity_type=PUSH_TO_TALK`, a stable running session and GET /v1/sessions/{session_id}/transcript. This hosted embed cannot offer those features via cross-origin React calls.
