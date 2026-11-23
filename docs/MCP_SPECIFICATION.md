# Model Context Protocol (MCP) Server Specification

## 1. Architecture & Security Sandbox
All MCP servers communicate with internal Python services using strictly bounded, least-privilege tool methods. Models cannot execute arbitrary shell commands or raw database queries.

## 2. Server Roster

### `project_context`
- `get_project_context(project_id: UUID)`: Overview and metadata.
- `get_story_summary(project_id: UUID)`: Premise and plot trajectory.
- `get_character_profile(project_id: UUID, character_id?: UUID)`: Dramaturg profile.
- `get_open_questions(project_id: UUID)`: Active narrative questions.

### `evidence`
- `search_evidence(project_id: UUID, query?: str)`: Verifies quotes.
- `get_scene(project_id: UUID, query?: str)`: Retrieves scene text.
- `get_ending_evidence(project_id: UUID)`: Retrieves quotes from ending segment.
- `get_dimension_evidence(project_id: UUID, dimension?: str)`: Supporting proof.

### `scoring`
- `calculate_cliffhanger_score(dimension_scores: Dict)`: Deterministic math engine.
- `validate_score_evidence(analysis_ids: List[UUID])`: Provenance validation.
- `compare_analysis_versions(analysis_ids: List[UUID])`: Version comparison.

### `rewrite`
- `generate_rewrite(project_id: UUID, target_dimension: str)`: Targeted rewrite generation.
- `validate_rewrite_consistency(project_id: UUID, rewrite_text: str)`: Continuity auditor.
- `compare_rewrites(project_id: UUID)`: Candidate comparison.
