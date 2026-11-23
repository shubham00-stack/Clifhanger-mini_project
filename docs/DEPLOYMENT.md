# Local & Cloud Deployment Guide

## Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Docker & Docker Compose (optional for containerized deployment)

## 1. Quickstart Local Development

### Backend API
```bash
# Install dependencies
pip install -r requirements.txt

# Start API gateway
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```
OpenAPI documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Frontend Web UI
```bash
cd apps/web
npm install
npm run dev
```
Dashboard will be available at [http://localhost:3000](http://localhost:3000).

---

## 2. Docker Compose Deployment
```bash
docker-compose up --build -d
```
This launches:
- `cliffhanger-api` on port `8000`
- `cliffhanger-web` on port `3000`
- `cliffhanger-mcp` service

---

## 3. Running Phase 6 Evaluation Benchmarks
```bash
python -m evaluation.benchmarks.cli
```
Verifies MAE, Spearman Rank Correlation, Citation Accuracy, and the regression assertion:
$$\text{Score}_{\text{Strong}} > \text{Score}_{\text{Moderate}} > \text{Score}_{\text{Weak}}$$
