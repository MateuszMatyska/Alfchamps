from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ChecklistItem, Project, ProjectItem
from ..schemas import ProjectItemAdd, ProjectItemUpdate

router = APIRouter(prefix="/projects/{project_id}/items", tags=["checklists"])


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
    if payload.parent_id is not None:
        parent = _get_item(db, project_id, payload.parent_id)
        if parent.parent_id is not None:
            raise HTTPException(status_code=400, detail="Sub-points can only be added to a top-level item")
    item = ChecklistItem(
        standard_id=None,
        code=payload.code,
        title=payload.title,
        description=payload.description,
        how_to_test=payload.how_to_test,
    )
    db.add(item)
    db.flush()
    pi = ProjectItem(
        project_id=project_id,
        checklist_item_id=item.id,
        parent_id=payload.parent_id,
        reproduce_steps=payload.reproduce_steps,
    )
    db.add(pi)
    db.commit()
    db.refresh(pi)
    return {
        "id": pi.id,
        "parent_id": pi.parent_id,
        "code": payload.code,
        "title": payload.title,
        "reproduce_steps": payload.reproduce_steps,
    }


@router.delete("/{item_id}", status_code=204)
def delete_item(project_id: int, item_id: int, db: Session = Depends(get_db)):
    item = _get_item(db, project_id, item_id)
    db.delete(item)
    db.commit()
