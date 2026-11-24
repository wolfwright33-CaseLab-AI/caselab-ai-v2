"""CaseLab v2 API. Run with: python -m uvicorn server:app --reload --port 8000"""
import os, re, time, secrets, io, html, json
from pathlib import Path
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable

load_dotenv()
BASE = Path(__file__).resolve().parent
app = FastAPI(title="CaseLab AI v2")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "caselab"}

@app.get("/api/scenarios")
def scenarios():
    return {"alex": bool(os.getenv("LIVEAVATAR_API_KEY") and os.getenv("LIVEAVATAR_AVATAR_ID") and os.getenv("LIVEAVATAR_CONTEXT_ID")), "sarah": bool(os.getenv("LIVEAVATAR_API_KEY") and os.getenv("SARAH_AVATAR_ID") and os.getenv("SARAH_CONTEXT_ID"))}

API = "https://api.liveavatar.com/v1"
# Tokens are not embedded in React; the LiveAvatar API key stays on the server.
# Single-worker, in-memory session ownership; demo only, NOT public production auth.
issued = {}
MAX_SESSIONS = int(os.getenv("MAX_DEMO_SESSIONS", "3"))
count = 0

class StartRequest(BaseModel):
    demo_passcode: str = Field(min_length=1, max_length=200)
    scenario: str = Field(default="alex", pattern="^(alex|sarah)$")

class ReviewRequest(BaseModel):
    session_id: str = Field(min_length=20, max_length=100)
    access_token: str = Field(min_length=20, max_length=200)
    first_name: str = Field(max_length=60)
    last_name: str = Field(max_length=60)

async def liveavatar_request(method, path, key, *, payload=None):
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.request(method, API + path, headers={"X-API-KEY": key, "accept": "application/json"}, json=payload)
    if res.status_code >= 400:
        raise HTTPException(502, f"LiveAvatar {res.status_code}: {res.text[:350]}")
    data = res.json()
    if data.get("code") not in (100, 0, None):
        raise HTTPException(502, f"LiveAvatar: {str(data.get('message'))[:250]}")
    return data.get("data") or {}

@app.post("/api/live/start")
async def start(data: StartRequest):
    global count
    password = os.getenv("CASELAB_DEMO_PASSCODE", "")
    if not password or not secrets.compare_digest(data.demo_passcode, password):
        raise HTTPException(403, "Incorrect demo access code")
    if count >= MAX_SESSIONS:
        raise HTTPException(429, "Demo session cap reached; restart server or change your cap")
    key = os.getenv("LIVEAVATAR_API_KEY", "")
    avatar = os.getenv("LIVEAVATAR_AVATAR_ID", "")
    context = os.getenv("LIVEAVATAR_CONTEXT_ID", "")
    voice = os.getenv("LIVEAVATAR_VOICE_ID", "")
    if not key or not avatar:
        raise HTTPException(503, "Configure LIVEAVATAR_API_KEY and LIVEAVATAR_AVATAR_ID in .env")
    persona = {}
    if context: persona["context_id"] = context
    if voice: persona["voice_id"] = voice
    duration = max(60, min(int(os.getenv("LIVEAVATAR_MAX_SECONDS", "600")), 1200))
    body = {"mode":"FULL", "avatar_id":avatar, "is_sandbox":False, "max_session_duration":duration,
            "interactivity_type":"PUSH_TO_TALK", "avatar_persona":persona}
    result = await liveavatar_request("POST", "/sessions/token", key, payload=body)
    session_id, token = result.get("session_id"), result.get("session_token")
    if not session_id or not token:
        raise HTTPException(502, "LiveAvatar returned no session token")
    access = secrets.token_urlsafe(32)
    issued[session_id] = (access, time.time())
    count += 1
    return {"session_id":session_id, "session_token":token, "access_token":access, "duration_seconds":duration}

