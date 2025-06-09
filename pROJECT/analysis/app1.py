import os
# Suppress TensorFlow warnings and info logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# Optional: disable oneDNN optimizations if you want consistent numeric results
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, render_template, request, jsonify
import json
from langchain_together import Together
from PyPDF2 import PdfReader  # For PDF text extraction
from docx import Document as DocxDocument  # For Word documents
from PIL import Image  # For image handling
import pytesseract  # For OCR
import numpy as np
import keras
from keras.layers import GRU, Dense, Dropout, Input, Masking, Bidirectional
from keras.models import Model
import tensorflow as tf  # Import TensorFlow for math operations
import os

# Initialize Flask app
app = Flask(__name__)

# Set API key for LLM
api_key = '5a4cc54bbbf71ae6fb492187ab58a81eaa79b1775cfbd6cbb96f6faa60cb20e0'
mistral_llm = Together(model="mistralai/Mixtral-8x7B-Instruct-v0.1", temperature=0.5, max_tokens=1024, together_api_key=api_key)

# Attention Layer for the Bi-GRU model
class AttentionLayer(keras.layers.Layer):
    def __init__(self, attention_dim=200, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        self.attention_dim = attention_dim

    def build(self, input_shape):
        # Initialize weights for the attention mechanism
        self.W = self.add_weight(shape=(input_shape[-1], self.attention_dim), initializer="glorot_uniform", trainable=True)
        self.b = self.add_weight(shape=(self.attention_dim,), initializer="zeros", trainable=True)
        self.u = self.add_weight(shape=(self.attention_dim, 1), initializer="glorot_uniform", trainable=True)
        super(AttentionLayer, self).build(input_shape)

    def call(self, x):
        # Compute attention scores
        u_t = tf.math.tanh(tf.linalg.matmul(x, self.W) + self.b)  # Use tf.math.tanh and tf.linalg.matmul
        a = tf.linalg.matmul(u_t, self.u)
        a = tf.nn.softmax(tf.squeeze(a, -1))
        weighted_input = x * tf.expand_dims(a, -1)  # Ensure dimensions match
        return tf.reduce_sum(weighted_input, axis=1)

# Model loading and building function for Bi-GRU
def load_bi_gru_model():
    input_text = Input(shape=(None, 768), dtype='float32', name='text')
    masked_input = Masking(mask_value=-99.)(input_text)
    gru_out = Bidirectional(GRU(100, return_sequences=True))(masked_input)
    gru_out = Bidirectional(GRU(100, return_sequences=True))(gru_out)
    attention_out = AttentionLayer(attention_dim=200)(gru_out)
    dropout_out = Dropout(0.5)(attention_out)
    dense_out = Dense(30, activation='relu')(dropout_out)
    final_out = Dense(1, activation='sigmoid')(dense_out)
    model = Model(inputs=input_text, outputs=final_out)
    return model

# Initialize the Bi-GRU model
bi_gru_model = load_bi_gru_model()

# Document input function with OCR for scanned documents
def extract_text_from_file(file):
    text = ""
    if file.filename.endswith(".pdf"):
        pdf_reader = PdfReader(file)
        text = "\n\n".join([page.extract_text().strip() for page in pdf_reader.pages if page.extract_text()])
    elif file.filename.endswith(".docx"):
        doc = DocxDocument(file)
        text = "\n\n".join([paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text])
    elif file.filename.lower().endswith(('png', 'jpg', 'jpeg')):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    else:
        raise ValueError("Unsupported file type.")
    return text

# Analyze case details using both models
def analyze_case(case_details):
    # Generate Bi-GRU model prediction
    embedded_input = np.random.randn(1, 512, 768)  # Replace with actual embeddings
    bi_gru_prediction = bi_gru_model.predict(embedded_input)
    bi_gru_verdict = "Guilty" if bi_gru_prediction[0][0] > 0.5 else "Not Guilty"
    
    # Generate rationale and related laws using LLM
    prompt = f"""
    Provide the rationale and relevant laws to support the predicted verdict: {bi_gru_verdict} as per given below response format having
    Case Details:
    {case_details}

    Response format:
    Rationale: (Short, concise, in future tense and directly to the point)
    Relevant Laws: (List legal references or principles that support the verdict)
    """
    response = mistral_llm(prompt)
    
    # Return the verdict followed by the rationale and relevant laws
    return f"Verdict: {bi_gru_verdict}\n\n{response.strip()}"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error="No file part")
    
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error="No selected file")
    
    try:
        document_text = extract_text_from_file(file)
        case_details = request.form['case_details']
        verdict_prediction = analyze_case(case_details)
        return render_template('index.html', case_details=case_details, result=verdict_prediction)
    except Exception as e:
        return render_template('index.html', error=str(e))


if __name__ == '__main__':
    # Turn off debug mode to prevent multiple auto-restarts and verbose logs
    app.run(debug=False, host='127.0.0.1', port=4000)
