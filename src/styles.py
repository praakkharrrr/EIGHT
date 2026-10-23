"""
Styles, branding, and dynamic Dark / Light theme engine for EIGHT — AI Crash-Test Lab.
"""

BRAND_SVG = """<svg width="44" height="44" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="eightGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="50%" stop-color="#6366F1" />
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

def get_theme_css(theme: str = "dark") -> str:
    """Returns dynamic CSS tailored for either dark or light mode."""
    is_dark = (theme.lower() == "dark")
    
    if is_dark:
        bg_color = "#0B0F19"
        bg_gradient = "radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.05) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.05) 0px, transparent 50%)"
        card_bg = "#111827"
        card_secondary = "#0F172A"
        border_color = "rgba(255, 255, 255, 0.08)"
        border_hover = "rgba(56, 189, 248, 0.3)"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        text_muted = "#64748B"
        sidebar_bg = "#080D1A"
        header_bg = "linear-gradient(135deg, rgba(17, 24, 39, 0.9) 0%, rgba(15, 23, 42, 0.8) 100%)"
        kpi_bg = "linear-gradient(180deg, #131B2E 0%, #0F172A 100%)"
        code_bg = "#0D121F"
        tab_bg = "#0E1424"
        tab_active_text = "#FFFFFF"
        stat_pill_bg = "rgba(255, 255, 255, 0.04)"
        callout_bg = "rgba(30, 41, 59, 0.6)"
    else:
        bg_color = "#F8FAFC"
        bg_gradient = "radial-gradient(at 0% 0%, rgba(224, 242, 254, 0.6) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(241, 245, 249, 0.6) 0px, transparent 50%)"
        card_bg = "#FFFFFF"
        card_secondary = "#F1F5F9"
        border_color = "rgba(15, 23, 42, 0.1)"
        border_hover = "rgba(2, 132, 199, 0.4)"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_muted = "#64748B"
        sidebar_bg = "#F1F5F9"
        header_bg = "linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%)"
        kpi_bg = "linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)"
        code_bg = "#F8FAFC"
        tab_bg = "#E2E8F0"
        tab_active_text = "#FFFFFF"
        stat_pill_bg = "rgba(15, 23, 42, 0.04)"
        callout_bg = "rgba(241, 245, 249, 0.9)"

    return f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Main App Wrapper */
.stApp {{
    background-color: {bg_color} !important;
    background-image: {bg_gradient} !important;
    color: {text_primary} !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {text_primary} !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}}

p, span, label, div {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* Top Hero Header */
.eight-header {{
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 20px 24px;
    background: {header_bg};
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid {border_color};
    border-radius: 14px;
    margin-bottom: 22px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, {'0.3' if is_dark else '0.06'});
}}

.eight-title-group {{
    flex-grow: 1;
}}

.eight-title-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
}}

.eight-main-title {{
    font-size: 24px;
    font-weight: 800;
    color: {text_primary};
    margin: 0;
    letter-spacing: -0.02em;
}}

.eight-tagline {{
    font-size: 13px;
    color: {text_secondary};
    margin-top: 3px;
    font-weight: 500;
}}

.stats-strip {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid {border_color};
}}

.stat-pill {{
    font-size: 11.5px;
    color: {text_secondary};
    background: {stat_pill_bg};
    border: 1px solid {border_color};
    padding: 3px 10px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}

/* Content Cards */
.eight-card {{
    background: {card_bg};
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, {'0.25' if is_dark else '0.04'});
    transition: border-color 0.15s ease, transform 0.15s ease;
}}

.eight-card:hover {{
    border-color: {border_hover};
}}

.eight-card-title {{
    font-size: 14.5px;
    font-weight: 700;
    color: {'#38BDF8' if is_dark else '#0284C7'};
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

/* Status Badges */
.badge-real-api {{
    background: rgba(16, 185, 129, {'0.15' if is_dark else '0.12'});
    color: {'#34D399' if is_dark else '#059669'};
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}

.badge-mock {{
    background: rgba(245, 158, 11, {'0.15' if is_dark else '0.12'});
    color: {'#FBBF24' if is_dark else '#D97706'};
    border: 1px solid rgba(245, 158, 11, 0.3);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}

.pulse-dot-green {{
    width: 7px;
    height: 7px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px #10B981;
}}

.pulse-dot-amber {{
    width: 7px;
    height: 7px;
    background-color: #F59E0B;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px #F59E0B;
}}

/* KPI Metric Cards */
.kpi-card {{
    background: {kpi_bg};
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, {'0.25' if is_dark else '0.04'});
    transition: transform 0.15s ease, border-color 0.15s ease;
}}

.kpi-card::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #38BDF8, #818CF8);
}}

.kpi-card:hover {{
    transform: translateY(-2px);
    border-color: {border_hover};
}}

.kpi-value {{
    font-size: 30px;
    font-weight: 800;
    color: {text_primary};
    line-height: 1.1;
    letter-spacing: -0.02em;
}}

.kpi-label {{
    font-size: 11.5px;
    font-weight: 700;
    color: {text_secondary};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 6px;
}}

.kpi-subtext {{
    font-size: 11.5px;
    color: {text_muted};
    margin-top: 4px;
}}

/* Stepper Stage Component */
.pipeline-step {{
    background: {card_bg};
    border: 1px solid {border_color};
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
    margin-bottom: 10px;
}}

.step-num {{
    background: linear-gradient(135deg, #0284C7, #38BDF8);
    color: #FFFFFF;
    font-weight: 800;
    font-size: 12px;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.step-body-title {{
    font-size: 13.5px;
    font-weight: 700;
    color: {text_primary};
}}

.step-body-desc {{
    font-size: 12px;
    color: {text_secondary};
    line-height: 1.4;
    margin-top: 2px;
}}

/* Agent Avatar Badges */
.agent-header-badge {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 12px;
}}

.badge-baseline {{
    background: rgba(147, 51, 234, {'0.12' if is_dark else '0.08'});
    border: 1px solid rgba(147, 51, 234, 0.25);
    color: {'#C084FC' if is_dark else '#7E22CE'};
}}

.badge-agent-a {{
    background: rgba(14, 165, 233, {'0.12' if is_dark else '0.08'});
    border: 1px solid rgba(14, 165, 233, 0.25);
    color: {'#38BDF8' if is_dark else '#0284C7'};
}}

.badge-agent-b {{
    background: rgba(16, 185, 129, {'0.12' if is_dark else '0.08'});
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: {'#34D399' if is_dark else '#059669'};
}}

/* Callouts */
.human-callout {{
    background: {callout_bg};
    border-left: 3px solid #38BDF8;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 13px;
    color: {text_secondary};
    margin: 14px 0;
    line-height: 1.5;
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background-color: {sidebar_bg} !important;
    border-right: 1px solid {border_color} !important;
}}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background: {tab_bg};
    padding: 5px;
    border-radius: 10px;
    border: 1px solid {border_color};
    margin-bottom: 18px;
}}

.stTabs [data-baseweb="tab"] {{
    color: {text_secondary} !important;
    font-weight: 600 !important;
    font-size: 12.5px !important;
    border-radius: 6px !important;
    padding: 7px 14px !important;
    border: none !important;
}}

.stTabs [aria-selected="true"] {{
    color: {tab_active_text} !important;
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%) !important;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.35) !important;
}}

/* Buttons */
.stButton > button {{
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    box-shadow: 0 2px 10px rgba(2, 132, 199, 0.3) !important;
}}

.stButton > button:hover {{
    background: linear-gradient(135deg, #0369A1 0%, #1D4ED8 100%) !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.45) !important;
    transform: translateY(-1px) !important;
}}

/* Code block container tweaks */
.stCodeBlock {{
    border: 1px solid {border_color} !important;
    border-radius: 8px !important;
    background-color: {code_bg} !important;
}}
</style>"""
