# 📊 BizPulse AI

> **Turn business data into better decisions.**

BizPulse AI is an AI-powered business intelligence prototype designed to help small and medium-sized businesses transform everyday sales data into understandable metrics, anomaly alerts, business insights, and actionable recommendations.

Instead of leaving SME owners to interpret spreadsheets manually, BizPulse analyzes transaction data, highlights what matters, detects unusual business activity, and uses AI to translate verified findings into practical actions.

The project was developed during the **GOMYCODE Hackathon 2026** with a focus on the **Artefact Data & AI Award**.

---

# 🚀 The Problem

Small businesses generate useful sales and transaction data every day, but many business owners lack the time, tools, or analytical expertise needed to turn that data into useful decisions.

As a result, they may fail to notice:

- Declining sales trends
- Unusual revenue drops or spikes
- Low-performing products
- Low-margin products
- Overdependence on a small number of products
- Weak sales periods
- Opportunities to improve profitability

Traditional spreadsheets can tell a business owner **what happened**, but they often do not clearly explain:

> **What deserves attention, why it matters, and what action should be considered next?**

---

# 💡 Our Solution

BizPulse AI converts raw SME transaction data into:

- Verified business KPIs
- Revenue and product trends
- Business performance insights
- Statistical anomaly alerts
- A Business Health Score
- AI-generated recommendations
- Human-reviewed decision support

The core workflow is:

```text
Sales CSV
    ↓
Validation & Cleaning
    ↓
Business Analytics
    ↓
KPIs & Visualizations
    ↓
Automatic Insights
    ↓
Anomaly Detection
    ↓
AI Business Advisor
    ↓
Human Decision
```

---

# 👤 Target User

BizPulse is designed primarily for **small and medium-sized business owners** who already collect transaction or sales data but do not have access to dedicated analysts or expensive business intelligence platforms.

Example businesses include:

- Mini-markets
- Retail shops
- Cafés
- Restaurants
- Clothing stores
- Electronics stores
- Pharmacies
- Other transaction-based SMEs

---

# ✨ Key Features

## 1. CSV Sales Data Upload

Users can upload their existing business sales data directly into BizPulse.

The application validates and cleans the data before analysis.

Required business fields include:

```text
Date
Product
Category
Quantity
Selling Price
Cost Price
```

The analytics engine also recognizes several common alternative column names.

For example:

```text
Selling Price
selling_price
SellingPrice
unit_price
price
```

Optional fields can include:

```text
Branch
Payment Method
Discount
```

---

## 2. Automatic Business KPIs

BizPulse automatically calculates:

- Total Revenue
- Total Profit
- Profit Margin
- Units Sold
- Best-Selling Product
- Highest-Revenue Category
- Revenue Growth

Important financial calculations are performed directly using the uploaded data rather than being delegated to a generative AI model.

For example:

```text
Revenue = Quantity × Selling Price

Cost = Quantity × Cost Price

Profit = Revenue − Cost
```

This keeps important business calculations deterministic and explainable.

---

# 📈 3. Interactive Business Dashboard

The Streamlit dashboard provides a visual overview of business performance.

Current visualizations include:

- Revenue over time
- Revenue by category
- Top-performing products
- Product-level revenue and profitability
- Weekly revenue changes
- Business performance indicators

The interface is designed to give SME owners a quick overview without requiring them to understand data-analysis tools.

---

# ❤️ 4. Business Health Score

BizPulse provides a prototype **Business Health Score from 0–100**.

The score considers indicators such as:

- Revenue trend
- Profitability
- Sales consistency
- Product concentration

Example:

```text
Business Health

78 / 100
GOOD

🟢 Revenue Trend
🟢 Profitability
🟡 Sales Consistency
🔴 Product Concentration
```

The score also highlights the most significant concern where appropriate.

> **Important:** The Business Health Score is a prototype decision-support indicator. It is not a certified financial, investment, credit, or accounting score.

---

# 🔍 5. Automatic Business Insights

BizPulse automatically interprets calculated business metrics and surfaces important findings.

Examples include:

```text
📈 Sales Growth
Revenue increased compared with the previous period.

🔥 High Performer
A specific product contributes significantly to total revenue.

💰 Margin Opportunity
A high-volume product has a lower margin than comparable products.

🏷️ Category Leader
A category contributes a large share of total revenue.
```

These findings are based on calculated data rather than generated assumptions.

---

# 🚨 6. Anomaly Detection

BizPulse includes statistical anomaly detection to identify unusual daily revenue activity.

