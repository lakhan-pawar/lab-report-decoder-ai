import streamlit as st
import os
import base64
import fitz  # PyMuPDF
from groq import Groq
from dotenv import load_dotenv
from PIL import Image
import io
import random

# ---------------------------------------------------------
# 1. Load Secrets
# ---------------------------------------------------------
load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

# ---------------------------------------------------------
# 2. Setup Page
# ---------------------------------------------------------
st.set_page_config(page_title="Lab Report Decoder", page_icon="🩺")

loading_messages = [
    "Sterilizing the AI instruments... 🧼",
    "Deciphering doctor handwriting... ✍️",
    "Paging Dr. Llama... 📟",
    "Running the centrifuge... 🌀",
    "Checking vital signs... 💓",
    "Consulting the medical journals... 📚",
    "Analyzing simpler terms... 🧠"
]

st.info(
    "⚠️ **Medical Disclaimer:** This tool is an AI prototype designed to assist with medical literacy. "
    "It is **not** a doctor and does not provide medical advice. No images or text uploaded here are stored. "
    "Consult your physician for all health decisions."
)

st.title("🩺 Lab Report Decoder")
st.write("Upload a **PDF** or **Image** of your lab result.")

# ---------------------------------------------------------
# 3. File Upload
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Upload Report", type=["jpg", "jpeg", "png", "pdf"])

# ---------------------------------------------------------
# Helper: Convert PDF → Image
# ---------------------------------------------------------
def pdf_to_image(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

# ---------------------------------------------------------
# Helper: Encode Image → Base64 (WITH RGBA FIX)
# ---------------------------------------------------------
def encode_image(image_obj):
    # FIX: Convert RGBA → RGB before saving as JPEG
    if image_obj.mode == "RGBA":
        image_obj = image_obj.convert("RGB")

    buffer = io.BytesIO()
    image_obj.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# ---------------------------------------------------------
# 4. Main Logic
# ---------------------------------------------------------
if uploaded_file:

    # Convert PDF or load image
    if uploaded_file.name.endswith(".pdf"):
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

        with st.spinner(random.choice(loading_messages)):
            try:
                base64_image = encode_image(image)

                # ---------------------------------------------------------
                # PROMPT
                # ---------------------------------------------------------
                prompt_text = """
                You are a medical lab analyzer.

                STEP 1: VALIDATION
                Check if this image is a medical lab report.
                - If NOT a medical document, output ONLY: [INVALID_DOC]
                - If YES, proceed.

                STEP 2: PRIVACY
                - Do NOT output the patient's name.

                STEP 3: ANALYSIS
                Output EACH test result on a SINGLE line.

                RULES FOR [BAD] RESULTS:
                Must include:
                1. "🛑 AVOID"
                2. "⚠️ SUGGESTION"
                3. "(Consult your Doctor)"

                FORMATS:
                [BAD] Test: Value (Range) - Explanation. (Consult your Doctor) || 🛑 AVOID:
                - Item A
                - Item B
                ⚠️ SUGGESTION:
                - Item C
                - Item D

                [WARN] Test: Value (Range) - Explanation. || ⚠️ SUGGESTION:
                - Item A
                - Item B

                [GOOD] Test: Value - Explanation.

                [INFO] Date: [Date]
                """

                # ---------------------------------------------------------
                # CORRECT GROQ IMAGE FORMAT
                # ---------------------------------------------------------
                chat_completion = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "input_image",
                                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            ]
                        }
                    ]
                )

                response_text = chat_completion.choices[0].message.content

                # ---------------------------------------------------------
                # INVALID DOCUMENT HANDLING
                # ---------------------------------------------------------
                if "[INVALID_DOC]" in response_text:
                    st.error(random.choice([
                        "🤖 I tried my best, but this doesn't look like a lab report.",
                        "🤔 This seems unrelated to medical tests. Try uploading a real report.",
                        "📉 I'm trained for lab results, not this. Please upload a proper medical report."
                    ]))
                    st.stop()

                # ---------------------------------------------------------
                # PARSE & DISPLAY RESULTS
                # ---------------------------------------------------------
                st.markdown("### 📋 Detailed Analysis & Recommendations")

                lines = response_text.split("\n")
                grouped = []

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith(("[GOOD]", "[BAD]", "[WARN]", "[INFO]")):
                        grouped.append(line)
                    elif grouped:
                        grouped[-1] += f"\n  {line}"

                for block in grouped:
                    display = block.replace("||", "\n\n")
                    display = display.replace("⚠️ SUGGESTION:", "\n\n⚠️ SUGGESTION:")

                    if block.startswith("[INFO]"):
                        if any(x in block.lower() for x in ["not found", "unknown", "n/a"]):
                            continue
                        st.info(display.replace("[INFO]", "").strip())

                    elif block.startswith("[GOOD]"):
                        st.success(display.replace("[GOOD]", "").strip())

                    elif block.startswith("[BAD]"):
                        st.error(display.replace("[BAD]", "").strip())

                    elif block.startswith("[WARN]"):
                        st.warning(display.replace("[WARN]", "").strip())

                    else:
                        st.write(display)

            except Exception as e:
                st.error(f"Error: {e}")
