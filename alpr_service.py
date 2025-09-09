import os
import cv2
import numpy as np
import easyocr
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image

app = FastAPI()
reader = easyocr.Reader(['en'])

@app.post("/scan_plate")
async def scan_plate(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # Chuyển ảnh sang OpenCV
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # OCR bằng EasyOCR
        results = reader.readtext(img)
        text = " ".join([res[1] for res in results])

        return JSONResponse({"plate": text})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # mặc định 8000 khi chạy local
    uvicorn.run("alpr_service:app", host="0.0.0.0", port=port, reload=False)
