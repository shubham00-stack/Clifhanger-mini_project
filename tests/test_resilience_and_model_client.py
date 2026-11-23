"""Phase 7 Resilience tests: JSON auto-repair, mock client, and model fallbacks."""

import pytest
from packages.model_client.json_repair import repair_json
from packages.model_client.mock import MockModelClient
from packages.model_client.nim_client import NimModelClient


def test_repair_json_with_markdown_fences():
    raw = "```json\n{\"score\": 85.0, \"status\": \"success\"}\n```"
    repaired = repair_json(raw)
    assert repaired["score"] == 85.0
    assert repaired["status"] == "success"


def test_repair_json_with_trailing_commas_and_text():
    raw = "Here is your analysis: {\"unresolved_question\": 80, \"stakes\": 90,} Hope this helps!"
    repaired = repair_json(raw)
    assert repaired["unresolved_question"] == 80
    assert repaired["stakes"] == 90


def test_repair_json_truncated_curly_braces():
    raw = "{\"score\": 92.5, \"nested\": {\"urgency\": 88.0"
    repaired = repair_json(raw)
    assert repaired["score"] == 92.5
    assert repaired["nested"]["urgency"] == 88.0


def test_mock_model_client_deterministic_keywords():
    client = MockModelClient()

    strong_res = client.analyze_text("This is an electrifying strong countdown bomb ending!")
    assert strong_res["dimension_scores"]["urgency"]["score"] >= 80.0

    weak_res = client.analyze_text("Arthur had a weak morning tea and slept quietly.")
    assert weak_res["dimension_scores"]["stakes"]["score"] <= 40.0


def test_nim_client_offline_fallback():
    # NimModelClient without API key must gracefully fall back to mock without raising network exceptions
    client = NimModelClient(api_key="")
    models = client.verify_models()
    assert len(models) >= 2

    res = client.analyze_text("Test ending")
    assert "dimension_scores" in res
