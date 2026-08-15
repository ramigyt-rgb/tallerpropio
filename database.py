from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import date
from typing import Any, Iterable

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


TABLES = {
    "thesis_items",
    "capital_movements",
    "simulation_snapshots",
    "economic_goals",
    "pricing_cases",
    "commercial_trials",
    "risks",
    "agreements",
    "independence_items",
    "valuation_snapshots",
    "decisions",
    "actual_periods",
    "app_settings",
}

SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS thesis_items (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    category TEXT NOT NULL,
    statement TEXT NOT NULL,
    owner_position TEXT,
    partner_position TEXT,
    status TEXT NOT NULL DEFAULT 'Pendiente',
    success_condition TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS capital_movements (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    movement_date DATE NOT NULL,
    contributor TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('Aporte','Recupero')),
    category TEXT NOT NULL,
    concept TEXT NOT NULL,
    amount NUMERIC(18,2) NOT NULL DEFAULT 0,
    recoverable BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS simulation_snapshots (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    name TEXT NOT NULL,
    rent NUMERIC(18,2) NOT NULL DEFAULT 0,
    fixed_costs NUMERIC(18,2) NOT NULL DEFAULT 0,
    avg_ticket NUMERIC(18,2) NOT NULL DEFAULT 0,
    jobs INTEGER NOT NULL DEFAULT 0,
    productive_days INTEGER NOT NULL DEFAULT 22,
    material_pct NUMERIC(8,4) NOT NULL DEFAULT 0,
    taxes_pct NUMERIC(8,4) NOT NULL DEFAULT 0,
    ads NUMERIC(18,2) NOT NULL DEFAULT 0,
    helper_cost NUMERIC(18,2) NOT NULL DEFAULT 0,
    other_costs NUMERIC(18,2) NOT NULL DEFAULT 0,
    owner_share_pct NUMERIC(8,4) NOT NULL DEFAULT 0.40,
    partner_share_pct NUMERIC(8,4) NOT NULL DEFAULT 0.60,
    revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
    net_profit NUMERIC(18,2) NOT NULL DEFAULT 0,
    owner_profit NUMERIC(18,2) NOT NULL DEFAULT 0,
    partner_profit NUMERIC(18,2) NOT NULL DEFAULT 0,
    break_even_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS economic_goals (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    phase TEXT NOT NULL,
    partner_target NUMERIC(18,2) NOT NULL DEFAULT 0,
    owner_target NUMERIC(18,2) NOT NULL DEFAULT 0,
    owner_share_pct NUMERIC(8,4) NOT NULL DEFAULT 0.40,
    expected_net_margin_pct NUMERIC(8,4) NOT NULL DEFAULT 0.35,
    productive_days INTEGER NOT NULL DEFAULT 22,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS pricing_cases (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    case_date DATE NOT NULL,
    vehicle TEXT,
    repair_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'Media',
    source TEXT,
    chapista_reference NUMERIC(18,2) NOT NULL DEFAULT 0,
    competitor_reference NUMERIC(18,2) NOT NULL DEFAULT 0,
    offered_price NUMERIC(18,2) NOT NULL DEFAULT 0,
    final_price NUMERIC(18,2) NOT NULL DEFAULT 0,
    accepted BOOLEAN NOT NULL DEFAULT FALSE,
    labor_hours NUMERIC(10,2) NOT NULL DEFAULT 0,
    material_cost NUMERIC(18,2) NOT NULL DEFAULT 0,
    other_cost NUMERIC(18,2) NOT NULL DEFAULT 0,
    rework_cost NUMERIC(18,2) NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS commercial_trials (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trial_date DATE NOT NULL,
    channel TEXT NOT NULL,
    campaign TEXT,
    spend NUMERIC(18,2) NOT NULL DEFAULT 0,
    inquiries INTEGER NOT NULL DEFAULT 0,
    quotes INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
    material_cost NUMERIC(18,2) NOT NULL DEFAULT 0,
    other_variable_cost NUMERIC(18,2) NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS risks (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    probability INTEGER NOT NULL DEFAULT 3 CHECK (probability BETWEEN 1 AND 5),
    impact INTEGER NOT NULL DEFAULT 3 CHECK (impact BETWEEN 1 AND 5),
    mitigation TEXT,
    trigger_signal TEXT,
    responsible TEXT,
    status TEXT NOT NULL DEFAULT 'Abierto',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS agreements (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    topic TEXT NOT NULL,
    agreed_text TEXT,
    owner_position TEXT,
    partner_position TEXT,
    decision_rule TEXT,
    pending_item TEXT,
    status TEXT NOT NULL DEFAULT 'Pendiente',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS independence_items (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    dimension TEXT NOT NULL,
    current_score NUMERIC(8,2) NOT NULL DEFAULT 0,
    target_score NUMERIC(8,2) NOT NULL DEFAULT 100,
    weight NUMERIC(8,2) NOT NULL DEFAULT 1,
    action_plan TEXT,
    due_date DATE,
    status TEXT NOT NULL DEFAULT 'En curso',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS valuation_snapshots (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    snapshot_date DATE NOT NULL,
    cash NUMERIC(18,2) NOT NULL DEFAULT 0,
    equipment NUMERIC(18,2) NOT NULL DEFAULT 0,
    other_assets NUMERIC(18,2) NOT NULL DEFAULT 0,
    liabilities NUMERIC(18,2) NOT NULL DEFAULT 0,
    avg_monthly_profit NUMERIC(18,2) NOT NULL DEFAULT 0,
    profit_multiple_months NUMERIC(10,2) NOT NULL DEFAULT 12,
    brand_value NUMERIC(18,2) NOT NULL DEFAULT 0,
    customer_value NUMERIC(18,2) NOT NULL DEFAULT 0,
    owner_pct NUMERIC(8,4) NOT NULL DEFAULT 0.40,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS decisions (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decision_date DATE NOT NULL,
    decision TEXT NOT NULL,
    rationale TEXT,
    expected_outcome TEXT,
    success_metric TEXT,
    review_date DATE,
    actual_outcome TEXT,
    result TEXT NOT NULL DEFAULT 'Sin revisar',
    learning TEXT,
    status TEXT NOT NULL DEFAULT 'Abierta',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS actual_periods (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    period_date DATE NOT NULL UNIQUE,
    revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
    materials NUMERIC(18,2) NOT NULL DEFAULT 0,
    payroll NUMERIC(18,2) NOT NULL DEFAULT 0,
    rent NUMERIC(18,2) NOT NULL DEFAULT 0,
    utilities NUMERIC(18,2) NOT NULL DEFAULT 0,
    advertising NUMERIC(18,2) NOT NULL DEFAULT 0,
    taxes NUMERIC(18,2) NOT NULL DEFAULT 0,
    other_costs NUMERIC(18,2) NOT NULL DEFAULT 0,
    jobs INTEGER NOT NULL DEFAULT 0,
    inquiries INTEGER NOT NULL DEFAULT 0,
    quotes INTEGER NOT NULL DEFAULT 0,
    reworks INTEGER NOT NULL DEFAULT 0,
    receivables NUMERIC(18,2) NOT NULL DEFAULT 0,
    owner_share_pct NUMERIC(8,4) NOT NULL DEFAULT 0.40,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value_text TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_capital_date ON capital_movements(movement_date);
CREATE INDEX IF NOT EXISTS idx_pricing_date ON pricing_cases(case_date);
CREATE INDEX IF NOT EXISTS idx_commercial_date ON commercial_trials(trial_date);
CREATE INDEX IF NOT EXISTS idx_decisions_review ON decisions(review_date);
CREATE INDEX IF NOT EXISTS idx_actual_period ON actual_periods(period_date);
"""


def _raw_database_url() -> str:
    value = os.getenv("DATABASE_URL", "").strip()
    if value:
        return value
    try:
        return str(st.secrets["DATABASE_URL"]).strip()
    except Exception:
        return ""


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    url = _raw_database_url()
    if not url:
        raise RuntimeError(
            "Falta DATABASE_URL. Esta app no usa SQLite ni el disco efímero de Streamlit."
        )
    normalized = _normalize_database_url(url)
    return create_engine(
        normalized,
        pool_pre_ping=True,
        pool_recycle=240,
        pool_size=3,
        max_overflow=2,
        future=True,
    )


def init_db() -> None:
    engine = get_engine()
    statements = [s.strip() for s in SCHEMA_SQL.split(";") if s.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
    seed_defaults()


def seed_defaults() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        goal_count = conn.execute(text("SELECT COUNT(*) FROM economic_goals")).scalar_one()
        if goal_count == 0:
            goals = [
                ("Fase 1", 4_000_000, 2_670_000, 0.40, 0.35, 22, "Primer objetivo de distribución mensual."),
                ("Fase 2", 6_000_000, 4_000_000, 0.40, 0.35, 22, "Escala intermedia."),
                ("Fase 3", 8_000_000, 5_330_000, 0.40, 0.35, 22, "Objetivo de madurez inicial."),
            ]
            for row in goals:
                conn.execute(text("""
                    INSERT INTO economic_goals
                    (phase, partner_target, owner_target, owner_share_pct, expected_net_margin_pct, productive_days, notes)
                    VALUES (:phase,:partner,:owner,:share,:margin,:days,:notes)
                """), {
                    "phase": row[0], "partner": row[1], "owner": row[2],
                    "share": row[3], "margin": row[4], "days": row[5], "notes": row[6]
                })

        risk_count = conn.execute(text("SELECT COUNT(*) FROM risks")).scalar_one()
        if risk_count == 0:
            defaults = [
                ("Dependencia del chapista", "Persona clave", 4, 5, "Documentar procesos, formar segundo recurso y crear cartera propia.", "Ausencia, conflicto o caída de productividad."),
                ("Dependencia de herramientas ajenas", "Activos", 4, 4, "Inventario crítico y plan progresivo de compra de herramientas propias.", "Herramienta no disponible o retirada."),
                ("Dependencia de cuenta en pinturería", "Proveedor", 4, 4, "Abrir cuenta comercial propia y segundo proveedor.", "Bloqueo de crédito o cambio de condiciones."),
                ("Cliente impago / financiación", "Caja", 3, 5, "Seña, hitos de cobro, límites de crédito y trazabilidad por trabajo.", "Saldo vencido."),
                ("Retrabajos", "Calidad", 3, 4, "Checklist de entrega, fotos, control final y registro de causa.", "Reingreso sin facturación."),
                ("Baja demanda", "Comercial", 3, 5, "Diversificar canales y medir CAC/cierre semanalmente.", "Pipeline menor al punto de equilibrio."),
                ("Conflicto societario", "Gobernanza", 3, 5, "Acuerdos escritos, caja transparente y reglas de salida.", "Decisiones bloqueadas o desacuerdo por dinero."),
                ("Habilitación / contingencia legal", "Legal", 3, 5, "Validar con contador/abogado/municipio antes de operar formalmente.", "Intimación, inspección o reclamo."),
            ]
            for name, cat, prob, impact, mitigation, trigger in defaults:
                conn.execute(text("""
                    INSERT INTO risks(name,category,probability,impact,mitigation,trigger_signal,responsible,status)
                    VALUES (:n,:c,:p,:i,:m,:t,'Dueño','Abierto')
                """), {"n": name, "c": cat, "p": prob, "i": impact, "m": mitigation, "t": trigger})

        ind_count = conn.execute(text("SELECT COUNT(*) FROM independence_items")).scalar_one()
        if ind_count == 0:
            dimensions = [
                ("Herramientas propias del taller", 0, 100, 1.3),
                ("Segundo chapista disponible", 0, 100, 1.5),
                ("Preparador formado", 0, 100, 1.1),
                ("Proveedores propios", 0, 100, 1.2),
                ("Cuenta propia en pinturería", 0, 100, 1.2),
                ("Clientes generados por la marca", 0, 100, 1.5),
                ("Procesos documentados", 0, 100, 1.3),
                ("Base de precios propia", 0, 100, 1.1),
            ]
            for dim, current, target, weight in dimensions:
                conn.execute(text("""
                    INSERT INTO independence_items(dimension,current_score,target_score,weight,action_plan,status)
                    VALUES (:d,:c,:t,:w,'Definir próximo hito','En curso')
                """), {"d": dim, "c": current, "t": target, "w": weight})


def _assert_table(table: str) -> None:
    if table not in TABLES:
        raise ValueError("Tabla no permitida")


def get_df(table: str, order_by: str = "id DESC") -> pd.DataFrame:
    _assert_table(table)
    allowed_order = {
        "id DESC", "id ASC", "created_at DESC", "movement_date DESC",
        "case_date DESC", "trial_date DESC", "snapshot_date DESC",
        "decision_date DESC", "period_date DESC", "phase ASC"
    }
    if order_by not in allowed_order:
        order_by = "id DESC"
    return pd.read_sql(text(f"SELECT * FROM {table} ORDER BY {order_by}"), get_engine())


def insert_row(table: str, data: dict[str, Any]) -> None:
    _assert_table(table)
    clean = {k: v for k, v in data.items() if k != "id"}
    columns = ", ".join(clean.keys())
    params = ", ".join(f":{k}" for k in clean)
    with get_engine().begin() as conn:
        conn.execute(text(f"INSERT INTO {table} ({columns}) VALUES ({params})"), clean)


def update_row(table: str, row_id: int, data: dict[str, Any]) -> None:
    _assert_table(table)
    clean = {k: v for k, v in data.items() if k not in {"id", "created_at"}}
    setters = ", ".join(f"{k}=:{k}" for k in clean)
    clean["row_id"] = int(row_id)
    with get_engine().begin() as conn:
        conn.execute(text(f"UPDATE {table} SET {setters} WHERE id=:row_id"), clean)


def delete_row(table: str, row_id: int) -> None:
    _assert_table(table)
    with get_engine().begin() as conn:
        conn.execute(text(f"DELETE FROM {table} WHERE id=:row_id"), {"row_id": int(row_id)})


def upsert_actual_period(data: dict[str, Any]) -> None:
    sql = text("""
        INSERT INTO actual_periods
        (period_date,revenue,materials,payroll,rent,utilities,advertising,taxes,other_costs,
         jobs,inquiries,quotes,reworks,receivables,owner_share_pct,notes)
        VALUES
        (:period_date,:revenue,:materials,:payroll,:rent,:utilities,:advertising,:taxes,:other_costs,
         :jobs,:inquiries,:quotes,:reworks,:receivables,:owner_share_pct,:notes)
        ON CONFLICT (period_date) DO UPDATE SET
          revenue=EXCLUDED.revenue,
          materials=EXCLUDED.materials,
          payroll=EXCLUDED.payroll,
          rent=EXCLUDED.rent,
          utilities=EXCLUDED.utilities,
          advertising=EXCLUDED.advertising,
          taxes=EXCLUDED.taxes,
          other_costs=EXCLUDED.other_costs,
          jobs=EXCLUDED.jobs,
          inquiries=EXCLUDED.inquiries,
          quotes=EXCLUDED.quotes,
          reworks=EXCLUDED.reworks,
          receivables=EXCLUDED.receivables,
          owner_share_pct=EXCLUDED.owner_share_pct,
          notes=EXCLUDED.notes
    """)
    with get_engine().begin() as conn:
        conn.execute(sql, data)


def set_setting(key: str, value: str) -> None:
    with get_engine().begin() as conn:
        conn.execute(text("""
            INSERT INTO app_settings(key,value_text,updated_at)
            VALUES (:k,:v,NOW())
            ON CONFLICT(key) DO UPDATE SET value_text=EXCLUDED.value_text, updated_at=NOW()
        """), {"k": key, "v": value})


def get_setting(key: str, default: str = "") -> str:
    with get_engine().connect() as conn:
        value = conn.execute(
            text("SELECT value_text FROM app_settings WHERE key=:k"), {"k": key}
        ).scalar()
    return default if value is None else str(value)


def export_all_tables() -> dict[str, pd.DataFrame]:
    return {table: get_df(table) for table in sorted(TABLES) if table != "app_settings"}