@app.post("/api/live/embed")
async def hosted_embed(data: StartRequest):
    """Reuses the prior working LiveAvatar hosted embed API; no JS SDK needed."""
    global count
    password = os.getenv("CASELAB_DEMO_PASSCODE", "")
    if not password or not secrets.compare_digest(data.demo_passcode, password):
        raise HTTPException(403, "Incorrect demo access code")
    if count >= MAX_SESSIONS:
        raise HTTPException(429, "Demo session cap reached. Restart backend only if intended.")
    key = os.getenv("LIVEAVATAR_API_KEY", "").strip()
    avatar = os.getenv("SARAH_AVATAR_ID", "").strip() if data.scenario == "sarah" else os.getenv("LIVEAVATAR_AVATAR_ID", "").strip()
    context = os.getenv("SARAH_CONTEXT_ID", "").strip() if data.scenario == "sarah" else os.getenv("LIVEAVATAR_CONTEXT_ID", "").strip()
    voice = os.getenv("SARAH_VOICE_ID", "").strip() if data.scenario == "sarah" else os.getenv("LIVEAVATAR_VOICE_ID", "").strip()
    if not (key and avatar and context):
        raise HTTPException(503, f"{data.scenario.title()} is not configured yet. Add the matching avatar and context IDs to server environment settings.")
    duration = max(30, min(int(os.getenv("LIVEAVATAR_MAX_SECONDS", "600")), 1200))
    payload = {"avatar_id":avatar, "context_id":context, "is_sandbox":False,
               "max_session_duration":duration,"orientation":"horizontal","type":"DEFAULT"}
    if voice:
        payload["voice_id"] = voice
    try:
        async with httpx.AsyncClient(timeout=35) as client:
            res=await client.post("https://api.liveavatar.com/v2/embeddings",json=payload,
                                  headers={"X-API-KEY":key,"Content-Type":"application/json"})
        if res.status_code >= 400:
            raise HTTPException(502, f"LiveAvatar embed {res.status_code}: {res.text[:400]}")
        reply=res.json()
        url=(reply.get("data") or {}).get("url", "")
        if not isinstance(url,str) or not url.startswith("https://embed.liveavatar.com/"):
            raise HTTPException(502, f"LiveAvatar did not return an embed URL: {str(reply.get('message'))[:200]}")
        count += 1
        return {"url":url,"duration_seconds":duration}
    except httpx.RequestError as exc:
        raise HTTPException(502, f"LiveAvatar embed connection error: {type(exc).__name__}") from exc

@app.post("/api/live/review")
async def review(req: ReviewRequest):
    entry = issued.get(req.session_id)
    if not entry or not secrets.compare_digest(entry[0], req.access_token):
        raise HTTPException(403, "Unknown or expired session")
    if time.time() - entry[1] > 7200:
        raise HTTPException(403, "Session expired")
    la_key = os.getenv("LIVEAVATAR_API_KEY", "")
    raw = await liveavatar_request("GET", f"/sessions/{req.session_id}/transcript", la_key)
    lines = raw.get("transcript_data") or []
    transcript = [{"speaker":x.get("role"), "text":x.get("transcript", "")} for x in lines if x.get("role") in ("user", "avatar") and x.get("transcript")]
    if len([x for x in transcript if x["speaker"] == "user"]) < 2:
        raise HTTPException(422, "Not enough recorded learner questions. Transcript may still be processing; retry shortly")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(503, "OPENAI_API_KEY missing on backend")
    prompt = """You are an evidence-led formative assessor for a simulated SQE2-style client interview, not an official SRA examiner.
Scenario: Alex Morgan is buying a house and is worried about a rear extension, absent building-regulations certificate and seller pressure to exchange. Assess ONLY the learner's utterances, using Alex's responses for context. Do not invent evidence. Criteria: rapport and empathy; open/focused questioning; fact finding incl documentation and timelines; recognising risk without premature legal advice; summary and closing.
Return concise JSON with keys: overview (string), strengths (array of strings), development_points (array of strings), criteria (array of objects with criterion, outcome (strong/developing/not_observed), evidence (string)). Use quotes or concrete paraphrases from the transcript. Say 'not observed' when the relevant skill is absent. Avoid an official grade or pass/fail.
"""
    conversation = "\n".join(f"{x['speaker'].upper()}: {x['text']}" for x in transcript)[:16000]
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    try:
        response = client.chat.completions.create(model=os.getenv("OPENAI_FEEDBACK_MODEL", "gpt-4o-mini"), response_format={"type":"json_object"}, messages=[{"role":"system","content":prompt},{"role":"user","content":conversation}])
        import json
        feedback = json.loads(response.choices[0].message.content or "{}")
    except Exception as exc:
        raise HTTPException(502, f"Feedback generation failed: {type(exc).__name__}")
    return {"learner":(req.first_name + " " + req.last_name).strip(), "transcript":transcript, "feedback":feedback}


class TranscriptReviewRequest(BaseModel):
    scenario: str = Field(default="alex", pattern="^(alex|sarah)$")
    demo_passcode: str = Field(min_length=1, max_length=200)
    transcript_text: str = Field(min_length=100, max_length=25000)
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)

