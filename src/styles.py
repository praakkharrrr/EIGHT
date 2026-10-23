"""
Styles, branding, and custom HTML/SVG components for EIGHT — AI Crash-Test Lab.
"""

BRAND_SVG = """
<svg width="44" height="44" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="eightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="50%" stop-color="#6366F1" />
      <stop offset="100%" stop-color="#0284C7" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
  <!-- Stylized Figure-8 / Infinity Loop -->
  <path d="M 30 32 C 16 32 16 50 30 50 C 44 50 56 68 70 68 C 84 68 84 50 70 50 C 56 50 44 32 30 32 Z" 
        stroke="url(#eightGrad)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>
  <circle cx="30" cy="41" r="3" fill="#38BDF8" />
  <circle cx="70" cy="59" r="3" fill="#818CF8" />
</svg>
"""

CUSTOM_CSS = """
<style>
/* Main dark background and base styles */
.stApp {
    background-color: #0A0E17 !important;
    color: #F8FAFC !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Header & Typography */
h1, h2, h3, h4, h5, h6 {
    color: #F8FAFC !important;
    font-weight: 700;
    letter-spacing: -0.02em;
}

/* Top bar banner */
.eight-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.6) 100%);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.eight-title {
    font-size: 26px;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: 0.05em;
}

.eight-tagline {
    font-size: 13px;
    color: #94A3B8;
    margin: 2px 0 0 0;
    font-weight: 400;
}

/* Glass card styling */
.eight-card {
    background: #111827;
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.eight-card-title {
    font-size: 16px;
    font-weight: 600;
    color: #38BDF8;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Status Badges */
.badge-real-api {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.badge-mock {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.badge-helped {
    background: rgba(16, 185, 129, 0.2);
    color: #10B981;
    border: 1px solid #10B981;
    padding: 4px 12px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 13px;
}

.badge-hurt {
    background: rgba(239, 68, 68, 0.2);
    color: #EF4444;
    border: 1px solid #EF4444;
    padding: 4px 12px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 13px;
}

.badge-no-effect {
    background: rgba(148, 163, 184, 0.2);
    color: #94A3B8;
    border: 1px solid #64748B;
    padding: 4px 12px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 13px;
}

/* Custom metric block */
.metric-box {
    background: #0F172A;
    border: 1px solid rgba(56, 189, 248, 0.12);
    border-radius: 8px;
    padding: 14px 16px;
    text-align: center;
}

.metric-value {
    font-size: 28px;
    font-weight: 800;
    color: #38BDF8;
    line-height: 1.1;
}

.metric-label {
    font-size: 12px;
    color: #94A3B8;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Code block container tweaks */
.stCodeBlock {
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    border-radius: 8px !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #080C14 !important;
    border-right: 1px solid rgba(56, 189, 248, 0.12) !important;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
    border-bottom: 1px solid rgba(56, 189, 248, 0.15);
}

.stTabs [data-baseweb="tab"] {
    color: #94A3B8 !important;
    font-weight: 600 !important;
    border-radius: 6px 6px 0 0;
    padding: 8px 16px !important;
}

.stTabs [aria-selected="true"] {
    color: #38BDF8 !important;
    border-bottom: 2px solid #38BDF8 !important;
    background: rgba(56, 189, 248, 0.05) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0369A1 0%, #1D4ED8 100%) !important;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.5) !important;
    transform: translateY(-1px) !important;
}
</style>
"""
