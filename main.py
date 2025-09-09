import os
import cv2
import numpy as np
import easyocr
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import gc
import re
from typing import List

# Khởi tạo FastAPI app
app = FastAPI(
    title="GoPark License Plate Scanner API",
    description="OCR service for Vietnamese license plates",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global OCR reader
ocr_reader = None

def get_ocr_reader():
    """Initialize EasyOCR reader (lazy loading)"""
    global ocr_reader
    if ocr_reader is None:
        try:
            print("Initializing EasyOCR reader...")
            ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            print("EasyOCR reader initialized successfully")
        except Exception as e:
            print(f"Failed to initialize EasyOCR: {e}")
            raise e
    return ocr_reader

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Preprocess image for better OCR results"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive threshold
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

def clean_plate_text(text: str) -> str:
    """Clean and format license plate text"""
    # Remove special characters except space and dash
    cleaned = re.sub(r'[^A-Za-z0-9\s\-]', '', text)
    
    # Split into words and filter
    words = cleaned.split()
    filtered_words = []
    
    for word in words:
        if len(word) >= 2:  # Minimum 2 characters
            filtered_words.append(word.upper())
    
    return ' '.join(filtered_words)

def validate_plate_format(text: str) -> bool:
    """Basic validation for Vietnamese license plate format"""
    if not text or len(text) < 4:
        return False
    
    # Check if contains both letters and numbers
    has_letter = any(c.isalpha() for c in text)
    has_number = any(c.isdigit() for c in text)
    
    return has_letter and has_number

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GoPark License Plate Scanner API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        reader = get_ocr_reader()
        return {
            "status": "healthy",
            "ocr_engine": "easyocr",
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=500
        )

@app.post("/scan_plate")
async def scan_plate(file: UploadFile = File(...)):
    """Scan license plate from uploaded image"""
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if len(contents) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        print(f"Processing file: {file.filename}, size: {len(contents)} bytes")
        
        # Convert to OpenCV image
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Resize if too large (save memory)
        height, width = img.shape[:2]
        if width > 1000:
            ratio = 1000.0 / width
            new_width = 1000
            new_height = int(height * ratio)
            img = cv2.resize(img, (new_width, new_height))
            print(f"Resized image from {width}x{height} to {new_width}x{new_height}")
        
        # Get OCR reader
        reader = get_ocr_reader()
        
        # Run OCR on original image
        print("Running OCR...")
        results = reader.readtext(img)
        
        # Also try on preprocessed image
        preprocessed = preprocess_image(img)
        results_preprocessed = reader.readtext(preprocessed)
        
        # Combine results
        all_results = results + results_preprocessed
        
        # Process results
        plate_candidates = []
        for (bbox, text, confidence) in all_results:
            if confidence > 0.3:  # Minimum confidence threshold
                cleaned_text = clean_plate_text(text)
                if cleaned_text and validate_plate_format(cleaned_text):
                    plate_candidates.append({
                        "text": cleaned_text,
                        "confidence": confidence,
                        "bbox": bbox
                    })
                    print(f"Found candidate: '{cleaned_text}' (confidence: {confidence:.2f})")
        
        # Get best result
        if plate_candidates:
            # Sort by confidence
            plate_candidates.sort(key=lambda x: x['confidence'], reverse=True)
            best_plate = plate_candidates[0]['text']
        else:
            best_plate = "No plate detected"
        
        # Cleanup memory
        del img, contents, nparr
        if 'preprocessed' in locals():
            del preprocessed
        gc.collect()
        
        print(f"Final result: {best_plate}")
        
        return JSONResponse({
            "success": True,
            "plate": best_plate,
            "candidates": plate_candidates[:3],  # Top 3 candidates
            "total_detections": len(all_results)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in scan_plate: {str(e)}")
        # Cleanup on error
        gc.collect()
        return JSONResponse(
            content={
                "success": False,
                "error": f"Processing error: {str(e)}",
                "plate": "Error occurred"
            },
            status_code=500
        )

if __name__ == "__main__":
    # Get port from environment
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting GoPark OCR Service on port {port}")
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )