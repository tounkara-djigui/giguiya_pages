from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    subtitle: str = Field(default="", max_length=300)
    category: str = Field(default="Comunità", max_length=60)
    summary: str = Field(default="", max_length=600)
    description: str = ""
    image_url: str | None = Field(default=None, max_length=500)
    partners: str = Field(default="", max_length=300)
    year_label: str = Field(default="", max_length=40)
    highlights: list[str] = []
    is_published: bool = True
    sort_order: int = 0


class ProjectOut(ProjectIn):
    model_config = ConfigDict(from_attributes=True)
    id: str
    slug: str
    created_at: datetime
