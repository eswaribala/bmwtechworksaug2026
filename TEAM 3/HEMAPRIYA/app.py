import requests
import streamlit as st




st.set_page_config(
    page_title="BMW Dealer Inventory Recommendation",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)




st.markdown(
    """
    <style>
    :root {
        --bmw-blue: #1c69d4;
        --bmw-dark: #0a0e17;
        --bmw-navy: #12203a;
        --ink: #1a1d29;
        --muted: #6b7280;
        --border: #e6e8ee;
        --card-bg: #ffffff;
        --success: #16a34a;
        --warning: #d97706;
        --danger: #dc2626;
    }

    #MainMenu, footer { visibility: hidden; }

    .main { padding-top: 0.5rem; }

    .block-container {
        padding-top: 1.5rem;
        max-width: 1200px;
    }

    /* ---------- Hero header ---------- */
    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.2rem 2.4rem;
        border-radius: 18px;
        background: radial-gradient(circle at 15% 20%, #1c3a63 0%, var(--bmw-navy) 45%, var(--bmw-dark) 100%);
        color: #fff;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 30px rgba(10, 14, 23, 0.25);
    }

    .hero::after {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(28,105,212,0.45) 0%, rgba(28,105,212,0) 70%);
    }

    .hero-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.28rem 0.7rem;
        border-radius: 999px;
        background: rgba(28,105,212,0.25);
        border: 1px solid rgba(28,105,212,0.5);
        color: #bcd6f7;
        margin-bottom: 0.9rem;
    }

    .hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .hero p {
        margin: 0;
        color: #aab4c6;
        font-size: 0.98rem;
        max-width: 620px;
    }

    /* ---------- Section titles ---------- */
    .section-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--ink);
        margin: 1.6rem 0 0.9rem 0;
    }

    .section-title .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--bmw-blue);
        display: inline-block;
    }

    /* ---------- Selection card ---------- */
    .selection-card {
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        background: var(--card-bg);
        border: 1px solid var(--border);
        box-shadow: 0 1px 3px rgba(16,24,40,0.04);
    }

    /* ---------- Metric cards ---------- */
    .metric-card {
        padding: 1.3rem 1.2rem;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: var(--card-bg);
        box-shadow: 0 1px 3px rgba(16,24,40,0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16,24,40,0.08);
    }

    .metric-icon {
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }

    .metric-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: var(--ink);
        line-height: 1.1;
    }

    .metric-sub {
        font-size: 0.78rem;
        color: var(--muted);
        margin-top: 0.3rem;
    }

    .metric-value.accent { color: var(--bmw-blue); }

    /* ---------- Badges ---------- */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: capitalize;
    }
    .badge-up { background: #dcfce7; color: var(--success); }
    .badge-down { background: #fee2e2; color: var(--danger); }
    .badge-flat { background: #fef3c7; color: var(--warning); }

    /* ---------- Reason box ---------- */
    .reason-box {
        padding: 1.1rem 1.3rem;
        border-radius: 14px;
        background: #eef4ff;
        border-left: 5px solid var(--bmw-blue);
        color: var(--ink);
        font-size: 0.96rem;
        line-height: 1.5;
    }

    /* ---------- Empty state ---------- */
    .empty-state {
        text-align: center;
        padding: 3.2rem 1.5rem;
        border-radius: 16px;
        border: 1.5px dashed var(--border);
        color: var(--muted);
        margin-top: 1rem;
    }

    .empty-state .emoji {
        font-size: 2.4rem;
        margin-bottom: 0.6rem;
        display: block;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: var(--bmw-dark);
    }

    section[data-testid="stSidebar"] * {
        color: #d7dde8 !important;
    }

    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    .sidebar-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
        border-radius: 8px;
        font-size: 0.78rem;
        background: rgba(28,105,212,0.18);
        border: 1px solid rgba(28,105,212,0.4);
        color: #bcd6f7 !important;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background: var(--bmw-blue);
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.55rem 1rem;
    }

    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: #1554a6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



st.markdown(
    """
    <div class="hero">
        <span class="hero-badge">Demand Intelligence · Live Recommendation</span>
        <h1>🚗 BMW Dealer Inventory Recommendation</h1>
        <p>
            Predict next‑month demand and get an optimal stocking
            quantity for any dealer and model, backed by your
            PySpark + XGBoost pipeline.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)



