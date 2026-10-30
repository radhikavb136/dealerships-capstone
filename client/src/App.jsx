import { useEffect, useMemo, useState } from "react";
import Register from "../../server/frontend/src/components/Register/Register.jsx";

const api = async (path, options = {}) => {
  const response = await fetch(path, { credentials: "same-origin", ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
};

export default function App() {
  const [dealers, setDealers] = useState([]);
  const [stateFilter, setStateFilter] = useState("All states");
  const [selected, setSelected] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [user, setUser] = useState("");
  const [page, setPage] = useState("home");
  const [notice, setNotice] = useState("");
  const [login, setLogin] = useState({ userName: "", password: "" });
  const [reviewForm, setReviewForm] = useState({ review: "", purchase: false, purchase_date: "", car_make: "Toyota", car_model: "Camry", car_year: 2024 });

  async function loadDealers() {
    try { setDealers(await api(stateFilter === "All states" ? "/fetchDealers" : `/fetchDealers/${encodeURIComponent(stateFilter)}`)); }
    catch (err) { setNotice(err.message); }
  }
  useEffect(() => { loadDealers(); }, [stateFilter]);
  const states = useMemo(() => [...new Set(dealers.map((dealer) => dealer.state))].sort(), [dealers]);

  async function openDealer(dealer) {
    try {
      const [detail, list] = await Promise.all([api(`/fetchDealer/${dealer.id}`), api(`/fetchReviews/dealer/${dealer.id}`)]);
      setSelected(detail); setReviews(list); setPage("detail"); setNotice("");
    } catch (err) { setNotice(err.message); }
  }
  async function signIn(event) {
    event.preventDefault(); setNotice("");
    try {
      const data = await api("/djangoapp/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(login) });
      setUser(data.userName); setPage("home"); setNotice(`Welcome, ${data.userName}!`);
    } catch (err) { setNotice(err.message); }
  }
  async function signOut() {
    try { await api("/djangoapp/logout"); setUser(""); setNotice("You have been logged out."); }
    catch (err) { setNotice(err.message); }
  }
  async function submitReview(event) {
    event.preventDefault();
    try {
      const created = await api(`/fetchReviews/dealer/${selected.id}`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(reviewForm),
      });
      setReviews((current) => [created, ...current]);
      setReviewForm({ ...reviewForm, review: "", purchase_date: "" });
      setNotice(`Review submitted — sentiment: ${created.sentiment}.`);
    } catch (err) { setNotice(err.message); }
  }

  return <div className="app-shell">
    <header className="topbar"><button className="brand" onClick={() => setPage("home")}>Drive<span>Review</span></button>
      <nav><button onClick={() => setPage("home")}>Dealerships</button><button onClick={() => setPage("about")}>About</button><button onClick={() => setPage("contact")}>Contact</button>
      {user ? <><span className="user-chip">{user}</span><button className="nav-cta" onClick={signOut}>Logout</button></> : <><button onClick={() => setPage("login")}>Login</button><button className="nav-cta" onClick={() => setPage("register")}>Register</button></>}</nav>
    </header>
    {notice && <div className="notice" role="status">{notice}<button onClick={() => setNotice("")}>×</button></div>}
    {page === "home" && <main>
      <section className="hero"><div className="eyebrow">YOUR NEXT DRIVE STARTS HERE</div><h1>Find a dealership<br /><span>you can trust.</span></h1><p>Explore local dealerships and learn from customer experiences before you visit.</p><div className="hero-stats"><div><strong>{dealers.length || "50+"}</strong><small>Dealerships shown</small></div><div><strong>Real stories</strong><small>Customer reviews</small></div></div></section>
      <section className="content"><div className="section-heading"><div><div className="eyebrow">EXPLORE OUR NETWORK</div><h2>Featured dealerships</h2><p>Choose a location and find your next automotive partner.</p></div><label className="filter">Filter by state<select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)}><option>All states</option>{[...new Set([...states, "Kansas", "Texas", "Arizona", "Colorado", "Washington", "Florida", "Ohio", "North Carolina"])].sort().map((state) => <option key={state}>{state}</option>)}</select></label></div>
      {dealers.length ? <div className="dealer-grid">{dealers.map((dealer, index) => <article className="dealer-card" key={dealer.id}><div className={`dealer-art art-${index % 4}`}><span>DR</span><small>VERIFIED DIRECTORY</small></div><div className="dealer-info"><span className="location">{dealer.city}, {dealer.state}</span><h3>{dealer.full_name}</h3><p>{dealer.address}</p><div className="card-bottom"><span>ZIP {dealer.zip}</span><button onClick={() => openDealer(dealer)}>View details ↗</button></div></div></article>)}</div> : <div className="empty"><h3>No dealerships loaded yet</h3><p>Start Django and run <code>python manage.py seed_dealerships</code> in the server folder.</p><button onClick={loadDealers}>Try again</button></div>}</section>
    </main>}
    {page === "detail" && selected && <main className="content detail-page"><button className="back" onClick={() => setPage("home")}>← All dealerships</button><section className="detail-hero"><div><span className="location">{selected.city}, {selected.state} · {selected.zip}</span><h1>{selected.full_name}</h1><p>{selected.address}</p><p>Coordinates: {selected.lat.toFixed(4)}, {selected.long.toFixed(4)}</p></div><div className="dealer-monogram">DR</div></section><div className="detail-columns"><section><h2>Customer reviews <span className="count">{reviews.length}</span></h2>{reviews.length ? reviews.map((r) => <article className="review-card" key={r.id}><div className="review-top"><strong>{r.name}</strong><span className={`sentiment ${r.sentiment}`}>{r.sentiment}</span></div><p>{r.review}</p><small>{r.car_year} {r.car_make} {r.car_model} · {r.purchase ? "Purchased here" : "Research visit"}{r.purchase_date ? ` · ${r.purchase_date}` : ""}</small></article>) : <div className="empty compact">No reviews yet. Be the first to share your experience.</div>}</section>
      <section className="form-panel"><h2>Share your experience</h2>{user ? <form onSubmit={submitReview}><label>Your review<textarea value={reviewForm.review} onChange={(e) => setReviewForm({ ...reviewForm, review: e.target.value })} required minLength={3} maxLength={3000} placeholder="What was your experience like?" /></label><label>Car make<select value={reviewForm.car_make} onChange={(e) => setReviewForm({ ...reviewForm, car_make: e.target.value, car_model: e.target.value === "Honda" ? "Civic" : "Camry" })}>{["Toyota","Honda","Ford","Chevrolet","Nissan","Hyundai","Subaru","Tesla"].map((m) => <option key={m}>{m}</option>)}</select></label><label>Car model<input value={reviewForm.car_model} onChange={(e) => setReviewForm({ ...reviewForm, car_model: e.target.value })} required /></label><label>Car year<input type="number" min="1900" max="2100" value={reviewForm.car_year} onChange={(e) => setReviewForm({ ...reviewForm, car_year: Number(e.target.value) })} required /></label><label className="check-row"><input type="checkbox" checked={reviewForm.purchase} onChange={(e) => setReviewForm({ ...reviewForm, purchase: e.target.checked })} /> I purchased a vehicle here</label><label>Purchase date (optional)<input type="date" value={reviewForm.purchase_date} onChange={(e) => setReviewForm({ ...reviewForm, purchase_date: e.target.value })} /></label><button className="primary" type="submit">Submit review</button></form> : <p className="muted">Please <button className="text-button" onClick={() => setPage("login")}>log in</button> to submit a review.</p>}</section></div></main>}
    {page === "login" && <main className="auth-wrap"><form className="form-panel auth-card" onSubmit={signIn}><div className="eyebrow">WELCOME BACK</div><h1>Sign in</h1><p className="muted">Log in to share your dealership experience.</p><label>Username<input value={login.userName} onChange={(e) => setLogin({ ...login, userName: e.target.value })} required autoComplete="username" /></label><label>Password<input type="password" value={login.password} onChange={(e) => setLogin({ ...login, password: e.target.value })} required autoComplete="current-password" /></label><button className="primary">Login</button><p className="muted">No account? <button type="button" className="text-button" onClick={() => setPage("register")}>Register</button></p></form></main>}
    {page === "register" && <main className="auth-wrap"><div className="form-panel auth-card"><Register onRegistered={() => setPage("login")} /></div></main>}
    {page === "about" && <main className="content simple-page"><div className="eyebrow">OUR STORY</div><h1>About DriveReview</h1><p>We help drivers compare dealership options and learn from customer experiences in one approachable directory.</p><div className="feature-row"><article className="feature"><b>01</b><h3>Discover</h3><p>Browse dealerships by location and explore the details that matter.</p></article><article className="feature"><b>02</b><h3>Understand</h3><p>Read customer feedback, including vehicle and purchase context.</p></article><article className="feature"><b>03</b><h3>Contribute</h3><p>Share your experience to help the next shopper make an informed choice.</p></article></div></main>}
    {page === "contact" && <main className="content simple-page"><div className="eyebrow">LET'S TALK</div><h1>Contact us</h1><p>Have a question or suggestion? Reach out to the demo team.</p><div className="contact-box"><div><h2>We're here to help</h2><p>Email: hello@drivereview.example</p><p>Phone: +1 (555) 014-0182</p><p>Office: 125 Market Street, Suite 400, Wichita, KS 67202</p><small>Demo contact information for the capstone project.</small></div><div className="contact-illustration">✦<span>Better journeys<br />start with good information.</span></div></div></main>}
    <footer><strong>DriveReview</strong><span>Smarter dealership discovery, one review at a time.</span><small>© 2026 DriveReview Capstone · Demo data</small></footer>
  </div>;
}
