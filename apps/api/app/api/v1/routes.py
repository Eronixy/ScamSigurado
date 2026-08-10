from datetime import timedelta
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies import get_session
from app.models import Analysis, Feedback, ScamReport, ensure_utc, utc_now
from app.schemas import (
    AnalysisResult,
    FeedbackCreate,
    FeedbackResponse,
    ScamReportCreate,
    ScamReportResponse,
)
from app.services.ml_runtime import MLRuntimeRequestError, MLRuntimeUnavailableError

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/analyses", response_model=AnalysisResult, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    request: Request,
    file: UploadFile = File(description="PNG or JPEG screenshot"),
    text_model: Annotated[Literal["rf", "svm", "nb"], Form()] = "rf",
    image_model: Annotated[Literal["vggnet", "resnet", "mobilenet", "efficientnet"], Form()] = "vggnet",
    text_weight: Annotated[float, Form(ge=0, le=1)] = 0.7,
    image_weight: Annotated[float, Form(ge=0, le=1)] = 0.3,
    session: Session = Depends(get_session),
) -> AnalysisResult:
    settings = request.app.state.settings
    temporary_path = await request.app.state.upload_store.save(file)
    try:
        analysis = Analysis(expires_at=utc_now() + timedelta(days=settings.result_retention_days))
        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        if text_weight + image_weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one model weight must be positive",
            )
        result = request.app.state.ml_runtime_client.analyze(
            temporary_path,
            file.content_type,
            {
                "text_model": text_model,
                "image_model": image_model,
                "text_weight": text_weight,
                "image_weight": image_weight,
            },
        )
        analysis.status = "completed"
        analysis.prediction = result["prediction"]
        analysis.scam_risk = result["scam_risk"]
        analysis.text_confidence = result["text_confidence"]
        analysis.image_confidence = result["image_confidence"]
        analysis.extracted_text = result["extracted_text"]
        analysis.feature_importance = result["feature_importance"]
        analysis.detected_urls = result["detected_urls"]
        analysis.high_risk_keywords = result["high_risk_keywords"]
        analysis.model_version = result["model_version"]
        analysis.completed_at = utc_now()
        session.commit()
        session.refresh(analysis)
        return _analysis_response(analysis)
    except MLRuntimeRequestError as error:
        analysis.status = "failed"
        analysis.error_code = "invalid_upload"
        analysis.completed_at = utc_now()
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The screenshot could not be processed",
        ) from error
    except MLRuntimeUnavailableError as error:
        analysis.status = "failed"
        analysis.error_code = "ml_runtime_unavailable"
        analysis.completed_at = utc_now()
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Screenshot analysis is temporarily unavailable",
        ) from error
    finally:
        temporary_path.unlink(missing_ok=True)


@router.get("/analyses/{analysis_id}", response_model=AnalysisResult)
def get_analysis(analysis_id: UUID, session: Session = Depends(get_session)) -> AnalysisResult:
    analysis = session.get(Analysis, analysis_id)
    if analysis is None or ensure_utc(analysis.expires_at) <= utc_now():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return _analysis_response(analysis)


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate, session: Session = Depends(get_session)
) -> FeedbackResponse:
    if payload.analysis_id is not None and session.get(Analysis, payload.analysis_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    feedback = Feedback(**payload.model_dump())
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return FeedbackResponse(id=feedback.id, created_at=feedback.created_at)


@router.post("/reports", response_model=ScamReportResponse, status_code=status.HTTP_201_CREATED)
def create_scam_report(
    payload: ScamReportCreate, session: Session = Depends(get_session)
) -> ScamReportResponse:
    if payload.analysis_id is not None and session.get(Analysis, payload.analysis_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    report = ScamReport(**payload.model_dump())
    session.add(report)
    session.commit()
    session.refresh(report)
    return ScamReportResponse(id=report.id, created_at=report.created_at)


def _analysis_response(analysis: Analysis) -> AnalysisResult:
    return AnalysisResult(
        id=analysis.id,
        status=analysis.status,
        prediction=analysis.prediction,
        scam_risk=analysis.scam_risk,
        text_confidence=analysis.text_confidence,
        image_confidence=analysis.image_confidence,
        extracted_text=analysis.extracted_text,
        feature_importance=analysis.feature_importance,
        detected_urls=analysis.detected_urls,
        high_risk_keywords=analysis.high_risk_keywords,
        model_version=analysis.model_version,
        created_at=ensure_utc(analysis.created_at),
        completed_at=ensure_utc(analysis.completed_at) if analysis.completed_at else None,
        expires_at=ensure_utc(analysis.expires_at),
    )
