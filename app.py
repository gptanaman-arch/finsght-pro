import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings, io
from datetime import datetime
from fpdf import FPDF

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="FinSight Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #0D1117 !important;
    color: #C9D1D9;
    -webkit-font-smoothing: antialiased;
}
.main { background: #0D1117 !important; }
.block-container { padding: 0.75rem 0.75rem 3rem !important; max-width: 1280px !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #010409 !important;
    border-right: 1px solid #21262D !important;
}
section[data-testid="stSidebar"] * { color: #C9D1D9 !important; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] input {
    background: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    color: #E6EDF3 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #238636, #2EA043) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important; font-size: 14px !important;
    padding: 13px !important; transition: all 0.2s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #2EA043, #3FB950) !important;
    box-shadow: 0 0 16px rgba(46,160,67,0.5) !important;
    transform: translateY(-1px) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #161B22; border: 1px solid #21262D;
    border-radius: 10px; padding: 4px; gap: 2px;
    overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    border-radius: 7px; font-weight: 600; font-size: 13px;
    color: #8B949E !important; padding: 8px 14px;
    white-space: nowrap; flex-shrink: 0;
}
.stTabs [aria-selected="true"] {
    background: #21262D !important; color: #E6EDF3 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.4) !important;
}

/* Cards */
.card {
    background: #161B22; border: 1px solid #21262D;
    border-radius: 14px; padding: 20px; margin-bottom: 16px;
}

/* KPI strip - 3 cols mobile, 6 cols desktop */
.kpi-strip {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px; margin-bottom: 16px;
}
@media (min-width: 700px) { .kpi-strip { grid-template-columns: repeat(6, 1fr); } }

.kpi-box {
    background: #161B22; border: 1px solid #21262D;
    border-radius: 12px; padding: 14px 12px;
    border-top: 3px solid var(--ac, #30363D);
    transition: all 0.2s;
}
.kpi-box:hover { border-color: #30363D; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }
.kpi-label { font-size: 10px; font-weight: 600; color: #8B949E; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
.kpi-value { font-family: 'Sora', sans-serif; font-size: clamp(15px, 3vw, 22px); font-weight: 700; color: #E6EDF3; line-height: 1; }
.kpi-sub   { font-size: 10px; color: #6E7681; margin-top: 4px; }

/* Hero */
.hero {
    background: #161B22; border: 1px solid #21262D;
    border-radius: 16px;
    padding: clamp(16px,4vw,28px) clamp(16px,4vw,32px);
    margin-bottom: 16px; position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -80px; right: -80px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(46,160,67,0.1) 0%, transparent 70%);
    pointer-events: none;
}
.hero-name {
    font-family: 'Sora', sans-serif;
    font-size: clamp(18px,5vw,30px);
    font-weight: 800; color: #E6EDF3; letter-spacing: -0.5px;
}
.hero-ticker {
    display: inline-block;
    background: rgba(46,160,67,0.15); border: 1px solid rgba(46,160,67,0.35);
    border-radius: 6px; padding: 2px 10px;
    font-size: 12px; color: #3FB950; font-weight: 700;
    margin-left: 8px; vertical-align: middle;
}
.hero-badges { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.badge {
    background: #21262D; border: 1px solid #30363D;
    border-radius: 20px; padding: 3px 10px;
    font-size: 11px; color: #8B949E;
}
.badge.up   { border-color:rgba(63,185,80,0.4);  color:#3FB950; background:rgba(63,185,80,0.08); }
.badge.down { border-color:rgba(248,81,73,0.4);  color:#F85149; background:rgba(248,81,73,0.08); }

/* Section title */
.sec-title {
    font-family: 'Sora', sans-serif; font-size: 14px; font-weight: 700;
    color: #E6EDF3; margin-bottom: 14px; padding-bottom: 10px;
    border-bottom: 1px solid #21262D; display: flex; align-items: center; gap: 8px;
}
.dot { width:8px; height:8px; border-radius:50%; display:inline-block; flex-shrink:0; }

/* Explain card */
.explain {
    background: #0D1117; border: 1px solid #21262D;
    border-left: 3px solid var(--ac, #58A6FF);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px; margin: 8px 0;
    font-size: 12.5px; color: #8B949E; line-height: 1.7;
}
.explain b { color: #C9D1D9; }
.explain .g { color: #3FB950; font-weight: 600; }
.explain .r { color: #F85149; font-weight: 600; }
.formula {
    background: #161B22; border: 1px solid #21262D;
    border-radius: 6px; padding: 6px 12px;
    font-family: monospace; font-size: 12px; color: #79C0FF;
    margin: 6px 0; display: block;
}

/* Ratio table */
.tw { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.rt { width:100%; border-collapse:collapse; font-size:clamp(11px,2vw,13px); min-width:320px; }
.rt th {
    background:#21262D; color:#8B949E; font-weight:600; font-size:11px;
    padding:10px 14px; text-align:center; text-transform:uppercase; letter-spacing:0.5px; white-space:nowrap;
}
.rt th:first-child { text-align:left; }
.rt td { padding:9px 14px; border-bottom:1px solid #161B22; text-align:center; color:#C9D1D9; white-space:nowrap; }
.rt td:first-child { text-align:left; color:#E6EDF3; font-weight:500; }
.rt tr:hover td { background:#161B22; }
.rt .pos { color:#3FB950; font-weight:600; }
.rt .neg { color:#F85149; font-weight:600; }
.rt .cat td { background:#161B22 !important; color:#58A6FF !important; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1px; }

/* Piotroski */
.pf-grid { display:grid; grid-template-columns:1fr 1fr; gap:7px; margin-top:12px; }
@media(min-width:480px){ .pf-grid { grid-template-columns:repeat(3,1fr); } }
.pfi { padding:8px 10px; border-radius:8px; font-size:11.5px; font-weight:600; display:flex; align-items:center; gap:6px; }
.pfi.pass { background:rgba(63,185,80,0.1); border:1px solid rgba(63,185,80,0.3); color:#3FB950; }
.pfi.fail { background:rgba(248,81,73,0.08); border:1px solid rgba(248,81,73,0.2); color:#F85149; }

/* Score ring */
.ring-wrap { display:flex; flex-direction:column; align-items:center; padding:20px 10px; }
.ring {
    width:clamp(100px,25vw,130px); height:clamp(100px,25vw,130px);
    border-radius:50%; display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    border: 6px solid var(--rc, #30363D);
    background:#0D1117;
    box-shadow: 0 0 24px var(--rg, transparent);
}
.ring-num { font-family:'Sora',sans-serif; font-size:clamp(28px,6vw,38px); font-weight:800; color:var(--rc,#E6EDF3); line-height:1; }
.ring-den { font-size:13px; color:#8B949E; }
.ring-lbl { font-size:12px; font-weight:700; margin-top:10px; }

/* Val card */
.val-row { display:flex; gap:10px; flex-wrap:wrap; }
.vc { background:#0D1117; border:1px solid #21262D; border-radius:12px; padding:18px; text-align:center; flex:1; min-width:130px; }
.vc-lbl { font-size:11px; color:#8B949E; text-transform:uppercase; letter-spacing:0.6px; margin-bottom:8px; font-weight:600; }
.vc-num { font-family:'Sora',sans-serif; font-size:clamp(18px,4vw,26px); font-weight:800; color:#58A6FF; }
.vc-sub { font-size:11px; margin-top:6px; font-weight:600; }

/* Info box */
.infobox {
    background:#161B22; border:1px solid #30363D; border-radius:10px;
    padding:14px 16px; font-size:12.5px; color:#8B949E; line-height:1.7; margin-top:8px;
}
.infobox b { color:#C9D1D9; }

/* Download btn */
.stDownloadButton > button {
    background:#21262D !important; color:#E6EDF3 !important;
    border:1px solid #30363D !important; border-radius:8px !important;
    font-weight:600 !important; font-size:13px !important;
    width:100% !important; padding:10px !important; transition:all 0.2s !important;
}
.stDownloadButton > button:hover { background:#30363D !important; border-color:#58A6FF !important; }

/* Metrics */
[data-testid="stMetric"] { background:#161B22 !important; border:1px solid #21262D !important; border-radius:10px !important; padding:12px 14px !important; }
[data-testid="stMetricLabel"] { color:#8B949E !important; font-size:11px !important; }
[data-testid="stMetricValue"] { color:#E6EDF3 !important; font-family:'Sora',sans-serif !important; font-size:20px !important; }
[data-testid="stMetricDelta"] { font-size:11px !important; }

/* Misc */
hr { border-color:#21262D !important; }
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0D1117; }
::-webkit-scrollbar-thumb { background:#30363D; border-radius:4px; }
.footer { text-align:center; color:#6E7681; font-size:11px; padding:20px; border-top:1px solid #21262D; margin-top:20px; }
.empty { text-align:center; padding:60px 20px; }
.empty-icon { font-size:56px; margin-bottom:16px; }
.empty-title { font-family:'Sora',sans-serif; font-size:clamp(18px,4vw,24px); font-weight:700; color:#E6EDF3; margin-bottom:8px; }
.empty-sub { color:#6E7681; font-size:14px; line-height:1.8; }

/* Sidebar logo */
.sb-logo { padding:20px 16px 14px; border-bottom:1px solid #21262D; margin-bottom:8px; }
.sb-title { font-family:'Sora',sans-serif; font-size:18px; font-weight:800; color:#E6EDF3 !important; }
.live-dot {
    display:inline-block; width:7px; height:7px;
    background:#3FB950; border-radius:50%;
    box-shadow:0 0 6px #3FB950; margin-right:5px; vertical-align:middle;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{box-shadow:0 0 6px #3FB950;} 50%{box-shadow:0 0 14px #3FB950;} }
.sb-label { font-size:10px !important; color:#8B949E !important; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-top:14px; display:block; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# METRIC EXPLANATIONS
# ══════════════════════════════════════════════════════════════
EXPLAIN = {
    "Revenue (Cr)": dict(
        what="Total money earned from selling goods/services before any costs are deducted. The 'top line'.",
        formula="Revenue = Sales + Other Operating Income",
        good="Consistent YoY growth shows business expansion",
        bad="Declining or stagnant revenue is a red flag", color="#58A6FF"),
    "Net Income (Cr)": dict(
        what="Actual profit after ALL expenses, taxes, and interest. What the company truly earned.",
        formula="Net Income = Revenue − All Expenses − Tax",
        good="Positive and growing consistently", bad="Negative means the company is losing money", color="#3FB950"),
    "FCF (Cr)": dict(
        what="Cash left over after operations and capital investment. More reliable than profit as it's hard to fake.",
        formula="FCF = Operating Cash Flow − Capital Expenditures",
        good="Positive FCF = real cash generation", bad="Consistently negative FCF = burning cash", color="#E3B341"),
    "Gross Margin %": dict(
        what="Profit remaining after paying to produce goods. Reflects pricing power and cost control.",
        formula="Gross Margin = (Revenue − Cost of Goods Sold) / Revenue × 100",
        good=">40% strong, >60% exceptional (tech/pharma)", bad="<20% suggests low pricing power", color="#58A6FF"),
    "Operating Margin %": dict(
        what="Profit from core business before interest and tax. Measures operational efficiency.",
        formula="Operating Margin = Operating Income / Revenue × 100",
        good=">15% healthy, >25% excellent", bad="<5% very tight, negative = operating loss", color="#79C0FF"),
    "Net Margin %": dict(
        what="Final profit percentage after ALL costs including taxes. The truest measure of profitability.",
        formula="Net Margin = Net Income / Revenue × 100",
        good=">10% good, >20% excellent", bad="<3% very tight, negative = net loss", color="#3FB950"),
    "EBITDA Margin %": dict(
        what="Earnings before interest, taxes, depreciation and amortisation. Proxy for operating cash flow.",
        formula="EBITDA Margin = EBITDA / Revenue × 100",
        good=">20% strong across most sectors", bad="<10% signals operational challenges", color="#D2A8FF"),
    "ROA %": dict(
        what="How efficiently management uses total assets to generate profit. Higher = better use of assets.",
        formula="ROA = Net Income / Total Assets × 100",
        good=">5% decent, >10% excellent", bad="<2% poor asset utilisation", color="#79C0FF"),
    "ROE %": dict(
        what="Returns generated for shareholders on their equity investment. Key metric for investors.",
        formula="ROE = Net Income / Shareholders Equity × 100",
        good=">15% healthy, >20% excellent", bad="<10% below expectations, negative = destroying value", color="#3FB950"),
    "Current Ratio": dict(
        what="Can the company pay debts due within 1 year? Ratio of short-term assets to short-term liabilities.",
        formula="Current Ratio = Current Assets / Current Liabilities",
        good="1.5 to 3.0 is ideal range", bad="<1.0 = more short-term debt than assets, danger zone", color="#58A6FF"),
    "Quick Ratio": dict(
        what="Stricter liquidity test — excludes inventory which may not sell quickly. Crisis survival measure.",
        formula="Quick Ratio = (Current Assets − Inventory) / Current Liabilities",
        good=">1.0 = can meet all short-term obligations", bad="<0.5 is a serious warning sign", color="#79C0FF"),
    "Cash Ratio": dict(
        what="Most conservative: only counts actual cash vs current liabilities. Immediate payment ability.",
        formula="Cash Ratio = Cash & Equivalents / Current Liabilities",
        good=">0.5 provides a safety cushion", bad="<0.2 leaves almost no immediate buffer", color="#E3B341"),
    "Debt/Equity": dict(
        what="How much the company borrows versus shareholder funds. High = more financial risk.",
        formula="D/E = Total Debt / Shareholders Equity",
        good="<1.0 conservative, <0.5 very safe", bad=">2.0 high risk; varies significantly by industry", color="#F85149"),
    "Debt/Assets": dict(
        what="Proportion of total assets funded by debt. Key measure of financial leverage.",
        formula="D/A = Total Debt / Total Assets",
        good="<0.4 is conservative and safe", bad=">0.6 = majority of assets are debt-funded", color="#FFA657"),
    "Interest Coverage": dict(
        what="How many times the company can pay interest from operating income. Debt safety buffer.",
        formula="Interest Coverage = Operating Income / Interest Expense",
        good=">3x safe, >5x very comfortable", bad="<1.5x dangerous, risk of loan default", color="#3FB950"),
    "Asset Turnover": dict(
        what="How efficiently the company uses its assets to generate revenue. Revenue per rupee of assets.",
        formula="Asset Turnover = Revenue / Total Assets",
        good=">1.0 for most industries", bad="<0.3 suggests poor asset productivity", color="#58A6FF"),
    "Days Inventory": dict(
        what="Average days to sell inventory. Lower means faster inventory movement and less capital tied up.",
        formula="Days Inventory = (Inventory / COGS) × 365",
        good="<45 days for most sectors", bad=">120 days signals inventory pile-up", color="#D2A8FF"),
    "Days Sales Outstanding": dict(
        what="Average days to collect cash from customers. Lower is better — shows collection efficiency.",
        formula="DSO = (Accounts Receivable / Revenue) × 365",
        good="<30 days excellent, <60 acceptable", bad=">90 days means slow/risky receivables", color="#79C0FF"),
    "Cash Conversion Cycle": dict(
        what="Total days to turn inventory investment into cash collected. Full working capital cycle.",
        formula="CCC = Days Inventory + Days Sales Outstanding",
        good="Near zero or negative = super-efficient", bad=">90 days ties up too much working capital", color="#E3B341"),
    "DuPont ROE %": dict(
        what="ROE broken into 3 drivers showing exactly WHY ROE is high or low.",
        formula="ROE = Net Margin % × Asset Turnover × Equity Multiplier",
        good="High ROE from margins/efficiency is sustainable", bad="High ROE only from leverage is risky", color="#3FB950"),
    "Altman Z-Score": dict(
        what="Bankruptcy prediction model using 5 ratios. Predicts financial distress up to 2 years ahead.",
        formula="Z = 1.2(WC/TA) + 1.4(RE/TA) + 3.3(EBIT/TA) + 0.6(Equity/Liabilities) + Asset Turnover",
        good=">2.99 Safe Zone — low bankruptcy risk", bad="<1.81 Distress Zone — high bankruptcy risk", color="#58A6FF"),
}

GLOSSARY = {
    "P/E Ratio": ("Price to Earnings", "How much investors pay per ₹1 of annual earnings. A high P/E suggests growth expectations; a low P/E may indicate undervaluation or poor prospects.", "Stock Price / Earnings Per Share", ">20 growth stock; 10-20 fair value range", "Negative = company making losses"),
    "P/B Ratio": ("Price to Book", "How much premium investors pay over the net asset value of the company.", "Market Price per Share / Book Value per Share", "1-3 fair value for most companies", ">5 may be overvalued unless high-quality business"),
    "EV/EBITDA": ("Enterprise Value to EBITDA", "Compares total company value (including debt) to earnings power. Better than P/E for comparing companies with different capital structures.", "Enterprise Value / EBITDA", "<10 potentially undervalued", ">20 expensive, requires high growth to justify"),
    "DCF Value": ("Discounted Cash Flow Intrinsic Value", "Projects future free cash flows and discounts them to present value. Widely considered the most rigorous valuation method.", "Sum of PV(future FCFs) + PV(Terminal Value)", "Stock price below DCF = margin of safety", "Stock price far above DCF = potentially overvalued"),
    "Graham Number": ("Benjamin Graham's Intrinsic Value", "Conservative valuation formula by Warren Buffett's mentor. The maximum price a defensive investor should pay.", "Square Root of (22.5 × EPS × Book Value per Share)", "Stock price below Graham Number = buy zone", "Stock far above Graham Number = overvalued"),
    "Piotroski F-Score": ("Financial Strength 0-9", "9-signal system scoring profitability, leverage trends, and efficiency. Each signal scores 1 if condition is met.", "Sum of 9 binary signals across 3 categories", "7-9 Strong financial health", "0-3 Weak, potentially deteriorating"),
    "Beta": ("Market Sensitivity", "How much the stock moves relative to the Nifty 50 index.", "Cov(stock returns, market returns) / Var(market returns)", "0.8-1.2 moves roughly with market", ">1.5 highly volatile, <0 inversely correlated"),
}

# ══════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════
INDIAN_COMPANIES = {
    "── NIFTY 50 ──": None,
    "Reliance Industries": "RELIANCE.NS", "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS", "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS", "Hindustan Unilever": "HINDUNILVR.NS",
    "ITC": "ITC.NS", "Bajaj Finance": "BAJFINANCE.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS", "Larsen & Toubro": "LT.NS",
    "Axis Bank": "AXISBANK.NS", "Asian Paints": "ASIANPAINT.NS",
    "Maruti Suzuki": "MARUTI.NS", "Sun Pharma": "SUNPHARMA.NS",
    "Wipro": "WIPRO.NS", "HCL Technologies": "HCLTECH.NS",
    "Titan Company": "TITAN.NS", "Tata Motors": "TATAMOTORS.NS",
    "Tata Steel": "TATASTEEL.NS", "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS", "JSW Steel": "JSWSTEEL.NS",
    "Bajaj Auto": "BAJAJ-AUTO.NS", "Nestle India": "NESTLEIND.NS",
    "Tech Mahindra": "TECHM.NS", "UltraTech Cement": "ULTRACEMCO.NS",
    "Adani Ports": "ADANIPORTS.NS",
    "── MID CAP ──": None,
    "Zomato": "ZOMATO.NS", "Nykaa": "NYKAA.NS",
    "Tata Elxsi": "TATAELXSI.NS", "Persistent Systems": "PERSISTENT.NS",
    "Mphasis": "MPHASIS.NS", "Godrej Consumer": "GODREJCP.NS",
    "Dabur India": "DABUR.NS", "Marico": "MARICO.NS",
    "Havells India": "HAVELLS.NS", "Pidilite Industries": "PIDILITIND.NS",
    "── BANKING ──": None,
    "State Bank of India": "SBIN.NS", "Bank of Baroda": "BANKBARODA.NS",
    "Punjab National Bank": "PNB.NS", "Canara Bank": "CANBK.NS",
    "HDFC Life Insurance": "HDFCLIFE.NS",
    "── PHARMA ──": None,
    "Dr Reddys Lab": "DRREDDY.NS", "Cipla": "CIPLA.NS",
    "Lupin": "LUPIN.NS", "Apollo Hospitals": "APOLLOHOSP.NS",
    "── ENERGY ──": None,
    "Adani Green Energy": "ADANIGREEN.NS", "Coal India": "COALINDIA.NS",
    "Indian Oil Corp": "IOC.NS", "BPCL": "BPCL.NS",
}

PEER_GROUPS = {
    "IT Giants":     ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Private Banks": ["HDFCBANK.NS","ICICIBANK.NS","KOTAKBANK.NS","AXISBANK.NS"],
    "PSU Banks":     ["SBIN.NS","BANKBARODA.NS","PNB.NS","CANBK.NS"],
    "FMCG":         ["HINDUNILVR.NS","ITC.NS","DABUR.NS","MARICO.NS"],
    "Pharma":        ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","LUPIN.NS"],
    "Auto":          ["MARUTI.NS","TATAMOTORS.NS","BAJAJ-AUTO.NS"],
}

C = ["#58A6FF","#3FB950","#E3B341","#F85149","#D2A8FF","#79C0FF","#FFA657","#A5D6FF"]

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def sv(df, col, *keys):
    for key in keys:
        for idx in df.index:
            if key.lower() in str(idx).lower():
                try:
                    v = df.loc[idx, col]
                    if not pd.isna(v): return float(v)
                except: pass
    return np.nan

def sd(a, b):
    if pd.isna(a) or pd.isna(b) or b == 0: return np.nan
    return a / b

def f(v, d=2):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "—"
    return f"{v:,.{d}f}"

def cc(title="", h=300):
    return dict(
        title=dict(text=title, font=dict(size=13, color="#C9D1D9", family="Sora"), x=0.01),
        height=h, margin=dict(l=8,r=8,t=40,b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0D1117",
        font=dict(family="Inter", size=11, color="#8B949E"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#21262D", linecolor="#21262D", tickfont=dict(color="#8B949E")),
        yaxis=dict(gridcolor="#21262D", linecolor="#21262D", tickfont=dict(color="#8B949E")),
    )

def ex(key):
    if key not in EXPLAIN: return ""
    e = EXPLAIN[key]
    return f"""<div class="explain" style="--ac:{e['color']}">
      <b>{key}</b> — {e['what']}<br>
      <span class="formula">{e['formula']}</span>
      <span class="g">Good: {e['good']}</span> &nbsp;|&nbsp;
      <span class="r">Watch: {e['bad']}</span>
    </div>"""

# ══════════════════════════════════════════════════════════════
# ANALYSIS ENGINE
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def analyse(ticker):
    stock = yf.Ticker(ticker)
    info  = stock.info
    IS, BS, CF = stock.financials, stock.balance_sheet, stock.cashflow
    name  = info.get("longName", ticker)
    if IS.empty: raise ValueError(f"No data found for {ticker}")

    rows = []
    for col in IS.columns:
        yr = str(col)[:4]
        g  = lambda df2, *k: sv(df2, col, *k)
        rev    = g(IS,"Total Revenue","Revenue")
        gp     = g(IS,"Gross Profit")
        oi     = g(IS,"Operating Income","Ebit")
        ni     = g(IS,"Net Income")
        ebitda = g(IS,"EBITDA","Ebitda")
        iexp   = g(IS,"Interest Expense")
        cogs   = g(IS,"Cost Of Revenue")
        ta     = g(BS,"Total Assets")
        tl     = g(BS,"Total Liabilities")
        eq     = g(BS,"Stockholders Equity","Common Stock Equity","Total Stockholder Equity")
        ca     = g(BS,"Current Assets","Total Current Assets")
        cl     = g(BS,"Current Liabilities","Total Current Liabilities")
        cash   = g(BS,"Cash And Cash Equivalents","Cash")
        inv    = g(BS,"Inventory")
        rec    = g(BS,"Net Receivables","Accounts Receivable")
        tdt    = g(BS,"Total Debt")
        re     = g(BS,"Retained Earnings")
        wc     = ca-cl if not (np.isnan(ca) or np.isnan(cl)) else np.nan
        cfo    = g(CF,"Operating Cash Flow","Total Cash From Operating")
        capex  = g(CF,"Capital Expenditures","Capital Expenditure")
        fcf    = cfo+capex if not (np.isnan(cfo) or np.isnan(capex)) else np.nan
        nm=sd(ni,rev); at=sd(rev,ta); eqm=sd(ta,eq)
        x1=sd(wc,ta); x2=sd(re,ta); x3=sd(oi,ta)
        x4=sd(eq,tl) if not np.isnan(tl) else np.nan
        z = 1.2*x1+1.4*x2+3.3*x3+0.6*x4+at if all(not np.isnan(v) for v in [x1,x2,x3,x4,at]) else np.nan
        rows.append({"Year":yr,
            "Revenue (Cr)":    rev/1e7 if not np.isnan(rev) else np.nan,
            "Net Income (Cr)": ni/1e7  if not np.isnan(ni)  else np.nan,
            "FCF (Cr)":        fcf/1e7 if not np.isnan(fcf) else np.nan,
            "Gross Margin %":      sd(gp,rev)*100,
            "Operating Margin %":  sd(oi,rev)*100,
            "Net Margin %":        sd(ni,rev)*100,
            "EBITDA Margin %":     sd(ebitda,rev)*100,
            "FCF Margin %":        sd(fcf,rev)*100,
            "ROA %":               sd(ni,ta)*100,
            "ROE %":               sd(ni,eq)*100,
            "Asset Turnover":      at,
            "Equity Multiplier":   eqm,
            "DuPont ROE %":        nm*at*eqm*100 if all(not np.isnan(v) for v in [nm,at,eqm]) else np.nan,
            "Current Ratio":       sd(ca,cl),
            "Quick Ratio":         sd((ca-inv) if not np.isnan(inv) else ca, cl),
            "Cash Ratio":          sd(cash,cl),
            "Debt/Equity":         sd(tdt,eq),
            "Debt/Assets":         sd(tdt,ta),
            "Interest Coverage":   sd(oi,abs(iexp)) if not np.isnan(iexp) else np.nan,
            "Inventory Turnover":  sd(cogs,inv),
            "Receivables Turnover":sd(rev,rec),
            "Days Inventory":      sd(365,sd(cogs,inv)),
            "Days Sales Outstanding": sd(365,sd(rev,rec)),
            "Cash Conversion Cycle":  (sd(365,sd(cogs,inv))+sd(365,sd(rev,rec)))
                                       if not np.isnan(sd(cogs,inv)) and not np.isnan(sd(rev,rec)) else np.nan,
            "Altman Z-Score": z,
        })

    df = pd.DataFrame(rows).set_index("Year")
    mkt = {k:info.get(v) for k,v in {
        "PE":"trailingPE","PB":"priceToBook","PS":"priceToSalesTrailing12Months",
        "EVEBITDA":"enterpriseToEbitda","Price":"currentPrice","MarketCap":"marketCap",
        "Sector":"sector","Industry":"industry","EPS":"trailingEps","BVPS":"bookValue",
        "52wHigh":"fiftyTwoWeekHigh","52wLow":"fiftyTwoWeekLow",
        "DivYield":"dividendYield","Beta":"beta",
    }.items()}
    mkt["Sector"]   = mkt["Sector"]   or "—"
    mkt["Industry"] = mkt["Industry"] or "—"

    dcf_val = None
    try:
        bf = df["FCF (Cr)"].dropna().iloc[0]*1e7
        sh = info.get("sharesOutstanding",1)
        pv = sum(bf*(1.1)**i/(1.1)**i for i in range(1,6))
        tv = bf*(1.1)**5*1.03/0.07; pv_tv = tv/(1.1)**5
        dcf_val = (pv+pv_tv)/sh
    except: pass

    graham = None
    try:
        e2,b2 = mkt["EPS"],mkt["BVPS"]
        if e2 and b2 and e2>0 and b2>0: graham = np.sqrt(22.5*e2*b2)
    except: pass

    pf = None
    try:
        r0,r1 = df.iloc[0],df.iloc[1]
        sc = {
            "ROA positive":       int(r0["ROA %"]>0),
            "FCF positive":       int(r0["FCF (Cr)"]>0),
            "ROA improving":      int(r0["ROA %"]>r1["ROA %"]),
            "Lower leverage":     int(r0["Debt/Assets"]<r1["Debt/Assets"]),
            "Better liquidity":   int(r0["Current Ratio"]>r1["Current Ratio"]),
            "Higher gross margin":int(r0["Gross Margin %"]>r1["Gross Margin %"]),
            "Better asset use":   int(r0["Asset Turnover"]>r1["Asset Turnover"]),
            "FCF > Net Income":   int(r0["FCF (Cr)"]>r0["Net Income (Cr)"]),
            "Positive FCF margin":int(r0["FCF Margin %"]>0),
        }
        pf = (sum(sc.values()), sc)
    except: pass

    return name, df, mkt, dcf_val, graham, pf

@st.cache_data(ttl=3600, show_spinner=False)
def load_peers(tickers):
    results = {}
    for t in tickers:
        try:
            _,df2,mkt2,_,_,_ = analyse(t)
            row = df2.iloc[0].to_dict()
            row.update({"Ticker":t,"PE":mkt2.get("PE"),"PB":mkt2.get("PB")})
            results[t] = row
        except: pass
    return pd.DataFrame(results).T if results else pd.DataFrame()

# ══════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════
def bar_line(df2, bars, line_k, title, h=300):
    yrs2 = list(df2.index)
    fig = make_subplots(specs=[[{"secondary_y": bool(line_k)}]])
    for i,k in enumerate(bars):
        if k in df2.columns:
            fig.add_trace(go.Bar(x=yrs2, y=df2[k], name=k,
                marker_color=C[i%len(C)], opacity=0.85, marker_line_width=0), secondary_y=False)
    if line_k and line_k in df2.columns:
        fig.add_trace(go.Scatter(x=yrs2, y=df2[line_k], name=line_k, mode="lines+markers",
            line=dict(color="#E3B341",width=2.5), marker=dict(size=7,color="#E3B341")), secondary_y=True)
        fig.update_yaxes(showgrid=False, tickfont=dict(color="#E3B341"), secondary_y=True)
    fig.update_layout(**cc(title,h), barmode="group")
    return fig

def lines(df2, keys, title, h=280):
    yrs2 = list(df2.index)
    fig = go.Figure()
    for i,k in enumerate(keys):
        if k in df2.columns:
            fig.add_trace(go.Scatter(x=yrs2, y=df2[k], name=k, mode="lines+markers",
                line=dict(color=C[i%len(C)],width=2.5),
                marker=dict(size=8,color=C[i%len(C)],line=dict(color="#0D1117",width=2))))
    fig.update_layout(**cc(title,h))
    return fig

def fcf_bars(df2, h=280):
    yrs2 = list(df2.index)
    vals = df2["FCF (Cr)"].fillna(0).values
    cols2 = ["#3FB950" if v>=0 else "#F85149" for v in vals]
    fig = go.Figure(go.Bar(x=yrs2, y=vals, marker_color=cols2, marker_line_width=0, name="FCF"))
    fig.add_hline(y=0, line_color="#30363D", line_width=1)
    fig.update_layout(**cc("Free Cash Flow (Rs Crore)",h))
    return fig

def gauge(z_val2, h=250):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=z_val2 if not np.isnan(z_val2) else 0,
        number={"font":{"size":34,"color":"#E6EDF3","family":"Sora"}},
        title={"text":"Altman Z-Score","font":{"size":12,"color":"#8B949E"}},
        gauge={"axis":{"range":[0,5],"tickcolor":"#30363D","tickfont":{"color":"#6E7681"}},
               "bar":{"color":"#58A6FF","thickness":0.22},
               "bgcolor":"#161B22","bordercolor":"#21262D",
               "steps":[{"range":[0,1.81],"color":"rgba(248,81,73,0.15)"},
                         {"range":[1.81,2.99],"color":"rgba(227,179,65,0.12)"},
                         {"range":[2.99,5],"color":"rgba(63,185,80,0.12)"}]}
    ))
    fig.update_layout(height=h, margin=dict(l=20,r=20,t=30,b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def radar(df2, h=300):
    keys = ["Gross Margin %","Net Margin %","ROE %","Current Ratio","Asset Turnover","FCF Margin %"]
    vals = [min(float(df2.iloc[0].get(k,0) or 0),60) for k in keys]
    fig = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=keys+[keys[0]], fill="toself",
        fillcolor="rgba(88,166,255,0.12)",
        line=dict(color="#58A6FF",width=2.5),
        marker=dict(size=6,color="#58A6FF",line=dict(color="#0D1117",width=1.5))
    ))
    fig.update_layout(
        polar=dict(bgcolor="#0D1117",
            radialaxis=dict(visible=True,range=[0,60],gridcolor="#21262D",tickfont=dict(color="#6E7681",size=9)),
            angularaxis=dict(gridcolor="#21262D",tickfont=dict(color="#8B949E",size=10))),
        showlegend=False, height=h, margin=dict(l=40,r=40,t=20,b=20),
        paper_bgcolor="rgba(0,0,0,0)")
    return fig

def peer_radar_chart(peer_df2, keys, h=380):
    fig = go.Figure()
    for i,(t2,row) in enumerate(peer_df2[keys].iterrows()):
        vals = [min(float(v) if not pd.isna(v) else 0,60) for v in row]
        fig.add_trace(go.Scatterpolar(r=vals+[vals[0]], theta=keys+[keys[0]],
            fill="toself", opacity=0.5, name=t2,
            line=dict(color=C[i%len(C)],width=2)))
    fig.update_layout(
        polar=dict(bgcolor="#0D1117",
            radialaxis=dict(visible=True,range=[0,60],gridcolor="#21262D",tickfont=dict(color="#6E7681",size=9)),
            angularaxis=dict(gridcolor="#21262D",tickfont=dict(color="#8B949E"))),
        height=h, showlegend=True, paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#C9D1D9",size=11)),
        margin=dict(l=40,r=40,t=20,b=20))
    return fig

# ══════════════════════════════════════════════════════════════
# PDF
# ══════════════════════════════════════════════════════════════
def make_pdf(name2, ticker2, df2, mkt2, dcf2, gr2, pf2):
    pdf = FPDF(); pdf.set_auto_page_break(True,15); pdf.add_page()
    def c2(s): return str(s).encode("latin-1","replace").decode("latin-1")
    pdf.set_fill_color(13,17,23); pdf.rect(0,0,210,28,"F")
    pdf.set_text_color(230,237,243); pdf.set_font("Helvetica","B",18)
    pdf.cell(0,14,"FinSight Pro",ln=True,align="C")
    pdf.set_font("Helvetica","",10)
    pdf.cell(0,10,c2(f"Financial Report  {name2} ({ticker2})"),ln=True,align="C")
    pdf.set_text_color(40,40,40); pdf.ln(4)
    pdf.set_font("Helvetica","I",8)
    pdf.cell(0,5,f"Generated: {datetime.now().strftime('%d %B %Y')}  |  NSE Data via Yahoo Finance",ln=True)
    pdf.ln(3)
    def sec(t3):
        pdf.set_font("Helvetica","B",10); pdf.set_fill_color(22,27,34)
        pdf.set_text_color(88,166,255); pdf.cell(0,7,c2(f"  {t3}"),ln=True,fill=True)
        pdf.set_text_color(40,40,40); pdf.ln(1)
    def kv(l3,v3):
        pdf.set_font("Helvetica","",9)
        pdf.cell(75,6,c2(str(l3)[:42])); pdf.cell(0,6,c2(str(v3)),ln=True)
    sec("Market Snapshot")
    for l3,v3 in [("Price",f"Rs {mkt2['Price']:.2f}" if mkt2.get("Price") else "-"),
                  ("Market Cap",f"Rs {mkt2['MarketCap']/1e7:,.0f} Cr" if mkt2.get("MarketCap") else "-"),
                  ("P/E",f(mkt2.get("PE"))),("P/B",f(mkt2.get("PB"))),
                  ("52W High",f"Rs {mkt2['52wHigh']:.0f}" if mkt2.get("52wHigh") else "-"),
                  ("Sector",mkt2.get("Sector","-")),("Industry",mkt2.get("Industry","-"))]:
        kv(l3,v3)
    pdf.ln(3)
    cols3 = list(df2.index)
    groups = {
        "Financials (Rs Crore)":["Revenue (Cr)","Net Income (Cr)","FCF (Cr)"],
        "Profitability (%)":["Gross Margin %","Operating Margin %","Net Margin %","EBITDA Margin %","ROE %","ROA %"],
        "Liquidity":["Current Ratio","Quick Ratio","Cash Ratio"],
        "Leverage":["Debt/Equity","Debt/Assets","Interest Coverage"],
        "Efficiency":["Asset Turnover","Days Inventory","Days Sales Outstanding","Cash Conversion Cycle"],
        "Scores":["DuPont ROE %","Altman Z-Score"],
    }
    pdf.set_font("Helvetica","B",9)
    pdf.cell(75,7,"Metric")
    for c3 in cols3[:4]: pdf.cell(28,7,c2(str(c3)),align="C")
    pdf.ln()
    for grp,metrics in groups.items():
        sec(grp)
        for m in metrics:
            if m not in df2.columns: continue
            pdf.set_font("Helvetica","",9); pdf.cell(75,6,c2(m[:42]))
            for c3 in cols3[:4]:
                v3 = df2.loc[c3,m] if c3 in df2.index else np.nan
                pdf.cell(28,6,c2(f(v3)),align="C")
            pdf.ln()
        pdf.ln(2)
    sec("Valuation")
    kv("DCF Intrinsic Value",f"Rs {dcf2:.2f}" if dcf2 else "-")
    kv("Graham Number",f"Rs {gr2:.2f}" if gr2 else "-")
    if mkt2.get("Price") and dcf2:
        kv("Upside vs DCF",f"{(dcf2-mkt2['Price'])/mkt2['Price']*100:+.1f}%")
    if pf2:
        score2,details2 = pf2
        sec(f"Piotroski F-Score: {score2}/9")
        for k3,v3 in details2.items(): kv(k3,"PASS" if v3 else "FAIL")
    buf = io.BytesIO(); pdf.output(buf); return buf.getvalue()

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="sb-title"><span class="live-dot"></span>FinSight Pro</div>
      <div style="color:#6E7681;font-size:11px;margin-top:3px">Indian Equity Analysis</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<span class="sb-label">Select Company</span>', unsafe_allow_html=True)
    valid = {k:v for k,v in INDIAN_COMPANIES.items() if v}
    labels = [k for k,v in INDIAN_COMPANIES.items() if v]
    sel_lbl = st.selectbox("co", labels, label_visibility="collapsed")
    sel_t   = valid[sel_lbl]

    st.markdown('<span class="sb-label">Custom NSE Ticker</span>', unsafe_allow_html=True)
    custom = st.text_input("ct", placeholder="e.g. DMART.NS", label_visibility="collapsed")
    if custom.strip():
        t2 = custom.strip().upper()
        sel_t = t2 if t2.endswith(".NS") else t2+".NS"

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    run_btn  = st.button("Run Analysis", use_container_width=True)

    st.markdown("<hr style='border-color:#21262D;margin:14px 0'>", unsafe_allow_html=True)
    st.markdown('<span class="sb-label">Peer Comparison</span>', unsafe_allow_html=True)
    pg = st.selectbox("pg", ["None"]+list(PEER_GROUPS.keys()), label_visibility="collapsed")
    peer_btn = st.button("Compare Peers", use_container_width=True)

    st.markdown("<hr style='border-color:#21262D;margin:14px 0'>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:11px;color:#6E7681;line-height:2">
    Data: Yahoo Finance (NSE)<br>Cache: 1 hour<br>
    Values in Rs Crore<br>Up to 4 years history</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "results" not in st.session_state: st.session_state.results = None
if "peers"   not in st.session_state: st.session_state.peers   = None

if run_btn:
    with st.spinner(f"Loading {sel_t}..."):
        try:
            name2,df2,mkt2,dcf2,gr2,pf2 = analyse(sel_t)
            st.session_state.results = (name2,sel_t,df2,mkt2,dcf2,gr2,pf2)
            st.session_state.peers   = None
        except Exception as err:
            st.error(f"Error: {err}")
            st.session_state.results = None

if peer_btn and pg != "None":
    with st.spinner(f"Loading {pg}..."):
        pdf3 = load_peers(PEER_GROUPS[pg])
        st.session_state.peers   = (pg, pdf3)
        st.session_state.results = None

# ══════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════
if st.session_state.results:
    name2,ticker2,df2,mkt2,dcf2,gr2,pf2 = st.session_state.results
    yrs2  = list(df2.index)
    price2 = mkt2.get("Price"); mktcap2 = mkt2.get("MarketCap")
    z2     = df2["Altman Z-Score"].iloc[0] if "Altman Z-Score" in df2.columns else np.nan
    zc     = "#3FB950" if (not np.isnan(z2) and z2>2.99) else ("#E3B341" if (not np.isnan(z2) and z2>1.81) else "#F85149")
    zl     = "Safe Zone" if (not np.isnan(z2) and z2>2.99) else ("Grey Zone" if (not np.isnan(z2) and z2>1.81) else "Distress Zone")

    # Hero
    h52=mkt2.get("52wHigh"); l52=mkt2.get("52wLow")
    price_badge = ""
    if price2 and h52:
        pct = (price2-h52)/h52*100
        cls = "up" if pct>-5 else "down"
        price_badge = f'<span class="badge {cls}">{pct:+.1f}% from 52W High</span>'

    st.markdown(f"""
    <div class="hero">
      <div class="hero-name">{name2}<span class="hero-ticker">{ticker2}</span></div>
      <div class="hero-badges">
        <span class="badge">{mkt2.get('Sector','—')}</span>
        <span class="badge">{mkt2.get('Industry','—')}</span>
        {price_badge}
        <span class="badge">52W: Rs{f(l52,0)} – Rs{f(h52,0)}</span>
        <span class="badge">Beta: {f(mkt2.get('Beta'))}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # KPI strip
    dy = f"{mkt2['DivYield']*100:.2f}%" if mkt2.get("DivYield") else "—"
    mc = f"Rs{f(mktcap2/1e7,0)} Cr" if mktcap2 else "—"
    st.markdown(f"""
    <div class="kpi-strip">
      <div class="kpi-box" style="--ac:#58A6FF">
        <div class="kpi-label">CMP</div>
        <div class="kpi-value">Rs{f(price2,0)}</div>
        <div class="kpi-sub">Current Price</div>
      </div>
      <div class="kpi-box" style="--ac:#3FB950">
        <div class="kpi-label">Market Cap</div>
        <div class="kpi-value">{mc}</div>
        <div class="kpi-sub">Total company value</div>
      </div>
      <div class="kpi-box" style="--ac:#E3B341">
        <div class="kpi-label">P/E Ratio</div>
        <div class="kpi-value">{f(mkt2.get('PE'))}</div>
        <div class="kpi-sub">Price per Rs1 earnings</div>
      </div>
      <div class="kpi-box" style="--ac:#D2A8FF">
        <div class="kpi-label">P/B Ratio</div>
        <div class="kpi-value">{f(mkt2.get('PB'))}</div>
        <div class="kpi-sub">Price vs book value</div>
      </div>
      <div class="kpi-box" style="--ac:#FFA657">
        <div class="kpi-label">Div Yield</div>
        <div class="kpi-value">{dy}</div>
        <div class="kpi-sub">Annual dividend %</div>
      </div>
      <div class="kpi-box" style="--ac:{zc}">
        <div class="kpi-label">Altman Z</div>
        <div class="kpi-value" style="color:{zc}">{f(z2)}</div>
        <div class="kpi-sub" style="color:{zc}">{zl}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Tabs
    tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
        "Financials","Charts","All Ratios","Scoring","Valuation","Learn","Export"
    ])

    # ── TAB 1 FINANCIALS
    with tab1:
        c1,c2 = st.columns([3,2])
        with c1:
            st.plotly_chart(bar_line(df2,["Revenue (Cr)","Net Income (Cr)"],"Net Margin %",
                "Revenue & Net Income (Rs Crore)",h=300), use_container_width=True, key="t1_rev")
        with c2:
            st.plotly_chart(fcf_bars(df2,h=300), use_container_width=True, key="t1_fcf")

        st.markdown(ex("Revenue (Cr)")+ex("Net Income (Cr)")+ex("FCF (Cr)"), unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        hdr2 = "<tr><th>Metric</th>"+"".join(f"<th>{y}</th>" for y in yrs2)+"</tr>"
        fin_keys2 = ["Revenue (Cr)","Net Income (Cr)","FCF (Cr)","Gross Margin %","Net Margin %","EBITDA Margin %","ROE %","ROA %"]
        rows2 = "".join(f"<tr><td>{k}</td>"+"".join(f"<td>{f(df2.loc[y,k])}</td>" for y in yrs2)+"</tr>"
                        for k in fin_keys2 if k in df2.columns)
        st.markdown(f'<div class="card"><div class="tw"><table class="rt"><thead>{hdr2}</thead><tbody>{rows2}</tbody></table></div></div>', unsafe_allow_html=True)

    # ── TAB 2 CHARTS
    with tab2:
        a1,a2 = st.columns(2)
        with a1:
            st.plotly_chart(bar_line(df2,["Gross Margin %","Operating Margin %","Net Margin %"],"","Profitability Margins (%)",h=280), use_container_width=True, key="t2_m")
        with a2:
            st.plotly_chart(lines(df2,["ROA %","ROE %"],"Return Ratios (%)",h=280), use_container_width=True, key="t2_r")

        b1,b2 = st.columns(2)
        with b1:
            fig_liq = go.Figure()
            for i2,k2 in enumerate(["Current Ratio","Quick Ratio","Cash Ratio"]):
                if k2 in df2.columns:
                    fig_liq.add_trace(go.Bar(x=yrs2,y=df2[k2],name=k2,marker_color=C[i2],opacity=0.85,marker_line_width=0))
            fig_liq.add_hline(y=1,line_color="#F85149",line_dash="dot",line_width=1.5,
                              annotation_text="Min=1",annotation_font_color="#F85149")
            fig_liq.update_layout(**cc("Liquidity Ratios",280),barmode="group")
            st.plotly_chart(fig_liq, use_container_width=True, key="t2_liq")
        with b2:
            st.plotly_chart(bar_line(df2,["Debt/Equity","Debt/Assets"],"Interest Coverage","Leverage",h=280), use_container_width=True, key="t2_lev")

        d1,d2 = st.columns(2)
        with d1:
            st.plotly_chart(bar_line(df2,["Days Inventory","Days Sales Outstanding"],"","Working Capital Days",h=280), use_container_width=True, key="t2_wc")
        with d2:
            st.plotly_chart(bar_line(df2,["Net Margin %","Asset Turnover","Equity Multiplier"],"","DuPont Decomposition",h=280), use_container_width=True, key="t2_dp")

        e1,e2 = st.columns(2)
        with e1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(radar(df2,h=290), use_container_width=True, key="t2_radar")
            st.markdown('</div>', unsafe_allow_html=True)
        with e2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(gauge(z2,h=240), use_container_width=True, key="t2_gauge")
            st.markdown(f'<div style="text-align:center;margin-top:-4px"><span style="color:{zc};font-weight:700;font-size:13px">{zl}</span><br><span style="color:#6E7681;font-size:11px">&gt;2.99 Safe | 1.81-2.99 Grey | &lt;1.81 Distress</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 3 ALL RATIOS
    with tab3:
        ratio_grps = [
            ("Profitability", "#3FB950",
             ["Gross Margin %","Operating Margin %","Net Margin %","EBITDA Margin %","FCF Margin %","ROA %","ROE %"],
             ["Gross Margin %","Net Margin %","ROE %"]),
            ("Liquidity", "#58A6FF",
             ["Current Ratio","Quick Ratio","Cash Ratio"],
             ["Current Ratio","Quick Ratio"]),
            ("Leverage & Solvency", "#F85149",
             ["Debt/Equity","Debt/Assets","Interest Coverage"],
             ["Debt/Equity","Interest Coverage"]),
            ("Efficiency", "#E3B341",
             ["Asset Turnover","Inventory Turnover","Receivables Turnover","Days Inventory","Days Sales Outstanding","Cash Conversion Cycle"],
             ["Days Sales Outstanding","Cash Conversion Cycle"]),
            ("DuPont", "#D2A8FF",
             ["Net Margin %","Asset Turnover","Equity Multiplier","DuPont ROE %"],
             ["DuPont ROE %"]),
            ("Risk", "#79C0FF",
             ["Altman Z-Score"], ["Altman Z-Score"]),
        ]
        hdr3 = "<tr><th>Metric</th>"+"".join(f"<th>{y}</th>" for y in yrs2)+"</tr>"
        for grp_name2, grp_col2, keys2, explain_keys in ratio_grps:
            rows3 = f'<tr class="cat"><td colspan="{len(yrs2)+1}">{grp_name2}</td></tr>'
            rows3 += "".join(f"<tr><td>{k2}</td>"+"".join(f"<td>{f(df2.loc[y,k2])}</td>" for y in yrs2)+"</tr>"
                             for k2 in keys2 if k2 in df2.columns)
            st.markdown(f'<div class="card"><div class="tw"><table class="rt"><thead>{hdr3}</thead><tbody>{rows3}</tbody></table></div>', unsafe_allow_html=True)
            for ek in explain_keys:
                st.markdown(ex(ek), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 4 SCORING
    with tab4:
        s1,s2 = st.columns(2)
        with s1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(gauge(z2,h=240), use_container_width=True, key="t4_gauge")
            z_msgs = {
                "#3FB950": ("Safe Zone — Z > 2.99", "Low bankruptcy risk. Company has strong financial foundations and can comfortably service its debts. Generally a good sign for long-term investors."),
                "#E3B341": ("Grey Zone — 1.81 to 2.99", "Moderate risk territory. Some financial stress present. Worth monitoring quarterly results and debt levels closely."),
                "#F85149": ("Distress Zone — Z < 1.81", "High bankruptcy risk. Serious financial stress. Company may struggle to meet debt obligations. Exercise extreme caution."),
            }
            lbl3,desc3 = z_msgs.get(zc,("—","—"))
            st.markdown(f'<div style="text-align:center;margin-bottom:8px"><b style="color:{zc};font-size:15px">{lbl3}</b></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="infobox">{desc3}</div>', unsafe_allow_html=True)
            st.markdown(ex("Altman Z-Score"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with s2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if pf2:
                score3,details3 = pf2
                rc = "#3FB950" if score3>=7 else ("#E3B341" if score3>=4 else "#F85149")
                rg = "rgba(63,185,80,0.4)" if score3>=7 else ("rgba(227,179,65,0.4)" if score3>=4 else "rgba(248,81,73,0.4)")
                rating3 = "Strong" if score3>=7 else ("Moderate" if score3>=4 else "Weak")
                pf_items = "".join(
                    f'<div class="pfi {"pass" if v3 else "fail"}">{"&#10003;" if v3 else "&#10007;"} {k3}</div>'
                    for k3,v3 in details3.items()
                )
                st.markdown(f"""
                <div class="ring-wrap">
                  <div class="ring" style="--rc:{rc};--rg:{rg}">
                    <div class="ring-num">{score3}</div>
                    <div class="ring-den">/9</div>
                  </div>
                  <div class="ring-lbl" style="color:{rc}">{rating3} Financial Health</div>
                </div>
                <div class="pf-grid">{pf_items}</div>""", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="infobox" style="margin-top:12px">
                <b>What is Piotroski F-Score?</b><br>
                A 9-point scoring system that rates the financial health trend of a company across 3 areas:<br><br>
                <b>Profitability (4 signals):</b> Is ROA positive? Is FCF positive? Is ROA improving year-over-year? Is FCF greater than net income (quality of earnings)?<br><br>
                <b>Leverage (3 signals):</b> Is debt falling? Is liquidity improving? Has the company avoided issuing new shares?<br><br>
                <b>Efficiency (2 signals):</b> Is gross margin improving? Is asset turnover improving?<br><br>
                <span class="g">7-9 = Strong — good buy signal</span><br>
                <span style="color:#E3B341">4-6 = Neutral — needs further investigation</span><br>
                <span class="r">0-3 = Weak — deteriorating financials, avoid or exit</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("Need 2+ years of data to compute Piotroski F-Score.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 5 VALUATION
    with tab5:
        v1,v2 = st.columns(2)
        with v1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title"><span class="dot" style="background:#58A6FF"></span>DCF Intrinsic Value</div>', unsafe_allow_html=True)
            if dcf2:
                up2 = (dcf2-price2)/price2*100 if price2 else None
                uc  = "#3FB950" if up2 and up2>0 else "#F85149"
                up_txt = f'<div class="vc-sub" style="color:{uc}">{up2:+.1f}% vs CMP</div>' if up2 else ""
                st.markdown(f"""
                <div class="val-row">
                  <div class="vc"><div class="vc-lbl">DCF Value</div><div class="vc-num">Rs{dcf2:,.0f}</div>{up_txt}</div>
                  <div class="vc"><div class="vc-lbl">CMP</div><div class="vc-num" style="color:#C9D1D9">Rs{f(price2,0)}</div><div class="vc-sub" style="color:#6E7681">Market Price</div></div>
                </div>""", unsafe_allow_html=True)
            else:
                st.warning("DCF unavailable — FCF data missing.")
            st.markdown("""
            <div class="infobox" style="margin-top:12px">
            <b>How DCF works:</b> The Discounted Cash Flow model projects the company's Free Cash Flow
            growing at 10% per year for 5 years. A terminal value is then calculated assuming 3% perpetual
            growth thereafter. All future cash flows are discounted back to today at a 10% rate (WACC),
            giving us the fair value per share today.<br><br>
            <b>Assumptions used:</b> 10% FCF growth rate | 10% discount rate (WACC) | 3% terminal growth
            </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with v2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title"><span class="dot" style="background:#D2A8FF"></span>Graham Number</div>', unsafe_allow_html=True)
            if gr2:
                gu2 = (gr2-price2)/price2*100 if price2 else None
                gc  = "#3FB950" if gu2 and gu2>0 else "#F85149"
                gu_txt = f'<div class="vc-sub" style="color:{gc}">{gu2:+.1f}% vs CMP</div>' if gu2 else ""
                st.markdown(f"""
                <div class="val-row">
                  <div class="vc"><div class="vc-lbl">Graham Number</div><div class="vc-num" style="color:#D2A8FF">Rs{gr2:,.0f}</div>{gu_txt}</div>
                  <div class="vc"><div class="vc-lbl">EPS</div><div class="vc-num" style="color:#C9D1D9">Rs{f(mkt2.get('EPS'))}</div><div class="vc-sub" style="color:#6E7681">BVPS: Rs{f(mkt2.get('BVPS'))}</div></div>
                </div>""", unsafe_allow_html=True)
            else:
                st.warning("Graham Number unavailable — EPS or BVPS missing.")
            st.markdown("""
            <div class="infobox" style="margin-top:12px">
            <b>Graham Number</b> is a conservative stock valuation formula created by Benjamin Graham,
            the father of value investing and mentor to Warren Buffett. It calculates the maximum fair
            price a defensive investor should pay for a stock.<br><br>
            <span class="formula" style="display:inline">Graham Number = Square Root of (22.5 x EPS x Book Value per Share)</span><br><br>
            If CMP is <b style="color:#3FB950">below</b> Graham Number: stock may be undervalued — potential buy signal.<br>
            If CMP is <b style="color:#F85149">far above</b> Graham Number: stock may be overvalued — exercise caution.
            </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card" style="margin-top:4px">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title"><span class="dot" style="background:#E3B341"></span>Market Multiples Explained</div>', unsafe_allow_html=True)
        mc1,mc2,mc3,mc4 = st.columns(4)
        for col4,label4,key4,tip4 in [
            (mc1,"P/E Ratio","PE","How much you pay for Rs1 of profit. Industry-relative benchmark."),
            (mc2,"P/B Ratio","PB","Price paid over book value. Premium reflects brand/moat."),
            (mc3,"EV/EBITDA","EVEBITDA","Total company value vs earnings. Best cross-company measure."),
            (mc4,"P/S Ratio","PS","Price relative to revenue. Useful for loss-making growth companies."),
        ]:
            with col4:
                st.metric(label4, f(mkt2.get(key4)))
                st.markdown(f'<div style="font-size:10px;color:#6E7681;margin-top:-8px;line-height:1.5">{tip4}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 6 LEARN
    with tab6:
        st.markdown('<div style="font-family:Sora;font-size:20px;font-weight:700;color:#E6EDF3;margin-bottom:6px">Financial Terms Explained</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#8B949E;font-size:13px;margin-bottom:20px;line-height:1.7">Every metric in this app explained in plain English — with formulas, benchmarks, and red flags to watch for.</div>', unsafe_allow_html=True)

        for key4, info4 in EXPLAIN.items():
            st.markdown(f"""
            <div class="card" style="margin-bottom:10px">
              <div style="font-family:Sora;font-size:14px;font-weight:700;color:#E6EDF3;margin-bottom:8px">
                <span style="color:{info4['color']};margin-right:8px">&#9632;</span>{key4}
              </div>
              <div style="color:#C9D1D9;font-size:13px;line-height:1.7;margin-bottom:8px">{info4['what']}</div>
              <span class="formula">{info4['formula']}</span>
              <div style="display:flex;gap:16px;font-size:12px;margin-top:8px;flex-wrap:wrap">
                <span style="color:#3FB950"><b>Good: </b>{info4['good']}</span>
                <span style="color:#F85149"><b>Watch: </b>{info4['bad']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:Sora;font-size:16px;font-weight:700;color:#E6EDF3;margin:16px 0 12px">Valuation and Scoring Models</div>', unsafe_allow_html=True)

        for key4,(fname,fdesc,fform,fg,fb) in GLOSSARY.items():
            st.markdown(f"""
            <div class="card" style="margin-bottom:10px">
              <div style="font-family:Sora;font-size:14px;font-weight:700;color:#E6EDF3;margin-bottom:6px">
                <span style="color:#58A6FF;margin-right:8px">&#9632;</span>{key4}
                <span style="font-size:11px;color:#8B949E;font-weight:400;margin-left:6px">{fname}</span>
              </div>
              <div style="color:#C9D1D9;font-size:13px;line-height:1.7;margin-bottom:6px">{fdesc}</div>
              <span class="formula">{fform}</span>
              <div style="display:flex;gap:16px;font-size:12px;margin-top:6px;flex-wrap:wrap">
                <span style="color:#3FB950"><b>Good: </b>{fg}</span>
                <span style="color:#F85149"><b>Watch: </b>{fb}</span>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 7 EXPORT
    with tab7:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title"><span class="dot" style="background:#3FB950"></span>Download Your Report</div>', unsafe_allow_html=True)
        dl1,dl2 = st.columns(2)
        with dl1:
            st.markdown("**PDF Report**")
            st.markdown('<div style="color:#8B949E;font-size:12px;margin-bottom:10px;line-height:1.6">Full analysis: ratios, valuation models, scoring, market snapshot, all years of data.</div>', unsafe_allow_html=True)
            pdf_bytes3 = make_pdf(name2,ticker2,df2,mkt2,dcf2,gr2,pf2)
            st.download_button("Download PDF", data=pdf_bytes3,
                file_name=f"FinSight_{ticker2}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf", use_container_width=True)
        with dl2:
            st.markdown("**CSV — All Ratios**")
            st.markdown('<div style="color:#8B949E;font-size:12px;margin-bottom:10px;line-height:1.6">All computed financial ratios across all available years in spreadsheet format.</div>', unsafe_allow_html=True)
            st.download_button("Download CSV", data=df2.to_csv().encode(),
                file_name=f"FinSight_{ticker2}_Ratios.csv",
                mime="text/csv", use_container_width=True)
        st.markdown("<hr style='border-color:#21262D;margin:16px 0'>", unsafe_allow_html=True)
        st.markdown("**Data Preview**")
        st.dataframe(df2.T.style.format("{:.2f}", na_rep="—"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PEER COMPARISON
# ══════════════════════════════════════════════════════════════
elif st.session_state.peers:
    group_name3, peer_df3 = st.session_state.peers
    st.markdown(f'<div style="font-family:Sora;font-size:22px;font-weight:800;color:#E6EDF3;margin-bottom:16px">Peer Comparison — {group_name3}</div>', unsafe_allow_html=True)
    if peer_df3.empty:
        st.error("Could not load peer data.")
    else:
        km = ["Gross Margin %","Net Margin %","ROE %","Current Ratio","Debt/Equity","Asset Turnover","Altman Z-Score"]
        disp3 = peer_df3[[c4 for c4 in km if c4 in peer_df3.columns]].apply(pd.to_numeric,errors="coerce")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Heatmap** — green = stronger, red = weaker within this peer group")
        st.dataframe(disp3.style.background_gradient(cmap="RdYlGn",axis=0).format("{:.2f}",na_rep="—"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        avail3 = [c4 for c4 in ["Gross Margin %","Net Margin %","ROE %","Current Ratio","Asset Turnover"] if c4 in disp3.columns]
        if avail3:
            st.markdown('<div class="card" style="margin-top:8px">', unsafe_allow_html=True)
            st.plotly_chart(peer_radar_chart(disp3,avail3,h=400), use_container_width=True, key="peer_r")
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# EMPTY STATE
# ══════════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div class="empty">
      <div class="empty-icon">📊</div>
      <div class="empty-title">Select a company to begin</div>
      <div class="empty-sub">
        Open the sidebar, pick from 50+ Indian companies<br>
        or type any NSE ticker (e.g. DMART.NS)<br><br>
        Get profitability · liquidity · solvency · DuPont<br>
        Altman Z-Score · Piotroski F-Score · DCF valuation<br>
        — every metric explained in plain English
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">FinSight Pro &nbsp;·&nbsp; Indian Market Edition &nbsp;·&nbsp; Data: Yahoo Finance (NSE) &nbsp;·&nbsp; AI & Fintech Class</div>', unsafe_allow_html=True)
