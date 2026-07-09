# =============================================================
# frontend/calculator.py
# Financial Calculator page for Money Matters.
#
# Tools: SIP, Step-Up SIP, Lump Sum, EMI, FD, PPF,
#        Loan Eligibility, Income Tax, CAGR
#
# Each tool has:
#   • Input form with validation
#   • Hero result card (teal gradient)
#   • Breakdown table
#   • AI explanation from Granite
#   • Bar chart from st.bar_chart
# =============================================================

from __future__ import annotations

import streamlit as st

from backend.models import CalculatorResult
from backend.session import get_current_user, is_authenticated
from frontend.components import (
    calc_result_card,
    calc_breakdown_table,
    section_header,
    divider,
)
from frontend.styles import COLORS
from services.calculator_service import run_calculator
from utils.logger import logger


# ── AI Explanation helper ─────────────────────────────────────

def _get_ai_explanation(result: CalculatorResult) -> str:
    try:
        from services.watsonx_service import generate_short
        from utils.prompts import build_calculator_prompt
        prompt = build_calculator_prompt(
            calculator_type = result.calculator_type,
            inputs          = str(result.inputs),
            result          = str({k: v for k, v in result.result.items()
                                   if not k.startswith("_")}),
        )
        return generate_short(prompt, max_tokens=200)
    except Exception as exc:
        logger.warning("Calculator AI explanation skipped: {}", exc)
        return ""


# ── Individual tool UIs ───────────────────────────────────────

def _sip_tool() -> None:
    st.markdown("**Calculate how much your monthly SIP will grow.**")
    c1, c2, c3 = st.columns(3)
    monthly = c1.number_input("Monthly Investment (₹)", min_value=100.0,
                               value=5000.0, step=500.0, key="sip_monthly")
    rate    = c2.number_input("Expected Return (% p.a.)", min_value=1.0,
                               max_value=50.0, value=12.0, step=0.5, key="sip_rate")
    years   = c3.number_input("Tenure (years)", min_value=1, max_value=50,
                               value=10, step=1, key="sip_years")

    if st.button("Calculate SIP", key="btn_sip", type="primary"):
        try:
            result = run_calculator("sip", monthly_investment=monthly,
                                    annual_return_rate=rate, tenure_years=float(years))
            _render_result(result, chart_keys=("total_invested", "total_returns"))
        except ValueError as e:
            st.error(str(e))


def _stepup_sip_tool() -> None:
    st.markdown("**SIP with annual step-up — accelerate your corpus.**")
    c1, c2, c3, c4 = st.columns(4)
    monthly  = c1.number_input("Starting SIP (₹)", min_value=100.0,
                                value=5000.0, step=500.0, key="ss_monthly")
    step_up  = c2.number_input("Annual Step-Up (%)", min_value=0.0,
                                max_value=50.0, value=10.0, key="ss_stepup")
    rate     = c3.number_input("Return (% p.a.)", min_value=1.0,
                                max_value=50.0, value=12.0, key="ss_rate")
    years    = c4.number_input("Years", min_value=1, max_value=50,
                                value=10, key="ss_years")

    if st.button("Calculate", key="btn_stepup", type="primary"):
        try:
            result = run_calculator(
                "step_up_sip",
                monthly_investment      = monthly,
                annual_return_rate      = rate,
                tenure_years            = float(years),
                annual_step_up_percent  = step_up,
            )
            _render_result(result, chart_keys=("total_invested", "total_returns"))
        except ValueError as e:
            st.error(str(e))


def _lumpsum_tool() -> None:
    st.markdown("**One-time investment growth calculator.**")
    c1, c2, c3 = st.columns(3)
    principal = c1.number_input("Investment Amount (₹)", min_value=1000.0,
                                 value=100000.0, step=10000.0, key="ls_principal")
    rate      = c2.number_input("Expected Return (% p.a.)", min_value=1.0,
                                 max_value=50.0, value=12.0, key="ls_rate")
    years     = c3.number_input("Tenure (years)", min_value=1, max_value=50,
                                 value=10, key="ls_years")

    if st.button("Calculate", key="btn_lumpsum", type="primary"):
        try:
            result = run_calculator("lumpsum", principal=principal,
                                    annual_return_rate=rate, tenure_years=float(years))
            _render_result(result, chart_keys=("total_invested", "total_returns"))
        except ValueError as e:
            st.error(str(e))


