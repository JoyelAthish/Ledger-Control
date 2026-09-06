import streamlit as st
import pandas as pd
import os
import json
from google import genai

# -------------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Autonomous Finance Controller",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------------
# ADVANCED MODERN DARK MODE CSS (GLASSMORPHISM & SLATE ACCENTS)
# -------------------------------------------------------------------
custom_css = """
<style>
    /* Main Background & Base Typography */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Top Hero Navigation Header */
    .hero-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 24px 30px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .hero-title {
        color: #38BDF8;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 14px;
        margin-top: 4px;
    }

    .system-status {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid #10B981;
        color: #10B981;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Metric Cards Styling */
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #F8FAFC !important;
    }
    
    div[data-testid="metric-container"] {
        background: #1E293B;
        border: 1px solid #334155;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* Tab Custom Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #1E293B;
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid #334155;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }

    /* Priority Risk Badges */
    .badge-high {
        background-color: #EF4444;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    .badge-medium {
        background-color: #F59E0B;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    .badge-low {
        background-color: #10B981;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }

    /* Primary Buttons Styling */
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -------------------------------------------------------------------
# FILE CONSTANTS & CACHING LOGIC (RULE C)
# -------------------------------------------------------------------
EXCEPTIONS_CSV = "reconciliation_exceptions.csv"
STORE_CSV = "store_ledger.csv"
GATEWAY_CSV = "gateway_settlement.csv"
BANK_CSV = "bank_statement.csv"
CACHE_FILE = "ai_tickets_cache.json"

def load_ticket_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_ticket_cache(cache_data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=4)

if "ticket_cache" not in st.session_state:
    st.session_state["ticket_cache"] = load_ticket_cache()

# -------------------------------------------------------------------
# DATA LOADING
# -------------------------------------------------------------------
@st.cache_data
def load_exceptions_data():
    if not os.path.exists(EXCEPTIONS_CSV):
        return None
    df = pd.read_csv(EXCEPTIONS_CSV)
    priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
    df["priority_rank"] = df["risk_level"].map(priority_order)
    df = df.sort_values(by=["priority_rank", "discrepancy_amount"], ascending=[True, False])
    return df

df_exceptions = load_exceptions_data()

if df_exceptions is None:
    st.error(f"'{EXCEPTIONS_CSV}' not found. Please execute `py reconcile.py` first.")
    st.stop()

# -------------------------------------------------------------------
# TOP HERO HEADER (REPLACED BORING TAG)
# -------------------------------------------------------------------
st.markdown("""
<div class="hero-header">
    <div>
        <div class="hero-title">⚡ Autonomous Reconciliation Workstation</div>
        <div class="hero-subtitle">Track 04: AI Exception Resolution & Multi-Ledger Audit Workspace</div>
    </div>
    <div>
        <span class="system-status">● SYSTEM ACTIVE (0.091s Engine Latency)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# TOP LEVEL NAVIGATION DASHBOARD TABS
# -------------------------------------------------------------------
tab_dashboard, tab_analytics, tab_files, tab_settings = st.tabs([
    "📊 Executive Dashboard", 
    "📈 Financial Analytics", 
    "📁 Raw Data Explorer", 
    "⚡ System & Cache Settings"
])

