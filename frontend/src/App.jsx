import { useEffect, useState } from 'react';
import { BriefcaseBusiness, Search, MapPin, Sparkles, ExternalLink, RefreshCw } from 'lucide-react';

const API = 'http://127.0.0.1:8000/api/v1';
export default function App() {
  const [jobs, setJobs] = useState([]);
  const [keywords, setKeywords] = useState('Python, Selenium, Data Analyst');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  async function loadJobs() {
    setLoading(true); setError('');
    try { const response = await fetch(`${API}/jobs`); if (!response.ok) throw new Error('Backend request failed'); const data = await response.json(); setJobs(data.items || []); }
    catch (e) { setError('Cannot connect to backend. Start FastAPI on port 8000.'); }
    finally { setLoading(false); }
  }
  async function matchJobs(e) {
    e.preventDefault(); setLoading(true); setError('');
    try { const response = await fetch(`${API}/jobs/match`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({keywords:keywords.split(',').map(x=>x.trim()).filter(Boolean), remote_only:true})}); if (!response.ok) throw new Error(); const data = await response.json(); setJobs(data.items || []); }
    catch { setError('Could not match jobs. Check that the backend is running.'); }
    finally { setLoading(false); }
  }
  useEffect(() => { loadJobs(); }, []);
  return <main className="shell">
    <nav className="nav"><div className="brand"><span className="brand-icon"><BriefcaseBusiness size={20}/></span> JobPilot <b>AI</b></div><span className="pill">MVP · Demo mode</span></nav>
    <section className="hero"><div className="eyebrow"><Sparkles size={15}/> YOUR SMART JOB SEARCH ASSISTANT</div><h1>Find the right job.<br/><em>Make your next move.</em></h1><p>Discover relevant roles, compare them with your skills, and keep every application organized in one place.</p>
    <form className="searchbox" onSubmit={matchJobs}><Search size={19}/><input value={keywords} onChange={e=>setKeywords(e.target.value)} placeholder="Enter skills or job titles"/><button disabled={loading}>{loading?'Searching...':'Find matches'}</button></form>
    </section>
    <section className="results-head"><div><div className="eyebrow">OPPORTUNITIES</div><h2>Recommended jobs</h2></div><button className="refresh" onClick={loadJobs} disabled={loading}><RefreshCw size={16}/> Refresh</button></section>
    {error && <div className="error">{error}</div>}
    <section className="jobs">{jobs.map(job=><article className="job" key={job.id}><div className="job-top"><div className="company-icon"><BriefcaseBusiness size={20}/></div><span className="score">{job.match_score ?? '—'}{job.match_score !== undefined ? '% match' : 'DEMO'}</span></div><h3>{job.title}</h3><div className="company">{job.company}</div><div className="location"><MapPin size={14}/>{job.location}</div><p>{job.description}</p><a href={job.url} target="_blank" rel="noreferrer">View opportunity <ExternalLink size={14}/></a></article>)}</section>
    <footer>JobPilot AI · Demo listings are sample data. Live job integrations will use sources that permit access. Applications remain under your control.</footer>
  </main>;
}