The current implementation uses **Z-score analysis**.

The system calculates the expected revenue distribution and flags unusually high or low values.

Example:

```text
🚨 Anomaly Detected

September 7
Revenue: KSh 650
Z-score: -2.4
```

Possible causes could include:

- Stockouts
- Store closures
- Promotions
- Operational disruptions
- Data-quality problems

BizPulse identifies the unusual event but leaves the final interpretation to the business owner.

---

# 🤖 7. AI Business Advisor

BizPulse integrates **Google Gemini** to translate verified business findings into understandable recommendations.

The AI is deliberately separated from the financial calculation layer.

The architecture is:

```text
Raw Data
   ↓
Pandas Analytics
   ↓
Verified Metrics
   ↓
Statistical Anomaly Detection
   ↓
Structured Business Context
   ↓
Google Gemini
   ↓
3 Actionable Recommendations
```

The default configured model is:

```text
gemini-2.5-flash
```

The model receives summarized business indicators rather than being asked to calculate revenue or profit itself.

---

# 🧠 Example AI Flow

### Input

BizPulse calculates that:

```text
Profit Margin: 12%
Top Product: Milk 500ml
Tuesday has below-average sales
An unusual revenue drop was detected
```

### AI Action

Gemini interprets the verified findings and identifies possible business actions.

### Example Output

```text
1. Review supplier costs or pricing because the overall profit margin is relatively low.

2. Maintain sufficient inventory for Milk 500ml because it is a major sales contributor.

3. Investigate the unusual low-revenue period for possible stockouts, closures, or operational issues.
```

The AI is instructed not to invent additional financial figures.

---

# 🛡️ AI Fallback & Reliability

The BizPulse dashboard does not depend entirely on an external AI service.

If Gemini is unavailable because of:

- Missing API credentials
- No internet connection
- Rate limits
- API errors
- Invalid model output
- Temporary provider outage

BizPulse automatically falls back to **deterministic analytics-based recommendations**.

Therefore:

```text
Gemini available
      ↓
AI-generated recommendations

Gemini unavailable
      ↓
Analytics-driven fallback recommendations
```

Core analytics, visualizations, anomaly detection, and dashboard functionality continue to work.

This was an intentional reliability decision.

---

# 🔐 Responsible AI & Data Privacy

BizPulse was designed with several Responsible AI principles.

## Data Minimization

The AI advisor receives summarized business indicators where possible rather than unnecessary customer-level information.

BizPulse does not require fields such as:

- Customer names
- Phone numbers
- Email addresses
- Identity documents

---

## Human Oversight

AI output is presented as decision support.

The system does **not automatically perform business actions** such as:

- Changing prices
- Ordering stock
- Removing products
- Making payments
- Firing employees
- Making financial commitments

The business owner remains responsible for the final decision.

---

## Explainable Analytics

Revenue, profit, margins, growth, and other business metrics are calculated using deterministic code.

The LLM is used primarily for:

> **Interpretation and recommendation generation**

rather than numerical calculation.

---

## AI Limitations

AI recommendations:

- May not capture every real-world factor
- Depend on the quality of the input data
- Should be reviewed before action
- Are not guaranteed business outcomes
- Are not professional financial advice

---

# 📊 Demo Dataset

The repository contains a synthetic sample dataset:

```text
data/sample_sales.csv
```

It is used to provide a reproducible demonstration of the product.

The sample contains realistic sales patterns and a deliberately unusual sales period so that anomaly detection can be demonstrated.

The synthetic dataset contains **no real customer personal information**.

During development, the team also tested BizPulse with synthetic:

- Mini-market transaction data
- Café transaction data

This helped validate that the analytics pipeline could work across more than one SME scenario.

---

# 🧪 Testing & Reliability

Automated tests are included using **Pytest**.

Current tests cover areas such as:

- Data loading and cleaning
- Revenue calculations
- Profit calculations
- Profit margin calculations
- Quantity calculations
- Best-selling product identification
- Highest-revenue category identification
- Empty dataset validation
- Missing-column detection
- Valid dataset handling

Run the tests using:

```bash
pytest
```

The project also considers failure scenarios such as:

```text
Empty CSV
Missing required columns
Invalid data
No anomalies
AI API unavailable
Missing AI credentials
```

---

# 🏗️ Project Architecture

