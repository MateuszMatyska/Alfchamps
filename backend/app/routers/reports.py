from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session, joinedload

from ..config import get_settings
from ..database import get_db
from ..memorial import ALFRED_TAGLINE, ALFRED_TRIBUTE
from ..models import ChecklistItem, Project, ProjectItem, ReportConfig, Standard

settings = get_settings()
router = APIRouter(prefix="/projects/{project_id}/report", tags=["reports"])

STATUS_LABEL = {
    "not_tested": "Not tested",
    "in_progress": "In progress",
    "passed": "Passed",
    "failed": "Failed",
    "na": "N/A",
}

STATUS_COLOR = {
    "not_tested": colors.HexColor("#9e9e9e"),
    "in_progress": colors.HexColor("#f39c12"),
    "passed": colors.HexColor("#27ae60"),
    "failed": colors.HexColor("#e74c3c"),
    "na": colors.HexColor("#3498db"),
}


@router.get("/config")
def get_report_config(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    cfg = project.report_config or ReportConfig(project_id=project_id)
    return {
        "accent_color": cfg.accent_color,
        "company_name": cfg.company_name,
        "report_title": cfg.report_title or project.name,
        "memorial_text": cfg.memorial_text or ALFRED_TRIBUTE,
    }


@router.put("/config")
def update_report_config(project_id: int, payload: dict, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    cfg = project.report_config
    if cfg is None:
        cfg = ReportConfig(project_id=project_id)
        db.add(cfg)
    if payload.get("accent_color"):
        cfg.accent_color = payload["accent_color"]
    if payload.get("company_name") is not None:
        cfg.company_name = payload["company_name"]
    if payload.get("report_title") is not None:
        cfg.report_title = payload["report_title"]
    if payload.get("memorial_text") is not None:
        cfg.memorial_text = payload["memorial_text"]
    db.commit()
    db.refresh(cfg)
    return {
        "accent_color": cfg.accent_color,
        "company_name": cfg.company_name,
        "report_title": cfg.report_title or project.name,
    }


@router.post("/config/logo")
def upload_company_logo(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    cfg = project.report_config
    if cfg is None:
        cfg = ReportConfig(project_id=project_id)
        db.add(cfg)
    dest = _save_image(file)
    cfg.company_logo_path = str(dest)
    db.commit()
    return {"company_logo": cfg.company_logo_path, "filename": dest.name}


def _save_image(file: UploadFile) -> Path:
    from ..routers.assets import _save_image as _inner
    return _inner(file)


@router.get("/pdf")
def generate_pdf(project_id: int, db: Session = Depends(get_db)):
    project = (
        db.query(Project)
        .options(
            joinedload(Project.items).joinedload(ProjectItem.screenshots),
            joinedload(Project.items).joinedload(ProjectItem.checklist_item),
            joinedload(Project.report_config),
        )
        .filter(Project.id == project_id)
        .first()
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    config = project.report_config or ReportConfig(project_id=project_id)
    accent = colors.HexColor(config.accent_color or "#1a56db")
    memorial = config.memorial_text or ALFRED_TRIBUTE
    report_title = config.report_title or project.name

    out_file = settings.reports_dir / f"alfchamps_report_{project.id}.pdf"
    doc = SimpleDocTemplate(
        str(out_file),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=report_title,
        author="Alfchamps",
    )

    styles = getSampleStyleSheet()
    title_st = ParagraphStyle("TitleX", parent=styles["Title"], textColor=accent, fontSize=26)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=accent, fontSize=16, spaceBefore=14, spaceAfter=6)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9.5, leading=13)

    story = []

    # ---- Cover ----
    story.append(Spacer(1, 8 * mm))
    # look for the bundled copy in backend
    for candidate in (
        Path(__file__).resolve().parents[3] / "assets" / "alfred_logo.png",
        Path("assets/alfred_logo.png"),
    ):
        if candidate.exists():
            story.append(Image(str(candidate), width=70 * mm, height=70 * mm))
            break
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(_esc("ALFCHAMPS"), title_st))
    sub_st = ParagraphStyle("Sub", parent=styles["Title"], fontSize=18, textColor=colors.black)
    story.append(Paragraph(_esc(report_title), sub_st))
    story.append(Spacer(1, 10 * mm))

    if config.company_logo_path and Path(config.company_logo_path).exists():
        story.append(Image(config.company_logo_path, width=45 * mm, height=45 * mm))
    company_st = ParagraphStyle("Company", parent=styles["Normal"], fontSize=14, alignment=TA_CENTER)
    if config.company_name:
        story.append(Paragraph(_esc(config.company_name), company_st))
    else:
        story.append(Paragraph("Company", ParagraphStyle("Company", parent=company_st, textColor=colors.grey)))

    story.append(Spacer(1, 12 * mm))
    mem_st = ParagraphStyle(
        "Mem", parent=styles["Italic"], fontSize=11, textColor=colors.HexColor("#555555"), alignment=TA_CENTER
    )
    story.append(Paragraph(_esc(memorial), mem_st))
    story.append(Spacer(1, 6 * mm))
    tag_st = ParagraphStyle(
        "Tag", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#888888"), alignment=TA_CENTER
    )
    story.append(Paragraph(_esc(ALFRED_TAGLINE), tag_st))
    story.append(Spacer(1, 20 * mm))

    meta = [
        ["Project", project.name],
        ["Date", datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")],
        ["Generated by", "Alfchamps (OWASP reporting tool)"],
    ]
    t = Table(meta, colWidths=[40 * mm, 110 * mm])
    t.setStyle(_table_style(accent))
    story.append(t)
    story.append(PageBreak())

    # ---- Summary ----
    story.append(Paragraph("Executive Summary", h1))
    counts = {s: 0 for s in STATUS_LABEL}
    for pi in project.items:
        counts[pi.status] = counts.get(pi.status, 0) + 1
    total = sum(counts.values())
    summary_rows = [["Status", "Count"]]
    for status, label in STATUS_LABEL.items():
        summary_rows.append([label, str(counts.get(status, 0))])
    summary_rows.append(["Total", str(total)])
    st = Table(summary_rows, colWidths=[110 * mm, 40 * mm])
    st.setStyle(_table_style(accent))
    story.append(st)
    story.append(PageBreak())

    # ---- Grouped findings by standard ----
    groups: dict[str, list[ProjectItem]] = {}
    std_of: dict[int, Standard | None] = {}
    for ci in db.query(ChecklistItem).all():
        std_of[ci.id] = ci.standard
    for pi in project.items:
        std = std_of.get(pi.checklist_item_id)
        key = std.name if std else "Custom items"
        groups.setdefault(key, []).append(pi)

    for std_name, items in groups.items():
        story.append(Paragraph(_esc(std_name), h1))
        rows = [["ID", "Finding", "Status"]]
        for pi in sorted(items, key=lambda x: x.checklist_item.code if x.checklist_item else ""):
            rows.append([
                _esc(pi.checklist_item.code if pi.checklist_item else "-"),
                _esc(pi.checklist_item.title if pi.checklist_item else ""),
                STATUS_LABEL.get(pi.status, pi.status),
            ])
        t = Table(rows, colWidths=[26 * mm, 94 * mm, 30 * mm], repeatRows=1)
        t.setStyle(_table_style(accent))
        tbody = TableStyle([("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 8)])
        t.setStyle(tbody)
        story.append(t)
        story.append(Spacer(1, 6 * mm))

        for pi in items:
            code = pi.checklist_item.code if pi.checklist_item else "-"
            title = pi.checklist_item.title if pi.checklist_item else ""
            desc = getattr(pi.checklist_item, "description", "") if pi.checklist_item else ""
            how = getattr(pi.checklist_item, "how_to_test", "") if pi.checklist_item else ""
            item_st = ParagraphStyle(
                "Item", parent=styles["Heading3"], fontSize=10.5, textColor=accent, spaceBefore=8
            )
            story.append(Paragraph(_esc(f"{code} - {title}"), item_st))
            if desc:
                story.append(Paragraph(_esc("What / Why: ") + _esc(desc), body))
            if how:
                story.append(Paragraph(_esc("How to test: ") + _esc(how), body))
            if pi.notes:
                story.append(Paragraph(_esc("Notes: ") + _esc(pi.notes), body))
            if pi.reproduce_steps:
                story.append(Paragraph(_esc("Reproduction steps: ") + _esc(pi.reproduce_steps), body))
            for shot in pi.screenshots:
                p = Path(shot.file_path)
                if p.exists():
                    try:
                        ir = ImageReader(str(p))
                        iw, ih = ir.getSize()
                        max_w, max_h = 120 * mm, 90 * mm
                        scale = min(max_w / iw, max_h / ih)
                        if scale >= 1:
                            w, h = iw, ih
                        else:
                            w, h = iw * scale, ih * scale
                        story.append(Image(str(p), width=w, height=h))
                    except (OSError, ValueError):
                        story.append(Paragraph("(screenshot could not be embedded)", body))
            stat_st = ParagraphStyle(
                "Stat", parent=styles["Normal"], fontSize=9, textColor=STATUS_COLOR.get(pi.status, colors.black)
            )
            story.append(Paragraph(f"<b>Status:</b> {STATUS_LABEL.get(pi.status, pi.status)}", stat_st))

    doc.build(story)
    return FileResponse(str(out_file), filename=f"alfchamps-{project.id}.pdf", media_type="application/pdf")


def _esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _table_style(accent):
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), accent),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#fafafa"), colors.white]),
        ]
    )
