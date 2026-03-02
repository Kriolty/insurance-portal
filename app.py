import streamlit as st
import random
import string
import time
import os
import json
import tomllib
from datetime import date, datetime, timedelta
from pathlib import Path
import io

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fire & General Insurance Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# FEATURE FLAGS
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def load_features():
    p = Path(__file__).parent / "features.toml"
    if p.exists():
        with open(p, "rb") as f:
            data = tomllib.load(f)
        return data.get("features", {})
    return {}

F = load_features()

def feat(name: str) -> bool:
    return bool(F.get(name, False))

# ─────────────────────────────────────────────────────────────
# OPTIONAL IMPORTS (only load when feature is enabled)
# ─────────────────────────────────────────────────────────────
if feat("pdf_quote"):
    try:
        from fpdf import FPDF
        PDF_OK = True
    except ImportError:
        PDF_OK = False
else:
    PDF_OK = False

if feat("risk_radar_chart") or feat("postcode_heatmap") or feat("admin_dashboard"):
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
else:
    import pandas as pd

if feat("ai_damage_detection") or feat("natural_language"):
    try:
        from openai import OpenAI
        import base64
        AI_OK = True
    except ImportError:
        AI_OK = False
else:
    AI_OK = False

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2b55 0%, #1a4a8a 100%);
        border-right: 1px solid #1e3a6e;
    }
    [data-testid="stSidebar"] * { color: #e8f0fe !important; }
    [data-testid="stSidebar"] hr { border-color: #2d5a9e !important; }

    .main-header {
        background: linear-gradient(135deg, #0d2b55 0%, #1a4a8a 50%, #2563eb 100%);
        color: white; padding: 2rem 2.5rem; border-radius: 12px;
        margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(13,43,85,0.35);
    }
    .main-header h1 { margin:0; font-size:2.1rem; font-weight:700; letter-spacing:-0.5px; }
    .main-header p  { margin:0.4rem 0 0; font-size:1rem; opacity:0.88; }

    .section-header {
        background:#f0f4ff; border-left:4px solid #2563eb;
        padding:0.6rem 1rem; border-radius:0 6px 6px 0;
        margin:1.5rem 0 1rem; font-weight:600; font-size:0.95rem; color:#0d2b55;
    }
    .feature-flag-badge {
        background:#e0f2fe; color:#0369a1; border:1px solid #7dd3fc;
        padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:600;
        display:inline-block; margin-left:8px;
    }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg,#f0f7ff 0%,#e8f0fe 100%);
        border:1px solid #c7d9f8; border-radius:10px;
        padding:1rem 1.2rem; box-shadow:0 2px 8px rgba(37,99,235,0.08);
    }
    [data-testid="stMetricValue"] { color:#0d2b55 !important; font-size:1.8rem !important; font-weight:700 !important; }
    [data-testid="stMetricLabel"] { color:#4b6a9b !important; font-weight:500 !important; }

    .stButton > button {
        background: linear-gradient(135deg,#1a4a8a 0%,#2563eb 100%);
        color:white !important; border:none; border-radius:8px;
        padding:0.55rem 1.8rem; font-weight:600; font-size:0.95rem;
        transition:all 0.2s ease; box-shadow:0 2px 8px rgba(37,99,235,0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg,#0d2b55 0%,#1a4a8a 100%);
        box-shadow:0 4px 14px rgba(37,99,235,0.4); transform:translateY(-1px);
    }
    .stTextInput input, .stNumberInput input {
        border-radius:7px !important; border:1px solid #c7d9f8 !important;
    }
    .claim-badge {
        background: linear-gradient(135deg,#0d2b55,#2563eb);
        color:white; padding:0.8rem 1.5rem; border-radius:10px;
        font-size:1.3rem; font-weight:700; letter-spacing:1px;
        display:inline-block; margin:0.5rem 0;
    }
    .status-pill {
        display:inline-block; padding:4px 14px; border-radius:20px;
        font-size:0.82rem; font-weight:600; margin:2px;
    }
    .status-lodged   { background:#fef3c7; color:#92400e; }
    .status-review   { background:#dbeafe; color:#1e40af; }
    .status-approved { background:#d1fae5; color:#065f46; }
    .status-paid     { background:#ede9fe; color:#5b21b6; }
    .fraud-low    { background:#d1fae5; color:#065f46; border-radius:8px; padding:0.5rem 1rem; }
    .fraud-medium { background:#fef3c7; color:#92400e; border-radius:8px; padding:0.5rem 1rem; }
    .fraud-high   { background:#fee2e2; color:#991b1b; border-radius:8px; padding:0.5rem 1rem; }
    .custom-divider { border:none; border-top:2px solid #e2eaf8; margin:1.5rem 0; }
    .footer {
        text-align:center; color:#8fa3c0; font-size:0.8rem;
        margin-top:3rem; padding-top:1rem; border-top:1px solid #e2eaf8;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────────────────────────
VEHICLE_DB = {
    "ABC123": {"make":"Toyota",    "model":"Camry",      "year":2020,"value":28500},
    "XYZ789": {"make":"Mazda",     "model":"CX-5",       "year":2019,"value":32000},
    "DEF456": {"make":"Honda",     "model":"Civic",      "year":2021,"value":26800},
    "GHI789": {"make":"Holden",    "model":"Commodore",  "year":2018,"value":22000},
    "JKL012": {"make":"Hyundai",   "model":"i30",        "year":2020,"value":24500},
    "MNO345": {"make":"Ford",      "model":"Ranger",     "year":2021,"value":48000},
    "PQR678": {"make":"Subaru",    "model":"Outback",    "year":2019,"value":35500},
    "STU901": {"make":"Nissan",    "model":"X-Trail",    "year":2020,"value":31200},
    "VWX234": {"make":"Kia",       "model":"Sportage",   "year":2022,"value":37800},
    "YZA567": {"make":"Mitsubishi","model":"Outlander",  "year":2021,"value":41000},
    "BCD890": {"make":"Volkswagen","model":"Golf",       "year":2020,"value":33500},
    "EFG123": {"make":"Toyota",    "model":"HiLux",      "year":2022,"value":52000},
    "HIJ456": {"make":"Isuzu",     "model":"D-Max",      "year":2021,"value":49500},
    "KLM789": {"make":"Mercedes",  "model":"C-Class",    "year":2020,"value":68000},
    "NOP012": {"make":"BMW",       "model":"3 Series",   "year":2021,"value":72000},
    "BT12AB": {"make":"Hyundai",   "model":"Tucson",     "year":2022,"value":39000},
    "CU34CD": {"make":"Toyota",    "model":"RAV4",       "year":2021,"value":44500},
    "DV56EF": {"make":"Mazda",     "model":"3",          "year":2020,"value":27000},
    "EW78GH": {"make":"Honda",     "model":"HR-V",       "year":2019,"value":28500},
    "FX90IJ": {"make":"Kia",       "model":"Cerato",     "year":2021,"value":26000},
    "GY12KL": {"make":"Subaru",    "model":"Forester",   "year":2020,"value":38000},
    "HZ34MN": {"make":"Nissan",    "model":"Navara",     "year":2021,"value":47000},
    "1AB2CD": {"make":"Toyota",    "model":"Corolla",    "year":2021,"value":29500},
    "3EF4GH": {"make":"Mazda",     "model":"CX-9",       "year":2020,"value":52000},
    "5IJ6KL": {"make":"Ford",      "model":"Escape",     "year":2019,"value":31000},
    "7MN8OP": {"make":"Holden",    "model":"Colorado",   "year":2018,"value":36000},
    "2QR3ST": {"make":"Volkswagen","model":"Tiguan",     "year":2022,"value":48500},
    "4UV5WX": {"make":"Audi",      "model":"A3",         "year":2021,"value":55000},
    "6YZ7AB": {"make":"BMW",       "model":"X3",         "year":2020,"value":78000},
    "8CD9EF": {"make":"Lexus",     "model":"RX",         "year":2021,"value":82000},
    "9GH0IJ": {"make":"Tesla",     "model":"Model 3",    "year":2022,"value":65000},
}

CAR_DAMAGE_TYPES  = ["Front bumper dent","Rear scratch","Hail damage to roof","Side panel scratch","Cracked windscreen","Door ding"]
HOME_DAMAGE_TYPES = ["Water damage to ceiling","Broken window","Storm damage to roof tiles","Flood damage to flooring","Fire damage to kitchen","Wall crack","Fence damage"]
CAR_REPAIR_COSTS  = {"Front bumper dent":(800,2500),"Rear scratch":(400,1200),"Hail damage to roof":(1500,5000),"Side panel scratch":(350,1100),"Cracked windscreen":(600,1800),"Door ding":(250,900)}
HOME_REPAIR_COSTS = {"Water damage to ceiling":(2000,8000),"Broken window":(300,1200),"Storm damage to roof tiles":(3000,12000),"Flood damage to flooring":(5000,20000),"Fire damage to kitchen":(8000,35000),"Wall crack":(500,3000),"Fence damage":(800,4000)}

MOCK_POLICIES = [
    {"policy_no":"POL-2024-001","type":"Car Insurance","vehicle":"2020 Toyota Camry (ABC123)","annual":892.50,"start":"2024-03-01","expiry":"2025-03-01","status":"Active","coverage":"Comprehensive"},
    {"policy_no":"POL-2024-002","type":"Home Insurance","address":"12 Beach Rd, Surfers Paradise QLD 4217","annual":2340.00,"start":"2024-06-15","expiry":"2025-06-15","status":"Active","coverage":"Premium"},
    {"policy_no":"POL-2023-089","type":"Car Insurance","vehicle":"2019 Mazda CX-5 (XYZ789)","annual":1050.00,"start":"2023-08-01","expiry":"2024-08-01","status":"Expired","coverage":"Comprehensive"},
]

MOCK_CLAIMS = [
    {"claim_no":"CLM-897655","type":"Car Damage","date":"2025-01-15","amount":2400.00,"status":"Approved","desc":"Front bumper dent — car park incident"},
    {"claim_no":"CLM-334210","type":"Home Damage","date":"2025-02-20","amount":8500.00,"status":"Under Review","desc":"Storm damage to roof tiles"},
    {"claim_no":"CLM-112987","type":"Car Damage","date":"2024-11-05","amount":650.00,"status":"Paid","desc":"Cracked windscreen"},
]

AU_POSTCODES_RISK = {
    "2000":{"flood":"Low","bushfire":"Low","state":"NSW"},
    "2010":{"flood":"Medium","bushfire":"Low","state":"NSW"},
    "2065":{"flood":"Low","bushfire":"Low","state":"NSW"},
    "2170":{"flood":"High","bushfire":"Low","state":"NSW"},
    "2750":{"flood":"Medium","bushfire":"Medium","state":"NSW"},
    "3000":{"flood":"Low","bushfire":"Low","state":"VIC"},
    "3121":{"flood":"Medium","bushfire":"Low","state":"VIC"},
    "3220":{"flood":"Low","bushfire":"Medium","state":"VIC"},
    "3550":{"flood":"Medium","bushfire":"High","state":"VIC"},
    "4000":{"flood":"Low","bushfire":"Low","state":"QLD"},
    "4217":{"flood":"High","bushfire":"Low","state":"QLD"},
    "4218":{"flood":"High","bushfire":"Low","state":"QLD"},
    "4220":{"flood":"Medium","bushfire":"Low","state":"QLD"},
    "4350":{"flood":"Medium","bushfire":"High","state":"QLD"},
    "5000":{"flood":"Low","bushfire":"Low","state":"SA"},
    "5950":{"flood":"Low","bushfire":"High","state":"SA"},
    "6000":{"flood":"Low","bushfire":"Low","state":"WA"},
    "6076":{"flood":"Low","bushfire":"High","state":"WA"},
    "7000":{"flood":"Medium","bushfire":"Low","state":"TAS"},
    "0800":{"flood":"High","bushfire":"Medium","state":"NT"},
}

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def fmt_aud(amount: float) -> str:
    return f"AUD {amount:,.2f}"

def gen_claim_number() -> str:
    return "CLM-" + "".join(random.choices(string.digits, k=6))

def gen_policy_number() -> str:
    return "POL-" + str(date.today().year) + "-" + "".join(random.choices(string.digits, k=4))

def detect_damage_mock(claim_type: str) -> tuple[str, float]:
    if claim_type == "Car Damage":
        damage = random.choice(CAR_DAMAGE_TYPES)
        lo, hi = CAR_REPAIR_COSTS[damage]
    else:
        damage = random.choice(HOME_DAMAGE_TYPES)
        lo, hi = HOME_REPAIR_COSTS[damage]
    cost = round(random.uniform(lo, hi), 2)
    return damage, cost

def calc_car_premium(drv_age, drv_years, accidents, claims_hist, fines, suspended,
                     drv_postcode, car_year, car_value, car_use, coverage, excess) -> dict:
    base_rate = 800
    age_factor = 2.0 if drv_age < 25 else (1.5 if drv_age < 30 else (1.0 if drv_age < 65 else 1.2))
    experience_factor = 1.4 if drv_years < 2 else (1.2 if drv_years < 5 else 1.0)
    history_factor = 1 + (accidents * 0.35) + (claims_hist * 0.25) + (fines * 0.1)
    suspension_factor = 1.5 if suspended else 1.0
    postcode_factor = 1.2 if drv_postcode in ["4217","4218","4220","2000","3000"] else 1.0
    vehicle_age_factor = 0.85 if (2026 - car_year) <= 2 else (1.0 if (2026 - car_year) <= 5 else 1.15)
    vehicle_value_factor = car_value / 30000
    usage_map = {"Personal":1.0,"Business":1.3,"Rideshare":1.5,"Farm":0.9}
    usage_factor = usage_map.get(car_use, 1.0)
    coverage_map = {"Third Party":0.35,"Third Party Fire & Theft":0.55,"Comprehensive":1.0}
    coverage_factor = coverage_map.get(coverage, 1.0)
    excess_factor = 1 - ((excess - 500) / 10000)
    annual = (base_rate * age_factor * experience_factor * history_factor * suspension_factor *
              postcode_factor * vehicle_age_factor * vehicle_value_factor * usage_factor *
              coverage_factor * excess_factor)
    return {
        "annual": round(annual, 2), "monthly": round(annual / 12, 2),
        "base_rate": base_rate, "age_factor": age_factor, "experience_factor": experience_factor,
        "history_factor": history_factor, "suspension_factor": suspension_factor,
        "postcode_factor": postcode_factor, "vehicle_age_factor": vehicle_age_factor,
        "vehicle_value_factor": vehicle_value_factor, "usage_factor": usage_factor,
        "coverage_factor": coverage_factor, "excess_factor": excess_factor,
    }

def calc_home_premium(owner_name, home_postcode, prop_type, bedrooms, building_value,
                      contents_value, construction, year_built, has_pool, has_alarm,
                      flood_risk, bushfire_risk, coast_dist, coverage_level, home_excess,
                      home_claims, prev_claim_types) -> dict:
    base_rate = 1200
    building_factor = building_value / 500000
    contents_factor = contents_value / 50000 if contents_value > 0 else 0
    prop_type_map = {"House":1.0,"Apartment":0.8,"Townhouse":0.9,"Villa":0.95}
    property_type_factor = prop_type_map.get(prop_type, 1.0)
    construction_map = {"Brick":1.0,"Concrete":0.95,"Mixed":1.1,"Timber":1.25}
    construction_factor = construction_map.get(construction, 1.0)
    age_factor = 1.0 if year_built >= 2000 else (1.15 if year_built >= 1980 else 1.3)
    flood_map = {"Low":1.0,"Medium":1.3,"High":1.8}
    flood_factor = flood_map.get(flood_risk, 1.0)
    bushfire_map = {"Low":1.0,"Medium":1.25,"High":1.6}
    bushfire_factor = bushfire_map.get(bushfire_risk, 1.0)
    coastal_factor = 1.3 if coast_dist < 1 else (1.15 if coast_dist < 5 else 1.0)
    postcode_factor = 1.2 if home_postcode in ["4217","4218","4220"] else 1.0
    pool_factor = 1.1 if has_pool else 1.0
    alarm_discount = 0.9 if has_alarm else 1.0
    coverage_map = {"Basic":0.7,"Standard":1.0,"Premium":1.4}
    coverage_factor = coverage_map.get(coverage_level, 1.0)
    excess_discount = 1 - ((home_excess - 500) / 10000)
    claims_factor = 1 + (home_claims * 0.25) + (len(prev_claim_types) * 0.15)
    building_premium = (base_rate * building_factor * property_type_factor * construction_factor *
                        age_factor * flood_factor * bushfire_factor * coastal_factor * postcode_factor *
                        pool_factor * alarm_discount * coverage_factor * excess_discount * claims_factor)
    contents_premium = (base_rate * 0.3 * contents_factor * flood_factor * bushfire_factor *
                        coverage_factor * excess_discount * claims_factor) if contents_value > 0 else 0
    annual = building_premium + contents_premium
    return {
        "annual": round(annual, 2), "monthly": round(annual / 12, 2),
        "building_premium": round(building_premium, 2), "contents_premium": round(contents_premium, 2),
        "building_factor": building_factor, "contents_factor": contents_factor,
        "property_type_factor": property_type_factor, "construction_factor": construction_factor,
        "age_factor": age_factor, "flood_factor": flood_factor, "bushfire_factor": bushfire_factor,
        "coastal_factor": coastal_factor, "postcode_factor": postcode_factor,
        "pool_factor": pool_factor, "alarm_discount": alarm_discount,
        "coverage_factor": coverage_factor, "excess_discount": excess_discount,
        "claims_factor": claims_factor,
    }

def fraud_score(policy_age_days: int, claim_amount: float, claim_number_in_year: int,
                damage_type: str, is_new_customer: bool) -> tuple[str, int, list]:
    score = 0
    flags = []
    if policy_age_days < 30:
        score += 40; flags.append("Policy less than 30 days old")
    elif policy_age_days < 90:
        score += 20; flags.append("Policy less than 90 days old")
    if claim_amount > 15000:
        score += 25; flags.append(f"High claim amount ({fmt_aud(claim_amount)})")
    elif claim_amount > 8000:
        score += 10; flags.append(f"Above-average claim amount ({fmt_aud(claim_amount)})")
    if claim_number_in_year >= 3:
        score += 30; flags.append(f"{claim_number_in_year} claims in 12 months")
    elif claim_number_in_year == 2:
        score += 15; flags.append("2 claims in 12 months")
    if is_new_customer:
        score += 10; flags.append("New customer (first policy)")
    if "Fire" in damage_type:
        score += 15; flags.append("Fire damage claim (elevated risk category)")
    score = min(score, 100)
    if score < 30:
        level = "Low"
    elif score < 60:
        level = "Medium"
    else:
        level = "High"
    return level, score, flags

# ─────────────────────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────────────────────
def generate_pdf_quote(quote_type: str, details: dict, annual: float, monthly: float, coverage: str) -> bytes:
    if not PDF_OK:
        return b""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Header
    pdf.set_fill_color(13, 43, 85)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(20, 10)
    pdf.cell(0, 10, "Fire & General Insurance Portal", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_xy(20, 22)
    pdf.cell(0, 8, "Australian General Insurance | ABN 00 000 000 000 | AFSL 000000")

    # Quote title
    pdf.set_text_color(13, 43, 85)
    pdf.set_xy(20, 50)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 10, f"{quote_type} — Insurance Quote", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.set_xy(20, 62)
    pdf.cell(0, 6, f"Quote Reference: QTE-{random.randint(100000,999999)}  |  Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", ln=True)
    pdf.cell(0, 6, f"Valid for 30 days from date of issue", ln=True)

    # Divider
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.8)
    pdf.line(20, 78, 190, 78)

    # Premium box
    pdf.set_fill_color(240, 247, 255)
    pdf.rect(20, 82, 170, 28, 'F')
    pdf.set_text_color(13, 43, 85)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_xy(25, 86)
    pdf.cell(80, 8, f"Annual Premium: {fmt_aud(annual)}")
    pdf.set_xy(110, 86)
    pdf.cell(80, 8, f"Monthly: {fmt_aud(monthly)}")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_xy(25, 96)
    pdf.cell(0, 8, f"Coverage: {coverage}")

    # Details
    pdf.set_xy(20, 118)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(13, 43, 85)
    pdf.cell(0, 8, "Quote Details", ln=True)
    pdf.set_line_width(0.3)
    pdf.set_draw_color(200, 210, 230)
    pdf.line(20, 128, 190, 128)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    y = 132
    for k, v in details.items():
        pdf.set_xy(20, y)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(70, 7, str(k) + ":")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, str(v), ln=True)
        y += 7
        if y > 250:
            pdf.add_page()
            y = 20

    # Footer
    pdf.set_xy(20, 270)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "This quote is indicative only and subject to full underwriting assessment. Not a contract of insurance.", ln=True)
    pdf.cell(0, 5, "© 2026 Fire & General Insurance Portal. This is a demonstration application only.")

    return bytes(pdf.output())

# ─────────────────────────────────────────────────────────────
# AI HELPERS
# ─────────────────────────────────────────────────────────────
def ai_analyse_damage(image_bytes: bytes, claim_type: str) -> dict:
    if not AI_OK:
        return {"damage_type": "Unable to analyse", "severity": "Unknown", "estimate_low": 0, "estimate_high": 0, "description": "AI not available"}
    try:
        client = OpenAI()
        b64 = base64.b64encode(image_bytes).decode()
        prompt = (
            f"You are an Australian insurance damage assessor. Analyse this {claim_type.lower()} photo. "
            "Respond ONLY with a JSON object with these exact keys: "
            "damage_type (string), severity (Minor/Moderate/Severe), "
            "estimate_low (integer AUD), estimate_high (integer AUD), description (1-2 sentence summary). "
            "Be realistic with Australian repair costs."
        )
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":[
                {"type":"text","text":prompt},
                {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
            ]}],
            max_tokens=300,
        )
        text = resp.choices[0].message.content.strip()
        # strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        return {"damage_type": "Analysis error", "severity": "Unknown", "estimate_low": 0, "estimate_high": 0, "description": str(e)}

def ai_natural_language_quote(user_text: str, quote_type: str) -> dict:
    if not AI_OK:
        return {}
    try:
        client = OpenAI()
        if quote_type == "Car":
            fields = "make, model, year (int), value_aud (int), postcode (string), driver_age (int), years_licensed (int)"
        else:
            fields = "postcode (string), property_type (House/Apartment/Townhouse/Villa), bedrooms (int), building_value_aud (int), year_built (int)"
        prompt = (
            f"Extract insurance quote fields from this text for a {quote_type} insurance quote in Australia. "
            f"Return ONLY a JSON object with these fields: {fields}. "
            f"If a field is not mentioned, omit it. Text: \"{user_text}\""
        )
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=200,
        )
        text = resp.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return {}

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ Insurance Portal")
    st.markdown("---")

    modules = ["Damage Claims", "Car Insurance Quote", "Home Insurance Quote", "Strata Insurance Quote"]
    if feat("claims_tracker"):
        modules.append("Claims Tracker")
    if feat("policy_dashboard"):
        modules.append("My Policies")
    if feat("multi_asset_bundle"):
        modules.append("Bundle Quote")
    if feat("postcode_heatmap"):
        modules.append("Risk Map")
    if feat("admin_dashboard"):
        modules.append("Admin Dashboard")

    module = st.radio("Select Module", options=modules, label_visibility="collapsed")
    st.markdown("---")

    if feat("broker_callback"):
        with st.expander("📞 Speak to a Broker"):
            bc_name_inp = st.text_input("Your Name", key="bc_name")
            bc_phone_inp = st.text_input("Phone Number", key="bc_phone")
            bc_time_inp = st.selectbox("Preferred Time", ["Morning (9am–12pm)","Afternoon (12pm–5pm)","Evening (5pm–7pm)"], key="bc_time")
            if st.button("Request Callback", key="bc_submit"):
                if bc_name_inp and bc_phone_inp:
                    st.success(f"✅ Thanks {bc_name_inp}! A broker will call {bc_phone_inp} during {bc_time_inp}.")
                else:
                    st.error("Please enter your name and phone number.")

    if feat("renewal_reminder"):
        with st.expander("🔔 Renewal Reminder"):
            rr_email = st.text_input("Your Email", key="rr_email")
            rr_expiry = st.date_input("Policy Expiry Date", key="rr_expiry", min_value=date.today())
            if st.button("Set Reminder", key="rr_submit"):
                if rr_email and "@" in rr_email:
                    reminder_date = rr_expiry - timedelta(days=30)
                    st.success(f"✅ Reminder set! We'll email {rr_email} on {reminder_date.strftime('%d %b %Y')} — 30 days before your policy expires.")
                else:
                    st.error("Please enter a valid email address.")

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.78rem;opacity:0.7;'>Australian General Insurance<br/>ABN 00 000 000 000<br/>AFSL 000000</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🛡️ Fire &amp; General Insurance Portal</h1>
    <p>Professional insurance solutions for Australian homes, vehicles, and strata properties</p>
</div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# MODULE: DAMAGE CLAIMS
# ═════════════════════════════════════════════════════════════
if module == "Damage Claims":
    st.markdown("## 📋 Damage Claims")
    st.markdown("Upload photos of the damage to automatically detect and pre-fill your claim form.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="section-header">📸 Upload Damage Photos</div>', unsafe_allow_html=True)
        claim_type = st.selectbox("Claim Type", ["Car Damage", "Home Damage"])

        if feat("natural_language"):
            with st.expander("💬 Describe the damage in plain English (AI auto-fill)"):
                nl_desc = st.text_area("Describe what happened", placeholder="e.g. A tree branch fell on my car during last night's storm and dented the roof and cracked the windscreen", key="nl_claim")
                if st.button("Auto-fill from description", key="nl_claim_btn"):
                    if nl_desc.strip():
                        with st.spinner("Analysing description..."):
                            time.sleep(0.5)
                        st.session_state["nl_claim_desc"] = nl_desc
                        st.success("✅ Description saved — damage type will be pre-filled below.")

        uploaded_files = st.file_uploader(
            "Upload damage photos (JPG, JPEG, PNG)",
            type=["jpg","jpeg","png"],
            accept_multiple_files=True,
        )

        damage_detected = None
        estimated_cost = None

        if uploaded_files:
            st.markdown(f"**{len(uploaded_files)} photo(s) uploaded**")
            for uf in uploaded_files[:3]:
                st.image(uf, use_container_width=True, caption=uf.name)

            if feat("ai_damage_detection") and AI_OK:
                with st.spinner("🤖 AI analysing damage..."):
                    img_bytes = uploaded_files[0].read()
                    result = ai_analyse_damage(img_bytes, claim_type)
                damage_detected = result.get("damage_type", "Unknown")
                estimated_cost = result.get("estimate_high", 0)
                severity = result.get("severity", "Unknown")
                desc = result.get("description", "")
                lo = result.get("estimate_low", 0)
                hi = result.get("estimate_high", 0)
                st.success(f"✅ AI Analysis Complete")
                st.markdown(f"**Damage:** {damage_detected}  \n**Severity:** {severity}  \n**Estimate:** {fmt_aud(lo)} – {fmt_aud(hi)}  \n_{desc}_")
            else:
                with st.spinner("Analysing damage..."):
                    time.sleep(1.5)
                damage_detected, estimated_cost = detect_damage_mock(claim_type)
                st.success(f"✅ Damage detected: **{damage_detected}** — Estimated repair: **{fmt_aud(estimated_cost)}**")

    with col2:
        st.markdown('<div class="section-header">📝 Claim Form</div>', unsafe_allow_html=True)
        claim_number = gen_claim_number()
        st.text_input("Claim Number", value=claim_number, disabled=True)
        claimant_name = st.text_input("Claimant Name *", value="Peter North")
        claim_date = st.date_input("Claim Date *", value=date.today())
        incident_date = st.date_input("Incident Date *", value=date.today())
        incident_location = st.text_input("Incident Location *", placeholder="e.g. 12 Beach Rd, Surfers Paradise QLD 4217")
        damage_description = st.text_area(
            "Damage Description *",
            value=damage_detected if damage_detected else "",
            placeholder="Describe the damage in detail...",
        )
        estimated_repair = st.number_input(
            "Estimated Repair Cost (AUD)",
            min_value=0.0, max_value=500000.0,
            value=float(estimated_cost) if estimated_cost else 0.0,
            step=100.0,
        )
        police_report = st.checkbox("Police report filed")
        third_party = st.checkbox("Third party involved")

        if feat("fraud_scoring"):
            st.markdown('<div class="section-header">🔍 Fraud Risk Assessment</div>', unsafe_allow_html=True)
            policy_age = st.number_input("Days since policy started", min_value=0, max_value=3650, value=180)
            claims_this_year = st.number_input("Number of claims in last 12 months", min_value=0, max_value=20, value=0)
            is_new_cust = st.checkbox("New customer (first policy)")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    with st.form("claim_form"):
        submitted = st.form_submit_button("📤 Submit Claim", use_container_width=True)
        if submitted:
            errors = []
            if not claimant_name.strip():
                errors.append("Claimant Name is required.")
            if not incident_location.strip():
                errors.append("Incident Location is required.")
            if not damage_description.strip():
                errors.append("Damage Description is required.")
            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                if feat("fraud_scoring"):
                    fr_level, fr_score, fr_flags = fraud_score(
                        policy_age, estimated_repair, claims_this_year,
                        damage_description, is_new_cust
                    )
                    css_class = f"fraud-{fr_level.lower()}"
                    st.markdown(f'<div class="{css_class}">🔍 <b>Fraud Risk: {fr_level}</b> (Score: {fr_score}/100)</div>', unsafe_allow_html=True)
                    if fr_flags:
                        with st.expander("Risk Flags"):
                            for flag in fr_flags:
                                st.warning(f"⚠️ {flag}")

                st.success(f"✅ Claim submitted successfully!")
                st.markdown(f'<div class="claim-badge">Claim Number: {claim_number}</div>', unsafe_allow_html=True)
                st.info(f"**{claimant_name}**, your claim for **{fmt_aud(estimated_repair)}** has been lodged. Our team will contact you within 2 business days.")
                st.balloons()

# ═════════════════════════════════════════════════════════════
# MODULE: CAR INSURANCE QUOTE
# ═════════════════════════════════════════════════════════════
elif module == "Car Insurance Quote":
    st.markdown("## 🚗 Car Insurance Quote")
    st.markdown("Get an instant comprehensive car insurance quote tailored to your vehicle and driving history.")

    # Natural language input
    if feat("natural_language"):
        with st.expander("💬 Describe your car and situation (AI auto-fill)"):
            nl_car = st.text_area("Tell us about your car", placeholder="e.g. I have a 2021 Toyota RAV4 in Brisbane, I'm 35 years old and have been driving for 15 years", key="nl_car")
            if st.button("Auto-fill from description", key="nl_car_btn"):
                if nl_car.strip():
                    with st.spinner("Extracting details..."):
                        extracted = ai_natural_language_quote(nl_car, "Car")
                    if extracted:
                        st.session_state.update({
                            "nl_car_make": extracted.get("make",""),
                            "nl_car_model": extracted.get("model",""),
                            "nl_car_year": extracted.get("year", 2020),
                            "nl_car_value": extracted.get("value_aud", 30000),
                            "nl_car_postcode": extracted.get("postcode",""),
                            "nl_car_age": extracted.get("driver_age", 35),
                            "nl_car_years": extracted.get("years_licensed", 10),
                        })
                        st.success("✅ Details extracted! Form fields pre-filled below.")
                    else:
                        st.warning("Could not extract details. Please fill in the form manually.")

    # Plate lookup
    st.markdown('<div class="section-header">🔍 Vehicle Lookup</div>', unsafe_allow_html=True)
    lc1, lc2, lc3 = st.columns([3,2,3])
    with lc1:
        plate = st.text_input("", placeholder="e.g. ABC123", key="plate_input", label_visibility="collapsed")
    with lc2:
        lookup_btn = st.button("🔍 Lookup Vehicle")
    with lc3:
        st.caption("Powered by Australian vehicle registry")

    if lookup_btn and plate:
        with st.spinner("Searching Australian vehicle database..."):
            time.sleep(random.uniform(0.8, 1.8))
        plate_upper = plate.strip().upper()
        if plate_upper in VEHICLE_DB:
            v = VEHICLE_DB[plate_upper]
            st.session_state["looked_up_vehicle"] = v
            st.success(f"✅ Vehicle found! Details auto-filled — {v['year']} {v['make']} {v['model']} (Value: {fmt_aud(v['value'])})")
        else:
            st.warning("⚠️ Vehicle not found in registry. Please enter details manually.")
            st.session_state.pop("looked_up_vehicle", None)

    lv = st.session_state.get("looked_up_vehicle", {})

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="section-header">👤 Driver Details</div>', unsafe_allow_html=True)
        drv_name = st.text_input("Full Name *", value=st.session_state.get("nl_car_name","Peter North"))
        drv_age  = st.number_input("Age *", min_value=16, max_value=100, value=st.session_state.get("nl_car_age", 35))
        drv_years = st.number_input("Years Licensed *", min_value=0, max_value=80, value=st.session_state.get("nl_car_years", 10))
        drv_postcode = st.text_input("Postcode *", value=st.session_state.get("nl_car_postcode","4217"))

        st.markdown('<div class="section-header">🚦 Driving History</div>', unsafe_allow_html=True)
        accidents   = st.number_input("Accidents (last 5 years)",    min_value=0, max_value=20, value=0)
        claims_hist = st.number_input("Claims (last 5 years)",       min_value=0, max_value=20, value=0)
        fines       = st.number_input("Speeding Fines (last 3 years)",min_value=0, max_value=20, value=0)
        suspended   = st.checkbox("Licence previously suspended")

    with col2:
        st.markdown('<div class="section-header">🚘 Vehicle Details</div>', unsafe_allow_html=True)
        car_make  = st.text_input("Make *",  value=lv.get("make",  st.session_state.get("nl_car_make","Toyota")))
        car_model = st.text_input("Model *", value=lv.get("model", st.session_state.get("nl_car_model","Camry")))
        car_year  = st.number_input("Year *", min_value=1980, max_value=2026, value=lv.get("year", st.session_state.get("nl_car_year", 2020)))
        car_value = st.number_input("Vehicle Value (AUD) *", min_value=1000, max_value=500000, value=lv.get("value", st.session_state.get("nl_car_value", 30000)), step=500)
        car_use   = st.selectbox("Primary Use *", ["Personal","Business","Rideshare","Farm"])

        st.markdown('<div class="section-header">🛡️ Coverage</div>', unsafe_allow_html=True)
        coverage  = st.selectbox("Coverage Type *", ["Comprehensive","Third Party Fire & Theft","Third Party"])

        if feat("excess_slider"):
            excess = st.slider("Excess Amount (AUD)", min_value=250, max_value=5000, value=500, step=250)
            # Live preview
            preview = calc_car_premium(drv_age, drv_years, accidents, claims_hist, fines,
                                       suspended, drv_postcode, car_year, car_value, car_use,
                                       coverage, excess)
            st.info(f"💡 With AUD {excess:,} excess → **{fmt_aud(preview['annual'])}/yr** ({fmt_aud(preview['monthly'])}/mo)")
        else:
            excess = st.selectbox("Excess Amount (AUD) *", [250, 500, 750, 1000, 1500, 2000, 5000])

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Comparison mode
    if feat("comparison_mode"):
        show_comparison = st.checkbox("📊 Show coverage comparison (Basic / Standard / Comprehensive)")
        if show_comparison:
            st.markdown("### 📊 Coverage Comparison")
            comp_cols = st.columns(3)
            for i, (cov_name, cov_label) in enumerate([("Third Party","Basic"),("Third Party Fire & Theft","Standard"),("Comprehensive","Comprehensive")]):
                q = calc_car_premium(drv_age, drv_years, accidents, claims_hist, fines,
                                     suspended, drv_postcode, car_year, car_value, car_use,
                                     cov_name, excess)
                with comp_cols[i]:
                    st.markdown(f"**{cov_label}**")
                    st.metric("Annual", fmt_aud(q["annual"]))
                    st.metric("Monthly", fmt_aud(q["monthly"]))
                    st.caption(cov_name)

    calc_btn = st.button("⚡ Calculate Premium", use_container_width=True, key="car_calc")

    if calc_btn:
        errors = []
        if not drv_name.strip():   errors.append("Full Name is required.")
        if not drv_postcode.strip(): errors.append("Postcode is required.")
        if not car_make.strip():   errors.append("Vehicle Make is required.")
        if not car_model.strip():  errors.append("Vehicle Model is required.")
        if errors:
            for e in errors: st.error(f"❌ {e}")
        else:
            q = calc_car_premium(drv_age, drv_years, accidents, claims_hist, fines,
                                 suspended, drv_postcode, car_year, car_value, car_use,
                                 coverage, excess)
            annual, monthly = q["annual"], q["monthly"]

            st.markdown("---")
            st.markdown("### 💰 Your Quote")
            m1, m2, m3 = st.columns(3)
            m1.metric("Annual Premium", fmt_aud(annual))
            m2.metric("Monthly Premium", fmt_aud(monthly))
            m3.metric("Coverage Type", coverage)

            if feat("risk_radar_chart"):
                with st.expander("🕸️ Your Risk Profile"):
                    categories = ["Age Risk","Experience","History","Postcode","Vehicle Value","Usage"]
                    values = [
                        min((q["age_factor"]-0.8)/1.2*100, 100),
                        min((q["experience_factor"]-0.9)/0.5*100, 100),
                        min((q["history_factor"]-1.0)/2.0*100, 100),
                        min((q["postcode_factor"]-1.0)/0.3*100, 100),
                        min((q["vehicle_value_factor"]-0.3)/2.0*100, 100),
                        min((q["usage_factor"]-0.8)/0.7*100, 100),
                    ]
                    fig = go.Figure(data=go.Scatterpolar(
                        r=values + [values[0]],
                        theta=categories + [categories[0]],
                        fill='toself',
                        fillcolor='rgba(37,99,235,0.2)',
                        line=dict(color='#2563eb', width=2),
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                        showlegend=False, height=350,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with st.expander("📊 Quote Breakdown — All Risk Factors"):
                bd = pd.DataFrame({
                    "Factor": [
                        "Base Rate", f"Age Factor (age {drv_age})",
                        f"Experience Factor ({drv_years} yrs)",
                        f"History Factor ({accidents} accidents, {claims_hist} claims, {fines} fines)",
                        "Suspension Factor", f"Postcode Factor ({drv_postcode})",
                        f"Vehicle Age Factor ({car_year})", f"Vehicle Value Factor ({fmt_aud(car_value)})",
                        f"Usage Factor ({car_use})", f"Coverage Factor ({coverage})",
                        f"Excess Discount (AUD {excess})",
                    ],
                    "Multiplier": [
                        f"AUD {q['base_rate']:,.2f}", f"×{q['age_factor']:.2f}",
                        f"×{q['experience_factor']:.2f}", f"×{q['history_factor']:.2f}",
                        f"×{q['suspension_factor']:.2f}", f"×{q['postcode_factor']:.2f}",
                        f"×{q['vehicle_age_factor']:.2f}", f"×{q['vehicle_value_factor']:.2f}",
                        f"×{q['usage_factor']:.2f}", f"×{q['coverage_factor']:.2f}",
                        f"×{q['excess_factor']:.2f}",
                    ],
                })
                st.table(bd)
                st.info(f"**Final Annual Premium: {fmt_aud(annual)}** | Monthly: {fmt_aud(monthly)}")

            if feat("email_quote"):
                st.markdown("---")
                eq_col1, eq_col2 = st.columns([3,1])
                with eq_col1:
                    eq_email = st.text_input("📧 Email this quote to:", placeholder="you@example.com", key="car_email")
                with eq_col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Send Quote", key="car_send_email"):
                        if eq_email and "@" in eq_email:
                            st.success(f"✅ Quote sent to **{eq_email}** — check your inbox!")
                        else:
                            st.error("Please enter a valid email address.")

            if feat("pdf_quote") and PDF_OK:
                details = {
                    "Driver": drv_name, "Age": drv_age, "Postcode": drv_postcode,
                    "Vehicle": f"{car_year} {car_make} {car_model}",
                    "Vehicle Value": fmt_aud(car_value), "Primary Use": car_use,
                    "Excess": fmt_aud(excess), "Coverage": coverage,
                    "Accidents (5yr)": accidents, "Claims (5yr)": claims_hist,
                }
                pdf_bytes = generate_pdf_quote("Car Insurance", details, annual, monthly, coverage)
                st.download_button(
                    label="📄 Download PDF Quote",
                    data=pdf_bytes,
                    file_name=f"car_quote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

# ═════════════════════════════════════════════════════════════
# MODULE: HOME INSURANCE QUOTE
# ═════════════════════════════════════════════════════════════
elif module == "Home Insurance Quote":
    st.markdown("## 🏠 Home Insurance Quote")
    st.markdown("Calculate your home and contents insurance premium based on your property details and location risk.")

    if feat("natural_language"):
        with st.expander("💬 Describe your property (AI auto-fill)"):
            nl_home = st.text_area("Tell us about your property", placeholder="e.g. I have a 4 bedroom brick house in Brisbane built in 2005, worth about $650,000", key="nl_home")
            if st.button("Auto-fill from description", key="nl_home_btn"):
                if nl_home.strip():
                    with st.spinner("Extracting details..."):
                        extracted = ai_natural_language_quote(nl_home, "Home")
                    if extracted:
                        st.session_state.update({
                            "nl_home_postcode": extracted.get("postcode",""),
                            "nl_home_type": extracted.get("property_type","House"),
                            "nl_home_beds": extracted.get("bedrooms", 3),
                            "nl_home_value": extracted.get("building_value_aud", 500000),
                            "nl_home_year": extracted.get("year_built", 2005),
                        })
                        st.success("✅ Details extracted! Form fields pre-filled below.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="section-header">🏡 Property Details</div>', unsafe_allow_html=True)
        owner_name    = st.text_input("Owner Name *", value="Peter North")
        home_postcode = st.text_input("Postcode *", value=st.session_state.get("nl_home_postcode","4217"))

        # Postcode risk lookup
        if home_postcode in AU_POSTCODES_RISK:
            risk_info = AU_POSTCODES_RISK[home_postcode]
            st.info(f"📍 {risk_info['state']} — Flood Risk: **{risk_info['flood']}** | Bushfire Risk: **{risk_info['bushfire']}**")

        prop_type      = st.selectbox("Property Type *", ["House","Apartment","Townhouse","Villa"],
                                      index=["House","Apartment","Townhouse","Villa"].index(st.session_state.get("nl_home_type","House")))
        bedrooms       = st.number_input("Bedrooms *", min_value=1, max_value=10, value=st.session_state.get("nl_home_beds",3))
        building_value = st.number_input("Building Value (AUD) *", min_value=50000, max_value=5000000,
                                         value=st.session_state.get("nl_home_value",500000), step=10000)
        contents_value = st.number_input("Contents Value (AUD) *", min_value=0, max_value=1000000, value=50000, step=1000)

        st.markdown('<div class="section-header">🏗️ Property Features</div>', unsafe_allow_html=True)
        construction = st.selectbox("Construction Type *", ["Brick","Timber","Mixed","Concrete"])
        year_built   = st.number_input("Year Built *", min_value=1900, max_value=2027, value=st.session_state.get("nl_home_year",2010))
        has_pool     = st.checkbox("Swimming Pool")
        has_alarm    = st.checkbox("Security Alarm")

    with col2:
        st.markdown('<div class="section-header">📍 Location & Risk</div>', unsafe_allow_html=True)
        default_flood = AU_POSTCODES_RISK.get(home_postcode, {}).get("flood","Low")
        default_bush  = AU_POSTCODES_RISK.get(home_postcode, {}).get("bushfire","Low")
        flood_risk    = st.selectbox("Flood Risk Zone *", ["Low","Medium","High"],
                                     index=["Low","Medium","High"].index(default_flood))
        bushfire_risk = st.selectbox("Bushfire Risk Zone *", ["Low","Medium","High"],
                                     index=["Low","Medium","High"].index(default_bush))
        coast_dist    = st.number_input("Distance to Coast (km) *", min_value=0.0, max_value=100.0, value=2.5, step=0.5, format="%.1f")

        st.markdown('<div class="section-header">🛡️ Coverage Options</div>', unsafe_allow_html=True)
        coverage_level = st.selectbox("Coverage Level *", ["Basic","Standard","Premium"])

        if feat("excess_slider"):
            home_excess = st.slider("Excess Amount (AUD)", min_value=500, max_value=5000, value=500, step=500)
        else:
            home_excess = st.selectbox("Excess (AUD) *", [500,1000,2000,5000])

        st.markdown('<div class="section-header">📋 Claims History</div>', unsafe_allow_html=True)
        home_claims     = st.number_input("Claims (last 5 years)", min_value=0, max_value=10, value=0)
        prev_claim_types = st.multiselect("Previous Claim Types", ["Storm","Flood","Fire","Theft","Water Damage"])

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    if feat("comparison_mode"):
        show_home_comp = st.checkbox("📊 Show coverage comparison (Basic / Standard / Premium)")
        if show_home_comp:
            st.markdown("### 📊 Coverage Comparison")
            hc_cols = st.columns(3)
            for i, cov in enumerate(["Basic","Standard","Premium"]):
                hq = calc_home_premium(owner_name, home_postcode, prop_type, bedrooms, building_value,
                                       contents_value, construction, year_built, has_pool, has_alarm,
                                       flood_risk, bushfire_risk, coast_dist, cov, home_excess,
                                       home_claims, prev_claim_types)
                with hc_cols[i]:
                    st.markdown(f"**{cov}**")
                    st.metric("Annual", fmt_aud(hq["annual"]))
                    st.metric("Monthly", fmt_aud(hq["monthly"]))

    home_calc_btn = st.button("⚡ Calculate Premium", use_container_width=True, key="home_calc")

    if home_calc_btn:
        errors = []
        if not owner_name.strip():    errors.append("Owner Name is required.")
        if not home_postcode.strip(): errors.append("Postcode is required.")
        if errors:
            for e in errors: st.error(f"❌ {e}")
        else:
            hq = calc_home_premium(owner_name, home_postcode, prop_type, bedrooms, building_value,
                                   contents_value, construction, year_built, has_pool, has_alarm,
                                   flood_risk, bushfire_risk, coast_dist, coverage_level, home_excess,
                                   home_claims, prev_claim_types)
            annual, monthly = hq["annual"], hq["monthly"]

            st.markdown("---")
            st.markdown("### 💰 Your Quote")
            m1, m2, m3 = st.columns(3)
            m1.metric("Annual Premium", fmt_aud(annual))
            m2.metric("Monthly Premium", fmt_aud(monthly))
            m3.metric("Coverage Level", coverage_level)

            if feat("risk_radar_chart"):
                with st.expander("🕸️ Your Risk Profile"):
                    categories = ["Flood Risk","Bushfire Risk","Coastal Risk","Building Age","Claims History","Coverage Level"]
                    flood_v   = {"Low":10,"Medium":50,"High":90}[flood_risk]
                    bush_v    = {"Low":10,"Medium":50,"High":90}[bushfire_risk]
                    coast_v   = 90 if coast_dist < 1 else (50 if coast_dist < 5 else 10)
                    age_v     = 10 if year_built >= 2000 else (50 if year_built >= 1980 else 90)
                    claims_v  = min(home_claims * 20, 100)
                    cov_v     = {"Basic":20,"Standard":50,"Premium":90}[coverage_level]
                    values = [flood_v, bush_v, coast_v, age_v, claims_v, cov_v]
                    fig = go.Figure(data=go.Scatterpolar(
                        r=values + [values[0]], theta=categories + [categories[0]],
                        fill='toself', fillcolor='rgba(37,99,235,0.2)',
                        line=dict(color='#2563eb', width=2),
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                        showlegend=False, height=350,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with st.expander("📊 Quote Breakdown — All Risk Factors"):
                bd = pd.DataFrame({
                    "Factor": [
                        "Base Rate", f"Building Value Factor ({fmt_aud(building_value)})",
                        f"Contents Value Factor ({fmt_aud(contents_value)})",
                        f"Property Type Factor ({prop_type})", f"Construction Factor ({construction})",
                        f"Building Age Factor (built {year_built})", f"Flood Risk Factor ({flood_risk})",
                        f"Bushfire Risk Factor ({bushfire_risk})", f"Coastal Factor ({coast_dist} km)",
                        f"Postcode Factor ({home_postcode})", "Pool Factor", "Security Alarm Discount",
                        f"Coverage Factor ({coverage_level})", f"Excess Discount (AUD {home_excess})",
                        f"Claims Factor ({home_claims} claims, {len(prev_claim_types)} types)",
                    ],
                    "Value": [
                        "AUD 1,200.00", f"×{hq['building_factor']:.2f}", f"×{hq['contents_factor']:.2f}",
                        f"×{hq['property_type_factor']:.2f}", f"×{hq['construction_factor']:.2f}",
                        f"×{hq['age_factor']:.2f}", f"×{hq['flood_factor']:.2f}",
                        f"×{hq['bushfire_factor']:.2f}", f"×{hq['coastal_factor']:.2f}",
                        f"×{hq['postcode_factor']:.2f}", f"×{hq['pool_factor']:.2f}",
                        f"×{hq['alarm_discount']:.2f}", f"×{hq['coverage_factor']:.2f}",
                        f"×{hq['excess_discount']:.2f}", f"×{hq['claims_factor']:.2f}",
                    ],
                })
                st.table(bd)
                st.info(f"Building: **{fmt_aud(hq['building_premium'])}** | Contents: **{fmt_aud(hq['contents_premium'])}** | **Total: {fmt_aud(annual)}**")

            if feat("email_quote"):
                st.markdown("---")
                eq_col1, eq_col2 = st.columns([3,1])
                with eq_col1:
                    eq_email_h = st.text_input("📧 Email this quote to:", placeholder="you@example.com", key="home_email")
                with eq_col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Send Quote", key="home_send_email"):
                        if eq_email_h and "@" in eq_email_h:
                            st.success(f"✅ Quote sent to **{eq_email_h}**!")
                        else:
                            st.error("Please enter a valid email address.")

            if feat("pdf_quote") and PDF_OK:
                details = {
                    "Owner": owner_name, "Postcode": home_postcode,
                    "Property Type": prop_type, "Bedrooms": bedrooms,
                    "Building Value": fmt_aud(building_value), "Contents Value": fmt_aud(contents_value),
                    "Construction": construction, "Year Built": year_built,
                    "Flood Risk": flood_risk, "Bushfire Risk": bushfire_risk,
                    "Coverage Level": coverage_level, "Excess": fmt_aud(home_excess),
                }
                pdf_bytes = generate_pdf_quote("Home Insurance", details, annual, monthly, coverage_level)
                st.download_button(
                    label="📄 Download PDF Quote",
                    data=pdf_bytes,
                    file_name=f"home_quote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

# ═════════════════════════════════════════════════════════════
# MODULE: STRATA INSURANCE QUOTE
# ═════════════════════════════════════════════════════════════
elif module == "Strata Insurance Quote":
    st.markdown("## 🏢 Strata Insurance Quote")
    st.markdown("Calculate body corporate insurance premiums for strata-titled properties across Australia.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="section-header">🏢 Body Corporate Details</div>', unsafe_allow_html=True)
        bc_name        = st.text_input("Body Corporate Name *", placeholder="e.g. Sunrise Residences BC")
        strata_postcode = st.text_input("Postcode *", value="4217")
        strata_manager = st.text_input("Strata Manager (optional)", placeholder="e.g. Smith Strata Pty Ltd")

        st.markdown('<div class="section-header">🏗️ Building Details</div>', unsafe_allow_html=True)
        num_units          = st.number_input("Number of Units/Lots *", min_value=1, max_value=500, value=24)
        building_type      = st.selectbox("Building Type *", ["Low-rise","High-rise"])
        strata_year_built  = st.number_input("Year Built *", min_value=1900, max_value=2027, value=2005)
        strata_construction = st.selectbox("Construction Type *", ["Brick","Concrete","Mixed"])

        st.markdown('<div class="section-header">🏊 Facilities</div>', unsafe_allow_html=True)
        strata_pool    = st.checkbox("Swimming Pool")
        strata_gym     = st.checkbox("Gym")
        strata_lifts   = st.checkbox("Lifts / Elevators")
        parking_levels = st.number_input("Number of Parking Levels", min_value=0, max_value=10, value=1)

    with col2:
        st.markdown('<div class="section-header">🛡️ Coverage & Risk</div>', unsafe_allow_html=True)
        building_insured = st.number_input("Building Insurance Value (AUD) *", min_value=500000,
                                           max_value=500000000, value=5000000, step=100000)
        liability_limit  = st.selectbox("Public Liability Limit (AUD) *",
                                        [10000000,20000000,30000000],
                                        format_func=lambda x: f"AUD {x:,}")
        office_bearers   = st.checkbox("Office Bearers Liability")

        st.markdown('<div class="section-header">📍 Location Risks</div>', unsafe_allow_html=True)
        strata_flood    = st.selectbox("Flood Risk Zone *", ["Low","Medium","High"])
        strata_bushfire = st.selectbox("Bushfire Risk Zone *", ["Low","Medium","High"])
        strata_coast    = st.number_input("Distance to Coast (km) *", min_value=0.0, max_value=100.0, value=2.5, step=0.5, format="%.1f")

        st.markdown('<div class="section-header">📋 Claims History</div>', unsafe_allow_html=True)
        strata_claims      = st.number_input("Claims (last 5 years)", min_value=0, max_value=10, value=0)
        strata_claim_types = st.multiselect("Claim Types", ["Storm","Flood","Fire","Liability","Property Damage"])

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    strata_calc_btn = st.button("⚡ Calculate Premium", use_container_width=True, key="strata_calc")

    if strata_calc_btn:
        errors = []
        if not bc_name.strip():        errors.append("Body Corporate Name is required.")
        if not strata_postcode.strip(): errors.append("Postcode is required.")
        if errors:
            for e in errors: st.error(f"❌ {e}")
        else:
            base_rate_per_unit  = 150
            units_factor        = num_units / 50
            building_age_factor = 1.0 if strata_year_built >= 2000 else (1.2 if strata_year_built >= 1980 else 1.4)
            sc_map = {"Brick":1.0,"Concrete":0.95,"Mixed":1.1}
            construction_factor = sc_map.get(strata_construction, 1.0)
            high_rise_factor    = 1.3 if building_type == "High-rise" else 1.0
            pool_factor         = 1.15 if strata_pool else 1.0
            gym_factor          = 1.1  if strata_gym  else 1.0
            lifts_factor        = 1.2  if strata_lifts else 1.0
            parking_factor      = 1 + (parking_levels * 0.05)
            flood_map           = {"Low":1.0,"Medium":1.25,"High":1.6}
            flood_factor        = flood_map.get(strata_flood, 1.0)
            coastal_factor      = 1.2 if strata_coast < 1 else (1.1 if strata_coast < 5 else 1.0)
            postcode_factor     = 1.15 if strata_postcode in ["4217","4218","4220"] else 1.0
            claims_factor       = 1 + (strata_claims * 0.2)
            liability_factor    = 1.0 + (liability_limit / 10000000 - 1) * 0.08
            office_factor       = 1.12 if office_bearers else 1.0
            building_value_factor = building_insured / 5000000

            total_annual = (base_rate_per_unit * num_units * units_factor * building_age_factor *
                            construction_factor * high_rise_factor * pool_factor * gym_factor *
                            lifts_factor * parking_factor * flood_factor * coastal_factor *
                            postcode_factor * claims_factor * liability_factor * office_factor *
                            building_value_factor)
            per_unit     = total_annual / num_units
            monthly_total = total_annual / 12

            st.markdown("---")
            st.markdown("### 💰 Your Quote")
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Annual Premium", fmt_aud(total_annual))
            m2.metric("Per Unit (Annual)",    fmt_aud(per_unit))
            m3.metric("Monthly Total",        fmt_aud(monthly_total))

            with st.expander("📊 Quote Breakdown — All Risk Factors"):
                bd = pd.DataFrame({
                    "Factor": [
                        f"Base Rate per Unit × {num_units} units",
                        f"Units Scale Factor ({num_units} units / 50)",
                        f"Building Age Factor (built {strata_year_built})",
                        f"Construction Factor ({strata_construction})",
                        f"Building Type Factor ({building_type})",
                        "Swimming Pool Factor", "Gym Factor", "Lifts/Elevators Factor",
                        f"Parking Factor ({parking_levels} levels)",
                        f"Flood Risk Factor ({strata_flood})",
                        f"Coastal Factor ({strata_coast} km)",
                        f"Postcode Factor ({strata_postcode})",
                        f"Claims Factor ({strata_claims} claims)",
                        f"Liability Limit Factor (AUD {liability_limit:,})",
                        "Office Bearers Liability",
                        f"Building Value Factor ({fmt_aud(building_insured)})",
                    ],
                    "Value": [
                        f"AUD {base_rate_per_unit * num_units:,.2f}", f"×{units_factor:.2f}",
                        f"×{building_age_factor:.2f}", f"×{construction_factor:.2f}",
                        f"×{high_rise_factor:.2f}", f"×{pool_factor:.2f}", f"×{gym_factor:.2f}",
                        f"×{lifts_factor:.2f}", f"×{parking_factor:.2f}", f"×{flood_factor:.2f}",
                        f"×{coastal_factor:.2f}", f"×{postcode_factor:.2f}", f"×{claims_factor:.2f}",
                        f"×{liability_factor:.2f}", f"×{office_factor:.2f}", f"×{building_value_factor:.2f}",
                    ],
                })
                st.table(bd)
                st.info(f"**Total Annual: {fmt_aud(total_annual)}** | Per Unit: {fmt_aud(per_unit)} | Monthly: {fmt_aud(monthly_total)}")

            if feat("pdf_quote") and PDF_OK:
                details = {
                    "Body Corporate": bc_name, "Postcode": strata_postcode,
                    "Units": num_units, "Building Type": building_type,
                    "Year Built": strata_year_built, "Construction": strata_construction,
                    "Building Value": fmt_aud(building_insured),
                    "Public Liability": fmt_aud(liability_limit),
                    "Flood Risk": strata_flood, "Bushfire Risk": strata_bushfire,
                }
                pdf_bytes = generate_pdf_quote("Strata Insurance", details, total_annual, monthly_total, "Strata Comprehensive")
                st.download_button(
                    label="📄 Download PDF Quote",
                    data=pdf_bytes,
                    file_name=f"strata_quote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

# ═════════════════════════════════════════════════════════════
# MODULE: CLAIMS TRACKER
# ═════════════════════════════════════════════════════════════
elif module == "Claims Tracker" and feat("claims_tracker"):
    st.markdown("## 📊 Claims Tracker")
    st.markdown("Track the status of your submitted claims in real time.")

    status_order = ["Lodged","Under Review","Approved","Paid"]
    status_css   = {"Lodged":"status-lodged","Under Review":"status-review","Approved":"status-approved","Paid":"status-paid"}

    search_claim = st.text_input("🔍 Search by Claim Number", placeholder="e.g. CLM-897655")

    claims_to_show = MOCK_CLAIMS
    if search_claim.strip():
        claims_to_show = [c for c in MOCK_CLAIMS if search_claim.strip().upper() in c["claim_no"].upper()]

    if not claims_to_show:
        st.info("No claims found matching your search.")
    else:
        for claim in claims_to_show:
            with st.container():
                st.markdown(f"### {claim['claim_no']} — {claim['type']}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Claim Amount", fmt_aud(claim["amount"]))
                c2.metric("Date Lodged", claim["date"])
                c3.metric("Status", claim["status"])
                c4.metric("Type", claim["type"])

                # Progress pipeline
                st.markdown("**Progress:**")
                prog_cols = st.columns(len(status_order))
                current_idx = status_order.index(claim["status"]) if claim["status"] in status_order else 0
                for i, status in enumerate(status_order):
                    with prog_cols[i]:
                        if i < current_idx:
                            st.markdown(f'<span class="status-pill status-paid">✅ {status}</span>', unsafe_allow_html=True)
                        elif i == current_idx:
                            css = status_css.get(status, "status-review")
                            st.markdown(f'<span class="status-pill {css}">▶ {status}</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<span class="status-pill" style="background:#f3f4f6;color:#9ca3af;">○ {status}</span>', unsafe_allow_html=True)

                st.caption(f"📝 {claim['desc']}")
                st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# MODULE: MY POLICIES
# ═════════════════════════════════════════════════════════════
elif module == "My Policies" and feat("policy_dashboard"):
    st.markdown("## 📁 My Policies")
    st.markdown("View and manage all your active insurance policies.")

    active   = [p for p in MOCK_POLICIES if p["status"] == "Active"]
    expired  = [p for p in MOCK_POLICIES if p["status"] == "Expired"]

    st.markdown(f"### Active Policies ({len(active)})")
    for pol in active:
        with st.container():
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Policy No.", pol["policy_no"])
            c2.metric("Annual Premium", fmt_aud(pol["annual"]))
            c3.metric("Expiry Date", pol["expiry"])
            c4.metric("Coverage", pol["coverage"])

            expiry_dt = datetime.strptime(pol["expiry"], "%Y-%m-%d").date()
            days_left = (expiry_dt - date.today()).days
            if days_left <= 30:
                st.warning(f"⚠️ Policy expires in **{days_left} days** — renew now to avoid a gap in cover.")
            elif days_left <= 60:
                st.info(f"ℹ️ Policy expires in {days_left} days.")
            else:
                st.success(f"✅ Active — {days_left} days remaining")

            if pol["type"] == "Car Insurance":
                st.caption(f"🚗 {pol['vehicle']} | {pol['type']}")
            else:
                st.caption(f"🏠 {pol['address']} | {pol['type']}")

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                if feat("pdf_quote") and PDF_OK:
                    cert_details = {"Policy No.": pol["policy_no"], "Type": pol["type"],
                                    "Coverage": pol["coverage"], "Start": pol["start"], "Expiry": pol["expiry"]}
                    cert_pdf = generate_pdf_quote(pol["type"], cert_details, pol["annual"], pol["annual"]/12, pol["coverage"])
                    st.download_button(f"📄 Certificate of Insurance", cert_pdf,
                                       file_name=f"certificate_{pol['policy_no']}.pdf",
                                       mime="application/pdf", key=f"cert_{pol['policy_no']}")
            with dl_col2:
                if st.button(f"🔄 Renew Policy", key=f"renew_{pol['policy_no']}"):
                    st.success(f"✅ Renewal initiated for {pol['policy_no']}. You'll receive a confirmation email shortly.")

            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    if expired:
        with st.expander(f"Expired Policies ({len(expired)})"):
            for pol in expired:
                st.markdown(f"**{pol['policy_no']}** — {pol['type']} | Expired: {pol['expiry']} | Premium was: {fmt_aud(pol['annual'])}")

# ═════════════════════════════════════════════════════════════
# MODULE: BUNDLE QUOTE
# ═════════════════════════════════════════════════════════════
elif module == "Bundle Quote" and feat("multi_asset_bundle"):
    st.markdown("## 📦 Bundle Quote — Car + Home")
    st.markdown("Combine your car and home insurance for a **10% bundle discount**.")

    st.info("💡 Bundle your Car and Home insurance together and save 10% on both premiums.")

    tab1, tab2 = st.tabs(["🚗 Car Details", "🏠 Home Details"])

    with tab1:
        bc1, bc2 = st.columns(2)
        with bc1:
            b_drv_name    = st.text_input("Driver Name *", value="Peter North", key="b_drv_name")
            b_drv_age     = st.number_input("Age *", min_value=16, max_value=100, value=35, key="b_age")
            b_drv_years   = st.number_input("Years Licensed *", min_value=0, max_value=80, value=10, key="b_yrs")
            b_postcode    = st.text_input("Postcode *", value="4217", key="b_post")
            b_accidents   = st.number_input("Accidents (5yr)", min_value=0, max_value=20, value=0, key="b_acc")
        with bc2:
            b_make  = st.text_input("Car Make *",  value="Toyota", key="b_make")
            b_model = st.text_input("Car Model *", value="Camry",  key="b_model")
            b_year  = st.number_input("Car Year *", min_value=1980, max_value=2026, value=2020, key="b_yr")
            b_value = st.number_input("Car Value (AUD) *", min_value=1000, max_value=500000, value=28500, step=500, key="b_val")
            b_cov   = st.selectbox("Car Coverage *", ["Comprehensive","Third Party Fire & Theft","Third Party"], key="b_cov")

    with tab2:
        bh1, bh2 = st.columns(2)
        with bh1:
            bh_postcode  = st.text_input("Home Postcode *", value="4217", key="bh_post")
            bh_type      = st.selectbox("Property Type *", ["House","Apartment","Townhouse","Villa"], key="bh_type")
            bh_bval      = st.number_input("Building Value (AUD) *", min_value=50000, max_value=5000000, value=500000, step=10000, key="bh_bval")
            bh_cval      = st.number_input("Contents Value (AUD) *", min_value=0, max_value=1000000, value=50000, step=1000, key="bh_cval")
        with bh2:
            bh_flood     = st.selectbox("Flood Risk *", ["Low","Medium","High"], key="bh_flood")
            bh_bushfire  = st.selectbox("Bushfire Risk *", ["Low","Medium","High"], key="bh_bush")
            bh_cov       = st.selectbox("Home Coverage Level *", ["Basic","Standard","Premium"], key="bh_cov")
            bh_construct = st.selectbox("Construction *", ["Brick","Timber","Mixed","Concrete"], key="bh_con")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    bundle_btn = st.button("⚡ Calculate Bundle Quote", use_container_width=True, key="bundle_calc")

    if bundle_btn:
        car_q  = calc_car_premium(b_drv_age, b_drv_years, b_accidents, 0, 0, False,
                                  b_postcode, b_year, b_value, "Personal", b_cov, 500)
        home_q = calc_home_premium("", bh_postcode, bh_type, 3, bh_bval, bh_cval,
                                   bh_construct, 2005, False, False,
                                   bh_flood, bh_bushfire, 2.5, bh_cov, 500, 0, [])
        car_annual  = car_q["annual"]
        home_annual = home_q["annual"]
        subtotal    = car_annual + home_annual
        discount    = subtotal * 0.10
        bundle_total = subtotal - discount

        st.markdown("### 💰 Bundle Quote Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Car Premium",    fmt_aud(car_annual))
        m2.metric("Home Premium",   fmt_aud(home_annual))
        m3.metric("10% Discount",   f"− {fmt_aud(discount)}")
        m4.metric("Bundle Total",   fmt_aud(bundle_total))

        st.success(f"🎉 You save **{fmt_aud(discount)}** per year by bundling! Total: **{fmt_aud(bundle_total)}/yr** ({fmt_aud(bundle_total/12)}/mo)")

        if feat("pdf_quote") and PDF_OK:
            details = {
                "Driver": b_drv_name, "Car": f"{b_year} {b_make} {b_model}",
                "Car Coverage": b_cov, "Car Premium": fmt_aud(car_annual),
                "Home Postcode": bh_postcode, "Home Coverage": bh_cov,
                "Home Premium": fmt_aud(home_annual),
                "Bundle Discount (10%)": f"− {fmt_aud(discount)}",
                "Bundle Total": fmt_aud(bundle_total),
            }
            pdf_bytes = generate_pdf_quote("Car + Home Bundle", details, bundle_total, bundle_total/12, "Bundle")
            st.download_button("📄 Download Bundle PDF Quote", pdf_bytes,
                               file_name=f"bundle_quote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                               mime="application/pdf", use_container_width=True)

# ═════════════════════════════════════════════════════════════
# MODULE: RISK MAP
# ═════════════════════════════════════════════════════════════
elif module == "Risk Map" and feat("postcode_heatmap"):
    st.markdown("## 🗺️ Australian Postcode Risk Map")
    st.markdown("Explore flood and bushfire risk levels across Australian postcodes.")

    risk_type = st.radio("Risk Type", ["Flood Risk","Bushfire Risk"], horizontal=True)

    map_data = []
    for pc, info in AU_POSTCODES_RISK.items():
        risk_val = info["flood"] if risk_type == "Flood Risk" else info["bushfire"]
        risk_num = {"Low":1,"Medium":2,"High":3}[risk_val]
        map_data.append({"Postcode": pc, "State": info["state"], "Risk Level": risk_val, "Risk Score": risk_num})

    df_map = pd.DataFrame(map_data)

    col1, col2 = st.columns([2,1])
    with col1:
        fig = px.bar(
            df_map.sort_values("Risk Score", ascending=False),
            x="Postcode", y="Risk Score", color="Risk Level",
            color_discrete_map={"Low":"#22c55e","Medium":"#f59e0b","High":"#ef4444"},
            title=f"{risk_type} by Postcode",
            labels={"Risk Score": "Risk Level (1=Low, 2=Med, 3=High)"},
        )
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Risk Summary")
        for level in ["High","Medium","Low"]:
            count = len(df_map[df_map["Risk Level"] == level])
            colour = {"High":"🔴","Medium":"🟡","Low":"🟢"}[level]
            st.metric(f"{colour} {level} Risk Postcodes", count)

    st.markdown("### Full Postcode Risk Table")
    st.dataframe(df_map[["Postcode","State","Risk Level"]].sort_values(["State","Postcode"]),
                 use_container_width=True, hide_index=True)

    st.info("💡 Enter your postcode in the Home or Strata quote modules to automatically apply the correct risk factors.")

# ═════════════════════════════════════════════════════════════
# MODULE: ADMIN DASHBOARD
# ═════════════════════════════════════════════════════════════
elif module == "Admin Dashboard" and feat("admin_dashboard"):
    st.markdown("## 📈 Admin Analytics Dashboard")

    pwd = st.text_input("Enter admin password", type="password", key="admin_pwd")
    ADMIN_PASSWORD = "admin2026"

    if pwd == ADMIN_PASSWORD:
        st.success("✅ Access granted")

        # KPI row
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Quotes (MTD)", "247", "+18%")
        k2.metric("Claims Lodged (MTD)", "34", "-5%")
        k3.metric("Avg Car Premium", "AUD 1,240", "+3%")
        k4.metric("Avg Home Premium", "AUD 2,180", "+7%")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Quote Volume by Module")
            fig_vol = px.pie(
                values=[112, 78, 43, 14],
                names=["Car Insurance","Home Insurance","Strata Insurance","Bundle"],
                color_discrete_sequence=["#2563eb","#1a4a8a","#60a5fa","#93c5fd"],
            )
            fig_vol.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_vol, use_container_width=True)

        with col2:
            st.markdown("#### Claims by Status")
            fig_status = px.bar(
                x=["Lodged","Under Review","Approved","Paid"],
                y=[8, 12, 9, 5],
                color=["Lodged","Under Review","Approved","Paid"],
                color_discrete_map={"Lodged":"#fbbf24","Under Review":"#60a5fa","Approved":"#34d399","Paid":"#a78bfa"},
            )
            fig_status.update_layout(height=300, showlegend=False,
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("#### Premium Trend (Last 6 Months)")
        months = ["Oct","Nov","Dec","Jan","Feb","Mar"]
        car_premiums  = [1180, 1205, 1190, 1220, 1235, 1240]
        home_premiums = [2050, 2080, 2110, 2140, 2165, 2180]
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=months, y=car_premiums,  mode='lines+markers', name='Car',  line=dict(color='#2563eb', width=2)))
        fig_trend.add_trace(go.Scatter(x=months, y=home_premiums, mode='lines+markers', name='Home', line=dict(color='#1a4a8a', width=2)))
        fig_trend.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                yaxis_title="Avg Premium (AUD)", legend=dict(orientation="h"))
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("#### Top Claim Types")
        claim_df = pd.DataFrame({
            "Claim Type": ["Hail Damage","Storm Roof","Cracked Windscreen","Water Damage","Flood Flooring","Front Bumper"],
            "Count": [18, 14, 11, 9, 7, 5],
            "Avg Amount (AUD)": [3200, 7500, 900, 5500, 12000, 1800],
        })
        st.dataframe(claim_df, use_container_width=True, hide_index=True)

    elif pwd:
        st.error("❌ Incorrect password.")
    else:
        st.info("Enter the admin password to access the analytics dashboard.")

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">© 2026 Fire &amp; General Insurance Portal · Australian General Insurance · '
    'ABN 00 000 000 000 · AFSL 000000 · This is a demonstration application only.</div>',
    unsafe_allow_html=True,
)
