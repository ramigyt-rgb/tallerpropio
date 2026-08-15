from __future__ import annotations
import os
from typing import Any
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

TABLES = {"thesis_items","capital_movements","simulation_snapshots","economic_goals","pricing_cases","commercial_trials","risks","agreements","independence_items","valuation_snapshots","decisions","actual_periods","app_settings"}

SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS thesis_items (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, category TEXT NOT NULL, statement TEXT NOT NULL, owner_position TEXT, partner_position TEXT, status TEXT NOT NULL DEFAULT 'Pendiente', success_condition TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS capital_movements (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, movement_date DATE NOT NULL, contributor TEXT NOT NULL, direction TEXT NOT NULL, category TEXT NOT NULL, concept TEXT NOT NULL, amount NUMERIC NOT NULL DEFAULT 0, recoverable BOOLEAN NOT NULL DEFAULT 1, notes TEXT);
CREATE TABLE IF NOT EXISTS simulation_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, rent NUMERIC NOT NULL DEFAULT 0, fixed_costs NUMERIC NOT NULL DEFAULT 0, avg_ticket NUMERIC NOT NULL DEFAULT 0, jobs INTEGER NOT NULL DEFAULT 0, productive_days INTEGER NOT NULL DEFAULT 22, material_pct NUMERIC NOT NULL DEFAULT 0, taxes_pct NUMERIC NOT NULL DEFAULT 0, ads NUMERIC NOT NULL DEFAULT 0, helper_cost NUMERIC NOT NULL DEFAULT 0, other_costs NUMERIC NOT NULL DEFAULT 0, owner_share_pct NUMERIC NOT NULL DEFAULT 0.40, partner_share_pct NUMERIC NOT NULL DEFAULT 0.60, revenue NUMERIC NOT NULL DEFAULT 0, net_profit NUMERIC NOT NULL DEFAULT 0, owner_profit NUMERIC NOT NULL DEFAULT 0, partner_profit NUMERIC NOT NULL DEFAULT 0, break_even_revenue NUMERIC NOT NULL DEFAULT 0, notes TEXT);
CREATE TABLE IF NOT EXISTS economic_goals (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, phase TEXT NOT NULL, partner_target NUMERIC NOT NULL DEFAULT 0, owner_target NUMERIC NOT NULL DEFAULT 0, owner_share_pct NUMERIC NOT NULL DEFAULT 0.40, expected_net_margin_pct NUMERIC NOT NULL DEFAULT 0.35, productive_days INTEGER NOT NULL DEFAULT 22, active BOOLEAN NOT NULL DEFAULT 1, notes TEXT);
CREATE TABLE IF NOT EXISTS pricing_cases (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, case_date DATE NOT NULL, vehicle TEXT, repair_type TEXT NOT NULL, severity TEXT NOT NULL DEFAULT 'Media', source TEXT, chapista_reference NUMERIC NOT NULL DEFAULT 0, competitor_reference NUMERIC NOT NULL DEFAULT 0, offered_price NUMERIC NOT NULL DEFAULT 0, final_price NUMERIC NOT NULL DEFAULT 0, accepted BOOLEAN NOT NULL DEFAULT 0, labor_hours NUMERIC NOT NULL DEFAULT 0, material_cost NUMERIC NOT NULL DEFAULT 0, other_cost NUMERIC NOT NULL DEFAULT 0, rework_cost NUMERIC NOT NULL DEFAULT 0, notes TEXT);
CREATE TABLE IF NOT EXISTS commercial_trials (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, trial_date DATE NOT NULL, channel TEXT NOT NULL, campaign TEXT, spend NUMERIC NOT NULL DEFAULT 0, inquiries INTEGER NOT NULL DEFAULT 0, quotes INTEGER NOT NULL DEFAULT 0, wins INTEGER NOT NULL DEFAULT 0, revenue NUMERIC NOT NULL DEFAULT 0, material_cost NUMERIC NOT NULL DEFAULT 0, other_variable_cost NUMERIC NOT NULL DEFAULT 0, notes TEXT);
CREATE TABLE IF NOT EXISTS risks (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, category TEXT NOT NULL, probability INTEGER NOT NULL DEFAULT 3, impact INTEGER NOT NULL DEFAULT 3, mitigation TEXT, trigger_signal TEXT, responsible TEXT, status TEXT NOT NULL DEFAULT 'Abierto', notes TEXT);
CREATE TABLE IF NOT EXISTS agreements (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, topic TEXT NOT NULL, agreed_text TEXT, owner_position TEXT, partner_position TEXT, decision_rule TEXT, pending_item TEXT, status TEXT NOT NULL DEFAULT 'Pendiente', notes TEXT);
CREATE TABLE IF NOT EXISTS independence_items (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, dimension TEXT NOT NULL, current_score NUMERIC NOT NULL DEFAULT 0, target_score NUMERIC NOT NULL DEFAULT 100, weight NUMERIC NOT NULL DEFAULT 1, action_plan TEXT, due_date DATE, status TEXT NOT NULL DEFAULT 'En curso', notes TEXT);
CREATE TABLE IF NOT EXISTS valuation_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, snapshot_date DATE NOT NULL, cash NUMERIC NOT NULL DEFAULT 0, equipment NUMERIC NOT NULL DEFAULT 0, other_assets NUMERIC NOT NULL DEFAULT 0, liabilities NUMERIC NOT NULL DEFAULT 0, avg_monthly_profit NUMERIC NOT NULL DEFAULT 0, profit_multiple_months NUMERIC NOT NULL DEFAULT 12, brand_value NUMERIC NOT NULL DEFAULT 0, customer_value NUMERIC NOT NULL DEFAULT 0, owner_pct NUMERIC NOT NULL DEFAULT 0.40, notes TEXT);
CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, decision_date DATE NOT NULL, decision TEXT NOT NULL, rationale TEXT, expected_outcome TEXT, success_metric TEXT, review_date DATE, actual_outcome TEXT, result TEXT NOT NULL DEFAULT 'Sin revisar', learning TEXT, status TEXT NOT NULL DEFAULT 'Abierta', notes TEXT);
CREATE TABLE IF NOT EXISTS actual_periods (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, period_date DATE NOT NULL UNIQUE, revenue NUMERIC NOT NULL DEFAULT 0, materials NUMERIC NOT NULL DEFAULT 0, payroll NUMERIC NOT NULL DEFAULT 0, rent NUMERIC NOT NULL DEFAULT 0, utilities NUMERIC NOT NULL DEFAULT 0, advertising NUMERIC NOT NULL DEFAULT 0, taxes NUMERIC NOT NULL DEFAULT 0, other_costs NUMERIC NOT NULL DEFAULT 0, jobs INTEGER NOT NULL DEFAULT 0, inquiries INTEGER NOT NULL DEFAULT 0, quotes INTEGER NOT NULL DEFAULT 0, reworks INTEGER NOT NULL DEFAULT 0, receivables NUMERIC NOT NULL DEFAULT 0, owner_share_pct NUMERIC NOT NULL DEFAULT 0.40, notes TEXT);
CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value_text TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
"""

def _raw_database_url() -> str:
    v = os.getenv("DATABASE_URL", "").strip()
    if v: return v
    try: return str(st.secrets["DATABASE_URL"]).strip()
    except Exception: return ""

def _normalize_database_url(url: str) -> str:
    if not url: return url
    if url.startswith("postgres://"): url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"): return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url

def get_storage_mode() -> str:
    return "postgres" if _raw_database_url() else "demo_local"

@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    db = _normalize_database_url(_raw_database_url())
    if db:
        return create_engine(db, pool_pre_ping=True, pool_recycle=240, pool_size=3, max_overflow=2, future=True)
    return create_engine("sqlite:///owner_os_demo.db", future=True)

def init_db():
    with get_engine().begin() as conn:
        for stmt in [s.strip() for s in SCHEMA_SQL.split(";") if s.strip()]:
            conn.execute(text(stmt))
    seed_defaults()
    if get_storage_mode() == "demo_local":
        seed_demo()

def seed_defaults():
    with get_engine().begin() as conn:
        if conn.execute(text("SELECT COUNT(*) FROM economic_goals")).scalar_one() == 0:
            for r in [("Fase 1",4000000,2670000,0.40,0.35,22,"Primer objetivo mensual"),("Fase 2",6000000,4000000,0.40,0.35,22,"Escala intermedia"),("Fase 3",8000000,5330000,0.40,0.35,22,"Madurez inicial")]:
                conn.execute(text("INSERT INTO economic_goals(phase,partner_target,owner_target,owner_share_pct,expected_net_margin_pct,productive_days,notes) VALUES (:a,:b,:c,:d,:e,:f,:g)"), {"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4],"f":r[5],"g":r[6]})
        if conn.execute(text("SELECT COUNT(*) FROM risks")).scalar_one() == 0:
            rows=[("Dependencia del chapista","Persona clave",4,5,"Documentar procesos y formar respaldo.","Ausencia o conflicto."),("Dependencia de herramientas ajenas","Activos",4,4,"Plan progresivo de compra propia.","Herramienta crítica no disponible."),("Dependencia de pinturería","Proveedor",4,4,"Abrir cuenta propia y segundo proveedor.","Bloqueo de crédito."),("Cliente impago","Caja",3,5,"Seña, hitos de cobro y límite de crédito.","Saldo vencido."),("Retrabajos","Calidad",3,4,"Checklist y control final.","Reingreso sin facturación."),("Baja demanda","Comercial",3,5,"Diversificar canales y medir cierre.","Pipeline bajo."),("Conflicto societario","Gobernanza",3,5,"Acuerdos escritos y reglas claras.","Decisiones bloqueadas."),("Habilitación / legal","Legal",3,5,"Validar con contador/abogado.","Inspección o reclamo.")]
            for r in rows:
                conn.execute(text("INSERT INTO risks(name,category,probability,impact,mitigation,trigger_signal,responsible,status) VALUES (:a,:b,:c,:d,:e,:f,'Dueño','Abierto')"), {"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4],"f":r[5]})
        if conn.execute(text("SELECT COUNT(*) FROM independence_items")).scalar_one() == 0:
            rows=[("Herramientas propias del taller",15,100,1.3),("Segundo chapista disponible",5,100,1.5),("Preparador formado",10,100,1.1),("Proveedores propios",20,100,1.2),("Cuenta propia en pinturería",0,100,1.2),("Clientes generados por la marca",12,100,1.5),("Procesos documentados",18,100,1.3),("Base de precios propia",25,100,1.1)]
            for r in rows:
                conn.execute(text("INSERT INTO independence_items(dimension,current_score,target_score,weight,action_plan,status) VALUES (:a,:b,:c,:d,'Definir próximo hito','En curso')"), {"a":r[0],"b":r[1],"c":r[2],"d":r[3]})

def seed_demo():
    with get_engine().begin() as conn:
        if conn.execute(text("SELECT COUNT(*) FROM actual_periods")).scalar_one() == 0:
            rows=[("2026-06-01",9500000,2450000,0,2000000,240000,250000,380000,420000,21,61,39,1,1100000,0.40,"Demo"),("2026-07-01",11800000,3150000,0,2000000,260000,300000,450000,590000,26,75,48,2,1350000,0.40,"Demo"),("2026-08-01",13200000,3500000,300000,2000000,280000,340000,520000,610000,29,83,55,1,1500000,0.40,"Demo")]
            for r in rows:
                conn.execute(text("INSERT INTO actual_periods(period_date,revenue,materials,payroll,rent,utilities,advertising,taxes,other_costs,jobs,inquiries,quotes,reworks,receivables,owner_share_pct,notes) VALUES (:a,:b,:c,:d,:e,:f,:g,:h,:i,:j,:k,:l,:m,:n,:o,:p)"), {"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4],"f":r[5],"g":r[6],"h":r[7],"i":r[8],"j":r[9],"k":r[10],"l":r[11],"m":r[12],"n":r[13],"o":r[14],"p":r[15]})
        if conn.execute(text("SELECT COUNT(*) FROM capital_movements")).scalar_one() == 0:
            rows=[("2026-08-01","Yo","Aporte","Depósito recuperable","Depósito del galpón",2000000,1,"Demo"),("2026-08-01","Yo","Aporte","Ingreso / llave","Entrada inicial",2000000,0,"Demo"),("2026-08-02","Yo","Aporte","Adecuación","Instalación y ordenamiento",1200000,0,"Demo"),("2026-08-03","Yo","Aporte","Capital de trabajo","Caja inicial",800000,1,"Demo"),("2026-08-05","Chapista","Aporte","Herramientas","Herramientas aportadas",3400000,1,"Demo")]
            for r in rows:
                conn.execute(text("INSERT INTO capital_movements(movement_date,contributor,direction,category,concept,amount,recoverable,notes) VALUES (:a,:b,:c,:d,:e,:f,:g,:h)"), {"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4],"f":r[5],"g":r[6],"h":r[7]})
        if conn.execute(text("SELECT COUNT(*) FROM pricing_cases")).scalar_one() == 0:
            rows=[("2026-08-04","Peugeot 208","Paragolpes","Media","Propio",100000,120000,110000,110000,1,6,18000,6000,0,"Demo"),("2026-08-06","Toyota Hilux","Puerta","Alta","Competidor",280000,340000,310000,320000,1,12,62000,14000,0,"Demo"),("2026-08-10","Volkswagen Gol","Guardabarros","Leve","Cliente",90000,110000,98000,0,0,4,12000,4000,0,"No aceptó - Demo")]
            for r in rows:
                conn.execute(text("INSERT INTO pricing_cases(case_date,vehicle,repair_type,severity,source,chapista_reference,competitor_reference,offered_price,final_price,accepted,labor_hours,material_cost,other_cost,rework_cost,notes) VALUES (:a,:b,:c,:d,:e,:f,:g,:h,:i,:j,:k,:l,:m,:n,:o)"), {"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4],"f":r[5],"g":r[6],"h":r[7],"i":r[8],"j":r[9],"k":r[10],"l":r[11],"m":r[12],"n":r[13],"o":r[14]})
        if conn.execute(text("SELECT COUNT(*) FROM commercial_trials")).scalar_one() == 0:
            rows=[("2026-08-03","Tarjetas / QR","Volanteo zona talleres",45000,18,11,4,690000,165000,20000,"Demo"),("2026-08-07","Instagram","Campaña antes/después",85000,29,16,5,1250000,320000,40000,"Demo"),("2026-08-12","Mecánicos","Acuerdo con mecánicos barriales",0,9,7,3,870000,220000,15000,"Demo")]
            for r in rows:
                conn.execute(text("INSERT INTO commercial_trials(trial_date,channel,campaign,spend,inquiries,quotes,wins,revenue,material_cost,other_variable_cost,notes) VALUES (:a,:b,:c,:d,:e,:f,:g,:h,:i,:j,:k)"), {"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4],"f":r[5],"g":r[6],"h":r[7],"i":r[8],"j":r[9],"k":r[10]})
        if conn.execute(text("SELECT COUNT(*) FROM thesis_items")).scalar_one() == 0:
            rows=[("Capital","El negocio puede sostener el alquiler si alcanza el volumen objetivo.","Yo","Chapista","Validando","3 meses arriba del punto de equilibrio.","Demo"),("Comercial","Tarjetas + QR pueden abrir un canal barato para cotizaciones.","Yo","","Validando","30 cotizaciones mensuales.","Demo"),("Sociedad","Un 60/40 puede servir si primero se pagan todos los costos.","Yo","Chapista","Pendiente","Definir reglas de caja y recupero.","Demo")]
            for r in rows:
                conn.execute(text("INSERT INTO thesis_items(category,statement,owner_position,partner_position,status,success_condition,notes) VALUES (:a,:b,:c,:d,:e,:f,:g)"), {"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4],"f":r[5],"g":r[6]})
        if conn.execute(text("SELECT COUNT(*) FROM agreements")).scalar_one() == 0:
            conn.execute(text("INSERT INTO agreements(topic,agreed_text,owner_position,partner_position,decision_rule,pending_item,status,notes) VALUES ('Reparto de utilidad','Distribución solo sobre utilidad neta luego de gastos.','Caja transparente y prioridad al recupero de capital.','Participación atractiva por su trabajo.','Decisiones grandes por acuerdo de ambos.','Formalizar porcentaje y reglas de salida.','En negociación','Demo')"))
        if conn.execute(text("SELECT COUNT(*) FROM decisions")).scalar_one() == 0:
            conn.execute(text("INSERT INTO decisions(decision_date,decision,rationale,expected_outcome,success_metric,review_date,actual_outcome,result,learning,status,notes) VALUES ('2026-08-01','Probar tarjetas con QR para cotizar por WhatsApp.','Bajo costo y capilaridad barrial.','Lograr al menos 30 cotizaciones al mes.','30 cotizaciones mensuales.','2026-11-01','','Sin revisar','','Abierta','Demo')"))
        if conn.execute(text("SELECT COUNT(*) FROM valuation_snapshots")).scalar_one() == 0:
            conn.execute(text("INSERT INTO valuation_snapshots(snapshot_date,cash,equipment,other_assets,liabilities,avg_monthly_profit,profit_multiple_months,brand_value,customer_value,owner_pct,notes) VALUES ('2026-08-15',800000,2200000,300000,500000,2400000,12,400000,600000,0.40,'Demo')"))

def _assert_table(table: str): 
    if table not in TABLES: raise ValueError("Tabla no permitida")

def get_df(table: str, order_by: str = "id DESC") -> pd.DataFrame:
    _assert_table(table)
    return pd.read_sql(text(f"SELECT * FROM {table} ORDER BY {order_by}"), get_engine())

def insert_row(table: str, data: dict[str, Any]) -> None:
    _assert_table(table)
    clean = {k:v for k,v in data.items() if k != "id"}
    cols = ", ".join(clean.keys())
    vals = ", ".join(f":{k}" for k in clean)
    with get_engine().begin() as conn:
        conn.execute(text(f"INSERT INTO {table} ({cols}) VALUES ({vals})"), clean)

def update_row(table: str, row_id: int, data: dict[str, Any]) -> None:
    _assert_table(table)
    clean = {k:v for k,v in data.items() if k not in {"id","created_at"}}
    sets = ", ".join(f"{k}=:{k}" for k in clean)
    clean["row_id"] = int(row_id)
    with get_engine().begin() as conn:
        conn.execute(text(f"UPDATE {table} SET {sets} WHERE id=:row_id"), clean)

def delete_row(table: str, row_id: int) -> None:
    _assert_table(table)
    with get_engine().begin() as conn:
        conn.execute(text(f"DELETE FROM {table} WHERE id=:row_id"), {"row_id": int(row_id)})

def upsert_actual_period(data: dict[str, Any]) -> None:
    with get_engine().begin() as conn:
        exists = conn.execute(text("SELECT COUNT(*) FROM actual_periods WHERE period_date=:p"), {"p": data["period_date"]}).scalar_one()
        if exists:
            conn.execute(text("UPDATE actual_periods SET revenue=:revenue, materials=:materials, payroll=:payroll, rent=:rent, utilities=:utilities, advertising=:advertising, taxes=:taxes, other_costs=:other_costs, jobs=:jobs, inquiries=:inquiries, quotes=:quotes, reworks=:reworks, receivables=:receivables, owner_share_pct=:owner_share_pct, notes=:notes WHERE period_date=:period_date"), data)
        else:
            conn.execute(text("INSERT INTO actual_periods(period_date,revenue,materials,payroll,rent,utilities,advertising,taxes,other_costs,jobs,inquiries,quotes,reworks,receivables,owner_share_pct,notes) VALUES (:period_date,:revenue,:materials,:payroll,:rent,:utilities,:advertising,:taxes,:other_costs,:jobs,:inquiries,:quotes,:reworks,:receivables,:owner_share_pct,:notes)"), data)

def export_all_tables() -> dict[str, pd.DataFrame]:
    return {t: get_df(t) for t in sorted(TABLES) if t != "app_settings"}
