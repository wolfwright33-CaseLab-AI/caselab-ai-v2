CaseLab AI public demo

1. Create a separate OpenAI API project and ENFORCE A HARD MONTHLY SPEND LIMIT (for example $10).
2. Create a NEW API key inside that project. Never upload .env or secrets.toml.
3. Upload app.py, caselab_reports.py, requirements.txt, image assets, and .gitignore to a PRIVATE GitHub repository.
4. On share.streamlit.io select Create app, choose that repository and app.py.
5. In Advanced settings > Secrets enter:
   OPENAI_API_KEY = "YOUR_NEW_PROJECT_KEY"
6. Start as a private app; test all three stages; only make public after checking spend limits.

Session restrictions: 2 meetings, 12 student messages each, 5 requested voice clips, 650 chars per message, 2 feedback reports.
These are NOT tamper-proof visitor/IP rate limits. Streamlit session resets on reconnect and users can open other browsers. OpenAI's enforced project hard spending limit is mandatory. For robust per-visitor quotas, add a persistent backend/database/identity or CAPTCHA before widespread promotion.

Public demo v1.2: Alex voice is generated automatically and cached. Input colour CSS restored. API project hard spending limit must remain enforced.
