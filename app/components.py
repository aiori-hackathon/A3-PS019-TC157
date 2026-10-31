"""UI components, SVG branding, and custom Plotly charts for AEGIS Privacy Scanner."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

CYBER_PALETTE = {
    "teal": "#00f2fe",
    "cyan": "#4facfe",
    "violet": "#8a2be2",
    "emerald": "#10b981",
    "amber": "#f59e0b",
    "rose": "#f43f5e",
    "muted": "#64748b",
    "text": "#f8fafc",
    "card_bg": "rgba(16, 24, 40, 0.75)",
}


def render_hero_header():
    """Render branded hero header with custom inline SVG cyber shield logo."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 1.2rem; padding: 1rem 0 1.5rem 0; border-bottom: 1px solid rgba(0, 242, 254, 0.18); margin-bottom: 1.5rem;">
            <div style="flex-shrink: 0;">
                <svg width="54" height="54" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#00f2fe"/>
                            <stop offset="100%" stop-color="#4facfe"/>
                        </linearGradient>
                        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur stdDeviation="3" result="blur" />
                            <feComposite in="SourceGraphic" in2="blur" operator="over" />
                        </filter>
                    </defs>
                    <path d="M32 4L10 14V28C10 43 19.5 53.5 32 60C44.5 53.5 54 43 54 28V14L32 4Z" 
                          stroke="url(#shieldGrad)" stroke-width="2.5" fill="rgba(0, 242, 254, 0.08)" filter="url(#glow)"/>
                    <path d="M32 18L18 25V33C18 41 23.5 48 32 52C40.5 48 46 41 46 33V25L32 18Z" 
                          stroke="#8a2be2" stroke-width="1.8" fill="rgba(138, 43, 226, 0.12)"/>
                    <circle cx="32" cy="33" r="5" fill="#00f2fe"/>
                    <path d="M32 38V43" stroke="#00f2fe" stroke-width="2.5" stroke-linecap="round"/>
                </svg>
            </div>
            <div>
                <div style="font-size: 1.7rem; font-weight: 800; letter-spacing: -0.02em; background: linear-gradient(90deg, #ffffff 10%, #00f2fe 70%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    AEGIS PRIVACY DISCOVERY & EVIDENCE INVENTORY
                </div>
                <div style="font-size: 0.88rem; color: #94a3b8; font-weight: 500; letter-spacing: 0.02em;">
                    Autonomous Personal-Data Discovery • Cryptographic Checksums • Privacy Compliance Gap Engine (AIORI-3 / PS-019)
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer_banner():
    """Render statutory disclaimer separating technical evidence from legal advice."""
    st.markdown(
        """
        <div class="cyber-disclaimer">
            <span class="disclaimer-icon">🛡️</span>
            <div>
                <strong style="color: #00f2fe;">TECHNICAL EVIDENCE ONLY • NOT LEGAL ADVICE</strong> — 
                Automated detection constitutes probabilistic technical evidence of personal data presence. 
                Lawful basis assessment, RoPA validation, and statutory determinations must be performed by human legal counsel.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, subtext: str = "", delta: str = ""):
    """Render animated glassmorphism metric tile."""
    delta_html = f"<span style='color: #34d399; font-size: 0.75rem; margin-left: 0.4rem;'>{delta}</span>" if delta else ""
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}{delta_html}</div>
        <div class="metric-subtext">{subtext}</div>
    </div>
    """


def render_confidence_badge(score: float, tier: str) -> str:
    """Return HTML confidence badge with cyber pill styling."""
    pct = round(score * 100, 1)
    if tier == "High":
        return f'<span class="badge-tier-high">● High ({pct}%)</span>'
    elif tier == "Medium":
        return f'<span class="badge-tier-medium">● Medium ({pct}%)</span>'
    elif tier == "Low":
        return f'<span class="badge-tier-low">▲ Low ({pct}%)</span>'
    else:
        return f'<span style="color: #64748b; font-size: 0.75rem;">None ({pct}%)</span>'


def render_gap_chip(severity: str) -> str:
    """Return HTML chip for privacy compliance gap severity."""
    if severity == "Critical Gap":
        return '<span class="badge-gap-critical">⚠️ CRITICAL GAP</span>'
    elif severity == "High Gap":
        return '<span class="badge-gap-high">⚡ HIGH GAP</span>'
    elif severity == "Medium Gap":
        return '<span style="background: rgba(234, 179, 8, 0.2); color: #facc15; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; font-size: 0.75rem;">MED GAP</span>'
    elif severity == "Declared":
        return '<span class="badge-gap-compliant">✓ DECLARED</span>'
    return f'<span style="color: #64748b; font-size: 0.75rem;">{severity}</span>'


# ==========================================
# PLOTLY CYBER CHARTS
# ==========================================

def get_base_plotly_layout(title: str = "") -> dict:
    """Shared glassmorphism dark theme layout for Plotly visuals."""
    return dict(
        title=dict(text=title, font=dict(family="Inter", size=15, color="#f8fafc"), x=0.02, y=0.96),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8", size=12),
        margin=dict(l=30, r=30, t=50, b=30),
        legend=dict(font=dict(color="#f8fafc", size=11), orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_family="Inter", font_color="#f8fafc"),
    )


def render_data_class_donut(inventory_df: pd.DataFrame) -> go.Figure:
    """Render Donut chart showing distribution across detected PII classes."""
    pii_df = inventory_df[inventory_df["is_pii"] == True]
    counts = pii_df["detected_class"].value_counts().reset_index()
    counts.columns = ["Data Class", "Count"]

    color_map = {
        "Name": CYBER_PALETTE["teal"],
        "Email": CYBER_PALETTE["cyan"],
        "Phone": CYBER_PALETTE["violet"],
        "Government ID": CYBER_PALETTE["amber"],
        "Date of Birth": CYBER_PALETTE["emerald"],
    }
    colors = [color_map.get(c, "#38bdf8") for c in counts["Data Class"]]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=counts["Data Class"],
                values=counts["Count"],
                hole=0.62,
                marker=dict(colors=colors, line=dict(color="#0a0f1d", width=2)),
                textinfo="label+value",
                textposition="outside",
                hoverinfo="label+value+percent",
            )
        ]
    )
    layout = get_base_plotly_layout("Personal Data Class Breakdown")
    fig.update_layout(**layout)
    return fig


