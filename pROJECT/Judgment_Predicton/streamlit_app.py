import streamlit as st #it is a web interface
import numpy as np #used to work with arrays
from PIL import Image # handle uploaded image files
from docx import Document as DocxDocument #to read docx files
from PyPDF2 import PdfReader # to read pdf files
import pytesseract #extract text from images

#deep learning model for judgment prediction
from keras.models import Model 
from keras.layers import Input, GRU, Dense, Dropout, Masking, Bidirectional

# This line imports TensorFlow, a powerful open-source library used for machine learning and deep learning.
import tensorflow as tf

# ✅ NEW OpenAI import
# Used to connect and send prompts to GPT models for generating reasoning and law references
from openai import OpenAI, OpenAIError

# ✅ Initialize OpenAI client (Replace with your key or use dummy mode)
# Initializes the OpenAI API using your API key.
client = OpenAI(api_key="sk-b24d126fe4d94dffab678e40bf5a9cc6")  # Replace with your actual key

# Optional dummy fallback if key is broken or quota exceeded
# If the real API fails or you want to test locally, a dummy output will be used.
USE_DUMMY = True

# Custom Attention Layer
# This is a custom Keras Attention Layer.
# It's used to focus on important parts of a sequence (like key sentences in a case).
# It’s applied after GRU layers in the deep model.

class AttentionLayer(tf.keras.layers.Layer):
    def __init__(self, attention_dim=200, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        self.attention_dim = attention_dim

    def build(self, input_shape):
        self.W = self.add_weight(shape=(input_shape[-1], self.attention_dim), initializer="glorot_uniform", trainable=True)
        self.b = self.add_weight(shape=(self.attention_dim,), initializer="zeros", trainable=True)
        self.u = self.add_weight(shape=(self.attention_dim, 1), initializer="glorot_uniform", trainable=True)

    def call(self, x):
        # Here, tanh is applied to:
        #Add non-linearity, so the model can learn more complex patterns.
        #This is part of the AttentionLayer, helping the model decide which parts of the input to focus on.
        u_t = tf.math.tanh(tf.linalg.matmul(x, self.W) + self.b)
        a = tf.linalg.matmul(u_t, self.u)
        a = tf.nn.softmax(tf.squeeze(a, -1))
        weighted_input = x * tf.expand_dims(a, -1)
        return tf.reduce_sum(weighted_input, axis=1)

# Build Bi-GRU Model
def load_bi_gru_model():
    input_text = Input(shape=(None, 768), dtype='float32', name='text')
    masked_input = Masking(mask_value=-99.)(input_text)

    # Bidirectional(GRU(...)): Two Bi-directional GRU layers process the sequence both forward and backward. This captures better context.
    gru_out = Bidirectional(GRU(100, return_sequences=True))(masked_input)
    gru_out = Bidirectional(GRU(100, return_sequences=True))(gru_out)

    # AttentionLayer: Adds the custom attention mechanism to focus on key info.
    attention_out = AttentionLayer(attention_dim=200)(gru_out)

    # Dropout: Prevents overfitting.
    dropout_out = Dropout(0.5)(attention_out)
    dense_out = Dense(30, activation='relu')(dropout_out)
    final_out = Dense(1, activation='sigmoid')(dense_out)

    # It returns a compiled Keras model used later to make the verdict prediction.
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
# Sends a prompt to GPT model like ChatGPT.
# Uses a "legal assistant" role to guide the response.
# If API fails or dummy mode is enabled, it returns a fake but example-like response.

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

    # Model outputs a number between 0 and 1.
    # If > 0.5 → Guilty, else Not Guilty.
    bi_gru_prediction = bi_gru_model.predict(embedded_input)
    bi_gru_verdict = "Guilty" if bi_gru_prediction[0][0] > 0.5 else "Not Guilty"

    # Combines the verdict with case details and asks GPT to give a rationale and relevant laws.
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
# Shows a header and file uploader for PDF, DOCX, or image files.
st.markdown("<h1 style='text-align: center;'>⚖️ AI Legal Assistant ⚖️</h1>", unsafe_allow_html=True)
st.subheader("👨‍⚖ Judgment Predictor", divider="grey")
uploaded_file = st.file_uploader("Upload Legal Document (PDF, DOCX, or scanned image)")

# Automatically extracts text and shows it in a textarea.
case_details = ""

if uploaded_file:
    case_details = extract_text_from_file(uploaded_file)

text_input = st.text_area("Extracted file for analysis:", case_details, height=300)

# When clicked:
    # Passes the text to analyze_case.
    # Gets a verdict + GPT-generated analysis.
    # Displays it on screen.

if st.button("Analyze Case"):
    result = analyze_case(text_input)
    st.subheader("Predicted Verdict and Analysis")
    st.write(result)