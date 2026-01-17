# 🩺 Lab Report Decoder AI

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-App-red) ![Groq](https://img.shields.io/badge/Groq-Fast_Inference-orange) ![Llama 4](https://img.shields.io/badge/Model-Llama_4_Scout-purple)

**A Privacy-First AI tool that translates complex medical lab reports into plain English.**

## 📖 Overview
We've all been there: you get a blood test result, see a scary number, and panic. **Lab Report Decoder** solves the "Health Literacy" gap by using Multimodal AI to read medical documents (Images or PDFs) and explain them in simple terms.

Unlike generic chatbots, this tool is engineered for **Actionable Intelligence**. It doesn't just say "High Cholesterol"; it provides specific dietary restrictions and lifestyle suggestions based on the values found.

## ✨ Key Features
* **📄 PDF & Image Support:** Custom pipeline using `PyMuPDF` to convert multi-page PDF reports into vision-ready images.
* **🔒 Privacy by Design:** The system is strictly prompted to **never** output patient names, ensuring anonymized analysis.
* **🚦 Actionable Advice:** * **Green:** Good results (Positive reinforcement).
    * **Red/Orange:** Bad results include specific `🛑 AVOID` and `⚠️ SUGGESTION` lists (foods, habits).
* **🛡️ Gatekeeper Logic:** Rejects non-medical images (e.g., selfies, pets) with a humorous error message to prevent hallucinations.

## 🛠️ Tech Stack
* **LLM Engine:** Meta Llama 4 Scout (17B) via **Groq API** (Ultra-low latency).
* **Computer Vision:** Multimodal analysis for reading table structures.
* **Frontend:** Streamlit (Python).
* **Preprocessing:** `PyMuPDF` (Fitz) for PDF rendering.

## 🚀 How to Run Locally

1.  **Clone the Repo**
    ```bash
    git clone [https://github.com/lakhan-pawar/lab-report-decoder-ai](https://github.com/lakhan-pawar/lab-report-decoder-ai.git)
    cd lab-report-decoder-ai
    ```

2.  **Install Dependencies**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Setup API Keys**
    Create a `.env` file in the root folder:
    ```text
    GROQ_API_KEY=gsk_your_key_here...
    ```

4.  **Run the App**
    ```bash
    streamlit run app.py
    ```

## ⚠️ Disclaimer
**This tool is for educational purposes only.** It is not a doctor and does not provide medical advice. Always consult a certified physician for diagnosis and treatment.

---
*Built with ❤️ by Lakhan Pawar*
