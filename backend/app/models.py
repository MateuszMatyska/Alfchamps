from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Standard(Base):
    __tablename__ = "standards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(16), index=True)  # web | api | mobile | genai
    edition: Mapped[str] = mapped_column(String(64), default="")
    description: Mapped[str] = mapped_column(Text, default="")

    items: Mapped[list["ChecklistItem"]] = relationship(
        back_populates="standard", cascade="all, delete-orphan"
    )


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    standard_id: Mapped[int | None] = mapped_column(ForeignKey("standards.id"), index=True, nullable=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text, default="")
    how_to_test: Mapped[str] = mapped_column(Text, default="")
    remediation: Mapped[str] = mapped_column(Text, default="")
    asvs_level: Mapped[int | None] = mapped_column(Integer, nullable=True)

    standard: Mapped["Standard"] = relationship(back_populates="items")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    items: Mapped[list["ProjectItem"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    report_config: Mapped["ReportConfig | None"] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=False
    )


class ProjectItem(Base):
    __tablename__ = "project_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    checklist_item_id: Mapped[int] = mapped_column(ForeignKey("checklist_items.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("project_items.id"), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="not_tested")
    notes: Mapped[str] = mapped_column(Text, default="")
    reproduce_steps: Mapped[str] = mapped_column(Text, default="")

    project: Mapped["Project"] = relationship(back_populates="items")
    checklist_item: Mapped["ChecklistItem"] = relationship()
    screenshots: Mapped[list["Screenshot"]] = relationship(
        back_populates="project_item", cascade="all, delete-orphan"
    )
    children: Mapped[list["ProjectItem"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    parent: Mapped["ProjectItem | None"] = relationship(back_populates="children", remote_side="ProjectItem.id")


class Screenshot(Base):
    __tablename__ = "screenshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_item_id: Mapped[int] = mapped_column(ForeignKey("project_items.id"), index=True)
    file_path: Mapped[str] = mapped_column(String(512))
    alt_text: Mapped[str] = mapped_column(String(256), default="")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project_item: Mapped["ProjectItem"] = relationship(back_populates="screenshots")


class ReportConfig(Base):
    __tablename__ = "report_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), unique=True)
    accent_color: Mapped[str] = mapped_column(String(16), default="#1a56db")
    company_name: Mapped[str] = mapped_column(String(256), default="")
    company_logo_path: Mapped[str] = mapped_column(String(512), default="")
    memorial_text: Mapped[str] = mapped_column(Text, default="")
    exec_summary: Mapped[str] = mapped_column(Text, default="")
    report_title: Mapped[str] = mapped_column(String(256), default="")

    project: Mapped["Project"] = relationship(back_populates="report_config")
