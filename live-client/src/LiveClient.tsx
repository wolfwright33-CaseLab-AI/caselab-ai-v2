import {useState} from 'react';

type Props = { onEnded: () => void; onPasscode: (passcode: string) => void; scenario: "alex" | "sarah" };

export default function LiveClient({onEnded,onPasscode,scenario}:Props){
  const clientName=scenario === "sarah" ? "Sarah Bennett" : "Alex Morgan";
  const [pass,setPass]=useState('');
  const [busy,setBusy]=useState(false);
  const [url,setUrl]=useState('');
  const [error,setError]=useState('');
  const [duration,setDuration]=useState(600);
  const [ended,setEnded]=useState(false);
  async function start(){
    if(!pass || busy || ended)return;
    setBusy(true); setError('');
    const controller=new AbortController();
    const timeout=setTimeout(()=>controller.abort(),45000);
    try{
      const response=await fetch('/api/live/embed',{
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({demo_passcode:pass,scenario}), signal:controller.signal,
      });
      const raw=await response.text();let data:any;
      try{data=JSON.parse(raw);}catch{throw new Error('No valid response from Python API. Check the backend terminal.');}
      if(!response.ok)throw new Error(data.detail||`Backend error ${response.status}`);
      if(!data.url || !String(data.url).startsWith('https://embed.liveavatar.com/'))throw new Error('LiveAvatar returned no valid embed URL.');
      setUrl(data.url);setDuration(data.duration_seconds||600);onPasscode(pass);
    }catch(e){setError(e instanceof Error?e.message:String(e));}
    finally{clearTimeout(timeout);setBusy(false);}
  }
  function finish(){setEnded(true);setUrl('');onEnded();}
  return <div className="caselab-live">
    {!url && !ended && <div className="live-access"><label>Private demo access code <input type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder="Enter demo code" autoComplete="off" /></label><button className="primary" disabled={!pass||busy} onClick={()=>void start()}>{busy?'Connecting…':'Start consultation →'}</button></div>}
    {url ? <>
      <p className="disclaimer">Select <strong>Chat now</strong> to begin. Ask your client questions using the microphone or message box. To finish, end the call with the red button inside the video.</p>
      <div style={{width:'100%'}}><iframe title="Live consultation with the selected client" src={url} allow="microphone;camera;autoplay;fullscreen" referrerPolicy="strict-origin-when-cross-origin" style={{width:'100%',height:'min(74vh,690px)',minHeight:360,border:0,borderRadius:12,background:'#112c42'}} /></div>
      <div className="live-buttons" style={{display:'flex',gap:12,flexWrap:'wrap',marginTop:16}}>
        <a href={url} target="_blank" rel="noopener noreferrer" className="outline" style={{display:'inline-block',padding:'12px 18px',textDecoration:'none'}}>Open interview in separate tab ↗</a>
        <button className="primary" onClick={finish}>End consultation & continue →</button>
      </div>
      <p className="disclaimer">After ending your conversation, open <strong>Transcript</strong> in the top-right of the video and copy the conversation. CaseLab uses those questions and answers to create your practice review. Then select <strong>End consultation &amp; continue</strong>.</p>
    </> : !ended ? <div className="live-video" style={{minHeight:300,display:'grid',placeItems:'center',color:'white'}}>{clientName} · Ready to connect</div> : <div className="panel" style={{padding:22}}><h3>Consultation ended</h3><p>Bring your copied interview transcript to the next stage to generate your review.</p><button className="primary" onClick={onEnded}>Continue to feedback →</button></div>}
    {error&&<p className="live-error" role="alert">{error}</p>}
  </div>
}
