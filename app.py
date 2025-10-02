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
            extracted_text = pytesseract.image_to_string(img_rgb)
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

def create_share_image_html2image(result_data):
    """Create a shareable PNG image using HTML template and html2image"""
    try:
        from html2image import Html2Image
        
        # Determine if scam or legitimate
        is_scam = result_data['prediction'] == 'scam'
        
        # Calculate values
        confidence = int(result_data['confidence'] * 100)
        text_confidence = int(result_data['text_confidence'] * 100)
        image_confidence = int(result_data['image_confidence'] * 100)
        
        # Set colors based on result
        if is_scam:
            status_color = '#ef4444'
            status_bg = '#fef2f2'
            status_text = 'POTENTIAL SCAM DETECTED'
            warning_message = 'Exercise caution with this content.<br>Verify through official channels.'
        else:
            status_color = '#22c55e'
            status_bg = '#f0fdf4'
            status_text = 'APPEARS LEGITIMATE'
            warning_message = 'Content appears legitimate.<br>Always stay vigilant online.'
        
        # Get timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        # Load template
        with open('templates/share_result.html', 'r') as f:
            template_content = f.read()
        
        # Replace template variables
        template = Template(template_content)
        html_content = template.render(
            is_scam=is_scam,
            status_color=status_color,
            status_bg=status_bg,
            status_text=status_text,
            confidence=confidence,
            text_confidence=text_confidence,
            image_confidence=image_confidence,
            warning_message=warning_message,
            timestamp=timestamp
        )
        
        # Initialize Html2Image
        hti = Html2Image(output_path=app.config['SHARE_FOLDER'], size=(1080, 1920))
        
        # Generate unique filename
        filename = f'share_{datetime.now().timestamp()}.png'
        
        # Convert HTML to image
        hti.screenshot(html_str=html_content, save_as=filename)
        
        # Read the generated image
        img_path = os.path.join(app.config['SHARE_FOLDER'], filename)
        with open(img_path, 'rb') as f:
            img_bytes = io.BytesIO(f.read())
        
        # Clean up
        os.remove(img_path)
        
        return img_bytes
        
    except Exception as e:
        print(f"Error creating share image with html2image: {e}")
        traceback.print_exc()
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

@app.route('/about')
def about():
    return render_template('about.html', active_page='about')

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
            result = detector.analyze_screenshot(
                filepath, 
                text_model=text_model,
                cnn_model=cnn_model,
                text_weight=text_weight,
                cnn_weight=cnn_weight
            )
            
            os.remove(filepath)
            
            if result.get('success', False):
                response_data = {
                    'success': True,
                    'prediction': 'scam' if result['is_scam'] else 'legitimate',
                    'confidence': round(float(result['confidence']) / 100, 2),
                    'text_confidence': round(float(result['text_confidence']) / 100, 2),
                    'image_confidence': round(float(result['image_confidence']) / 100, 2),
                    'extracted_text': result['extracted_text'],
                    'feature_importance': result['feature_importance']
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
            return jsonify({'success': False, 'error': str(e)}), 500
            
    except Exception as e:
        print(f"Error in analyze route: {e}")
        return jsonify({'success': False, 'error': 'Analysis failed'}), 500

@app.route("/api/share", methods=["POST"])
def share():
    try:
        print("---- /api/share called ----")
        
        req_data = request.get_json()
        result_data = req_data.get("result") if req_data else None
        
        if not result_data:
            print("❌ Missing 'result' in request")
            return jsonify({"error": "Missing result"}), 400
        
        print("Calling create_share_image_html2image with result_data...")
        
        # Use html2image version (easier to install)
        # Or use create_share_image_html if you have wkhtmltoimage installed
        img_bytes = create_share_image_html2image(result_data)
        
        if not img_bytes:
            print("❌ create_share_image returned None")
            return jsonify({"error": "Failed to create image"}), 500
        
        print("✅ Image created successfully, returning PNG...")
        
        return send_file(
            img_bytes,
            mimetype="image/png",
            as_attachment=False,
            download_name=f"ScamSigurado_analysis.png"
        )
    
    except Exception as e:
        print("🔥 Exception in /api/share:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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