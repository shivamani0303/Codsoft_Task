from pathlib import Path
import joblib
import streamlit as st
from auth import register_user, verify_user

# ─────────────────────────────────────────────────────────────────────────────
# PATHS  — preserved exactly from train_model.py
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "movie_genre_model.joblib"

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title            = "Movie AI Studio",
    page_icon             = "🎬",
    layout                = "wide",
    initial_sidebar_state = "collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CREDENTIALS  — production-grade via st.secrets + SHA-256 hashing
#
# Passwords are NEVER stored in plain text anywhere in this file.
# The secrets.toml file stores SHA-256 hashes only.
#
# Local dev  : credentials are read from .streamlit/secrets.toml
# Streamlit Cloud: paste the same secrets.toml contents into
#                  App dashboard → Settings → Secrets
#
# To add a new user or change a password:
#   1. Run: python -c "import hashlib; print(hashlib.sha256('newpassword'.encode()).hexdigest())"
#   2. Add  newuser = "<hash>"  under [credentials] in secrets.toml
#   3. On Streamlit Cloud, update the Secrets dashboard and reboot the app.
# ─────────────────────────────────────────────────────────────────────────────

import hashlib
import hmac

def _load_credentials() -> dict:
    """Load username-to-password-hash mappings from Streamlit secrets."""
    try:
        return dict(st.secrets["credentials"])
    except (KeyError, FileNotFoundError):
        return {}

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def do_login(username: str, password: str) -> bool:
    """Check the username and SHA-256 password hash."""
    creds = _load_credentials()
    stored_hash = creds.get(username.strip())

    if not stored_hash:
        return False

    entered_hash = _hash(password)
    return hmac.compare_digest(entered_hash, str(stored_hash).strip())

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN PAGE — cinematic purple/blue split-screen authentication
# ─────────────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "login_user" not in st.session_state:
    st.session_state["login_user"] = ""
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False

