CaseLab v1.5.1 - secure preview

WHY
- Keeps the existing original CaseLab chatbot / TTS / feedback intact.
- LiveAvatar FULL-mode conversation remains separate and is NOT captured for CaseLab scoring.
- Protects credit-consuming avatar sessions behind a presenter access code.
- Your browser is authorised for avatar sessions only after supplying the code. Do not post the code on LinkedIn.

LOCAL RUN
1. Create .streamlit/secrets.toml based on LIVEAVATAR_SECRETS_EXAMPLE.toml.
2. Supply your REAL, working OPENAI_API_KEY (not the placeholder), LIVEAVATAR_API_KEY, avatar, context, Archer voice IDs.
3. Choose your own secret LIVEAVATAR_PREVIEW_PASSCODE.
4. python -m pip install -r requirements.txt
5. python -m streamlit run app.py

ONLINE UPDATE
Upload app.py, image files if modified, and requirements.txt to your existing private GitHub repo.
In Streamlit Community Cloud -> app -> Settings -> Secrets add all the above settings. Do NOT upload secrets.toml.
Test in incognito. Only the presenter can unlock LiveAvatar sessions; regular users can still access the normal CaseLab written interview.

WARNING
The avatar's two-minute free-tier limit remains unchanged. Full-mode avatar responses are not fed to the CaseLab assessment engine. Voice overrides may affect perceived lip sync; compare with default voice to isolate.
