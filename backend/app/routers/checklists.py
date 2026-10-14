import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ChecklistItem, Project, ProjectItem
from ..schemas import ProjectItemAdd, ProjectItemUpdate

router = APIRouter(prefix="/projects/{project_id}/items", tags=["checklists"])

_SUFFIX_RE = re.compile(r"-(\d+)$")


def _get_project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_item(db: Session, project_id: int, item_id: int) -> ProjectItem:
    item = (
        db.query(ProjectItem)
        .filter(ProjectItem.id == item_id, ProjectItem.project_id == project_id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Project item not found")
    return item


def _next_sub_code(parent: ProjectItem) -> str:
    """Auto-name a sub-point from its parent: A01 -> A01-01, A01-02, ..."""
    parent_code = (parent.checklist_item.code if parent.checklist_item else "") or "CUSTOM"
    highest = 0
    for child in parent.children:
        child_code = child.checklist_item.code if child.checklist_item else ""
        match = _SUFFIX_RE.search(child_code or "")
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{parent_code}-{highest + 1:02d}"


@router.patch("/{item_id}")
def update_item(project_id: int, item_id: int, payload: ProjectItemUpdate, db: Session = Depends(get_db)):
    item = _get_item(db, project_id, item_id)
    if payload.status is not None:
        item.status = payload.status
    if payload.notes is not None:
        item.notes = payload.notes
    if payload.reproduce_steps is not None:
        item.reproduce_steps = payload.reproduce_steps
    db.commit()
    db.refresh(item)
    return {"id": item.id, "status": item.status, "notes": item.notes, "reproduce_steps": item.reproduce_steps}


@router.post("")
def add_custom_item(project_id: int, payload: ProjectItemAdd, db: Session = Depends(get_db)):
    _get_project(db, project_id)
    if payload.parent_id is None:
        raise HTTPException(status_code=400, detail="Custom points must be added under a main point")
    parent = _get_item(db, project_id, payload.parent_id)
    if parent.parent_id is not None:
        raise HTTPException(status_code=400, detail="Sub-points can only be added to a top-level item")

    code = payload.code.strip() or _next_sub_code(parent)
    item = ChecklistItem(
        standard_id=None,
        code=code,
        title=payload.title,
        description=payload.description,
        how_to_test=payload.how_to_test,
        test_examples=payload.test_examples,
        reference_url=payload.reference_url,
    )
    db.add(item)
    db.flush()
    pi = ProjectItem(
        project_id=project_id,
        checklist_item_id=item.id,
        parent_id=parent.id,
        reproduce_steps=payload.reproduce_steps,
    )
    db.add(pi)
    db.commit()
    db.refresh(pi)
    return {
        "id": pi.id,
        "parent_id": pi.parent_id,
        "code": code,
        "title": payload.title,
        "reproduce_steps": payload.reproduce_steps,
    }


@router.delete("/{item_id}", status_code=204)
def delete_item(project_id: int, item_id: int, db: Session = Depends(get_db)):
    item = _get_item(db, project_id, item_id)
    # Custom items carry their own project-scoped ChecklistItem (standard_id is
    # NULL); seeded items are shared across projects and must never be removed.
    custom_checklist_ids = [
        pi.checklist_item_id
        for pi in [item, *item.children]
        if (ci := db.get(ChecklistItem, pi.checklist_item_id)) is not None and ci.standard_id is None
    ]
    db.delete(item)
    db.flush()
    for checklist_id in custom_checklist_ids:
        ci = db.get(ChecklistItem, checklist_id)
        if ci is not None:
            db.delete(ci)
    db.commit()
