from __future__ import annotations

from datetime import date
import math
import pandas as pd
import numpy as np


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0)
    return out


def capital_metrics(df: pd.DataFrame, owner_name: str = "Yo") -> dict:
    if df.empty:
        return dict(contributed=0, recovered=0, exposed=0, recoverable_exposed=0, sunk=0, partner_net=0)
    x = numeric(df, ["amount"])
    owner = x[x["contributor"].astype(str) == owner_name].copy()
    aportes = owner[owner["direction"] == "Aporte"]["amount"].sum()
    recuperos = owner[owner["direction"] == "Recupero"]["amount"].sum()
    exposed = max(aportes - recuperos, 0)
    rec_ap = owner[(owner["direction"] == "Aporte") & (owner["recoverable"].astype(bool))]["amount"].sum()
    rec_rec = owner[(owner["direction"] == "Recupero") & (owner["recoverable"].astype(bool))]["amount"].sum()
    recoverable_exposed = max(rec_ap - rec_rec, 0)
    sunk = owner[(owner["direction"] == "Aporte") & (~owner["recoverable"].astype(bool))]["amount"].sum()
    partner = x[x["contributor"].astype(str) == "Chapista"].copy()
    partner_net = partner.apply(lambda r: r["amount"] if r["direction"]=="Aporte" else -r["amount"], axis=1).sum() if not partner.empty else 0
    return dict(
        contributed=float(aportes), recovered=float(recuperos), exposed=float(exposed),
        recoverable_exposed=float(recoverable_exposed), sunk=float(sunk), partner_net=float(partner_net)
    )


def simulate(
    rent: float, fixed_costs: float, avg_ticket: float, jobs: int, productive_days: int,
    material_pct: float, taxes_pct: float, ads: float, helper_cost: float,
    other_costs: float, owner_share_pct: float
) -> dict:
    jobs = max(int(jobs), 0)
    productive_days = max(int(productive_days), 1)
    revenue = max(float(avg_ticket), 0) * jobs
    variable_pct = min(max(float(material_pct) + float(taxes_pct), 0), .95)
    variable_costs = revenue * variable_pct
    fixed = max(float(rent),0)+max(float(fixed_costs),0)+max(float(ads),0)+max(float(helper_cost),0)+max(float(other_costs),0)
    net = revenue - variable_costs - fixed
    owner_share_pct = min(max(float(owner_share_pct),0),1)
    partner_share_pct = 1-owner_share_pct
    owner_profit = max(net,0) * owner_share_pct
    partner_profit = max(net,0) * partner_share_pct
    contribution_margin = 1-variable_pct
    break_even = fixed/contribution_margin if contribution_margin > 0 else float("inf")
    jobs_break_even = math.ceil(break_even/max(float(avg_ticket),1)) if np.isfinite(break_even) else 0
    return {
        "revenue": revenue,
        "variable_costs": variable_costs,
        "fixed_costs_total": fixed,
        "net_profit": net,
        "net_margin": net/revenue if revenue else 0,
        "owner_profit": owner_profit,
        "partner_profit": partner_profit,
        "owner_share_pct": owner_share_pct,
        "partner_share_pct": partner_share_pct,
        "break_even_revenue": break_even,
        "break_even_jobs": jobs_break_even,
        "daily_revenue": revenue/productive_days,
        "daily_net": net/productive_days,
    }


def goal_math(owner_target, partner_target, owner_share_pct, net_margin_pct, productive_days):
    owner_share_pct = max(min(float(owner_share_pct), .99), .01)
    partner_share_pct = 1-owner_share_pct
    needed_for_owner = float(owner_target)/owner_share_pct
    needed_for_partner = float(partner_target)/partner_share_pct
    net_needed = max(needed_for_owner, needed_for_partner)
    margin = max(float(net_margin_pct), .01)
    revenue_needed = net_needed/margin
    days = max(int(productive_days), 1)
    return {
        "net_needed": net_needed,
        "revenue_needed": revenue_needed,
        "daily_revenue": revenue_needed/days,
        "daily_net": net_needed/days,
        "owner_check": net_needed*owner_share_pct,
        "partner_check": net_needed*partner_share_pct,
    }


def pricing_enriched(df):
    if df.empty: return df
    x = numeric(df, ["chapista_reference","competitor_reference","offered_price","final_price","labor_hours","material_cost","other_cost","rework_cost"])
    x["direct_cost"] = x["material_cost"] + x["other_cost"] + x["rework_cost"]
    x["gross_profit"] = x["final_price"] - x["direct_cost"]
    x["gross_margin_pct"] = np.where(x["final_price"]>0, x["gross_profit"]/x["final_price"], 0)
    x["revenue_per_hour"] = np.where(x["labor_hours"]>0, x["final_price"]/x["labor_hours"], 0)
    x["profit_per_hour"] = np.where(x["labor_hours"]>0, x["gross_profit"]/x["labor_hours"], 0)
    return x


