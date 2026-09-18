from pydantic import BaseModel, Field

STATUS_VALUES = {"not_tested", "in_progress", "passed", "failed", "na"}


class ChecklistItemOut(BaseModel):
    id: int
    code: str
    title: str
    description: str
    how_to_test: str
    remediation: str
    asvs_level: int | None = None

    class Config:
        from_attributes = True


class StandardOut(BaseModel):
    id: int
    slug: str
    name: str
    category: str
    edition: str
    description: str

    class Config:
        from_attributes = True


class StandardWithItems(StandardOut):
    items: list[ChecklistItemOut] = []


class ProjectItemOut(BaseModel):
    id: int
    checklist_item_id: int
    parent_id: int | None = None
    code: str = ""
    title: str = ""
    description: str = ""
    how_to_test: str = ""
    status: str
    notes: str
    reproduce_steps: str
    screenshots: list["ScreenshotOut"] = []
    children: list["ProjectItemOut"] = []

    class Config:
        from_attributes = True


class ScreenshotOut(BaseModel):
    id: int
    project_item_id: int
    alt_text: str

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    id: int
    name: str
    created_at: object | None = None
    updated_at: object | None = None

    class Config:
        from_attributes = True


class ProjectDetail(ProjectOut):
    items: list[ProjectItemOut] = []
    report_config: "ReportConfigOut | None" = None


class ReportConfigOut(BaseModel):
    accent_color: str
    company_name: str
    report_title: str
    exec_summary: str = ""

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    standard_slugs: list[str] = Field(default_factory=list)
    asvs_level: int | None = Field(default=None, ge=1, le=3)


class ProjectItemUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    reproduce_steps: str | None = None


class ProjectItemAdd(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=256)
    description: str = ""
    how_to_test: str = ""
    reproduce_steps: str = ""
    parent_id: int | None = None


class StandardSelect(BaseModel):
    asvs_level: int | None = Field(default=None, ge=1, le=3)
    standard_slugs: list[str] = Field(default_factory=list)


class ReportConfigUpdate(BaseModel):
    project_id: int
    accent_color: str = Field(default="#1a56db", pattern=r"^#([0-9a-fA-F]{6})$")
    company_name: str = ""
    report_title: str = ""
    memorial_text: str = ""
    exec_summary: str = ""
