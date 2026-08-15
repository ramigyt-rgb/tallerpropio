from __future__ import annotations

import io
import math
import zipfile
from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from auth import require_login, logout_button
from database import (
    init_db, get_df, insert_row, update_row, delete_row, upsert_actual_period,
    export_all_tables, get_engine
)
from metrics import (
    capital_metrics, simulate, goal_math, pricing_enriched, commercial_enriched,
    actual_enriched, independence_score, valuation, risk_priority, owner_alerts
)
from ui import apply_theme, hero, section, money, pct, safe_div, score_label, callout


st.set_page_config(
    page_title="Owner OS · Taller Lab",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

try:
    init_db()
except Exception as exc:
    st.error("No se pudo conectar con la base PostgreSQL externa.")
    st.code(str(exc))
    st.info(
        "Configurá DATABASE_URL en .streamlit/secrets.toml (local) o en Secrets de Streamlit Cloud. "
        "Esta app no guarda la base en el disco de Streamlit."
    )
    st.stop()

require_login()


NAV = {
    "Sala de Mando": "dashboard",
    "Resultados reales": "actuals",
    "1 · Tesis del negocio": "thesis",
    "2 · Capital e inversión": "capital",
    "3 · Simulador": "simulator",
    "4 · Objetivos económicos": "goals",
    "5 · Inteligencia de precios": "pricing",
    "6 · Laboratorio comercial": "commercial",
    "7 · Mapa de riesgos": "risks",
    "8 · Sociedad y negociación": "agreements",
    "9 · Plan de independencia": "independence",
    "10 · Valuación": "valuation",
    "Diario de decisiones": "decisions",
    "Respaldo / Sistema": "system",
}

with st.sidebar:
    st.markdown("### ◈ OWNER OS")
    st.caption("Taller Lab · Private Business Intelligence")
    page_label = st.radio("Navegación", list(NAV.keys()), label_visibility="collapsed")
    st.divider()
    st.caption(f"Sesión: {st.session_state.get('display_name','Owner')}")
    logout_button()

page = NAV[page_label]


def df_show(df, columns=None, height=360):
    if df is None or df.empty:
        st.info("Todavía no hay registros.")
        return
    view = df.copy()
    if columns:
        view = view[[c for c in columns if c in view.columns]]
    st.dataframe(view, use_container_width=True, hide_index=True, height=height)


def record_manager(table, df, field_map=None):
    if df.empty:
        return
    with st.expander("Editar / eliminar un registro"):
        options = df["id"].astype(int).tolist()
        rid = st.selectbox("ID", options, key=f"manage_{table}")
        row = df[df["id"] == rid].iloc[0].to_dict()
        st.caption("Edición rápida de texto/estado. Para cambios numéricos complejos, eliminá y volvé a cargar.")
        field_map = field_map or {}
        updates = {}
        cols = st.columns(2)
        idx = 0
        for field, label in field_map.items():
            val = row.get(field, "")
            if isinstance(val, (bool, np.bool_)):
                updates[field] = cols[idx % 2].checkbox(label, value=bool(val), key=f"{table}_{rid}_{field}")
            elif isinstance(val, (int, float, np.number)) and not pd.isna(val):
                updates[field] = cols[idx % 2].number_input(label, value=float(val), key=f"{table}_{rid}_{field}")
            else:
                updates[field] = cols[idx % 2].text_input(label, value="" if pd.isna(val) else str(val), key=f"{table}_{rid}_{field}")
            idx += 1
        c1, c2 = st.columns(2)
        if c1.button("Guardar cambios", key=f"save_{table}_{rid}", type="primary"):
            update_row(table, rid, updates)
            st.success("Actualizado.")
            st.rerun()
        if c2.button("Eliminar registro", key=f"del_{table}_{rid}"):
            delete_row(table, rid)
            st.success("Eliminado.")
            st.rerun()


def page_dashboard():
    hero(
        "Sala de Mando del Dueño",
        "Una sola pantalla para saber cuánto capital sigue expuesto, si el taller genera utilidad real, "
        "qué tan dependiente es de una sola persona y dónde se está fugando margen."
    )
    cap_df = get_df("capital_movements", "movement_date DESC")
    act = actual_enriched(get_df("actual_periods", "period_date DESC"))
    risk = risk_priority(get_df("risks"))
    ind = get_df("independence_items")
    price = pricing_enriched(get_df("pricing_cases", "case_date DESC"))
    comm = commercial_enriched(get_df("commercial_trials", "trial_date DESC"))
    goals = get_df("economic_goals", "phase ASC")
    decisions = get_df("decisions", "decision_date DESC")

    cap = capital_metrics(cap_df)
    ind_score = independence_score(ind)

    if not act.empty:
        latest = act.sort_values("period_date").iloc[-1]
        rev = float(latest["revenue"])
        net = float(latest["net_profit"])
        owner_profit = float(latest["owner_profit"])
        margin = float(latest["net_margin_pct"])
    else:
        rev = net = owner_profit = margin = 0

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Capital mío expuesto", money(cap["exposed"]))
    c2.metric("Facturación último mes", money(rev))
    c3.metric("Utilidad neta último mes", money(net), delta=pct(margin))
    c4.metric("Mi resultado estimado", money(owner_profit))
    c5.metric("Independencia estructural", f"{ind_score:.0f}/100", score_label(ind_score))

    alerts = owner_alerts(cap, act, risk, ind_score, price, comm)
    section("Radar ejecutivo", "Alertas calculadas únicamente con tus datos")
    for level, text in alerts[:6]:
        callout(text, level)

    if not act.empty:
        section("Evolución real", "Facturación y utilidad por período")
        chart = act.sort_values("period_date").copy()
        chart["period_date"] = pd.to_datetime(chart["period_date"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=chart["period_date"], y=chart["revenue"], name="Facturación"))
        fig.add_trace(go.Scatter(x=chart["period_date"], y=chart["net_profit"], name="Utilidad neta", mode="lines+markers"))
        fig.update_layout(height=350, margin=dict(l=10,r=10,t=20,b=10), legend_orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    a,b = st.columns(2)
    with a:
        section("Riesgos prioritarios")
        if risk.empty:
            st.info("Sin riesgos.")
        else:
            df_show(risk[["name","category","probability","impact","risk_score","status"]].head(8), height=300)
    with b:
        section("Objetivos")
        if goals.empty:
            st.info("Sin objetivos.")
        else:
            rows=[]
            for _,r in goals.iterrows():
                g=goal_math(r["owner_target"],r["partner_target"],r["owner_share_pct"],r["expected_net_margin_pct"],r["productive_days"])
                rows.append({
                    "Fase":r["phase"],"Él":r["partner_target"],"Vos":r["owner_target"],
                    "Utilidad necesaria":g["net_needed"],"Facturación objetivo":g["revenue_needed"],
                    "Objetivo diario":g["daily_revenue"]
                })
            df_show(pd.DataFrame(rows), height=300)

    c,d = st.columns(2)
    with c:
        section("Decisiones a revisar")
        if decisions.empty:
            st.info("Sin decisiones.")
        else:
            dd=decisions.copy()
            dd["review_date"]=pd.to_datetime(dd["review_date"],errors="coerce")
            pending=dd[(dd["status"].astype(str)!="Cerrada") & dd["review_date"].notna()].sort_values("review_date")
            df_show(pending[["decision_date","decision","review_date","result"]].head(8), height=280)
    with d:
        section("Embudo comercial consolidado")
        if comm.empty:
            st.info("Sin pruebas comerciales.")
        else:
            st.metric("Consultas", int(comm["inquiries"].sum()))
            x1,x2,x3=st.columns(3)
            x1.metric("Presupuestos", int(comm["quotes"].sum()))
            x2.metric("Cierres", int(comm["wins"].sum()))
            x3.metric("Conversión", pct(safe_div(comm["wins"].sum(),comm["quotes"].sum())))


def page_actuals():
    hero("Resultados reales", "El tablero no sirve si no existe una verdad mensual. Cargá acá el cierre real del taller.")
    existing = actual_enriched(get_df("actual_periods","period_date DESC"))
    with st.form("actual_form"):
        c1,c2,c3,c4 = st.columns(4)
        period = c1.date_input("Mes", value=date.today().replace(day=1))
        revenue = c2.number_input("Facturación", min_value=0.0, step=100000.0)
        materials = c3.number_input("Materiales", min_value=0.0, step=100000.0)
        payroll = c4.number_input("Sueldos / ayudantes", min_value=0.0, step=100000.0)
        c1,c2,c3,c4 = st.columns(4)
        rent = c1.number_input("Alquiler", min_value=0.0, step=100000.0)
        utilities = c2.number_input("Luz / servicios", min_value=0.0, step=50000.0)
        advertising = c3.number_input("Publicidad", min_value=0.0, step=50000.0)
        taxes = c4.number_input("Impuestos", min_value=0.0, step=50000.0)
        c1,c2,c3,c4 = st.columns(4)
        other = c1.number_input("Otros costos", min_value=0.0, step=50000.0)
        jobs = c2.number_input("Trabajos entregados", min_value=0, step=1)
        inquiries = c3.number_input("Consultas", min_value=0, step=1)
        quotes = c4.number_input("Presupuestos", min_value=0, step=1)
        c1,c2,c3 = st.columns(3)
        reworks = c1.number_input("Retrabajos", min_value=0, step=1)
        receivables = c2.number_input("Cuentas a cobrar", min_value=0.0, step=100000.0)
        owner_share = c3.slider("Tu % de utilidad",0,100,40)/100
        notes=st.text_area("Notas del cierre")
        if st.form_submit_button("Guardar / actualizar mes", type="primary"):
            upsert_actual_period({
                "period_date":period.replace(day=1),"revenue":revenue,"materials":materials,"payroll":payroll,
                "rent":rent,"utilities":utilities,"advertising":advertising,"taxes":taxes,"other_costs":other,
                "jobs":jobs,"inquiries":inquiries,"quotes":quotes,"reworks":reworks,"receivables":receivables,
                "owner_share_pct":owner_share,"notes":notes
            })
            st.success("Cierre guardado en PostgreSQL.")
            st.rerun()

    if not existing.empty:
        view=existing.copy()
        view["Mes"]=pd.to_datetime(view["period_date"]).dt.strftime("%Y-%m")
        view["Margen neto"]=view["net_margin_pct"]
        section("Historial real")
        df_show(view[["Mes","revenue","total_costs","net_profit","owner_profit","partner_profit","jobs","ticket_avg","Margen neto","receivables"]])
        record_manager("actual_periods", existing, {"notes":"Notas"})


def page_thesis():
    hero("1 · Tesis del negocio","Registrá las hipótesis fundacionales. Después vas a poder demostrar qué fue cierto y qué no.")
    with st.form("thesis_add"):
        c1,c2=st.columns(2)
        category=c1.selectbox("Categoría",["Capital","Sociedad","Comercial","Operación","Precios","Personas","Escala","Otro"])
        status=c2.selectbox("Estado",["Pendiente","Validando","Validada","Refutada","Reformular"])
        statement=st.text_area("Hipótesis / tesis",placeholder="Ej.: podemos generar suficiente volumen manteniendo calidad y precio competitivo.")
        owner_pos=st.text_area("Tu posición")
        partner_pos=st.text_area("Posición del chapista")
        success=st.text_area("Condición para seguir invirtiendo",placeholder="Ej.: llegar a X trabajos y Y margen durante 3 meses.")
        notes=st.text_area("Notas")
        if st.form_submit_button("Agregar tesis",type="primary"):
            insert_row("thesis_items",{"category":category,"statement":statement,"owner_position":owner_pos,"partner_position":partner_pos,"status":status,"success_condition":success,"notes":notes})
            st.success("Tesis registrada."); st.rerun()
    df=get_df("thesis_items")
    section("Registro de tesis")
    df_show(df,[ "id","category","statement","status","success_condition","owner_position","partner_position","notes"])
    record_manager("thesis_items",df,{"status":"Estado","statement":"Tesis","success_condition":"Condición de éxito","notes":"Notas"})


def page_capital():
    hero("2 · Capital e inversión","Separá depósito recuperable, costo hundido, adecuaciones, herramientas y recuperos. El número central es cuánto capital tuyo sigue expuesto.")
    df=get_df("capital_movements","movement_date DESC")
    m=capital_metrics(df)
    a,b,c,d=st.columns(4)
    a.metric("Aportes tuyos",money(m["contributed"]))
    b.metric("Recuperado",money(m["recovered"]))
    c.metric("Capital expuesto",money(m["exposed"]))
    d.metric("Recuperable pendiente",money(m["recoverable_exposed"]))
    callout(f"Costo hundido registrado: <b>{money(m['sunk'])}</b>. Aporte neto del chapista registrado: <b>{money(m['partner_net'])}</b>.", "warn" if m["sunk"] else "")
    with st.form("capital_add"):
        c1,c2,c3,c4=st.columns(4)
        dt=c1.date_input("Fecha",value=date.today())
        who=c2.selectbox("Quién",["Yo","Chapista","Negocio"])
        direction=c3.selectbox("Movimiento",["Aporte","Recupero"])
        category=c4.selectbox("Categoría",["Depósito recuperable","Ingreso / llave","Adecuación","Herramientas","Capital de trabajo","Publicidad inicial","Honorarios","Otro"])
        concept=st.text_input("Concepto")
        c1,c2=st.columns(2)
        amount=c1.number_input("Monto",min_value=0.0,step=100000.0)
        recoverable=c2.checkbox("¿Es recuperable?",value=True)
        notes=st.text_area("Notas")
        if st.form_submit_button("Registrar movimiento",type="primary"):
            insert_row("capital_movements",{"movement_date":dt,"contributor":who,"direction":direction,"category":category,"concept":concept,"amount":amount,"recoverable":recoverable,"notes":notes})
            st.success("Movimiento guardado."); st.rerun()
    section("Libro de capital")
    df_show(df)
    record_manager("capital_movements",df,{"notes":"Notas","concept":"Concepto","recoverable":"Recuperable"})


def page_simulator():
    hero("3 · Simulador del negocio","Tocá cualquier variable y mirá en segundos facturación, utilidad, reparto, punto de equilibrio y objetivo diario.")
    c1,c2,c3=st.columns(3)
    with c1:
        rent=st.number_input("Alquiler",min_value=0.0,value=2_000_000.0,step=100000.0)
        fixed=st.number_input("Otros fijos",min_value=0.0,value=500_000.0,step=100000.0)
        ads=st.number_input("Publicidad",min_value=0.0,value=300_000.0,step=50000.0)
        helper=st.number_input("Ayudante / nómina",min_value=0.0,value=0.0,step=100000.0)
    with c2:
        ticket=st.number_input("Ticket promedio",min_value=0.0,value=500_000.0,step=50000.0)
        jobs=st.number_input("Trabajos por mes",min_value=0,value=30,step=1)
        days=st.number_input("Días productivos",min_value=1,value=22,step=1)
        other=st.number_input("Otros costos",min_value=0.0,value=200_000.0,step=50000.0)
    with c3:
        material_pct=st.slider("Materiales % facturación",0,80,25)/100
        taxes_pct=st.slider("Impuestos / comisiones %",0,40,8)/100
        owner_share=st.slider("Tu participación en utilidad",0,100,40)/100
        st.caption(f"Chapista: {(1-owner_share):.0%}")

    r=simulate(rent,fixed,ticket,jobs,days,material_pct,taxes_pct,ads,helper,other,owner_share)
    section("Resultado instantáneo")
    a,b,c,d,e=st.columns(5)
    a.metric("Facturación",money(r["revenue"]))
    b.metric("Utilidad neta",money(r["net_profit"]),delta=pct(r["net_margin"]))
    c.metric("Vos",money(r["owner_profit"]))
    d.metric("Chapista",money(r["partner_profit"]))
    e.metric("Punto de equilibrio",money(r["break_even_revenue"]))
    a,b,c,d=st.columns(4)
    a.metric("Trabajos p/ equilibrio",r["break_even_jobs"])
    b.metric("Facturación diaria",money(r["daily_revenue"]))
    c.metric("Utilidad diaria",money(r["daily_net"]))
    d.metric("Costos variables",money(r["variable_costs"]))

    if r["net_profit"] < 0:
        callout("Con estas variables el negocio pierde dinero. El problema no se resuelve con el reparto: primero debe existir utilidad.", "bad")
    elif r["net_margin"] < .20:
        callout("El negocio da positivo, pero el margen neto es frágil ante retrabajos, descuentos o demoras.", "warn")
    else:
        callout("El escenario supera el punto de equilibrio y deja margen positivo. Falta contrastarlo con resultados reales.", "good")

    st.divider()
    name=st.text_input("Nombre del escenario",value=f"Escenario {datetime.now():%d-%m %H:%M}")
    notes=st.text_input("Notas del escenario")
    if st.button("Guardar escenario",type="primary"):
        insert_row("simulation_snapshots",{
            "name":name,"rent":rent,"fixed_costs":fixed,"avg_ticket":ticket,"jobs":jobs,"productive_days":days,
            "material_pct":material_pct,"taxes_pct":taxes_pct,"ads":ads,"helper_cost":helper,"other_costs":other,
            "owner_share_pct":owner_share,"partner_share_pct":1-owner_share,"revenue":r["revenue"],
            "net_profit":r["net_profit"],"owner_profit":r["owner_profit"],"partner_profit":r["partner_profit"],
            "break_even_revenue":r["break_even_revenue"],"notes":notes
        })
        st.success("Escenario guardado."); st.rerun()
    snaps=get_df("simulation_snapshots")
    section("Escenarios guardados")
    df_show(snaps)
    record_manager("simulation_snapshots",snaps,{"name":"Nombre","notes":"Notas"})


def page_goals():
    hero("4 · Objetivos económicos","Convierte cuánto quieren llevarse ustedes en utilidad necesaria, facturación requerida y objetivo diario.")
    df=get_df("economic_goals","phase ASC")
    rows=[]
    for _,r in df.iterrows():
        g=goal_math(r["owner_target"],r["partner_target"],r["owner_share_pct"],r["expected_net_margin_pct"],r["productive_days"])
        rows.append({
            "ID":r["id"],"Fase":r["phase"],"Objetivo él":r["partner_target"],"Objetivo vos":r["owner_target"],
            "Tu %":r["owner_share_pct"],"Margen supuesto":r["expected_net_margin_pct"],
            "Utilidad necesaria":g["net_needed"],"Facturación necesaria":g["revenue_needed"],
            "Facturación diaria":g["daily_revenue"],"Días":r["productive_days"]
        })
    if rows:
        section("Fases preconfiguradas")
        df_show(pd.DataFrame(rows))
    with st.form("goal_add"):
        c1,c2,c3=st.columns(3)
        phase=c1.text_input("Fase / nombre")
        partner=c2.number_input("Objetivo chapista",min_value=0.0,step=100000.0)
        owner=c3.number_input("Objetivo tuyo",min_value=0.0,step=100000.0)
        c1,c2,c3=st.columns(3)
        share=c1.slider("Tu %",0,100,40,key="goalshare")/100
        margin=c2.slider("Margen neto esperado",1,80,35)/100
        days=c3.number_input("Días productivos",min_value=1,value=22)
        notes=st.text_area("Notas")
        if st.form_submit_button("Agregar objetivo",type="primary"):
            insert_row("economic_goals",{"phase":phase,"partner_target":partner,"owner_target":owner,"owner_share_pct":share,"expected_net_margin_pct":margin,"productive_days":days,"active":True,"notes":notes})
            st.success("Objetivo agregado.");st.rerun()
    record_manager("economic_goals",df,{"phase":"Fase","notes":"Notas","active":"Activo"})


def page_pricing():
    hero("5 · Inteligencia de precios","Tu baremo propio: cuánto se cotizó, si cerró, cuántas horas consumió y cuánto margen real dejó.")
    df=pricing_enriched(get_df("pricing_cases","case_date DESC"))
    if not df.empty:
        a,b,c,d=st.columns(4)
        a.metric("Casos",len(df))
        a_rate=safe_div(df["accepted"].astype(bool).sum(),len(df))
        b.metric("Aceptación",pct(a_rate))
        c.metric("Margen bruto medio",pct(df["gross_margin_pct"].mean()))
        d.metric("Ganancia/hora media",money(df[df["profit_per_hour"]>0]["profit_per_hour"].mean() if (df["profit_per_hour"]>0).any() else 0))
    with st.form("price_add"):
        c1,c2,c3,c4=st.columns(4)
        dt=c1.date_input("Fecha",value=date.today())
        vehicle=c2.text_input("Vehículo")
        repair=c3.selectbox("Trabajo",["Paragolpes","Puerta","Guardabarros","Zócalo","Capot","Techo","Lateral","Choque leve","Choque medio","Choque grande","Otro"])
        severity=c4.selectbox("Severidad",["Leve","Media","Alta"])
        c1,c2,c3=st.columns(3)
        source=c1.selectbox("Origen referencia",["Propio","Competidor","Chapista","Cliente","Seguro","Otro"])
        chap_ref=c2.number_input("Precio que cobra él hoy",min_value=0.0,step=50000.0)
        comp_ref=c3.number_input("Referencia externa / competidor",min_value=0.0,step=50000.0)
        c1,c2,c3=st.columns(3)
        offered=c1.number_input("Precio ofrecido",min_value=0.0,step=50000.0)
        final=c2.number_input("Precio final cobrado",min_value=0.0,step=50000.0)
        accepted=c3.checkbox("¿Aceptado / cerrado?")
        c1,c2,c3,c4=st.columns(4)
        hours=c1.number_input("Horas reales",min_value=0.0,step=.5)
        material=c2.number_input("Material real",min_value=0.0,step=10000.0)
        other=c3.number_input("Otros costos",min_value=0.0,step=10000.0)
        rework=c4.number_input("Costo retrabajo",min_value=0.0,step=10000.0)
        notes=st.text_area("Notas / detalle del daño")
        if st.form_submit_button("Guardar caso de precio",type="primary"):
            insert_row("pricing_cases",{"case_date":dt,"vehicle":vehicle,"repair_type":repair,"severity":severity,"source":source,"chapista_reference":chap_ref,"competitor_reference":comp_ref,"offered_price":offered,"final_price":final,"accepted":accepted,"labor_hours":hours,"material_cost":material,"other_cost":other,"rework_cost":rework,"notes":notes})
            st.success("Caso guardado.");st.rerun()
    section("Baremo vivo")
    if not df.empty:
        by=df.groupby("repair_type",as_index=False).agg(
            casos=("id","count"),precio_medio=("final_price","mean"),horas=("labor_hours","mean"),
            margen=("gross_margin_pct","mean"),ganancia_hora=("profit_per_hour","mean")
        ).sort_values("casos",ascending=False)
        df_show(by,height=300)
        section("Casos")
        df_show(df)
    else:
        st.info("Cargá los primeros presupuestos para empezar a construir tu baremo.")
    record_manager("pricing_cases",df,{"vehicle":"Vehículo","notes":"Notas","accepted":"Aceptado"})


def page_commercial():
    hero("6 · Laboratorio comercial","Medí cada canal como experimento: consultas → presupuestos → cierres → margen → CAC.")
    df=commercial_enriched(get_df("commercial_trials","trial_date DESC"))
    if not df.empty:
        a,b,c,d,e=st.columns(5)
        a.metric("Consultas",int(df["inquiries"].sum()))
        b.metric("Presupuestos",int(df["quotes"].sum()))
        c.metric("Cierres",int(df["wins"].sum()))
        d.metric("Conversión",pct(safe_div(df["wins"].sum(),df["quotes"].sum())))
        e.metric("CAC global",money(safe_div(df["spend"].sum(),df["wins"].sum())))
    with st.form("commercial_add"):
        c1,c2,c3=st.columns(3)
        dt=c1.date_input("Fecha",value=date.today())
        channel=c2.selectbox("Canal",["Tarjetas / QR","Google","Instagram","Mecánicos","Lavaderos","Compraventas","Seguros","Productores","Flotas","Referidos","Otro"])
        campaign=c3.text_input("Campaña / prueba")
        c1,c2,c3,c4=st.columns(4)
        spend=c1.number_input("Gasto",min_value=0.0,step=10000.0)
        inquiries=c2.number_input("Consultas",min_value=0,step=1)
        quotes=c3.number_input("Presupuestos",min_value=0,step=1)
        wins=c4.number_input("Cierres",min_value=0,step=1)
        c1,c2,c3=st.columns(3)
        revenue=c1.number_input("Facturación atribuida",min_value=0.0,step=50000.0)
        materials=c2.number_input("Materiales atribuibles",min_value=0.0,step=50000.0)
        other=c3.number_input("Otros variables",min_value=0.0,step=50000.0)
        notes=st.text_area("Qué probamos / qué aprendimos")
        if st.form_submit_button("Registrar experimento",type="primary"):
            insert_row("commercial_trials",{"trial_date":dt,"channel":channel,"campaign":campaign,"spend":spend,"inquiries":inquiries,"quotes":quotes,"wins":wins,"revenue":revenue,"material_cost":materials,"other_variable_cost":other,"notes":notes})
            st.success("Experimento guardado.");st.rerun()
    if not df.empty:
        section("Rendimiento por canal")
        by=df.groupby("channel",as_index=False).agg(
            gasto=("spend","sum"),consultas=("inquiries","sum"),presupuestos=("quotes","sum"),
            cierres=("wins","sum"),facturacion=("revenue","sum"),ganancia=("gross_profit","sum")
        )
        by["CAC"]=np.where(by["cierres"]>0,by["gasto"]/by["cierres"],0)
        by["Cierre"]=np.where(by["presupuestos"]>0,by["cierres"]/by["presupuestos"],0)
        by=by.sort_values(["ganancia","cierres"],ascending=False)
        df_show(by,height=330)
        fig=px.bar(by,x="channel",y="ganancia",hover_data=["cierres","CAC","Cierre"],title="Ganancia atribuida por canal")
        fig.update_layout(height=330,margin=dict(l=10,r=10,t=45,b=10))
        st.plotly_chart(fig,use_container_width=True)
        section("Experimentos")
        df_show(df)
    record_manager("commercial_trials",df,{"campaign":"Campaña","notes":"Aprendizaje"})


def page_risks():
    hero("7 · Mapa de riesgos","Probabilidad × impacto, con señal temprana y plan de contingencia. La idea es ver el problema antes de que te cueste plata.")
    df=risk_priority(get_df("risks"))
    if not df.empty:
        open_df=df[df["status"].astype(str)!="Cerrado"]
        a,b,c=st.columns(3)
        a.metric("Riesgos abiertos",len(open_df))
        b.metric("Críticos ≥20",int((open_df["risk_score"]>=20).sum()))
        c.metric("Score máximo",int(open_df["risk_score"].max()) if not open_df.empty else 0)
        heat=open_df.copy()
        if not heat.empty:
            fig=px.scatter(heat,x="probability",y="impact",size="risk_score",hover_name="name",hover_data=["category","status"],range_x=[.5,5.5],range_y=[.5,5.5],title="Matriz probabilidad × impacto")
            fig.update_layout(height=380,margin=dict(l=10,r=10,t=45,b=10))
            st.plotly_chart(fig,use_container_width=True)
    with st.form("risk_add"):
        c1,c2=st.columns(2)
        name=c1.text_input("Riesgo")
        cat=c2.selectbox("Categoría",["Persona clave","Activos","Proveedor","Caja","Calidad","Comercial","Gobernanza","Legal","Seguridad","Otro"])
        c1,c2,c3=st.columns(3)
        prob=c1.slider("Probabilidad",1,5,3)
        impact=c2.slider("Impacto",1,5,3)
        status=c3.selectbox("Estado",["Abierto","Mitigando","Aceptado","Cerrado"])
        mitigation=st.text_area("Plan de contingencia")
        trigger=st.text_area("Señal temprana / gatillo")
        responsible=st.text_input("Responsable",value="Dueño")
        notes=st.text_area("Notas")
        if st.form_submit_button("Agregar riesgo",type="primary"):
            insert_row("risks",{"name":name,"category":cat,"probability":prob,"impact":impact,"mitigation":mitigation,"trigger_signal":trigger,"responsible":responsible,"status":status,"notes":notes})
            st.success("Riesgo agregado.");st.rerun()
    section("Registro de riesgos")
    df_show(df)
    record_manager("risks",df,{"status":"Estado","mitigation":"Mitigación","trigger_signal":"Señal temprana","notes":"Notas"})


def page_agreements():
    hero("8 · Sociedad y negociación","Tu memoria contractual antes del contrato: qué se acordó, qué falta y qué pasa si algo sale mal.")
    df=get_df("agreements")
    with st.form("agreement_add"):
        c1,c2=st.columns(2)
        topic=c1.selectbox("Tema",["Reparto de utilidad","Capital inicial","Herramientas","Caja y cobranzas","Funciones","Compras","Deudas","Salida de uno","Falta de dinero","Decisiones conjuntas","Clientes propios","Marca","Confidencialidad","Otro"])
        status=c2.selectbox("Estado",["Pendiente","En negociación","Acordado verbal","Para formalizar","Formalizado"])
        agreed=st.text_area("Qué acordaron")
        c1,c2=st.columns(2)
        owner= c1.text_area("Tu posición")
        partner=c2.text_area("Posición del chapista")
        rule=st.text_area("Regla de decisión / qué ocurre ante conflicto")
        pending=st.text_area("Qué falta resolver")
        notes=st.text_area("Notas para contador / abogado")
        if st.form_submit_button("Guardar punto de negociación",type="primary"):
            insert_row("agreements",{"topic":topic,"agreed_text":agreed,"owner_position":owner,"partner_position":partner,"decision_rule":rule,"pending_item":pending,"status":status,"notes":notes})
            st.success("Punto guardado.");st.rerun()
    section("Matriz de acuerdos")
    df_show(df)
    record_manager("agreements",df,{"status":"Estado","agreed_text":"Acordado","pending_item":"Pendiente","notes":"Notas"})


def page_independence():
    hero("9 · Plan de independencia","El objetivo no es reemplazar a nadie: es evitar que el valor del negocio dependa de una sola persona, herramienta, proveedor o cuenta.")
    df=get_df("independence_items")
    score=independence_score(df)
    a,b,c=st.columns(3)
    a.metric("Independencia global",f"{score:.0f}/100",score_label(score))
    b.metric("Dependencia persona-clave",f"{100-score:.0f}/100")
    c.metric("Dimensiones",len(df))
    if not df.empty:
        plot=df.copy()
        plot["current_score"]=pd.to_numeric(plot["current_score"],errors="coerce").fillna(0)
        fig=go.Figure(data=go.Scatterpolar(r=plot["current_score"].tolist()+[plot["current_score"].iloc[0]],theta=plot["dimension"].tolist()+[plot["dimension"].iloc[0]],fill="toself"))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),height=430,margin=dict(l=40,r=40,t=25,b=25),showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    with st.form("ind_add"):
        c1,c2=st.columns(2)
        dim=c1.text_input("Nueva dimensión")
        status=c2.selectbox("Estado",["En curso","Bloqueado","Logrado"])
        c1,c2,c3=st.columns(3)
        current=c1.slider("Nivel actual",0,100,0)
        target=c2.slider("Objetivo",1,100,100)
        weight=c3.number_input("Peso",min_value=.1,max_value=5.0,value=1.0,step=.1)
        action=st.text_area("Próxima acción concreta")
        due=st.date_input("Fecha objetivo",value=date.today())
        notes=st.text_area("Notas")
        if st.form_submit_button("Agregar dimensión",type="primary"):
            insert_row("independence_items",{"dimension":dim,"current_score":current,"target_score":target,"weight":weight,"action_plan":action,"due_date":due,"status":status,"notes":notes})
            st.success("Dimensión agregada.");st.rerun()
    section("Plan")
    df_show(df)
    record_manager("independence_items",df,{"current_score":"Nivel actual","target_score":"Objetivo","action_plan":"Próxima acción","status":"Estado","notes":"Notas"})


def page_valuation():
    hero("10 · Valuación del negocio","No es una tasación profesional: es un modelo interno consistente para seguir la evolución del valor económico y de tu participación.")
    df=get_df("valuation_snapshots","snapshot_date DESC")
    with st.form("valuation_add"):
        c1,c2,c3,c4=st.columns(4)
        dt=c1.date_input("Fecha",value=date.today())
        cash=c2.number_input("Caja",min_value=0.0,step=100000.0)
        equip=c3.number_input("Equipamiento propio",min_value=0.0,step=100000.0)
        other_assets=c4.number_input("Otros activos",min_value=0.0,step=100000.0)
        c1,c2,c3=st.columns(3)
        liabilities=c1.number_input("Pasivos / deudas",min_value=0.0,step=100000.0)
        avg_profit=c2.number_input("Utilidad mensual promedio normalizada",min_value=0.0,step=100000.0)
        multiple=c3.number_input("Múltiplo en meses de utilidad",min_value=0.0,value=12.0,step=1.0)
        c1,c2,c3=st.columns(3)
        brand=c1.number_input("Valor de marca estimado",min_value=0.0,step=100000.0)
        customers=c2.number_input("Valor cartera/clientes",min_value=0.0,step=100000.0)
        owner_pct=c3.slider("Tu participación",0,100,40)/100
        notes=st.text_area("Supuestos / notas")
        preview=valuation({"cash":cash,"equipment":equip,"other_assets":other_assets,"liabilities":liabilities,"avg_monthly_profit":avg_profit,"profit_multiple_months":multiple,"brand_value":brand,"customer_value":customers,"owner_pct":owner_pct})
        st.caption(f"Valor patrimonial-operativo estimado: {money(preview['equity'])} · Tu participación: {money(preview['owner_value'])}")
        if st.form_submit_button("Guardar foto de valuación",type="primary"):
            insert_row("valuation_snapshots",{"snapshot_date":dt,"cash":cash,"equipment":equip,"other_assets":other_assets,"liabilities":liabilities,"avg_monthly_profit":avg_profit,"profit_multiple_months":multiple,"brand_value":brand,"customer_value":customers,"owner_pct":owner_pct,"notes":notes})
            st.success("Valuación guardada.");st.rerun()
    if not df.empty:
        out=[]
        for _,r in df.iterrows():
            v=valuation(r)
            out.append({"Fecha":r["snapshot_date"],"Activos":v["assets"],"Valor por rentabilidad":v["earnings_value"],"Intangibles":v["intangible"],"Equity":v["equity"],"Tu valor":v["owner_value"]})
        section("Evolución")
        valdf=pd.DataFrame(out)
        df_show(valdf)
        fig=px.line(valdf.sort_values("Fecha"),x="Fecha",y=["Equity","Tu valor"],markers=True)
        fig.update_layout(height=340,margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig,use_container_width=True)
    record_manager("valuation_snapshots",df,{"notes":"Notas"})


def page_decisions():
    hero("Diario de decisiones","Congelá lo que creías antes de conocer el resultado. Después revisalo contra la realidad y convertí intuición en aprendizaje.")
    df=get_df("decisions","decision_date DESC")
    today=pd.Timestamp(date.today())
    if not df.empty:
        d=df.copy()
        d["review_date"]=pd.to_datetime(d["review_date"],errors="coerce")
        due=d[(d["review_date"].notna())&(d["review_date"]<=today)&(d["status"].astype(str)!="Cerrada")]
        if len(due):
            callout(f"Tenés <b>{len(due)}</b> decisión(es) cuya fecha de revisión ya llegó.", "warn")
    with st.form("decision_add"):
        c1,c2=st.columns(2)
        dt=c1.date_input("Fecha de decisión",value=date.today())
        review=c2.date_input("Revisar el",value=date.today())
        decision=st.text_area("Decisión",placeholder="Ej.: imprimir y repartir tarjetas con QR para captar presupuestos por foto.")
        rationale=st.text_area("Por qué la tomaste")
        expectation=st.text_area("Qué esperabas que ocurriera")
        metric=st.text_input("Métrica de éxito",placeholder="Ej.: 30 cotizaciones mensuales.")
        notes=st.text_area("Notas")
        if st.form_submit_button("Congelar decisión",type="primary"):
            insert_row("decisions",{"decision_date":dt,"decision":decision,"rationale":rationale,"expected_outcome":expectation,"success_metric":metric,"review_date":review,"actual_outcome":"","result":"Sin revisar","learning":"","status":"Abierta","notes":notes})
            st.success("Decisión congelada.");st.rerun()

    section("Historial")
    df_show(df,[ "id","decision_date","decision","expected_outcome","success_metric","review_date","actual_outcome","result","learning","status"])
    if not df.empty:
        with st.expander("Revisar una decisión"):
            rid=st.selectbox("Decisión",df["id"].astype(int).tolist(),format_func=lambda x: f"#{x} · {str(df[df.id==x].iloc[0]['decision'])[:80]}")
            row=df[df.id==rid].iloc[0]
            st.caption(f"Esperabas: {row.get('expected_outcome','')} · Métrica: {row.get('success_metric','')}")
            actual=st.text_area("Qué ocurrió realmente",value="" if pd.isna(row.get("actual_outcome")) else str(row.get("actual_outcome")))
            result=st.selectbox("Resultado",["Sin revisar","Mejor de lo esperado","Como se esperaba","Peor de lo esperado","Inconcluso"],index=0)
            learning=st.text_area("Qué aprendiste",value="" if pd.isna(row.get("learning")) else str(row.get("learning")))
            status=st.selectbox("Estado",["Abierta","Seguimiento","Cerrada"])
            if st.button("Guardar revisión",type="primary"):
                update_row("decisions",rid,{"actual_outcome":actual,"result":result,"learning":learning,"status":status})
                st.success("Revisión guardada.");st.rerun()
        record_manager("decisions",df,{"notes":"Notas"})


def page_system():
    hero("Respaldo / Sistema","La fuente de verdad vive en PostgreSQL externo. Streamlit es solamente la interfaz.")
    try:
        with get_engine().connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        callout("Conexión PostgreSQL activa. Los datos no dependen del ciclo de vida de la app de Streamlit.", "good")
    except Exception as exc:
        callout(f"Error de conexión: {exc}", "bad")

    section("Backup manual descargable")
    st.caption("Genera CSV de todas las tablas en memoria y los comprime en un ZIP. No escribe la base al disco de Streamlit.")
    if st.button("Preparar backup ahora"):
        tables=export_all_tables()
        buff=io.BytesIO()
        with zipfile.ZipFile(buff,"w",zipfile.ZIP_DEFLATED) as z:
            for name,df in tables.items():
                z.writestr(f"{name}.csv",df.to_csv(index=False).encode("utf-8-sig"))
        st.download_button("Descargar backup ZIP",data=buff.getvalue(),file_name=f"owner_os_backup_{datetime.now():%Y%m%d_%H%M}.zip",mime="application/zip",use_container_width=True)
    section("Arquitectura")
    st.code("Streamlit UI  →  SQLAlchemy  →  PostgreSQL externo (Supabase recomendado)")
    st.caption("La contraseña y DATABASE_URL se guardan en Secrets, nunca en el repositorio.")


if page=="dashboard": page_dashboard()
elif page=="actuals": page_actuals()
elif page=="thesis": page_thesis()
elif page=="capital": page_capital()
elif page=="simulator": page_simulator()
elif page=="goals": page_goals()
elif page=="pricing": page_pricing()
elif page=="commercial": page_commercial()
elif page=="risks": page_risks()
elif page=="agreements": page_agreements()
elif page=="independence": page_independence()
elif page=="valuation": page_valuation()
elif page=="decisions": page_decisions()
elif page=="system": page_system()