def render_table_heatmap(inventory_df: pd.DataFrame) -> go.Figure:
    """Render Heatmap of PII candidate count cross-tabulated by dataset table and data class."""
    pii_df = inventory_df[inventory_df["is_pii"] == True]
    ct = pd.crosstab(pii_df["table_name"], pii_df["detected_class"])
    
    fig = go.Figure(
        data=go.Heatmap(
            z=ct.values,
            x=ct.columns.tolist(),
            y=ct.index.tolist(),
            colorscale=[[0, "rgba(15,23,42,0.6)"], [0.5, "rgba(79,172,254,0.5)"], [1, "#00f2fe"]],
            showscale=True,
            text=ct.values,
            texttemplate="%{text}",
            textfont=dict(color="#ffffff", size=13, family="Inter"),
        )
    )
    layout = get_base_plotly_layout("PII Density Matrix by Table")
    fig.update_layout(**layout)
    fig.update_xaxes(side="bottom", tickfont=dict(color="#f8fafc"))
    fig.update_yaxes(tickfont=dict(color="#f8fafc"))
    return fig


def render_precision_recall_chart(per_class_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart for Precision, Recall, and F1 per class."""
    df_plot = per_class_df[per_class_df["Data Class"] != "Non-PII"]
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Precision",
        x=df_plot["Data Class"],
        y=(df_plot["Precision"] * 100).round(1),
        marker_color=CYBER_PALETTE["teal"],
        text=(df_plot["Precision"] * 100).round(1).astype(str) + "%",
        textposition="auto",
    ))
    fig.add_trace(go.Bar(
        name="Recall",
        x=df_plot["Data Class"],
        y=(df_plot["Recall"] * 100).round(1),
        marker_color=CYBER_PALETTE["cyan"],
        text=(df_plot["Recall"] * 100).round(1).astype(str) + "%",
        textposition="auto",
    ))
    fig.add_trace(go.Bar(
        name="F1-Score",
        x=df_plot["Data Class"],
        y=(df_plot["F1-Score"] * 100).round(1),
        marker_color=CYBER_PALETTE["violet"],
        text=(df_plot["F1-Score"] * 100).round(1).astype(str) + "%",
        textposition="auto",
    ))

    layout = get_base_plotly_layout("Per-Class Benchmark Metrics (Precision / Recall / F1)")
    fig.update_layout(**layout, barmode="group", yaxis=dict(range=[0, 110], gridcolor="rgba(255,255,255,0.08)"))
    return fig


def render_confusion_matrix_heatmap(conf_df: pd.DataFrame) -> go.Figure:
    """Render interactive Confusion Matrix heatmap."""
    fig = go.Figure(
        data=go.Heatmap(
            z=conf_df.values,
            x=conf_df.columns.tolist(),
            y=conf_df.index.tolist(),
            colorscale=[[0, "rgba(15,23,42,0.8)"], [0.2, "rgba(138,43,226,0.3)"], [0.6, "rgba(79,172,254,0.6)"], [1, "#00f2fe"]],
            showscale=False,
            text=conf_df.values,
            texttemplate="%{text}",
            textfont=dict(color="#ffffff", size=13, family="Inter"),
        )
    )
    layout = get_base_plotly_layout("Multi-Class Confusion Matrix")
    fig.update_layout(**layout)
    fig.update_xaxes(title="Predicted Class", tickfont=dict(color="#f8fafc"), gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(title="Ground Truth Class", tickfont=dict(color="#f8fafc"), gridcolor="rgba(255,255,255,0.05)")
    return fig


def render_compliance_gauge(completeness_pct: float) -> go.Figure:
    """Render risk-style radial gauge for metadata completeness (% PII with declared purpose & retention)."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(completeness_pct, 1),
            number=dict(suffix="%", font=dict(family="Inter", size=32, color="#00f2fe")),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor="#64748b", tickwidth=1),
                bar=dict(color="#00f2fe", thickness=0.28),
                bgcolor="rgba(15, 23, 42, 0.6)",
                borderwidth=1,
                bordercolor="rgba(0, 242, 254, 0.2)",
                steps=[
                    {"range": [0, 50], "color": "rgba(244, 63, 94, 0.15)"},
                    {"range": [50, 80], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [80, 100], "color": "rgba(16, 185, 129, 0.15)"},
                ],
                threshold=dict(
                    line=dict(color="#34d399", width=3),
                    thickness=0.8,
                    value=80,
                ),
            ),
        )
    )
    layout = get_base_plotly_layout("Metadata Completeness Index (Purpose & Retention Declared)")
    fig.update_layout(**layout, height=260)
    return fig