with st.sidebar:
    st.markdown("## ℹ️ Project Info")

    st.markdown("**Purpose**")
    st.caption(
        "Recommend how many vehicles a dealer should stock "
        "based on predicted demand and current inventory."
    )

    st.markdown("**Pipeline**")
    st.caption("Data → PySpark → S3 → Athena → ML → Recommendation → FastAPI")

    st.divider()

    st.markdown("**Technology**")
    st.markdown(
        """
        <span class="sidebar-pill">Python</span>
        <span class="sidebar-pill">PySpark</span>
        <span class="sidebar-pill">AWS S3</span>
        <span class="sidebar-pill">AWS Athena</span>
        <span class="sidebar-pill">XGBoost</span>
        <span class="sidebar-pill">FastAPI</span>
        <span class="sidebar-pill">Streamlit</span>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("Connects to the FastAPI service on `127.0.0.1:8000`.")




st.markdown(
    '<div class="section-title"><span class="dot"></span>Dealer &amp; Model Selection</div>',
    unsafe_allow_html=True,
)

with st.container():
    st.markdown('<div class="selection-card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 0.7])

    with col1:
        dealer_id = st.selectbox(
            "Select Dealer",
            ["D001", "D002", "D003", "D004", "D005"],
        )

    with col2:
        model = st.selectbox(
            "Select BMW Model",
            [
                "i4",
                "X1",
                "X3",
                "X5",
                "iX1",
                "iX3",
                "3 Series",
                "5 Series",
            ],
        )

    with col3:
        st.write("")
        st.write("")
        generate = st.button(
            "⚡ Generate Recommendation",
            use_container_width=True,
            type="primary",
        )

    st.markdown("</div>", unsafe_allow_html=True)



def trend_badge(trend: str) -> str:
    trend_lower = (trend or "").lower()
    if "up" in trend_lower or "increas" in trend_lower or "grow" in trend_lower:
        cls, icon = "badge-up", "▲"
    elif "down" in trend_lower or "decreas" in trend_lower or "declin" in trend_lower:
        cls, icon = "badge-down", "▼"
    else:
        cls, icon = "badge-flat", "■"
    return f'<span class="badge {cls}">{icon} {trend.title()}</span>'



if generate:

    with st.spinner("Fetching prediction from the model service..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/recommend",
                json={
                    "dealer_id": dealer_id,
                    "model": model,
                },
                timeout=30,
            )
        except requests.exceptions.ConnectionError:
            response = None
            st.error(
                "🔌 Cannot connect to the FastAPI server. "
                "Please make sure the API is running on port 8000."
            )
        except requests.exceptions.Timeout:
            response = None
            st.error("⏱️ The API request timed out. Please try again.")
        except Exception as e:
            response = None
            st.error(f"Unexpected error: {str(e)}")

    if response is not None:
        if response.status_code == 200:

            result = response.json()

            st.success(f"✅ Recommendation generated for **{dealer_id} — {model}**")

     

            st.markdown(
                '<div class="section-title"><span class="dot"></span>Recommendation Summary</div>',
                unsafe_allow_html=True,
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-icon">📈</div>
                        <div class="metric-title">Predicted Demand</div>
                        <div class="metric-value">{result['Predicted Next Month Demand']:.1f}</div>
                        <div class="metric-sub">units, next month</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-icon">📦</div>
                        <div class="metric-title">Current Inventory</div>
                        <div class="metric-value">{result['Current Inventory']:.0f}</div>
                        <div class="metric-sub">units on lot</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-icon">🎯</div>
                        <div class="metric-title">Target Inventory</div>
                        <div class="metric-value">{result['Target Inventory']:.1f}</div>
                        <div class="metric-sub">optimal stocking level</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col4:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-icon">✅</div>
                        <div class="metric-title">Recommended Qty</div>
                        <div class="metric-value accent">{result['Recommended Quantity']}</div>
                        <div class="metric-sub">units to order</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

         

            st.markdown(
                '<div class="section-title"><span class="dot"></span>Inventory Analysis</div>',
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-icon">📅</div>
                        <div class="metric-title">Days of Inventory</div>
                        <div class="metric-value">{result['Days of Inventory']:.1f}<span style="font-size:1rem;font-weight:600;color:var(--muted);"> days</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-icon">📊</div>
                        <div class="metric-title">Sales Trend</div>
                        <div style="margin-top:0.2rem;">{trend_badge(result["Sales Trend"])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

      

            st.markdown(
                '<div class="section-title"><span class="dot"></span>Demand vs. Inventory</div>',
                unsafe_allow_html=True,
            )

            chart_data = {
                "Metric": [
                    "Predicted Demand",
                    "Current Inventory",
                    "Target Inventory",
                ],
                "Quantity": [
                    result["Predicted Next Month Demand"],
                    result["Current Inventory"],
                    result["Target Inventory"],
                ],
            }

            st.bar_chart(
                chart_data,
                x="Metric",
                y="Quantity",
                color="#1c69d4",
                use_container_width=True,
            )

        

            st.markdown(
                '<div class="section-title"><span class="dot"></span>Recommendation Reason</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="reason-box">
                    💡 {result["Reason"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            try:
                error_detail = response.json().get("detail", "Unknown API error")
            except Exception:
                error_detail = response.text

            st.error(f"API error ({response.status_code}): {error_detail}")

else:
    st.markdown(
        """
        <div class="empty-state">
            <span class="emoji">🚗</span>
            <strong>No recommendation yet</strong><br/>
            Pick a dealer and model above, then click
            <em>Generate Recommendation</em> to see the results.
        </div>
        """,
        unsafe_allow_html=True,
    )




st.divider()

st.caption(
    "BMW Dealer Inventory Recommendation • "
    "Demand Prediction + Inventory Analytics"
)