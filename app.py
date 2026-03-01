import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Prop Risk Calculator",
    page_icon="📊",
    layout="centered"
)

# ---------------- THEME TOGGLE ----------------
theme = st.toggle("🌙 Dark Mode", value=True)

if theme:
    bg_color = "#0f172a"
    card_color = "#1e293b"
    text_color = "#f1f5f9"
    sub_text = "#94a3b8"
else:
    bg_color = "#f8fafc"
    card_color = "#ffffff"
    text_color = "#0f172a"
    sub_text = "#475569"

# ---------------- CUSTOM CSS ----------------
st.markdown(f"""
<style>
html, body, [class*="css"] {{
    background-color: {bg_color};
    color: {text_color};
}}

.block-container {{
    padding-top: 2rem;
}}

.metric-card {{
    background-color: {card_color};
    padding: 20px;
    border-radius: 14px;
    margin-top: 15px;
    color: {text_color};
    font-size: 16px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}}

.stButton>button {{
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
    border: none;
}}

.stButton>button:hover {{
    opacity: 0.9;
}}

.footer {{
    text-align: center;
    font-size: 12px;
    color: {sub_text};
    margin-top: 40px;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
START_EQUITY = 5000
PERSONAL_CAP = 100
ASSET_CAP_PERCENT = 0.03
FAIL_LEVEL = 4500
RISK_PER_TRADE = 30

ASSETS = {
    "BTCUSDT": {"type": "crypto", "lev": 2},
    "ETHUSDT": {"type": "crypto", "lev": 2},
    "SOLUSDT": {"type": "crypto", "lev": 2},
    "XRPUSDT": {"type": "crypto", "lev": 2},
    "XAUUSD": {"type": "gold", "lev": 30},
    "EURUSD": {"type": "forex", "lev": 50},
    "USDJPY": {"type": "forex", "lev": 50},
}

# ---------------- SESSION STATE ----------------
if "equity" not in st.session_state:
    st.session_state.equity = START_EQUITY
    st.session_state.personal_loss = 0
    st.session_state.asset_risk = {}

# ---------------- HEADER ----------------
st.title("📊 Prop Risk Calculator")
st.caption("Structured risk enforcement for funded accounts")

# ---------------- INPUT SECTION ----------------
st.markdown("### Trade Setup")

col1, col2 = st.columns(2)

with col1:
    asset = st.selectbox("Asset", list(ASSETS.keys()))
    price = st.number_input("Current Price", min_value=0.0)

with col2:
    sl = st.number_input("Stop Distance", min_value=0.0)
    equity_input = st.number_input("Current Equity", value=st.session_state.equity)

# ---------------- CALCULATE POSITION ----------------
if st.button("Calculate Position"):

    if sl > 0 and price > 0:
        config = ASSETS[asset]
        lev = config["lev"]
        a_type = config["type"]

        if a_type == "crypto":
            size = RISK_PER_TRADE / sl
            trade_value = size * price
            unit = f"{size:.6f} {asset.replace('USDT','')}"
        elif a_type == "gold":
            size = RISK_PER_TRADE / (sl * 100)
            trade_value = size * 100 * price
            unit = f"{size:.3f} lots"
        else:
            size = RISK_PER_TRADE / (sl * 100000)
            trade_value = size * 100000 * price
            unit = f"{size:.3f} lots"

        margin = trade_value / lev

        st.markdown(f"""
        <div class="metric-card">
        <b>Trade Value:</b> ${trade_value:,.0f}<br>
        <b>Margin Required:</b> ${margin:,.0f}<br>
        <b>Position Size:</b> {unit}
        </div>
        """, unsafe_allow_html=True)

# ---------------- UPDATE EQUITY ----------------
if st.button("Update Equity"):

    change = equity_input - st.session_state.equity

    if change < 0:
        loss = abs(change)
        st.session_state.personal_loss += loss
        st.session_state.asset_risk[asset] = st.session_state.asset_risk.get(asset, 0) + loss

    st.session_state.equity = equity_input

# ---------------- ACCOUNT STATUS ----------------
st.markdown("### 📈 Account Status")

asset_cap = START_EQUITY * ASSET_CAP_PERCENT
asset_loss = st.session_state.asset_risk.get(asset, 0)
profit = st.session_state.equity - START_EQUITY

colA, colB = st.columns(2)

with colA:
    st.markdown(f"""
    <div class="metric-card">
    <b>Equity:</b> ${st.session_state.equity:,.0f}<br>
    <b>Net Profit:</b> ${profit:+,.0f}
    </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown(f"""
    <div class="metric-card">
    <b>Personal Loss:</b> ${st.session_state.personal_loss} / ${PERSONAL_CAP}<br>
    <b>{asset} Loss Used:</b> ${asset_loss} / ${asset_cap}
    </div>
    """, unsafe_allow_html=True)

if st.session_state.equity <= FAIL_LEVEL:
    st.error("⚠ Account Failure Level Reached")

# ---------------- FOOTER ----------------
st.markdown(
    "<div class='footer'>Developed by Roheet Purkayastha</div>",
    unsafe_allow_html=True
)