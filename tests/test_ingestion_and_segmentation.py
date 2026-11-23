import io
import pytest
from uuid import uuid4
from docx import Document
from pypdf import PdfWriter
from fastapi.testclient import TestClient
from apps.api.main import app
from services.ingestion.parser import ManuscriptParser
from services.narrative.segmenter import NarrativeSegmenter
from packages.shared.errors import IngestionError
from packages.schemas.enums import LocationType

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

def test_manuscript_parser_pdf():
    parser = ManuscriptParser()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buf = io.BytesIO()
    writer.write(buf)
    
    res = parser.parse_pdf("blank.pdf", buf.getvalue())
    assert res["asset_type"] == "pdf"
    assert res["page_count"] == 1

def test_manuscript_parser_empty_files_raise_error():
    parser = ManuscriptParser()
    with pytest.raises(IngestionError):
        parser.parse_pdf("empty.pdf", b"")
    with pytest.raises(IngestionError):
        parser.parse_docx("empty.docx", b"")

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

    # Out-of-bounds boundary index must fallback safely without clearing all flags
    fallback_scenes = segmenter.set_ending_boundary(scenes, boundary_scene_index=999)
    assert any(s["is_ending_segment"] for s in fallback_scenes)

def test_api_upload_and_scene_endpoints():
    from apps.api.routes.projects import create_project
    from apps.api.routes.analysis import (
        upload_document,
        get_project_scenes,
        set_ending_boundary,
    )
    from packages.schemas.models import ProjectCreate
    from fastapi import UploadFile

    proj = create_project(ProjectCreate(title="Ingestion Test Project"))
    proj_id = proj.id

    # Upload document
    file_content = b"INT. BUNKER - NIGHT\nSoldier locks the blast door.\n\nEXT. SURFACE - NIGHT\nThe bomb detonates."
    upload_file = UploadFile(filename="script.txt", file=io.BytesIO(file_content))
    upload_res = upload_document(project_id=proj_id, file=upload_file)
    assert upload_res["scene_count"] >= 2

    # Get segmented scenes
    scenes = get_project_scenes(project_id=proj_id)
    assert len(scenes) >= 2
    assert scenes[-1]["is_ending_segment"] is True

    # Shift boundary to scene 1
    updated_scenes = set_ending_boundary(project_id=proj_id, scene_index=1)
    assert updated_scenes[0]["is_ending_segment"] is True
    assert updated_scenes[1]["is_ending_segment"] is False

    # Out-of-bounds boundary index returns 400 Bad Request
    with pytest.raises(Exception):
        set_ending_boundary(project_id=proj_id, scene_index=999)

    # Analyze project without explicit text (pulls uploaded asset seamlessly)
    from packages.schemas.requests import AnalysisRequest
    from apps.api.routes.analysis import analyze_cliffhanger, upload_and_analyze_document
    analyze_asset_res = analyze_cliffhanger(project_id=proj_id, payload=AnalysisRequest())
    assert analyze_asset_res.final_score > 0
    assert len(analyze_asset_res.dimension_breakdown) == 9

def test_api_direct_document_upload_and_analyze():
    from apps.api.routes.analysis import upload_and_analyze_document
    from fastapi import UploadFile
    file_content = b"INT. MISSILE SILO - NIGHT\nDavid reaches for the red wire. The timer hits 00:00:01.\nCUT TO BLACK."
    upload_file = UploadFile(filename="silo_final.txt", file=io.BytesIO(file_content))
    data = upload_and_analyze_document(file=upload_file)
    assert data.final_score >= 70.0
    tax_types = [t.get("type") or t.get("label") for t in data.taxonomy_classifications]
    assert "threat" in tax_types
