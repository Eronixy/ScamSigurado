from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf

from app.inference.image import preprocess_image
from app.inference.model_loader import ModelRegistry

LAST_CONVOLUTIONAL_LAYERS = {
    "alexnet": "conv5",
    "vggnet": "block5_conv3",
    "resnet": "conv5_block3_out",
    "mobilenet": "conv_pw_13_relu",
    "efficientnet": "top_conv",
}


def generate_heatmap_png(
    image_path: Path, model_name: str, registry: ModelRegistry, intensity: float = 0.5
) -> bytes | None:
    """Generate a PNG Grad-CAM artifact when the selected model exposes a known layer."""
    model = registry.get_image_model(model_name)
    layer_name = LAST_CONVOLUTIONAL_LAYERS.get(model_name)
    if not layer_name or layer_name not in {layer.name for layer in model.layers}:
        return None

    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer(layer_name).output, model.output]
    )
    image_array = preprocess_image(image_path, model_name)
    with tf.GradientTape() as tape:
        convolution_output, predictions = grad_model(image_array)
        loss = predictions[:, 0]

    gradients = tape.gradient(loss, convolution_output)
    pooled_gradients = tf.reduce_mean(gradients, axis=(0, 1, 2))
    heatmap = tf.reduce_mean(pooled_gradients * convolution_output[0], axis=-1).numpy()
    heatmap = np.maximum(heatmap, 0)
    heatmap /= np.max(heatmap) if np.max(heatmap) else 1

    original = cv2.imread(str(image_path))
    if original is None:
        return None
    heatmap = cv2.resize(heatmap, (original.shape[1], original.shape[0]))
    colorized = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    composed = cv2.addWeighted(original, 1 - intensity, colorized, intensity, 0)
    encoded, buffer = cv2.imencode(".png", composed)
    return buffer.tobytes() if encoded else None
