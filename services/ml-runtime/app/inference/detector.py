from dataclasses import dataclass
from pathlib import Path

from app.inference import heuristics, image, text
from app.inference.model_loader import ModelRegistry


@dataclass(frozen=True)
class AnalysisOptions:
    text_model: str
    image_model: str
    text_weight: float
    image_weight: float

    def validate(self) -> None:
        if self.text_weight < 0 or self.image_weight < 0:
            raise ValueError("Model weights cannot be negative")
        if self.text_weight + self.image_weight <= 0:
            raise ValueError("At least one model weight must be positive")


class ScamDetector:
    """Coordinates OCR, text inference, image inference, and user-facing signals."""

    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def analyze(self, image_path: Path, options: AnalysisOptions) -> dict:
        options.validate()
        extracted_text = text.extract_text_from_image(str(image_path))
        text_probability = text.predict_scam_probability(
            extracted_text, options.text_model, self.registry
        )
        image_probability = image.predict_scam_probability(
            image_path, options.image_model, self.registry
        )
        total_weight = options.text_weight + options.image_weight
        combined_probability = (
            options.text_weight * text_probability + options.image_weight * image_probability
        ) / total_weight
        is_scam = combined_probability > 0.5

        return {
            "prediction": "scam" if is_scam else "legitimate",
            "confidence": combined_probability if is_scam else 1 - combined_probability,
            "text_confidence": text_probability,
            "image_confidence": image_probability,
            "extracted_text": extracted_text[:500],
            "feature_importance": text.get_feature_importance(
                extracted_text, options.text_model, self.registry
            ),
            "detected_urls": heuristics.detect_urls(extracted_text),
            "high_risk_keywords": heuristics.detect_high_risk_keywords(extracted_text),
        }
