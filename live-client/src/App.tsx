import { useEffect, useRef, useState } from 'react';
import logoImage from './assets/caselab_logo_user.png';
import courthouseImage from './assets/legal_hero_courthouse.png';
import alexImage from './assets/alex_morgan_portrait.png';
import './App.css';
import LiveClient from './LiveClient';

type Stage = 'identity' | 'scenarios' | 'briefing' | 'consultation' | 'review';
type Learner = { first: string; last: string; email: string };
const sarahGoals = ['Establish trust and show empathy in a bereavement conversation', 'Clarify the will, executors, beneficiaries and estate assets', 'Explore any potential family disputes with sensitivity', 'Summarise the facts and explain appropriate next steps without premature advice'];
const alexGoals = ['Build rapport and understand the client’s priorities', 'Use open questions before narrowing into focused enquiries', 'Identify the relevant facts, missing documents and concerns', 'Summarise what you have heard and close without premature legal advice'];
const stages: {key: Stage; title: string}[] = [{key:'identity',title:'Your details'},{key:'scenarios',title:'Choose a client'},{key:'briefing',title:'Case briefing'},{key:'consultation',title:'Live interview'},{key:'review',title:'Your feedback'}];
function App() {
  const tabsRef = useRef<HTMLElement>(null);
  const [learner, setLearner] = useState<Learner>({first:'', last:'', email:''});
  const [stage, setStage] = useState<Stage>('identity');
  const [highest, setHighest] = useState(0);
  const [scenario, setScenario] = useState<'alex'|'sarah'>('alex');
  const [briefRead, setBriefRead] = useState(false);
  const [permission, setPermission] = useState(false);
  const [sarahEnabled,setSarahEnabled] = useState(false);
  useEffect(()=>{fetch('/api/scenarios').then(r=>r.json()).then(x=>setSarahEnabled(Boolean(x.sarah))).catch(()=>{});},[]);
  const [consultationEnded, setConsultationEnded] = useState(false);
  const [feedbackTranscript, setFeedbackTranscript] = useState('');
  const [reviewPasscode, setReviewPasscode] = useState('');
  const [clipboardStatus, setClipboardStatus] = useState('');
  const [feedback, setFeedback] = useState<any>(null);
  const [reviewError,setReviewError] = useState('');
  const [reviewBusy,setReviewBusy] = useState(false);
  function normaliseTranscript(text:string){
    const lines=text.replace(/\r/g,'').split('\n');
    let speaker = '';
    const cleaned:string[] = [];
    for (const raw of lines){
      const line=raw.trim();
      if (!line || /^transcript$/i.test(line) || /^\d{1,2}:\d{2}(?::\d{2})?$/.test(line)) continue;
      const heading=line.match(/^(A|U|ALEX|TRAINEE|USER|CLIENT)(?:\s*[:：-]\s*(.*))?$/i);
      if (heading){
        speaker=/^(A|ALEX|CLIENT)$/i.test(heading[1])?'ALEX':'TRAINEE';
        if (heading[2]) cleaned.push(`${speaker}: ${heading[2]}`);
        continue;
      }
      const inline=line.match(/^(A|U|ALEX|TRAINEE|USER|CLIENT)\s*[:：-]\s*(.+)$/i);
      if (inline){
        speaker=/^(A|ALEX|CLIENT)$/i.test(inline[1])?'ALEX':'TRAINEE';
        cleaned.push(`${speaker}: ${inline[2]}`);
      } else if (speaker){
        cleaned.push(line);
      } else {
        cleaned.push(line);
      }
    }
    return cleaned.join('\n').trim();
  }
  async function importCopiedTranscript(){
    setClipboardStatus('');setReviewError('');
    try{
      if(!navigator.clipboard?.readText)throw new Error('Clipboard access is unavailable in this browser. Paste the transcript into the box instead.');
      const text=await navigator.clipboard.readText();
      if(!text.trim())throw new Error('Clipboard is empty. Open Transcript in the client window and copy the conversation first.');
      const formatted=normaliseTranscript(text);
      if(formatted.length<100)throw new Error('The imported text is too short for a useful review. Copy the full conversation or paste it manually.');
      setFeedbackTranscript(formatted);
      setClipboardStatus('Transcript imported. Ready for your practice review.');
    }catch(e){setReviewError(e instanceof Error?e.message:'Clipboard permission was blocked. Paste into the box instead.');}
  }
  async function downloadReport(){
    if(!feedback || !reviewPasscode)return;
    setReviewError('');
    try{
      const response=await fetch('/api/live/report-pdf',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({demo_passcode:reviewPasscode,learner:displayName,feedback:feedback.feedback,transcript_text:feedback.transcript_text||feedbackTranscript,scenario})});
      if(!response.ok){const payload=await response.json().catch(()=>({}));throw new Error(payload.detail||'Could not prepare PDF.');}
      const blob=await response.blob();const url=URL.createObjectURL(blob);const anchor=document.createElement('a');anchor.href=url;anchor.download=`CaseLab_AI_${displayName.replace(/[^a-z0-9]+/gi,'_')||'Learner'}_Review.pdf`;document.body.appendChild(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    }catch(e){setReviewError(e instanceof Error?e.message:'PDF download failed');}
  }
  async function makeFeedback(){
    if(!feedbackTranscript.trim() || !reviewPasscode)return;
    setReviewBusy(true);setReviewError('');
    try{
      const r=await fetch('/api/live/transcript-review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({demo_passcode:reviewPasscode,transcript_text:normaliseTranscript(feedbackTranscript),first_name:learner.first,last_name:learner.last,scenario})});
      const j=await r.json();if(!r.ok)throw new Error(j.detail||'Feedback failed');
      setFeedback(j);setFeedbackTranscript(normaliseTranscript(feedbackTranscript));
    }catch(e){setReviewError(e instanceof Error?e.message:String(e));}finally{setReviewBusy(false);}
  }
  const valid = learner.first.trim().length>0 && learner.last.trim().length>0 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(learner.email.trim());
  const go = (step:Stage) => {const index=stages.findIndex(x=>x.key===step); setHighest(h=>Math.max(h,index)); setStage(step);};
  useEffect(() => {
    // On narrow viewports only, centre the active stage in its own horizontal strip.
    // Do not scroll the document vertically or alter desktop behaviour.
    const tabs = tabsRef.current;
    if (!tabs || !window.matchMedia('(max-width: 760px)').matches) return;
    const active = tabs.querySelector<HTMLButtonElement>('button[aria-current="step"]');
    if (!active) return;
    const tabBox = tabs.getBoundingClientRect();
    const activeBox = active.getBoundingClientRect();
    const destination = tabs.scrollLeft + (activeBox.left - tabBox.left) - (tabs.clientWidth - activeBox.width) / 2;
    tabs.scrollTo({ left: Math.max(0, destination), behavior: 'smooth' });
  }, [stage]);
  const displayName = `${learner.first.trim()} ${learner.last.trim()}`.trim();
  return <main className="page">
    {stage==='identity' && <header className="masthead"><img src={logoImage} alt="CaseLab AI — Legal Skills, Intelligent Practice" /><div className="byline"><span>Developed by</span><strong>Wolf Wright</strong></div></header>}
    {stage==='identity' && <section className="hero"><img className="hero-art" src={courthouseImage} alt="" aria-hidden="true" /><div className="hero-content"><h1>Realistic clients.<br/>Real conversations.<br/>Sharper legal judgement.</h1><p>An AI-powered client meeting simulation for developing professional communication, fact-finding and legal practice skills.</p></div></section>}
    <nav ref={tabsRef} className="steps" aria-label="Learning journey">{stages.map((step,i)=><button key={step.key} className={stage===step.key?'current':''} disabled={i>highest} onClick={()=>go(step.key)} aria-current={stage===step.key?'step':undefined}><span className="step-num">{String(i+1).padStart(2,'0')}</span><span>{step.title}</span>{i<highest&&<span aria-label="completed">✓</span>}</button>)}</nav>
    <div className="stage-transition" key={stage}>
    {stage==='identity' && <section className="section panel"><div className="intro"><div><span className="eyebrow">01 / LEARNER ACCESS</span><h2>Before we begin.</h2><p>Enter your details so your practice review can be personalised to you.</p></div><span className="annotation">SSO-STYLE DEMO</span></div><div className="notice"><strong>Prototype sign-in — not real SSO.</strong> This screen does not verify your identity or connect to a university account. Don't enter sensitive personal information. Details stay in this browser session and are not submitted by this screen.</div><form className="identity-form" onSubmit={e=>{e.preventDefault();if(valid)go('scenarios');}}><label>First name<input required value={learner.first} autoComplete="given-name" onChange={e=>setLearner({...learner,first:e.target.value})} placeholder="First name" /></label><label>Last name<input required value={learner.last} autoComplete="family-name" onChange={e=>setLearner({...learner,last:e.target.value})} placeholder="Last name" /></label><label className="email">Email address<input required type="email" value={learner.email} autoComplete="email" onChange={e=>setLearner({...learner,email:e.target.value})} placeholder="you@example.com" /></label><button className="primary" disabled={!valid}>Continue to scenarios <span>→</span></button></form></section>}
    {stage==='scenarios' && <section className="section"><div className="intro"><div><span className="eyebrow">02 / CLIENT LIBRARY</span><h2>Choose your client.</h2><p>Welcome, {learner.first.trim()}. Select a legal practice scenario to explore.</p></div></div><div className="scenario-grid"><article className={`scenario-card ${scenario==='alex'?'selected':''}`}><div className="portrait"><img src={alexImage} alt="Portrait of the simulated client Alex Morgan"/></div><div className="scenario-body"><span className="eyebrow">SCENARIO 01 · PROPERTY PRACTICE</span><h3>Alex Morgan</h3><p>A buyer concerned about a rear extension, missing building-regulations documentation and pressure to exchange contracts.</p><button className="primary" onClick={()=>{setScenario('alex');setBriefRead(false);go('briefing')}}>Select Alex <span>→</span></button></div></article></div></section>}
    {stage==='briefing' && <section className="section"><div className="intro"><div><span className="eyebrow">03 / {scenario==='alex'?'SCENARIO 01 · PROPERTY PRACTICE':'SCENARIO 02 · WILLS & PROBATE'}</span><h2>Your client briefing.</h2><p>Review the matter and your interviewing objectives before you meet {scenario==='alex'?'Alex':'Sarah'}.</p></div></div><div className="brief-grid"><div className="panel"><span className="eyebrow">CLIENT PROFILE</span><div className="brief-profile-image">{scenario==='alex'?<img className="brief-photo" src={alexImage} alt="Alex Morgan"/>:<div className="sarah-initials" aria-label="Sarah Bennett avatar portrait not configured">SB</div>}</div><h3>{scenario==='alex'?'Alex Morgan':'Sarah Bennett'}</h3><p>{scenario==='alex'?'Residential property purchaser · York':'Wills & probate · bereavement consultation'}</p></div><div className="panel"><span className="eyebrow">SUPERVISING SOLICITOR’S BRIEFING</span><h3>{scenario==='alex'?'Residential property purchase':'Estate administration and a disputed will'}</h3><p>{scenario==='alex'?'Alex has requested an urgent meeting after discovering a potential issue during the conveyancing process.':'Sarah has recently lost her father and is unsure whether his will reflects his wishes. She needs help understanding the estate administration process and possible family disagreements.'}</p><p><strong>Your remit:</strong> establish the relevant facts, explore the client’s concerns, identify missing evidence and consider appropriate next steps — without offering unsupported assurances.</p><span className="eyebrow">SQE2-STYLE INTERVIEWING SKILLS</span><ul>{(scenario==='alex'?alexGoals:sarahGoals).map(g=><li key={g}>{g}</li>)}</ul><p className="disclaimer">Formative practice aligned to client-interviewing skills. This is not an official SRA or University of Law SQE assessment.</p><label className="confirm"><input type="checkbox" checked={briefRead} onChange={e=>setBriefRead(e.target.checked)}/> I've reviewed the briefing and understand my objectives.</label><button className="primary" disabled={!briefRead} onClick={()=>go('consultation')}>Proceed to consultation <span>→</span></button></div></div></section>}
    {stage==='consultation' && <section className="section"><div className="intro"><div><span className="eyebrow">04 / LIVE CLIENT CONSULTATION</span><h2>Meet {scenario==='alex'?'Alex':'Sarah'}, face to face.</h2><p>Use the microphone controls inside the LiveAvatar window to question your client. When finished, end the conversation to continue.</p></div></div><LiveClient scenario={scenario} onPasscode={setReviewPasscode} onEnded={()=>{setConsultationEnded(true);go('review');}}/></section>}
    {stage==='review' && <section className="section panel assessment-page">
      <span className="eyebrow">05 / PERSONALISED PRACTICE REVIEW</span>
      <h2>Your practice review.</h2>
      <p className="review-greeting">Prepared for <strong>{displayName}</strong> · {scenario==='alex'?'Property practice':'Wills & probate'} / client interviewing</p>
      {!feedback ? <>
        <div className="review-steps"><span className="review-step-number">01</span><div><strong>Bring in your conversation</strong><p>In your client’s video, open the <strong>Transcript</strong> icon (top-right) and use its copy button. Then select <strong>Import copied transcript</strong> below. We use your actual questions and the client’s answers to identify strengths and development areas.</p></div></div>
        <div className="review-actions"><button className="primary" onClick={()=>void importCopiedTranscript()}>Import copied transcript <span>↓</span></button><span className="review-hint">If import fails: click the transcript box and press Ctrl+V.</span></div>
        {clipboardStatus&&<p className="review-success" role="status">{clipboardStatus}</p>}
        <label className="review-transcript-label">Interview transcript<textarea value={feedbackTranscript} onChange={e=>{setFeedbackTranscript(e.target.value);setClipboardStatus('');}} placeholder={'CLIENT: Tell me what brought you in today…\nTRAINEE: Could you explain the main concern?'} rows={10} /></label>
        <div className="review-steps"><span className="review-step-number">02</span><div><strong>Generate your feedback</strong><p>Review the transcript, then generate a personalised assessment of your interviewing skills. If importing is blocked by browser clipboard permissions, click the transcript box and press Ctrl+V to paste.</p></div></div>
        <button className="primary review-generate" disabled={reviewBusy||feedbackTranscript.trim().length<100||!reviewPasscode} onClick={()=>void makeFeedback()}>{reviewBusy?'Analysing your interview…':'Generate my practice review →'}</button>
        {reviewError&&<p role="alert" className="live-error">{reviewError}</p>}
      </> : <>
        <div className="review-summary"><div><span className="eyebrow">YOUR PERFORMANCE AT A GLANCE</span><h3>What went well. What comes next.</h3><p>{feedback.feedback?.overview}</p></div><div className="review-summary-count"><strong>{(feedback.feedback?.criteria||[]).length}</strong><span>Skills reviewed</span></div></div>
        <div className="rag-legend"><span><i className="rag-dot strong"/> Demonstrated</span><span><i className="rag-dot developing"/> Developing</span><span><i className="rag-dot not-observed"/> Not yet observed</span></div>
        <div className="rag-grid">{(feedback.feedback?.criteria||[]).map((x:any,i:number)=>{const rawTone=String(x.outcome||'').toLowerCase().replace(/[- ]/g,'_');const tone=['strong','developing','not_observed'].includes(rawTone)?rawTone:'not_observed';return <article className={`rag-card ${tone}`} key={i}><div className="rag-card-top"><span className="rag-index">{String(i+1).padStart(2,'0')}</span><span className={`rag-pill ${tone}`}>{tone==='strong'?'Demonstrated':tone==='developing'?'Developing':'Not observed'}</span></div><h3>{x.criterion}</h3><p>{x.evidence||'No supporting evidence in the supplied conversation.'}</p></article>})}</div>
        <div className="review-columns"><section className="review-note"><span className="eyebrow">STRENGTHS</span><h3>Keep building on these.</h3><ul>{(feedback.feedback?.strengths||[]).map((x:string,i:number)=><li key={i}>{x}</li>)}</ul></section><section className="review-note"><span className="eyebrow">DEVELOPMENT PRIORITIES</span><h3>Your next steps.</h3><ul>{(feedback.feedback?.development_points||[]).map((x:string,i:number)=><li key={i}>{x}</li>)}</ul></section></div>
        <details className="review-details"><summary>Read the interview transcript</summary><pre>{feedback.transcript_text||feedbackTranscript}</pre></details>
        <div className="review-downloads"><button className="primary" onClick={()=>void downloadReport()}>Download branded PDF report ↓</button><button className="outline" onClick={()=>window.print()}>Print this review</button><button className="outline" onClick={()=>{setFeedback(null);setReviewError('');}}>Review a different transcript</button></div>
        {reviewError&&<p role="alert" className="live-error">{reviewError}</p>}
      </>}
      <button className="outline review-return" onClick={()=>go('scenarios')}>Return to scenarios</button>
    </section>}
    </div>
    <footer className={`footer ${stage!=='identity'?'footer-branded':''}`}>{stage!=='identity' ? <div className="footer-identity"><img src={logoImage} alt="CaseLab AI"/><span>Developed by <strong>Wolf Wright</strong></span></div> : <span>CASELAB AI · DEVELOPED BY WOLF WRIGHT</span>}</footer>
  </main>;
}
export default App;
