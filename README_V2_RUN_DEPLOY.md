# CaseLab AI — connected development build

## STATUS
Real LiveAvatar token endpoint, SDK push-to-talk, Full Mode transcript retrieval, OpenAI formative assessment and mobile UI are coded. They have **not** been exercised against your paid credentials and have **not** been deployed. Do not overwrite your existing Streamlit site yet.

## Local test (Windows / VS Code)
1. Create `.env` next to `server.py` by copying `.env.example`; populate API keys, avatar pose UUID, your existing Alex context and Archer voice LiveAvatar IDs, and a private demo access code. **Never push .env to GitHub.**
2. Terminal 1 in project root: `python -m pip install -r requirements_v2.txt` then `python -m uvicorn server:app --reload --port 8000`.
3. Terminal 2: `cd live-client`; `npm.cmd install`; `npm.cmd run dev`.
4. Open `http://localhost:5173`, complete stages 1–3, enter private code at stage 4, Start consultation, hold/release push-to-talk, End, Generate AI Feedback.
5. If import/build fails: send the exact terminal error. SDK package is installed with `latest`, rather than an invented pinned version.

## Hosting
This is a **React + FastAPI** app. Streamlit Community Cloud cannot run the FastAPI server alongside the built-in Streamlit server as a supported public service. Recommended deployment for this React version is **Render Web Service via Docker** or equivalent Python container hosting. Upload folder to a **new private GitHub repo**, and on Render create a Docker web service pointing to it; set environment secrets for values in `.env.example`. Publish as a separate preview URL first. Keep `caselab-ai-demo.streamlit.app` untouched until tested. The previous Streamlit `app.py` is retained as reference only.

## Security and spending
This is a password-protected demo endpoint with an in-memory session cap, **not production authentication**. The passcode is transmitted to the server, and keys stay server-side. On Render, memory resets on restart. Turn off the publicly reachable instance or use a trusted external auth proxy before opening it widely. Avoid real learner data until proper authentication/storage/security is implemented. Session duration must be within your paid LiveAvatar tier. Only actual LiveAvatar use confirms voice quality, lip sync and transcript availability.

## Known limitations
- Full Mode transcript endpoint may take time to populate after termination; retry Generate AI feedback.
- Download is JSON; the prior branded PDF exporter is not yet migrated to this React backend.
- The OpenAI summary relies on transcript fidelity and is NOT an official SQE grade.
- Production deployment needs full end-to-end testing and an external durable session store/rate limiter.
- CaseLab stage logic is preserved, along with logo and courthouse artwork.
