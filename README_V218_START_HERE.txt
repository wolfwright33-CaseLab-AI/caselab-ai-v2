CaseLab AI v2.18 — hosted LiveAvatar review polish

Local start (two VS Code terminals):
1. Copy your existing private .env into the folder containing server.py. Never publish it.
2. Backend: python -m pip install -r requirements_v2.txt
   python -m uvicorn server:app --host 127.0.0.1 --port 8765
3. Frontend: cd live-client
   npm.cmd install
   npm.cmd run dev
4. Open the exact localhost URL Vite displays.

In Stage 4: conduct the interview, end the call in the LiveAvatar panel, use its top-right Transcript feature to COPY the dialogue, then choose End consultation & continue.
In Stage 5: choose Import copied transcript. It normalises LiveAvatar A/U speaker labels. Click Generate my practice review, then Download branded PDF.

IMPORTANT: A cross-origin hosted iframe cannot grant CaseLab direct access to its transcript or microphone. Automatic capture is NOT implemented; one-click clipboard import is the supported alternative until FULL SDK is implemented and tested.
The LiveAvatar transcript's own copy control belongs to the third-party iframe. We cannot repair that internal button from CaseLab; if it fails, select and copy its text manually.

For public hosting use the included Dockerfile on a Docker-capable host, keeping .env private. Do not overwrite the existing Streamlit app; it is a different frontend.
