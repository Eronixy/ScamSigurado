from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    status: str
    service: str
    environment: str


class FeatureImportance(BaseModel):
    word: str
    importance: float


class AnalysisResult(BaseModel):
    id: UUID
    status: Literal["completed", "failed", "processing"]
    prediction: Literal["scam", "legitimate"] | None = None
    scam_risk: float | None = Field(default=None, ge=0, le=1)
    text_confidence: float | None = Field(default=None, ge=0, le=1)
    image_confidence: float | None = Field(default=None, ge=0, le=1)
    extracted_text: str | None = None
    feature_importance: list[FeatureImportance] = Field(default_factory=list)
    detected_urls: list[str] = Field(default_factory=list)
    high_risk_keywords: list[str] = Field(default_factory=list)
    model_version: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    expires_at: datetime


class FeedbackCreate(BaseModel):
    analysis_id: UUID | None = None
    was_result_accurate: bool
    comment: str | None = Field(default=None, max_length=2_000)


class FeedbackResponse(BaseModel):
    id: UUID
    created_at: datetime


class ScamReportCreate(BaseModel):
    analysis_id: UUID | None = None
    category: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=10, max_length=5_000)
    contact_information: str | None = Field(default=None, max_length=500)


class ScamReportResponse(BaseModel):
    id: UUID
    created_at: datetime
