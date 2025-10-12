from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from tensorflow.keras.models import load_model
import os
import pickle
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import pytesseract
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing import image
import warnings
import io
import traceback
from datetime import datetime
from jinja2 import Template
import subprocess
import tempfile
from datetime import datetime
import base64
from io import BytesIO
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SHARE_FOLDER'] = 'shares'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 
app.secret_key = 'your-secret-key-here'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SHARE_FOLDER'], exist_ok=True)

class ScamDetector:
    def __init__(self):
        self.text_models = {}
        self.cnn_models = {}
        self.vectorizer = None
        self.load_models()
    
    def load_models(self):
        try:
            text_model_paths = {
                'svm': 'models/svm_model.pkl',
                'rf': 'models/rf_model.pkl', 
                'nb': 'models/nb_model.pkl',
            }
            
            for model_name, path in text_model_paths.items():
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        self.text_models[model_name] = pickle.load(f)
                    print(f"Loaded {model_name} text model")
            
            cnn_model_paths = {
                'alexnet': 'models/alexnet_model.h5',
                'vggnet': 'models/vggnet_model.h5',
                'resnet': 'models/resnet_model.h5',
                'mobilenet': 'models/mobilenet_model.h5',
                'efficientnet': 'models/efficientnet_model.h5'
            }
            
            for model_name, path in cnn_model_paths.items():
                if os.path.exists(path):
                    self.cnn_models[model_name] = load_model(path)
                    print(f"Loaded {model_name} CNN model")
            
            if os.path.exists('models/tfidf_vectorizer.pkl'):
                with open('models/tfidf_vectorizer.pkl', 'rb') as f:
                    self.vectorizer = pickle.load(f)
                print("Loaded TF-IDF vectorizer")
            
        except Exception as e:
            print(f"Error loading models: {e}")
    
    
    def extract_text_from_image(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None:
                return ""

            # Step 1: Grayscale + contrast boost
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.convertScaleAbs(gray, alpha=1.7, beta=15)

            # Step 2: Denoise but keep edges
            gray = cv2.bilateralFilter(gray, 11, 75, 75)

            # Step 3: Threshold — adapt to lighting
            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                35, 15
            )

            # Step 4: Morphological cleanup (remove noise + connect letters)
            kernel = np.ones((2, 2), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # Step 5: Invert for Tesseract
            thresh = cv2.bitwise_not(thresh)

            # Step 6: OCR config — focus on text symbols only
            custom_config = (
                r'--oem 3 --psm 6 '
                r'-c preserve_interword_spaces=1 '
                r'-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:/.-@ '
            )

            text = pytesseract.image_to_string(thresh, config=custom_config)
            return text.strip()

        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def preprocess_text(self, text):
        if not text:
            return ""

        text = text.lower()

        # Remove timestamps
        text = re.sub(r'\b\d{1,2}:\d{2}\s?(?:am|pm|a\.m\.|p\.m\.)?\b', '', text)

        # Keep URLs, emails, dots, and hyphens (important for scam detection)
        text = re.sub(r'[^a-z0-9@:/.\-\s]', ' ', text)

        # Normalize currency symbols (₱, $, etc.)
        text = re.sub(r'[₱$]+', ' money ', text)

        # Replace multiple spaces with one
        text = re.sub(r'\s+', ' ', text)

        return text.strip()
    
    def preprocess_image_for_cnn(self, image_path, model_name='efficientnet'):
        try:
            if model_name in ['efficientnet', 'mobilenet', 'vggnet', 'resnet']:
                target_size = (224, 224)
            else: 
                target_size = (227, 227)
            
            img = image.load_img(image_path, target_size=target_size)
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            
            if model_name == 'efficientnet':
                img_array = preprocess_input(img_array)
            else:
                img_array = img_array / 255.0 
            
            return img_array
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def predict_text_scam(self, text, model_name='svm'):
        try:
            if model_name not in self.text_models or not self.vectorizer:
                return 0.5
            
            processed_text = self.preprocess_text(text)
            if not processed_text:
                return 0.5
            
            text_vector = self.vectorizer.transform([processed_text])
            model = self.text_models[model_name]
            
            if hasattr(model, 'predict_proba'):
                prob = model.predict_proba(text_vector)[0]
                return prob[1] if len(prob) > 1 else prob[0] 
            else:
                prediction = model.predict(text_vector)[0]
                return float(prediction)
            
        except Exception as e:
            print(f"Error in text prediction: {e}")
            return 0.5
    
    def predict_image_scam(self, image_path, model_name='efficientnet'):
        try:
            if model_name not in self.cnn_models:
                return 0.5  
            
            img_array = self.preprocess_image_for_cnn(image_path, model_name)
            if img_array is None:
                return 0.5
            
            model = self.cnn_models[model_name]
            prediction = model.predict(img_array)[0]
            return float(prediction[0]) if len(prediction) > 0 else 0.5
            
        except Exception as e:
            print(f"Error in image prediction: {e}")
            return 0.5

    def get_feature_importance(self, text, model_name='svm', top_n=10):
        try:
            if model_name not in self.text_models or not self.vectorizer:
                return []
            
            processed_text = self.preprocess_text(text)
            if not processed_text:
                return []

            text_vector = self.vectorizer.transform([processed_text])
            model = self.text_models[model_name]
            feature_names = self.vectorizer.get_feature_names_out()

            if model_name == 'svm' and hasattr(model, 'coef_'):
                coefficients = model.coef_[0]
                text_features = text_vector.toarray()[0]
                feature_scores = []
                
                for idx, (feature_val, coef) in enumerate(zip(text_features, coefficients)):
                    if feature_val > 0: 
                        importance = abs(coef * feature_val)
                        feature_scores.append({
                            'word': feature_names[idx],
                            'importance': float(importance),
                            'coefficient': float(coef)
                        })
                
                feature_scores.sort(key=lambda x: x['importance'], reverse=True)
                return feature_scores[:top_n]
            
            elif model_name == 'rf' and hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                text_features = text_vector.toarray()[0]
                feature_scores = []
                
                for idx, (feature_val, importance) in enumerate(zip(text_features, importances)):
                    if feature_val > 0: 
                        score = importance * feature_val
                        feature_scores.append({
                            'word': feature_names[idx],
                            'importance': float(score),
                            'feature_importance': float(importance)
                        })
                
                feature_scores.sort(key=lambda x: x['importance'], reverse=True)
                return feature_scores[:top_n]
            
            elif model_name == 'nb' and hasattr(model, 'feature_log_prob_'):
                scam_log_probs = model.feature_log_prob_[1]
                text_features = text_vector.toarray()[0]
                feature_scores = []
                
                for idx, (feature_val, log_prob) in enumerate(zip(text_features, scam_log_probs)):
                    if feature_val > 0: 
                        score = feature_val * log_prob
                        feature_scores.append({
                            'word': feature_names[idx],
                            'importance': float(abs(score)),
                            'log_prob': float(log_prob)
                        })
                
                feature_scores.sort(key=lambda x: x['importance'], reverse=True)
                return feature_scores[:top_n]
            
            return []
            
        except Exception as e:
            print(f"Error getting feature importance: {e}")
            return []
    
    def analyze_screenshot(self, image_path, text_model='svm', cnn_model='efficientnet', 
                        text_weight=0.6, cnn_weight=0.4):
        try:
            extracted_text = self.extract_text_from_image(image_path)
            text_probability = self.predict_text_scam(extracted_text, text_model)
            image_probability = self.predict_image_scam(image_path, cnn_model)
            
            combined_probability = (text_weight * text_probability + 
                                cnn_weight * image_probability)
            
            is_scam = bool(combined_probability > 0.5) 
            confidence = float(combined_probability if is_scam else (1 - combined_probability))
            feature_importance = self.get_feature_importance(extracted_text, text_model, top_n=15)
            
            return {
                'success': True,
                'is_scam': is_scam, 
                'confidence': confidence * 100,
                'text_confidence': float(text_probability) * 100,
                'image_confidence': float(image_probability) * 100,
                'extracted_text': extracted_text[:500],
                'combined_probability': float(combined_probability),
                'feature_importance': feature_importance
            }

        except Exception as e:
            print(f"Error in analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'is_scam': False,
                'confidence': 0.0,
                'text_confidence': 0.0,
                'image_confidence': 0.0,
                'extracted_text': "",
                'combined_probability': 0.0,
                'feature_importance': []
            }


def preprocess_image_opencv(image_path):
    """Preprocess image using OpenCV and return base64 encoded images with layout analysis"""
    try:
        # Read original
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        
        # Encode original
        _, buffer_orig = cv2.imencode('.png', img_rgb)
        img_orig_base64 = base64.b64encode(buffer_orig).decode('utf-8')
        
        # Encode preprocessed
        _, buffer_prep = cv2.imencode('.png', thresh)
        img_prep_base64 = base64.b64encode(buffer_prep).decode('utf-8')
        
        return {
            'original': f'data:image/png;base64,{img_orig_base64}',
            'preprocessed': f'data:image/png;base64,{img_prep_base64}'
        }
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return None

def detect_urls(text):
    """Extract URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls

def detect_high_risk_keywords(text):
    """Detect high-risk keywords in text"""
    high_risk_words = [
        'urgent', 'verify', 'suspend', 'confirm', 'click', 'prize', 
        'winner', 'claim', 'account', 'password', 'security', 'alert',
        'congratulations', 'free', 'limited time', 'act now', 'guarantee'
    ]
    
    detected = []
    text_lower = text.lower()
    
    for word in high_risk_words:
        if word in text_lower:
            detected.append(word)
    
    return detected

def generate_gradcam_heatmap(image_path, model_name, detector, intensity=0.5):
    """Generate Grad-CAM heatmap supporting all CNN models"""
    try:
        if model_name not in detector.cnn_models:
            print(f"Model {model_name} not found for Grad-CAM.")
            return None

        model = detector.cnn_models[model_name]

        # Preprocess image
        img_array = detector.preprocess_image_for_cnn(image_path, model_name)
        if img_array is None:
            return None

        # Get the last convolutional layer based on model type
        layer_map = {
            'vggnet': 'block5_conv3',
            'resnet': 'conv5_block3_out',
            'mobilenet': 'conv_pw_13_relu',
            'efficientnet': 'top_conv',
            'alexnet': 'conv5'
        }
        last_conv_layer_name = layer_map.get(model_name)
        if last_conv_layer_name not in [layer.name for layer in model.layers]:
            print(f"Layer {last_conv_layer_name} not found in {model_name}")
            return None

        grad_model = tf.keras.models.Model(
            [model.inputs],
            [model.get_layer(last_conv_layer_name).output, model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            loss = predictions[:, 0]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]

        heatmap = tf.reduce_mean(tf.multiply(pooled_grads, conv_outputs), axis=-1)
        heatmap = np.maximum(heatmap, 0)
        heatmap /= np.max(heatmap) if np.max(heatmap) != 0 else 1

        # Load original image
        img = cv2.imread(image_path)
        img = cv2.resize(img, (224, 224))

        if hasattr(heatmap, 'numpy'):
            heatmap = heatmap.numpy()

        # No second .numpy() call here
        heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap = np.uint8(255 * heatmap)
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        superimposed_img = cv2.addWeighted(img, 1 - intensity, heatmap, intensity, 0)

        # Encode as base64
        _, buffer = cv2.imencode('.png', superimposed_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        print(f"Error generating Grad-CAM for {model_name}: {e}")
        return None

# Initialize detector
detector = ScamDetector()

# Routes
@app.route('/')
def home():
    return render_template('home.html', active_page='home')

@app.route('/upload')
def upload():
    return render_template('upload.html', active_page='upload')

@app.route('/learn')
def learn():
    return render_template('learn.html', active_page='learn')

@app.route('/results')
def about():
    return render_template('results.html', active_page='results')

@app.route('/settings')
def settings():
    return render_template('settings.html', active_page='settings')

# API Routes
@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
        text_model = request.form.get('text_model', 'svm')
        cnn_model = request.form.get('cnn_model', 'efficientnet')
        text_weight = float(request.form.get('text_weight', 0.6))
        cnn_weight = float(request.form.get('cnn_weight', 0.4))
        
        filename = f"temp_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Run main analysis
            result = detector.analyze_screenshot(
                filepath, 
                text_model=text_model,
                cnn_model=cnn_model,
                text_weight=text_weight,
                cnn_weight=cnn_weight
            )
            
            # Get preprocessed images
            preprocessed_images = preprocess_image_opencv(filepath)
            
            # Generate detailed heatmap with layout analysis
            scam_confidence = result.get('combined_probability', 0.5)
            gradcam_image = generate_gradcam_heatmap(filepath, cnn_model, detector)
            
            # Detect URLs and high-risk keywords
            extracted_text = result.get('extracted_text', '')
            urls = detect_urls(extracted_text)
            high_risk_keywords = detect_high_risk_keywords(extracted_text)
            
            # Clean up temp file
            os.remove(filepath)
            
            if result.get('success', False):
                response_data = {
                    'success': True,
                    'prediction': 'scam' if result['is_scam'] else 'legitimate',
                    'confidence': round(float(result['confidence']) / 100, 2),
                    'text_confidence': round(float(result['text_confidence']) / 100, 2),
                    'image_confidence': round(float(result['image_confidence']) / 100, 2),
                    'extracted_text': result['extracted_text'],
                    'feature_importance': result['feature_importance'],
                    
                    # Enhanced data
                    'original_image': preprocessed_images['original'] if preprocessed_images else None,
                    'preprocessed_image': preprocessed_images['preprocessed'] if preprocessed_images else None,
                    'heatmap': gradcam_image if gradcam_image else None,
                    'detected_urls': urls,
                    'high_risk_keywords': high_risk_keywords
                }
                return jsonify(response_data)
            else:
                return jsonify({
                    'success': False, 
                    'error': result.get('error', 'Analysis failed')
                }), 500
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
            
    except Exception as e:
        print(f"Error in analyze route: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Analysis failed'}), 500


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        print(f"Feedback received: {data}")
        # TODO: Save feedback to database
        return jsonify({'success': True, 'message': 'Feedback received'})
        
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({'success': False, 'error': 'Failed to submit feedback'}), 500

@app.route('/api/report', methods=['POST'])
def report_scam():
    try:
        data = request.get_json()
        print(f"Scam report received: {data}")
        # TODO: Save report to database
        return jsonify({'success': True, 'message': 'Report submitted'})
        
    except Exception as e:
        print(f"Error submitting report: {e}")
        return jsonify({'success': False, 'error': 'Failed to submit report'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)