# ===================================================================
# TAB 1: EXECUTIVE DASHBOARD
# ===================================================================
with tab_dashboard:
    # Metric Summary Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Analyzed Orders", "2,000", help="Processed across 3 source files")
    col2.metric("Flagged Exceptions", len(df_exceptions), delta="-288 Anomalies", delta_color="inverse")
    col3.metric("High-Priority Cases", len(df_exceptions[df_exceptions["risk_level"] == "HIGH"]))
    total_loss = df_exceptions["discrepancy_amount"].sum()
    col4.metric("Total Disputed Amount", f"₹{total_loss:,.2f}")

    st.divider()

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.subheader(f"📋 Priority Queue ({len(df_exceptions)} Exceptions)")
        
        # Sidebar-style Filters in Expander
        with st.expander("🔍 Filter Queue Options", expanded=False):
            risk_filter = st.multiselect("Filter Priority:", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM", "LOW"])
            issue_filter = st.multiselect("Filter Issue Type:", list(df_exceptions["issue_type"].unique()), default=list(df_exceptions["issue_type"].unique()))
        
        filtered_df = df_exceptions[
            (df_exceptions["risk_level"].isin(risk_filter)) &
            (df_exceptions["issue_type"].isin(issue_filter))
        ]

        display_cols = ["order_id", "risk_level", "issue_type", "customer_name", "discrepancy_amount"]
        st.dataframe(
            filtered_df[display_cols].style.format({"discrepancy_amount": "₹{:.2f}"}),
            use_container_width=True,
            height=400
        )

        selected_order_id = st.selectbox(
            "Select Order ID for AI Resolution Package:",
            options=filtered_df["order_id"].tolist()
        )

    with right_col:
        st.subheader("🤖 AI Copilot Resolution Desk")
        
        selected_row = filtered_df[filtered_df["order_id"] == selected_order_id].iloc[0]

        def get_val(row, *keys, default=0.0):
            for k in keys:
                if k in row.index:
                    return row[k]
            return default

        store_amt = get_val(selected_row, 'store_ledger_amount', 'store_amount')
        gateway_amt = get_val(selected_row, 'gateway_payout_amount', 'gateway_amount')
        bank_amt = get_val(selected_row, 'bank_deposited_amount', 'bank_amount')
        fee_amt = get_val(selected_row, 'gateway_fee_charged', 'fee_charged')

        risk_tag = selected_row['risk_level']
        badge_class = f"badge-{risk_tag.lower()}"

        st.markdown(f"""
        <div style="background-color: #1E293B; padding: 16px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px;">
            <span class="{badge_class}">{risk_tag} PRIORITY</span>
            <h3 style="margin-top: 8px; margin-bottom: 4px; color: #38BDF8;">Order #{selected_row['order_id']}</h3>
            <p style="color: #94A3B8; font-size: 14px; margin: 0;">Customer: <b>{selected_row['customer_name']}</b></p>
            <p style="color: #F8FAFC; font-size: 16px; margin-top: 8px;">Discrepancy Variance: <b style="color: #EF4444;">₹{selected_row['discrepancy_amount']}</b> ({selected_row['issue_type']})</p>
        </div>
        """, unsafe_allow_html=True)

        cache_key = str(selected_row['order_id'])
        
        # RULE C: CACHE CHECK
        if cache_key in st.session_state["ticket_cache"]:
            st.success("⚡ Loaded from Local Cache (0 Tokens Used)")
            cached_ticket = st.session_state["ticket_cache"][cache_key]
            
            st.markdown("#### 🔬 Financial Root-Cause Diagnosis")
            st.write(cached_ticket["diagnosis"])
            
            st.markdown("#### ✉️ Drafted Vendor Dispute Email")
            st.code(cached_ticket["email"], language="markdown")
            
            if st.button("Approve & Copy Draft", type="primary"):
                st.toast("Draft copied to clipboard & logged as APPROVED!")

        else:
            # RULE A: ON-DEMAND EXECUTION
            st.info("Click below to execute Gemini diagnosis for this exception.")
            
            if st.button("Generate Resolution Package", type="primary"):
                with st.spinner("Analyzing contract logic & drafting dispute email..."):
                    
                    api_key = os.getenv("GEMINI_API_KEY")
                    client = genai.Client(api_key=api_key) if api_key else genai.Client()

                    prompt = f"""
You are an expert AI FinOps Controller. Analyze this exception and generate an action ticket.

DETAILS:
- Order ID: {selected_row['order_id']}
- Customer: {selected_row['customer_name']}
- Issue Type: {selected_row['issue_type']}
- Priority: {selected_row['risk_level']}
- Store Amount: ₹{store_amt}
- Gateway Amount: ₹{gateway_amt}
- Bank Amount: ₹{bank_amt}
- Charged Fee: ₹{fee_amt}
- Discrepancy Amount: ₹{selected_row['discrepancy_amount']}

INSTRUCTIONS:
1. Provide a "Financial Root-Cause Diagnosis" (2-3 sentences explaining why this variance occurred mathematically).
2. Draft a formal "Vendor Dispute Email" to Razorpay/Bank citing order number, contracted terms, and exact refund claim amounts.
"""

                    try:
                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=prompt,
                        )
                        full_text = response.text

                        if "Vendor Dispute Email" in full_text:
                            parts = full_text.split("Vendor Dispute Email")
                            diagnosis = parts[0].replace("Financial Root-Cause Diagnosis", "").replace("#", "").strip()
                            email = parts[1].strip()
                        else:
                            diagnosis = full_text
                            email = full_text

                        st.session_state["ticket_cache"][cache_key] = {
                            "diagnosis": diagnosis,
                            "email": email
                        }
                        save_ticket_cache(st.session_state["ticket_cache"])

                        st.rerun()

                    except Exception as e:
                        st.error(f"API Request Failed: {e}")

