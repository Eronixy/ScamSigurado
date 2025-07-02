from flask import Flask, render_template, request, redirect, url_for, jsonify
from tensorflow.keras.models import load_model
import os
import pickle
import numpy as np
from PIL import Image
import cv2
import pytesseract
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing import image
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class ScamDetector:
    def __init__(self):
        self.text_models = {}
        self.cnn_models = {}
        self.vectorizer = None
        self.load_models()
    
    def load_models(self):
        """Load all the pickle files"""
        try:
            text_model_paths = {
                'svm': 'models/svm_model.pkl',
                'rf': 'models/rf_model.pkl', 
                'nb': 'models/nb_model.pkl',
                # 'bert': 'models/bert_model.pkl'
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
                    with open(path, 'rb') as f:
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
            if model_name in ['efficientnet', 'mobilenet']:
                target_size = (224, 224)
            elif model_name == 'vggnet':
                target_size = (224, 224)
            elif model_name == 'resnet':
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
        """Predict scam probability from image"""
        try:
            if model_name not in self.cnn_models:
                return 0.5  
            
            img_array = self.preprocess_image_for_cnn(image_path, model_name)
            if img_array is None:
                return 0.5
            
            model = self.cnn_models[model_name]
            
            if hasattr(model, 'predict_proba'):
                prob = model.predict_proba(img_array)[0]
                return prob[1] if len(prob) > 1 else prob[0]
            elif hasattr(model, 'predict'):
                prediction = model.predict(img_array)[0]
                return float(prediction)
            else:
                return 0.5
            
        except Exception as e:
            print(f"Error in image prediction: {e}")
            return 0.5
    
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
            
            return {
                'success': True,
                'is_scam': is_scam, 
                'confidence': confidence * 100,
                'text_confidence': float(text_probability) * 100,
                'image_confidence': float(image_probability) * 100,
                'extracted_text': extracted_text[:500],
                'combined_probability': float(combined_probability)
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
                'combined_probability': 0.0
            }

detector = ScamDetector()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files.get('screenshot')
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
                print("DEBUG: Analysis successful, preparing response...")
                response_data = {
                    'success': True,
                    'is_scam': bool(result['is_scam']), 
                    'confidence': round(float(result['confidence']), 1),
                    'text_confidence': round(float(result['text_confidence']), 1),
                    'image_confidence': round(float(result['image_confidence']), 1),
                    'extracted_text': result['extracted_text']
                }
                print(f"DEBUG: Sending successful response: {response_data}")
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

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Handle user feedback"""
    try:
        data = request.get_json()
        
        print(f"Feedback received: {data}")
        
        return jsonify({'success': True, 'message': 'Feedback received'})
        
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@app.route('/report', methods=['POST'])
def report_scam():
    """Handle scam reports"""
    try:
        data = request.get_json()
        
        print(f"Scam report received: {data}")
        
        return jsonify({'success': True, 'message': 'Report submitted'})
        
    except Exception as e:
        print(f"Error submitting report: {e}")
        return jsonify({'error': 'Failed to submit report'}), 500

if __name__ == '__main__':
    app.run(debug=True)