from typing import Literal

from pydantic import BaseModel, Field


class FeatureImportance(BaseModel):
    word: str
    importance: float


class AnalysisResponse(BaseModel):
    prediction: Literal["scam", "legitimate"]
    confidence: float = Field(ge=0, le=1)
    text_confidence: float = Field(ge=0, le=1)
    image_confidence: float = Field(ge=0, le=1)
    extracted_text: str
    feature_importance: list[FeatureImportance]
    detected_urls: list[str]
    high_risk_keywords: list[str]
    model_version: str


class RuntimeStatus(BaseModel):
    status: Literal["ok", "not_ready"]
    service: str = "scamsigurado-ml-runtime"
    model_version: str
    available_text_models: list[str] = []
    available_image_models: list[str] = []
