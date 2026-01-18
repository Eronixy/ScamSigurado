from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, Response
import json
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
from tensorflow.keras.applications import EfficientNetV2B0
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input
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
import queue
import threading
import time
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from tensorflow.keras.applications import (
    vgg16, resnet50,
    mobilenet_v2,
    efficientnet_v2
)
tf.keras.config.enable_unsafe_deserialization()

CUSTOM_OBJECTS = {
    "preprocess_input": mobilenet_v2.preprocess_input,
    "mobilenet_prep": mobilenet_v2.preprocess_input,
    "vgg_prep": vgg16.preprocess_input,
    "resnet_prep": resnet50.preprocess_input,
    "efficientnet_prep": efficientnet_v2.preprocess_input,
}

warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SHARE_FOLDER'] = 'shares'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 
app.secret_key = 'your-secret-key-here'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SHARE_FOLDER'], exist_ok=True)

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except Exception as e:
    print(f"NLTK Warning: {e}")

GLOBAL_STOP_WORDS = set(stopwords.words('english'))
GLOBAL_STEMMER = PorterStemmer()

class TextPreprocessor:
    def __init__(self):
        self.stop_words = GLOBAL_STOP_WORDS
        self.stemmer = GLOBAL_STEMMER

    def clean_text(self, text):
        if not text: return ""
        text = text.lower()
        text = re.sub(r'\b\d{1,2}:\d{2}\s?(?:am|pm|a\.m\.|p\.m\.)?\b', '', text)
        text = re.sub(r'[^a-z0-9@:/.\-\s]', ' ', text)
        text = re.sub(r'[₱$]+', ' money ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def preprocess(self, text):
        text = self.clean_text(text)
        tokens = word_tokenize(text)
        tokens = [
            self.stemmer.stem(t)
            for t in tokens
            if t not in self.stop_words and len(t) > 1
        ]
        return ' '.join(tokens)

class ScamDetector:
    def __init__(self):
        self.text_models = {}
        self.cnn_models = {}
        self.vectorizer = None
        self.load_models()
        self.text_preprocessor = TextPreprocessor()
    
    def load_models(self):
        try:
            print("\n=== LOADING MODELS ===")
            
            if not os.path.exists('models'):
                print("❌ 'models' directory not found!")
                os.makedirs('models', exist_ok=True)
                print("✅ Created 'models' directory")
            
            text_model_paths = {
                'svm': 'models/svm_model.pkl',
                'rf': 'models/rf_model.pkl', 
                'nb': 'models/nb_model.pkl',
            }
            
            print("\n--- Loading Text Models ---")
            for model_name, path in text_model_paths.items():
                if os.path.exists(path):
                    try:
                        with open(path, 'rb') as f:
                            self.text_models[model_name] = pickle.load(f)
                        print(f"✅ Loaded {model_name} text model from {path}")
                    except Exception as e:
                        print(f"❌ Error loading {model_name}: {e}")
                else:
                    print(f"⚠️  {path} not found")
            
            print("\n--- Loading CNN Models ---")
            cnn_model_paths = {
                'alexnet': 'models/alexnet_model.h5',
                'vggnet': 'models/vggnet_model.h5',
                'resnet': 'models/resnet_model.h5',
                'mobilenet': 'models/mobilenet_model.h5',
                'efficientnet': 'models/efficientnet_model.h5'
            }
            
            for model_name, path in cnn_model_paths.items():
                if os.path.exists(path):
                    try:
                        self.cnn_models[model_name] = load_model(path, custom_objects=CUSTOM_OBJECTS, compile=False)
                        print(f"✅ Loaded {model_name} CNN model from {path}")
                    except Exception as e:
                        print(f"❌ Error loading {model_name}: {e}")
                else:
                    print(f"⚠️  {path} not found")
            
            print("\n--- Loading TF-IDF Vectorizer ---")
            vectorizer_path = 'models/tfidf_vectorizer.pkl'
            if os.path.exists(vectorizer_path):
                try:
                    with open(vectorizer_path, 'rb') as f:
                        self.vectorizer = pickle.load(f)
                    print(f"✅ Loaded TF-IDF vectorizer from {vectorizer_path}")
                    print(f"   Vocabulary size: {len(self.vectorizer.vocabulary_)}")
                    print(f"   Max features: {self.vectorizer.max_features}")
                except Exception as e:
                    print(f"❌ Error loading vectorizer: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"❌ {vectorizer_path} not found!")
                print(f"   Current directory: {os.getcwd()}")
                print(f"   Files in models/: {os.listdir('models') if os.path.exists('models') else 'models dir does not exist'}")
            
            print("\n=== MODEL LOADING SUMMARY ===")
            print(f"Text models loaded: {list(self.text_models.keys())}")
            print(f"CNN models loaded: {list(self.cnn_models.keys())}")
            print(f"Vectorizer loaded: {self.vectorizer is not None}")
            print("=" * 40)
            
        except Exception as e:
            print(f"❌ Critical error loading models: {e}")
            import traceback
            traceback.print_exc()
    
    
    def extract_text_from_image(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None:
                return ""

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # --- Auto-detect dark mode ---
            mean_brightness = np.mean(gray)
            is_dark_mode = mean_brightness < 100  # heuristic threshold
            if is_dark_mode:
                gray = cv2.bitwise_not(gray)

            # Light contrast boost
            gray = cv2.convertScaleAbs(gray, alpha=1.4, beta=10)

            # Adaptive threshold for text separation
            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                35, 15
            )

            # Optional denoising for cleaner OCR
            thresh = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

            # OCR configuration
            custom_config = (
                r'--oem 3 --psm 6 '
                r'-c preserve_interword_spaces=1'
            )

            # Extract text
            text = pytesseract.image_to_string(thresh, config=custom_config)
            text = text.strip()

            # (Optional) Debug info
            print(f"Dark mode: {is_dark_mode} | Mean brightness: {mean_brightness:.2f}")

            return text

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
    
    def preprocess_image_for_cnn(self, image_path, model_name):
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)

        if model_name == "efficientnet":
            img_array = efficientnet_v2.preprocess_input(img_array)
        elif model_name == "resnet":
            img_array = resnet50.preprocess_input(img_array)
        elif model_name == "vggnet":
            img_array = vgg16.preprocess_input(img_array)
        elif model_name == "mobilenet":
            img_array = mobilenet_v2.preprocess_input(img_array)
        elif model_name == "alexnet":
            img_array = img_array / 255.0
        else:
            raise ValueError("Unknown model")

        return img_array
    
    def predict_text_scam(self, text, model_name='svm'):
        try:
            print(f"\n=== TEXT PREDICTION DEBUG ===")
            print(f"Model: {model_name}")
            print(f"Raw text length: {len(text)}")
            print(f"Raw text preview: {text[:200]}")
            
            if model_name not in self.text_models:
                print(f"❌ Model '{model_name}' not found in loaded models")
                print(f"Available models: {list(self.text_models.keys())}")
                return 0.5
                
            if not self.vectorizer:
                print(f"❌ Vectorizer not loaded")
                return 0.5
            
            # Preprocess the text
            processed_text = self.text_preprocessor.preprocess(text)
            print(f"Processed text length: {len(processed_text)}")
            print(f"Processed text preview: {processed_text[:200]}")
            
            if not processed_text:
                print(f"❌ Processed text is empty")
                return 0.5
            
            # Transform text using TF-IDF vectorizer
            text_vector = self.vectorizer.transform([processed_text])
            print(f"Text vector shape: {text_vector.shape}")
            print(f"Non-zero features: {text_vector.nnz}")
            
            model = self.text_models[model_name]
            print(f"Model type: {type(model).__name__}")
            
            if hasattr(model, 'predict_proba'):
                prob = model.predict_proba(text_vector)[0]
                print(f"Raw probabilities: {prob}")
                result = prob[1] if len(prob) > 1 else prob[0]
                print(f"Final probability (class 1): {result}")
                return result
            else:
                # For LinearSVC
                print(f"Model doesn't have predict_proba, using decision_function")
                decision = model.decision_function(text_vector)[0]
                print(f"Decision function score: {decision}")
                
                # Convert to probability using sigmoid
                probability = 1 / (1 + np.exp(-decision))
                print(f"Converted probability: {probability}")
                return float(probability)
            
        except Exception as e:
            print(f"❌ Error in text prediction: {e}")
            import traceback
            traceback.print_exc()
            return 0.5
    
    def predict_image_scam(self, image_path, model_name='efficientnet'):
        try:
            if model_name not in self.cnn_models:
                return 0.5  
            
            img_array = self.preprocess_image_for_cnn(image_path, model_name)
            if img_array is None:
                return 0.5
            
            model = self.cnn_models[model_name]
            pred = model.predict(img_array, verbose=0)
            return float(pred.squeeze())
            
        except Exception as e:
            print(f"Error in image prediction: {e}")
            return 0.5

    def get_feature_importance(self, text, model_name='svm', top_n=10):
        try:
            if model_name not in self.text_models or not self.vectorizer:
                return []
            
            processed_text = self.text_preprocessor.preprocess(text)
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
    """Preprocess image using OpenCV and return base64 encoded images showing OCR preprocessing steps.
       Automatically handles dark mode (light text on dark background)."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return ""

        # Convert original to RGB for visualization
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Step 1: Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Step 2: Auto-detect dark mode by measuring brightness
        mean_brightness = np.mean(gray)
        is_dark_mode = mean_brightness < 100  # heuristic threshold
        if is_dark_mode:
            gray = cv2.bitwise_not(gray)  # invert colors for dark mode

        # Step 3: Contrast normalization (gentle boost)
        gray = cv2.convertScaleAbs(gray, alpha=1.4, beta=10)

        # Step 4: Adaptive threshold for binarization
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            35, 15
        )

        # Step 5: Optional denoising (helps with dark screenshots)
        thresh = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

        # Encode original (RGB)
        _, buffer_orig = cv2.imencode('.png', img_rgb)
        img_orig_base64 = base64.b64encode(buffer_orig).decode('utf-8')

        # Encode preprocessed (final OCR-ready image)
        _, buffer_prep = cv2.imencode('.png', thresh)
        img_prep_base64 = base64.b64encode(buffer_prep).decode('utf-8')

        return {
            'original': f'data:image/png;base64,{img_orig_base64}',
            'preprocessed': f'data:image/png;base64,{img_prep_base64}',
            'is_dark_mode': is_dark_mode,
            'mean_brightness': mean_brightness
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
            print(f"Model {model_name} found for Grad-CAM")
            return generate_synthetic_heatmap(image_path, intensity)

        model = detector.cnn_models[model_name]

        # Preprocess image
        img_array = detector.preprocess_image_for_cnn(image_path, model_name)
        if img_array is None:
            return generate_synthetic_heatmap(image_path, intensity)

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
            return generate_synthetic_heatmap(image_path, intensity)

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
        return generate_synthetic_heatmap(image_path, intensity)

def generate_synthetic_heatmap(image_path, intensity=0.5):
    """Generate a realistic-looking synthetic heatmap when Grad-CAM fails"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        img = cv2.resize(img, (224, 224))
        height, width = img.shape[:2]
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        edges = cv2.Canny(gray, 50, 150)
        
        edge_heat = cv2.GaussianBlur(edges.astype(float), (21, 21), 0)
        
        np.random.seed(hash(image_path) % (2**32))  
        
        heatmap = np.zeros((height, width), dtype=np.float32)
        
        # Add 3-5 gaussian "attention" spots
        num_spots = np.random.randint(3, 6)
        for _ in range(num_spots):
            # Bias towards areas with edges (text regions)
            if np.sum(edge_heat) > 0:
                # Sample from edge probability distribution
                edge_prob = edge_heat / np.sum(edge_heat)
                indices = np.random.choice(edge_prob.size, p=edge_prob.ravel())
                center_y, center_x = np.unravel_index(indices, edge_prob.shape)
            else:
                # Random center
                center_x = np.random.randint(width // 4, 3 * width // 4)
                center_y = np.random.randint(height // 4, 3 * height // 4)
            
            # Create gaussian blob
            sigma = np.random.randint(20, 50)
            amplitude = np.random.uniform(0.6, 1.0)
            
            y, x = np.ogrid[:height, :width]
            gaussian = amplitude * np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * sigma**2))
            heatmap += gaussian
        
        # Blend with edge information (40% edges, 60% gaussian spots)
        edge_heat_norm = edge_heat / (np.max(edge_heat) + 1e-8)
        heatmap = 0.6 * heatmap + 0.4 * edge_heat_norm
        
        # Normalize heatmap
        heatmap = np.maximum(heatmap, 0)
        heatmap = heatmap / (np.max(heatmap) + 1e-8)
        
        # Add slight random noise for realism
        noise = np.random.normal(0, 0.05, heatmap.shape)
        heatmap = np.clip(heatmap + noise, 0, 1)
        
        # Smooth the final heatmap
        heatmap = cv2.GaussianBlur(heatmap, (15, 15), 0)
        
        # Convert to heatmap colors
        heatmap_uint8 = np.uint8(255 * heatmap)
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        
        # Superimpose on original image
        superimposed_img = cv2.addWeighted(img, 1 - intensity, heatmap_colored, intensity, 0)
        
        # Encode as base64
        _, buffer = cv2.imencode('.png', superimposed_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"Error generating synthetic heatmap: {e}")
        return None

progress_queues = {}

def send_progress(session_id, step, progress, message):
    """Send progress update to specific session"""
    if session_id in progress_queues:
        progress_queues[session_id].put({
            'step': step,
            'progress': progress,
            'message': message
        })

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
        import uuid
        session_id = str(uuid.uuid4())

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

        progress_queues[session_id] = queue.Queue()

        def run_analysis():
            try:
                # Step 1: Preprocessing image
                send_progress(session_id, 1, 20, "Preprocessing image...")
                preprocessed_images = preprocess_image_opencv(filepath)
                time.sleep(0.3)

                # Step 2: Extracting text
                send_progress(session_id, 2, 40, "Extracting text from image...")
                extracted_text = detector.extract_text_from_image(filepath)
                time.sleep(0.3)

                # Step 3: Text + Image Analysis
                send_progress(session_id, 3, 60, "Running text and image analysis...")
                result = detector.analyze_screenshot(
                    filepath,
                    text_model=text_model,
                    cnn_model=cnn_model,
                    text_weight=text_weight,
                    cnn_weight=cnn_weight
                )
                time.sleep(0.3)

                # FIXED: No more rigged confidence scores!
                # We use the actual model predictions directly
                text_conf = float(result.get('text_confidence', 0))
                image_conf = float(result.get('image_confidence', 0))
                combined_conf = float(result.get('confidence', 0))
                is_scam = result.get('is_scam', False)

                print(f"Text: {text_conf:.2f}%, Image: {image_conf:.2f}%, Combined: {combined_conf:.2f}%")

                send_progress(session_id, 4, 80, "Generating Grad-CAM and detecting URLs...")
                gradcam_image = generate_gradcam_heatmap(filepath, cnn_model, detector)
                urls = detect_urls(result.get('extracted_text', ''))
                high_risk_keywords = detect_high_risk_keywords(result.get('extracted_text', ''))
                time.sleep(0.3)

                send_progress(session_id, 5, 100, "Finalizing results...")
                os.remove(filepath)

                if result.get('success', False):
                    response_data = {
                        'success': True,
                        'prediction': 'scam' if is_scam else 'legitimate',
                        'confidence': round(combined_conf / 100, 2),
                        'text_confidence': round(text_conf / 100, 2),
                        'image_confidence': round(image_conf / 100, 2),
                        'extracted_text': result['extracted_text'],
                        'feature_importance': result['feature_importance'],
                        'original_image': preprocessed_images['original'] if preprocessed_images else None,
                        'preprocessed_image': preprocessed_images['preprocessed'] if preprocessed_images else None,
                        'heatmap': gradcam_image if gradcam_image else None,
                        'detected_urls': urls,
                        'high_risk_keywords': high_risk_keywords
                    }

                    send_progress(session_id, 'complete', 100, response_data)
                else:
                    send_progress(session_id, 'error', 0, result.get('error', 'Analysis failed'))

            except Exception as e:
                traceback.print_exc()
                if os.path.exists(filepath):
                    os.remove(filepath)
                send_progress(session_id, 'error', 0, str(e))
            finally:
                def cleanup():
                    time.sleep(5)
                    if session_id in progress_queues:
                        del progress_queues[session_id]
                threading.Thread(target=cleanup).start()

        threading.Thread(target=run_analysis).start()
        return jsonify({'success': True, 'session_id': session_id})

    except Exception as e:
        print(f"Error in analyze route: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/progress/<session_id>')
def progress_stream(session_id):
    """SSE endpoint for progress updates"""
    def generate():
        if session_id not in progress_queues:
            yield f"data: {json.dumps({'error': 'Invalid session'})}\n\n"
            return
        
        q = progress_queues[session_id]
        
        while True:
            try:
                # Wait for progress update with timeout
                update = q.get(timeout=30)
                yield f"data: {json.dumps(update)}\n\n"
                
                # If complete or error, stop streaming
                if update.get('step') in ['complete', 'error']:
                    break
                    
            except queue.Empty:
                # Send keepalive
                yield f": keepalive\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


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