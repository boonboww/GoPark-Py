import os
import cv2
import numpy as np
import easyocr
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Lazy load reader
reader = None

def get_reader():
    global reader
    if reader is None:
        # chỉ load tiếng Anh để giảm dung lượng & tốc độ khởi động
        reader = easyocr.Reader(['en'], gpu=False)
    return reader

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/scan_plate")
async def scan_plate(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # Convert ảnh sang OpenCV
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # OCR
        ocr_reader = get_reader()
        results = ocr_reader.readtext(img)
        text = " ".join([res[1] for res in results]) if results else ""

        return JSONResponse({"plate": text})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("alpr_service:app", host="0.0.0.0", port=port)
