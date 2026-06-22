"""
ui.py — TraffiCast AI design system.
Premium dark "command center" theme: fonts, glassmorphism cards, glowing KPIs,
styled Plotly templates and free OpenStreetMap (Carto) map styling.
Pure presentation layer — no model logic here.
"""
from __future__ import annotations
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# --------------------------------------------------------------------------- #
#  Brand palette
# --------------------------------------------------------------------------- #
INK        = "#0a0e1a"     # app background (deep navy-black)
PANEL      = "#121829"     # cards / panels
PANEL_2    = "#0f1422"     # darker panel
STROKE     = "#26304a"     # borders
TEXT       = "#e7ecf5"
MUTED      = "#8b98b5"
ACCENT     = "#f59e0b"     # amber (traffic signal)
ACCENT_2   = "#22d3ee"     # cyan
ACCENT_3   = "#a78bfa"     # violet

TIER_COLOR = {"CRITICAL": "#ff2d6e", "HIGH": "#ff8a3d", "MODERATE": "#ffd23f", "LOW": "#37c2ff"}

# Free OpenStreetMap-based vector tiles (no API key / token needed)
MAP_STYLE_DARK  = "carto-darkmatter"
MAP_STYLE_LIGHT = "carto-positron"


# --------------------------------------------------------------------------- #
#  Global CSS
# --------------------------------------------------------------------------- #
def inject_css():
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');
:root {{
  --ink:{INK}; --panel:{PANEL}; --panel2:{PANEL_2}; --stroke:{STROKE};
  --text:{TEXT}; --muted:{MUTED}; --accent:{ACCENT}; --accent2:{ACCENT_2}; --accent3:{ACCENT_3};
}}

/* base */
html, body, [class*="css"] {{ font-family:'Inter',system-ui,sans-serif; }}
.stApp {{
  background:
    radial-gradient(1200px 600px at 12% -8%, rgba(245,158,11,.10), transparent 55%),
    radial-gradient(1100px 620px at 95% 0%, rgba(34,211,238,.10), transparent 50%),
    linear-gradient(180deg, #0a0e1a 0%, #080b14 100%);
  background-attachment: fixed;
}}
h1,h2,h3,h4 {{ font-family:'Space Grotesk','Inter',sans-serif!important; letter-spacing:-.02em; }}

/* hide chrome */
#MainMenu, footer, header [data-testid="stToolbar"] {{ visibility:hidden; }}
[data-testid="stHeader"] {{ background:transparent; }}
.block-container {{ padding-top:1.4rem; padding-bottom:3rem; max-width:1400px; }}

/* sidebar */
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg,#0d1322 0%, #0a0e1a 100%);
  border-right:1px solid var(--stroke);
}}
[data-testid="stSidebar"] .stRadio label {{
  padding:8px 12px; border-radius:10px; margin:2px 0; transition:.15s;
  border:1px solid transparent;
}}
[data-testid="stSidebar"] .stRadio label:hover {{ background:rgba(255,255,255,.04); }}