@app.post("/api/live/transcript-review")
async def transcript_review(req: TranscriptReviewRequest):
    """Hosted embed fallback: assess an explicitly provided transcript.

    Does not claim to retrieve conversations from the cross-origin LiveAvatar iframe.
    """
    password = os.getenv("CASELAB_DEMO_PASSCODE", "")
    if not password or not secrets.compare_digest(req.demo_passcode, password):
        raise HTTPException(403, "Incorrect demo access code")
    if not os.getenv("OPENAI_API_KEY", ""):
        raise HTTPException(503, "OPENAI_API_KEY missing in backend .env")
    transcript = req.transcript_text.strip()
    if len(transcript) < 100:
        raise HTTPException(422, "Please provide a longer interview transcript")
    scenario_notes = ("The learner is interviewing Sarah Bennett, a recently bereaved client seeking advice on her late father's estate, an unclear will, estate administration and potential family disagreements. Focus on sensitive communication, fact-finding about the will, executors, assets, liabilities, beneficiaries, and next steps without making unsupported assumptions." if req.scenario == "sarah" else "The learner is interviewing Alex Morgan, a buyer concerned about a rear extension, missing building regulations approval and pressure to exchange contracts.")
    prompt = """You are a careful formative assessor of an SQE2-style client interview.
Assess only what appears in the supplied dialogue. Never invent quotes, facts, or performance.
LiveAvatar can label the client as A and the learner as U; normalise these as the selected client and Trainee. If speaker identity is unclear or the dialogue is incomplete, do not attribute statements without evidence.
Evaluate rapport/empathy, clear open and focused questions, relevant fact-finding,
identifying missing evidence and risks without premature advice, and closing/summarising.
Return a JSON object with these fields exactly:
overview (string), strengths (array of strings), development_points (array of strings),
criteria (array of objects with criterion, outcome as strong/developing/not_observed,
evidence as a string). No official SQE grade, pass or fail.
Be constructive but precise; do not invent empathy, questions, legal analysis or quoted words. Assign strong only for clear positive evidence; developing where there is partial or poor performance; not_observed for missing skills. Refer to actual observed transcript evidence only."""
    prompt += "\nScenario: " + scenario_notes
    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        result = client.chat.completions.create(
            model=os.getenv("OPENAI_FEEDBACK_MODEL", "gpt-4o-mini"),
            response_format={"type":"json_object"},
            messages=[{"role":"system","content":prompt},{"role":"user","content":transcript[:20000]}],
            timeout=50,
        )
        import json
        feedback = json.loads(result.choices[0].message.content or "{}")
    except Exception as exc:
        raise HTTPException(502, f"AI feedback failed: {type(exc).__name__}") from exc
    return {"learner": f"{req.first_name.strip()} {req.last_name.strip()}",
            "source":"Learner-supplied transcript — not automatically captured from hosted LiveAvatar",
            "transcript_text": transcript, "feedback": feedback}

class ReportRequest(BaseModel):
    demo_passcode: str = Field(min_length=1, max_length=200)
    learner: str = Field(min_length=1, max_length=160)
    feedback: dict
    transcript_text: str = Field(default="", max_length=25000)
    scenario: str = Field(default="alex", pattern="^(alex|sarah)$")

