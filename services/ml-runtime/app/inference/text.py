import logging
import math
import re
from typing import Any

import cv2
import numpy as np
import pytesseract
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

from app.inference.model_loader import ModelRegistry

logger = logging.getLogger(__name__)

# This is the NLTK English stop-word list used by the training notebook. Keep
# it local so production containers never download language data at startup.
_STOP_WORDS = frozenset(
    {
        "a",
        "about",
        "above",
        "after",
        "again",
        "against",
        "ain",
        "all",
        "am",
        "an",
        "and",
        "any",
        "are",
        "aren",
        "aren't",
        "as",
        "at",
        "be",
        "because",
        "been",
        "before",
        "being",
        "below",
        "between",
        "both",
        "but",
        "by",
        "can",
        "couldn",
        "couldn't",
        "d",
        "did",
        "didn",
        "didn't",
        "do",
        "does",
        "doesn",
        "doesn't",
        "doing",
        "don",
        "don't",
        "down",
        "during",
        "each",
        "few",
        "for",
        "from",
        "further",
        "had",
        "hadn",
        "hadn't",
        "has",
        "hasn",
        "hasn't",
        "have",
        "haven",
        "haven't",
        "having",
        "he",
        "her",
        "here",
        "hers",
        "herself",
        "him",
        "himself",
        "his",
        "how",
        "i",
        "if",
        "in",
        "into",
        "is",
        "isn",
        "isn't",
        "it",
        "it's",
        "its",
        "itself",
        "just",
        "ll",
        "m",
        "ma",
        "me",
        "mightn",
        "mightn't",
        "more",
        "most",
        "mustn",
        "mustn't",
        "my",
        "myself",
        "needn",
        "needn't",
        "no",
        "nor",
        "not",
        "now",
        "o",
        "of",
        "off",
        "on",
        "once",
        "only",
        "or",
        "other",
        "our",
        "ours",
        "ourselves",
        "out",
        "over",
        "own",
        "re",
        "s",
        "same",
        "shan",
        "shan't",
        "she",
        "she's",
        "should",
        "should've",
        "shouldn",
        "shouldn't",
        "so",
        "some",
        "such",
        "t",
        "than",
        "that",
        "that'll",
        "the",
        "their",
        "theirs",
        "them",
        "themselves",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "to",
        "too",
        "under",
        "until",
        "up",
        "ve",
        "very",
        "was",
        "wasn",
        "wasn't",
        "we",
        "were",
        "weren",
        "weren't",
        "what",
        "when",
        "where",
        "which",
        "while",
        "who",
        "whom",
        "why",
        "will",
        "with",
        "won",
        "won't",
        "wouldn",
        "wouldn't",
        "y",
        "you",
        "you'd",
        "you'll",
        "you're",
        "you've",
        "your",
        "yours",
        "yourself",
        "yourselves",
    }
)
_STEMMER = PorterStemmer()


def extract_text_from_image(image_path: str) -> str:
    """Run conservative OCR preprocessing before invoking Tesseract."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("The uploaded file could not be read as an image")

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if np.mean(grayscale) < 100:
        grayscale = cv2.bitwise_not(grayscale)
    enhanced = cv2.convertScaleAbs(grayscale, alpha=1.4, beta=10)
    thresholded = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        35,
        15,
    )
    denoised = cv2.fastNlMeansDenoising(thresholded, None, 10, 7, 21)
    return pytesseract.image_to_string(
        denoised,
        config="--oem 3 --psm 6 -c preserve_interword_spaces=1",
    ).strip()


def preprocess_text(text: str) -> str:
    """Reproduce the exact clean/tokenize/stem sequence used for training."""
    normalized = text.lower()
    normalized = re.sub(
        r"\b\d{1,2}:\d{2}\s?(?:am|pm|a\.m\.|p\.m\.)?\b", "", normalized
    )
    normalized = re.sub(r"[^a-z0-9@:/\.\-\s]", " ", normalized)
    normalized = re.sub(r"[₱$]+", " money ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    # preserve_line skips Punkt sentence loading while retaining the same
    # Treebank word tokenization used by word_tokenize during training.
    tokens = word_tokenize(normalized, preserve_line=True)
    return " ".join(
        _STEMMER.stem(token)
        for token in tokens
        if token not in _STOP_WORDS and len(token) > 1
    )


def analyze_text(
    text: str, model_name: str, registry: ModelRegistry, top_n: int = 15
) -> tuple[float, list[dict[str, float | str]]]:
    """Return scam probability and word signals using one TF-IDF transform."""
    if not text.strip():
        return 0.5, []

    vectorizer = registry.vectorizer
    if vectorizer is None:
        raise RuntimeError("The TF-IDF vectorizer is unavailable")

    processed_text = preprocess_text(text)
    if not processed_text:
        return 0.5, []

    vector = vectorizer.transform([processed_text])
    model = registry.get_text_model(model_name)
    probability = _predict_scam_probability(model, vector)
    importance = _get_feature_importance(model, vector, vectorizer, top_n)
    return probability, importance


def _predict_scam_probability(model: Any, vector: Any) -> float:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(vector)[0]
        classes = list(getattr(model, "classes_", []))
        index = classes.index(1) if 1 in classes else min(1, len(probabilities) - 1)
        return _bounded_probability(probabilities[index])
    if hasattr(model, "decision_function"):
        decision = float(model.decision_function(vector)[0])
        if decision >= 0:
            return 1.0 / (1.0 + math.exp(-decision))
        exponential = math.exp(decision)
        return exponential / (1.0 + exponential)
    return _bounded_probability(model.predict(vector)[0])


def _get_feature_importance(
    model: Any, vector: Any, vectorizer: Any, top_n: int
) -> list[dict[str, float | str]]:
    """Return model-specific word signals for display or auditing."""
    feature_values = vector.toarray()[0]
    feature_names = vectorizer.get_feature_names_out()
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
        classes = list(getattr(model, "classes_", []))
        scam_index = classes.index(1) if 1 in classes else min(1, len(model.feature_log_prob_) - 1)
        scam_log_probabilities = model.feature_log_prob_[scam_index]
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
