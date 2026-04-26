import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import io

# ============================================================================
# PAGE CONFIGURATION - MUST BE FIRST
# ============================================================================

st.set_page_config(
    page_title="FinCoach AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS & THEME
# ============================================================================

CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
    * {
        font-family: 'Inter', sans-serif;
    }

    :root {
        --primary: #1B4FBB;
        --accent: #00C6A2;
        --warning: #F5A623;
        --danger: #E03E3E;
        --success: #27AE60;
        --bg-dark: #0F1117;
        --bg-card: #1A1D27;
        --bg-input: #1E2130;
        --text-primary: #FFFFFF;
        --text-muted: #9FA6B2;
        --border: rgba(255,255,255,0.08);
    }

    body {
        background-color: var(--bg-dark);
        color: var(--text-primary);
    }

    .stMetric {
        background-color: var(--bg-card);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }

    .stMetric:hover {
        transform: translateY(-2px);
        border-color: var(--accent);
    }

    .metric-card-success {
        border-left: 4px solid var(--success);
    }

    .metric-card-danger {
        border-left: 4px solid var(--danger);
    }

    .metric-card-primary {
        border-left: 4px solid var(--primary);
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(27, 79, 187, 0.3);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [role="tab"] {
        border-radius: 20px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }

    [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    }

    .card {
        background-color: var(--bg-card);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        margin-bottom: 1rem;
    }

    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: var(--text-primary);
    }

    .stTextInput, .stNumberInput, .stSelectbox, .stDateInput {
        background-color: var(--bg-input);
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {
        background-color: var(--bg-input);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 8px;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(0, 198, 162, 0.1);
    }

    .warning-banner {
        background-color: rgba(245, 166, 35, 0.1);
        border-left: 4px solid var(--warning);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .danger-banner {
        background-color: rgba(224, 62, 62, 0.1);
        border-left: 4px solid var(--danger);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .success-banner {
        background-color: rgba(39, 174, 96, 0.1);
        border-left: 4px solid var(--success);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .info-banner {
        background-color: rgba(27, 79, 187, 0.1);
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .chat-message-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1rem;
    }

    .chat-message-ai {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 1rem;
    }

    .chat-bubble-user {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 16px;
        max-width: 70%;
        word-wrap: break-word;
    }

    .chat-bubble-ai {
        background-color: var(--bg-card);
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        max-width: 70%;
        word-wrap: break-word;
    }

    .gradient-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .badge-pill {
        display: inline-block;
        padding: 0.375rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .badge-success {
        background-color: rgba(39, 174, 96, 0.2);
        color: var(--success);
    }

    .badge-warning {
        background-color: rgba(245, 166, 35, 0.2);
        color: var(--warning);
    }

    .badge-danger {
        background-color: rgba(224, 62, 62, 0.2);
        color: var(--danger);
    }

    [data-testid="stSidebar"] {
        background-color: var(--bg-card);
    }

    .sidebar-section {
        border-bottom: 1px solid var(--border);
        padding: 1rem 0;
    }

    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# CATEGORY KEYWORDS & TRANSACTION CATEGORIZATION
# ============================================================================

CATEGORY_KEYWORDS = {
    "🍽️ Food & Dining": [
        "restaurant", "cafe", "mcdonalds", "kfc", "burger", "pizza", "starbucks",
        "costa", "talabat", "deliveroo", "zomato", "food", "dining", "eat",
        "lunch", "dinner", "breakfast", "biryani", "shawarma", "sushi", "barista"
    ],
    "🛒 Groceries": [
        "spinneys", "carrefour", "lulu", "waitrose", "supermarket", "grocery",
        "market", "hypermarket", "choithrams", "geant", "organic", "sainsbury"
    ],
    "🚗 Transport": [
        "uber", "careem", "taxi", "metro", "bus", "petrol", "fuel", "parking",
        "salik", "toll", "rta", "transport", "ride", "lyft", "emirates", "rac"
    ],
    "🛍️ Shopping": [
        "amazon", "noon", "mall", "zara", "hm", "h&m", "ikea", "marks",
        "shopping", "store", "boutique", "fashion", "clothes", "shoes", "uniqlo"
    ],
    "🏠 Rent & Housing": [
        "rent", "mortgage", "landlord", "property", "housing", "maintenance",
        "repairs", "furniture", "home", "apartment", "leaseback"
    ],
    "⚡ Utilities": [
        "dewa", "sewa", "fewa", "electric", "water", "gas", "utility",
        "etisalat", "du", "internet", "telecom", "phone", "mobile", "broadband"
    ],
    "🎬 Entertainment": [
        "netflix", "spotify", "apple", "disney", "hbo", "cinema", "vox",
        "entertainment", "gaming", "playstation", "xbox", "stream", "youtube"
    ],
    "🏥 Healthcare": [
        "pharmacy", "hospital", "clinic", "doctor", "dental", "medical",
        "health", "medicine", "lab", "test", "insurance", "vaccination"
    ],
    "📚 Education": [
        "university", "school", "college", "course", "udemy", "coursera",
        "tuition", "fees", "books", "education", "training", "certification", "course"
    ],
    "✈️ Travel": [
        "airline", "hotel", "booking", "airbnb", "flight", "holiday",
        "travel", "trip", "vacation", "resort", "emirates", "flydubai", "expedia"
    ],
    "💰 Income": [
        "salary", "credit", "payment received", "transfer in", "freelance",
        "dividend", "bonus", "commission", "refund", "cashback", "invoice"
    ],
    "🔄 Subscriptions": [
        "subscription", "membership", "annual", "monthly plan", "renewal",
        "adobe", "microsoft", "google", "dropbox", "zoom", "slack", "linkedin"
    ],
    "💳 Finance & Banking": [
        "loan", "emi", "installment", "credit card", "interest", "fee",
        "charge", "bank", "transfer", "withdrawal", "savings", "investment"
    ],
    "🎁 Personal Care": [
        "salon", "spa", "gym", "fitness", "beauty", "grooming", "barber",
        "massage", "wellness", "yoga", "pilates", "haircut"
    ],
}

def categorize_transaction(description: str) -> str:
    """Categorize a transaction using keyword matching."""
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in desc_lower for keyword in keywords):
            return category
    return "📦 Other"


def call_azure_ai(prompt: str, system_message: str = "You are FinCoach, a helpful personal finance assistant.") -> str:
    """Call Azure AI API with optimized timeout."""
    try:
        endpoint = st.secrets.get("AZURE_API_ENDPOINT", "")
        api_key = st.secrets.get("AZURE_API_KEY", "")
        model = st.secrets.get("MODEL_NAME", "Phi-4")
        
        if not endpoint or not api_key:
            return "⚙️ AI service not configured. Check Streamlit Secrets. Demo mode still working!"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt[:4000]}
            ],
            "max_tokens": 600,
            "temperature": 0.7
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    except requests.exceptions.Timeout:
        return "⏱️ AI response taking too long (network delay). Please try again in a moment."
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return "⚠️ Too many requests. Please wait a moment and try again."
        elif e.response.status_code == 401:
            return "🔑 API key error. Check Streamlit Secrets configuration."
        else:
            return "❌ AI service error. Please try again shortly."
    except Exception as e:
        return "❌ Connection error. Check internet and try again."

# ============================================================================
# DEMO DATA GENERATOR
# ============================================================================

def generate_demo_data() -> pd.DataFrame:
    """Generate 6 months of realistic synthetic bank transactions using user profile."""
    np.random.seed(42)
    
    transactions = []
    base_date = pd.Timestamp.now() - pd.DateOffset(months=6)
    
    # Use user's monthly income if provided, otherwise default to 8500
    monthly_salary = st.session_state.monthly_income if st.session_state.monthly_income > 0 else 8500
    
    # Scale expenses based on income
    expense_scale = monthly_salary / 8500
    
    # Monthly salary
    for i in range(6):
        transactions.append({
            'Date': base_date + pd.DateOffset(months=i, day=1),
            'Description': 'Monthly Salary Credit',
            'Amount': monthly_salary,
            'Type': 'Credit'
        })
    
    # Regular expenses - scaled to user's income level
    expense_templates = [
        ('Careem ride', int(-45 * expense_scale), 4), ('Talabat order', int(-75 * expense_scale), 8),
        ('Spinneys Groceries', int(-280 * expense_scale), 4), ('DEWA Bill', int(-320 * expense_scale), 6),
        ('Netflix subscription', -35, 6), ('Spotify', -15, 6),
        ('Etisalat Bill', int(-250 * expense_scale), 6), ('Gym membership', int(-180 * expense_scale), 6),
        ('Uber ride', int(-40 * expense_scale), 4), ('Amazon purchase', int(-120 * expense_scale), 3),
        ('Noon shopping', int(-150 * expense_scale), 2), ('Zara clothing', int(-250 * expense_scale), 1),
        ('VOX Cinema', int(-80 * expense_scale), 2), ('Costa Coffee', -35, 12),
        ('IKEA furniture', int(-500 * expense_scale), 1), ('Pharmacy', int(-75 * expense_scale), 3),
        ('Dentist', int(-300 * expense_scale), 1), ('Petrol', int(-150 * expense_scale), 6),
        ('Parking fee', -20, 6), ('Restaurant dinner', int(-200 * expense_scale), 6),
        ('School fees', int(-1500 * expense_scale), 2), ('Rent payment', int(-3000 * expense_scale), 6),
        ('Adobe Creative Cloud', -200, 6),
    ]
    
    for desc, amount, count in expense_templates:
        for _ in range(count):
            random_day = np.random.randint(1, 28)
            random_month = np.random.randint(0, 6)
            transactions.append({
                'Date': base_date + pd.DateOffset(months=random_month, day=random_day),
                'Description': desc,
                'Amount': amount + np.random.randint(-10, 10),
                'Type': 'Debit'
            })
    
    df = pd.DataFrame(transactions)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    return df

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_csv(df: pd.DataFrame) -> tuple:
    """Validate uploaded CSV structure."""
    if df.empty:
        return False, "The uploaded file is empty."
    if len(df) > 10000:
        return False, "File too large. Maximum 10,000 transactions."
    
    required_columns_options = [
        ['date', 'description', 'amount'],
        ['date', 'narration', 'amount'],
        ['transaction date', 'description', 'debit/credit'],
    ]
    
    cols_lower = [c.lower() for c in df.columns]
    for option in required_columns_options:
        if all(col in cols_lower for col in option):
            return True, "Valid"
    
    return False, "Could not detect required columns. Ensure your CSV has Date, Description, and Amount columns."


def check_secrets():
    """Verify all required secrets are configured."""
    required = ["AZURE_API_KEY", "AZURE_API_ENDPOINT"]
    missing = [key for key in required if key not in st.secrets]
    if missing:
        st.warning(f"⚙️ Optional: Configure Azure AI in Settings → Secrets for AI features. Missing: {', '.join(missing)}")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'df' not in st.session_state:
    st.session_state.df = None

if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

if 'user_name' not in st.session_state:
    st.session_state.user_name = "User"

if 'currency' not in st.session_state:
    st.session_state.currency = "AED"

if 'monthly_income' not in st.session_state:
    st.session_state.monthly_income = 0

if 'goals' not in st.session_state:
    st.session_state.goals = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'last_processed_message' not in st.session_state:
    st.session_state.last_processed_message = None

if 'ai_processing' not in st.session_state:
    st.session_state.ai_processing = False

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="margin: 0; font-size: 2rem;">💰</h1>
        <h3 style="margin: 0.5rem 0 0 0;">FinCoach AI</h3>
        <p style="color: #9FA6B2; margin: 0.25rem 0 0 0;">Your Smart Money Coach</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # User Profile Section
    st.markdown("### 👤 User Profile")
    st.session_state.user_name = st.text_input("Your Name", value=st.session_state.user_name, label_visibility="collapsed", placeholder="Enter your name")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.currency = st.selectbox(
            "Currency",
            ["USD ($)", "AED (د.إ)", "GBP (£)", "EUR (€)", "SAR (﷼)", "INR (₹)"],
            index=1,
            label_visibility="collapsed"
        )
    with col2:
        st.session_state.monthly_income = st.number_input(
            "Monthly Income",
            min_value=0,
            value=st.session_state.monthly_income,
            label_visibility="collapsed",
            placeholder="Income"
        )
    
    st.divider()
    
    # Data Upload Section
    st.markdown("### 📁 Upload Bank Statement")
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'], label_visibility="collapsed")
    
    if uploaded_file:
        try:
            df_upload = pd.read_csv(uploaded_file)
            is_valid, message = validate_csv(df_upload)
            if is_valid:
                st.session_state.df = df_upload
                st.session_state.demo_mode = False
                st.success("✅ File uploaded successfully!")
            else:
                st.error(f"❌ {message}")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    if st.button("🎮 Load Demo Data", use_container_width=True):
        st.session_state.df = generate_demo_data()
        st.session_state.demo_mode = True
        st.success("✅ Demo data loaded!")
    
    st.divider()
    
    # Data Management
    st.markdown("### 🗑️ Data Management")
    if st.button("🗑️ Clear All Data", use_container_width=True):
        st.session_state.df = None
        st.session_state.demo_mode = False
        st.session_state.goals = []
        st.session_state.chat_history = []
        st.success("✅ All data cleared!")
        st.rerun()
    
    st.divider()
    
    # Privacy Notice
    st.markdown("""
    <div class="info-banner" style="margin-top: 2rem;">
        <p><strong>🔒 Privacy Protected</strong></p>
        <p style="font-size: 0.875rem; margin: 0.5rem 0 0 0;">
            Your data is NEVER stored, sold, or shared. Session-only processing. 
            <br><br>
            <strong>⚠️ Not Financial Advice</strong>
            <br>
            Educational insights only. Consult qualified professionals for major decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# DEMO MODE BANNER
# ============================================================================

if st.session_state.demo_mode:
    st.info("🎮 **Demo Mode Active** — Using synthetic data. Upload your own CSV to analyze real transactions.", icon="ℹ️")

# Check secrets configuration
check_secrets()

# ============================================================================
# MAIN APP TABS
# ============================================================================

if st.session_state.df is not None:
    
    # Prepare data for analysis
    df = st.session_state.df.copy()
    
    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Detect and standardize date, description, amount columns
    date_cols = [col for col in df.columns if 'date' in col]
    desc_cols = [col for col in df.columns if 'description' in col or 'narration' in col]
    amount_cols = [col for col in df.columns if 'amount' in col or 'debit' in col or 'credit' in col]
    
    if date_cols and desc_cols and amount_cols:
        df['date'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
        df['description'] = df[desc_cols[0]].astype(str)
        df['amount'] = pd.to_numeric(df[amount_cols[0]], errors='coerce')
        
        # Categorize transactions
        df['category'] = df['description'].apply(categorize_transaction)
        df['type'] = df['amount'].apply(lambda x: 'Credit' if x > 0 else 'Debit')
        
        df = df.dropna(subset=['date', 'amount'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # ====================================================================
        # TAB 1: DASHBOARD
        # ====================================================================
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📊 Dashboard",
            "💸 Spending Analysis",
            "🤖 AI Coach",
            "🎯 Goals Tracker",
            "📈 Investments",
            "💼 Budget Planner",
            "⚠️ Risk Report",
            "🧾 Tax Summary"
        ])
        
        with tab1:
            # Header Banner
            st.markdown(f"""
            <div class="gradient-header">
                <h1 style="margin: 0; font-size: 2rem;">Welcome back, {st.session_state.user_name}! 👋</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1rem;">{pd.Timestamp.now().strftime('%A, %B %d, %Y')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate KPIs
            total_income = df[df['type'] == 'Credit']['amount'].sum()
            total_expenses = abs(df[df['type'] == 'Debit']['amount'].sum())
            net_savings = total_income - total_expenses
            savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
            
            # KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Income",
                    value=f"{st.session_state.currency.split()[0]} {total_income:,.0f}",
                    delta="↑ Cash in"
                )
            
            with col2:
                st.metric(
                    label="Total Expenses",
                    value=f"{st.session_state.currency.split()[0]} {total_expenses:,.0f}",
                    delta="↓ Cash out"
                )
            
            with col3:
                delta_color = "off" if net_savings < 0 else "normal"
                st.metric(
                    label="Net Savings",
                    value=f"{st.session_state.currency.split()[0]} {net_savings:,.0f}",
                    delta=f"{savings_rate:.1f}%",
                    delta_color=delta_color
                )
            
            with col4:
                savings_color = "normal" if savings_rate >= 20 else ("off" if savings_rate >= 10 else "off")
                st.metric(
                    label="Savings Rate",
                    value=f"{savings_rate:.1f}%",
                    delta="Target: 20%",
                    delta_color=savings_color
                )
            
            # Get date range for aggregation info
            date_range = f"({df['date'].min().strftime('%b %d, %Y')} → {df['date'].max().strftime('%b %d, %Y')})"
            st.caption(f"📊 6-Month Aggregated Summary {date_range}")
            
            st.divider()
            
            # Charts Row
            col1, col2 = st.columns([0.6, 0.4])
            
            with col1:
                # Spending by Category (Donut)
                category_spending = df[df['type'] == 'Debit'].groupby('category')['amount'].sum().abs().sort_values(ascending=False).head(8)
                
                fig_donut = go.Figure(data=[go.Pie(
                    labels=category_spending.index,
                    values=category_spending.values,
                    hole=0.4,
                    marker=dict(
                        colors=['#00C6A2', '#1B4FBB', '#F5A623', '#E03E3E', '#27AE60', '#9FA6B2', '#6C5CE7', '#FD79A8'],
                        line=dict(color='#1A1D27', width=2)
                    ),
                    hovertemplate='<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>'
                )])
                fig_donut.update_layout(
                    title="Spending by Category",
                    showlegend=True,
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FFFFFF', family='Inter'),
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            
            with col2:
                # Monthly Income vs Expenses (Bar)
                df['month'] = df['date'].dt.to_period('M')
                monthly_data = df.groupby('month').agg(
                    income=('amount', lambda x: x[x > 0].sum()),
                    expenses=('amount', lambda x: abs(x[x < 0].sum()))
                ).reset_index()
                monthly_data['month'] = monthly_data['month'].astype(str)
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=monthly_data['month'],
                    y=monthly_data['income'],
                    name='Income',
                    marker=dict(color='#27AE60')
                ))
                fig_bar.add_trace(go.Bar(
                    x=monthly_data['month'],
                    y=monthly_data['expenses'],
                    name='Expenses',
                    marker=dict(color='#E03E3E')
                ))
                fig_bar.update_layout(
                    title="Monthly Income vs Expenses",
                    xaxis_title="Month",
                    yaxis_title="Amount",
                    barmode='group',
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FFFFFF', family='Inter'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.divider()
            
            # Bottom Row
            col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
            
            with col1:
                # AI Quick Insight
                st.markdown("### 💡 AI Quick Insight")
                insight_prompt = f"""Give ONE sentence insight about this person's spending for the last month:
                Total Income: {total_income:,.0f}
                Total Expenses: {total_expenses:,.0f}
                Top Category: {df[df['type'] == 'Debit'].groupby('category')['amount'].sum().abs().idxmax()}
                Keep it positive and encouraging. Max 20 words."""
                
                insight = call_azure_ai(insight_prompt)
                st.info(insight)
            
            with col2:
                # Financial Health Score
                health_score = min(100, max(0, (savings_rate / 20 * 100)))
                fig_gauge = go.Figure(data=[go.Indicator(
                    mode="gauge+number",
                    value=health_score,
                    title='Health Score',
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': '#00C6A2'},
                        'steps': [
                            {'range': [0, 40], 'color': 'rgba(224, 62, 62, 0.2)'},
                            {'range': [40, 70], 'color': 'rgba(245, 166, 35, 0.2)'},
                            {'range': [70, 100], 'color': 'rgba(39, 174, 96, 0.2)'}
                        ]
                    }
                )])
                fig_gauge.update_layout(
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FFFFFF', family='Inter')
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col3:
                st.markdown("### ⭐ Top Recommendations")
                recommendations = [
                    "Review subscriptions for cancellations",
                    "Set up automatic savings transfers",
                    "Create a monthly budget plan"
                ]
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"<div class='card'><strong>{i}.</strong> {rec}</div>", unsafe_allow_html=True)
        
        # ====================================================================
        # TAB 2: SPENDING ANALYSIS
        # ====================================================================
        
        with tab2:
            st.markdown("### 💸 Spending Analysis")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_category = st.selectbox(
                    "Category",
                    ["All"] + sorted(df['category'].unique().tolist()),
                    label_visibility="collapsed"
                )
            
            with col2:
                date_range = st.date_input(
                    "Date Range",
                    value=(df['date'].min(), df['date'].max()),
                    label_visibility="collapsed"
                )
            
            with col3:
                amount_range = st.slider(
                    "Amount Range",
                    min_value=int(df['amount'].min()),
                    max_value=int(df['amount'].max()),
                    value=(int(df['amount'].min()), int(df['amount'].max())),
                    label_visibility="collapsed"
                )
            
            # Filter data
            filtered_df = df.copy()
            if selected_category != "All":
                filtered_df = filtered_df[filtered_df['category'] == selected_category]
            
            filtered_df = filtered_df[
                (filtered_df['date'] >= pd.Timestamp(date_range[0])) &
                (filtered_df['date'] <= pd.Timestamp(date_range[1]))
            ]
            filtered_df = filtered_df[
                (filtered_df['amount'] >= amount_range[0]) &
                (filtered_df['amount'] <= amount_range[1])
            ]
            
            st.divider()
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Top categories bar chart
                top_categories = filtered_df[filtered_df['type'] == 'Debit'].groupby('category')['amount'].sum().abs().sort_values()
                
                fig_h_bar = go.Figure(data=[go.Bar(
                    y=top_categories.index,
                    x=top_categories.values,
                    orientation='h',
                    marker=dict(color='#00C6A2')
                )])
                fig_h_bar.update_layout(
                    title="Top Spending Categories",
                    xaxis_title="Amount",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FFFFFF', family='Inter')
                )
                st.plotly_chart(fig_h_bar, use_container_width=True)
            
            with col2:
                # Spending trend line chart
                trend_data = filtered_df[filtered_df['type'] == 'Debit'].copy()
                trend_data['date'] = trend_data['date'].dt.date
                daily_spending = trend_data.groupby('date')['amount'].sum().abs()
                
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(
                    x=daily_spending.index,
                    y=daily_spending.values,
                    mode='lines+markers',
                    name='Daily Spending',
                    line=dict(color='#1B4FBB', width=2),
                    marker=dict(size=6)
                ))
                fig_line.update_layout(
                    title="Spending Trend",
                    xaxis_title="Date",
                    yaxis_title="Amount",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FFFFFF', family='Inter'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            
            st.divider()
            
            # Subscription Detector
            st.markdown("### 🔄 Subscription Detector")
            
            # Group by description to find recurring charges
            recurring = {}
            for desc, group in filtered_df.groupby('description'):
                if len(group) >= 2 and group['type'].all() == 'Debit':
                    monthly_count = len(group) / (group['date'].max() - group['date'].min()).days * 30
                    if monthly_count >= 0.8:  # Appears roughly monthly
                        avg_amount = group['amount'].mean()
                        recurring[desc] = {
                            'monthly_cost': abs(avg_amount),
                            'annual_cost': abs(avg_amount) * 12,
                            'count': len(group)
                        }
            
            if recurring:
                total_subscription_cost = sum(s['monthly_cost'] for s in recurring.values())
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Monthly Subscriptions", f"{st.session_state.currency.split()[0]} {total_subscription_cost:,.0f}")
                with col2:
                    st.metric("Annual Subscription Cost", f"{st.session_state.currency.split()[0]} {total_subscription_cost * 12:,.0f}")
                
                st.divider()
                
                for desc, data in sorted(recurring.items(), key=lambda x: x[1]['monthly_cost'], reverse=True):
                    col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
                    with col1:
                        st.markdown(f"**{desc}**")
                    with col2:
                        st.text(f"📅 {data['monthly_cost']:,.0f}/mo")
                    with col3:
                        st.text(f"📆 {data['annual_cost']:,.0f}/yr")
            else:
                st.info("No recurring subscriptions detected.")
            
            st.divider()
            
            # Transaction Table
            st.markdown("### 📋 Transaction Details")
            
            # Calculate anomalies
            category_stats = filtered_df[filtered_df['type'] == 'Debit'].groupby('category')['amount'].agg(['mean', 'std']).abs()
            
            display_df = filtered_df.copy()
            display_df['Flag'] = '✅ Normal'
            
            for idx, row in display_df.iterrows():
                if row['type'] == 'Debit':
                    cat = row['category']
                    if cat in category_stats.index:
                        mean_val = category_stats.loc[cat, 'mean']
                        std_val = category_stats.loc[cat, 'std']
                        if abs(row['amount']) > mean_val + (2.5 * std_val):
                            display_df.at[idx, 'Flag'] = '🚨 Anomaly'
                        elif abs(row['amount']) > mean_val + std_val:
                            display_df.at[idx, 'Flag'] = '⚠️ Above Average'
            
            # Format for display
            display_df['Amount_Formatted'] = display_df['amount'].apply(lambda x: f"{st.session_state.currency.split()[0]} {x:,.0f}")
            display_df['Date_Formatted'] = display_df['date'].dt.strftime('%Y-%m-%d')
            
            table_data = display_df[['Date_Formatted', 'description', 'category', 'Amount_Formatted', 'Flag']].copy()
            table_data.columns = ['Date', 'Description', 'Category', 'Amount', 'Status']
            
            st.dataframe(table_data, use_container_width=True, hide_index=True)
            
            # Export button
            csv_data = table_data.to_csv(index=False)
            st.download_button(
                label="📥 Export to CSV",
                data=csv_data,
                file_name="spending_analysis.csv",
                mime="text/csv"
            )
        
        # ====================================================================
        # TAB 3: AI COACH
        # ====================================================================
        
        with tab3:
            st.markdown("### 🤖 AI Coach")
            
            # Calculate financial summary for AI
            total_income = df[df['type'] == 'Credit']['amount'].sum()
            total_expenses = abs(df[df['type'] == 'Debit']['amount'].sum())
            savings_rate = (total_income - total_expenses) / total_income * 100 if total_income > 0 else 0
            top_category = df[df['type'] == 'Debit'].groupby('category')['amount'].sum().abs().idxmax()
            subscription_count = len(recurring) if 'recurring' in locals() else 0
            
            # Financial summary for system prompt
            financial_summary = f"Monthly Income: {total_income:,.0f}, Monthly Expenses: {total_expenses:,.0f}, Top Spending: {top_category}"
            
            # Suggested questions
            st.markdown("#### 💬 Common Questions")
            suggestions = [
                "Where am I overspending?",
                f"How can I save {st.session_state.currency.split()[0]} 1,000 more per month?",
                "Which subscriptions should I cancel?",
                "Am I on track financially?",
                "Give me a 3-month savings plan",
                "How do I start investing?"
            ]
            
            cols = st.columns(len(suggestions))
            for idx, suggestion in enumerate(suggestions):
                if cols[idx].button(suggestion, key=f"q_{idx}", use_container_width=True):
                    if suggestion not in st.session_state.chat_history:
                        st.session_state.chat_history.append({"role": "user", "content": suggestion})
            
            st.divider()
            
            # Chat Interface
            st.markdown("#### 💭 Chat History")
            
            chat_container = st.container()
            
            with chat_container:
                for message in st.session_state.chat_history:
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div class="chat-message-user">
                            <div class="chat-bubble-user">{message['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message-ai">
                            <div class="chat-bubble-ai">💰 {message['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Input & Process
            st.divider()
            user_input = st.text_input("Ask FinCoach anything about your finances...", label_visibility="collapsed", key="ai_coach_input")
            
            # Only process new messages (prevent loop)
            if user_input and user_input != st.session_state.last_processed_message and not st.session_state.ai_processing:
                st.session_state.last_processed_message = user_input
                st.session_state.ai_processing = True
                
                # Add user message to history
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Get AI response with loading indicator
                with st.spinner("🤖 FinCoach is thinking..."):
                    system_msg = f"""You are FinCoach, a friendly expert personal finance coach.
User: {st.session_state.user_name}
Financial Summary: {financial_summary}
Savings Rate: {savings_rate:.1f}%
Subscriptions: {subscription_count}

Give specific, actionable advice. Use bullet points. Keep under 250 words.
End with: "💡 Educational guidance, not regulated advice."
Be warm and encouraging."""
                    
                    ai_response = call_azure_ai(user_input, system_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                
                st.session_state.ai_processing = False
                st.rerun()
            
            # Clear chat button
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
            
            st.divider()
            st.markdown("""
            <div class="danger-banner">
                <p><strong>⚠️ Disclaimer</strong></p>
                <p>FinCoach provides educational insights only. This is not regulated financial or investment advice. 
                Consult qualified professionals for major financial decisions.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # ====================================================================
        # TAB 4: GOALS TRACKER
        # ====================================================================
        
        with tab4:
            st.markdown("### 🎯 Goals Tracker")
            
            # Add Goal Form
            with st.expander("➕ Add New Goal", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    goal_name = st.text_input("Goal Name", placeholder="e.g., Emergency Fund")
                    goal_target = st.number_input("Target Amount", min_value=0)
                with col2:
                    goal_saved = st.number_input("Current Saved", min_value=0)
                    goal_date = st.date_input("Target Date")
                
                col1, col2 = st.columns(2)
                with col1:
                    goal_category = st.selectbox(
                        "Category",
                        ["Emergency Fund", "Vacation", "Home", "Car", "Education", "Investment", "Other"]
                    )
                with col2:
                    goal_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                
                if st.button("✅ Create Goal", use_container_width=True):
                    if goal_name and goal_target > 0:
                        new_goal = {
                            "name": goal_name,
                            "target": goal_target,
                            "saved": goal_saved,
                            "date": goal_date,
                            "category": goal_category,
                            "priority": goal_priority,
                            "created": pd.Timestamp.now()
                        }
                        st.session_state.goals.append(new_goal)
                        st.success(f"✅ Goal '{goal_name}' created!")
                        st.rerun()
                    else:
                        st.error("Please fill in all fields.")
            
            st.divider()
            
            # Goals Summary
            if st.session_state.goals:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Goals", len(st.session_state.goals))
                with col2:
                    on_track = sum(1 for g in st.session_state.goals if g['saved'] > 0)
                    st.metric("On Track", on_track)
                with col3:
                    total_target = sum(g['target'] for g in st.session_state.goals)
                    st.metric(f"Target Amount", f"{st.session_state.currency.split()[0]} {total_target:,.0f}")
                with col4:
                    total_saved = sum(g['saved'] for g in st.session_state.goals)
                    st.metric(f"Total Saved", f"{st.session_state.currency.split()[0]} {total_saved:,.0f}")
                
                st.divider()
                
                # Display goals
                for idx, goal in enumerate(st.session_state.goals):
                    col1, col2 = st.columns([0.9, 0.1])
                    
                    with col1:
                        progress = (goal['saved'] / goal['target'] * 100) if goal['target'] > 0 else 0
                        days_remaining = (goal['date'] - pd.Timestamp.now().date()).days
                        
                        # Status badge
                        if progress >= 100:
                            status = "✅ Complete"
                            status_color = "green"
                        elif days_remaining < 30 and progress < 80:
                            status = "🚨 Behind"
                            status_color = "red"
                        elif progress < 50:
                            status = "⚠️ At Risk"
                            status_color = "orange"
                        else:
                            status = "✅ On Track"
                            status_color = "green"
                        
                        # Monthly needed
                        if days_remaining > 0:
                            monthly_needed = (goal['target'] - goal['saved']) / (days_remaining / 30)
                        else:
                            monthly_needed = 0
                        
                        st.markdown(f"""
                        <div class="card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h4 style="margin: 0;">{goal['name']}</h4>
                                    <p style="color: #9FA6B2; margin: 0.25rem 0 0 0;">{goal['category']} • Priority: {goal['priority']}</p>
                                </div>
                                <span class="badge-pill badge-success">{status}</span>
                            </div>
                            <div style="margin-top: 1rem;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                    <span>{st.session_state.currency.split()[0]} {goal['saved']:,.0f} / {st.session_state.currency.split()[0]} {goal['target']:,.0f}</span>
                                    <span>{progress:.0f}%</span>
                                </div>
                                <div style="background-color: #1E2130; border-radius: 8px; height: 8px; overflow: hidden;">
                                    <div style="background: linear-gradient(90deg, #00C6A2, #1B4FBB); height: 100%; width: {progress:.0f}%; border-radius: 8px;"></div>
                                </div>
                            </div>
                            <div style="margin-top: 1rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.875rem;">
                                <div>
                                    <p style="color: #9FA6B2; margin: 0;">Days Remaining</p>
                                    <p style="margin: 0.25rem 0 0 0;"><strong>{days_remaining} days</strong></p>
                                </div>
                                <div>
                                    <p style="color: #9FA6B2; margin: 0;">Monthly Needed</p>
                                    <p style="margin: 0.25rem 0 0 0;"><strong>{st.session_state.currency.split()[0]} {monthly_needed:,.0f}</strong></p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("🗑️", key=f"delete_goal_{idx}"):
                            st.session_state.goals.pop(idx)
                            st.rerun()
            else:
                st.info("No goals yet. Create your first goal to get started!")
        
        # ====================================================================
        # TAB 5: INVESTMENTS
        # ====================================================================
        
        with tab5:
            st.markdown("### 📈 Investments")
            
            st.markdown("""
            <div class="warning-banner">
                <p><strong>📌 Disclaimer</strong></p>
                <p>Investment information is for educational purposes only. Not regulated financial advice.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Risk Profile Assessment
            st.markdown("#### 🎯 Risk Profile Assessment")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                time_horizon = st.slider("Investment Time Horizon (years)", 1, 30, 10)
            with col2:
                risk_tolerance = st.select_slider("Risk Tolerance", ["Very Low", "Low", "Medium", "High", "Very High"], value="Medium")
            with col3:
                monthly_investable = st.number_input("Monthly Investable Surplus", min_value=0, value=1000)
            
            col1, col2 = st.columns(2)
            with col1:
                existing_investments = st.number_input("Existing Investments", min_value=0)
            with col2:
                investment_goals = st.multiselect(
                    "Financial Goals",
                    ["Retirement", "Education", "Home", "Emergency Fund", "Wealth Growth"],
                    default=["Wealth Growth"]
                )
            
            st.divider()
            
            # Determine risk profile
            risk_map = {"Very Low": 0, "Low": 1, "Medium": 2, "High": 3, "Very High": 4}
            risk_score = risk_map[risk_tolerance] + (time_horizon / 30 * 2)
            
            if risk_score < 2:
                profile = "Conservative"
                allocation = {"Bonds": 60, "Stocks": 25, "Gold": 15}
                color_scheme = ["#27AE60", "#1B4FBB", "#F5A623"]
            elif risk_score < 4:
                profile = "Moderate"
                allocation = {"Stocks": 40, "Bonds": 30, "Gold": 20, "Crypto": 10}
                color_scheme = ["#1B4FBB", "#27AE60", "#F5A623", "#E03E3E"]
            else:
                profile = "Aggressive"
                allocation = {"Stocks": 70, "Crypto": 15, "Gold": 10, "Bonds": 5}
                color_scheme = ["#E03E3E", "#1B4FBB", "#F5A623", "#27AE60"]
            
            st.markdown(f"**Your Risk Profile: {profile}**")
            
            # Asset Allocation
            st.markdown("#### 📊 Suggested Asset Allocation")
            
            fig_alloc = go.Figure(data=[go.Pie(
                labels=list(allocation.keys()),
                values=list(allocation.values()),
                marker=dict(colors=color_scheme, line=dict(color='#1A1D27', width=2)),
                textinfo='label+percent'
            )])
            fig_alloc.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF', family='Inter')
            )
            st.plotly_chart(fig_alloc, use_container_width=True)
            
            st.divider()
            
            # Investment Calculator
            st.markdown("#### 💰 Investment Calculator")
            
            col1, col2 = st.columns(2)
            with col1:
                principal = st.number_input("Initial Investment", min_value=0, value=10000)
                monthly_contribution = st.number_input("Monthly Contribution", min_value=0, value=500)
            with col2:
                expected_return = st.slider("Expected Annual Return (%)", 1.0, 20.0, 8.0)
                years = st.slider("Investment Period (years)", 1, 40, 10)
            
            # Calculate compound interest
            months = years * 12
            monthly_rate = expected_return / 100 / 12
            
            # Future value of principal
            fv_principal = principal * (1 + monthly_rate) ** months
            
            # Future value of monthly contributions
            fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            
            total_value = fv_principal + fv_contributions
            total_invested = principal + (monthly_contribution * months)
            profit = total_value - total_invested
            
            # Chart
            balance_data = []
            for m in range(0, months + 1, max(1, months // 50)):
                principal_val = principal * (1 + monthly_rate) ** m
                contrib_val = monthly_contribution * (((1 + monthly_rate) ** m - 1) / monthly_rate) if m > 0 else 0
                balance_data.append(principal_val + contrib_val)
            
            fig_compound = go.Figure()
            fig_compound.add_trace(go.Scatter(
                y=balance_data,
                mode='lines',
                name='Total Value',
                line=dict(color='#00C6A2', width=3),
                fill='tozeroy',
                fillcolor='rgba(0, 198, 162, 0.1)'
            ))
            fig_compound.update_layout(
                title="Compound Interest Growth",
                xaxis_title="Months",
                yaxis_title="Value",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF', family='Inter'),
                hovermode='x unified'
            )
            st.plotly_chart(fig_compound, use_container_width=True)
            
            # Results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Invested", f"{st.session_state.currency.split()[0]} {total_invested:,.0f}")
            with col2:
                st.metric("Projected Value", f"{st.session_state.currency.split()[0]} {total_value:,.0f}")
            with col3:
                st.metric("Profit", f"{st.session_state.currency.split()[0]} {profit:,.0f}")
            
            st.divider()
            
            # Investment Education
            st.markdown("#### 📚 Investment Basics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("📊 What are ETFs?"):
                    st.write("Exchange-Traded Funds (ETFs) are baskets of stocks, bonds, or commodities traded like stocks. They offer instant diversification at low cost.")
                
                with st.expander("🏆 Gold as a Hedge"):
                    st.write("Gold historically preserves wealth during inflation and market downturns. Consider 10-15% allocation for stability.")
                
                with st.expander("🆘 Emergency Fund Basics"):
                    st.write("Keep 3-6 months of expenses in liquid, low-risk savings before investing.")
            
            with col2:
                with st.expander("📈 Dollar Cost Averaging"):
                    st.write("Investing fixed amounts regularly (monthly) reduces timing risk and emotional decisions.")
                
                with st.expander("🎯 Diversification Explained"):
                    st.write("Spread investments across asset classes, sectors, and geographies to reduce risk.")
                
                with st.expander("💡 Investment Starting Plan"):
                    st.write("1. Build emergency fund\n2. Start with low-cost index funds\n3. Gradually increase exposure\n4. Rebalance annually")
        
        # ====================================================================
        # TAB 6: BUDGET PLANNER
        # ====================================================================
        
        with tab6:
            st.markdown("### 💼 Budget Planner")
            
            if st.session_state.monthly_income > 0:
                # 50/30/20 Rule
                st.markdown("#### 📏 50/30/20 Budget Rule")
                
                needs = st.session_state.monthly_income * 0.50
                wants = st.session_state.monthly_income * 0.30
                savings = st.session_state.monthly_income * 0.20
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("50% Needs", f"{st.session_state.currency.split()[0]} {needs:,.0f}")
                with col2:
                    st.metric("30% Wants", f"{st.session_state.currency.split()[0]} {wants:,.0f}")
                with col3:
                    st.metric("20% Savings", f"{st.session_state.currency.split()[0]} {savings:,.0f}")
                
                st.divider()
                
                # Compare actual vs budget
                st.markdown("#### 📊 Actual vs Budget")
                
                actual_needs = abs(df[df['category'].isin(['🏠 Rent & Housing', '⚡ Utilities', '🛒 Groceries'])]['amount'].sum())
                actual_wants = abs(df[df['category'].isin(['🍽️ Food & Dining', '🛍️ Shopping', '🎬 Entertainment', '✈️ Travel'])]['amount'].sum())
                actual_savings = df[df['type'] == 'Credit']['amount'].sum() - abs(df[df['type'] == 'Debit']['amount'].sum())
                
                budget_data = pd.DataFrame({
                    'Category': ['Needs', 'Wants', 'Savings'],
                    'Budget': [needs, wants, savings],
                    'Actual': [actual_needs, actual_wants, max(0, actual_savings)]
                })
                
                fig_budget = go.Figure()
                fig_budget.add_trace(go.Bar(name='Budget', x=budget_data['Category'], y=budget_data['Budget'], marker_color='#1B4FBB'))
                fig_budget.add_trace(go.Bar(name='Actual', x=budget_data['Category'], y=budget_data['Actual'], marker_color='#00C6A2'))
                fig_budget.update_layout(
                    barmode='group',
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#FFFFFF', family='Inter')
                )
                st.plotly_chart(fig_budget, use_container_width=True)
                
                st.divider()
                
                # Budget Gauges
                st.markdown("#### 🎯 Budget Status")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    needs_pct = (actual_needs / needs * 100) if needs > 0 else 0
                    fig_needs = go.Figure(data=[go.Indicator(
                        mode="gauge+number",
                        value=min(needs_pct, 100),
                        title='Needs Budget',
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': '#00C6A2' if needs_pct <= 50 else '#F5A623' if needs_pct <= 60 else '#E03E3E'},
                        }
                    )])
                    fig_needs.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFFFFF'))
                    st.plotly_chart(fig_needs, use_container_width=True)
                
                with col2:
                    wants_pct = (actual_wants / wants * 100) if wants > 0 else 0
                    fig_wants = go.Figure(data=[go.Indicator(
                        mode="gauge+number",
                        value=min(wants_pct, 100),
                        title='Wants Budget',
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': '#00C6A2' if wants_pct <= 30 else '#F5A623' if wants_pct <= 40 else '#E03E3E'},
                        }
                    )])
                    fig_wants.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFFFFF'))
                    st.plotly_chart(fig_wants, use_container_width=True)
                
                with col3:
                    savings_pct = (max(0, actual_savings) / savings * 100) if savings > 0 else 0
                    fig_savings = go.Figure(data=[go.Indicator(
                        mode="gauge+number",
                        value=min(savings_pct, 100),
                        title='Savings Budget',
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': '#27AE60' if savings_pct >= 20 else '#F5A623' if savings_pct >= 10 else '#E03E3E'},
                        }
                    )])
                    fig_savings.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFFFFF'))
                    st.plotly_chart(fig_savings, use_container_width=True)
                
            else:
                st.warning("Please set your monthly income in the sidebar to see budget recommendations.")
        
        # ====================================================================
        # TAB 7: RISK REPORT
        # ====================================================================
        
        with tab7:
            st.markdown("### ⚠️ Risk Report")
            
            # Financial Health Score
            total_income = df[df['type'] == 'Credit']['amount'].sum()
            total_expenses = abs(df[df['type'] == 'Debit']['amount'].sum())
            savings_rate = (total_income - total_expenses) / total_income * 100 if total_income > 0 else 0
            
            health_score = min(100, max(0, (savings_rate / 20 * 100)))
            
            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
            
            with col2:
                fig_health = go.Figure(data=[go.Indicator(
                    mode="gauge+number",
                    value=health_score,
                    title='Financial Health Score',
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': '#00C6A2'},
                        'steps': [
                            {'range': [0, 40], 'color': 'rgba(224, 62, 62, 0.2)'},
                            {'range': [40, 70], 'color': 'rgba(245, 166, 35, 0.2)'},
                            {'range': [70, 100], 'color': 'rgba(39, 174, 96, 0.2)'}
                        ]
                    }
                )])
                fig_health.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFFFFF'))
                st.plotly_chart(fig_health, use_container_width=True)
            
            st.divider()
            
            # Risk Assessment Cards
            st.markdown("#### 🔍 Risk Assessment")
            
            # 1. Overspending Risk
            expense_ratio = total_expenses / total_income if total_income > 0 else 0
            if expense_ratio > 0.80:
                severity = "🚨 Critical"
                severity_color = "danger"
            elif expense_ratio > 0.70:
                severity = "⚠️ High"
                severity_color = "warning"
            else:
                severity = "✅ Low"
                severity_color = "success"
            
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">💸 Overspending Risk</h4>
                    <span class="badge-pill badge-{severity_color}">{severity}</span>
                </div>
                <p style="margin: 1rem 0 0 0; color: #9FA6B2;">Your expenses are {expense_ratio*100:.0f}% of income. Target: <80%</p>
                <p style="margin: 0.5rem 0 0 0;"><strong>Action:</strong> Review {df[df['type']=='Debit'].groupby('category')['amount'].sum().abs().idxmax()} category for cuts</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Emergency Fund Risk
            monthly_expenses = total_expenses
            if 'emergency_fund' not in st.session_state:
                st.session_state.emergency_fund = 0
            
            months_covered = st.session_state.emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
            
            if months_covered < 1:
                emerg_severity = "🚨 Critical"
                emerg_color = "danger"
            elif months_covered < 3:
                emerg_severity = "⚠️ High"
                emerg_color = "warning"
            else:
                emerg_severity = "✅ Good"
                emerg_color = "success"
            
            target_emergency = monthly_expenses * 6
            
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">🆘 Emergency Fund Risk</h4>
                    <span class="badge-pill badge-{emerg_color}">{emerg_severity}</span>
                </div>
                <p style="margin: 1rem 0 0 0; color: #9FA6B2;">Covers {months_covered:.1f} months of expenses. Target: 6 months</p>
                <p style="margin: 0.5rem 0 0 0;"><strong>Target Fund:</strong> {st.session_state.currency.split()[0]} {target_emergency:,.0f}</p>
                <p style="margin: 0.5rem 0 0 0;"><strong>Action:</strong> Save {st.session_state.currency.split()[0]} {(target_emergency - st.session_state.emergency_fund) / 6:,.0f}/month to reach 6-month goal</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 3. Subscription Bloat
            total_subscriptions = sum(s['monthly_cost'] for s in recurring.values()) if 'recurring' in locals() else 0
            
            sub_severity = "✅ Healthy" if total_subscriptions < (total_income * 0.05) else "⚠️ High" if total_subscriptions < (total_income * 0.10) else "🚨 Critical"
            sub_color = "success" if total_subscriptions < (total_income * 0.05) else "warning" if total_subscriptions < (total_income * 0.10) else "danger"
            
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">🔄 Subscription Bloat Risk</h4>
                    <span class="badge-pill badge-{sub_color}">{sub_severity}</span>
                </div>
                <p style="margin: 1rem 0 0 0; color: #9FA6B2;">Total monthly: {st.session_state.currency.split()[0]} {total_subscriptions:,.0f} ({total_subscriptions/total_income*100:.1f}% of income)</p>
                <p style="margin: 0.5rem 0 0 0;"><strong>Action:</strong> Review and cancel unused services. Target: <5% of income</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 4. Debt & Loan Risk
            loan_payments = abs(df[df['category'] == '💳 Finance & Banking']['amount'].sum())
            loan_ratio = loan_payments / total_income * 100 if total_income > 0 else 0
            
            loan_severity = "✅ Safe" if loan_ratio < 20 else "⚠️ Medium" if loan_ratio < 40 else "🚨 High"
            loan_color = "success" if loan_ratio < 20 else "warning" if loan_ratio < 40 else "danger"
            
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">💳 Debt & Loan Risk</h4>
                    <span class="badge-pill badge-{loan_color}">{loan_severity}</span>
                </div>
                <p style="margin: 1rem 0 0 0; color: #9FA6B2;">Debt payments: {loan_ratio:.1f}% of income. Safe: <40%</p>
                <p style="margin: 0.5rem 0 0 0;"><strong>Action:</strong> Consider debt snowball or avalanche method to reduce burden</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 5. Anomaly Risk
            category_stats = df[df['type'] == 'Debit'].groupby('category')['amount'].agg(['mean', 'std']).abs()
            anomalies = []
            
            for idx, row in df[df['type'] == 'Debit'].iterrows():
                cat = row['category']
                if cat in category_stats.index:
                    mean_val = category_stats.loc[cat, 'mean']
                    std_val = category_stats.loc[cat, 'std']
                    if abs(row['amount']) > mean_val + (2.5 * std_val):
                        anomalies.append(row)
            
            anom_severity = "✅ None" if len(anomalies) == 0 else f"⚠️ {len(anomalies)}"
            anom_color = "success" if len(anomalies) == 0 else "warning"
            
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">🚨 Anomaly Risk</h4>
                    <span class="badge-pill badge-{anom_color}">{anom_severity} unusual transactions</span>
                </div>
                <p style="margin: 1rem 0 0 0; color: #9FA6B2;">Detected {len(anomalies)} unusual transactions</p>
                <p style="margin: 0.5rem 0 0 0;"><strong>Action:</strong> Review flagged transactions in Spending Analysis tab</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Mandatory Risk Disclosures
            st.markdown("""
            <div class="danger-banner">
                <h4 style="margin-top: 0;">⚠️ IMPORTANT DISCLOSURES</h4>
                <p><strong>1. NOT FINANCIAL ADVICE</strong><br>
                FinCoach AI provides educational insights only. Nothing constitutes regulated financial or investment advice. 
                Consult a qualified financial advisor for major decisions.</p>
                
                <p><strong>2. AI LIMITATIONS</strong><br>
                AI-generated insights may contain errors or omissions. Always verify important information independently.</p>
                
                <p><strong>3. DATA ACCURACY</strong><br>
                Analysis is only as accurate as data provided. Ensure your uploaded statements are complete and correct.</p>
                
                <p><strong>4. NO DATA STORAGE</strong><br>
                Your financial data is NEVER stored, sold, or shared with third parties. All data exists only for the duration of your session.</p>
                
                <p><strong>5. INVESTMENT RISK</strong><br>
                All investments carry risk of loss. Past performance does not guarantee future results.</p>
                
                <p><strong>6. SESSION PRIVACY</strong><br>
                Each user session is fully isolated. No data persists between sessions.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # ====================================================================
        # TAB 8: TAX SUMMARY
        # ====================================================================
        
        with tab8:
            st.markdown("### 🧾 Tax Summary")
            
            st.markdown("""
            <div class="warning-banner">
                <p><strong>📌 Disclaimer</strong></p>
                <p>This is a general overview. Consult a tax professional for accurate advice specific to your jurisdiction.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Year overview
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            
            st.markdown("#### 📅 Income Summary")
            
            annual_income = df[df['type'] == 'Credit']['amount'].sum()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Annual Income", f"{st.session_state.currency.split()[0]} {annual_income:,.0f}")
            with col2:
                st.metric("Monthly Average", f"{st.session_state.currency.split()[0]} {annual_income/6:,.0f}")
            with col3:
                st.metric("Income Sources", len(df[df['type'] == 'Credit']['description'].unique()))
            
            st.divider()
            
            # Income by month
            income_monthly = df[df['type'] == 'Credit'].groupby('month')['amount'].sum()
            
            fig_income = go.Figure()
            fig_income.add_trace(go.Bar(
                x=income_monthly.index,
                y=income_monthly.values,
                marker=dict(color='#27AE60'),
                name='Monthly Income'
            ))
            fig_income.update_layout(
                title="Income by Month",
                xaxis_title="Month",
                yaxis_title="Amount",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF', family='Inter')
            )
            st.plotly_chart(fig_income, use_container_width=True)
            
            st.divider()
            
            # Deductible Expenses Overview
            st.markdown("#### 🧮 Potential Deductible Expenses")
            
            deductible_categories = ['📚 Education', '🏥 Healthcare', '💼 Finance & Banking']
            deductible_amount = abs(df[df['category'].isin(deductible_categories)]['amount'].sum())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Potentially Deductible", f"{st.session_state.currency.split()[0]} {deductible_amount:,.0f}")
            with col2:
                st.metric("Education Expenses", f"{st.session_state.currency.split()[0]} {abs(df[df['category']=='📚 Education']['amount'].sum()):,.0f}")
            with col3:
                st.metric("Healthcare Expenses", f"{st.session_state.currency.split()[0]} {abs(df[df['category']=='🏥 Healthcare']['amount'].sum()):,.0f}")
            
            st.info("💡 **Note:** Deductibility varies by country/jurisdiction. Consult your tax advisor for details.")
            
            st.divider()
            
            # Tax Calendar
            st.markdown("#### 📆 Important Tax Dates")
            
            tax_dates = {
                "Q1 Estimated Tax": "April 15",
                "Q2 Estimated Tax": "June 15",
                "Q3 Estimated Tax": "September 15",
                "Q4 Estimated Tax": "January 15 (next year)",
                "Annual Tax Return": "April 15 (next year)",
                "End of Tax Year": "December 31"
            }
            
            for event, date in tax_dates.items():
                st.markdown(f"**{event}** — {date}")
            
            st.divider()
            
            # Annual Report
            st.markdown("#### 📊 Annual Financial Report")
            
            total_income_annual = df[df['type'] == 'Credit']['amount'].sum()
            total_expenses_annual = abs(df[df['type'] == 'Debit']['amount'].sum())
            net_income = total_income_annual - total_expenses_annual
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Income", f"{st.session_state.currency.split()[0]} {total_income_annual:,.0f}")
            with col2:
                st.metric("Total Expenses", f"{st.session_state.currency.split()[0]} {total_expenses_annual:,.0f}")
            with col3:
                st.metric("Net Income", f"{st.session_state.currency.split()[0]} {net_income:,.0f}")
            with col4:
                st.metric("Months of Data", len(df['month'].unique()))
            
            st.divider()
            
            # Export Report
            report_data = pd.DataFrame({
                'Metric': ['Total Income', 'Total Expenses', 'Net Income', 'Months', 'Average Monthly Income'],
                'Amount': [total_income_annual, total_expenses_annual, net_income, len(df['month'].unique()), total_income_annual / 6]
            })
            
            csv_report = report_data.to_csv(index=False)
            st.download_button(
                label="📥 Export Annual Report",
                data=csv_report,
                file_name="tax_summary_report.csv",
                mime="text/csv"
            )

else:
    # Welcome Screen
    st.markdown(f"""
    <div class="gradient-header" style="text-align: center; padding: 3rem;">
        <h1 style="font-size: 3rem; margin: 0;">💰 FinCoach AI</h1>
        <p style="font-size: 1.25rem; margin: 1rem 0;">Your Smart Personal Finance Coach</p>
        <p style="font-size: 1rem; color: rgba(255,255,255,0.8); margin: 1rem 0;">Powered by Azure AI & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
    with col2:
        st.markdown("""
        ### 🚀 Get Started
        
        Choose one of the options in the sidebar:
        
        1. **📁 Upload Bank Statement** — Analyze your real transactions
           - CSV format required
           - Max 10,000 transactions
           - Data never stored
        
        2. **🎮 Load Demo Data** — See FinCoach in action
           - 6 months of realistic transactions
           - Fully interactive demo
           - Perfect for exploration
        
        ### ✨ Features
        
        Once you load data, unlock:
        - 📊 **Dashboard** — Financial overview & insights
        - 💸 **Spending Analysis** — Deep dive into categories & trends
        - 🤖 **AI Coach** — Get personalized financial advice
        - 🎯 **Goals Tracker** — Track progress toward your dreams
        - 📈 **Investments** — Learn and plan investment strategy
        - 💼 **Budget Planner** — 50/30/20 and custom budgets
        - ⚠️ **Risk Report** — Identify financial risks
        - 🧾 **Tax Summary** — Annual financial overview
        
        ### 🔒 Your Privacy
        
        - **Zero Storage** — Data only exists during your session
        - **No Tracking** — Complete anonymity
        - **Session-Only** — Everything clears when you close
        - **AI-Powered** — Azure AI for smart insights
        """)
