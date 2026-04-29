import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
import sqlite3
import re
import json
import pdfplumber

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="FinCoach AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SIMPLIFIED LIGHTWEIGHT THEME
# ============================================================================

CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    * { font-family: 'Inter', sans-serif; }
    body { background-color: #0F1117; color: #FFFFFF; }
    
    .gradient-header {
        background: linear-gradient(135deg, #1B4FBB 0%, #00C6A2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .card {
        background-color: #1A1D27;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 0.75rem;
    }
    
    .signup-form {
        background-color: #1A1D27;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid rgba(0, 198, 162, 0.3);
        max-width: 400px;
        margin: 2rem auto;
    }
    
    .metric-box {
        background-color: #1A1D27;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .gradient-header { padding: 1rem; }
        .card { padding: 0.75rem; }
        .signup-form { padding: 1.5rem; max-width: 100%; }
        .stMetric { padding: 0.5rem; }
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_database():
    """Create SQLite database for users."""
    conn = sqlite3.connect('fincoach_users.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        contact TEXT NOT NULL,
        signup_date TEXT NOT NULL,
        account_type TEXT DEFAULT 'free'
    )''')
    
    conn.commit()
    return conn

def get_user_count():
    """Get total number of registered users."""
    try:
        conn = sqlite3.connect('fincoach_users.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM users')
        count = c.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def register_user(email, contact):
    """Register new user if under 100 limit."""
    try:
        if get_user_count() >= 100:
            return False, "❌ Free tier limit reached (100 users). Please try again later."
        
        conn = sqlite3.connect('fincoach_users.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO users (email, contact, signup_date, account_type) 
                     VALUES (?, ?, ?, 'free')''',
                  (email, contact, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True, f"✅ Welcome! You're user #{get_user_count()} of 100 free users."
    except sqlite3.IntegrityError:
        return False, "❌ This email is already registered."
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_contact(contact):
    """Validate contact number (10-15 digits)."""
    contact = contact.replace('+', '').replace('-', '').replace(' ', '')
    return contact.isdigit() and 10 <= len(contact) <= 15

# ============================================================================
# CATEGORY & TRANSACTION FUNCTIONS
# ============================================================================

CATEGORY_KEYWORDS = {
    "🍽️ Food": ["restaurant", "cafe", "talabat", "deliveroo", "food", "dining"],
    "🛒 Shopping": ["amazon", "noon", "mall", "zara", "shopping"],
    "🚗 Transport": ["uber", "careem", "taxi", "petrol", "parking"],
    "🏠 Housing": ["rent", "mortgage", "property", "maintenance"],
    "⚡ Utilities": ["dewa", "etisalat", "electric", "water", "internet"],
    "🎬 Entertainment": ["netflix", "spotify", "cinema", "gaming"],
    "🏥 Healthcare": ["pharmacy", "hospital", "clinic", "medical"],
    "💰 Income": ["salary", "credit", "payment received", "bonus"],
}

def categorize_transaction(description):
    """Categorize transaction by keyword matching."""
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "📦 Other"

def generate_demo_data(monthly_income=6600):
    """Generate 6 months of demo transactions."""
    np.random.seed(42)
    transactions = []
    base_date = pd.Timestamp.now() - pd.DateOffset(months=6)
    
    expense_scale = monthly_income / 8500
    
    for i in range(6):
        transactions.append({
            'Date': base_date + pd.DateOffset(months=i, day=1),
            'Description': 'Monthly Salary',
            'Amount': monthly_income,
            'Type': 'Credit'
        })
    
    expense_templates = [
        ('Groceries', int(-280 * expense_scale), 4),
        ('Restaurant', int(-200 * expense_scale), 6),
        ('Utilities', int(-320 * expense_scale), 6),
        ('Transport', int(-150 * expense_scale), 8),
        ('Shopping', int(-180 * expense_scale), 4),
        ('Entertainment', -100, 6),
        ('Rent', int(-3000 * expense_scale), 6),
    ]
    
    for desc, amount, count in expense_templates:
        for _ in range(count):
            random_day = np.random.randint(1, 28)
            random_month = np.random.randint(0, 6)
            transactions.append({
                'Date': base_date + pd.DateOffset(months=random_month, day=random_day),
                'Description': desc,
                'Amount': amount + np.random.randint(-5, 5),
                'Type': 'Debit'
            })
    
    df = pd.DataFrame(transactions)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Category'] = df['Description'].apply(categorize_transaction)
    df = df.sort_values('Date').reset_index(drop=True)
    return df

def parse_csv(uploaded_file):
    """Parse CSV file."""
    try:
        df = pd.read_csv(uploaded_file)
        cols_lower = [c.lower() for c in df.columns]
        
        if not any(kw in cols_lower for kw in ['date', 'description', 'amount']):
            return None, "❌ CSV must have: Date, Description, Amount columns"
        
        df.columns = [c.lower() for c in df.columns]
        if 'amount' not in df.columns:
            return None, "❌ Missing Amount column"
        
        df['Date'] = pd.to_datetime(df[[col for col in df.columns if 'date' in col][0]], errors='coerce')
        df = df.dropna(subset=['Date'])
        df['Category'] = df[[col for col in df.columns if 'description' in col][0]].apply(categorize_transaction)
        
        return df[['Date', 'Description', 'Amount', 'Category']], "✅ CSV loaded"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

def parse_pdf(uploaded_file):
    """Parse PDF bank statement."""
    try:
        transactions = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            if row and len(row) >= 3:
                                try:
                                    transactions.append({
                                        'Date': pd.to_datetime(str(row[0]).strip()),
                                        'Description': str(row[1]).strip(),
                                        'Amount': float(str(row[2]).strip().replace(',', '')),
                                        'Category': categorize_transaction(str(row[1]).strip())
                                    })
                                except:
                                    continue
        
        if not transactions:
            return None, "❌ No transaction data found in PDF"
        
        df = pd.DataFrame(transactions)
        return df, "✅ PDF loaded"
    except Exception as e:
        return None, f"❌ Error parsing PDF: {str(e)}"

# ============================================================================
# AI COACH FUNCTION
# ============================================================================

def call_azure_ai(prompt, user_name, financial_summary):
    """Call Azure AI for coaching."""
    try:
        endpoint = st.secrets.get("AZURE_API_ENDPOINT", "")
        api_key = st.secrets.get("AZURE_API_KEY", "")
        
        if not endpoint or not api_key:
            return "💡 Demo response: Focus on reducing housing and transportation costs. Set a 20% savings goal."
        
        headers = {"Content-Type": "application/json", "api-key": api_key}
        payload = {
            "model": "Phi-4",
            "messages": [
                {"role": "system", "content": f"You are FinCoach, a financial advisor. User: {user_name}. {financial_summary}"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=15)
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "💡 Unable to connect to AI. Try demo mode or check your internet."

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'mode' not in st.session_state:
    st.session_state.mode = 'auth'  # auth, demo, data
if 'df' not in st.session_state:
    st.session_state.df = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = "User"
if 'monthly_income' not in st.session_state:
    st.session_state.monthly_income = 0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize database
init_database()

# ============================================================================
# AUTH PAGE
# ============================================================================

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="gradient-header">
            <h1>💰 FinCoach AI</h1>
            <p>Smart Personal Finance Coach</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Sign Up", "📱 Demo"])
        
        with tab1:
            st.markdown(f"""
            <div class="card">
                <h3>Create Account</h3>
                <p>Free tier: {min(get_user_count(), 100)}/100 users registered</p>
            </div>
            """, unsafe_allow_html=True)
            
            email = st.text_input("📧 Email Address", placeholder="your@email.com")
            contact = st.text_input("📱 Contact Number", placeholder="+971501234567")
            
            if st.button("✅ Sign Up", use_container_width=True):
                if not email:
                    st.error("❌ Please enter email")
                elif not validate_email(email):
                    st.error("❌ Invalid email format")
                elif not contact:
                    st.error("❌ Please enter contact number")
                elif not validate_contact(contact):
                    st.error("❌ Invalid contact (10-15 digits)")
                else:
                    success, message = register_user(email, contact)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.mode = 'data'
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        with tab2:
            st.markdown("""
            <div class="card">
                <h3>Try Demo Account</h3>
                <p>Use demo data or enter your info manually</p>
            </div>
            """, unsafe_allow_html=True)
            
            demo_name = st.text_input("👤 Your Name", placeholder="John Doe", key="demo_name")
            demo_income = st.number_input("💰 Monthly Income", min_value=1000, value=6600, step=100)
            currency = st.selectbox("💵 Currency", ["AED", "USD", "EUR", "GBP"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Load Demo Data", use_container_width=True):
                    if not demo_name:
                        st.error("❌ Enter your name")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user_email = "demo@fincoach.app"
                        st.session_state.user_name = demo_name
                        st.session_state.monthly_income = demo_income
                        st.session_state.df = generate_demo_data(demo_income)
                        st.session_state.mode = 'data'
                        st.success(f"✅ Welcome, {demo_name}!")
                        st.rerun()
            
            with col2:
                if st.button("➕ Enter Manual Data", use_container_width=True):
                    if not demo_name:
                        st.error("❌ Enter your name")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user_email = "demo@fincoach.app"
                        st.session_state.user_name = demo_name
                        st.session_state.monthly_income = demo_income
                        st.session_state.mode = 'data'
                        st.rerun()

# ============================================================================
# MAIN APP
# ============================================================================

else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.markdown(f"📧 {st.session_state.user_email}")
        st.divider()
        
        st.markdown("### ⚙️ Settings")
        user_name = st.text_input("Name", value=st.session_state.user_name)
        monthly_income = st.number_input("Monthly Income", value=st.session_state.monthly_income, min_value=0)
        
        if st.button("🔄 Update Profile"):
            st.session_state.user_name = user_name
            st.session_state.monthly_income = monthly_income
            st.success("✅ Profile updated")
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.df = None
            st.session_state.chat_history = []
            st.rerun()
    
    # Main content
    st.markdown(f"""
    <div class="gradient-header">
        <h1>Welcome, {st.session_state.user_name}! 👋</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Data section
    if st.session_state.df is None:
        st.info("📊 Upload data to get started")
        
        col1, col2 = st.columns(2)
        with col1:
            uploaded_csv = st.file_uploader("📄 Upload CSV", type=['csv'])
            if uploaded_csv:
                df, msg = parse_csv(uploaded_csv)
                if df is not None:
                    st.session_state.df = df
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        with col2:
            uploaded_pdf = st.file_uploader("📄 Upload PDF", type=['pdf'])
            if uploaded_pdf:
                df, msg = parse_pdf(uploaded_pdf)
                if df is not None:
                    st.session_state.df = df
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        if st.button("🎮 Load Demo Data", use_container_width=True):
            st.session_state.df = generate_demo_data(st.session_state.monthly_income)
            st.success("✅ Demo data loaded")
            st.rerun()
    
    else:
        # Tabs
        df = st.session_state.df.copy()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💬 AI Coach", "📁 Data", "❓ Help"])
        
        # TAB 1: Dashboard
        with tab1:
            total_income = df[df['Description'].str.lower().str.contains('salary|credit|income', na=False)]['Amount'].sum()
            total_expenses = abs(df[df['Amount'] < 0]['Amount'].sum())
            net_savings = total_income - total_expenses
            savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""<div class="metric-box"><h4>💰 Income</h4><p style="font-size:24px">{total_income:,.0f}</p></div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="metric-box"><h4>💸 Expenses</h4><p style="font-size:24px">{total_expenses:,.0f}</p></div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class="metric-box"><h4>🎯 Savings</h4><p style="font-size:24px">{net_savings:,.0f}</p></div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""<div class="metric-box"><h4>📈 Rate</h4><p style="font-size:24px">{savings_rate:.1f}%</p></div>""", unsafe_allow_html=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                category_spending = df[df['Amount'] < 0].groupby('Category')['Amount'].sum().abs().sort_values(ascending=False)
                fig_pie = px.pie(values=category_spending.values, names=category_spending.index, 
                                 title="Spending by Category", hole=0.3)
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                monthly = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum()
                fig_bar = px.bar(y=monthly.values, x=monthly.index.astype(str), 
                                title="Monthly Cash Flow", labels={'y': 'Amount', 'x': 'Month'})
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # TAB 2: AI Coach
        with tab2:
            st.markdown("### 💬 Ask Your AI Coach")
            
            total_income = df[df['Description'].str.lower().str.contains('salary|credit|income', na=False)]['Amount'].sum()
            total_expenses = abs(df[df['Amount'] < 0]['Amount'].sum())
            top_category = df[df['Amount'] < 0].groupby('Category')['Amount'].sum().abs().idxmax()
            
            financial_summary = f"Total Income: {total_income:,.0f}, Total Expenses: {total_expenses:,.0f}, Top Category: {top_category}"
            
            suggestions = [
                "How can I save more?",
                "Where am I overspending?",
                "Is my savings rate healthy?",
                "How to reduce expenses?"
            ]
            
            st.write("**Quick Questions:**")
            cols = st.columns(2)
            for idx, suggestion in enumerate(suggestions):
                with cols[idx % 2]:
                    if st.button(suggestion, use_container_width=True):
                        st.session_state.chat_history.append({"role": "user", "content": suggestion})
            
            st.divider()
            
            # Chat display
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown(f"**Coach:** {msg['content']}")
            
            # Input
            user_input = st.text_input("Ask a question...")
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                with st.spinner("🤖 Thinking..."):
                    response = call_azure_ai(user_input, st.session_state.user_name, financial_summary)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                st.rerun()
        
        # TAB 3: Data
        with tab3:
            st.markdown("### 📊 Your Transactions")
            st.dataframe(df, use_container_width=True, height=400)
            
            csv = df.to_csv(index=False).encode()
            st.download_button("📥 Download CSV", csv, "transactions.csv", "text/csv")
            
            if st.button("🗑️ Clear Data"):
                st.session_state.df = None
                st.rerun()
        
        # TAB 4: Help
        with tab4:
            st.markdown("""
            ### ❓ Frequently Asked Questions
            
            **How does FinCoach work?**
            - Upload your bank statement or use demo data
            - AI Coach analyzes your spending patterns
            - Get personalized financial recommendations
            
            **What data do we collect?**
            - Email and contact (for free tier tracking)
            - Your transactions (stored locally)
            - Anonymous usage stats
            
            **Is my data safe?**
            - Data is encrypted and stored securely
            - We never sell your information
            - Delete anytime from settings
            
            **How is it free?**
            - First 100 users get premium features free
            - After 100, premium subscription available
            - Demo mode always free
            """)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #9FA6B2; font-size: 0.85rem;">
📊 FinCoach AI | 🔒 Secure | 💼 Personal Finance Made Simple<br>
For support: support@fincoach.app
</div>
""", unsafe_allow_html=True)
