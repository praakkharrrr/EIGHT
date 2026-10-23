"""
Enhanced styles, typography, branding, and modern UI components for EIGHT — AI Crash-Test Lab.
"""

BRAND_SVG = """
<svg width="48" height="48" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="eightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="45%" stop-color="#818CF8" />
      <stop offset="100%" stop-color="#0284C7" />
    </linearGradient>
    <filter id="neonGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  <!-- Stylized Figure-8 / Infinity Loop -->
  <path d="M 32 30 C 18 30 18 50 32 50 C 46 50 54 70 68 70 C 82 70 82 50 68 50 C 54 50 46 30 32 30 Z" 
        stroke="url(#eightGrad)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" filter="url(#neonGlow)"/>
  <circle cx="32" cy="40" r="3.5" fill="#38BDF8" />
  <circle cx="68" cy="60" r="3.5" fill="#818CF8" />
</svg>
"""

CUSTOM_CSS = """
<style>
/* Import Modern Google Fonts: Plus Jakarta Sans for UI, JetBrains Mono for Code */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Global Reset & Base Theme */
.stApp {
    background-color: #0B0F19 !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.05) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.05) 0px, transparent 50%) !important;
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    letter-spacing: -0.01em;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #F8FAFC !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
}

/* Top App Header / Hero Banner */
.eight-header {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 28px;
    background: linear-gradient(135deg, rgba(17, 24, 39, 0.85) 0%, rgba(15, 23, 42, 0.75) 100%);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
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
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.eight-tagline {
    font-size: 13.5px;
    color: #94A3B8;
    margin-top: 4px;
    font-weight: 400;
}

/* Quick Stats Bar */
.stats-strip {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.stat-pill {
    font-size: 11.5px;
    color: #CBD5E1;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 4px 10px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Glassmorphism Cards */
.eight-card {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 18px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.eight-card:hover {
    border-color: rgba(56, 189, 248, 0.25);
}

.eight-card-title {
    font-size: 15px;
    font-weight: 600;
    color: #38BDF8;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.01em;
}

/* Status Badges */
.badge-real-api {
    background: rgba(16, 185, 129, 0.12);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.28);
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.15);
}

.badge-mock {
    background: rgba(245, 158, 11, 0.12);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.28);
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.1);
}

.pulse-dot-green {
    width: 7px;
    height: 7px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #10B981;
}

.pulse-dot-amber {
    width: 7px;
    height: 7px;
    background-color: #F59E0B;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #F59E0B;
}

/* Outcome Pills */
.badge-helped {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 4px 12px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 12.5px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.badge-hurt {
    background: rgba(244, 63, 94, 0.15);
    color: #FB7185;
    border: 1px solid rgba(244, 63, 94, 0.3);
    padding: 4px 12px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 12.5px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.badge-no-effect {
    background: rgba(148, 163, 184, 0.12);
    color: #94A3B8;
    border: 1px solid rgba(148, 163, 184, 0.25);
    padding: 4px 12px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 12.5px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Metric KPI Blocks */
.kpi-card {
    background: linear-gradient(180deg, #131B2E 0%, #0F172A 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    transition: all 0.2s ease;
}

.kpi-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #38BDF8, #818CF8);
    opacity: 0.8;
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(56, 189, 248, 0.3);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}

.kpi-value {
    font-size: 32px;
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.1;
    margin-bottom: 6px;
    letter-spacing: -0.03em;
}

.kpi-label {
    font-size: 12px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.kpi-subtext {
    font-size: 11.5px;
    color: #64748B;
    margin-top: 6px;
}

/* Stepper Stage Component */
.pipeline-step {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 16px 18px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
    margin-bottom: 12px;
}

.step-num {
    background: linear-gradient(135deg, #0284C7, #38BDF8);
    color: #FFFFFF;
    font-weight: 800;
    font-size: 13px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4);
}

.step-body-title {
    font-size: 14px;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 2px;
}

.step-body-desc {
    font-size: 12.5px;
    color: #94A3B8;
    line-height: 1.4;
}

/* Agent Avatar Badges */
.agent-header-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 14px;
}

.badge-baseline {
    background: rgba(147, 51, 234, 0.12);
    border: 1px solid rgba(147, 51, 234, 0.25);
    color: #C084FC;
}

.badge-agent-a {
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(14, 165, 233, 0.25);
    color: #38BDF8;
}

.badge-agent-b {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #34D399;
}

/* Callout Note */
.human-callout {
    background: rgba(30, 41, 59, 0.6);
    border-left: 3px solid #38BDF8;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    font-size: 13px;
    color: #CBD5E1;
    margin: 14px 0;
    line-height: 1.5;
}

/* Sidebar Polish */
[data-testid="stSidebar"] {
    background-color: #080D1A !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    padding-top: 1.5rem !important;
}

/* Modern Tab Navigation */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #0E1424;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #F8FAFC !important;
    background: rgba(255, 255, 255, 0.04) !important;
}

.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%) !important;
    box-shadow: 0 2px 10px rgba(2, 132, 199, 0.35) !important;
}

/* Polished Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3) !important;
    transition: all 0.2s ease !important;
    letter-spacing: -0.01em !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0369A1 0%, #1D4ED8 100%) !important;
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Button style */
button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Code block container tweaks */
.stCodeBlock {
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    background-color: #0D121F !important;
}

/* Inputs and Selectboxes */
.stTextInput > div > div > input, .stSelectbox > div > div {
    background-color: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    color: #F8FAFC !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: #111827 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    color: #CBD5E1 !important;
}
</style>
"""
