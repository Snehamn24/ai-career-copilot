from fastapi import FastAPI, UploadFile, File
import PyPDF2
import io
import pytesseract
from pdf2image import convert_from_bytes

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Career Copilot is running"}

@app.post("/analyse-resume")
async def analyse_resume(file: UploadFile = File(...)):
    try:
        # Read file
        contents = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))

        text = ""

        # ✅ Step 1: Try normal extraction
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        # ✅ Step 2: If empty → OCR
        if not text.strip():
            images = convert_from_bytes(
                contents,
                poppler_path=r"C:\Users\Sneha M N\Downloads\poppler-xx\Library\bin"
            )

            for img in images:
                text += pytesseract.image_to_string(img)

        # ✅ Final response
        return {
            "filename": file.filename,
            "extracted_text_preview": text[:500]
        }

    except Exception as e:
        return {"error": str(e)}