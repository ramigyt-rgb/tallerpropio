from __future__ import annotations

from datetime import date
import math
import streamlit as st


CSS = r"""
<style>
:root{
  --bg:#0B0D10; --card:#12161B; --card2:#171C22; --line:#252C34;
  --text:#F4F5F7; --muted:#9CA7B2; --pink:#D86C95; --pink2:#F19AB8;
  --good:#81C995; --warn:#F2C66D; --bad:#E98686;
}
html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.stApp { background: radial-gradient(circle at 20% -10%, rgba(216,108,149,.10), transparent 34%), var(--bg); }
.block-container { max-width: 1480px; padding-top: 1.7rem; padding-bottom: 4rem; }
[data-testid="stSidebar"] { background: #0E1115; border-right:1px solid var(--line); }
[data-testid="stSidebar"] .block-container { padding-top:1rem; }
h1,h2,h3 { letter-spacing:-.02em; }
h1 { font-weight:760; }
div[data-testid="stMetric"]{
  background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.015));
  border:1px solid var(--line); border-radius:18px; padding:16px 18px;
}
div[data-testid="stMetric"] label { color:var(--muted)!important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-weight:720; }
div[data-testid="stForm"], .stDataFrame, [data-testid="stExpander"]{
  border-radius:18px!important;
}
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  width:100%; min-height:44px; border-radius:12px; font-weight:650;
}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"]{
  background:linear-gradient(135deg,var(--pink),var(--pink2));
  border:0; color:#141217;
}
.owner-hero{
  border:1px solid var(--line); border-radius:24px; padding:26px;
  background:linear-gradient(135deg,rgba(216,108,149,.15),rgba(255,255,255,.025) 55%,rgba(255,255,255,.012));
  margin-bottom:18px;
}
.owner-kicker{color:var(--pink2);font-size:.76rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase}
.owner-title{font-size:2.1rem;font-weight:800;letter-spacing:-.04em;margin:.25rem 0 .35rem}
.owner-sub{color:var(--muted);font-size:.98rem;max-width:900px}
.section-head{display:flex;justify-content:space-between;align-items:end;margin:1.2rem 0 .65rem}
.section-title{font-size:1.15rem;font-weight:750}
.section-note{font-size:.82rem;color:var(--muted)}
.pill{display:inline-block;padding:5px 9px;border:1px solid var(--line);border-radius:99px;color:var(--muted);font-size:.76rem;margin-right:5px}
.callout{padding:14px 16px;border-left:3px solid var(--pink);background:rgba(216,108,149,.08);border-radius:10px;margin:.5rem 0 1rem}
.callout.good{border-left-color:var(--good);background:rgba(129,201,149,.08)}
.callout.warn{border-left-color:var(--warn);background:rgba(242,198,109,.08)}
.callout.bad{border-left-color:var(--bad);background:rgba(233,134,134,.08)}
.login-shell{text-align:center;max-width:520px;margin:10vh auto 2rem;padding:28px;border:1px solid var(--line);border-radius:24px;background:rgba(18,22,27,.88)}
.eyebrow{color:var(--pink2);font-size:.75rem;letter-spacing:.2em;font-weight:800}
.login-title{font-size:2.6rem;font-weight:850;letter-spacing:-.06em}
.login-subtitle{color:var(--muted)}
.small-muted{color:var(--muted);font-size:.82rem}
hr{border-color:var(--line)!important}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str, kicker: str = "OWNER OS · TALLER LAB"):
    st.markdown(
        f"""<div class="owner-hero">
        <div class="owner-kicker">{kicker}</div>
        <div class="owner-title">{title}</div>
        <div class="owner-sub">{subtitle}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def section(title: str, note: str = ""):
    st.markdown(
        f"""<div class="section-head">
        <div class="section-title">{title}</div>
        <div class="section-note">{note}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def money(value) -> str:
    try:
        v = float(value or 0)
    except Exception:
        v = 0
    return f"$ {v:,.0f}".replace(",", ".")


def pct(value, decimals=1) -> str:
    try:
        v = float(value or 0) * 100
    except Exception:
        v = 0
    return f"{v:.{decimals}f}%"


def safe_div(a, b, default=0.0):
    try:
        return float(a) / float(b) if float(b) != 0 else default
    except Exception:
        return default


def score_label(score: float) -> str:
    if score >= 80: return "Fuerte"
    if score >= 60: return "Aceptable"
    if score >= 40: return "Frágil"
    return "Crítico"


def callout(text: str, level: str = ""):
    cls = "callout " + level
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)
