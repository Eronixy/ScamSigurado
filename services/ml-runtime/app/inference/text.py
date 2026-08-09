import logging
import re
from typing import Any

import cv2
import pytesseract

from app.inference.model_loader import ModelRegistry

logger = logging.getLogger(__name__)


def extract_text_from_image(image_path: str) -> str:
    """Run conservative OCR preprocessing before invoking Tesseract."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("The uploaded file could not be read as an image")

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    enhanced = cv2.convertScaleAbs(grayscale, alpha=1.4, beta=10)
    thresholded = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        35,
        15,
    )
    return pytesseract.image_to_string(
        thresholded,
        config="--oem 3 --psm 6 -c preserve_interword_spaces=1",
    ).strip()


def normalize_text(text: str) -> str:
    """Normalize OCR output while retaining URLs and email-like tokens."""
    normalized = text.lower()
    normalized = re.sub(
        r"\b\d{1,2}:\d{2}\s?(?:am|pm|a\.m\.|p\.m\.)?\b", "", normalized
    )
    normalized = re.sub(r"[₱$]+", " money ", normalized)
    normalized = re.sub(r"[^a-z0-9@:/\.\-\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def predict_scam_probability(text: str, model_name: str, registry: ModelRegistry) -> float:
    """Return the selected text model's scam probability in the range 0..1."""
    if not text.strip():
        return 0.5

    vectorizer = registry.vectorizer
    if vectorizer is None:
        raise RuntimeError("The TF-IDF vectorizer is unavailable")

    vector = vectorizer.transform([normalize_text(text)])
    model = registry.get_text_model(model_name)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(vector)[0]
        classes = list(getattr(model, "classes_", []))
        index = classes.index(1) if 1 in classes else min(1, len(probabilities) - 1)
        return _bounded_probability(probabilities[index])
    return _bounded_probability(model.predict(vector)[0])


def get_feature_importance(
    text: str, model_name: str, registry: ModelRegistry, top_n: int = 15
) -> list[dict[str, float | str]]:
    """Return model-specific word signals for display or auditing."""
    if not text.strip() or registry.vectorizer is None:
        return []

    vector = registry.vectorizer.transform([normalize_text(text)])
    feature_values = vector.toarray()[0]
    feature_names = registry.vectorizer.get_feature_names_out()
    model: Any = registry.get_text_model(model_name)
    scores: list[dict[str, float | str]] = []

    if hasattr(model, "coef_"):
        for index, (value, coefficient) in enumerate(zip(feature_values, model.coef_[0])):
            if value > 0:
                scores.append(
                    {
                        "word": str(feature_names[index]),
                        "importance": float(abs(coefficient * value)),
                    }
                )
    elif hasattr(model, "feature_importances_"):
        for index, (value, importance) in enumerate(
            zip(feature_values, model.feature_importances_)
        ):
            if value > 0:
                scores.append(
                    {
                        "word": str(feature_names[index]),
                        "importance": float(importance * value),
                    }
                )
    elif hasattr(model, "feature_log_prob_"):
        scam_log_probabilities = model.feature_log_prob_[1]
        for index, (value, log_probability) in enumerate(
            zip(feature_values, scam_log_probabilities)
        ):
            if value > 0:
                scores.append(
                    {
                        "word": str(feature_names[index]),
                        "importance": float(abs(value * log_probability)),
                    }
                )

    return sorted(scores, key=lambda item: float(item["importance"]), reverse=True)[:top_n]


def _bounded_probability(value: Any) -> float:
    return min(1.0, max(0.0, float(value)))