```text
                   ┌──────────────────────────┐
                   │      Sales CSV Upload    │
                   └─────────────┬────────────┘
                                 │
                                 ▼
                   ┌──────────────────────────┐
                   │   Validation & Cleaning  │
                   │       Pandas / Utils     │
                   └─────────────┬────────────┘
                                 │
                                 ▼
                   ┌──────────────────────────┐
                   │    Analytics Engine      │
                   │ Revenue / Profit / KPIs  │
                   └─────────────┬────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                  ▼                             ▼
       ┌─────────────────────┐       ┌─────────────────────┐
       │ Business Dashboard  │       │ Anomaly Detection   │
       │ Charts / Health     │       │ Z-score Analysis    │
       └──────────┬──────────┘       └──────────┬──────────┘
                  │                             │
                  └──────────────┬──────────────┘
                                 │
                                 ▼
                   ┌──────────────────────────┐
                   │    AI Business Advisor   │
                   │   Google Gemini /        │
                   │   Deterministic Fallback │
                   └─────────────┬────────────┘
                                 │
                                 ▼
                   ┌──────────────────────────┐
                   │ Human-Reviewed Decision  │
                   └──────────────────────────┘
```

---

# 📁 Repository Structure

```text
bizpulse-ai/
│
├── app.py
│
├── analytics/
│   ├── __init__.py
│   └── analytics.py
│
├── ai/
│   ├── __init__.py
│   ├── anomaly.py
│   └── recommendations.py
│
├── data/
│   └── sample_sales.csv
│
├── utils/
│   ├── __init__.py
│   └── validation.py
│
├── tests/
│   ├── test_analytics.py
│   └── test_validation.py
│
├── docs/
│   └── DEMO_NOTES.md
│
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── requirements.txt
└── README.md
```

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application and business logic |
| **Streamlit** | Web dashboard and user interface |
| **Pandas** | Data cleaning, grouping and analytics |
| **NumPy** | Numerical/statistical operations |
| **Google Gemini API** | AI-generated business recommendations |
| **Google GenAI SDK** | Gemini integration |
| **Z-score analysis** | Statistical anomaly detection |
| **python-dotenv** | Secure environment-variable management |
| **Pytest** | Automated testing |
| **Git** | Version control |
| **GitHub** | Team collaboration and source repository |

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

Enter the project folder:

```bash
cd bizpulse-ai
```

---

# 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

---

# 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The project requires packages including:

```text
streamlit
pandas
numpy
scikit-learn
plotly
python-dotenv
pytest
google-genai
```

---

# 🔑 AI Configuration

BizPulse can operate without an AI API key using its deterministic fallback recommendations.

To enable the Gemini AI advisor, create a local `.env` file.

You can copy the supplied example:

```bash
cp .env.example .env
```

On Windows, you may simply create `.env` manually.

Add:

```env
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-2.5-flash
```

Do **not** commit your `.env` file.

The repository's `.gitignore` is configured to keep secrets and environment files out of version control.

---

# ▶️ Running BizPulse

Start the Streamlit application:

```bash
streamlit run app.py
```

Streamlit will provide a local URL, usually:

```text
http://localhost:8501
```

Open it in your browser.

---

# 🧭 User Journey

Once BizPulse is running:

### Step 1 — Upload Data

Upload a CSV containing:

```text
Date
Product
Category
Quantity
Selling Price
Cost Price
```

Alternatively, select the built-in sample dataset.

---

### Step 2 — Review KPIs

BizPulse displays:

- Revenue
- Profit
- Profit Margin
- Units Sold
- Revenue Growth
- Top Product
- Top Category

---

### Step 3 — Review Business Health

The application summarizes performance into a prototype health score.

---

### Step 4 — Explore Trends

Review:

- Revenue over time
- Category performance
- Product performance

---

### Step 5 — Review Insights

BizPulse highlights important trends and opportunities automatically.

---

### Step 6 — Investigate Anomalies

Review unusual revenue activity detected statistically.

---

### Step 7 — Review AI Recommendations

The AI Business Advisor converts verified insights into three possible business actions.

The business owner then decides whether those actions are appropriate.

---

# 🎬 90-Second Demo Flow

Our recommended demonstration flow is:

### 0–15 seconds — Problem

> Small business owners generate transaction data every day, but spreadsheets often tell them what happened without explaining what deserves attention or what to do next.

### 15–30 seconds — Upload

Upload the sales dataset into BizPulse.

### 30–45 seconds — Dashboard

Show:

- Revenue
- Profit
- Margin
- Business Health
- Top product/category

### 45–60 seconds — Intelligence

Show:

- Automatic insights
- Revenue trends
- Detected anomaly

### 60–75 seconds — AI Advisor

Show the AI-generated business recommendations.

### 75–90 seconds — Impact

> BizPulse turns raw SME transaction data into verified insights, early warnings, and practical decisions — while keeping the business owner in control.

---

# 🏆 Hackathon Award Fit

BizPulse was developed primarily for the:

## Artefact Data & AI Award

The project fits the award because it demonstrates:

```text
Raw Business Data
       ↓
Reliable Analytics
       ↓
AI Interpretation
       ↓
Actionable Insight
       ↓
Measurable Business Value
```

Rather than adding AI as a standalone chatbot, BizPulse uses AI as one component of a larger data-driven decision-support pipeline.

---

# 🧩 What We Built During the Hackathon

The team built and integrated:

- Sales data ingestion and cleaning
- Flexible column detection
- Revenue and profit calculations
- KPI engine
- Product/category analytics
- Revenue trends
- Business Health Score
- Automatic business insight rules
- Statistical anomaly detection
- Gemini recommendation integration
- Deterministic fallback recommendations
- Streamlit dashboard
- Data validation
- Automated tests
- Synthetic demonstration datasets
- Responsible AI safeguards
- Documentation and demonstration materials

We reused established open-source libraries and APIs rather than rebuilding foundational tools such as Pandas, Streamlit, NumPy, or Gemini.

---

# 👥 Team Workflow

The project was developed by a **5-person team**.

Responsibilities were divided across:

1. **Data & Analytics**
   - Dataset preparation
   - Cleaning
   - KPI and business analytics

2. **AI & Machine Learning**
   - Anomaly detection
   - Gemini integration
   - Recommendation fallback

3. **Frontend**
   - Streamlit interface
   - Dashboard
   - Visualization and UX

4. **Testing & Responsible AI**
   - Validation
   - Test cases
   - Reliability
   - Responsible AI review

5. **Product, Integration & Demo**
   - GitHub coordination
   - Integration
   - Documentation
   - Demo
   - Submission

Development was handled using separate feature branches before integration into `main`.

---

# ⚠️ Current MVP Limitations

BizPulse is currently a hackathon prototype.

Current limitations include:

- CSV upload rather than direct POS integration
- No persistent user accounts
- No production database
- No automated inventory ordering
- No validated financial/credit scoring model
- Z-score anomaly detection is currently based on relatively simple statistical thresholds
- Recommendations depend on the quality and quantity of business data
- AI recommendations require human review
- Revenue forecasting is not yet part of the core MVP

---

# 🔮 Future Development

The next version of BizPulse would focus on:

### POS & Accounting Integration

Automatically connect to business systems rather than requiring manual CSV upload.

### Persistent Business Profiles

Allow owners to securely track performance over time.

### Forecasting

Introduce:

- Revenue forecasting
- Demand forecasting
- Inventory forecasting

### Improved Anomaly Detection

Move from generic thresholds to business-specific historical baselines and potentially more advanced anomaly models.

### Recommendation Impact Tracking

Allow businesses to record whether they followed a recommendation and measure the resulting impact.

Example:

```text
Recommendation:
Run Tuesday promotion

Action taken:
Yes

Before:
KSh 12,000 average Tuesday revenue

After:
KSh 15,200

Measured improvement:
+26.7%
```

### Real SME Validation

Test BizPulse with consented, anonymized data from real SMEs and evaluate:

- Recommendation usefulness
- False anomaly rate
- Decision quality
- Time saved
- Business-owner trust

---

# 📌 Project Philosophy

BizPulse follows one central principle:

> **AI should not replace reliable business analytics — it should help people understand and act on them.**

Our system therefore separates:

```text
Analytics
→ What happened?

Anomaly Detection
→ What looks unusual?

Generative AI
→ What could the owner consider doing?

Human Oversight
→ What action should actually be taken?
```

---

# 🔒 Security Reminder

Never commit:

```text
.env
API keys
Passwords
Credentials
Customer personal data
```

Use:

```text
.env.example
```

to document required environment variables without exposing secrets.

---

# 📄 License / Usage

This project was developed as a hackathon prototype for demonstration and educational purposes.

The included sample business data is synthetic and should not be interpreted as representing a real business.

---

# 📊 BizPulse AI

**From spreadsheets to decisions.**

```text
Business Data
     ↓
Reliable Analytics
     ↓
Meaningful AI
     ↓
Actionable Recommendation
     ↓
Human Decision
```