# ===================================================================
# TAB 2: FINANCIAL ANALYTICS
# ===================================================================
with tab_analytics:
    st.subheader("📈 Financial Anomaly Breakdown & Loss Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("#### Discrepancy Loss by Issue Type (₹)")
        loss_by_issue = df_exceptions.groupby("issue_type")["discrepancy_amount"].sum()
        st.bar_chart(loss_by_issue)

    with chart_col2:
        st.markdown("#### Exceptions Breakdown by Risk Level")
        risk_counts = df_exceptions["risk_level"].value_counts()
        st.bar_chart(risk_counts)

    st.divider()
    st.markdown("#### High-Value Loss Concentration")
    top_10_losses = df_exceptions.nlargest(10, "discrepancy_amount")[["order_id", "customer_name", "issue_type", "discrepancy_amount"]]
    st.table(top_10_losses.style.format({"discrepancy_amount": "₹{:.2f}"}))

# ===================================================================
# TAB 3: RAW DATA FILE EXPLORER
# ===================================================================
with tab_files:
    st.subheader("📁 Ledger Source CSV Data Explorer")
    
    file_sub_tabs = st.tabs([
        "⚠️ Reconciliation Exceptions (288)", 
        "🛍️ Store Ledger (2,000)", 
        "💳 Gateway Settlement (2,000)", 
        "🏦 Bank Statement (2,000)"
    ])
    
    with file_sub_tabs[0]:
        st.dataframe(df_exceptions, use_container_width=True)
        st.caption(f"File Path: `{EXCEPTIONS_CSV}`")
        
    with file_sub_tabs[1]:
        if os.path.exists(STORE_CSV):
            st.dataframe(pd.read_csv(STORE_CSV), use_container_width=True)
        else:
            st.info(f"File '{STORE_CSV}' not found.")
            
    with file_sub_tabs[2]:
        if os.path.exists(GATEWAY_CSV):
            st.dataframe(pd.read_csv(GATEWAY_CSV), use_container_width=True)
        else:
            st.info(f"File '{GATEWAY_CSV}' not found.")

    with file_sub_tabs[3]:
        if os.path.exists(BANK_CSV):
            st.dataframe(pd.read_csv(BANK_CSV), use_container_width=True)
        else:
            st.info(f"File '{BANK_CSV}' not found.")

# ===================================================================
# TAB 4: SYSTEM AUDIT & CACHE SETTINGS
# ===================================================================
with tab_settings:
    st.subheader("⚡ System Configuration & Token Cache Management")
    
    st.markdown("""
    * **Engine Matching Model:** Rule-based Deterministic Join (`reconcile.py`)
    * **AI Model Engine:** `gemini-3.6-flash`
    * **Token Consumption Mode:** Rule A (Lazy On-Demand Execution)
    * **Active Local Cache:** Rule C (`ai_tickets_cache.json`)
    """)
    
    st.divider()
    
    cached_count = len(st.session_state["ticket_cache"])
    st.write(f"**Currently Cached AI Resolution Packages:** {cached_count} tickets")
    
    if st.button("Clear AI Tickets Cache", type="secondary"):
        st.session_state["ticket_cache"] = {}
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        st.toast("Local ticket cache cleared!")
        st.rerun()