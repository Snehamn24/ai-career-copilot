from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
import pytesseract
from pdf2image import convert_from_bytes
from google import genai

# 🔑 Add your Gemini API key here
client = genai.Client(api_key="YOUR_API_KEY")

# 🔧 Tesseract path (keep correct)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

# ✅ CORS (for frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root API
@app.get("/")
def home():
    return {"message": "AI Career Copilot Backend is running 🚀"}


# 🚀 MAIN API: Resume Upload + AI Analysis
@app.post("/analyse-resume")
async def analyse_resume(file: UploadFile = File(...)):
    try:
        # 📥 Read file
        contents = await file.read()

        # 📄 Try normal text extraction
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = ""

        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        # 🧠 If empty → use OCR
        if not text.strip():
            images = convert_from_bytes(
                contents,
                poppler_path=r"C:\Users\Sneha M N\Downloads\poppler-xx\Library\bin"
            )

            for img in images:
                text += pytesseract.image_to_string(img)

        # 🤖 Gemini AI Analysis
        prompt = f"""
Analyze this resume and give:

1. Strengths
2. Weaknesses
3. Missing skills
4. Suggestions for improvement

Resume:
{text}
"""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        # 📤 Return response
        return {
            "filename": file.filename,
            "analysis": response.text
        }

    except Exception as e:
        return {"error": str(e)}