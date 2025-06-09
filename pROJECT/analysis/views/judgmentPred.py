import streamlit as st
import numpy as np
from PIL import Image
from docx import Document as DocxDocument
from PyPDF2 import PdfReader
import pytesseract
from keras.models import Model
from keras.layers import Input, GRU, Dense, Dropout, Masking, Bidirectional
import tensorflow as tf

# ✅ NEW OpenAI import
from openai import OpenAI, OpenAIError

# ✅ Initialize OpenAI client (Replace with your key or use dummy mode)
client = OpenAI(api_key="5a4cc54bbbf71ae6fb492187ab58a81eaa79b1775cfbd6cbb96f6faa60cb20e0")  # Replace with your actual key

# Optional dummy fallback if key is broken or quota exceeded
USE_DUMMY = True

# Custom Attention Layer
class AttentionLayer(tf.keras.layers.Layer):
    def __init__(self, attention_dim=200, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        self.attention_dim = attention_dim

    def build(self, input_shape):
        self.W = self.add_weight(shape=(input_shape[-1], self.attention_dim), initializer="glorot_uniform", trainable=True)
        self.b = self.add_weight(shape=(self.attention_dim,), initializer="zeros", trainable=True)
        self.u = self.add_weight(shape=(self.attention_dim, 1), initializer="glorot_uniform", trainable=True)

    def call(self, x):
        u_t = tf.math.tanh(tf.linalg.matmul(x, self.W) + self.b)
        a = tf.linalg.matmul(u_t, self.u)
        a = tf.nn.softmax(tf.squeeze(a, -1))
        weighted_input = x * tf.expand_dims(a, -1)
        return tf.reduce_sum(weighted_input, axis=1)

# Build Bi-GRU Model
def load_bi_gru_model():
    input_text = Input(shape=(None, 768), dtype='float32', name='text')
    masked_input = Masking(mask_value=-99.)(input_text)
    gru_out = Bidirectional(GRU(100, return_sequences=True))(masked_input)
    gru_out = Bidirectional(GRU(100, return_sequences=True))(gru_out)
    attention_out = AttentionLayer(attention_dim=200)(gru_out)
    dropout_out = Dropout(0.5)(attention_out)
    dense_out = Dense(30, activation='relu')(dropout_out)
    final_out = Dense(1, activation='sigmoid')(dense_out)
    return Model(inputs=input_text, outputs=final_out)

bi_gru_model = load_bi_gru_model()

# Extract text from files
def extract_text_from_file(file):
    text = ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = "\n\n".join([p.extract_text().strip() for p in reader.pages if p.extract_text()])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = DocxDocument(file)
        text = "\n\n".join([p.text.strip() for p in doc.paragraphs if p.text])
    elif file.type.startswith("image/"):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    else:
        st.error("Unsupported file type.")
    return text

# 🔮 GPT-4 Call
def call_gpt(prompt):
    if USE_DUMMY:
        return "Rationale: Based on the presented evidence and applicable laws, the individual is deemed guilty.\nRelevant Laws: IPC Section 302, Indian Evidence Act Section 114."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use gpt-4 only if you have access
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        return f"⚠️ OpenAI Error: {str(e)}"

# Analyze case
def analyze_case(case_details):
    embedded_input = np.random.randn(1, 512, 768)  # Dummy embedding
    bi_gru_prediction = bi_gru_model.predict(embedded_input)
    bi_gru_verdict = "Guilty" if bi_gru_prediction[0][0] > 0.5 else "Not Guilty"

    prompt = f"""
    Provide the rationale and relevant laws to support the predicted verdict: {bi_gru_verdict}.
    Case Details:
    {case_details}

    Response format:
    Rationale: (Short, concise)
    Relevant Laws: (List of laws or principles)
    """
    response = call_gpt(prompt)
    return f"Verdict: {bi_gru_verdict}\n\n{response}"

# 🔵 Streamlit UI
st.markdown("<h1 style='text-align: center;'>⚖️ AI Legal Assistant ⚖️</h1>", unsafe_allow_html=True)
st.subheader("👨‍⚖ Judgment Predictor", divider="grey")
uploaded_file = st.file_uploader("Upload Legal Document (PDF, DOCX, or scanned image)")
case_details = ""

if uploaded_file:
    case_details = extract_text_from_file(uploaded_file)

text_input = st.text_area("Extracted file for analysis:", case_details, height=300)

if st.button("Analyze Case"):
    result = analyze_case(text_input)
    st.subheader("Predicted Verdict and Analysis")
    st.write(result)
