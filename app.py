import streamlit as st
import os
import base64
import fitz  # PyMuPDF
from groq import Groq
from dotenv import load_dotenv
from PIL import Image
import io
import random

# 1. Load Secrets
load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

# 2. Setup Page
st.set_page_config(page_title="Lab Report Decoder", page_icon="🩺")

# --- CUSTOM LOADING MESSAGES ---
loading_messages = [
    "Sterilizing the AI instruments... 🧼",
    "Deciphering doctor handwriting... ✍️",
    "Paging Dr. Llama... 📟",
    "Running the centrifuge... 🌀",
    "Checking vital signs... 💓",
    "Consulting the medical journals... 📚",
    "Analyzing simpler terms... 🧠"
]

# --- DISCLAIMER ---
st.info("⚠️ **Medical Disclaimer:** This tool is an AI prototype designed to assist with medical literacy. It is **not** a doctor and does not provide medical advice. No images or text uploaded here are stored on our servers. Please consult your physician for all health decisions.")

st.title("🩺 Lab Report Decoder")
st.write("Upload a **PDF** or **Image** of your lab result.")

# 3. File Uploader
uploaded_file = st.file_uploader("Upload Report", type=["jpg", "jpeg", "png", "pdf"])

# Helper: Convert PDF Page to Image
def pdf_to_image(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    page = doc.load_page(0) 
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

# Helper: Encode Image for AI
def encode_image(image_obj):
    buffered = io.BytesIO()
    image_obj.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# 4. The Logic
if uploaded_file:
    if uploaded_file.name.endswith('.pdf'):
        with st.spinner(f"{random.choice(loading_messages)} (Converting PDF)"):
            image = pdf_to_image(uploaded_file)
    else:
        image = Image.open(uploaded_file)

    st.image(image, caption="Report Preview", use_container_width=True)
    
    if st.button("Analyze Report 🔍"):
        if not api_key:
            st.error("API Key missing!")
            st.stop()
            
        client = Groq(api_key=api_key)
        
        spinner_text = random.choice(loading_messages)
        
        with st.spinner(spinner_text):
            try:
                base64_image = encode_image(image)
                
                # --- PROMPT ---
                prompt_text = """
                You are a medical lab analyzer. 
                
                STEP 1: VALIDATION
                Check if this image is a medical lab report.
                - If NOT a medical document, output ONLY: [INVALID_DOC]
                - If YES, proceed to STEP 2.

                STEP 2: PRIVACY CHECK
                - Do NOT output the patient's name.

                STEP 3: ROBUST ANALYSIS
                Output EACH test result on a SINGLE text line.
                
                CRITICAL RULE FOR [BAD] RESULTS: 
                You MUST provide:
                1. "🛑 AVOID" (What not to do)
                2. "⚠️ SUGGESTION" (What to do instead)
                3. The tag "(Consult your Doctor)"
                
                FORMAT RULES:
                [BAD] Test Name: Value (Ref Range) - Explanation. (Consult your Doctor) || 🛑 AVOID:\n- Item A\n- Item B\n⚠️ SUGGESTION:\n- Item C\n- Item D
                [WARN] Test Name: Value (Ref Range) - Explanation. || ⚠️ SUGGESTION:\n- Item A\n- Item B
                [GOOD] Test Name: Value - Explanation.
                [INFO] Date: [Date]

                Example Output:
                [INFO] Date: Oct 15, 2025
                [BAD] LDL Cholesterol: 160 (High) - This is 'bad' cholesterol. (Consult your Doctor) || 🛑 AVOID:\n- Fried foods\n- Red meat\n⚠️ SUGGESTION:\n- Eat Oats & Fiber\n- 30 min Cardio daily
                [WARN] Vitamin D: 28 (Low) - Slightly low. || ⚠️ SUGGESTION:\n- Morning sunlight\n- Fatty fish
                [GOOD] Hemoglobin: 14.0 - Perfect.
                """

                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    model="meta-llama/llama-4-scout-17b-16e-instruct", 
                )
                
                response_text = chat_completion.choices[0].message.content
                
                # --- CHECK FOR INVALID DOCUMENT ---
                if "[INVALID_DOC]" in response_text:
                    error_messages = [
                        "🤖 Look, I have a PhD in deciphering medical gibberish, but I have *no idea* what this is. I'm not smart enough for the real world yet—please stick to lab reports!",
                        "🤔 Is this... art? Because it definitely isn't a cholesterol test. I only speak 'Doctor', not 'Random Internet Image'. Try again with a real report!",
                        "📉 I'm just a baby AI trying to read blood tests. Please don't confuse me with pictures of your cat/lunch/car. I might cry."
                    ]
                    st.error(random.choice(error_messages))
                    st.stop() 

                # --- IF VALID, SHOW RESULTS ---
                st.markdown("### 📋 Detailed Analysis & Recommendations")

                lines = response_text.split('\n')
                final_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    
                    # --- IMPROVED PARSER: STICKY GROUPING ---
                    if line.startswith(("[GOOD]", "[BAD]", "[WARN]", "[INFO]")):
                        final_lines.append(line)
                    elif final_lines:
                        final_lines[-1] += f"\n  {line}" 
                    
                for line in final_lines:
                    # Clean up separator
                    display_text = line.replace("||", "\n\n")
                    
                    # --- FORCE NEW LINE FOR SUGGESTIONS ---
                    # This fixes the issue where "SUGGESTION" gets stuck on the previous line
                    display_text = display_text.replace("⚠️ SUGGESTION:", "\n\n⚠️ SUGGESTION:")
                    
                    # --- PYTHON FILTER: HIDE "NOT FOUND" DATES ---
                    if line.startswith("[INFO]"):
                        lower_line = line.lower()
                        if "not found" in lower_line or "n/a" in lower_line or "unknown" in lower_line:
                            continue 
                        st.info(display_text.replace("[INFO]", "").strip())
                        
                    elif line.startswith("[GOOD]"):
                        st.success(display_text.replace("[GOOD]", "").strip())
                    elif line.startswith("[BAD]"):
                        st.error(display_text.replace("[BAD]", "").strip())
                    elif line.startswith("[WARN]"):
                        st.warning(display_text.replace("[WARN]", "").strip())
                    else:
                        st.write(display_text)
                
            except Exception as e:
                st.error(f"Error: {e}")
