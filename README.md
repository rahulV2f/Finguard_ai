# FinGuard AI: Banking Fraud Detection & Transaction Risk Intelligence Platform

FinGuard AI is an enterprise-grade AI-powered banking fraud detection and transaction risk intelligence platform designed for simulated financial surveillance environments. Built with modern full-stack technologies and explainable machine learning, FinGuard surveils high-throughput financial transactions, computes hybrid risk scores (0–100), visualizes anomaly drivers, and provides fraud analysts with investigation case management tools.

> **Disclaimer:** FinGuard AI is an educational simulation platform operating strictly on synthetic and anonymized financial transaction records. It does not connect to real bank accounts, initiate real payment orders, or claim to prevent real-world financial fraud. No official affiliation with ICICI Bank or any financial institution is claimed.

---

## Architecture Overview

```
                      ┌──────────────────────────────────────┐
                      │    FinGuard AI React 19 Frontend     │
                      │ (Vite, Tailwind CSS, Lucide, Recharts)│
                      └──────────────────┬───────────────────┘
                                         │ JSON / JWT Bearer
                                         ▼
                      ┌──────────────────────────────────────┐
                      │        FastAPI REST Gateway          │
                      │ (Pydantic v2, CORS, Rate Protection) │
                      └──────────────────┬───────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
    ┌──────────────────────────┐                   ┌──────────────────────────┐
    │     Hybrid ML Engine     │                   │   PostgreSQL / SQLite    │
    │  • Balanced Random Forest│                   │  • Transactions Ledger   │
    │  • Deterministic Rules   │                   │  • Fraud Alerts Queue    │
    │  • SHAP / Driver Factors │                   │  • Investigation Cases   │
    │  • Precision-Recall AUC  │                   │  • Append-Only Audit Log │
    └──────────────────────────┘                   └──────────────────────────┘
```

---

## Core Capabilities & Feature Modules

1. **Transaction Surveillance Engine:**
   - Ingestion of live payment, transfer, ATM, POS, and UPI settlements.
   - Deep validation for CSV batch uploads with malformed data rejection.
   - Deterministic synthetic transaction generator with configurable fraud injection ratios.

2. **Hybrid Detection Engine (Rules + Machine Learning):**
   - **Deterministic Rule Baseline:** Instant zero-overhead Boolean guards for velocity spikes (5+ txns in 60 min), amount anomalies (>10x customer baseline), geographic impossible travel (>800 km in short interval), and midnight high-value executions.
   - **Balanced Random Forest ML:** 120-tree classifier with balanced class weighting, robust to extreme banking class imbalance.
   - **Calibrated Risk Scoring (0–100):** 65% ML confidence + 35% deterministic rule score mapped to 4 configurable risk bands: Low (0–29), Medium (30–59), High (60–79), and Critical (80–100).

3. **Explainable AI (XAI) Attribution:**
   - Factor attribution cards for every flagged transaction explaining *why* an anomaly was identified without exposing proprietary model internals.

4. **Alerts & Investigation Case Management:**
   - Automated alert dispatch for transactions exceeding safety thresholds.
   - Case workflow tracking: `OPEN` ➔ `INVESTIGATING` ➔ `ESCALATED` ➔ `CLOSED_FRAUD` / `CLOSED_LEGITIMATE`.
   - Immutable audit trail documenting analyst triage notes and resolution rationale.

5. **Model Governance & Performance Benchmarking:**
   - Real offline test metrics: Precision, Recall, F1-Score, PR-AUC, and ROC-AUC.
   - 2x2 Confusion Matrix visualizer (TP, FP, TN, FN).
   - Side-by-side comparison between Rule-Based baselines and Random Forest ML.

---

## Tech Stack

- **Frontend:** React 19, Vite 8, Tailwind CSS, Recharts, Lucide React, Axios, React Router v7.
- **Backend:** Python 3.13, FastAPI, SQLAlchemy ORM, Pydantic v2, PyJWT, Bcrypt, Pytest.
- **Machine Learning:** scikit-learn, NumPy, Pandas, Joblib.
- **Database:** SQLite (local zero-dependency dev) / PostgreSQL (production docker).
- **Deployment:** Docker, Docker Compose.

---

## Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup & Seeding
```bash
# Clone repository
git clone https://github.com/rahullcout/Fraud_AI.git
cd Fraud_AI

# Install Python backend dependencies
pip install -r backend/requirements.txt

# Seed database with demo accounts, train ML model, and ingest synthetic transactions
python scripts/seed_data.py

# Start FastAPI backend server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
*API Swagger Documentation will be available at:* `http://localhost:8000/api/v1/docs`

### 3. Frontend Setup
```bash
# In a separate terminal:
cd frontend
npm install --legacy-peer-deps
npm run dev
```
*Frontend Application will be available at:* `http://localhost:5173`

---

## Demo Credentials (Pre-seeded)

| Role | Institutional Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Chief Risk Admin** | `admin@finguard.ai` | `Admin@123456` | Full system governance, audit logs, pipeline retraining |
| **Fraud Analyst** | `analyst@finguard.ai` | `Analyst@123456` | Transaction surveillance, alert triage, case notes |

*Quick Access Tip:* The login page includes 1-click demo access buttons to populate credentials automatically.

---

## Running Automated Tests

Run the complete backend test suite:
```bash
pytest tests/ -v
```

---

## Docker Deployment (PostgreSQL + FastAPI + React)

```bash
docker-compose up --build -d
```
- Frontend: `http://localhost:5173`
- Backend API & Swagger: `http://localhost:8000/api/v1/docs`
- PostgreSQL: `localhost:5432`

---

## License
MIT License. Developed for technical demonstration and portfolio evaluation.
