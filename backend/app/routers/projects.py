from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import ChecklistItem, Project, ProjectItem, ReportConfig, Standard
from ..schemas import (
    ProjectCreate,
    ProjectDetail,
    ProjectOut,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_project(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.updated_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = (
        db.query(Project)
        .options(
            joinedload(Project.items).joinedload(ProjectItem.screenshots),
            joinedload(Project.items).joinedload(ProjectItem.checklist_item),
        )
        .filter(Project.id == project_id)
        .first()
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    result = ProjectDetail.model_validate(project)
    out_by_id = {out.id: out for out in result.items}
    for out in result.items:
        out.children = []
    for pi in project.items:
        out = out_by_id[pi.id]
        out.parent_id = pi.parent_id
        out.code = pi.checklist_item.code if pi.checklist_item else ""
        out.title = pi.checklist_item.title if pi.checklist_item else ""
        out.description = pi.checklist_item.description if pi.checklist_item else ""
        out.how_to_test = pi.checklist_item.how_to_test if pi.checklist_item else ""
    for pi in project.items:
        if pi.parent_id is not None and pi.parent_id in out_by_id:
            out_by_id[pi.parent_id].children.append(out_by_id[pi.id])
    for out in result.items:
        out.children.sort(key=lambda c: c.id)
    result.items = [out for out in result.items if out.parent_id is None]
    return result


@router.post("", response_model=ProjectDetail)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=payload.name)
    db.add(project)
    db.flush()

    rows = (
        db.query(ChecklistItem)
        .join(Standard)
        .filter(Standard.slug.in_(payload.standard_slugs))
        .order_by(Standard.id, ChecklistItem.code)
    )
    if payload.asvs_level is not None:
        # The ASVS level filter applies ONLY to ASVS items. Other standards'
        # items (with NULL asvs_level) must remain included.
        rows = rows.filter(
            or_(
                Standard.slug != "owasp-asvs",
                ChecklistItem.asvs_level <= payload.asvs_level,
            )
        )
    for item in rows.all():
        db.add(ProjectItem(project_id=project.id, checklist_item_id=item.id))

    db.add(ReportConfig(project_id=project.id, report_title=payload.name))
    db.commit()
    return get_project(project.id, db)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = _get_project(db, project_id)
    db.delete(project)
    db.commit()