/* brand header in sidebar */
.tc-brand {{
  display:flex; align-items:center; gap:12px; padding:6px 4px 14px;
  border-bottom:1px solid var(--stroke); margin-bottom:12px;
}}
.tc-logo {{
  width:42px;height:42px;border-radius:12px;flex:none;
  background:linear-gradient(135deg,var(--accent),#ff5d8f);
  display:flex;align-items:center;justify-content:center;font-size:22px;
  box-shadow:0 6px 20px rgba(245,158,11,.45);
}}
.tc-brand-name {{ font-family:'Space Grotesk';font-weight:700;font-size:20px;line-height:1; }}
.tc-brand-sub {{ color:var(--muted);font-size:11.5px;margin-top:3px;letter-spacing:.04em;text-transform:uppercase; }}

/* hero */
.tc-hero {{
  background:linear-gradient(135deg, rgba(18,24,41,.9), rgba(15,20,34,.7));
  border:1px solid var(--stroke); border-radius:20px; padding:22px 26px; margin-bottom:18px;
  position:relative; overflow:hidden;
}}
.tc-hero:before {{
  content:""; position:absolute; inset:0;
  background:radial-gradient(600px 200px at 90% -40%, rgba(34,211,238,.18), transparent);
}}
.tc-hero h1 {{ margin:0; font-size:30px;
  background:linear-gradient(90deg,#fff,#cbd5e1 60%,var(--accent2));
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
.tc-hero p {{ margin:6px 0 0; color:var(--muted); font-size:14px; max-width:760px; }}
.tc-pill {{
  display:inline-flex;align-items:center;gap:7px;font-size:11.5px;font-weight:600;
  padding:5px 12px;border-radius:999px;border:1px solid var(--stroke);
  background:rgba(55,194,255,.08);color:var(--accent2);margin-bottom:10px;
}}
.tc-pulse {{ width:8px;height:8px;border-radius:50%;background:#22e07a;box-shadow:0 0 0 0 rgba(34,224,122,.7);
  animation:pulse 2s infinite; }}
@keyframes pulse {{ 0%{{box-shadow:0 0 0 0 rgba(34,224,122,.6)}} 70%{{box-shadow:0 0 0 9px rgba(34,224,122,0)}} 100%{{box-shadow:0 0 0 0 rgba(34,224,122,0)}} }}

/* KPI cards */
.kpi-row {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:14px; margin:4px 0 6px; }}
.kpi {{
  background:linear-gradient(160deg, var(--panel), var(--panel2));
  border:1px solid var(--stroke); border-radius:16px; padding:16px 18px;
  position:relative; overflow:hidden; transition:.18s; min-height:104px;
}}
.kpi:hover {{ transform:translateY(-3px); border-color:#3a466a; box-shadow:0 10px 30px rgba(0,0,0,.35); }}
.kpi .cap {{ font-size:12px;color:var(--muted);font-weight:600;letter-spacing:.02em; display:flex;align-items:center;gap:7px;}}
.kpi .val {{ font-family:'Space Grotesk';font-weight:700;font-size:30px;line-height:1.1;margin-top:8px; }}
.kpi .sub {{ font-size:11.5px;color:var(--muted);margin-top:5px; }}
.kpi .bar {{ position:absolute;left:0;top:0;bottom:0;width:4px;border-radius:4px 0 0 4px; }}

/* generic card */
.tc-card {{ background:linear-gradient(160deg,var(--panel),var(--panel2));
  border:1px solid var(--stroke);border-radius:16px;padding:16px 18px;margin-bottom:14px; }}
.tc-sec {{ display:flex;align-items:center;gap:10px;margin:18px 0 10px;font-family:'Space Grotesk';
  font-weight:700;font-size:18px; }}
.tc-sec:before {{ content:"";width:4px;height:18px;border-radius:3px;
  background:linear-gradient(180deg,var(--accent),#ff5d8f); }}

/* event list rows */
.evrow {{ display:flex;gap:11px;align-items:flex-start;padding:11px 12px;border-radius:12px;
  border:1px solid var(--stroke);background:rgba(255,255,255,.015);margin-bottom:9px;transition:.15s; }}
.evrow:hover {{ background:rgba(255,255,255,.045); border-color:#3a466a; }}
.evrow .ttl {{ font-weight:600;font-size:13.5px; }}
.evrow .meta {{ font-size:11.5px;color:var(--muted);margin-top:3px; }}
.badge {{ font-size:10.5px;font-weight:700;letter-spacing:.04em;padding:3px 9px;border-radius:999px;
  color:#0a0e1a;white-space:nowrap; }}

/* buttons */
.stButton>button, .stForm [data-testid="stFormSubmitButton"]>button {{
  background:linear-gradient(135deg,var(--accent),#ff7a3d)!important;
  color:#0a0e1a!important;border:none!important;font-weight:700!important;border-radius:12px!important;
  padding:.55rem 1rem!important;box-shadow:0 6px 18px rgba(245,158,11,.35)!important;transition:.15s!important;
}}
.stButton>button:hover, .stForm [data-testid="stFormSubmitButton"]>button:hover {{
  transform:translateY(-2px)!important;filter:brightness(1.06)!important;
}}

/* inputs */
[data-testid="stSidebar"] [data-testid="stMetric"] {{
  background:rgba(255,255,255,.03);border:1px solid var(--stroke);border-radius:12px;padding:10px 12px;
}}
[data-testid="stMetricValue"] {{ font-family:'Space Grotesk'; }}
.stTabs [data-baseweb="tab-list"] {{ gap:6px; }}
.stTabs [data-baseweb="tab"] {{ background:rgba(255,255,255,.03);border:1px solid var(--stroke);
  border-radius:10px 10px 0 0;padding:8px 16px; }}
.stTabs [aria-selected="true"] {{ background:rgba(245,158,11,.14);border-color:var(--accent); }}
.stDataFrame {{ border-radius:12px;overflow:hidden;border:1px solid var(--stroke); }}

/* chips */
.chip {{ display:inline-block;font-size:12px;padding:6px 12px;margin:3px 5px 3px 0;border-radius:999px;
  border:1px solid var(--stroke);background:rgba(255,255,255,.03);color:var(--muted); }}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  HTML component builders
# --------------------------------------------------------------------------- #
def hero(title: str, subtitle: str, pill: str = "LIVE OPERATING PICTURE"):
    st.markdown(f"""
<div class="tc-hero">
  <span class="tc-pill"><span class="tc-pulse"></span>{pill}</span>
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>""", unsafe_allow_html=True)


def kpi_row(cards: list[dict]):
    """cards: [{label, value, sub, color, icon}]"""
    html = '<div class="kpi-row">'
    for c in cards:
        col = c.get("color", ACCENT)
        html += f"""<div class="kpi"><div class="bar" style="background:{col}"></div>
          <div class="cap">{c.get('icon','')} {c['label']}</div>
          <div class="val" style="color:{col}">{c['value']}</div>
          <div class="sub">{c.get('sub','')}</div></div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def section(title: str):
    st.markdown(f'<div class="tc-sec">{title}</div>', unsafe_allow_html=True)


def tier_badge(tier: str) -> str:
    return f'<span class="badge" style="background:{TIER_COLOR.get(tier,"#888")}">{tier}</span>'


def event_row(tier, cause, corridor, impact, closure, longblock):
    col = TIER_COLOR.get(tier, "#888")
    return f"""<div class="evrow">
      <span class="badge" style="background:{col}">{tier}</span>
      <div><div class="ttl">{cause}</div>
      <div class="meta">📍 {corridor} &nbsp;·&nbsp; impact <b style="color:{col}">{impact}</b>
      &nbsp;·&nbsp; closure {closure:.0%} &nbsp;·&nbsp; &gt;3h {longblock:.0%}</div></div></div>"""


# --------------------------------------------------------------------------- #
#  Plotly styling
# --------------------------------------------------------------------------- #
def style_fig(fig: go.Figure, height=None, legend_top=True):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT, size=12.5),
        margin=dict(l=8, r=8, t=10, b=8),
        colorway=[ACCENT, ACCENT_2, ACCENT_3, "#22e07a", "#ff5d8f", "#ffd23f"],
    )
    if height:
        fig.update_layout(height=height)
    if legend_top:
        fig.update_layout(legend=dict(orientation="h", y=1.04, x=0,
                                      bgcolor="rgba(0,0,0,0)", font=dict(size=11.5)))
    return fig


def style_map(fig: go.Figure, center=None, zoom=10.4, height=560, dark=True):
    fig.update_layout(
        mapbox_style=MAP_STYLE_DARK if dark else MAP_STYLE_LIGHT,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT),
        margin=dict(l=0, r=0, t=0, b=0), height=height,
        legend=dict(orientation="h", y=1.02, x=0, bgcolor="rgba(10,14,26,.6)",
                    bordercolor=STROKE, borderwidth=1, font=dict(size=11.5)),
    )
    mbox = dict(zoom=zoom)
    if center:
        mbox["center"] = dict(lat=center[0], lon=center[1])
    fig.update_layout(mapbox=mbox)
    return fig


# --------------------------------------------------------------------------- #
#  Sidebar footer — credit + GitHub link
# --------------------------------------------------------------------------- #
_GH_SVG = ('<svg height="17" width="17" viewBox="0 0 16 16" fill="currentColor" '
           'style="vertical-align:middle">'
           '<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 '
           '0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53'
           '.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 '
           '0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36'
           '.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 '
           '3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 '
           '8c0-4.42-3.58-8-8-8z"/></svg>')


def sidebar_footer(github_url: str, name: str = "Anmol Saharawat"):
    st.sidebar.markdown(f"""<style>
.tc-credit {{ margin-top:18px; padding-top:12px; border-top:1px solid var(--stroke); }}
.tc-credit a {{ display:inline-flex; align-items:center; gap:9px; text-decoration:none;
  color:var(--muted); font-size:13px; font-weight:600; padding:8px 12px; border-radius:11px;
  border:1px solid var(--stroke); background:rgba(255,255,255,.025); transition:.18s; cursor:pointer; }}
.tc-credit a:hover {{ color:#fff; border-color:var(--accent);
  background:linear-gradient(135deg, rgba(245,158,11,.16), rgba(255,93,143,.10));
  box-shadow:0 6px 18px rgba(245,158,11,.22); transform:translateY(-1px); }}
.tc-credit .gh {{ color:#e7ecf5; display:flex; }}
.tc-credit .lbl {{ line-height:1.1; }}
.tc-credit .lbl small {{ display:block; color:var(--muted); font-weight:500; font-size:10.5px;
  text-transform:uppercase; letter-spacing:.05em; }}
</style>
<div class="tc-credit">
  <a href="{github_url}" target="_blank" rel="noopener"
     title="Created by {name} · click to open GitHub profile">
     <span class="gh">{_GH_SVG}</span>
     <span class="lbl">Created by {name}<small>github · click to open</small></span>
  </a>
</div>""", unsafe_allow_html=True)


def credit_badge(github_url: str, name: str = "Anmol Saharawat"):
    """Floating 'Created by' popup badge (fixed bottom-right) — a persistent, clickable credit
    with the GitHub icon. Visible on every page, links straight to the GitHub profile."""
    st.markdown(f"""<style>
.tc-fab {{
  position:fixed; right:18px; bottom:18px; z-index:9999;
  display:inline-flex; align-items:center; gap:10px; text-decoration:none;
  padding:10px 15px; border-radius:14px; font-family:'Space Grotesk','Inter',sans-serif;
  font-weight:700; font-size:13.5px; color:#0a0e1a;
  background:linear-gradient(135deg, {ACCENT}, #ff5d8f);
  box-shadow:0 10px 30px rgba(245,158,11,.45); border:1px solid rgba(255,255,255,.25);
  transition:.18s; cursor:pointer; animation:tcPop .5s ease-out;
}}
.tc-fab:hover {{ transform:translateY(-3px) scale(1.03); filter:brightness(1.06);
  box-shadow:0 14px 38px rgba(245,158,11,.6); }}
.tc-fab .gh {{ display:flex; color:#0a0e1a; }}
.tc-fab .nm small {{ display:block; font-weight:600; font-size:10px; opacity:.8;
  text-transform:uppercase; letter-spacing:.06em; line-height:1.1; }}
@keyframes tcPop {{ 0%{{opacity:0; transform:translateY(14px) scale(.9)}}
  100%{{opacity:1; transform:translateY(0) scale(1)}} }}
@media (max-width:640px) {{ .tc-fab {{ right:10px; bottom:10px; padding:8px 12px; font-size:12px; }} }}
</style>
<a class="tc-fab" href="{github_url}" target="_blank" rel="noopener"
   title="Created by {name} · open GitHub profile">
   <span class="gh">{_GH_SVG}</span>
   <span class="nm">Created by {name}<small>github · TraffiCast AI</small></span>
</a>""", unsafe_allow_html=True)
