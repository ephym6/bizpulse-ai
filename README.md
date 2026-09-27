# BizPulse AI

BizPulse AI is an AI-powered business intelligence prototype that helps SMEs transform sales data into clear metrics, anomaly alerts, and actionable recommendations.

## MVP Flow

CSV Upload → Analytics → Dashboard → Anomaly Detection → AI Recommendations

## Required CSV Columns

- Date
- Product
- Category
- Quantity
- Selling Price
- Cost Price

## Quick Start

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Run tests:

```bash
pytest
```

## Team Ownership

- Member 1: `analytics/` and `data/`
- Member 2: `ai/`
- Member 3: `app.py` and frontend presentation
- Member 4: `tests/`, validation, reliability and responsible AI notes
- Member 5: integration, GitHub, README, demo and submission

## Important Rule

Do not commit real API keys. Use `.env` locally and keep `.env` ignored by Git.
