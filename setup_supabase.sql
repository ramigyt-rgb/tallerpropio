-- OWNER OS / TALLER LAB
-- Este archivo es opcional: app.py crea las tablas automáticamente.
-- Podés ejecutarlo en Supabase > SQL Editor para verificar/precrear la estructura.

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
