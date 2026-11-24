CASELAB v1.6 — LIVE INTERVIEW REVIEW + ARCHER VOICE

WHAT'S NEW
- Target 8-minute LiveAvatar session (paid plan; set LIVEAVATAR_MAX_SECONDS = 480 in Streamlit Secrets).
- Optional ElevenLabs text-chat voice, to match Archer. Copy Archer's ElevenLabs VOICE ID (not the LiveAvatar voice ID) and a valid ElevenLabs API key into Streamlit Secrets.
- New 'END LIVE CONSULTATION & GENERATE FEEDBACK' action retrieves session dialogue via LiveAvatar and passes the authentic turns to the existing formative-feedback/PDF pipeline.
- If an embed's session hasn't populated in LiveAvatar's session listing, find the ID under LiveAvatar > Usage and enter it in Advanced.

SAFETY / LIMITATIONS
- TEST ON A PRIVATE DEVELOPMENT APP BEFORE UPDATING MAIN. Upload app.py to GitHub only after checks pass.
- Never upload .streamlit/secrets.toml to GitHub. Use Streamlit Cloud Settings > Secrets.
- The live avatar remains behind your presenter passcode; it consumes credits.
- Switching text-chat voice to ElevenLabs can incur separate charges; remove the two ELEVENLABS_ entries to fall back to Fable.
- The avatar still uses LiveAvatar's independent Full-mode client brain (Alex context), not the original OpenAI client. Its transcript can feed the assessment.
- An iframe refresh may not end the LiveAvatar remote session; use Chat controls to end it before submitting feedback.
- This is untested against your private API accounts; voice, session lookup and transcript shape need real end-to-end verification.
- Eight minutes in Full mode uses approximately sixteen LiveAvatar credits at two per minute.
- Treat this as formative/educational feedback, not validated SQE2 assessment.

DEPLOY
Upload app.py from this ZIP. Preserve all other existing repository files. Add/update LIVEAVATAR_MAX_SECONDS = 480, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID in Streamlit Secrets (leave all existing keys intact). No requirements.txt change needed.
