import os
import cv2
import numpy as np
import easyocr
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import gc

app = FastAPI()

# Khởi tạo reader với cấu hình tối ưu memory
reader = None

def get_reader():
    global reader
    if reader is None:
        # Chỉ load English, tắt GPU để tiết kiệm memory
        reader = easyocr.Reader(['en'], gpu=False)
    return reader

@app.post("/scan_plate")
async def scan_plate(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        # Resize ảnh để giảm memory usage
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Resize ảnh xuống kích thước nhỏ hơn (giữ tỉ lệ)
        height, width = img.shape[:2]
        if width > 800:  # Giới hạn width tối đa 800px
            ratio = 800.0 / width
            new_width = 800
            new_height = int(height * ratio)
            img = cv2.resize(img, (new_width, new_height))
        
        # OCR bằng EasyOCR
        ocr_reader = get_reader()
        results = ocr_reader.readtext(img)
        
        # Lọc kết quả có confidence cao và có thể là biển số
        filtered_text = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5 and len(text.strip()) > 2:  # Chỉ lấy text có confidence > 0.5
                filtered_text.append(text.strip())
        
        final_text = " ".join(filtered_text) if filtered_text else "No plate detected"
        
        # Clear memory sau mỗi request
        del img, contents, nparr
        gc.collect()
        
        return JSONResponse({"plate": final_text})
        
    except Exception as e:
        # Clear memory khi có lỗi
        gc.collect()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(f"{__name__}:app", host="0.0.0.0", port=port, reload=False)