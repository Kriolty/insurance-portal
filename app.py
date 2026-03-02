import streamlit as st
import random
import string
import time
from datetime import date, datetime
from PIL import Image
import io

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fire & General Insurance Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2b55 0%, #1a4a8a 100%);
        border-right: 1px solid #1e3a6e;
    }
    [data-testid="stSidebar"] * {
        color: #e8f0fe !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
        padding: 6px 0;
    }
    [data-testid="stSidebar"] hr {
        border-color: #2d5a9e !important;
    }

    /* ── Main header ── */
    .main-header {
        background: linear-gradient(135deg, #0d2b55 0%, #1a4a8a 50%, #2563eb 100%);
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(13,43,85,0.35);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 0.4rem 0 0;
        font-size: 1rem;
        opacity: 0.88;
    }

    /* ── Section headers ── */
    .section-header {
        background: #f0f4ff;
        border-left: 4px solid #2563eb;
        padding: 0.6rem 1rem;
        border-radius: 0 6px 6px 0;
        margin: 1.5rem 0 1rem;
        font-weight: 600;
        font-size: 0.95rem;
        color: #0d2b55;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f0f7ff 0%, #e8f0fe 100%);
        border: 1px solid #c7d9f8;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(37,99,235,0.08);
    }
    [data-testid="stMetricValue"] {
        color: #0d2b55 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #4b6a9b !important;
        font-weight: 500 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #1a4a8a 0%, #2563eb 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.55rem 1.8rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(37,99,235,0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0d2b55 0%, #1a4a8a 100%);
        box-shadow: 0 4px 14px rgba(37,99,235,0.4);
        transform: translateY(-1px);
    }

    /* ── Input fields ── */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border-radius: 7px !important;
        border: 1px solid #c7d9f8 !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
    }

    /* ── Success / info boxes ── */
    .stSuccess {
        border-radius: 8px;
    }
    .stInfo {
        border-radius: 8px;
    }

    /* ── Claim number badge ── */
    .claim-badge {
        background: linear-gradient(135deg, #0d2b55, #2563eb);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
        margin: 0.5rem 0;
    }

    /* ── Divider ── */
    .custom-divider {
        border: none;
        border-top: 2px solid #e2eaf8;
        margin: 1.5rem 0;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        color: #8fa3c0;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e2eaf8;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────────────────────────
VEHICLE_DB = {
    # QLD
    "ABC123": {"make": "Toyota",    "model": "Camry",         "year": 2020, "value": 28500},
    "XYZ789": {"make": "Mazda",     "model": "CX-5",          "year": 2019, "value": 32000},
    "DEF456": {"make": "Honda",     "model": "Civic",         "year": 2021, "value": 26800},
    "GHI789": {"make": "Holden",    "model": "Commodore",     "year": 2018, "value": 22000},
    "JKL012": {"make": "Hyundai",   "model": "i30",           "year": 2020, "value": 24500},
    "MNO345": {"make": "Ford",      "model": "Ranger",        "year": 2021, "value": 48000},
    "PQR678": {"make": "Subaru",    "model": "Outback",       "year": 2019, "value": 35500},
    "STU901": {"make": "Nissan",    "model": "X-Trail",       "year": 2020, "value": 31200},
    "VWX234": {"make": "Kia",       "model": "Sportage",      "year": 2022, "value": 37800},
    "YZA567": {"make": "Mitsubishi","model": "Outlander",     "year": 2021, "value": 41000},
    "BCD890": {"make": "Volkswagen","model": "Golf",          "year": 2020, "value": 33500},
    "EFG123": {"make": "Toyota",    "model": "HiLux",         "year": 2022, "value": 52000},
    "HIJ456": {"make": "Isuzu",     "model": "D-Max",         "year": 2021, "value": 49500},
    "KLM789": {"make": "Mercedes",  "model": "C-Class",       "year": 2020, "value": 68000},
    "NOP012": {"make": "BMW",       "model": "3 Series",      "year": 2021, "value": 72000},
    # NSW
    "BT12AB": {"make": "Hyundai",   "model": "Tucson",        "year": 2022, "value": 39000},
    "CU34CD": {"make": "Toyota",    "model": "RAV4",          "year": 2021, "value": 44500},
    "DV56EF": {"make": "Mazda",     "model": "3",             "year": 2020, "value": 27000},
    "EW78GH": {"make": "Honda",     "model": "HR-V",          "year": 2019, "value": 28500},
    "FX90IJ": {"make": "Kia",       "model": "Cerato",        "year": 2021, "value": 26000},
    "GY12KL": {"make": "Subaru",    "model": "Forester",      "year": 2020, "value": 38000},
    "HZ34MN": {"make": "Nissan",    "model": "Navara",        "year": 2021, "value": 47000},
    # VIC
    "1AB2CD": {"make": "Toyota",    "model": "Corolla",       "year": 2021, "value": 29500},
    "3EF4GH": {"make": "Mazda",     "model": "CX-9",          "year": 2020, "value": 52000},
    "5IJ6KL": {"make": "Ford",      "model": "Escape",        "year": 2019, "value": 31000},
    "7MN8OP": {"make": "Holden",    "model": "Colorado",      "year": 2018, "value": 36000},
    "2QR3ST": {"make": "Volkswagen","model": "Tiguan",        "year": 2022, "value": 48500},
    "4UV5WX": {"make": "Audi",      "model": "A3",            "year": 2021, "value": 55000},
    "6YZ7AB": {"make": "BMW",       "model": "X3",            "year": 2020, "value": 78000},
    "8CD9EF": {"make": "Lexus",     "model": "RX",            "year": 2021, "value": 82000},
    "9GH0IJ": {"make": "Tesla",     "model": "Model 3",       "year": 2022, "value": 65000},
}

CAR_DAMAGE_TYPES = [
    "Front bumper dent",
    "Rear scratch",
    "Hail damage to roof",
    "Side panel scratch",
    "Cracked windscreen",
    "Door ding",
]

HOME_DAMAGE_TYPES = [
    "Water damage to ceiling",
    "Broken window",
    "Storm damage to roof tiles",
    "Flood damage to flooring",
    "Fire damage to kitchen",
    "Wall crack",
    "Fence damage",
]

CAR_REPAIR_COSTS = {
    "Front bumper dent": (800, 2500),
    "Rear scratch": (400, 1200),
    "Hail damage to roof": (1500, 5000),
    "Side panel scratch": (350, 1100),
    "Cracked windscreen": (600, 1800),
    "Door ding": (250, 900),
}

HOME_REPAIR_COSTS = {
    "Water damage to ceiling": (2000, 8000),
    "Broken window": (300, 1200),
    "Storm damage to roof tiles": (3000, 12000),
    "Flood damage to flooring": (5000, 20000),
    "Fire damage to kitchen": (8000, 35000),
    "Wall crack": (500, 3000),
    "Fence damage": (800, 4000),
}

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def fmt_aud(amount: float) -> str:
    return f"AUD {amount:,.2f}"

def gen_claim_number() -> str:
    return "CLM-" + "".join(random.choices(string.digits, k=6))

def detect_damage(claim_type: str) -> tuple[str, float]:
    if claim_type == "Car Damage":
        damage = random.choice(CAR_DAMAGE_TYPES)
        lo, hi = CAR_REPAIR_COSTS[damage]
    else:
        damage = random.choice(HOME_DAMAGE_TYPES)
        lo, hi = HOME_REPAIR_COSTS[damage]
    cost = round(random.uniform(lo, hi), 2)
    return damage, cost

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ Insurance Portal")
    st.markdown("---")
    module = st.radio(
        "Select Module",
        options=["Damage Claims", "Car Insurance Quote", "Home Insurance Quote", "Strata Insurance Quote"],
        label_visibility="collapsed",
    )
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
# MODULE 1 – DAMAGE CLAIMS
# ═════════════════════════════════════════════════════════════
if module == "Damage Claims":
    st.markdown("## 📋 Damage Claims")
    st.markdown("Upload photos of the damage to automatically detect and pre-fill your claim form.")

    col_upload, col_form = st.columns([1, 1.6], gap="large")

    with col_upload:
        st.markdown('<div class="section-header">📸 Upload Damage Photos</div>', unsafe_allow_html=True)
        claim_type = st.selectbox("Claim Type", ["Car Damage", "Home Damage"])
        uploaded_files = st.file_uploader(
            "Upload damage photos (JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            for uf in uploaded_files[:3]:
                img = Image.open(uf)
                st.image(img, caption=uf.name, use_container_width=True)

        analyze_btn = st.button("🔍 Analyse Damage", use_container_width=True)

    with col_form:
        st.markdown('<div class="section-header">📝 Claim Form</div>', unsafe_allow_html=True)

        # Session state for auto-fill
        if "claim_damage" not in st.session_state:
            st.session_state.claim_damage = ""
            st.session_state.claim_cost = 0.0
            st.session_state.claim_number = gen_claim_number()

        if analyze_btn:
            if not uploaded_files:
                st.warning("⚠️ Please upload at least one damage photo before analysing.")
            else:
                with st.spinner("🤖 Analysing damage with AI vision..."):
                    time.sleep(1.5)
                damage, cost = detect_damage(claim_type)
                st.session_state.claim_damage = damage
                st.session_state.claim_cost = cost
                st.session_state.claim_number = gen_claim_number()
                st.success(f"✅ Damage detected: **{damage}** — Estimated repair cost: **{fmt_aud(cost)}**")

        with st.form("claim_form"):
            claim_number = st.text_input("Claim Number", value=st.session_state.claim_number, disabled=True)
            claimant_name = st.text_input("Claimant Name *", value="Peter North")
            claim_date = st.date_input("Claim Date", value=date.today())
            postcode = st.text_input("Postcode *", value="4217")
            damage_desc = st.text_area(
                "Damage Description *",
                value=st.session_state.claim_damage,
                height=100,
                placeholder="Describe the damage in detail...",
            )
            repair_cost = st.number_input(
                "Estimated Repair Cost (AUD) *",
                min_value=0.0,
                value=float(st.session_state.claim_cost),
                step=100.0,
                format="%.2f",
            )

            submitted = st.form_submit_button("📤 Submit Claim", use_container_width=True)

        if submitted:
            errors = []
            if not claimant_name.strip():
                errors.append("Claimant Name is required.")
            if not postcode.strip():
                errors.append("Postcode is required.")
            if not damage_desc.strip():
                errors.append("Damage Description is required.")
            if repair_cost <= 0:
                errors.append("Estimated Repair Cost must be greater than zero.")

            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                st.balloons()
                st.success(f"✅ Claim submitted successfully!")
                st.markdown(
                    f'<div class="claim-badge">🎫 {claim_number}</div>',
                    unsafe_allow_html=True,
                )
                st.info(
                    f"Your claim **{claim_number}** has been lodged on **{claim_date.strftime('%d %B %Y')}**. "
                    f"A claims assessor will contact **{claimant_name}** within 2 business days. "
                    f"Estimated repair cost: **{fmt_aud(repair_cost)}**."
                )
                # Reset for next claim
                st.session_state.claim_number = gen_claim_number()
                st.session_state.claim_damage = ""
                st.session_state.claim_cost = 0.0


# ═════════════════════════════════════════════════════════════
# MODULE 2 – CAR INSURANCE QUOTE
# ═════════════════════════════════════════════════════════════
elif module == "Car Insurance Quote":
    st.markdown("## 🚗 Car Insurance Quote")
    st.markdown("Get an instant comprehensive car insurance quote tailored to your vehicle and driving history.")

    # ── Plate Lookup ──
    st.markdown('<div class="section-header">🔍 Vehicle Lookup</div>', unsafe_allow_html=True)
    lk_col1, lk_col2, lk_col3 = st.columns([2, 1, 3])
    with lk_col1:
        plate_input = st.text_input(
            "Enter Number Plate",
            placeholder="e.g. ABC123",
            max_chars=7,
            label_visibility="collapsed",
        ).upper()
    with lk_col2:
        lookup_btn = st.button("🔍 Lookup Vehicle", use_container_width=True)
    with lk_col3:
        st.caption("Powered by Australian vehicle registry")

    # Session state for vehicle data
    if "car_make" not in st.session_state:
        st.session_state.car_make = "Toyota"
        st.session_state.car_model = "Camry"
        st.session_state.car_year = 2020
        st.session_state.car_value = 25000

    if lookup_btn:
        if not plate_input.strip():
            st.warning("⚠️ Please enter a number plate.")
        else:
            with st.spinner("Searching Australian vehicle database..."):
                time.sleep(random.uniform(1.0, 1.8))
            if plate_input in VEHICLE_DB:
                v = VEHICLE_DB[plate_input]
                st.session_state.car_make = v["make"]
                st.session_state.car_model = v["model"]
                st.session_state.car_year = v["year"]
                st.session_state.car_value = v["value"]
                st.success(f"✅ Vehicle found! Details auto-filled — **{v['year']} {v['make']} {v['model']}** (Value: {fmt_aud(v['value'])})")
            else:
                st.info("ℹ️ Plate not found in database — please enter details manually.")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="section-header">👤 Driver Details</div>', unsafe_allow_html=True)
        drv_name = st.text_input("Full Name *", value="Peter North", key="drv_name")
        drv_age = st.number_input("Age *", min_value=18, max_value=100, value=35, key="drv_age")
        drv_years = st.number_input("Years Licensed *", min_value=0, max_value=50, value=10, key="drv_years")
        drv_postcode = st.text_input("Postcode *", value="4217", key="drv_postcode")

        st.markdown('<div class="section-header">🚦 Driving History</div>', unsafe_allow_html=True)
        accidents = st.number_input("Accidents (last 5 years)", min_value=0, max_value=10, value=0)
        claims_hist = st.number_input("Claims (last 5 years)", min_value=0, max_value=10, value=0)
        fines = st.number_input("Speeding Fines (last 3 years)", min_value=0, max_value=20, value=0)
        suspended = st.checkbox("Licence previously suspended")

    with col2:
        st.markdown('<div class="section-header">🚘 Vehicle Details</div>', unsafe_allow_html=True)
        car_make = st.text_input("Make *", value=st.session_state.car_make, key="car_make_input")
        car_model = st.text_input("Model *", value=st.session_state.car_model, key="car_model_input")
        car_year = st.number_input("Year *", min_value=1980, max_value=2027, value=st.session_state.car_year, key="car_year_input")
        car_value = st.number_input("Vehicle Value (AUD) *", min_value=1000, max_value=500000,
                                    value=st.session_state.car_value, step=500, key="car_value_input")
        car_use = st.selectbox("Primary Use *", ["Personal", "Business", "Rideshare"])

        st.markdown('<div class="section-header">🛡️ Coverage</div>', unsafe_allow_html=True)
        coverage = st.selectbox("Coverage Type *", ["Comprehensive", "Third Party Fire & Theft", "Third Party Only"])
        excess = st.selectbox("Excess Amount (AUD) *", [500, 750, 1000, 1500, 2000])

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    calc_btn = st.button("⚡ Calculate Premium", use_container_width=True, key="car_calc")

    if calc_btn:
        errors = []
        if not drv_name.strip():
            errors.append("Full Name is required.")
        if not drv_postcode.strip():
            errors.append("Postcode is required.")
        if not car_make.strip():
            errors.append("Vehicle Make is required.")
        if not car_model.strip():
            errors.append("Vehicle Model is required.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            # ── Calculation ──
            base_rate = 850
            age_factor = 1.4 if drv_age < 25 else (1.0 if drv_age < 65 else 1.15)
            experience_factor = 1.25 if drv_years < 3 else 1.0
            history_factor = 1 + (accidents * 0.35) + (claims_hist * 0.3) + (fines * 0.12)
            suspension_factor = 1.5 if suspended else 1.0
            postcode_factor = 1.15 if drv_postcode in ["4215", "4220", "4221"] else 1.05
            vehicle_age_factor = 1.0 if car_year >= 2018 else 1.1
            vehicle_value_factor = car_value / 25000
            usage_map = {"Personal": 1.0, "Business": 1.3, "Rideshare": 1.6}
            usage_factor = usage_map[car_use]
            coverage_map = {"Comprehensive": 1.0, "Third Party Fire & Theft": 0.55, "Third Party Only": 0.35}
            coverage_factor = coverage_map[coverage]
            excess_factor = 1 - ((excess - 500) / 5000)

            annual = (base_rate * age_factor * experience_factor * history_factor *
                      suspension_factor * postcode_factor * vehicle_age_factor *
                      vehicle_value_factor * usage_factor * coverage_factor * excess_factor)
            monthly = annual / 12

            st.markdown("---")
            st.markdown("### 💰 Your Quote")
            m1, m2, m3 = st.columns(3)
            m1.metric("Annual Premium", fmt_aud(annual))
            m2.metric("Monthly Premium", fmt_aud(monthly))
            m3.metric("Coverage Type", coverage)

            with st.expander("📊 Quote Breakdown — All Risk Factors"):
                breakdown_data = {
                    "Factor": [
                        "Base Rate",
                        f"Age Factor (age {drv_age})",
                        f"Experience Factor ({drv_years} yrs licensed)",
                        f"History Factor ({accidents} accidents, {claims_hist} claims, {fines} fines)",
                        f"Suspension Factor",
                        f"Postcode Factor ({drv_postcode})",
                        f"Vehicle Age Factor ({car_year})",
                        f"Vehicle Value Factor ({fmt_aud(car_value)})",
                        f"Usage Factor ({car_use})",
                        f"Coverage Factor ({coverage})",
                        f"Excess Discount (AUD {excess})",
                    ],
                    "Multiplier": [
                        f"AUD {base_rate:,.2f}",
                        f"×{age_factor:.2f}",
                        f"×{experience_factor:.2f}",
                        f"×{history_factor:.2f}",
                        f"×{suspension_factor:.2f}",
                        f"×{postcode_factor:.2f}",
                        f"×{vehicle_age_factor:.2f}",
                        f"×{vehicle_value_factor:.2f}",
                        f"×{usage_factor:.2f}",
                        f"×{coverage_factor:.2f}",
                        f"×{excess_factor:.2f}",
                    ],
                }
                import pandas as pd
                st.table(pd.DataFrame(breakdown_data))
                st.info(f"**Final Annual Premium: {fmt_aud(annual)}** | Monthly: {fmt_aud(monthly)}")


# ═════════════════════════════════════════════════════════════
# MODULE 3 – HOME INSURANCE QUOTE
# ═════════════════════════════════════════════════════════════
elif module == "Home Insurance Quote":
    st.markdown("## 🏠 Home Insurance Quote")
    st.markdown("Calculate your home and contents insurance premium based on your property details and location risk.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="section-header">🏡 Property Details</div>', unsafe_allow_html=True)
        owner_name = st.text_input("Owner Name *", value="Peter North")
        home_postcode = st.text_input("Postcode *", value="4217")
        prop_type = st.selectbox("Property Type *", ["House", "Apartment", "Townhouse", "Villa"])
        bedrooms = st.number_input("Bedrooms *", min_value=1, max_value=10, value=3)
        building_value = st.number_input("Building Value (AUD) *", min_value=50000, max_value=5000000,
                                         value=500000, step=10000)
        contents_value = st.number_input("Contents Value (AUD) *", min_value=0, max_value=1000000,
                                         value=50000, step=1000)

        st.markdown('<div class="section-header">🏗️ Property Features</div>', unsafe_allow_html=True)
        construction = st.selectbox("Construction Type *", ["Brick", "Timber", "Mixed", "Concrete"])
        year_built = st.number_input("Year Built *", min_value=1900, max_value=2027, value=2010)
        has_pool = st.checkbox("Swimming Pool")
        has_alarm = st.checkbox("Security Alarm")

    with col2:
        st.markdown('<div class="section-header">📍 Location & Risk</div>', unsafe_allow_html=True)
        flood_risk = st.selectbox("Flood Risk Zone *", ["Low", "Medium", "High"])
        bushfire_risk = st.selectbox("Bushfire Risk Zone *", ["Low", "Medium", "High"])
        coast_dist = st.number_input("Distance to Coast (km) *", min_value=0.0, max_value=100.0,
                                     value=2.5, step=0.5, format="%.1f")

        st.markdown('<div class="section-header">🛡️ Coverage Options</div>', unsafe_allow_html=True)
        coverage_level = st.selectbox("Coverage Level *", ["Basic", "Standard", "Premium"])
        home_excess = st.selectbox("Excess (AUD) *", [500, 1000, 2000, 5000])

        st.markdown('<div class="section-header">📋 Claims History</div>', unsafe_allow_html=True)
        home_claims = st.number_input("Claims (last 5 years)", min_value=0, max_value=10, value=0)
        prev_claim_types = st.multiselect(
            "Previous Claim Types",
            ["Storm", "Flood", "Fire", "Theft", "Water Damage"],
        )

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    home_calc_btn = st.button("⚡ Calculate Premium", use_container_width=True, key="home_calc")

    if home_calc_btn:
        errors = []
        if not owner_name.strip():
            errors.append("Owner Name is required.")
        if not home_postcode.strip():
            errors.append("Postcode is required.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            base_rate = 1200
            building_factor = building_value / 500000
            contents_factor = contents_value / 50000 if contents_value > 0 else 0
            prop_type_map = {"House": 1.0, "Apartment": 0.8, "Townhouse": 0.9, "Villa": 0.95}
            property_type_factor = prop_type_map[prop_type]
            construction_map = {"Brick": 1.0, "Concrete": 0.95, "Mixed": 1.1, "Timber": 1.25}
            construction_factor = construction_map[construction]
            age_factor = 1.0 if year_built >= 2000 else (1.15 if year_built >= 1980 else 1.3)
            flood_map = {"Low": 1.0, "Medium": 1.3, "High": 1.8}
            flood_factor = flood_map[flood_risk]
            bushfire_map = {"Low": 1.0, "Medium": 1.25, "High": 1.6}
            bushfire_factor = bushfire_map[bushfire_risk]
            coastal_factor = 1.3 if coast_dist < 1 else (1.15 if coast_dist < 5 else 1.0)
            postcode_factor = 1.2 if home_postcode in ["4217", "4218", "4220"] else 1.0
            pool_factor = 1.1 if has_pool else 1.0
            alarm_discount = 0.9 if has_alarm else 1.0
            coverage_map = {"Basic": 0.7, "Standard": 1.0, "Premium": 1.4}
            coverage_factor = coverage_map[coverage_level]
            excess_discount = 1 - ((home_excess - 500) / 10000)
            claims_factor = 1 + (home_claims * 0.25) + (len(prev_claim_types) * 0.15)

            # Building + contents combined
            building_premium = (base_rate * building_factor * property_type_factor *
                                 construction_factor * age_factor * flood_factor *
                                 bushfire_factor * coastal_factor * postcode_factor *
                                 pool_factor * alarm_discount * coverage_factor *
                                 excess_discount * claims_factor)
            contents_premium = (base_rate * 0.3 * contents_factor * flood_factor *
                                 bushfire_factor * coverage_factor * excess_discount *
                                 claims_factor) if contents_value > 0 else 0
            annual = building_premium + contents_premium
            monthly = annual / 12

            st.markdown("---")
            st.markdown("### 💰 Your Quote")
            m1, m2, m3 = st.columns(3)
            m1.metric("Annual Premium", fmt_aud(annual))
            m2.metric("Monthly Premium", fmt_aud(monthly))
            m3.metric("Coverage Level", coverage_level)

            with st.expander("📊 Quote Breakdown — All Risk Factors"):
                breakdown_data = {
                    "Factor": [
                        "Base Rate",
                        f"Building Value Factor ({fmt_aud(building_value)})",
                        f"Contents Value Factor ({fmt_aud(contents_value)})",
                        f"Property Type Factor ({prop_type})",
                        f"Construction Factor ({construction})",
                        f"Building Age Factor (built {year_built})",
                        f"Flood Risk Factor ({flood_risk})",
                        f"Bushfire Risk Factor ({bushfire_risk})",
                        f"Coastal Factor ({coast_dist} km)",
                        f"Postcode Factor ({home_postcode})",
                        f"Pool Factor",
                        f"Security Alarm Discount",
                        f"Coverage Factor ({coverage_level})",
                        f"Excess Discount (AUD {home_excess})",
                        f"Claims Factor ({home_claims} claims, {len(prev_claim_types)} types)",
                    ],
                    "Value": [
                        f"AUD {base_rate:,.2f}",
                        f"×{building_factor:.2f}",
                        f"×{contents_factor:.2f}",
                        f"×{property_type_factor:.2f}",
                        f"×{construction_factor:.2f}",
                        f"×{age_factor:.2f}",
                        f"×{flood_factor:.2f}",
                        f"×{bushfire_factor:.2f}",
                        f"×{coastal_factor:.2f}",
                        f"×{postcode_factor:.2f}",
                        f"×{pool_factor:.2f}",
                        f"×{alarm_discount:.2f}",
                        f"×{coverage_factor:.2f}",
                        f"×{excess_discount:.2f}",
                        f"×{claims_factor:.2f}",
                    ],
                }
                import pandas as pd
                st.table(pd.DataFrame(breakdown_data))
                st.info(
                    f"Building Premium: **{fmt_aud(building_premium)}** | "
                    f"Contents Premium: **{fmt_aud(contents_premium)}** | "
                    f"**Total Annual: {fmt_aud(annual)}**"
                )


# ═════════════════════════════════════════════════════════════
# MODULE 4 – STRATA INSURANCE QUOTE
# ═════════════════════════════════════════════════════════════
elif module == "Strata Insurance Quote":
    st.markdown("## 🏢 Strata Insurance Quote")
    st.markdown("Calculate body corporate insurance premiums for strata-titled properties across Australia.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="section-header">🏢 Body Corporate Details</div>', unsafe_allow_html=True)
        bc_name = st.text_input("Body Corporate Name *", placeholder="e.g. Sunrise Residences BC")
        strata_postcode = st.text_input("Postcode *", value="4217")
        strata_manager = st.text_input("Strata Manager (optional)", placeholder="e.g. Smith Strata Pty Ltd")

        st.markdown('<div class="section-header">🏗️ Building Details</div>', unsafe_allow_html=True)
        num_units = st.number_input("Number of Units/Lots *", min_value=1, max_value=500, value=24)
        building_type = st.selectbox("Building Type *", ["Low-rise", "High-rise"])
        strata_year_built = st.number_input("Year Built *", min_value=1900, max_value=2027, value=2005)
        strata_construction = st.selectbox("Construction Type *", ["Brick", "Concrete", "Mixed"])

        st.markdown('<div class="section-header">🏊 Facilities</div>', unsafe_allow_html=True)
        strata_pool = st.checkbox("Swimming Pool")
        strata_gym = st.checkbox("Gym")
        strata_lifts = st.checkbox("Lifts / Elevators")
        parking_levels = st.number_input("Number of Parking Levels", min_value=0, max_value=10, value=1)

    with col2:
        st.markdown('<div class="section-header">🛡️ Coverage & Risk</div>', unsafe_allow_html=True)
        building_insured = st.number_input("Building Insurance Value (AUD) *", min_value=500000,
                                           max_value=500000000, value=5000000, step=100000)
        liability_limit = st.selectbox("Public Liability Limit (AUD) *",
                                       [10000000, 20000000, 30000000],
                                       format_func=lambda x: f"AUD {x:,}")
        office_bearers = st.checkbox("Office Bearers Liability", value=True)

        st.markdown('<div class="section-header">📍 Location Risks</div>', unsafe_allow_html=True)
        strata_flood = st.selectbox("Flood Risk Zone *", ["Low", "Medium", "High"])
        strata_bushfire = st.selectbox("Bushfire Risk Zone *", ["Low", "Medium", "High"])
        strata_coast = st.number_input("Distance to Coast (km) *", min_value=0.0, max_value=100.0,
                                       value=2.5, step=0.5, format="%.1f")

        st.markdown('<div class="section-header">📋 Claims History</div>', unsafe_allow_html=True)
        strata_claims = st.number_input("Claims (last 5 years)", min_value=0, max_value=10, value=0)
        strata_claim_types = st.multiselect(
            "Claim Types",
            ["Storm", "Flood", "Fire", "Liability", "Property Damage"],
        )

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    strata_calc_btn = st.button("⚡ Calculate Premium", use_container_width=True, key="strata_calc")

    if strata_calc_btn:
        errors = []
        if not bc_name.strip():
            errors.append("Body Corporate Name is required.")
        if not strata_postcode.strip():
            errors.append("Postcode is required.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            base_rate_per_unit = 150
            units_factor = num_units / 50
            building_age_factor = 1.0 if strata_year_built >= 2000 else (1.2 if strata_year_built >= 1980 else 1.4)
            strata_construction_map = {"Brick": 1.0, "Concrete": 0.95, "Mixed": 1.1}
            construction_factor = strata_construction_map[strata_construction]
            high_rise_factor = 1.3 if building_type == "High-rise" else 1.0
            pool_factor = 1.15 if strata_pool else 1.0
            gym_factor = 1.1 if strata_gym else 1.0
            lifts_factor = 1.2 if strata_lifts else 1.0
            parking_factor = 1 + (parking_levels * 0.05)
            flood_map = {"Low": 1.0, "Medium": 1.25, "High": 1.6}
            flood_factor = flood_map[strata_flood]
            coastal_factor = 1.2 if strata_coast < 1 else (1.1 if strata_coast < 5 else 1.0)
            postcode_factor = 1.15 if strata_postcode in ["4217", "4218", "4220"] else 1.0
            claims_factor = 1 + (strata_claims * 0.2)
            liability_factor = 1.0 + (liability_limit / 10000000 - 1) * 0.08
            office_factor = 1.12 if office_bearers else 1.0
            building_value_factor = building_insured / 5000000

            total_annual = (base_rate_per_unit * num_units * units_factor * building_age_factor *
                            construction_factor * high_rise_factor * pool_factor * gym_factor *
                            lifts_factor * parking_factor * flood_factor * coastal_factor *
                            postcode_factor * claims_factor * liability_factor * office_factor *
                            building_value_factor)
            per_unit = total_annual / num_units
            monthly_total = total_annual / 12

            st.markdown("---")
            st.markdown("### 💰 Your Quote")
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Annual Premium", fmt_aud(total_annual))
            m2.metric("Per Unit (Annual)", fmt_aud(per_unit))
            m3.metric("Monthly Total", fmt_aud(monthly_total))

            with st.expander("📊 Quote Breakdown — All Risk Factors"):
                breakdown_data = {
                    "Factor": [
                        f"Base Rate per Unit × {num_units} units",
                        f"Units Scale Factor ({num_units} units / 50)",
                        f"Building Age Factor (built {strata_year_built})",
                        f"Construction Factor ({strata_construction})",
                        f"Building Type Factor ({building_type})",
                        f"Swimming Pool Factor",
                        f"Gym Factor",
                        f"Lifts/Elevators Factor",
                        f"Parking Factor ({parking_levels} levels)",
                        f"Flood Risk Factor ({strata_flood})",
                        f"Coastal Factor ({strata_coast} km)",
                        f"Postcode Factor ({strata_postcode})",
                        f"Claims Factor ({strata_claims} claims)",
                        f"Liability Limit Factor (AUD {liability_limit:,})",
                        f"Office Bearers Liability",
                        f"Building Value Factor ({fmt_aud(building_insured)})",
                    ],
                    "Value": [
                        f"AUD {base_rate_per_unit * num_units:,.2f}",
                        f"×{units_factor:.2f}",
                        f"×{building_age_factor:.2f}",
                        f"×{construction_factor:.2f}",
                        f"×{high_rise_factor:.2f}",
                        f"×{pool_factor:.2f}",
                        f"×{gym_factor:.2f}",
                        f"×{lifts_factor:.2f}",
                        f"×{parking_factor:.2f}",
                        f"×{flood_factor:.2f}",
                        f"×{coastal_factor:.2f}",
                        f"×{postcode_factor:.2f}",
                        f"×{claims_factor:.2f}",
                        f"×{liability_factor:.2f}",
                        f"×{office_factor:.2f}",
                        f"×{building_value_factor:.2f}",
                    ],
                }
                import pandas as pd
                st.table(pd.DataFrame(breakdown_data))
                st.info(
                    f"**Total Annual Premium: {fmt_aud(total_annual)}** | "
                    f"Per Unit: {fmt_aud(per_unit)} | "
                    f"Monthly Total: {fmt_aud(monthly_total)}"
                )

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">© 2026 Fire &amp; General Insurance Portal · Australian General Insurance · '
    'ABN 00 000 000 000 · AFSL 000000 · This is a demonstration application only.</div>',
    unsafe_allow_html=True,
)
