from __future__ import annotations
import streamlit as st

CSS = r"""
<style>
:root{
  --bg:#F3F4F6; --bg2:#EEF0F3; --card:#FFFFFF; --line:#D8DDE5;
  --text:#1F2937; --muted:#6B7280; --soft:#F8F9FB;
  --g1:#727781; --g2:#A8AFBA;
  --good:#5F8A68; --warn:#9B7D38; --bad:#A65D5D;
}
html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--text); }
.stApp{ background: radial-gradient(circle at 15% -5%, rgba(114,119,129,.14), transparent 32%), linear-gradient(180deg,var(--bg),var(--bg2)); }
.block-container{ max-width:1480px; padding-top:1.4rem; padding-bottom:4rem; }
[data-testid="stSidebar"]{ background:#F0F2F5; border-right:1px solid var(--line); }
h1,h2,h3{ color:var(--text); letter-spacing:-.02em; }
div[data-testid="stMetric"]{ background:linear-gradient(180deg,#FFFFFF,#F8F9FB); border:1px solid var(--line); border-radius:18px; padding:16px 18px; box-shadow:0 10px 30px rgba(17,24,39,.04); }
div[data-testid="stMetric"] label{ color:var(--muted)!important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"]{ font-weight:760; }
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button{ width:100%; min-height:44px; border-radius:12px; font-weight:650; }
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"]{ background:linear-gradient(135deg,var(--g1),var(--g2)); border:0; color:white; }
.stButton > button:not([kind="primary"]){ background:white; border:1px solid var(--line); color:var(--text); }
.owner-hero{ border:1px solid var(--line); border-radius:24px; padding:26px; margin-bottom:18px; background:linear-gradient(135deg,rgba(114,119,129,.18),rgba(255,255,255,.96) 60%,rgba(255,255,255,.88)); box-shadow:0 10px 28px rgba(17,24,39,.05); }
.owner-kicker{ color:#6B7280; font-size:.76rem; font-weight:800; letter-spacing:.18em; text-transform:uppercase; }
.owner-title{ font-size:2.05rem; font-weight:820; letter-spacing:-.04em; margin:.25rem 0 .35rem; color:var(--text); }
.owner-sub{ color:var(--muted); font-size:.98rem; max-width:920px; }
.section-head{ display:flex; justify-content:space-between; align-items:end; margin:1.2rem 0 .65rem; }
.section-title{ font-size:1.15rem; font-weight:760; color:var(--text); }
.section-note{ font-size:.82rem; color:var(--muted); }
.callout{ padding:14px 16px; border-left:3px solid var(--g1); background:rgba(114,119,129,.10); border-radius:12px; margin:.5rem 0 1rem; color:var(--text); }
.callout.good{ border-left-color:var(--good); background:rgba(95,138,104,.08); }
.callout.warn{ border-left-color:var(--warn); background:rgba(155,125,56,.09); }
.callout.bad{ border-left-color:var(--bad); background:rgba(166,93,93,.09); }
.login-shell{text-align:center;max-width:520px;margin:10vh auto 2rem;padding:28px;border:1px solid var(--line);border-radius:24px;background:rgba(255,255,255,.95)}
.eyebrow{color:#6B7280;font-size:.75rem;letter-spacing:.2em;font-weight:800}
.login-title{font-size:2.4rem;font-weight:850;letter-spacing:-.06em;color:var(--text)}
.login-subtitle{color:var(--muted)}
</style>
"""

def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)

def hero(title: str, subtitle: str, kicker: str = "OWNER OS · TALLER LAB"):
    st.markdown(f"""<div class="owner-hero"><div class="owner-kicker">{kicker}</div><div class="owner-title">{title}</div><div class="owner-sub">{subtitle}</div></div>""", unsafe_allow_html=True)

def section(title: str, note: str = ""):
    st.markdown(f"""<div class="section-head"><div class="section-title">{title}</div><div class="section-note">{note}</div></div>""", unsafe_allow_html=True)

def money(value) -> str:
    try: v = float(value or 0)
    except Exception: v = 0
    return f"$ {v:,.0f}".replace(",", ".")

def pct(value, decimals=1) -> str:
    try: v = float(value or 0) * 100
    except Exception: v = 0
    return f"{v:.{decimals}f}%"

def safe_div(a,b,default=0.0):
    try: return float(a)/float(b) if float(b)!=0 else default
    except Exception: return default

def score_label(score: float) -> str:
    if score >= 80: return "Fuerte"
    if score >= 60: return "Aceptable"
    if score >= 40: return "Frágil"
    return "Crítico"

def callout(text: str, level: str = ""):
    st.markdown(f'<div class="callout {level}">{text}</div>', unsafe_allow_html=True)
