"""Unit tests for Model Context Protocol (MCP) servers."""

import pytest
from uuid import uuid4
from mcp.project_context.server import registry as pc_reg
from mcp.evidence.server import registry as ev_reg
from mcp.scoring.server import registry as sc_reg
from mcp.rewrite.server import registry as rw_reg


def test_project_context_mcp_tools():
    proj_id = uuid4()
    context = pc_reg.execute_tool("get_project_context", project_id=proj_id)
    assert context["project_id"] == str(proj_id)

    summary = pc_reg.execute_tool("get_story_summary", project_id=proj_id)
    assert "summary" in summary

    questions = pc_reg.execute_tool("get_open_questions", project_id=proj_id)
    assert len(questions) > 0


def test_evidence_mcp_tools():
    proj_id = uuid4()
    evidence = ev_reg.execute_tool("search_evidence", project_id=proj_id)
    assert len(evidence) > 0
    assert "quote" in evidence[0]


def test_scoring_mcp_tools():
    scores = {
        "unresolved_question": {"score": 85.0},
        "stakes": {"score": 90.0},
        "emotional_intensity": {"score": 85.0},
        "character_consequence": {"score": 80.0},
        "surprise": {"score": 75.0},
        "urgency": {"score": 90.0},
        "causal_setup": {"score": 80.0},
        "information_gap": {"score": 70.0},
        "originality": {"score": 75.0},
    }
    result = sc_reg.execute_tool("calculate_cliffhanger_score", dimension_scores=scores)
    assert result["final_score"] > 80.0
    assert result["score_band"] == "Very Strong"


def test_rewrite_mcp_tools():
    proj_id = uuid4()
    rewrite = rw_reg.execute_tool("generate_rewrite", project_id=proj_id, target_dimension="urgency")
    assert "content" in rewrite
    assert rewrite["predicted_score"] > 80.0

    audit = rw_reg.execute_tool("validate_rewrite_consistency", project_id=proj_id, rewrite_text=rewrite["content"])
    assert audit["is_consistent"] is True
