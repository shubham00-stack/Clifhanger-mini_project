# Cliffhanger Strength Analyzer

> **Enterprise-Grade, Explainable AI Platform for Evaluating Narrative Tension, Unresolved Questions, Stakes, and Cliffhanger Strength.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM%20Nemotron-76B900.svg)](https://developer.nvidia.com/nim)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Key Capabilities

1. **Deterministic Score Calculation**: The AI model rates calibrated dimensions and extracts quotes; the backend deterministically calculates the weighted score and score bands ($Final\ Score = \sum_{i=1}^9 w_i \times D_i$).
2. **Strict Evidence-Based Provenance**: Every score claim is verified against verbatim quotes from the story text.
3. **NVIDIA NIM Integration & Provider Agility**: Built on an OpenAI-compatible abstraction supporting NVIDIA Nemotron models (`nvidia/nemotron-3-nano-omni-30b-a3b-instruct`, `nvidia/nemotron-3.5-bolt-e4b`) with automated retries, JSON repair, and offline mock fallbacks.
4. **Model Context Protocol (MCP)**: 4 secure, least-privilege MCP servers (`project_context`, `evidence`, `scoring`, `rewrite`).
5. **Phase 6 Evaluation Framework**: Seed benchmark datasets for Weak, Moderate, and Strong endings, measuring Mean Absolute Error (MAE), Spearman Rank Correlation, Citation Accuracy, and asserting the regression gate:
   $$\text{Score}_{\text{Strong}} > \text{Score}_{\text{Moderate}} > \text{Score}_{\text{Weak}}$$
6. **Phase 7 Production Hardening**:
   - Resilience: Exponential backoff retries, JSON auto-repair, rate-limit (429) backoff, and model fallback chains.
   - Security: Payload size limits, safe filename sanitization, CORS restrictions, project-level tenancy boundaries.
   - Observability: Request-ID tracking (`X-Request-ID`), Prometheus `/metrics` endpoint, and structured JSON logs.

---

## Architecture Overview

```
apps/
  api/               # FastAPI backend with Request-ID & Prometheus metrics
  web/               # Next.js 14+ React TypeScript frontend & Rewrite Lab
services/
  scoring/           # Deterministic 9-dimension arithmetic & taxonomy classifier
  narrative/         # Scene segmenter, rewrite generator & consistency auditor
  ingestion/         # Document parser & provenance extractor
  retrieval/         # Vector embeddings & reranking
  reporting/         # Markdown & JSON executive report generators
mcp/
  project_context/   # MCP server for story context & questions
  evidence/          # MCP server for quotes, scenes & citations
  scoring/           # MCP server for score calculation & validation
  rewrite/           # MCP server for rewrite generation & consistency
packages/
  schemas/           # Shared Pydantic data schemas & contracts
  prompts/           # Versioned prompts (v1.0.0)
  model_client/      # NVIDIA NIM / OpenAI client & MockModelClient
  shared/            # Logging, security, error handling, config
evaluation/
  datasets/          # Ground truth Weak, Moderate, Strong seed suites
  benchmarks/        # MAE, Spearman, precision/recall, citation accuracy
infrastructure/
  docker/            # Dockerfiles for API, Web, MCP
  docker-compose.yml # Orchestration file
docs/                # Architecture, scoring, API, and MCP documentation
```

---

## Quickstart

### 1. Environment Setup
```bash
cp .env.example .env
```

### 2. Run API
```bash
pip install -r requirements.txt
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Run Web Dashboard
```bash
cd apps/web
npm install
npm run dev
```

### 4. Run Phase 6 Benchmark Suite
```bash
python -m evaluation.benchmarks.cli
```

### 5. Run Automated Tests
```bash
pytest tests/ -v
```
