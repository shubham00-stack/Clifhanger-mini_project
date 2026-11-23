import io
from uuid import uuid4
from fastapi.testclient import TestClient
from docx import Document
from pypdf import PdfWriter
from apps.api.main import app
from services.ingestion.parser import ManuscriptParser
from services.narrative.segmenter import NarrativeSegmenter
from packages.schemas.enums import LocationType

client = TestClient(app)

def test_manuscript_parser_text():
    parser = ManuscriptParser()
    text = "Chapter 1.\n\nDetective Miller arrived at the docks."
    res = parser.parse_text("test.txt", text)
    assert res["word_count"] == 8
    assert res["char_count"] == len(text)
    assert res["paragraph_count"] == 2

def test_manuscript_parser_docx():
    parser = ManuscriptParser()
    doc = Document()
    doc.add_heading("SCENE 1: THE HANGAR", level=1)
    doc.add_paragraph("The cargo jet taxiways were clear.")
    buf = io.BytesIO()
    doc.save(buf)
    
    res = parser.parse_docx("script.docx", buf.getvalue())
    assert res["asset_type"] == "docx"
    assert "cargo jet" in res["raw_text"]
    assert res["word_count"] > 0

def test_manuscript_parser_universal_routing():
    parser = ManuscriptParser()
    text_data = b"Plain text file manuscript content."
    res = parser.parse_file("story.txt", text_data)
    assert res["asset_type"] == "text"
    assert "Plain text" in res["raw_text"]

def test_narrative_segmenter_screenplay_scenes():
    segmenter = NarrativeSegmenter()
    script = """INT. LAB - NIGHT
Dr. Chen examines the Petri dish.
CHEN
It is mutating.

EXT. CITY STREETS - CONTINUOUS
The sirens echo across the river.

INT. VAULT - NIGHT
The timer reaches zero."""

    scenes = segmenter.segment_scenes_with_provenance(script)
    assert len(scenes) >= 3
    assert scenes[0]["location_type"].upper() == "INT"
    assert scenes[1]["location_type"].upper() == "EXT"
    assert scenes[-1]["is_ending_segment"] is True

def test_dialogue_and_action_boundaries():
    segmenter = NarrativeSegmenter()
    scene = """Commander Ross enters the briefing room.

ROSS
The countdown has commenced.

He slams his fists onto the holographic table."""

    res = segmenter.extract_dialogue_and_action_boundaries(scene)
    assert res["dialogue_count"] >= 1
    assert res["dialogues"][0]["speaker"] == "ROSS"
    assert "countdown" in res["dialogues"][0]["dialogue"]
    assert res["action_count"] >= 2

def test_manual_ending_boundary_selection():
    segmenter = NarrativeSegmenter()
    script = "SCENE 1: ALPHA\nAction alpha.\n\nSCENE 2: BRAVO\nAction bravo.\n\nSCENE 3: CHARLIE\nAction charlie."
    scenes = segmenter.segment_scenes_with_provenance(script)
    assert scenes[2]["is_ending_segment"] is True

    # Move ending boundary to scene 2
    updated = segmenter.set_ending_boundary(scenes, boundary_scene_index=2)
    assert updated[1]["is_ending_segment"] is True
    assert updated[2]["is_ending_segment"] is False

def test_api_upload_and_scene_endpoints():
    proj_res = client.post("/api/projects", json={"title": "Ingestion Test Project"})
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # Upload document
    file_content = b"INT. BUNKER - NIGHT\nSoldier locks the blast door.\n\nEXT. SURFACE - NIGHT\nThe bomb detonates."
    files = {"file": ("script.txt", file_content, "text/plain")}
    upload_res = client.post(f"/api/projects/{proj_id}/upload", files=files)
    assert upload_res.status_code == 201
    assert upload_res.json()["scene_count"] >= 2

    # Get segmented scenes
    scenes_res = client.get(f"/api/projects/{proj_id}/scenes")
    assert scenes_res.status_code == 200
    scenes = scenes_res.json()
    assert len(scenes) >= 2
    assert scenes[-1]["is_ending_segment"] is True

    # Shift boundary to scene 1
    boundary_res = client.post(f"/api/projects/{proj_id}/boundary?scene_index=1")
    assert boundary_res.status_code == 200
    updated_scenes = boundary_res.json()
    assert updated_scenes[0]["is_ending_segment"] is True
    assert updated_scenes[1]["is_ending_segment"] is False
