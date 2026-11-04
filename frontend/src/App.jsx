import { useEffect, useState } from 'react';
import { BriefcaseBusiness, Search, MapPin, Sparkles, ExternalLink, RefreshCw, UserRound, Upload, LogOut, Save, Settings2 } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';
const emptyPreferences = {
  target_roles: [], locations: [], skills: [],
  min_experience_years: '', max_experience_years: '',
  min_salary: '', max_salary: '', currency: 'INR', work_mode: 'any',
};
const splitList = (value) => value.split(',').map((item) => item.trim()).filter(Boolean);
const numberOrNull = (value) => value === '' ? null : Number(value);

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [keywords, setKeywords] = useState('Python, Selenium, Data Analyst');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [mode, setMode] = useState('register');
  const [form, setForm] = useState({ full_name: '', email: '', password: '' });
  const [token, setToken] = useState(localStorage.getItem('jobpilot_token') || '');
  const [user, setUser] = useState(null);
  const [profileName, setProfileName] = useState('');
  const [resumes, setResumes] = useState([]);
  const [applications, setApplications] = useState([]);
  const [resumeFile, setResumeFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [analyzingId, setAnalyzingId] = useState(null);
  const [preferences, setPreferences] = useState(emptyPreferences);
  const [preferenceText, setPreferenceText] = useState({ target_roles: '', locations: '', skills: '' });
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPreferences, setSavingPreferences] = useState(false);

  async function loadJobs() {
    setLoading(true); setError('');
    try {
      const response = await fetch(API + '/jobs');
      if (!response.ok) throw new Error('Could not load jobs');
      setJobs((await response.json()).items || []);
    } catch {
      setError('Cannot connect to backend. Start FastAPI on port 8000.');
    } finally { setLoading(false); }
  }

  async function matchJobs(event) {
    event.preventDefault(); setLoading(true); setError('');
    try {
      const response = await fetch(API + '/jobs/match', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keywords: splitList(keywords), remote_only: true }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not match jobs');
      setJobs(data.items || []);
    } catch (err) { setError(err.message || 'Could not match jobs.'); }
    finally { setLoading(false); }
  }

  async function loadAccount(accessToken) {
    const headers = { Authorization: 'Bearer ' + accessToken };
    const [profileResponse, resumeResponse, preferenceResponse, applicationResponse] = await Promise.all([
      fetch(API + '/profile', { headers }),
      fetch(API + '/resumes/', { headers }),
      fetch(API + '/preferences', { headers }),
      fetch(API + '/applications/', { headers }),
    ]);
    if (!profileResponse.ok) throw new Error('Session expired. Please sign in again.');
    const profile = await profileResponse.json();
    setUser(profile); setProfileName(profile.full_name || '');
    if (resumeResponse.ok) setResumes(await resumeResponse.json());
    if (applicationResponse.ok) setApplications(await applicationResponse.json());
    if (preferenceResponse.ok) {
      const saved = await preferenceResponse.json();
      const next = { ...emptyPreferences, ...saved };
      setPreferences(next);
      setPreferenceText({
        target_roles: (next.target_roles || []).join(', '),
        locations: (next.locations || []).join(', '),
        skills: (next.skills || []).join(', '),
      });
    }
  }

  useEffect(() => { loadJobs(); }, []);
  useEffect(() => {
    if (!token) {
      setUser(null); setResumes([]); setApplications([]); setPreferences(emptyPreferences);
      setPreferenceText({ target_roles: '', locations: '', skills: '' });
      return;
    }
    loadAccount(token).catch((err) => {
      localStorage.removeItem('jobpilot_token'); setToken(''); setUser(null);
      setError(err.message || 'Your session expired. Please sign in again.');
    });
  }, [token]);

  async function submitAuth(event) {
    event.preventDefault(); setError(''); setNotice('');
    const endpoint = mode === 'register' ? 'register' : 'login';
    const payload = mode === 'register' ? form : { email: form.email, password: form.password };
    try {
      const response = await fetch(API + '/auth/' + endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Authentication failed');
      localStorage.setItem('jobpilot_token', data.access_token);
      setToken(data.access_token); setUser(data.user); setNotice('You are signed in successfully.');
    } catch (err) { setError(err.message || 'Could not connect to backend.'); }
  }

  async function saveProfile(event) {
    event.preventDefault(); setSavingProfile(true); setError(''); setNotice('');
    try {
      const response = await fetch(API + '/profile', {
        method: 'PATCH',
        headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: profileName.trim() }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Profile update failed');
      setUser(data); setProfileName(data.full_name); setNotice('Profile updated successfully.');
    } catch (err) { setError(err.message || 'Profile update failed.'); }
    finally { setSavingProfile(false); }
  }

  async function savePreferences(event) {
    event.preventDefault(); setSavingPreferences(true); setError(''); setNotice('');
    const payload = {
      ...preferences,
      ...Object.fromEntries(Object.entries(preferenceText).map(([key, value]) => [key, splitList(value)])),
      min_experience_years: numberOrNull(preferences.min_experience_years),
      max_experience_years: numberOrNull(preferences.max_experience_years),
      min_salary: numberOrNull(preferences.min_salary),
      max_salary: numberOrNull(preferences.max_salary),
    };
    try {
      const response = await fetch(API + '/preferences', {
        method: 'PUT',
        headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail?.[0]?.msg || data.detail || 'Preferences update failed');
      setPreferences({ ...emptyPreferences, ...data });
      setPreferenceText({
        target_roles: (data.target_roles || []).join(', '),
        locations: (data.locations || []).join(', '),
        skills: (data.skills || []).join(', '),
      });
      setNotice('Job preferences saved successfully.');
    } catch (err) { setError(typeof err.message === 'string' ? err.message : 'Preferences update failed.'); }
    finally { setSavingPreferences(false); }
  }


  async function trackJob(job) {
    setError(''); setNotice('');
    try {
      const response = await fetch(API + '/applications/', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: 'demo', title: job.title, company: job.company,
          location: job.location || '', job_url: job.url, status: 'saved', notes: '',
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not save this job');
      setApplications((items) => [data, ...items]);
      setNotice('Job added to your application tracker.');
    } catch (err) { setError(err.message || 'Could not save this job.'); }
  }

  async function updateApplicationStatus(id, nextStatus) {
    try {
      const response = await fetch(API + '/applications/' + id, {
        method: 'PATCH',
        headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: nextStatus }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Could not update application');
      setApplications((items) => items.map((item) => item.id === id ? data : item));
      setNotice('Application status updated.');
    } catch (err) { setError(err.message || 'Could not update application.'); }
  }

  async function uploadResume(event) {
    event.preventDefault(); if (!resumeFile || !token) return;
    setError(''); setNotice('');
    const body = new FormData(); body.append('file', resumeFile);
    try {
      const response = await fetch(API + '/resumes/upload', {
        method: 'POST', headers: { Authorization: 'Bearer ' + token }, body,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Upload failed');
      setResumes((items) => [data, ...items]); setResumeFile(null); event.target.reset();
      setNotice('Resume uploaded successfully.');
    } catch (err) { setError(err.message || 'Resume upload failed.'); }
  }

  async function analyzeResume(id) {
    setAnalyzingId(id); setError(''); setNotice('');
    try {
      const response = await fetch(API + '/resumes/' + id + '/analyze', {
        method: 'POST', headers: { Authorization: 'Bearer ' + token },
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Resume analysis failed');
      setAnalysis(data); setJobs(data.matched_jobs || []);
      setNotice('Resume analyzed. Job matches are shown below.');
    } catch (err) { setError(err.message || 'Resume analysis failed.'); }
    finally { setAnalyzingId(null); }
  }

  function logout() {
    localStorage.removeItem('jobpilot_token'); setToken(''); setUser(null); setAnalysis(null); setApplications([]);
    setNotice('You have been signed out.');
  }

  return (
    <main className="shell">
      <nav className="nav">
        <div className="brand"><span className="brand-icon"><BriefcaseBusiness size={20} /></span> JobPilot <b>AI</b></div>
        <div className="nav-right">{user ? <><span className="pill">{user.full_name}</span><button className="refresh" onClick={logout}><LogOut size={15} /> Logout</button></> : <span className="pill">MVP · Demo mode</span>}</div>
      </nav>

      <section className="hero">
        <div className="eyebrow"><Sparkles size={15} /> YOUR SMART JOB SEARCH ASSISTANT</div>
        <h1>Find the right job.<br /><em>Make your next move.</em></h1>
        <p>Discover relevant roles, compare them with your skills, and keep every application organized in one place.</p>
        <form className="searchbox" onSubmit={matchJobs}>
          <Search size={19} /><input value={keywords} onChange={(event) => setKeywords(event.target.value)} placeholder="Enter skills or job titles" />
          <button disabled={loading}>{loading ? 'Searching...' : 'Find matches'}</button>
        </form>
      </section>

      {!user ? (
        <section className="account-card">
          <div className="eyebrow"><UserRound size={14} /> ACCOUNT</div>
          <h2>{mode === 'register' ? 'Create your account' : 'Welcome back'}</h2>
          <p className="muted">Register or sign in to upload and manage your resume.</p>
          <form className="auth-form" onSubmit={submitAuth}>
            {mode === 'register' && <input required minLength="2" placeholder="Full name" value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} />}
            <input required type="email" placeholder="Email address" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
            <input required minLength={mode === 'register' ? 8 : 1} type="password" placeholder="Password (minimum 8 characters)" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} />
            <button>{mode === 'register' ? 'Create account' : 'Sign in'}</button>
          </form>
          <button className="text-button" onClick={() => setMode(mode === 'register' ? 'login' : 'register')}>{mode === 'register' ? 'Already registered? Sign in' : 'New here? Create an account'}</button>
        </section>
      ) : (
        <>
          <section className="account-card">
            <div className="eyebrow"><UserRound size={14} /> YOUR PROFILE</div>
            <h2>Welcome, {user.full_name}</h2>
            <p className="muted">{user.email}</p>
            <form className="profile-form" onSubmit={saveProfile}>
              <label>Full name<input required minLength="2" maxLength="120" value={profileName} onChange={(event) => setProfileName(event.target.value)} /></label>
              <button disabled={savingProfile || !profileName.trim()}><Save size={15} /> {savingProfile ? 'Saving...' : 'Save profile'}</button>
            </form>
            <div className="resume-section">
              <h3>Resume manager</h3>
              <form className="upload-form" onSubmit={uploadResume}>
                <label className="file-label"><Upload size={17} /> Choose resume (PDF, DOC, DOCX)<input type="file" accept=".pdf,.doc,.docx" required onChange={(event) => setResumeFile(event.target.files?.[0] || null)} /></label>
                <button disabled={!resumeFile}>Upload resume</button>
              </form>
              <div className="resume-list"><h3>Your uploaded resumes</h3>
                {resumes.length ? resumes.map((item) => (
                  <div className="resume-item" key={item.id}>
                    <span>{item.original_filename}</span><small>{(item.size_bytes / 1024).toFixed(1)} KB</small>
                    <button className="analyze-button" disabled={analyzingId === item.id} onClick={() => analyzeResume(item.id)}>{analyzingId === item.id ? 'Analyzing...' : 'Analyze & match jobs'}</button>
                  </div>
                )) : <p className="muted">No resume uploaded yet.</p>}
              </div>
              {analysis && <div className="analysis-box"><h3>Skills found ({analysis.skill_count})</h3><div className="skill-tags">{analysis.skills.map((skill) => <span key={skill}>{skill}</span>)}</div><p className="muted">{analysis.note}</p></div>}
            </div>
          </section>

          <section className="account-card preferences-card">
            <div className="eyebrow"><Settings2 size={14} /> JOB SEARCH SETTINGS</div>
            <h2>Your job preferences</h2>
            <p className="muted">These settings are saved to your account and kept separate from other users.</p>
            <form className="preferences-form" onSubmit={savePreferences}>
              <label>Target job titles <span>Comma separated</span><input value={preferenceText.target_roles} onChange={(event) => setPreferenceText({ ...preferenceText, target_roles: event.target.value })} placeholder="Data Analyst, Python Developer, Automation Engineer" /></label>
              <label>Preferred locations <span>Comma separated</span><input value={preferenceText.locations} onChange={(event) => setPreferenceText({ ...preferenceText, locations: event.target.value })} placeholder="Pune, Mumbai, Remote" /></label>
              <label>Skills <span>Comma separated</span><input value={preferenceText.skills} onChange={(event) => setPreferenceText({ ...preferenceText, skills: event.target.value })} placeholder="Python, SQL, Selenium, API testing" /></label>
              <div className="form-grid">
                <label>Minimum experience (years)<input type="number" min="0" max="60" value={preferences.min_experience_years ?? ''} onChange={(event) => setPreferences({ ...preferences, min_experience_years: event.target.value })} /></label>
                <label>Maximum experience (years)<input type="number" min="0" max="60" value={preferences.max_experience_years ?? ''} onChange={(event) => setPreferences({ ...preferences, max_experience_years: event.target.value })} /></label>
                <label>Minimum annual salary<input type="number" min="0" value={preferences.min_salary ?? ''} onChange={(event) => setPreferences({ ...preferences, min_salary: event.target.value })} placeholder="e.g. 500000" /></label>
                <label>Maximum annual salary<input type="number" min="0" value={preferences.max_salary ?? ''} onChange={(event) => setPreferences({ ...preferences, max_salary: event.target.value })} placeholder="e.g. 900000" /></label>
                <label>Currency<select value={preferences.currency} onChange={(event) => setPreferences({ ...preferences, currency: event.target.value })}><option value="INR">INR – Indian Rupee</option><option value="USD">USD – US Dollar</option><option value="GBP">GBP – Pound Sterling</option><option value="EUR">EUR – Euro</option></select></label>
                <label>Work mode<select value={preferences.work_mode} onChange={(event) => setPreferences({ ...preferences, work_mode: event.target.value })}><option value="any">Any</option><option value="remote">Remote</option><option value="hybrid">Hybrid</option><option value="onsite">On-site</option></select></label>
              </div>
              <button disabled={savingPreferences}><Save size={15} /> {savingPreferences ? 'Saving preferences...' : 'Save job preferences'}</button>
            </form>
          </section>
        </>
      )}

      {notice && <div className="notice">{notice}</div>}
      {error && <div className="error">{error}</div>}
      {user && <section className="account-card tracker-card">
        <div className="eyebrow"><BriefcaseBusiness size={14} /> APPLICATION TRACKER</div>
        <h2>Your tracked jobs</h2>
        {applications.length ? <div className="application-list">{applications.map((item) => <article className="application-row" key={item.id}>
          <div className="application-info"><strong>{item.title}</strong><span>{item.company} · {item.location || 'Location not listed'}</span><a href={item.job_url} target="_blank" rel="noreferrer">Open job posting <ExternalLink size={12} /></a></div>
          <select aria-label={'Status for ' + item.title} value={item.status} onChange={(event) => updateApplicationStatus(item.id, event.target.value)}>
            <option value="saved">Saved</option><option value="applied">Applied</option><option value="interview">Interview</option><option value="rejected">Rejected</option><option value="offer">Offer</option>
          </select>
        </article>)}</div> : <p className="muted">No jobs tracked yet. Use “Track job” on a job card below.</p>}
      </section>}

      <section className="results-head"><div><div className="eyebrow">OPPORTUNITIES</div><h2>Recommended jobs</h2></div><button className="refresh" onClick={loadJobs} disabled={loading}><RefreshCw size={16} /> Refresh</button></section>
      <section className="jobs">{jobs.map((job) => (
        <article className="job" key={job.id}>
          <div className="job-top"><div className="company-icon"><BriefcaseBusiness size={20} /></div><span className="score">{job.match_score ?? '—'}{job.match_score !== undefined ? '% match' : 'DEMO'}</span></div>
          <h3>{job.title}</h3><div className="company">{job.company}</div><div className="location"><MapPin size={14} />{job.location}</div>
          <p>{job.description}</p><a href={job.url} target="_blank" rel="noreferrer">View opportunity <ExternalLink size={14} /></a>{user && <button className="track-button" onClick={() => trackJob(job)}><Save size={14} /> Track job</button>}
        </article>
      ))}</section>
      <footer>JobPilot AI · Demo listings are sample data. Resume uploads are private to the signed-in account. Live job integrations will use sources that permit access.</footer>
    </main>
  );
}
