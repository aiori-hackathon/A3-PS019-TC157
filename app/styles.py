"""Custom CSS design system for AEGIS Privacy Evidence Inventory.
Dark 'cyber' theme with glassmorphism, neon cyan/teal accents, Google Fonts, and smooth transitions.
"""

def get_cyber_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-primary: #0a0e17;
        --bg-card: rgba(16, 24, 40, 0.65);
        --bg-card-hover: rgba(22, 34, 56, 0.85);
        --neon-teal: #00f2fe;
        --neon-cyan: #4facfe;
        --neon-violet: #8a2be2;
        --neon-emerald: #10b981;
        --neon-amber: #f59e0b;
        --neon-rose: #f43f5e;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-subtle: rgba(0, 242, 254, 0.16);
        --border-glow: rgba(0, 242, 254, 0.35);
    }

    /* Streamlit Global Overrides */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }

    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 85% 85%, rgba(138, 43, 226, 0.06) 0%, transparent 45%),
                    #0a0f1d !important;
    }

    /* Hide default Streamlit clutter (but keep the sidebar arrow working) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppDeployButton"] {display: none !important;}
    [data-testid="stMainMenu"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}

    /* Keep the header and toolbar so the sidebar arrow stays visible */
    header, [data-testid="stHeader"] {
        background: transparent !important;
        visibility: visible !important;
    }
    [data-testid="stToolbar"] {visibility: visible !important;}

    /* Arrow that re-opens the sidebar: always visible, teal colour */
    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        color: #00f2fe !important;
    }
    [data-testid="stExpandSidebarButton"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        fill: #00f2fe !important;
        color: #00f2fe !important;
    }

    /* Remove the button that collapses the sidebar, so it can never be hidden by accident */
    [data-testid="stSidebarCollapseButton"] {display: none !important;}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 15, 29, 0.95) !important;
        border-right: 1px solid var(--border-subtle);
        backdrop-filter: blur(20px);
    }

    [data-testid="stSidebarNav"] {
        padding-top: 1.5rem;
    }

    /* Cyber Glassmorphism Cards */
    .cyber-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.5rem;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1.2rem;
    }

    .cyber-card:hover {
        border-color: var(--border-glow);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 242, 254, 0.12);
    }

    /* KPI Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(16, 24, 40, 0.75) 0%, rgba(12, 19, 34, 0.6) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        backdrop-filter: blur(12px);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--neon-teal), transparent);
    }

    .metric-card:hover {
        border-color: var(--neon-cyan);
        box-shadow: 0 6px 24px rgba(0, 242, 254, 0.15);
    }

    .metric-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 0.4rem;
        font-weight: 600;
    }

    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #ffffff 30%, var(--neon-teal) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }

    .metric-subtext {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.3rem;
    }

    /* Disclaimer Cyber Banner */
    .cyber-disclaimer {
        background: rgba(14, 23, 42, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-left: 4px solid var(--neon-teal);
        border-radius: 8px;
        padding: 0.85rem 1.25rem;
        margin: 1rem 0 1.5rem 0;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        backdrop-filter: blur(8px);
    }

    .disclaimer-icon {
        color: var(--neon-teal);
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    /* Badges & Pills */
    .badge-tier-high {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 9999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        display: inline-flex;
        align-items: center;
    }

    .badge-tier-medium {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 9999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        display: inline-flex;
        align-items: center;
    }

    .badge-tier-low {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 9999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        display: inline-flex;
        align-items: center;
    }

    .badge-gap-critical {
        background: rgba(244, 63, 94, 0.2);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.4);
        border-radius: 6px;
        padding: 0.25rem 0.6rem;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .badge-gap-high {
        background: rgba(249, 115, 22, 0.2);
        color: #fb923c;
        border: 1px solid rgba(249, 115, 22, 0.4);
        border-radius: 6px;
        padding: 0.25rem 0.6rem;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .badge-gap-compliant {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        padding: 0.25rem 0.6rem;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Code & Mono Badges */
    .mono-token {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        background: rgba(0, 242, 254, 0.08);
        border: 1px solid rgba(0, 242, 254, 0.2);
        color: #7dd3fc;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.15) 0%, rgba(79, 172, 254, 0.25) 100%) !important;
        color: #ffffff !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.15) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.3) 0%, rgba(79, 172, 254, 0.45) 100%) !important;
        border-color: var(--neon-teal) !important;
        box-shadow: 0 6px 22px rgba(0, 242, 254, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* Inputs, Selectboxes, Textareas */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--neon-teal) !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.25) !important;
    }

    /* Dataframe Table styling */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--neon-teal), var(--neon-cyan)) !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.6);
    }

    /* Sidebar Radio Nav Styling */
    [data-testid="stSidebar"] .stRadio > label {
        color: var(--text-secondary) !important;
        font-size: 0.9rem;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.2rem;
    }

    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        transition: background 0.2s ease;
        margin-bottom: 0.1rem;
    }

    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover {
        background: rgba(0, 242, 254, 0.08);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(10, 15, 29, 0.5);
        border-radius: 10px;
        padding: 0.2rem;
        gap: 0.2rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: var(--text-secondary) !important;
        font-weight: 500;
        font-size: 0.88rem;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(0, 242, 254, 0.12) !important;
        color: var(--neon-teal) !important;
        border-bottom: 2px solid var(--neon-teal) !important;
    }

    /* Info / Success / Warning Box styling */
    .stAlert {
        border-radius: 10px !important;
        border: 1px solid var(--border-subtle) !important;
    }

    /* Slider */
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        color: var(--neon-teal) !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.12) 0%, rgba(79, 172, 254, 0.2) 100%) !important;
        color: #ffffff !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.25) 0%, rgba(79, 172, 254, 0.4) 100%) !important;
        box-shadow: 0 6px 22px rgba(0, 242, 254, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .metric-value { font-size: 1.5rem; }
        .cyber-card { padding: 1rem; }
    }

    /* Animated loading pulse for scans */
    @keyframes pulse-teal {
        0%, 100% { box-shadow: 0 0 8px rgba(0, 242, 254, 0.3); }
        50% { box-shadow: 0 0 20px rgba(0, 242, 254, 0.7); }
    }

    .stProgress > div {
        animation: pulse-teal 2s ease-in-out infinite;
        border-radius: 999px !important;
    }
    </style>
    """