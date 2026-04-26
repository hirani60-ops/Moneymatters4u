# 💰 FinCoach AI — Your Smart Personal Finance Coach

A production-ready, AI-powered personal finance coaching web application built with **Python**, **Streamlit**, and **Azure AI Foundry**.

![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18-239DAD?logo=plotly&logoColor=white)
![Azure AI](https://img.shields.io/badge/Azure%20AI-Foundry-0078D4?logo=microsoft-azure&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Features

FinCoach AI provides 8 powerful modules to transform your financial life:

### 📊 Dashboard
- Real-time financial KPIs (Income, Expenses, Savings, Savings Rate)
- Spending breakdown by category (interactive donut chart)
- 6-month income vs expenses trend
- AI-generated financial insights
- Financial health score
- Top recommendations

### 💸 Spending Analysis
- Interactive filters (category, date range, amount)
- Top spending categories visualization
- Spending trends over time
- **Subscription Detector** — Auto-detect recurring charges
- Transaction anomaly detection & flagging
- Detailed transaction table with export
- AI-powered anomaly explanations

### 🤖 AI Coach
- Chat interface with Azure AI
- Contextual financial advice based on your data
- Suggested questions (6 pre-built prompts)
- Chat history (session-persistent)
- Personalized recommendations

### 🎯 Goals Tracker
- Create and track financial goals
- Categories: Emergency Fund, Vacation, Home, Car, Education, Investment, Other
- Progress visualization with gauges
- Days remaining & monthly savings needed
- Priority levels (High/Medium/Low)
- Status indicators (On Track, At Risk, Behind, Complete)

### 📈 Investments
- Risk profile assessment (5-question questionnaire)
- Suggested asset allocation (Conservative/Moderate/Aggressive)
- Compound interest calculator
- Monthly/yearly growth visualization
- Investment education cards
- Starting plan based on profile

### 💼 Budget Planner
- 50/30/20 rule calculator
- Budget vs actual tracking
- Category-specific gauges
- Savings recommendations
- AI budget optimization

### ⚠️ Risk Report
- Financial health score (0-100 gauge)
- 5 risk assessment cards:
  - Overspending Risk
  - Emergency Fund Risk
  - Subscription Bloat Risk
  - Debt & Loan Risk
  - Anomaly Risk
- **MANDATORY Disclosures** — 6 compliance statements
- Risk-specific action items

### 🧾 Tax Summary
- Annual income overview
- Monthly income breakdown
- Deductible expenses identification
- Tax calendar (key dates)
- Annual report export

---

## 🛡️ Security & Privacy

✅ **Zero Data Storage** — All data processed in-memory, never saved  
✅ **Session-Only Processing** — Everything cleared on logout  
✅ **No Tracking** — Complete anonymity guaranteed  
✅ **HTTPS Only** — Encrypted connections  
✅ **API Key Security** — Secrets never committed to GitHub  
✅ **Input Validation** — Max 10MB file size, CSV format only  

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit 1.32 |
| **Backend** | Python 3.9+ |
| **Charts** | Plotly 5.18 (no matplotlib) |
| **Data** | Pandas 2.1.4, NumPy 1.26.4 |
| **AI** | Azure AI Foundry (Phi-4) |
| **HTTP** | Requests 2.31 |

---

## 📋 Requirements

### System Requirements
- Python 3.9 or higher
- 4GB RAM minimum
- 500MB disk space

### Dependencies (see `requirements.txt`)
```
streamlit==1.32.0
pandas==2.1.4
plotly==5.18.0
requests==2.31.0
numpy==1.26.4
python-dateutil==2.8.2
```

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/fincoach-ai.git
cd fincoach-ai
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Azure AI Foundry
Copy the template and fill in your credentials:
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:
```toml
AZURE_API_ENDPOINT = "https://your-endpoint.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview"
AZURE_API_KEY = "your-api-key-here"
MODEL_NAME = "Phi-4"
```

**⚠️ Never commit `secrets.toml` to GitHub!**

### 5. Run Locally
```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

---

## 🔑 Azure AI Foundry Setup

### Get Your Credentials

1. **Log in to [Azure AI Foundry](https://ai.azure.com)**
2. Create or select a project
3. Go to **Deployments** (or **Models**)
4. Create a new deployment for **Phi-4** (or your chosen model)
5. Copy:
   - **API Endpoint** → `AZURE_API_ENDPOINT`
   - **API Key** → `AZURE_API_KEY`

### Endpoint Format
```
https://{resource-name}.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview
```

### Free Credits
- **$200** free Azure AI credits for new accounts
- Enough for ~1,000 AI chat interactions
- No credit card required for trial

---

## 📂 Project Structure

```
fincoach-ai/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── .streamlit/
│   ├── config.toml                 # Streamlit configuration
│   └── secrets.toml.template       # Secrets template (safe to commit)
└── .streamlit/secrets.toml         # Secrets (DO NOT COMMIT)
```

---

## 🎮 Demo Mode

No Azure AI credentials? No problem!

FinCoach AI includes **Demo Mode** with 6 months of realistic synthetic data:
- Monthly salary: 8,500
- Various expenses across 14+ categories
- Realistic patterns and anomalies

**Start Demo:**
1. Click **🎮 Load Demo Data** in sidebar
2. Explore all 8 tabs with sample data
3. AI features show helpful messages without API calls

---

## 📤 Deployment on Streamlit Community Cloud

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "🚀 Initial release: FinCoach AI v1.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fincoach-ai.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository `fincoach-ai`
5. Set **Main file path**: `app.py`
6. Click **Deploy**

### Step 3: Configure Secrets
Once deployed:
1. Click app menu (⋮) → **Settings**
2. Go to **Secrets**
3. Paste your credentials:
```toml
AZURE_API_KEY = "your-key"
AZURE_API_ENDPOINT = "your-endpoint"
MODEL_NAME = "Phi-4"
```
4. Save → Wait 60 seconds → ✅ Live!

---

## 🧪 Testing Checklist

- [ ] App runs without errors: `streamlit run app.py`
- [ ] Demo data loads instantly
- [ ] All 8 tabs render correctly
- [ ] No deprecated pandas functions used
- [ ] All Azure API calls have error handling
- [ ] No API keys in source code
- [ ] Charts use Plotly (no matplotlib)
- [ ] "Clear Data" button fully resets session
- [ ] Risk disclosures visible in Risk Report
- [ ] CSV upload validation works
- [ ] Currency selector affects all amounts
- [ ] Mobile responsive layout
- [ ] Works in dark & light themes

---

## 🎨 Design System

### Color Palette
```
PRIMARY:     #1B4FBB  (Deep Trust Blue)
ACCENT:      #00C6A2  (Fresh Teal)
WARNING:     #F5A623  (Amber)
DANGER:      #E03E3E  (Red)
SUCCESS:     #27AE60  (Green)
BG_DARK:     #0F1117  (Main Background)
BG_CARD:     #1A1D27  (Card Surface)
TEXT_PRIMARY:#FFFFFF
TEXT_MUTED:  #9FA6B2
```

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300 (light), 400 (normal), 500 (medium), 600 (semi-bold), 700 (bold)

---

## 📊 Data Format

### Supported CSV Columns
FinCoach detects these column names (case-insensitive):

**Required:**
- Date column: `date`, `transaction date`
- Description: `description`, `narration`
- Amount: `amount`, `debit`, `credit`

**Example CSV:**
```csv
date,description,amount
2024-01-15,Monthly Salary Credit,8500
2024-01-16,Careem ride,-45
2024-01-18,Spinneys Groceries,-320
2024-01-20,Netflix subscription,-49
```

**Constraints:**
- Max 10,000 transactions
- CSV format only
- Max 10MB file size
- All dates must be valid
- All amounts must be numeric

---

## 🤖 AI Features

### Azure AI Phi-4 Model
- Fast response time (~5 seconds)
- Optimized for financial advice
- 800 token max output
- Temperature: 0.7 (balanced creative & deterministic)

### Fallback Behavior
If Azure is unavailable:
- Demo Mode works without AI
- AI Chat shows friendly error messages
- All other features remain fully functional

---

## 🔐 Compliance & Disclosures

### Legal Disclaimers (in-app)
1. ✅ **NOT Financial Advice** — Educational only
2. ✅ **AI Limitations** — May contain errors
3. ✅ **Data Accuracy** — User responsibility
4. ✅ **NO Data Storage** — Session-only
5. ✅ **Investment Risk** — Losses possible
6. ✅ **Session Privacy** — Fully isolated

### Regulatory Notes
- Not licensed as financial advisor
- No securities advice provided
- No tax advice (refer to tax professional)
- Educational purposes only

---

## 🐛 Troubleshooting

### Issue: "Could not detect required columns"
**Solution:** Ensure CSV has `Date`, `Description`, and `Amount` columns

### Issue: "API key issue" in AI Coach
**Solution:** Check `.streamlit/secrets.toml` has correct Azure credentials

### Issue: App crashes on file upload
**Solution:** Ensure CSV is <10MB and has valid data

### Issue: Charts not displaying
**Solution:** Check Plotly is installed: `pip install plotly==5.18.0`

### Issue: Demo data not loading
**Solution:** This is built-in and should always work. Try `streamlit cache clear`

---

## 📈 Performance

| Operation | Time |
|-----------|------|
| Load demo data | <1 second |
| Process 6 months data | <2 seconds |
| AI response (Azure) | ~5 seconds |
| Chart rendering | <1 second |
| Export CSV | <1 second |

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Streamlit** — Amazing framework for data apps
- **Azure AI Foundry** — Powerful AI models
- **Plotly** — Beautiful interactive charts
- **Pandas** — Data manipulation excellence

---

## 📞 Support

Need help?
- 📖 Check [Streamlit Docs](https://docs.streamlit.io)
- 🔑 See [Azure AI Setup Guide](https://learn.microsoft.com/en-us/azure/ai-services/)
- 🐛 Report issues on GitHub Issues
- 💬 Discussion forum in GitHub

---

## 🎯 Roadmap

Future enhancements:
- [ ] Dark/Light theme toggle
- [ ] Multi-language support
- [ ] Custom report generation
- [ ] Bank API integration
- [ ] Mobile app version
- [ ] Advanced ML predictions
- [ ] Collaborative goals
- [ ] Integration with Twilio SMS alerts

---

## ⭐ Star This Project!

If FinCoach AI helps you, please star ⭐ the GitHub repository!

---

**Made with ❤️ by FinCoach AI Team**

*Empowering smarter financial decisions, one transaction at a time.*
