import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tensorflow.keras.models import load_model

logger = logging.getLogger(__name__)


class ModelUnavailableError(RuntimeError):
    """Raised when a requested model cannot serve an inference request."""


@dataclass
class ModelRegistry:
    """Loads the model set once and exposes only available models."""

    model_dir: Path
    text_models: dict[str, Any] = field(default_factory=dict)
    image_models: dict[str, Any] = field(default_factory=dict)
    vectorizer: Any | None = None
    load_errors: dict[str, str] = field(default_factory=dict)
    loaded: bool = False

    def load(self) -> None:
        self.model_dir = self.model_dir.resolve()
        self._load_pickle_models(
            {
                "svm": "svm_model.pkl",
                "rf": "rf_model.pkl",
                "nb": "nb_model.pkl",
            }
        )
        self._load_vectorizer()
        self._load_image_models(
            {
                "alexnet": "alexnet_model.h5",
                "vggnet": "vggnet_model.h5",
                "resnet": "resnet_model.h5",
                "mobilenet": "mobilenet_model.h5",
                "efficientnet": "efficientnet_model.h5",
            }
        )
        self.loaded = True
        logger.info(
            "ML registry loaded: text=%s image=%s errors=%s",
            sorted(self.text_models),
            sorted(self.image_models),
            sorted(self.load_errors),
        )

    @property
    def is_ready(self) -> bool:
        return bool(self.loaded and self.vectorizer and self.text_models and self.image_models)

    def get_text_model(self, name: str) -> Any:
        try:
            return self.text_models[name]
        except KeyError as error:
            raise ModelUnavailableError(f"Text model '{name}' is unavailable") from error

    def get_image_model(self, name: str) -> Any:
        try:
            return self.image_models[name]
        except KeyError as error:
            raise ModelUnavailableError(f"Image model '{name}' is unavailable") from error

    def _load_pickle_models(self, model_paths: dict[str, str]) -> None:
        for name, filename in model_paths.items():
            path = self.model_dir / filename
            if not path.exists():
                self.load_errors[name] = f"Missing model file: {path.name}"
                continue
            try:
                with path.open("rb") as model_file:
                    self.text_models[name] = pickle.load(model_file)
            except Exception as error:  # pragma: no cover - model files vary by runtime
                logger.exception("Unable to load text model %s", name)
                self.load_errors[name] = str(error)

    def _load_vectorizer(self) -> None:
        path = self.model_dir / "tfidf_vectorizer.pkl"
        if not path.exists():
            self.load_errors["vectorizer"] = f"Missing model file: {path.name}"
            return
        try:
            with path.open("rb") as vectorizer_file:
                self.vectorizer = pickle.load(vectorizer_file)
        except Exception as error:  # pragma: no cover - model files vary by runtime
            logger.exception("Unable to load TF-IDF vectorizer")
            self.load_errors["vectorizer"] = str(error)

    def _load_image_models(self, model_paths: dict[str, str]) -> None:
        for name, filename in model_paths.items():
            path = self.model_dir / filename
            if not path.exists():
                self.load_errors[name] = f"Missing model file: {path.name}"
                continue
            try:
                self.image_models[name] = load_model(path, compile=False)
            except Exception as error:  # pragma: no cover - model files vary by runtime
                logger.exception("Unable to load image model %s", name)
                self.load_errors[name] = str(error)
