"""
Masterclass UI Styles & Branding for EIGHT — AI Crash-Test Lab.
Crafted for flawless contrast, crisp typography, and zero icon/ligature breakage.
"""

BRAND_SVG = """<svg width="42" height="42" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="eightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="45%" stop-color="#818CF8" />
      <stop offset="100%" stop-color="#0284C7" />
    </linearGradient>
    <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  <path d="M 32 30 C 18 30 18 50 32 50 C 46 50 54 70 68 70 C 82 70 82 50 68 50 C 54 50 46 30 32 30 Z" 
        stroke="url(#eightGrad)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" filter="url(#neonGlow)"/>
  <circle cx="32" cy="40" r="3.5" fill="#38BDF8" />
  <circle cx="68" cy="60" r="3.5" fill="#818CF8" />
</svg>"""

MASTERCLASS_CSS = """<style>
/* Import Inter for ultra-clean developer tool typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Apply font safely without breaking Material Symbols / icon ligatures */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Fix Material Icon ligatures so text like 'keyboard_double' or 'visibili' NEVER appears */
.material-symbols-rounded, 
.material-icons, 
[data-testid="stIconMaterial"], 
[data-testid="stIconMaterial"] * {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    text-transform: none !important;
}

/* Background Atmosphere */
.stApp {
    background-color: #0B0F19 !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.06) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.06) 0px, transparent 50%) !important;
    color: #F8FAFC !important;
}

/* Top App Header Banner */
.eight-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 22px 26px;
    background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
}

.eight-title-group {
    flex-grow: 1;
}

.eight-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}

.eight-main-title {
    font-size: 26px;
    font-weight: 800;
    color: #FFFFFF !important;
    margin: 0;
    letter-spacing: -0.025em;
}

.eight-tagline {
    font-size: 13.5px;
    color: #94A3B8 !important;
    margin-top: 4px;
    font-weight: 400;
}

.stats-strip {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.stat-pill {
    font-size: 11.5px;
    color: #CBD5E1 !important;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 4px 10px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
}

/* Premium Card Component */
.eight-card {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    transition: border-color 0.15s ease, transform 0.15s ease;
}

.eight-card:hover {
    border-color: rgba(56, 189, 248, 0.3);
}

.eight-card-title {
    font-size: 15px;
    font-weight: 700;
    color: #38BDF8 !important;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Status Badges */
.badge-real-api {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399 !important;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.badge-mock {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24 !important;
    border: 1px solid rgba(245, 158, 11, 0.3);
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.pulse-dot-green {
    width: 7px;
    height: 7px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px #10B981;
}

.pulse-dot-amber {
    width: 7px;
    height: 7px;
    background-color: #F59E0B;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px #F59E0B;
}

/* Metric KPI Card */
.kpi-card {
    background: linear-gradient(180deg, #131B2E 0%, #0F172A 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.kpi-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #38BDF8, #818CF8);
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(56, 189, 248, 0.35);
}

.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #F8FAFC !important;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.kpi-label {
    font-size: 11.5px;
    font-weight: 700;
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 6px;
}

.kpi-subtext {
    font-size: 11.5px;
    color: #64748B !important;
    margin-top: 4px;
}

/* Stepper Stage Component */
.pipeline-step {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
    margin-bottom: 10px;
}

.step-num {
    background: linear-gradient(135deg, #0284C7, #38BDF8);
    color: #FFFFFF !important;
    font-weight: 800;
    font-size: 12px;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.step-body-title {
    font-size: 13.5px;
    font-weight: 700;
    color: #F8FAFC !important;
}

.step-body-desc {
    font-size: 12px;
    color: #94A3B8 !important;
    line-height: 1.4;
    margin-top: 2px;
}

/* Agent Avatar Badges */
.agent-header-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 12px;
}

.badge-baseline {
    background: rgba(147, 51, 234, 0.12);
    border: 1px solid rgba(147, 51, 234, 0.3);
    color: #C084FC !important;
}

.badge-agent-a {
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(14, 165, 233, 0.3);
    color: #38BDF8 !important;
}

.badge-agent-b {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34D399 !important;
}

/* Callouts */
.human-callout {
    background: rgba(30, 41, 59, 0.7);
    border-left: 3px solid #38BDF8;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 13px;
    color: #CBD5E1 !important;
    margin: 14px 0;
    line-height: 1.5;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #080D1A !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

/* -------------------------------------------------------------
   STREAMLIT TABS: GUARANTEED HIGH CONTRAST & LEGIBILITY
   ------------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #0E1424 !important;
    padding: 6px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 22px;
}

/* Inactive tabs: crisp, high contrast readable slate */
.stTabs [data-baseweb="tab"] {
    color: #CBD5E1 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    border: none !important;
    opacity: 1 !important;
    background: transparent !important;
    transition: all 0.15s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #38BDF8 !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

/* Active tab: glowing electric blue gradient */
.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%) !important;
    box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4) !important;
}

/* Ensure tab text elements inside buttons inherit colors */
.stTabs [data-baseweb="tab"] p, 
.stTabs [data-baseweb="tab"] span, 
.stTabs [data-baseweb="tab"] div {
    color: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
}

/* Primary Button Styling */
.stButton > button {
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    box-shadow: 0 2px 10px rgba(2, 132, 199, 0.3) !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0369A1 0%, #1D4ED8 100%) !important;
    box-shadow: 0 4px 16px rgba(2, 132, 199, 0.5) !important;
    transform: translateY(-1px) !important;
}

/* Inputs & Form Controls */
.stTextInput input, 
.stSelectbox [data-baseweb="select"] {
    background-color: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    color: #F8FAFC !important;
}

/* Code block container */
.stCodeBlock {
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px !important;
    background-color: #0D121F !important;
}
</style>"""