if not st.session_state["logged_in"]:
    # Login-page-only CSS. The dashboard CSS below remains unchanged.
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    .stApp {
        background:
            radial-gradient(ellipse at 8% 5%, rgba(109,40,217,.22), transparent 42%),
            radial-gradient(ellipse at 95% 95%, rgba(14,165,233,.14), transparent 40%),
            linear-gradient(135deg, #060711 0%, #0a1021 55%, #070914 100%);
        color: #e5e7eb;
    }
    .block-container {
        max-width: 1180px !important;
        padding: 2rem 1.5rem 3rem !important;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    div[data-testid="stDecoration"] { display: none !important; }

    .auth-brand {
        display:flex; align-items:center; gap:12px;
        margin: 0 0 1.5rem .2rem;
        color:#f8fafc; font-family:'Space Grotesk',sans-serif;
        font-size:1.12rem; font-weight:700;
    }
    .auth-brand-icon {
        display:flex; align-items:center; justify-content:center;
        width:42px; height:42px; border-radius:13px;
        background:linear-gradient(135deg,#7c3aed,#2563eb);
        box-shadow:0 0 28px rgba(99,102,241,.35);
        font-size:1.25rem;
    }
    .auth-brand em { color:#a78bfa; font-style:normal; }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width:0;
    }
    .auth-art {
        min-height: 590px; height:100%;
        position:relative; overflow:hidden;
        display:flex; flex-direction:column; justify-content:space-between;
        padding:2.4rem 2.1rem;
        border:1px solid rgba(167,139,250,.20);
        border-radius:26px;
        background:
            radial-gradient(ellipse at 50% 35%, rgba(124,58,237,.32), transparent 44%),
            radial-gradient(ellipse at 90% 85%, rgba(37,99,235,.30), transparent 42%),
            linear-gradient(145deg, rgba(21,18,49,.98), rgba(7,15,33,.98));
        box-shadow:0 25px 80px rgba(0,0,0,.30), inset 0 1px rgba(255,255,255,.05);
    }
    .auth-art:before {
        content:""; position:absolute; width:330px; height:330px;
        border:1px solid rgba(167,139,250,.19); border-radius:50%;
        top:20%; left:50%; transform:translateX(-50%);
        box-shadow:0 0 0 35px rgba(139,92,246,.035),
                   0 0 0 75px rgba(59,130,246,.025),
                   inset 0 0 55px rgba(99,102,241,.08);
    }
    .auth-art:after {
        content:""; position:absolute; width:210px; height:280px;
        left:50%; top:24%; transform:translateX(-50%) rotate(8deg);
        border-radius:48% 48% 22% 22%;
        background:linear-gradient(160deg,rgba(167,139,250,.18),rgba(37,99,235,.025));
        border:1px solid rgba(147,197,253,.20);
        filter:drop-shadow(0 0 35px rgba(124,58,237,.25));
    }
    .art-top, .art-middle, .art-bottom { position:relative; z-index:1; }
    .art-kicker {
        display:inline-block; padding:.42rem .8rem; border-radius:999px;
        border:1px solid rgba(167,139,250,.28);
        background:rgba(139,92,246,.10); color:#c4b5fd;
        font-size:.68rem; font-weight:700; letter-spacing:.14em;
        text-transform:uppercase;
    }
    .art-middle { margin-top:2rem; margin-bottom:2rem; }
    .art-overline {
        color:#93c5fd; font-size:.72rem; font-weight:700;
        letter-spacing:.22em; text-transform:uppercase; margin-bottom:.8rem;
    }
    .art-title {
        font-family:'Space Grotesk',sans-serif; font-weight:700;
        font-size:clamp(2.2rem,4vw,3.45rem); line-height:1.05;
        letter-spacing:-.045em; color:#f8fafc; margin:0 0 1rem;
    }
    .art-title span {
        background:linear-gradient(100deg,#c4b5fd,#818cf8,#7dd3fc);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .art-copy { max-width:390px; color:#9ca3af; font-size:.94rem; line-height:1.8; }
    .art-bottom { border-top:1px solid rgba(255,255,255,.10); padding-top:1.2rem; }
    .art-pills { display:flex; flex-wrap:wrap; gap:.5rem; margin-bottom:1rem; }
    .art-pill {
        padding:.36rem .68rem; border-radius:9px;
        border:1px solid rgba(255,255,255,.10);
        background:rgba(255,255,255,.04); color:#cbd5e1; font-size:.72rem;
    }
    .art-footnote { color:#64748b; font-size:.73rem; line-height:1.6; }

    /* Style the actual Streamlit form column, not an HTML wrapper.
       Streamlit widgets cannot reliably be wrapped by divs split across markdown calls. */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-of-type(2) {
        min-height:590px;
        padding:2.1rem 2rem !important;
        border:1px solid rgba(255,255,255,.09) !important;
        border-radius:26px !important;
        background:linear-gradient(155deg,rgba(16,20,39,.94),rgba(8,12,26,.96)) !important;
        box-shadow:0 25px 80px rgba(0,0,0,.24);
    }
    .auth-eyebrow {
        color:#a78bfa; font-size:.68rem; font-weight:700;
        letter-spacing:.18em; text-transform:uppercase; margin-bottom:.8rem;
    }
    .auth-heading {
        font-family:'Space Grotesk',sans-serif; color:#f8fafc;
        font-size:2.15rem; line-height:1.15; letter-spacing:-.04em;
        font-weight:700; margin:0 0 .7rem;
    }
    .auth-subtitle { color:#94a3b8; font-size:.88rem; line-height:1.7; margin-bottom:1.5rem; }
    div[data-testid="stTextInput"] label {
        color:#cbd5e1 !important; font-size:.78rem !important;
        font-weight:600 !important; margin-bottom:.35rem !important;
    }
    div[data-testid="stTextInput"] input {
        background:rgba(5,9,23,.78) !important;
        border:1px solid rgba(129,140,248,.22) !important;
        border-radius:12px !important; color:#f1f5f9 !important;
        min-height:47px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color:#8b5cf6 !important;
        box-shadow:0 0 0 2px rgba(139,92,246,.16) !important;
    }
    .stButton > button[kind="primary"], button[kind="primaryFormSubmit"] {
        background:linear-gradient(110deg,#7c3aed,#4f46e5 58%,#2563eb) !important;
        color:white !important; border:1px solid rgba(167,139,250,.34) !important;
        border-radius:12px !important; min-height:47px !important;
        font-weight:700 !important; box-shadow:0 8px 26px rgba(79,70,229,.22);
        transition:transform .18s ease, filter .18s ease;
    }
    .stButton > button[kind="primary"]:hover,
    button[kind="primaryFormSubmit"]:hover {
        filter:brightness(1.12); transform:translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        background:rgba(255,255,255,.035) !important;
        border:1px solid rgba(167,139,250,.20) !important;
        color:#c4b5fd !important; border-radius:12px !important;
        min-height:42px !important;
    }
    div[data-testid="stAlert"] { border-radius:12px !important; }
    .auth-privacy {
        color:#64748b; font-size:.72rem; line-height:1.65;
        text-align:center; margin-top:1.25rem;
    }
    @media (max-width: 850px) {
        .auth-art { min-height:320px; padding:1.6rem; }
        .auth-art:before { width:220px; height:220px; top:22%; }
        .auth-art:after { width:130px; height:170px; top:25%; }
        .art-middle { margin-top:1.5rem; margin-bottom:1.5rem; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-of-type(2) {
            min-height:0; padding:1.6rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-brand">
      <div class="auth-brand-icon">🎬</div>
      <span>Movie <em>AI</em> Studio</span>
    </div>
    """, unsafe_allow_html=True)

    art_col, form_col = st.columns([1.04, 0.96], gap="large")

    with art_col:
        st.markdown("""
        <div class="auth-art">
          <div class="art-top">
            <span class="art-kicker">✦ &nbsp;Your story, decoded</span>
          </div>
          <div class="art-middle">
            <div class="art-overline">Welcome to the next scene</div>
            <h1 class="art-title">Every plot has<br>a <span>genre.</span></h1>
            <div class="art-copy">
              Step into your personal movie intelligence studio. Explore stories,
              uncover patterns, and let AI predict the genre behind every plot.
            </div>
          </div>
          <div class="art-bottom">
            <div class="art-pills">
              <span class="art-pill">✧ NLP powered</span>
              <span class="art-pill">◈ 27 genres</span>
              <span class="art-pill">⌘ Smart prediction</span>
            </div>
            <div class="art-footnote">
              Powered by TF-IDF vectorisation and a Linear Support Vector Classifier.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with form_col:
        if st.session_state["show_login"]:
            st.markdown(
                '<div class="auth-eyebrow">Your next scene awaits</div>'
                '<div class="auth-heading">Welcome back.</div>'
                '<div class="auth-subtitle">Sign in to continue exploring Movie AI Studio.</div>',
                unsafe_allow_html=True,
            )
            with st.form("signin_form", clear_on_submit=False):
                username = st.text_input("Username", key="signin_username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", key="signin_password", placeholder="Enter your password")
                sign_in = st.form_submit_button("Sign In  →", use_container_width=True, type="primary")

            if sign_in:
                if verify_user(username, password):
                    st.session_state["logged_in"] = True
                    st.session_state["login_user"] = username.strip()
                    st.rerun()
                else:
                    st.error("Incorrect username or password. Please try again.")

            st.markdown('<div class="auth-privacy">Your account keeps your Movie AI Studio experience personal.</div>', unsafe_allow_html=True)
            if st.button("New here?  Create an account", use_container_width=True, type="secondary"):
                st.session_state["show_login"] = False
                st.rerun()

        else:
            st.markdown(
                '<div class="auth-eyebrow">Start your journey</div>'
                '<div class="auth-heading">Create account.</div>'
                '<div class="auth-subtitle">One account. A whole universe of movie stories.</div>',
                unsafe_allow_html=True,
            )
            with st.form("register_form", clear_on_submit=False):
                username = st.text_input("Choose a username", key="register_username", placeholder="Create a username")
                password = st.text_input("Create a password", type="password", key="register_password", placeholder="Use a strong password")
                confirm_password = st.text_input("Confirm password", type="password", key="register_confirm_password", placeholder="Enter your password again")
                create_account = st.form_submit_button("Create Account  →", use_container_width=True, type="primary")

            if create_account:
                if not username.strip():
                    st.error("Please choose a username.")
                elif not password:
                    st.error("Please create a password.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = register_user(username, password)
                    if success:
                        st.session_state["show_login"] = True
                        st.session_state["registration_message"] = message
                        st.rerun()
                    else:
                        st.error(message)

            st.markdown('<div class="auth-privacy">Create an account to save your place and access the studio.</div>', unsafe_allow_html=True)
            if st.button("Already have an account?  Sign in", use_container_width=True, type="secondary"):
                st.session_state["show_login"] = True
                st.rerun()

    if st.session_state["show_login"] and st.session_state.get("registration_message"):
        st.success(st.session_state["registration_message"])
        del st.session_state["registration_message"]

    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# GENRE REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
GENRE_META = {
    "action":      ("⚔️",  "#ef4444"),
    "adult":       ("🔞",  "#d946ef"),
    "adventure":   ("🗺️",  "#f97316"),
    "animation":   ("🎨",  "#10b981"),
    "biography":   ("📖",  "#3b82f6"),
    "comedy":      ("😂",  "#eab308"),
    "crime":       ("🔍",  "#f43f5e"),
    "documentary": ("🎥",  "#06b6d4"),
    "drama":       ("🎭",  "#8b5cf6"),
    "family":      ("👨‍👩‍👧",  "#22c55e"),
    "fantasy":     ("🧙",  "#a855f7"),
    "game-show":   ("🎮",  "#ec4899"),
    "history":     ("🏛️",  "#f59e0b"),
    "horror":      ("👻",  "#6366f1"),
    "music":       ("🎵",  "#ec4899"),
    "musical":     ("🎶",  "#f472b6"),
    "mystery":     ("🕵️",  "#818cf8"),
    "news":        ("📰",  "#94a3b8"),
    "reality-tv":  ("📺",  "#fb923c"),
    "romance":     ("❤️",  "#f43f5e"),
    "sci-fi":      ("🚀",  "#22d3ee"),
    "short":       ("🎞️",  "#84cc16"),
    "sport":       ("🏆",  "#fbbf24"),
    "talk-show":   ("🎙️",  "#64748b"),
    "thriller":    ("😰",  "#f87171"),
    "war":         ("🪖",  "#a16207"),
    "western":     ("🤠",  "#d97706"),
}

# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE PLOTS
# ─────────────────────────────────────────────────────────────────────────────
EXAMPLES = {
    "— write your own —": "",
    "🚀  Sci-Fi":
        "In the year 2157, a lone engineer discovers an alien signal buried deep within "
        "Jupiter's atmosphere. Racing against a hostile corporation, she must decode the "
        "message before humanity loses its only chance at first contact.",
    "🕵️  Crime Thriller":
        "A retired detective is pulled back into the shadows when a series of cryptic "
        "murders mirror an unsolved case from his past. As the bodies pile up, he "
        "realises the killer has been watching him all along.",
    "😂  Romantic Comedy":
        "Two rival food-truck owners are forced to share a prime spot at a summer "
        "festival. Between cooking contests and constant bickering, they discover "
        "that the secret ingredient they were both missing was each other.",
    "👻  Horror":
        "A family moves into a crumbling Victorian mansion only to find the previous "
        "owners never truly left. As terrifying visions grow stronger each night, "
        "the youngest daughter is the only one who can hear the house's dark secret.",
    "🏆  Sports Drama":
        "A once-celebrated marathon runner returns to competition after a devastating "
        "injury, facing a new generation of elite athletes. Fuelled by grief and iron "
        "will, she fights to prove her greatest race is still ahead.",
    "🎨  Animation":
        "A small dragon terrified of fire accidentally sets off on an epic quest "
        "across enchanted kingdoms, befriending a sarcastic wizard and a gentle giant, "
        "learning that courage comes in many shapes and sizes.",
    "🏜️  Western":
        "A disgraced lawman rides into a lawless border town where a ruthless cattle "
        "baron rules through fear. With nothing left to lose, he makes one last stand "
        "for justice against impossible odds.",
    "🎭  Drama":
        "Three estranged siblings reunite at their childhood home after their mother's "
        "sudden death and must confront decades of buried secrets, betrayal, and grief "
        "before they can finally begin to forgive one another.",
}

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for _k, _v in [("prediction", None), ("last_plot", "")]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────────────────
# MODEL LOADER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initialising model…")
def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)

# ═════════════════════════════════════════════════════════════════════════════
# CSS
# Key fix: glass panel styling applied to Streamlit's column containers
# via [data-testid="column"] so real widgets live INSIDE styled panels.
# We never use open/close HTML divs to wrap st.* calls.
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>

/* ── Fonts ────────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

/* ── App background ─────────────────────────────────────────────────────── */
.stApp {
    min-height: 100vh;
    background:
        radial-gradient(ellipse 90% 55% at  8% -5%,  rgba(109,40,217,.28) 0%, transparent 55%),
        radial-gradient(ellipse 60% 45% at 92% 105%, rgba(14,165,233,.15)  0%, transparent 50%),
        radial-gradient(ellipse 70% 60% at 50%  80%, rgba(168,85,247,.06)  0%, transparent 55%),
        linear-gradient(180deg, #06070f 0%, #080c1a 55%, #060914 100%);
    color: #e2e8f0;
}

.block-container {
    max-width: 1280px !important;
    padding: 0 2.5rem 6rem !important;
}

header[data-testid="stHeader"]  { background: transparent !important; }
div[data-testid="stDecoration"] { display: none !important; }

/* ── NAV ────────────────────────────────────────────────────────────────── */
.nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 0 1.1rem;
    border-bottom: 1px solid rgba(139,92,246,.15);
    margin-bottom: 0;
}
.nav-left  { display: flex; align-items: center; gap: .7rem; }
.nav-right { display: flex; align-items: center; gap: .9rem; }
.nav-mark {
    width: 38px; height: 38px;
    border-radius: 11px;
    background: linear-gradient(140deg, #7c3aed 0%, #2563eb 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 0 22px rgba(124,58,237,.50), 0 0 0 1px rgba(124,58,237,.25);
}
.nav-wordmark {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.08rem; font-weight: 700;
    color: #f1f5f9; letter-spacing: -.01em;
}
.nav-wordmark em { font-style: normal; color: #a78bfa; }
.nav-tag {
    font-size: .68rem; font-weight: 700;
    letter-spacing: .14em; text-transform: uppercase;
    color: #4338ca;
}
.nav-badge {
    background: rgba(139,92,246,.12);
    border: 1px solid rgba(139,92,246,.32);
    color: #c4b5fd;
    font-size: .68rem; font-weight: 600;
    letter-spacing: .10em; text-transform: uppercase;
    padding: .28rem .80rem; border-radius: 999px;
}
.nav-user {
    font-size: .72rem; font-weight: 500;
    color: #4b5563; letter-spacing: .02em;
}

/* ── HERO ───────────────────────────────────────────────────────────────── */
.hero {
    position: relative;
    text-align: center;
    padding: 5rem 2rem 4rem;
    overflow: hidden;
    isolation: isolate;
}
.hero-glow {
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 65% 55% at 50% 60%, rgba(109,40,217,.17) 0%, transparent 65%);
    pointer-events: none;
    animation: glow-breathe 5s ease-in-out infinite;
    z-index: 0;
}
@keyframes glow-breathe {
    0%,100% { opacity:.8; transform:scale(1); }
    50%     { opacity:1;  transform:scale(1.05); }
}
.hero-ring {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    border-radius: 50%;
    border: 1px solid rgba(139,92,246,.09);
    pointer-events: none; z-index: 0;
}
.hero-ring-1 { width:420px; height:420px; }
.hero-ring-2 { width:640px; height:640px; border-color:rgba(99,102,241,.06); }
.hero-ring-3 { width:860px; height:860px; border-color:rgba(139,92,246,.035); }
.hero-dot {
    position: absolute;
    border-radius: 50%;
    background: rgba(139,92,246,.55);
    animation: dot-pulse 3s ease-in-out infinite;
    z-index: 0;
}
.hero-dot-1 { width:4px; height:4px; top:22%; left:15%; animation-delay:0s; }
.hero-dot-2 { width:3px; height:3px; top:60%; left:8%;  animation-delay:.8s;  background:rgba(34,211,238,.5); }
.hero-dot-3 { width:5px; height:5px; top:30%; right:12%; animation-delay:1.4s; background:rgba(236,72,153,.5); }
.hero-dot-4 { width:3px; height:3px; top:70%; right:18%; animation-delay:.4s; }
@keyframes dot-pulse {
    0%,100% { opacity:.3; transform:scale(1); }
    50%     { opacity:1;  transform:scale(1.9); }
}
.hero-content { position:relative; z-index:1; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: .5rem;
    background: rgba(139,92,246,.10);
    border: 1px solid rgba(139,92,246,.30);
    color: #c4b5fd;
    font-size: .70rem; font-weight: 600;
    letter-spacing: .16em; text-transform: uppercase;
    padding: .32rem .95rem; border-radius: 999px;
    margin-bottom: 1.8rem;
}
.eyebrow-pulse {
    width:6px; height:6px; background:#a78bfa;
    border-radius:50%; box-shadow:0 0 8px #a78bfa;
    animation: blink 2.2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:.2;} }
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.8rem, 7vw, 5rem);
    font-weight: 800; letter-spacing: -.03em; line-height: 1.0;
    margin-bottom: .2rem;
    background: linear-gradient(110deg, #ffffff 0%, #e2d9f3 25%, #c4b5fd 55%, #7dd3fc 80%, #67e8f9 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-subtitle {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(1rem, 2.5vw, 1.5rem);
    font-weight: 400; letter-spacing: .28em; text-transform: uppercase;
    color: rgba(167,139,250,.45); margin-bottom: 1.6rem;
}
.hero-tagline {
    max-width: 520px; margin: 0 auto 2.4rem;
    color: #64748b; font-size: 1.0rem; line-height: 1.7;
}
.hero-tags { display:flex; flex-wrap:wrap; justify-content:center; gap:.45rem; }
.hero-tag {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.08);
    color: #475569; font-size: .73rem;
    padding: .22rem .72rem; border-radius: 999px;
    transition: all .2s ease; cursor: default;
}
.hero-tag:hover { border-color:rgba(139,92,246,.35); color:#a78bfa; background:rgba(139,92,246,.07); }
.hero-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(139,92,246,.22) 30%, rgba(99,102,241,.30) 50%, rgba(139,92,246,.22) 70%, transparent 100%);
    margin: 0 0 2.6rem;
}

/* ── COLUMN HEADER labels ───────────────────────────────────────────────── */
.col-hdr {
    display: flex; align-items: center; gap: .45rem;
    margin-bottom: .9rem;
}
.col-hdr-dot {
    width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0;
}
.col-hdr-text {
    font-size: .65rem; font-weight: 700;
    letter-spacing: .16em; text-transform: uppercase;
}

/* ── GLASS PANEL — applied to column containers, NOT wrapping widgets ───── */
/*
   KEY FIX: target the two workspace columns by their data-testid.
   This gives a glass-card look without any unclosed HTML div.
   We use nth-of-type(1) for left and nth-of-type(2) for right.
*/
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-of-type(1) {
    background: rgba(255,255,255,.026) !important;
    border: 1px solid rgba(255,255,255,.080) !important;
    border-radius: 22px !important;
    padding: 1.8rem 1.9rem !important;
    position: relative;
    transition: border-color .35s ease;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-of-type(1):hover {
    border-color: rgba(139,92,246,.20) !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-of-type(2) {
    background: rgba(255,255,255,.022) !important;
    border: 1px solid rgba(255,255,255,.070) !important;
    border-radius: 22px !important;
    padding: 1.8rem 1.9rem !important;
    position: relative;
    transition: border-color .35s ease;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-of-type(2):hover {
    border-color: rgba(139,92,246,.18) !important;
}
/* Top shimmer line for both panels */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]::before {
    content: "";
    position: absolute; top: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,.38), transparent);
    border-radius: 1px;
    pointer-events: none;
}

/* ── Sub-labels inside panels ───────────────────────────────────────────── */
.sub-lbl {
    font-size: .67rem; font-weight: 600;
    letter-spacing: .13em; text-transform: uppercase;
    color: #374151; margin-bottom: .45rem;
}

/* ── Character progress bar ─────────────────────────────────────────────── */
.prog-wrap  { margin-top: .65rem; }
.prog-track {
    height: 3px; border-radius: 3px;
    background: rgba(255,255,255,.06); overflow: hidden; margin-bottom: .4rem;
}
.prog-fill  { height: 100%; border-radius: 3px; transition: width .35s ease, background-color .35s ease; }
.prog-meta  { display:flex; justify-content:space-between; font-size:.74rem; }

/* ── RESULT PANEL ───────────────────────────────────────────────────────── */
.result-waiting {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 300px; text-align: center; gap: 1rem; opacity: .35;
}
.result-waiting-icon  { font-size:3rem; filter:grayscale(1); line-height:1; }
.result-waiting-line  { font-size:.82rem; color:#374151; max-width:180px; line-height:1.55; }

.result-card {
    display: flex; flex-direction: column; min-height: 300px;
    animation: slide-in .38s cubic-bezier(.22,1,.36,1) both;
}
@keyframes slide-in { from{opacity:0;transform:translateY(14px);} to{opacity:1;transform:translateY(0);} }
.result-eyebrow {
    font-size:.62rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase;
    margin-bottom:.7rem; display:flex; align-items:center; gap:.35rem;
}
.result-eyebrow-line { flex:1; height:1px; background:currentColor; opacity:.2; }
.result-icon {
    font-size:4.8rem; line-height:1; margin-bottom:1rem; display:block;
    animation: pop-in .5s cubic-bezier(.34,1.56,.64,1) .08s both;
}
@keyframes pop-in { from{transform:scale(.45) rotate(-8deg);opacity:0;} to{transform:scale(1) rotate(0);opacity:1;} }
.result-genre {
    font-family: 'Space Grotesk', sans-serif;
    font-size:2.9rem; font-weight:800; line-height:1;
    letter-spacing:-.02em; margin-bottom:.6rem;
}
.result-bar {
    height:3px; border-radius:3px; width:48px; margin:.7rem 0 1.1rem;
    animation: bar-grow .4s ease .2s both;
}
@keyframes bar-grow { from{width:0;opacity:0;} to{width:48px;opacity:1;} }
.result-summary  { font-size:.84rem; color:#475569; line-height:1.65; flex:1; }
.result-summary strong { font-weight:600; }
.result-disclaimer {
    margin-top:1.2rem; padding-top:1rem;
    border-top:1px solid rgba(255,255,255,.06);
    font-size:.74rem; color:#374151; line-height:1.55;
}

/* ── PRIMARY BUTTON ─────────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    width: 100% !important;
    background: linear-gradient(135deg, #5b21b6 0%, #4338ca 45%, #1e40af 100%) !important;
    border: 1px solid rgba(139,92,246,.30) !important;
    border-radius: 16px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.08rem !important; font-weight: 700 !important;
    letter-spacing: .05em !important; padding: .88rem 2.5rem !important;
    color: #f8fafc !important;
    box-shadow: 0 4px 28px rgba(91,33,182,.50), 0 1px 0 rgba(255,255,255,.12) inset !important;
    transition: transform .2s ease, box-shadow .2s ease, filter .2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 40px rgba(91,33,182,.70), 0 1px 0 rgba(255,255,255,.15) inset !important;
    filter: brightness(1.08) !important;
}
.stButton > button[kind="primary"]:active { transform:translateY(0) !important; filter:brightness(.95) !important; }

/* ── SECONDARY (reset) BUTTON ───────────────────────────────────────────── */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    border-radius: 10px !important; color: #4b5563 !important;
    font-size: .80rem !important; font-weight: 500 !important;
    padding: .32rem .85rem !important;
    transition: border-color .2s, color .2s, background .2s !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: rgba(239,68,68,.32) !important;
    color: #f87171 !important; background: rgba(239,68,68,.05) !important;
}

/* ── ALERTS ─────────────────────────────────────────────────────────────── */
div[data-testid="stAlert"] { border-radius: 14px !important; font-size: .87rem !important; }

/* ── TEXTAREA ───────────────────────────────────────────────────────────── */
div[data-testid="stTextArea"] textarea {
    background: rgba(6,9,24,.82) !important;
    border: 1px solid rgba(99,102,241,.22) !important;
    border-radius: 14px !important;
    color: #cbd5e1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .91rem !important; line-height: 1.72 !important;
    caret-color: #a78bfa !important;
    transition: border-color .25s, box-shadow .25s !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(139,92,246,.60) !important;
    box-shadow: 0 0 0 3px rgba(109,40,217,.16), 0 0 24px rgba(109,40,217,.08) !important;
    outline: none !important;
}
div[data-testid="stTextArea"] textarea::placeholder { color: #1e2d40 !important; }
div[data-testid="stTextArea"] label { display: none !important; }

/* ── SELECTBOX ──────────────────────────────────────────────────────────── */
div[data-testid="stSelectbox"] > div > div {
    background: rgba(6,9,24,.82) !important;
    border: 1px solid rgba(99,102,241,.22) !important;
    border-radius: 12px !important;
    color: #94a3b8 !important; font-size: .87rem !important;
    transition: border-color .2s !important;
}
div[data-testid="stSelectbox"] > div > div:hover { border-color: rgba(139,92,246,.45) !important; color: #c4b5fd !important; }
div[data-testid="stSelectbox"] label { display: none !important; }

/* ── FEATURE CARDS ──────────────────────────────────────────────────────── */
.section-hdg       { text-align:center; margin-bottom:1.4rem; }
.section-hdg-eyebrow { font-size:.63rem; font-weight:700; letter-spacing:.20em; text-transform:uppercase; color:#374155; margin-bottom:.3rem; }
.section-hdg-title {
    font-family:'Space Grotesk',sans-serif; font-size:1.45rem; font-weight:700; color:#e2e8f0;
}
.section-hdg-title em { font-style:normal; color:#a78bfa; }

.feat {
    background: rgba(255,255,255,.022);
    border: 1px solid rgba(255,255,255,.062);
    border-radius: 18px; padding: 1.5rem 1.55rem 1.4rem;
    height: 100%; position: relative; overflow: hidden;
    transition: border-color .3s ease, transform .3s ease, box-shadow .3s ease;
}
.feat:hover { border-color:rgba(139,92,246,.28); transform:translateY(-4px); box-shadow:0 12px 40px rgba(0,0,0,.35); }
.feat::before {
    content:""; position:absolute; top:0; left:15%; right:15%; height:1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,.4), transparent);
    opacity:0; transition: opacity .3s;
}
.feat:hover::before { opacity:1; }
.feat-icon-box {
    width:40px; height:40px; border-radius:11px;
    display:flex; align-items:center; justify-content:center;
    font-size:1.15rem; margin-bottom:.9rem;
}
.feat-step { font-size:.60rem; font-weight:700; letter-spacing:.15em; text-transform:uppercase; margin-bottom:.28rem; }
.feat-title { font-family:'Space Grotesk',sans-serif; font-size:1.0rem; font-weight:700; color:#e2e8f0; margin-bottom:.5rem; }
.feat-desc  { font-size:.80rem; color:#4b5563; line-height:1.60; }
.feat-desc em { font-style:normal; color:#6b7280; }

/* ── FOOTER ─────────────────────────────────────────────────────────────── */
.footer {
    margin-top:4rem;
    border-top:1px solid rgba(255,255,255,.055);
    padding:1.8rem 0 .5rem;
    display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:1rem;
}
.footer-brand { display:flex; align-items:center; gap:.55rem; }
.footer-mark {
    width:28px; height:28px; border-radius:8px;
    background:linear-gradient(140deg,#7c3aed,#2563eb);
    display:flex; align-items:center; justify-content:center;
    font-size:.80rem; opacity:.7;
}
.footer-brand-text { font-family:'Space Grotesk',sans-serif; font-size:.82rem; font-weight:600; color:#374151; }
.footer-mid   { font-size:.74rem; color:#1f2937; text-align:center; line-height:1.5; }
.footer-right { font-size:.72rem; color:#1f2937; text-align:right; }

/* ── SCROLLBAR ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(99,102,241,.28); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:rgba(139,92,246,.50); }

</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# LOAD MODEL
# ═════════════════════════════════════════════════════════════════════════════
model = load_model()

# ═════════════════════════════════════════════════════════════════════════════
# NAV BAR
# ═════════════════════════════════════════════════════════════════════════════
nav_left, nav_right = st.columns([6, 1])
with nav_left:
    st.markdown(f"""
    <div class="nav">
      <div class="nav-left">
        <div class="nav-mark">🎬</div>
        <span class="nav-wordmark">Movie&nbsp;<em>AI</em>&nbsp;Studio</span>
      </div>
      <div class="nav-right">
        <span class="nav-tag">NLP · Text Classification</span>
        <span class="nav-badge">✦ AI Genre Intelligence</span>
        <span class="nav-user">👤 &nbsp;{st.session_state.get("login_user", "")}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
with nav_right:
    st.markdown('<div style="padding-top:1.15rem;"></div>', unsafe_allow_html=True)
    if st.button("Sign Out", type="secondary", use_container_width=True):
        st.session_state["logged_in"]  = False
        st.session_state["login_user"] = ""
        st.session_state["prediction"] = None
        st.session_state["last_plot"]  = ""
        st.rerun()

# ── Model gate ────────────────────────────────────────────────────────────────
if model is None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.error("⚠️  Trained model not found at `models/movie_genre_model.joblib`.")
    st.markdown("Run the training script once to generate it:")
    st.code("python train_model.py", language="bash")
    st.info("After training finishes, relaunch: `streamlit run app.py`")
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# HERO
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-glow"></div>
  <div class="hero-ring hero-ring-1"></div>
  <div class="hero-ring hero-ring-2"></div>
  <div class="hero-ring hero-ring-3"></div>
  <div class="hero-dot hero-dot-1"></div>
  <div class="hero-dot hero-dot-2"></div>
  <div class="hero-dot hero-dot-3"></div>
  <div class="hero-dot hero-dot-4"></div>
  <div class="hero-content">
    <div class="hero-eyebrow">
      <span class="eyebrow-pulse"></span>
      Natural Language Processing &nbsp;·&nbsp; Genre Classification
    </div>
    <h1 class="hero-title">MOVIE AI STUDIO</h1>
    <p class="hero-subtitle">Genre Intelligence Engine</p>
    <p class="hero-tagline">
      Describe any film in plain language. The model reads linguistic patterns
      across your text and classifies the genre using TF-IDF vectorisation
      and a Linear Support Vector Classifier.
    </p>
    <div class="hero-tags">
      <span class="hero-tag">27 genres</span>
      <span class="hero-tag">Word n-grams</span>
      <span class="hero-tag">Character n-grams</span>
      <span class="hero-tag">TF-IDF</span>
      <span class="hero-tag">LinearSVC</span>
      <span class="hero-tag">scikit-learn</span>
      <span class="hero-tag">Pipeline</span>
      <span class="hero-tag">FeatureUnion</span>
    </div>
  </div>
</div>
<div class="hero-divider"></div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# WORKSPACE — two columns
# The glass panel CSS is applied to the column containers via CSS selectors.
# No open/close HTML div wrappers around st.* calls.
# ═════════════════════════════════════════════════════════════════════════════
col_L, col_R = st.columns([1.08, 0.92], gap="large")

# ─────────────────────────────────────────────────── LEFT: Plot Input ────────
with col_L:

    st.markdown("""
    <div class="col-hdr">
      <span class="col-hdr-dot" style="background:#6366f1;box-shadow:0 0 6px #6366f1;"></span>
      <span class="col-hdr-text" style="color:#4338ca;">Plot Input</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sub-lbl">Quick-load example</p>', unsafe_allow_html=True)

    chosen = st.selectbox(
        "example-select",
        list(EXAMPLES.keys()),
        label_visibility="collapsed",
    )

    r_col, _ = st.columns([1, 3])
    with r_col:
        if st.button("✕  Reset", type="secondary", use_container_width=True):
            st.session_state["prediction"] = None
            st.session_state["last_plot"]  = ""
            st.rerun()

    # Textarea default: use selected example, else restore last typed text
    if chosen != "— write your own —":
        area_default = EXAMPLES[chosen]
    else:
        area_default = st.session_state["last_plot"]

    st.markdown('<p class="sub-lbl" style="margin-top:.85rem;">Movie plot summary</p>',
                unsafe_allow_html=True)

    plot_input = st.text_area(
        "plot-text",
        value    = area_default,
        height   = 200,
        placeholder = (
            "Describe the story — setting, characters, central conflict…\n\n"
            "e.g. A disgraced astronaut is stranded alone on Mars after a dust storm "
            "forces her crew to evacuate. Using only ingenuity and resourcefulness, she "
            "must survive long enough for a rescue mission to reach her."
        ),
        label_visibility = "collapsed",
    )

    # Character progress bar
    n     = len(plot_input.strip())
    pct   = min(n / 130 * 100, 100)
    color = "#ef4444" if n < 20 else ("#f59e0b" if n < 60 else "#22c55e")
    msg   = "Too short — add more detail" if n < 20 else ("Good — a bit more helps" if n < 60 else "✓  Ready to analyse")
    st.markdown(f"""
    <div class="prog-wrap">
      <div class="prog-track">
        <div class="prog-fill" style="width:{pct:.1f}%;background:{color};"></div>
      </div>
      <div class="prog-meta">
        <span style="color:{color};font-weight:500;">{msg}</span>
        <span style="color:#374151;">{n} chars</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────── RIGHT: Prediction Result ────────
with col_R:

    st.markdown("""
    <div class="col-hdr">
      <span class="col-hdr-dot" style="background:#a78bfa;box-shadow:0 0 6px #a78bfa;"></span>
      <span class="col-hdr-text" style="color:#7c3aed;">Prediction Result</span>
    </div>
    """, unsafe_allow_html=True)

    pred = st.session_state["prediction"]

    if pred is None:
        st.markdown("""
        <div class="result-waiting">
          <div class="result-waiting-icon">🎞️</div>
          <div class="result-waiting-line">
            Enter a plot on the left, then click<br>
            <span style="color:#6366f1;font-weight:600;">Analyse Movie Plot</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        genre  = pred["genre"]
        icon   = pred["icon"]
        accent = pred["accent"]
        st.markdown(f"""
        <div class="result-card">
          <div class="result-eyebrow" style="color:{accent};">
            ✦ &nbsp;Predicted Genre
            <span class="result-eyebrow-line" style="color:{accent};"></span>
          </div>
          <span class="result-icon">{icon}</span>
          <div class="result-genre" style="color:{accent};">{genre.title()}</div>
          <div class="result-bar" style="background:linear-gradient(90deg,{accent},{accent}44);"></div>
          <div class="result-summary">
            The classifier matched the linguistic patterns in your description
            to the&nbsp;<strong style="color:{accent}bb;">{genre.title()}</strong>&nbsp;genre.
          </div>
          <div class="result-disclaimer">
            This is a model prediction, not a verified label. Genre boundaries often
            overlap — many films genuinely belong to more than one category.
            Results depend on the vocabulary and phrasing of your input.
          </div>
        </div>
        """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ANALYSE BUTTON
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
_, b_mid, _ = st.columns([1, 2.6, 1])
with b_mid:
    clicked = st.button("✦  Analyse Movie Plot", type="primary", use_container_width=True)

if clicked:
    clean = plot_input.strip()
    if len(clean) == 0:
        st.warning("Please enter a plot summary before analysing.")
    elif len(clean) < 20:
        st.warning("The description is too short. Add a few more sentences for a reliable result.")
    else:
        with st.spinner("Analysing linguistic patterns…"):
            raw: str = model.predict([clean])[0]
        predicted = raw.strip().lower()
        icon, accent = GENRE_META.get(predicted, ("🎬", "#a78bfa"))
        st.session_state["prediction"] = {"genre": predicted, "icon": icon, "accent": accent}
        st.session_state["last_plot"]  = clean
        st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# HOW IT WORKS — three feature cards
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div class="section-hdg">
  <div class="section-hdg-eyebrow">Under the hood</div>
  <div class="section-hdg-title">How the <em>Model Works</em></div>
</div>
""", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3, gap="medium")

with f1:
    st.markdown("""
    <div class="feat">
      <div class="feat-icon-box" style="background:rgba(99,102,241,.14);color:#818cf8;">📝</div>
      <div class="feat-step" style="color:#4338ca;">Step 01</div>
      <div class="feat-title">Text Pre-processing</div>
      <p class="feat-desc">
        Input is lower-cased and common English stop words —
        <em>the, a, is, in</em> — are stripped, leaving only the
        content-bearing terms that carry real genre signal.
      </p>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="feat">
      <div class="feat-icon-box" style="background:rgba(139,92,246,.14);color:#a78bfa;">🔢</div>
      <div class="feat-step" style="color:#7c3aed;">Step 02</div>
      <div class="feat-title">TF-IDF Vectorisation</div>
      <p class="feat-desc">
        Word and character n-grams are converted to sparse numerical vectors.
        Terms distinctive to a genre score higher than words appearing
        uniformly across all plots.
      </p>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="feat">
      <div class="feat-icon-box" style="background:rgba(34,211,238,.12);color:#22d3ee;">⚡</div>
      <div class="feat-step" style="color:#0891b2;">Step 03</div>
      <div class="feat-title">LinearSVC Classification</div>
      <p class="feat-desc">
        A Linear Support Vector Classifier finds the optimal separating
        hyperplane across 27 genre classes in the high-dimensional
        TF-IDF feature space.
      </p>
    </div>
    """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  <div class="footer-brand">
    <div class="footer-mark">🎬</div>
    <span class="footer-brand-text">Movie AI Studio</span>
  </div>
  <div class="footer-mid">
    CodSoft Machine Learning Internship &nbsp;·&nbsp; Task 1 — Movie Genre Classification
  </div>
  <div class="footer-right">
    scikit-learn &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; TF-IDF + LinearSVC
  </div>
</div>
""", unsafe_allow_html=True)