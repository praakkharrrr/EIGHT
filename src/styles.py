"""
Frosted Glass Aurora / Liquid Glassmorphism theme for EIGHT — AI Crash-Test Lab.
Inspired by the modern Kite AI / VisionOS liquid frosted glass aesthetic.
"""

BRAND_SVG = """<svg width="36" height="36" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="eightGradGlass" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F97316" />
      <stop offset="50%" stop-color="#EC4899" />
      <stop offset="100%" stop-color="#3B82F6" />
    </linearGradient>
  </defs>
  <path d="M 32 30 C 18 30 18 50 32 50 C 46 50 54 70 68 70 C 82 70 82 50 68 50 C 54 50 46 30 32 30 Z" 
        stroke="url(#eightGradGlass)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="32" cy="40" r="4" fill="#F97316" />
  <circle cx="68" cy="60" r="4" fill="#3B82F6" />
</svg>"""

FROSTED_GLASS_CSS = """<style>
/* Import Modern Google Fonts: Plus Jakarta Sans for UI, Silkscreen for pixel accent, JetBrains Mono for code */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Silkscreen:wght@400;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Fix Material Icon ligatures so text like 'keyboard_double' or 'visibili' NEVER appears */
.material-symbols-rounded, 
.material-icons, 
[data-testid="stIconMaterial"], 
[data-testid="stIconMaterial"] * {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    text-transform: none !important;
}

/* Global Aurora Mesh Background */
.stApp {
    background-color: #FDF6EE !important;
    background-image: 
        radial-gradient(at 12% 15%, rgba(253, 186, 116, 0.7) 0px, transparent 55%),
        radial-gradient(at 88% 12%, rgba(252, 165, 165, 0.6) 0px, transparent 50%),
        radial-gradient(at 45% 45%, rgba(254, 240, 138, 0.6) 0px, transparent 60%),
        radial-gradient(at 92% 85%, rgba(186, 230, 253, 0.75) 0px, transparent 55%),
        radial-gradient(at 10% 82%, rgba(196, 181, 253, 0.55) 0px, transparent 50%) !important;
    background-attachment: fixed !important;
    color: #0F172A !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #0F172A !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}

/* Retro-Modern Pixel Title Accent */
.pixel-accent {
    font-family: 'Silkscreen', monospace !important;
    letter-spacing: 0.08em;
    font-weight: 700;
    color: #0F172A;
    display: inline-block;
}

/* -------------------------------------------------------------
   KITE AI FLOATING FROSTED GLASS CAPSULE NAV
   Matches uploaded design template exactly:
   [ EIGHT     Overview   Evaluation Lab   Agent Arena   Verification   Analytics     • OFFLINE SIMULATOR ]
   ------------------------------------------------------------- */
.glass-nav-capsule {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    padding: 10px 32px !important;
    background: rgba(255, 255, 255, 0.75) !important;
    backdrop-filter: blur(28px) !important;
    -webkit-backdrop-filter: blur(28px) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
    border-radius: 9999px !important;
    box-shadow: 
        0 16px 36px rgba(0, 0, 0, 0.04),
        inset 0 1px 2px rgba(255, 255, 255, 1) !important;
    margin: 8px auto 26px auto !important;
    max-width: 980px !important;
}

.glass-nav-brand {
    font-size: 16.5px !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    letter-spacing: -0.03em !important;
    text-decoration: none !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

.glass-nav-links {
    display: flex !important;
    align-items: center !important;
    gap: 28px !important;
}

.glass-nav-link {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    text-decoration: none !important;
    transition: color 0.15s ease, font-weight 0.15s ease !important;
    padding: 4px 6px !important;
    cursor: pointer !important;
}

.glass-nav-link:hover {
    color: #0F172A !important;
    text-decoration: none !important;
}

.glass-nav-link.active {
    color: #0F172A !important;
    font-weight: 800 !important;
    text-decoration: none !important;
}

.glass-nav-status {
    display: flex !important;
    align-items: center !important;
}

/* -------------------------------------------------------------
   HERO DISPLAY FRAME
   ------------------------------------------------------------- */
.hero-glass-frame {
    text-align: center;
    padding: 40px 30px 30px 30px;
    margin-bottom: 24px;
    position: relative;
}

.hero-main-heading {
    font-size: 52px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.1;
    margin-bottom: 12px;
    letter-spacing: -0.04em;
}

.hero-subcard {
    background: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1.5px solid rgba(255, 255, 255, 0.85);
    border-radius: 28px;
    padding: 32px 36px;
    max-width: 720px;
    margin: 20px auto 0 auto;
    box-shadow: 
        0 30px 60px rgba(0, 0, 0, 0.05),
        inset 0 1px 2px rgba(255, 255, 255, 1);
}

.hero-subcard-text {
    font-size: 15px;
    color: #334155;
    line-height: 1.6;
    margin-bottom: 20px;
}

/* Capsule CTA Buttons */
.capsule-btn-row {
    display: flex;
    justify-content: center;
    gap: 14px;
    flex-wrap: wrap;
}

.btn-pill-dark {
    background: #0F172A;
    color: #FFFFFF !important;
    padding: 10px 24px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 13.5px;
    border: none;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.2);
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.btn-pill-light {
    background: #FFFFFF;
    color: #0F172A !important;
    padding: 10px 24px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 13.5px;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

/* -------------------------------------------------------------
   FROSTED GLASS CONTENT CARDS
   ------------------------------------------------------------- */
.eight-card {
    background: rgba(255, 255, 255, 0.55) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.85) !important;
    border-radius: 22px !important;
    padding: 22px 26px !important;
    margin-bottom: 18px !important;
    box-shadow: 
        0 16px 36px rgba(0, 0, 0, 0.04),
        inset 0 1px 2px rgba(255, 255, 255, 1) !important;
    color: #0F172A !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.eight-card:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 24px 48px rgba(0, 0, 0, 0.06),
        inset 0 1px 2px rgba(255, 255, 255, 1) !important;
}

.eight-card-title {
    font-size: 15.5px;
    font-weight: 800;
    color: #0F172A !important;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: -0.01em;
}

/* KPI Card */
.kpi-card {
    background: rgba(255, 255, 255, 0.6) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
    border-radius: 20px !important;
    padding: 20px 22px !important;
    box-shadow: 
        0 14px 30px rgba(0, 0, 0, 0.04),
        inset 0 1px 2px rgba(255, 255, 255, 1) !important;
    text-align: left;
    transition: transform 0.15s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
}

.kpi-value {
    font-size: 34px;
    font-weight: 800;
    color: #0F172A !important;
    line-height: 1.1;
    letter-spacing: -0.03em;
}

.kpi-label {
    font-size: 11.5px;
    font-weight: 700;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 6px;
}

.kpi-subtext {
    font-size: 12px;
    color: #334155 !important;
    margin-top: 4px;
    font-weight: 500;
}

/* Stepper Stage Component */
.pipeline-step {
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1.5px solid rgba(255, 255, 255, 0.85);
    border-radius: 18px;
    padding: 16px 20px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
    margin-bottom: 12px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.03);
}

.step-num {
    background: #0F172A;
    color: #FFFFFF !important;
    font-weight: 800;
    font-size: 12px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.2);
}

.step-body-title {
    font-size: 14px;
    font-weight: 800;
    color: #0F172A !important;
}

.step-body-desc {
    font-size: 12.5px;
    color: #475569 !important;
    line-height: 1.45;
    margin-top: 2px;
}

/* Agent Avatar Badges */
.agent-header-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-radius: 14px;
    margin-bottom: 12px;
}

.badge-baseline {
    background: rgba(147, 51, 234, 0.1);
    border: 1.5px solid rgba(147, 51, 234, 0.25);
    color: #7E22CE !important;
}

.badge-agent-a {
    background: rgba(14, 165, 233, 0.1);
    border: 1.5px solid rgba(14, 165, 233, 0.25);
    color: #0284C7 !important;
}

.badge-agent-b {
    background: rgba(16, 185, 129, 0.1);
    border: 1.5px solid rgba(16, 185, 129, 0.25);
    color: #059669 !important;
}

/* Callouts */
.human-callout {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(20px);
    border-left: 4px solid #0F172A;
    border-radius: 0 14px 14px 0;
    padding: 14px 18px;
    font-size: 13.5px;
    color: #334155 !important;
    margin: 16px 0;
    line-height: 1.55;
    border-top: 1px solid rgba(255, 255, 255, 0.8);
    border-bottom: 1px solid rgba(255, 255, 255, 0.8);
    border-right: 1px solid rgba(255, 255, 255, 0.8);
}

/* -------------------------------------------------------------
   STREAMLIT TABS: FLOATING GLASS CAPSULE TABS
   ------------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255, 255, 255, 0.55) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    padding: 6px;
    border-radius: 9999px !important;
    border: 1.5px solid rgba(255, 255, 255, 0.85) !important;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.03) !important;
    margin-bottom: 24px;
}

.stTabs [data-baseweb="tab"] {
    color: #475569 !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border-radius: 9999px !important;
    padding: 8px 18px !important;
    border: none !important;
    opacity: 1 !important;
    background: transparent !important;
    transition: all 0.15s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #0F172A !important;
    background: rgba(255, 255, 255, 0.6) !important;
}

.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    background: #0F172A !important;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.25) !important;
}

.stTabs [data-baseweb="tab"] p, 
.stTabs [data-baseweb="tab"] span, 
.stTabs [data-baseweb="tab"] div {
    color: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
}

/* -------------------------------------------------------------
   STREAMLIT SIDEBAR: FROSTED GLASS TRANSLUCENCY
   ------------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.45) !important;
    backdrop-filter: blur(32px) !important;
    -webkit-backdrop-filter: blur(32px) !important;
    border-right: 1.5px solid rgba(255, 255, 255, 0.8) !important;
}

/* Sidebar text elements */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {
    color: #0F172A !important;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] small {
    color: #64748B !important;
}

/* Toggles & Checkboxes in Sidebar */
[data-testid="stSidebar"] [data-testid="stCheckbox"] label,
[data-testid="stSidebar"] [data-testid="stToggle"] label,
[data-testid="stSidebar"] [data-testid="stCheckbox"] label p,
[data-testid="stSidebar"] [data-testid="stToggle"] label p {
    color: #0F172A !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* Inputs & Form Controls */
.stTextInput input,
[data-testid="stSidebar"] input {
    background: rgba(255, 255, 255, 0.95) !important;
    color: #0F172A !important;
    border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
    border-radius: 9999px !important;
    padding: 10px 18px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
}

.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] * {
    background: rgba(255, 255, 255, 0.95) !important;
    color: #0F172A !important;
}

.stSelectbox [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="select"] {
    border-radius: 14px !important;
    border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
}

/* Buttons: Capsule Pills — Bright White High Contrast */
.stButton > button,
.stButton > button *,
.stButton > button p,
.stButton > button span,
.stButton > button div,
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button *,
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    line-height: 1.4 !important;
    text-decoration: none !important;
}

.stButton > button,
[data-testid="stSidebar"] .stButton > button {
    background: #0F172A !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 9999px !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.25) !important;
    transition: all 0.2s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.stButton > button:hover,
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1E293B !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.35) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active,
[data-testid="stSidebar"] .stButton > button:active {
    transform: translateY(0px) !important;
}

/* Primary buttons */
.stButton > button[kind="primary"],
.stButton > button[kind="primary"] *,
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span,
.stButton > button[kind="primary"] div,
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"] *,
[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
[data-testid="stSidebar"] .stButton > button[kind="primary"] span,
[data-testid="stSidebar"] .stButton > button[kind="primary"] div {
    background: #0284C7 !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.stButton > button[kind="primary"]:hover,
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #0369A1 !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
}

/* Code block container */
.stCodeBlock {
    border: 1.5px solid rgba(255, 255, 255, 0.8) !important;
    border-radius: 14px !important;
    background-color: rgba(255, 255, 255, 0.85) !important;
}

/* Status Badges */
.badge-mock {
    background: rgba(245, 158, 11, 0.12);
    color: #B45309 !important;
    border: 1px solid rgba(245, 158, 11, 0.3);
    font-weight: 700;
    border-radius: 9999px;
    padding: 4px 12px;
    font-size: 11px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.04em;
}

.badge-real-api {
    background: rgba(16, 185, 129, 0.12);
    color: #047857 !important;
    border: 1px solid rgba(16, 185, 129, 0.3);
    font-weight: 700;
    border-radius: 9999px;
    padding: 4px 12px;
    font-size: 11px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.04em;
}

.pulse-dot-amber {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #F59E0B;
    display: inline-block;
    animation: pulse 2s infinite;
}

.pulse-dot-green {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10B981;
    display: inline-block;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.85); }
    100% { opacity: 1; transform: scale(1); }
}

/* Stats Pill Strip */
.stats-strip {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 18px;
}

.stat-pill {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    border: 1.2px solid rgba(255, 255, 255, 0.9);
    border-radius: 9999px;
    padding: 6px 16px;
    font-size: 12.5px;
    font-weight: 600;
    color: #334155;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

/* Dataframe Glass Styling */
[data-testid="stDataFrame"] {
    border: 1.5px solid rgba(255, 255, 255, 0.85) !important;
    border-radius: 16px !important;
    background: rgba(255, 255, 255, 0.6) !important;
    backdrop-filter: blur(20px) !important;
    overflow: hidden;
}

/* Expander glass styling */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.45) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    border-radius: 14px !important;
    margin-top: 8px !important;
}
</style>"""

# Backwards compatibility alias
MASTERCLASS_CSS = FROSTED_GLASS_CSS

