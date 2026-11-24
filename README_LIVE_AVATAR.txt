CASELAB AI v1.5 — Live Avatar Preview (local demo / gated feature)

START HERE
1. Create a local .streamlit/secrets.toml in THIS folder (do NOT upload it).
2. Copy and fill the settings from LIVEAVATAR_SECRETS_EXAMPLE.toml.
3. In the VS Code terminal in this folder run:
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
4. Review portfolio, continue to client meeting, click Begin meeting with Alex.
5. Click Start live video consultation; click Chat now inside the embedded window.
6. Keep live chat to 2 minutes (provider may impose additional restrictions).

NOTE
- Existing CaseLab typed interview, feedback, PDF and voice remain unchanged.
- The LiveAvatar preview uses its OWN conversational model/context and is NOT
  transcribed into CaseLab's formative feedback or downloaded report.
- LiveAvatar API key is server-side. Do not commit secrets.toml to GitHub.
- LiveAvatar credits are charged for non-sandbox tests. Set LIVEAVATAR_ENABLED
  to false before publishing a public demo unless you are prepared for usage.
- Select a British male voice in LiveAvatar -> Voices; copy its VOICE ID.
- This is an integration PROTOTYPE, not a complete voice-driven CaseLab engine.
- Do not advertise the video conversation as feeding the AI assessment.
