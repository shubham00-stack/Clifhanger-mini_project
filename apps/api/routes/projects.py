"""Project management API routes."""

from typing import Dict, List
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from packages.schemas.models import ProjectCreate, ProjectRead
from packages.shared.security import enforce_project_tenancy

router = APIRouter(prefix="/api/projects", tags=["Projects"])

# In-memory storage for demonstration & standalone operation
DEFAULT_PROJECT_ID = UUID("00000000-0000-0000-0000-000000000001")
PROJECTS_STORE: Dict[UUID, ProjectRead] = {
    DEFAULT_PROJECT_ID: ProjectRead(
        id=DEFAULT_PROJECT_ID,
        title="Arctic Vault Climax",
        description="Bio-vault emergency containment breach screenplay scene.",
        genre="Sci-Fi Thriller",
        target_audience="General",
    )
}


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate):
    proj_id = uuid4()
    project = ProjectRead(
        id=proj_id,
        title=payload.title,
        description=payload.description,
        genre=payload.genre,
        target_audience=payload.target_audience,
    )
    PROJECTS_STORE[proj_id] = project
    return project


@router.get("", response_model=List[ProjectRead])
def list_projects():
    return list(PROJECTS_STORE.values())


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: UUID):
    if project_id not in PROJECTS_STORE:
        raise HTTPException(status_code=404, detail="Project not found")
    return PROJECTS_STORE[project_id]
