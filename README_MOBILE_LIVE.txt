CaseLab v1.5.2 - mobile/live preview

Changes from v1.5.1:
- Full-width LiveAvatar panel (no desktop column squeeze); internal scrolling enabled to reach Chat now on narrow screens.
- Explicit instruction for mobile microphone/separate tab fallback.
- Optional LIVEAVATAR_MAX_SECONDS secret, set 120 on Free plan and up to 1200 only if subscribed to Essential. The provider enforces plan caps.
- Existing passcode gate, chat, Fable, reports remain untouched.

This is an experimental FULL-mode embed. Spoken transcript is NOT yet connected to CaseLab feedback.
Only the presenter with the access code can start paid-credit sessions. Public site users retain the original written simulation.

To deploy: upload app.py and any changed portrait/requirements to existing private GitHub repo; set LiveAvatar settings in Streamlit Cloud -> app settings -> Secrets, preserving OPENAI_API_KEY. NEVER upload secrets.toml.
Test in incognito and on phone before announcing.
