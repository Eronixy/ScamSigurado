from pathlib import Path

import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing import image as keras_image

from app.inference.model_loader import ModelRegistry


def preprocess_image(image_path: Path, model_name: str) -> np.ndarray:
    """Convert an image into the input shape expected by the selected CNN."""
    target_size = (227, 227) if model_name == "alexnet" else (224, 224)
    loaded_image = keras_image.load_img(image_path, target_size=target_size)
    image_array = keras_image.img_to_array(loaded_image)
    image_array = np.expand_dims(image_array, axis=0)
    return preprocess_input(image_array) if model_name == "efficientnet" else image_array / 255.0


def predict_scam_probability(
    image_path: Path, model_name: str, registry: ModelRegistry
) -> float:
    """Return the selected image model's scam probability in the range 0..1."""
    model = registry.get_image_model(model_name)
    prediction = model.predict(preprocess_image(image_path, model_name), verbose=0)[0]
    probability = prediction[0] if len(prediction) else 0.5
    return min(1.0, max(0.0, float(probability)))