def commercial_enriched(df):
    if df.empty: return df
    x = numeric(df, ["spend","inquiries","quotes","wins","revenue","material_cost","other_variable_cost"])
    x["cac"] = np.where(x["wins"]>0, x["spend"]/x["wins"], 0)
    x["quote_rate"] = np.where(x["inquiries"]>0, x["quotes"]/x["inquiries"], 0)
    x["close_rate"] = np.where(x["quotes"]>0, x["wins"]/x["quotes"], 0)
    x["gross_profit"] = x["revenue"] - x["material_cost"] - x["other_variable_cost"] - x["spend"]
    x["roas"] = np.where(x["spend"]>0, x["revenue"]/x["spend"], 0)
    return x


def actual_enriched(df):
    if df.empty: return df
    cols = ["revenue","materials","payroll","rent","utilities","advertising","taxes","other_costs","jobs","inquiries","quotes","reworks","receivables","owner_share_pct"]
    x = numeric(df, cols)
    x["total_costs"] = x[["materials","payroll","rent","utilities","advertising","taxes","other_costs"]].sum(axis=1)
    x["net_profit"] = x["revenue"] - x["total_costs"]
    x["net_margin_pct"] = np.where(x["revenue"]>0, x["net_profit"]/x["revenue"],0)
    x["owner_profit"] = np.maximum(x["net_profit"],0)*x["owner_share_pct"]
    x["partner_profit"] = np.maximum(x["net_profit"],0)*(1-x["owner_share_pct"])
    x["ticket_avg"] = np.where(x["jobs"]>0,x["revenue"]/x["jobs"],0)
    x["close_rate"] = np.where(x["quotes"]>0,x["jobs"]/x["quotes"],0)
    x["rework_rate"] = np.where(x["jobs"]>0,x["reworks"]/x["jobs"],0)
    return x


def independence_score(df):
    if df.empty: return 0.0
    x = numeric(df, ["current_score","target_score","weight"])
    ratios = np.where(x["target_score"]>0, np.minimum(x["current_score"]/x["target_score"],1),0)
    w = x["weight"].replace(0,1)
    return float(np.average(ratios*100, weights=w)) if len(x) else 0


def valuation(row):
    assets = float(row.get("cash",0))+float(row.get("equipment",0))+float(row.get("other_assets",0))
    earnings_value = max(float(row.get("avg_monthly_profit",0)),0)*max(float(row.get("profit_multiple_months",0)),0)
    intangible = float(row.get("brand_value",0))+float(row.get("customer_value",0))
    gross_value = assets + earnings_value + intangible
    equity = max(gross_value-float(row.get("liabilities",0)),0)
    owner_value = equity*float(row.get("owner_pct",0))
    return {
        "assets": assets, "earnings_value": earnings_value, "intangible": intangible,
        "equity": equity, "owner_value": owner_value
    }


def risk_priority(df):
    if df.empty: return df
    x = numeric(df, ["probability","impact"])
    x["risk_score"] = x["probability"]*x["impact"]
    return x.sort_values(["risk_score","impact"], ascending=False)


def owner_alerts(capital, actuals, risks, independence, pricing, commercial):
    alerts = []
    if capital.get("exposed",0) > 0 and capital.get("recovered",0) == 0:
        alerts.append(("warn", f"Capital expuesto sin recuperos registrados: {capital['exposed']:,.0f}."))
    if not actuals.empty:
        latest = actuals.sort_values("period_date").iloc[-1]
        if float(latest.get("net_profit",0)) < 0:
            alerts.append(("bad","El último período real cerró con pérdida operativa."))
        if float(latest.get("rework_rate",0)) > .08:
            alerts.append(("warn",f"Retrabajos altos en el último período: {latest['rework_rate']:.1%}."))
        if float(latest.get("receivables",0)) > max(float(latest.get("revenue",0))*.35,1):
            alerts.append(("warn","Cuentas a cobrar elevadas respecto de la facturación del último período."))
    if not risks.empty:
        top = risks[risks["status"].astype(str)!="Cerrado"]
        if "risk_score" in top and (top["risk_score"]>=20).any():
            alerts.append(("bad","Hay riesgos críticos abiertos (score ≥ 20)."))
    if independence < 40:
        alerts.append(("bad",f"Independencia estructural baja: {independence:.0f}/100."))
    if not pricing.empty and float(pricing["gross_margin_pct"].mean()) < .30:
        alerts.append(("warn","El margen bruto promedio de los casos de precios está por debajo de 30%."))
    if not commercial.empty:
        total_spend = commercial["spend"].sum()
        total_wins = commercial["wins"].sum()
        if total_spend > 0 and total_wins == 0:
            alerts.append(("bad","Hay inversión comercial registrada pero todavía ningún cierre atribuido."))
    if not alerts:
        alerts.append(("good","No hay alertas estructurales disparadas con los datos actuales."))
    return alerts
