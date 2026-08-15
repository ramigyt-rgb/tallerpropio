from __future__ import annotations

import streamlit as st


CSS = r"""
<style>

:root {
    --os-bg: #F2F3F5;
    --os-bg-2: #ECEEF1;
    --os-sidebar: #ECEEF1;
    --os-sidebar-hover: #E1E4E8;
    --os-sidebar-active: #D5D9DE;
    --os-card: #FFFFFF;
    --os-border: #D3D7DD;
    --os-text: #24272C;
    --os-muted: #747981;
    --os-accent: #555B63;
    --os-good: #5F8A68;
    --os-warn: #9B7D38;
    --os-bad: #A65D5D;
}

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp {
    background:
        radial-gradient(circle at 15% -5%, rgba(114,119,129,.12), transparent 32%),
        linear-gradient(180deg, var(--os-bg), var(--os-bg-2)) !important;
    color: var(--os-text) !important;
    color-scheme: light !important;
}

html,
body,
button,
input,
textarea,
select,
label,
p,
span,
div {
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

.main .block-container,
[data-testid="stMainBlockContainer"] {
    max-width: 1480px !important;
    padding-top: 1.35rem !important;
    padding-bottom: 4rem !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"],
div[data-testid="stSidebar"],
[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: var(--os-sidebar) !important;
    border-right-color: var(--os-border) !important;
    color: var(--os-text) !important;
}

section[data-testid="stSidebar"] *,
[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] button,
section[data-testid="stSidebar"] a {
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #2B2E33 !important;
    -webkit-text-fill-color: #2B2E33 !important;
    font-weight: 800 !important;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *,
[data-testid="stSidebar"] small {
    color: var(--os-muted) !important;
    -webkit-text-fill-color: var(--os-muted) !important;
}

section[data-testid="stSidebar"] hr {
    border-color: var(--os-border) !important;
}

/* RADIO MENU */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 2px !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label,
section[data-testid="stSidebar"] label[data-baseweb="radio"] {
    position: relative !important;
    min-height: 42px !important;
    display: flex !important;
    align-items: center !important;
    padding: 7px 10px !important;
    margin: 0 !important;
    border-radius: 11px !important;
    background: transparent !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover,
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: var(--os-sidebar-hover) !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"] p,
section[data-testid="stSidebar"] label[data-baseweb="radio"] span,
section[data-testid="stSidebar"] div[role="radiogroup"] > label p,
section[data-testid="stSidebar"] div[role="radiogroup"] > label span {
    color: #34383E !important;
    -webkit-text-fill-color: #34383E !important;
    font-weight: 520 !important;
}

/* ocultar radio nativo */
section[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child,
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    opacity: 0 !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"] svg,
section[data-testid="stSidebar"] div[role="radiogroup"] svg {
    display: none !important;
}

section[data-testid="stSidebar"] input[type="radio"] {
    accent-color: var(--os-accent) !important;
}

/* seleccionado */
section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked),
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: var(--os-sidebar-active) !important;
    box-shadow: inset 3px 0 0 var(--os-accent) !important;
}

section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p,
section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) span,
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p,
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) span {
    color: #202328 !important;
    -webkit-text-fill-color: #202328 !important;
    font-weight: 760 !important;
}

/* collapse */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] button *,
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] button * {
    color: #555A61 !important;
    -webkit-text-fill-color: #555A61 !important;
}

/* METRICS */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, #FFFFFF, #F8F9FA) !important;
    border: 1px solid var(--os-border) !important;
    border-radius: 18px !important;
    padding: 16px 18px !important;
    box-shadow: 0 9px 26px rgba(24,28,34,.045) !important;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label * {
    color: var(--os-muted) !important;
    -webkit-text-fill-color: var(--os-muted) !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"],
div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
    font-weight: 760 !important;
}

/* INPUTS */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] textarea,
input,
textarea {
    background: #FFFFFF !important;
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
    border-color: var(--os-border) !important;
}

input::placeholder,
textarea::placeholder {
    color: #9A9FA6 !important;
    -webkit-text-fill-color: #9A9FA6 !important;
}

[data-baseweb="select"] *,
[data-baseweb="popover"] *,
[role="listbox"] *,
[role="option"] * {
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
}

[role="listbox"] {
    background: #FFFFFF !important;
}

[role="option"]:hover {
    background: #ECEEF1 !important;
}

/* BUTTONS */
.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    min-height: 44px !important;
    border-radius: 12px !important;
    font-weight: 650 !important;
}

.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #5F646C, #888E96) !important;
    border: none !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

.stButton > button[kind="primary"] *,
[data-testid="stFormSubmitButton"] > button[kind="primary"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

.stButton > button:not([kind="primary"]),
.stDownloadButton > button {
    background: #FFFFFF !important;
    border: 1px solid var(--os-border) !important;
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
}

/* FORM / EXPANDER */
[data-testid="stForm"],
[data-testid="stExpander"],
[data-testid="stDataFrame"] {
    border-radius: 18px !important;
}

[data-testid="stExpander"] {
    background: rgba(255,255,255,.60) !important;
    border: 1px solid var(--os-border) !important;
}

[data-testid="stExpander"] *,
[data-testid="stExpander"] summary * {
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
}

/* ALERTS */
[data-testid="stAlert"] {
    background: #E4E7EA !important;
    border: 1px solid #D1D5DA !important;
    border-radius: 14px !important;
}

[data-testid="stAlert"],
[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span {
    color: #4C5158 !important;
    -webkit-text-fill-color: #4C5158 !important;
}

[data-testid="stAlert"] svg {
    color: #686E75 !important;
    fill: #686E75 !important;
}

/* HERO */
.owner-hero {
    border: 1px solid var(--os-border);
    border-radius: 24px;
    padding: 26px;
    margin-bottom: 18px;
    background: linear-gradient(135deg, rgba(124,130,138,.17), rgba(255,255,255,.97) 60%, rgba(255,255,255,.89));
    box-shadow: 0 10px 28px rgba(17,24,39,.05);
}

.owner-kicker {
    color: #6B7078 !important;
    -webkit-text-fill-color: #6B7078 !important;
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: .18em;
    text-transform: uppercase;
}

.owner-title {
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
    font-size: 2.05rem;
    font-weight: 820;
    letter-spacing: -.04em;
    margin: .25rem 0 .35rem;
}

.owner-sub {
    color: var(--os-muted) !important;
    -webkit-text-fill-color: var(--os-muted) !important;
    font-size: .98rem;
    max-width: 920px;
}

.section-head {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 16px;
    margin: 1.2rem 0 .65rem;
}

.section-title {
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
    font-size: 1.15rem;
    font-weight: 760;
}

.section-note {
    color: var(--os-muted) !important;
    -webkit-text-fill-color: var(--os-muted) !important;
    font-size: .82rem;
}

/* CALLOUT */
.callout {
    padding: 14px 16px;
    border-left: 3px solid var(--os-accent);
    background: rgba(114,119,129,.10);
    border-radius: 12px;
    margin: .5rem 0 1rem;
    color: var(--os-text) !important;
}

.callout,
.callout * {
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
}

.callout.good {
    border-left-color: var(--os-good);
    background: rgba(95,138,104,.08);
}

.callout.warn {
    border-left-color: var(--os-warn);
    background: rgba(155,125,56,.09);
}

.callout.bad {
    border-left-color: var(--os-bad);
    background: rgba(166,93,93,.09);
}

/* LOGIN */
.login-shell {
    text-align: center;
    max-width: 520px;
    margin: 10vh auto 2rem;
    padding: 28px;
    border: 1px solid var(--os-border);
    border-radius: 24px;
    background: rgba(255,255,255,.95);
}

.eyebrow {
    color: #6B7280 !important;
    -webkit-text-fill-color: #6B7280 !important;
    font-size: .75rem;
    letter-spacing: .2em;
    font-weight: 800;
}

.login-title {
    color: var(--os-text) !important;
    -webkit-text-fill-color: var(--os-text) !important;
    font-size: 2.4rem;
    font-weight: 850;
    letter-spacing: -.06em;
}

.login-subtitle {
    color: var(--os-muted) !important;
    -webkit-text-fill-color: var(--os-muted) !important;
}

/* MOBILE */
@media (max-width: 768px) {

    [data-testid="stMainBlockContainer"],
    .main .block-container {
        padding-top: .8rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    section[data-testid="stSidebar"] {
        width: min(86vw, 360px) !important;
        min-width: min(86vw, 360px) !important;
        max-width: min(86vw, 360px) !important;
        background: #ECEEF1 !important;
        box-shadow: 18px 0 42px rgba(31,41,55,.13) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        background: #ECEEF1 !important;
        padding-top: .8rem !important;
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"] {
        min-height: 40px !important;
        padding: 6px 9px !important;
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"] p,
    section[data-testid="stSidebar"] label[data-baseweb="radio"] span {
        font-size: .96rem !important;
        line-height: 1.30rem !important;
    }

    .owner-hero {
        padding: 20px 18px !important;
        border-radius: 20px !important;
    }

    .owner-title {
        font-size: 1.65rem !important;
    }

    .owner-sub {
        font-size: .92rem !important;
    }

    .section-head {
        align-items: flex-start;
        flex-direction: column;
        gap: 3px;
    }
}

</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str, kicker: str = "OWNER OS · TALLER LAB"):
    st.markdown(
        f"""
        <div class="owner-hero">
            <div class="owner-kicker">{kicker}</div>
            <div class="owner-title">{title}</div>
            <div class="owner-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, note: str = ""):
    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-title">{title}</div>
            <div class="section-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def money(value) -> str:
    try:
        v = float(value or 0)
    except Exception:
        v = 0
    return f"$ {v:,.0f}".replace(",", ".")


def pct(value, decimals: int = 1) -> str:
    try:
        v = float(value or 0) * 100
    except Exception:
        v = 0
    return f"{v:.{decimals}f}%"


def safe_div(a, b, default: float = 0.0):
    try:
        return float(a) / float(b) if float(b) != 0 else default
    except Exception:
        return default


def score_label(score: float) -> str:
    if score >= 80:
        return "Fuerte"
    if score >= 60:
        return "Aceptable"
    if score >= 40:
        return "Frágil"
    return "Crítico"


def callout(text: str, level: str = ""):
    st.markdown(
        f'<div class="callout {level}">{text}</div>',
        unsafe_allow_html=True,
    )
