# GoPark Python OCR Service

Vietnamese License Plate Recognition service using EasyOCR and FastAPI.

## Features
- License plate detection and recognition
- Image preprocessing for better accuracy
- RESTful API with FastAPI
- Memory optimized for deployment
- CORS enabled for web integration

## API Endpoints

### Health Check
```
GET /health
```

### Scan License Plate
```
POST /scan_plate
Content-Type: multipart/form-data
Body: file (image file)
```

Response:
```json
{
  "success": true,
  "plate": "29A12345",
  "candidates": [...],
  "total_detections": 5
}
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Deploy to Render

1. Connect GitHub repo to Render
2. Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
3. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables:
   - `PYTHON_VERSION=3.11`
   - `PORT=8000`
   - `PYTHONUNBUFFERED=1`