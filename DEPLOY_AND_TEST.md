# CaseLab AI — Stable deployment path

## What this release actually does
- Keeps the verified v2.18 five-stage React design and branded RAG/PDF feedback.
- Uses the **working hosted LiveAvatar iframe** for Alex.
- Includes an independent Sarah Bennett wills & probate scenario. It **unlocks only when SARAH_AVATAR_ID and SARAH_CONTEXT_ID are configured** in the backend; SARAH_VOICE_ID is optional. Set up Sarah's own scenario context in LiveAvatar before using it. The placeholder portrait is initials; provide an authorised real avatar photo before public launch.
- Transcript import is **manual**. The hosted iframe does not expose its transcript directly to CaseLab. Press the Transcript copy control and then import; if clipboard permission fails, paste into the input field with Ctrl+V.
- Automatic transcript-to-feedback requires a different, correctly tested API/SDK integration, which is NOT implemented in this build. Do not advertise automatic capture until tested.

## Local test — two PowerShell terminals from project root
Terminal A: `python -m pip install -r requirements_v2.txt` then `python -m uvicorn server:app --host 127.0.0.1 --port 8765`
Terminal B: `cd live-client`, `npm.cmd ci`, `npm.cmd run dev`
Open the URL reported by Vite. Confirm `http://127.0.0.1:8765/api/health` returns ok.

## Deployment steps
1. Create a **new private GitHub repo** containing these files; never include `.env` or secrets.
2. Render > New > Web Service > Build and deploy from Git repository > select repo.
3. Choose Docker runtime and paid starter or another non-sleep instance. Use the Dockerfile at the repository root.
4. Under Environment, supply the values in `.env.example` with your real values, as secrets. Do not paste secrets into source code.
5. Deploy. Test `/api/health`, then the staged journey, live avatar, transcript paste, feedback and PDF.
6. Test an Incognito window on a second device. Keep the old Streamlit app unchanged until the new address is verified.
7. Restrict access to the demo code and review usage regularly; the in-memory session cap resets when the service restarts and is not a robust public rate limiter.

## Important caveats
The app has a demonstration password, not real identity management or student SSO. It does not securely persist learner accounts, transcripts or assessments. Avoid sensitive personal information. This is a private demonstration build, not a university production system.
