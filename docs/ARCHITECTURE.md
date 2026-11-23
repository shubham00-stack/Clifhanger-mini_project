# System Architecture — Cliffhanger Strength Analyzer

## 1. Overview
The **Cliffhanger Strength Analyzer** is an enterprise-grade explainable AI platform designed to evaluate narrative tension, unresolved questions, stakes, and narrative impact of cliffhangers across screenplays, novels, and teleplays.

```
+-----------------------------------------------------------------------------------+
|                                 Client Layer                                      |
|          Next.js Web UI (Dashboard, Upload, Ending Selector, Rewrite Lab)          |
+------------------------------------------+----------------------------------------+
                                           | HTTP / REST
+------------------------------------------v----------------------------------------+
|                               API & Gateway Layer                                 |
|         FastAPI Gateway (OpenAPI, CORS, Request-ID Tracking, Prometheus /metrics) |
+------------------------------------------+----------------------------------------+
                                           |
+------------------------------------------v----------------------------------------+
|                      MCP Layer (Controlled Tool Interfaces)                       |
|   +-------------------+  +---------------+  +---------------+  +---------------+  |
|   |  project_context  |  |   evidence    |  |    scoring    |  |    rewrite    |  |
|   +-------------------+  +---------------+  +---------------+  +---------------+  |
+------------------------------------------+----------------------------------------+
                                           |
+------------------------------------------v----------------------------------------+
|                               Core Services Layer                                 |
|   - Ingestion Service (Parser & provenance tracker)                               |
|   - Narrative Service (Scene segmentation, graph, rewrite generator)              |
|   - Scoring Engine (Deterministic 9-dimension math & band mapper)                 |
|   - Retrieval Service (Vector embeddings & candidate reranker)                    |
|   - Reporting Service (Markdown & JSON executive reports)                         |
+------------------------------------------+----------------------------------------+
                                           |
+------------------------------------------v----------------------------------------+
|                              AI Provider Abstraction                              |
|                BaseModelClient / NimModelClient / MockModelClient                 |
|            (NVIDIA NIM: Nemotron 3 Nano Omni 30B / Bolt E4B / Retries)            |
+-----------------------------------------------------------------------------------+
```

## 2. Key Monorepo Packages
- `apps/api`: Production FastAPI application with endpoints, middleware, and metrics.
- `apps/web`: Next.js 14+ React TypeScript frontend.
- `services/scoring`: Deterministic mathematical score calculation engine and taxonomy validator.
- `services/narrative`: Scene boundary segmenter, character/event graph, and rewrite generator.
- `services/ingestion`: Text and manuscript parsers with provenance tracking.
- `services/retrieval`: Embedding and reranking interfaces.
- `services/reporting`: Executive report generators.
- `packages/schemas`: Shared Pydantic data schemas & contracts.
- `packages/model_client`: NVIDIA NIM client with exponential backoff retries, JSON auto-repair, and mock provider.
- `evaluation/datasets`: Curated Weak, Moderate, and Strong benchmark suites.
- `evaluation/benchmarks`: MAE, Spearman rank correlation, taxonomy F1, and citation accuracy calculators.