def _emi_tool() -> None:
    st.markdown("**Calculate your monthly loan EMI and total cost.**")
    c1, c2, c3 = st.columns(3)
    principal = c1.number_input("Loan Amount (₹)", min_value=10000.0,
                                 value=1000000.0, step=50000.0, key="emi_principal")
    rate      = c2.number_input("Interest Rate (% p.a.)", min_value=1.0,
                                 max_value=50.0, value=8.5, step=0.25, key="emi_rate")
    months    = c3.number_input("Tenure (months)", min_value=1, max_value=600,
                                 value=240, step=12, key="emi_months")

    if st.button("Calculate EMI", key="btn_emi", type="primary"):
        try:
            result = run_calculator("emi", principal=principal,
                                    annual_interest_rate=rate, tenure_months=int(months))
            _render_result(result, chart_keys=("principal", "total_interest"),
                           primary_key="Monthly EMI")
        except ValueError as e:
            st.error(str(e))


def _fd_tool() -> None:
    st.markdown("**Fixed Deposit maturity calculator.**")
    c1, c2, c3, c4 = st.columns(4)
    principal   = c1.number_input("Deposit Amount (₹)", min_value=1000.0,
                                   value=100000.0, step=10000.0, key="fd_principal")
    rate        = c2.number_input("Interest Rate (% p.a.)", min_value=1.0,
                                   max_value=20.0, value=7.0, step=0.25, key="fd_rate")
    years       = c3.number_input("Tenure (years)", min_value=1, max_value=10,
                                   value=3, key="fd_years")
    compounding = c4.selectbox("Compounding", ["quarterly", "monthly", "annually"],
                                key="fd_comp")

    if st.button("Calculate FD", key="btn_fd", type="primary"):
        try:
            result = run_calculator("fd", principal=principal,
                                    annual_interest_rate=rate, tenure_years=float(years),
                                    compounding=compounding)
            _render_result(result, chart_keys=("principal", "total_interest"),
                           primary_key="Maturity Amount")
        except ValueError as e:
            st.error(str(e))


def _ppf_tool() -> None:
    st.markdown("**PPF maturity calculator — EEE tax benefits.**")
    c1, c2, c3 = st.columns(3)
    annual  = c1.number_input("Annual Investment (₹)", min_value=500.0,
                               max_value=150000.0, value=150000.0, key="ppf_annual")
    rate    = c2.number_input("Interest Rate (%)", min_value=1.0, max_value=15.0,
                               value=7.1, step=0.1, key="ppf_rate")
    years   = c3.number_input("Tenure (years)", min_value=15, max_value=50,
                               value=15, key="ppf_years")

    if st.button("Calculate PPF", key="btn_ppf", type="primary"):
        try:
            result = run_calculator("ppf", annual_investment=annual,
                                    annual_interest_rate=rate, tenure_years=int(years))
            _render_result(result, chart_keys=("total_invested", "total_interest"),
                           primary_key="Maturity Amount")
        except ValueError as e:
            st.error(str(e))


def _loan_eligibility_tool() -> None:
    st.markdown("**Estimate your maximum loan eligibility based on RBI FOIR.**")
    c1, c2, c3, c4 = st.columns(4)
    income      = c1.number_input("Monthly Income (₹)", min_value=10000.0,
                                   value=80000.0, step=5000.0, key="le_income")
    obligations = c2.number_input("Existing EMIs (₹)", min_value=0.0,
                                   value=10000.0, step=1000.0, key="le_oblig")
    rate        = c3.number_input("Loan Rate (% p.a.)", min_value=1.0,
                                   max_value=30.0, value=8.5, key="le_rate")
    months      = c4.number_input("Tenure (months)", min_value=12, max_value=360,
                                   value=240, step=12, key="le_months")

    if st.button("Check Eligibility", key="btn_le", type="primary"):
        try:
            result = run_calculator("loan_eligibility", monthly_income=income,
                                    monthly_obligations=obligations,
                                    annual_interest_rate=rate, tenure_months=int(months))
            _render_result(result, primary_key="Maximum Loan Amount")
        except ValueError as e:
            st.error(str(e))