@app.post("/api/live/report-pdf")
def report_pdf(req: ReportRequest):
    password = os.getenv("CASELAB_DEMO_PASSCODE", "")
    if not password or not secrets.compare_digest(req.demo_passcode, password):
        raise HTTPException(403, "Incorrect demo access code")
    f = req.feedback
    if not isinstance(f.get("criteria"), list) or not isinstance(f.get("overview"), str):
        raise HTTPException(422, "No complete practice assessment supplied")
    blue = colors.HexColor("#142d43")
    blue_light = colors.HexColor("#4b687a")
    teal = colors.HexColor("#008aa4")
    light = colors.HexColor("#f4f6f5")
    palette = {
        "strong": (colors.HexColor("#23734a"), colors.HexColor("#e5f3e9"), "DEMONSTRATED"),
        "developing": (colors.HexColor("#9d6c1d"), colors.HexColor("#fff2d8"), "DEVELOPING"),
        "not_observed": (colors.HexColor("#a14c45"), colors.HexColor("#f6e5e2"), "NOT OBSERVED"),
    }
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm, title=f"CaseLab AI — {req.learner} — Practice Review", author="CaseLab AI")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CLTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=26, leading=31, textColor=blue, spaceAfter=10))
    styles.add(ParagraphStyle(name="CLSection", fontName="Helvetica-Bold", fontSize=13, leading=18, textColor=blue, spaceBefore=17, spaceAfter=8))
    styles.add(ParagraphStyle(name="CLBody", fontName="Helvetica", fontSize=10.5, leading=16, textColor=blue_light, spaceAfter=8))
    styles.add(ParagraphStyle(name="CLSmall", fontName="Helvetica", fontSize=9, leading=13, textColor=blue_light, spaceAfter=4))
    styles.add(ParagraphStyle(name="CLBadge", fontName="Helvetica-Bold", fontSize=8, leading=12, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="CLCardTitle", fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=blue, spaceAfter=6))
    def safe(value): return html.escape(str(value or ""))
    def para(value, name="CLBody"): return Paragraph(safe(value).replace("\n", "<br/>"), styles[name])
    story=[]
    logo = BASE / "caselab_logo_user.png"
    if logo.is_file():
        from reportlab.platypus import Image
        from PIL import Image as PILImage
        with PILImage.open(logo) as im:
            w,h=im.size
        story.append(Image(str(logo), width=64*mm, height=64*mm*h/w))
        story.append(Spacer(1,5*mm))
    else:
        story.append(para("CASELAB AI", "CLSection"))
    story.append(Paragraph("Your practice review.",styles["CLTitle"]))
    story.append(para(f"Prepared for {req.learner}   |   {'Wills & probate' if req.scenario == 'sarah' else 'Property practice'} · client interviewing", "CLSmall"))
    story.append(HRFlowable(width="100%",thickness=1,color=teal,spaceBefore=8,spaceAfter=15))
    story.append(para("PERFORMANCE OVERVIEW","CLSection"))
    story.append(para(f.get("overview","")))
    story.append(para("INTERVIEWING CRITERIA","CLSection"))
    for index,item in enumerate(f.get("criteria",[])[:16],1):
        outcome=str(item.get("outcome","not_observed")).lower()
        tone,bg,label=palette.get(outcome,palette["not_observed"])
        badge=Table([[Paragraph(label,styles["CLBadge"])]],colWidths=[33*mm])
        badge.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("TEXTCOLOR",(0,0),(-1,-1),tone),("BOX",(0,0),(-1,-1),0.5,bg),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        block=[Paragraph(f"{index:02d}  {safe(item.get('criterion','Skill'))}",styles["CLCardTitle"]),badge,Spacer(1,6),para(item.get("evidence", "No observed transcript evidence"),"CLSmall"),Spacer(1,9)]
        story.append(KeepTogether(block))
    story.append(para("STRENGTHS","CLSection"))
    for point in f.get("strengths",[])[:8]: story.append(para("•  "+str(point)))
    story.append(para("NEXT DEVELOPMENT PRIORITIES","CLSection"))
    for point in f.get("development_points",[])[:8]: story.append(para("•  "+str(point)))
    if req.transcript_text.strip():
        story.append(para("INTERVIEW TRANSCRIPT","CLSection"))
        for line in req.transcript_text.strip().splitlines():
            if line.strip(): story.append(para(line[:1100],"CLSmall"))
    def footer(canvas,doc):
        canvas.saveState()
        width,_=A4
        canvas.setStrokeColor(colors.HexColor("#dbdfdf"));canvas.line(18*mm,14*mm,width-18*mm,14*mm)
        canvas.setFont("Helvetica",8);canvas.setFillColor(blue_light)
        canvas.drawString(18*mm,10*mm,"CASELAB AI  ·  DEVELOPED BY WOLF WRIGHT")
        canvas.drawRightString(width-18*mm,10*mm,f"{doc.page}")
        canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    buf.seek(0)
    return StreamingResponse(buf,media_type="application/pdf",headers={"Content-Disposition":"attachment; filename=CaseLab_Practice_Review.pdf"})

build = BASE / "live-client" / "dist"
if build.exists():
    app.mount("/assets", StaticFiles(directory=str(build / "assets")), name="assets")
    @app.get("/{rest:path}")
    def frontend(rest: str):
        target = (build / rest).resolve()
        if target.is_relative_to(build.resolve()) and target.is_file(): return FileResponse(target)
        return FileResponse(build / "index.html")
else:
    @app.get("/")
    def missing_build(): return {"message":"Start React on localhost:5173 for development, or run npm run build first."}
