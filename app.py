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
# SIMPLIFIED LIGHTWEIGHT THEME (Inspired by YNAB, Mint, Personal Capital)
# ============================================================================

CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    * { font-family: 'Inter', sans-serif; }
    body { background-color: #0F1117; color: #FFFFFF; }
    
    .gradient-header {
        background: linear-gradient(135deg, #1B4FBB 0%, #00C6A2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .card {
        background-color: #1A1D27;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 0.75rem;
    }
    
    .metric-box {
        background-color: #1A1D27;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border-left: 4px solid #00C6A2;
        transition: transform 0.2s;
    }
    
    .metric-box:hover {
        transform: translateY(-2px);
    }
    
    .modal-signup {
        background-color: #1A1D27;
        padding: 2.5rem;
        border-radius: 12px;
        border: 1px solid rgba(0, 198, 162, 0.3);
        max-width: 450px;
        margin: 2rem auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .chat-bubble {
        background-color: #1B4FBB;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        max-width: 85%;
    }
    
    .chat-bubble-ai {
        background-color: #00C6A2;
        color: #0F1117;
        margin-left: auto;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .gradient-header { padding: 1rem; }
        .card { padding: 0.75rem; }
        .modal-signup { padding: 1.5rem; max-width: 100%; }
        .metric-box { padding: 1rem; }
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
    "🛒 Shopping": ["amazon", "noon", "mall", "zara", "shopping", "store"],
    "🚗 Transport": ["uber", "careem", "taxi", "petrol", "parking", "transport"],
    "🏠 Housing": ["rent", "mortgage", "property", "maintenance", "utilities"],
    "⚡ Utilities": ["dewa", "etisalat", "electric", "water", "internet", "phone"],
    "🎬 Entertainment": ["netflix", "spotify", "cinema", "gaming", "entertainment"],
    "🏥 Healthcare": ["pharmacy", "hospital", "clinic", "medical", "health"],
    "💰 Income": ["salary", "credit", "payment received", "bonus", "income"],
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
        
        date_col = [col for col in df.columns if 'date' in col][0]
        desc_col = [col for col in df.columns if 'description' in col][0]
        
        df['Date'] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=['Date'])
        df['Description'] = df[desc_col]
        df['Category'] = df['Description'].apply(categorize_transaction)
        
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

def create_empty_6month_dataframe():
    """Create an empty 6-month expense template dataframe."""
    base_date = pd.Timestamp.now() - pd.DateOffset(months=5)
    months = pd.date_range(start=base_date, periods=6, freq='M')
    
    transactions = []
    for month in months:
        transactions.append({
            'Date': month.replace(day=1),
            'Description': 'Monthly Income',
            'Amount': 0,
            'Category': '💰 Income',
            'Type': 'Income'
        })
    
    return pd.DataFrame(transactions)

def generate_monthly_expense_summary(months_count=6):
    """Generate a summary template for 6 months with common expense categories."""
    base_date = pd.Timestamp.now() - pd.DateOffset(months=months_count-1)
    months = pd.date_range(start=base_date.replace(day=1), periods=months_count, freq='M')
    
    month_labels = [m.strftime('%B %Y') for m in months]
    
    default_categories = {
        "🍽️ Food": 300,
        "🛒 Shopping": 200,
        "🚗 Transport": 150,
        "🏠 Housing": 1500,
        "⚡ Utilities": 300,
        "🎬 Entertainment": 100,
        "🏥 Healthcare": 100,
    }
    
    return {
        "months": month_labels,
        "month_dates": months,
        "categories": default_categories
    }

# ============================================================================
# AI COACH FUNCTION
# ============================================================================

def call_azure_ai(prompt, user_name, financial_summary):
    """Call Azure AI for coaching."""
    try:
        endpoint = st.secrets.get("AZURE_API_ENDPOINT", "")
        api_key = st.secrets.get("AZURE_API_KEY", "")
        
        if not endpoint or not api_key:
            return "💡 Demo response: Based on your spending, I recommend: 1) Reduce discretionary spending by 15%, 2) Set up automatic savings, 3) Review subscription services. Your savings potential: 20-25% of income."
        
        headers = {"Content-Type": "application/json", "api-key": api_key}
        payload = {
            "model": "Phi-4",
            "messages": [
                {"role": "system", "content": f"You are FinCoach, a financial advisor. User: {user_name}. {financial_summary}. Provide actionable advice."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=15)
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "💡 Demo response: Unable to connect to AI. Try upgrading your internet connection."

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = "User"
if 'monthly_income' not in st.session_state:
    st.session_state.monthly_income = 0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'manual_entry_mode' not in st.session_state:
    st.session_state.manual_entry_mode = False
if 'monthly_expenses' not in st.session_state:
    st.session_state.monthly_expenses = None

# Initialize database
init_database()

# ============================================================================
# SIGNUP MODAL (SEPARATE WINDOW)
# ============================================================================

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="gradient-header">
            <h1>💰 FinCoach AI</h1>
            <p style="font-size: 1.1rem; margin-top: 0.5rem;">Smart Personal Finance Made Simple</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Signup Tab
        st.markdown(f"""
        <div class="modal-signup">
            <h2>✨ Create Your Account</h2>
            <p style="color: #00C6A2; margin-bottom: 1rem;">Free tier: {min(get_user_count(), 100)}/100 users • No credit card required</p>
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("📧 Email Address", placeholder="you@example.com", key="signup_email")
        contact = st.text_input("📱 Contact Number", placeholder="+971 50 123 4567", key="signup_contact")
        
        if st.button("✅ Create Account", use_container_width=True, key="signup_btn"):
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
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        st.divider()
        st.markdown("#### 🎮 Or Try Demo Account")
        
        demo_name = st.text_input("👤 Your Name", placeholder="John Doe", key="demo_name_modal")
        demo_income = st.number_input("💰 Monthly Income", min_value=1000, value=6600, step=100, key="demo_income_modal")
        
        if st.button("📊 Demo Data", use_container_width=True, key="demo_data_btn"):
            name = demo_name if demo_name else "Demo User"
            st.session_state.authenticated = True
            st.session_state.user_email = "demo@fincoach.app"
            st.session_state.user_name = name
            st.session_state.monthly_income = demo_income
            st.session_state.df = generate_demo_data(demo_income)
            st.success(f"✅ Welcome, {name}!")
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
        user_name = st.text_input("Name", value=st.session_state.user_name, key="sidebar_name")
        monthly_income = st.number_input("Monthly Income", value=st.session_state.monthly_income, min_value=0, key="sidebar_income")
        
        if st.button("🔄 Update Profile", use_container_width=True):
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
        <h1>Welcome back, {st.session_state.user_name}! 👋</h1>
        <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data section
    if st.session_state.df is None:
        if st.session_state.manual_entry_mode:
            st.info("📝 Enter your expenses for the last 6 months to get started")
            
            with st.expander("📋 Quick Entry - Monthly Expense Summary", expanded=True):
                st.markdown("### 💰 Income & Expenses by Month")
                
                template = generate_monthly_expense_summary(6)
                months = template["months"]
                month_dates = template["month_dates"]
                default_categories = template["categories"]
                
                # Monthly income section
                st.markdown("#### 📊 Monthly Income")
                income_cols = st.columns(3)
                monthly_incomes = {}
                for idx, month in enumerate(months):
                    with income_cols[idx % 3]:
                        monthly_incomes[month] = st.number_input(
                            f"{month}",
                            value=int(st.session_state.monthly_income),
                            min_value=0,
                            step=100,
                            key=f"income_{idx}"
                        )
                
                st.divider()
                
                # Expense categories section
                st.markdown("#### 💸 Expenses by Category")
                expense_data = {}
                
                for category in default_categories.keys():
                    st.markdown(f"**{category}**")
                    cols = st.columns(3)
                    
                    for idx, month in enumerate(months):
                        with cols[idx % 3]:
                            if category not in expense_data:
                                expense_data[category] = {}
                            
                            amount = st.number_input(
                                f"{month}",
                                value=-default_categories[category],
                                min_value=-100000,
                                max_value=0,
                                step=-10,
                                key=f"expense_{category}_{idx}"
                            )
                            expense_data[category][month] = amount
                
                st.divider()
                
                if st.button("✅ Create Expense Data from Summary", use_container_width=True):
                    transactions = []
                    
                    # Add income transactions
                    for idx, (month, income) in enumerate(monthly_incomes.items()):
                        if income > 0:
                            transactions.append({
                                'Date': month_dates[idx],
                                'Description': 'Monthly Income',
                                'Amount': income,
                                'Category': '💰 Income'
                            })
                    
                    # Add expense transactions
                    for category, months_data in expense_data.items():
                        for idx, (month, amount) in enumerate(months_data.items()):
                            if amount != 0:
                                transactions.append({
                                    'Date': month_dates[idx],
                                    'Description': category.split()[1] if len(category.split()) > 1 else category,
                                    'Amount': amount,
                                    'Category': category
                                })
                    
                    df_manual = pd.DataFrame(transactions)
                    df_manual['Date'] = pd.to_datetime(df_manual['Date'])
                    st.session_state.df = df_manual.sort_values('Date').reset_index(drop=True)
                    st.session_state.manual_entry_mode = False
                    st.success("✅ Expense data created successfully!")
                    st.rerun()
            
            st.divider()
            st.markdown("### 📄 Or Use Other Methods")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 📄 Upload CSV")
                uploaded_csv = st.file_uploader("Choose CSV file", type=['csv'], key="csv_upload")
                if uploaded_csv:
                    df, msg = parse_csv(uploaded_csv)
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.manual_entry_mode = False
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col2:
                st.markdown("#### 📄 Upload PDF")
                uploaded_pdf = st.file_uploader("Choose PDF file", type=['pdf'], key="pdf_upload")
                if uploaded_pdf:
                    df, msg = parse_pdf(uploaded_pdf)
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.manual_entry_mode = False
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col3:
                st.markdown("#### 🎮 Demo Data")
                if st.button("Load Sample Data", use_container_width=True, key="load_demo"):
                    st.session_state.df = generate_demo_data(st.session_state.monthly_income)
                    st.session_state.manual_entry_mode = False
                    st.success("✅ Demo data loaded")
                    st.rerun()
        
        else:
            st.info("📊 Upload your bank statement, add expenses manually, or load sample data to get started")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("#### 📝 Manual Entry")
                if st.button("Add Expenses", use_container_width=True, key="manual_entry_btn_main"):
                    st.session_state.manual_entry_mode = True
                    st.rerun()
            
            with col2:
                st.markdown("#### 📄 Upload CSV")
                uploaded_csv = st.file_uploader("Choose CSV file", type=['csv'], key="csv_upload")
                if uploaded_csv:
                    df, msg = parse_csv(uploaded_csv)
                    if df is not None:
                        st.session_state.df = df
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col3:
                st.markdown("#### 📄 Upload PDF")
                uploaded_pdf = st.file_uploader("Choose PDF file", type=['pdf'], key="pdf_upload")
                if uploaded_pdf:
                    df, msg = parse_pdf(uploaded_pdf)
                    if df is not None:
                        st.session_state.df = df
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col4:
                st.markdown("#### 🎮 Demo Data")
                if st.button("Load Sample Data", use_container_width=True, key="load_demo"):
                    st.session_state.df = generate_demo_data(st.session_state.monthly_income)
                    st.success("✅ Demo data loaded")
                    st.rerun()
    
    else:
        # Tabs
        df = st.session_state.df.copy()
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💬 AI Coach", "➕ Add Expense", "📁 Data"])
        
        # TAB 1: Dashboard
        with tab1:
            total_income = df[df['Description'].str.lower().str.contains('salary|credit|income', na=False)]['Amount'].sum()
            total_expenses = abs(df[df['Amount'] < 0]['Amount'].sum())
            net_savings = total_income - total_expenses
            savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""<div class="metric-box"><h4>💰 Income</h4><p style="font-size:24px; color: #00C6A2;">{total_income:,.0f}</p></div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="metric-box"><h4>💸 Expenses</h4><p style="font-size:24px; color: #E03E3E;">{total_expenses:,.0f}</p></div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class="metric-box"><h4>🎯 Savings</h4><p style="font-size:24px; color: #27AE60;">{net_savings:,.0f}</p></div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""<div class="metric-box"><h4>📈 Rate</h4><p style="font-size:24px; color: #1B4FBB;">{savings_rate:.1f}%</p></div>""", unsafe_allow_html=True)
            
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
            top_category = df[df['Amount'] < 0].groupby('Category')['Amount'].sum().abs().idxmax() if len(df[df['Amount'] < 0]) > 0 else "None"
            
            financial_summary = f"Total Income: {total_income:,.0f}, Total Expenses: {total_expenses:,.0f}, Top Spending: {top_category}"
            
            st.markdown("**Quick Questions:**")
            suggestions = [
                "How can I save more?",
                "Where am I overspending?",
                "Is my savings rate healthy?",
                "How to reduce expenses?"
            ]
            
            cols = st.columns(2)
            for idx, suggestion in enumerate(suggestions):
                with cols[idx % 2]:
                    if st.button(suggestion, use_container_width=True, key=f"faq_{idx}"):
                        st.session_state.chat_history.append({"role": "user", "content": suggestion})
                        with st.spinner("🤖 Getting AI response..."):
                            response = call_azure_ai(suggestion, st.session_state.user_name, financial_summary)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
            
            st.divider()
            
            # Chat display
            if st.session_state.chat_history:
                st.markdown("**Conversation:**")
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f'<div class="chat-bubble">👤 You: {msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-bubble chat-bubble-ai">🤖 Coach: {msg["content"]}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Input
            user_input = st.text_input("💬 Ask your own question...", key="coach_input")
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                with st.spinner("🤖 FinCoach is thinking..."):
                    response = call_azure_ai(user_input, st.session_state.user_name, financial_summary)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                st.rerun()
        
        # TAB 3: Add Expense Manually
        with tab3:
            st.markdown("### ➕ Add Expenses Manually")
            
            add_mode = st.radio("Choose entry method:", ["Single Expense", "Bulk Entry (Multiple)"], horizontal=True, key="add_mode")
            
            if add_mode == "Single Expense":
                col1, col2 = st.columns(2)
                
                with col1:
                    expense_date = st.date_input("📅 Date", key="exp_date")
                    expense_desc = st.text_input("📝 Description", placeholder="e.g., Restaurant dinner", key="exp_desc")
                
                with col2:
                    expense_amount = st.number_input("💰 Amount", min_value=-10000, max_value=100000, value=0, key="exp_amount")
                    expense_category = st.selectbox("🏷️ Category", list(CATEGORY_KEYWORDS.keys()), key="exp_category")
                
                if st.button("✅ Add Transaction", use_container_width=True):
                    if not expense_desc:
                        st.error("❌ Please enter a description")
                    elif expense_amount == 0:
                        st.error("❌ Please enter an amount")
                    else:
                        new_transaction = pd.DataFrame({
                            'Date': [pd.to_datetime(expense_date)],
                            'Description': [expense_desc],
                            'Amount': [expense_amount],
                            'Category': [expense_category]
                        })
                        st.session_state.df = pd.concat([st.session_state.df, new_transaction], ignore_index=True)
                        st.session_state.df = st.session_state.df.sort_values('Date').reset_index(drop=True)
                        st.success("✅ Transaction added successfully!")
                        st.rerun()
            
            else:  # Bulk Entry
                st.markdown("#### 📋 Add Multiple Expenses at Once")
                
                with st.expander("📊 Monthly Expense Summary", expanded=False):
                    template = generate_monthly_expense_summary(6)
                    months = template["months"]
                    month_dates = template["month_dates"]
                    default_categories = template["categories"]
                    
                    st.markdown("**Add expenses by category for each month:**")
                    
                    expense_data = {}
                    
                    for category in default_categories.keys():
                        st.markdown(f"**{category}**")
                        cols = st.columns(3)
                        
                        for idx, month in enumerate(months):
                            with cols[idx % 3]:
                                if category not in expense_data:
                                    expense_data[category] = {}
                                
                                amount = st.number_input(
                                    f"{month}",
                                    value=0,
                                    min_value=-100000,
                                    max_value=0,
                                    step=-10,
                                    key=f"bulk_expense_{category}_{idx}"
                                )
                                expense_data[category][month] = amount
                    
                    if st.button("✅ Add All Expenses", use_container_width=True):
                        transactions = []
                        
                        for category, months_data in expense_data.items():
                            for idx, (month, amount) in enumerate(months_data.items()):
                                if amount != 0:
                                    transactions.append({
                                        'Date': month_dates[idx],
                                        'Description': category.split()[1] if len(category.split()) > 1 else category,
                                        'Amount': amount,
                                        'Category': category
                                    })
                        
                        if transactions:
                            df_bulk = pd.DataFrame(transactions)
                            df_bulk['Date'] = pd.to_datetime(df_bulk['Date'])
                            st.session_state.df = pd.concat([st.session_state.df, df_bulk], ignore_index=True)
                            st.session_state.df = st.session_state.df.sort_values('Date').reset_index(drop=True)
                            st.success(f"✅ Added {len(transactions)} transactions!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Please enter at least one expense")
                
                st.divider()
                st.markdown("#### 📄 Or Paste CSV Data")
                csv_input = st.text_area(
                    "Paste CSV data (Date, Description, Amount, Category):",
                    height=150,
                    placeholder="2024-01-15,Restaurant,100,🍽️ Food\n2024-01-20,Uber,-50,🚗 Transport",
                    key="csv_paste"
                )
                
                if st.button("✅ Import CSV Data", use_container_width=True):
                    try:
                        from io import StringIO
                        csv_data = StringIO(csv_input)
                        df_csv = pd.read_csv(csv_data, names=['Date', 'Description', 'Amount', 'Category'])
                        df_csv['Date'] = pd.to_datetime(df_csv['Date'])
                        df_csv['Amount'] = pd.to_numeric(df_csv['Amount'], errors='coerce')
                        df_csv = df_csv.dropna(subset=['Date', 'Amount'])
                        
                        st.session_state.df = pd.concat([st.session_state.df, df_csv], ignore_index=True)
                        st.session_state.df = st.session_state.df.sort_values('Date').reset_index(drop=True)
                        st.success(f"✅ Imported {len(df_csv)} transactions!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error parsing CSV: {str(e)}")
        
        # TAB 4: Data
        with tab4:
            st.markdown("### 📊 Your Transactions")
            
            st.dataframe(st.session_state.df, use_container_width=True, height=400)
            
            csv = st.session_state.df.to_csv(index=False).encode()
            st.download_button("📥 Download as CSV", csv, "fincoach_transactions.csv", "text/csv", use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Start Over with Manual Entry", use_container_width=True):
                    st.session_state.df = None
                    st.session_state.chat_history = []
                    st.session_state.manual_entry_mode = True
                    st.success("✅ Ready for manual entry")
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Clear All Data", use_container_width=True):
                    st.session_state.df = None
                    st.session_state.chat_history = []
                    st.success("✅ Data cleared")
                    st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #9FA6B2; font-size: 0.85rem;">
💰 FinCoach AI | 🔒 Secure & Private | ⚡ Free for First 100 Users<br>
Design inspired by YNAB, Mint & Personal Capital | Questions? support@fincoach.app
</div>
""", unsafe_allow_html=True)