def _income_tax_tool() -> None:
    st.markdown("**Estimate income tax for FY 2024-25 (AY 2025-26).**")
    c1, c2 = st.columns(2)
    gross   = c1.number_input("Gross Annual Income (₹)", min_value=0.0,
                               value=1200000.0, step=50000.0, key="tax_gross")
    regime  = c2.selectbox("Tax Regime", ["new", "old"], key="tax_regime")

    ded_80c  = 0.0
    ded_other= 0.0
    hra_ex   = 0.0

    if regime == "old":
        st.markdown("**Old Regime Deductions**")
        d1, d2, d3 = st.columns(3)
        ded_80c   = d1.number_input("Section 80C (₹)", min_value=0.0,
                                    max_value=150000.0, value=150000.0, key="tax_80c")
        ded_other = d2.number_input("Other Deductions (₹)", min_value=0.0,
                                    value=0.0, key="tax_other")
        hra_ex    = d3.number_input("HRA Exemption (₹)", min_value=0.0,
                                    value=0.0, key="tax_hra")

    if st.button("Estimate Tax", key="btn_tax", type="primary"):
        try:
            result = run_calculator("income_tax", gross_income=gross, regime=regime,
                                    deductions_80c=ded_80c, deductions_other=ded_other,
                                    hra_exempt=hra_ex)
            _render_result(result, primary_key="Total Tax Payable")
        except ValueError as e:
            st.error(str(e))


def _cagr_tool() -> None:
    st.markdown("**Measure the annualised growth of any investment.**")
    c1, c2, c3 = st.columns(3)
    initial = c1.number_input("Initial Value (₹)", min_value=1.0,
                               value=100000.0, key="cagr_initial")
    final   = c2.number_input("Final Value (₹)", min_value=1.0,
                               value=200000.0, key="cagr_final")
    years   = c3.number_input("Period (years)", min_value=1, max_value=50,
                               value=5, key="cagr_years")

    if st.button("Calculate CAGR", key="btn_cagr", type="primary"):
        try:
            result = run_calculator("cagr", initial_value=initial,
                                    final_value=final, tenure_years=float(years))
            _render_result(result, primary_key="CAGR")
        except ValueError as e:
            st.error(str(e))


# ── Result renderer ───────────────────────────────────────────

def _render_result(
    result      : CalculatorResult,
    chart_keys  : tuple[str, str] | None = None,
    primary_key : str = "Maturity Value",
) -> None:
    """Render a CalculatorResult: hero card + table + chart + AI explanation."""

    raw     = result.result.get("_raw", {})
    display = {k: v for k, v in result.result.items() if not k.startswith("_")}

    # Hero card
    hero_value = display.get(primary_key, list(display.values())[0] if display else "")
    calc_result_card(primary_key, str(hero_value))

    # Breakdown table
    calc_breakdown_table(display)

    # Bar chart
    if chart_keys and all(k in raw for k in chart_keys):
        import pandas as pd
        chart_data = pd.DataFrame({
            "Amount (₹)": [raw[chart_keys[0]], raw[chart_keys[1]]],
        }, index=[chart_keys[0].replace("_", " ").title(),
                  chart_keys[1].replace("_", " ").title()])
        st.bar_chart(chart_data, color=COLORS["primary"])

    # AI explanation
    divider()
    with st.spinner("Getting AI insights..."):
        explanation = _get_ai_explanation(result)
    if explanation:
        st.markdown(
            f"""
            <div style="background:{COLORS['surface']};
                        border:1px solid {COLORS['border']};
                        border-radius:10px;padding:1rem 1.25rem;
                        font-size:14px;color:{COLORS['text']};">
                🤖 <strong>Money Matters AI:</strong> {explanation}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Tool registry ─────────────────────────────────────────────

_TOOLS = {
    "SIP Calculator"        : _sip_tool,
    "Step-Up SIP"           : _stepup_sip_tool,
    "Lump Sum"              : _lumpsum_tool,
    "EMI Calculator"        : _emi_tool,
    "FD Calculator"         : _fd_tool,
    "PPF Calculator"        : _ppf_tool,
    "Loan Eligibility"      : _loan_eligibility_tool,
    "Income Tax Estimator"  : _income_tax_tool,
    "CAGR Calculator"       : _cagr_tool,
}


# ── Main render ────────────────────────────────────────────────

def render_calculator() -> None:
    """Render the Financial Calculator page."""
    section_header(
        "Financial Calculator",
        "Precise calculations with AI-powered explanations",
    )

    tool_name = st.selectbox(
        "Select Calculator",
        list(_TOOLS.keys()),
        key="calc_tool_selector",
        label_visibility="collapsed",
    )

    divider()

    fn = _TOOLS.get(tool_name)
    if fn:
        fn()


__all__ = ["render_calculator"]
