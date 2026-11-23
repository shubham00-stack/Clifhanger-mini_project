# API Contracts Specification

## Base URL
`http://localhost:8000/api`

## Endpoints

### 1. Health & Readiness
`GET /api/health`
- Returns system status, environment, and model verification.

### 2. Project Management
`POST /api/projects`
- Body: `{"title": str, "description": str, "genre": str, "target_audience": str}`
- Returns: `ProjectRead`

`GET /api/projects`
- Returns: `List[ProjectRead]`

`GET /api/projects/{id}`
- Returns: `ProjectRead`

### 3. Cliffhanger Analysis
`POST /api/projects/{id}/analyze`
- Body:
```json
{
  "text": "Full story text ending in a cliffhanger cutoff...",
  "asset_id": "UUID (optional)",
  "ending_scene_index": 0,
  "model_name": "nvidia/nemotron-3-nano-omni-30b-a3b-instruct"
}
```
- Returns: `AnalysisResponse` (Score, Band, Dimension Breakdown, Taxonomy, Evidence Citations)

`GET /api/analyses/{id}`
- Returns: `AnalysisResponse`

### 4. Rewrites & Consistency Lab
`POST /api/analyses/{id}/rewrite`
- Body: `{"target_dimension": "urgency", "style": "intensified"}`
- Returns: `RewriteResponse` (Predicted score, delta, consistency audit)

`GET /api/analyses/{id}/rewrites`
- Returns: `List[RewriteResponse]`

### 5. Evaluation Benchmarks
`GET /api/benchmarks/run`
- Returns: `BenchmarkEvaluationResult` (MAE, Spearman correlation, citation accuracy, regression status)

### 6. Prometheus Observability
`GET /metrics`
- Plaintext Prometheus scrape output (request totals, latencies, response status counts).
