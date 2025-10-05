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
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            gray = cv2.medianBlur(gray, 3)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)
            custom_config = r'--oem 3 --psm 6'
            extracted_text = pytesseract.image_to_string(thresh, config=custom_config)
            return extracted_text.strip()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def preprocess_text(self, text):
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        return text
    
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

def analyze_layout_and_text_regions(image_path):
    """
    Analyze image layout to detect text-rich regions and generate heatmap data.
    Returns coordinates and confidence scores for text regions.
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        height, width = gray.shape
        
        # Create heatmap overlay
        heatmap = np.zeros((height, width), dtype=np.float32)
        
        # Method 1: Text detection using connected components
        # Apply binary threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphological operations to connect text regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        dilated = cv2.dilate(binary, kernel, iterations=2)
        
        # Find contours (text regions)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Filter out very small or very large regions
            if area > 500 and area < (width * height * 0.8):
                aspect_ratio = w / float(h) if h > 0 else 0
                
                # Text typically has certain aspect ratios
                if 0.1 < aspect_ratio < 20:
                    text_regions.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'area': int(area),
                        'aspect_ratio': float(aspect_ratio)
                    })
                    
                    # Add to heatmap with Gaussian blur
                    cv2.rectangle(heatmap, (x, y), (x + w, y + h), 1.0, -1)
        
        # Method 2: Edge detection for suspicious elements
        edges = cv2.Canny(gray, 50, 150)
        edge_density = cv2.GaussianBlur(edges.astype(np.float32) / 255.0, (51, 51), 0)
        
        # Combine text regions and edge density
        heatmap = cv2.GaussianBlur(heatmap, (51, 51), 0)
        combined_heatmap = 0.7 * heatmap + 0.3 * edge_density
        
        # Normalize to 0-1 range
        if combined_heatmap.max() > 0:
            combined_heatmap = combined_heatmap / combined_heatmap.max()
        
        # Method 3: Detect high-contrast regions (often used in scams)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        contrast_map = cv2.Laplacian(enhanced, cv2.CV_64F)
        contrast_map = np.abs(contrast_map)
        contrast_map = cv2.GaussianBlur(contrast_map, (21, 21), 0)
        contrast_map = (contrast_map - contrast_map.min()) / (contrast_map.max() - contrast_map.min() + 1e-8)
        
        # Final combined heatmap
        final_heatmap = 0.5 * combined_heatmap + 0.3 * contrast_map
        
        # Create colored heatmap overlay
        heatmap_colored = cv2.applyColorMap((final_heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Blend with original image
        overlay = cv2.addWeighted(img_rgb, 0.6, heatmap_colored, 0.4, 0)
        
        # Encode heatmap
        _, buffer_heat = cv2.imencode('.png', overlay)
        heatmap_base64 = base64.b64encode(buffer_heat).decode('utf-8')
        
        # Calculate statistics
        text_density = len(text_regions) / ((width * height) / 10000)  # regions per 100x100 pixels
        total_text_area = sum(region['area'] for region in text_regions)
        text_coverage = (total_text_area / (width * height)) * 100
        
        # Detect layout characteristics
        layout_score = analyze_layout_characteristics(img_rgb, text_regions)
        
        return {
            'heatmap': f'data:image/png;base64,{heatmap_base64}',
            'text_regions': text_regions[:20],  # Limit to top 20 regions
            'statistics': {
                'total_regions': len(text_regions),
                'text_density': round(float(text_density), 2),
                'text_coverage': round(float(text_coverage), 2),
                'layout_score': round(float(layout_score), 2)
            }
        }
        
    except Exception as e:
        print(f"Error in layout analysis: {e}")
        traceback.print_exc()
        return None

def analyze_layout_characteristics(img, text_regions):
    """
    Analyze layout characteristics that might indicate scam content.
    Returns a suspicion score (0-1).
    """
    try:
        height, width, _ = img.shape
        score = 0.0
        
        # Check for center-heavy text (common in scam popups)
        center_regions = [r for r in text_regions 
                         if 0.3 * width < r['x'] + r['width']/2 < 0.7 * width and
                            0.3 * height < r['y'] + r['height']/2 < 0.7 * height]
        if len(text_regions) > 0:
            center_ratio = len(center_regions) / len(text_regions)
            if center_ratio > 0.6:
                score += 0.3
        
        # Check for large text regions (urgency indicators)
        if text_regions:
            avg_area = sum(r['area'] for r in text_regions) / len(text_regions)
            large_regions = [r for r in text_regions if r['area'] > avg_area * 2]
            if len(large_regions) > 0:
                score += 0.2
        
        # Check for high text density (cluttered, overwhelming)
        total_text_area = sum(r['area'] for r in text_regions)
        coverage = total_text_area / (width * height)
        if coverage > 0.4:
            score += 0.2
        elif coverage < 0.05:
            score += 0.1  # Very little text also suspicious
        
        # Check color analysis - bright/saturated colors
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1].mean()
        if saturation > 150:  # High saturation (bright colors)
            score += 0.3
        
        return min(score, 1.0)
        
    except Exception as e:
        print(f"Error analyzing layout characteristics: {e}")
        return 0.0

def generate_detailed_heatmap_data(image_path, scam_confidence):
    """
    Generate detailed heatmap data including text regions and suspicious areas.
    This replaces the simple radial gradient approach.
    """
    try:
        layout_data = analyze_layout_and_text_regions(image_path)
        
        if not layout_data:
            return None
        
        # Adjust heatmap intensity based on scam confidence
        intensity_multiplier = scam_confidence
        
        return {
            'heatmap_image': layout_data['heatmap'],
            'text_regions': layout_data['text_regions'],
            'statistics': layout_data['statistics'],
            'intensity': float(intensity_multiplier),
            'layout_suspicion': layout_data['statistics']['layout_score']
        }
        
    except Exception as e:
        print(f"Error generating heatmap data: {e}")
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
            heatmap_data = generate_detailed_heatmap_data(filepath, scam_confidence)
            
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
                    'heatmap': heatmap_data['heatmap_image'] if heatmap_data else None,
                    'text_regions': heatmap_data['text_regions'] if heatmap_data else [],
                    'layout_statistics': heatmap_data['statistics'] if heatmap_data else {},
                    'layout_suspicion': heatmap_data['layout_suspicion'] if heatmap_data else 0.0,
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
    app.run(debug=True)