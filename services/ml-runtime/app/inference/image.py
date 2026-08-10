from pathlib import Path

import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
from tensorflow.keras.applications.mobilenet import preprocess_input as mobilenet_preprocess
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.applications.vgg16 import preprocess_input as vgg_preprocess

from app.inference.model_loader import ModelRegistry


def preprocess_image(image_path: Path, model_name: str) -> tf.Tensor:
    """Reproduce training-time RGB decoding, aspect padding, and scaling."""
    encoded = tf.io.read_file(str(image_path))
    image = tf.image.decode_image(encoded, channels=3, expand_animations=False)
    image = tf.image.resize_with_pad(image, 224, 224, method="bilinear")
    image = tf.cast(image, tf.float32)
    batch = tf.expand_dims(image, axis=0)

    # The deployed artifacts expose their ImageNet bases directly. Their
    # architecture-specific preprocessing is therefore applied here once.
    if model_name == "vggnet":
        return vgg_preprocess(batch)
    if model_name == "resnet":
        return resnet_preprocess(batch)
    if model_name == "mobilenet":
        return mobilenet_preprocess(batch)
    if model_name == "efficientnet":
        # EfficientNet preprocessing is intentionally a pass-through in the
        # installed Keras version; the artifact contains its Rescaling layers.
        return efficientnet_preprocess(batch)
    if model_name == "alexnet":
        # The training graph owns AlexNet's 1/255 Rescaling layer.
        return batch
    raise ValueError(f"Unsupported image model '{model_name}'")


def predict_scam_probability(
    image_path: Path, model_name: str, registry: ModelRegistry
) -> float:
    """Return the selected image model's scam probability in the range 0..1."""
    model = registry.get_image_model(model_name)
    prediction = model(preprocess_image(image_path, model_name), training=False).numpy()[0]
    probability = prediction[0] if len(prediction) else 0.5
    return min(1.0, max(0.0, float(probability)))
