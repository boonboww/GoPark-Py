from fastapi import FastAPI, UploadFile, File
import easyocr
import cv2
import numpy as np

app = FastAPI()
reader = easyocr.Reader(['en'])

@app.post("/scan_plate")
async def scan_plate(file: UploadFile = File(...)):
    image_bytes = await file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = reader.readtext(img)
    text = " ".join([res[1] for res in results])

    return {"plate": text}
