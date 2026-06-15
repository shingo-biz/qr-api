import base64
import io
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
import zxingcpp

app = FastAPI(title="ZXing QR Decoder API")

class DecodeRequest(BaseModel):
    image: str  # base64 encoded image string

class DecodeResponse(BaseModel):
    status: str
    payload: str

def clean_base64(b64_string: str) -> str:
    # Strip data URL prefix if present (e.g., data:image/jpeg;base64,...)
    if ',' in b64_string:
        b64_string = b64_string.split(',', 1)[1]
    # Remove any whitespaces
    b64_string = re.sub(r'\s+', '', b64_string)
    return b64_string

@app.post("/decode", response_model=DecodeResponse)
async def decode_image(request: DecodeRequest):
    try:
        b64_clean = clean_base64(request.image)
        img_bytes = base64.b64decode(b64_clean)
        image = Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 or image data: {str(e)}")

    try:
        # Decode QR/Barcodes using zxing-cpp
        results = zxingcpp.read_barcodes(image)
        
        if not results:
            return DecodeResponse(status="error", payload="No QR code found")
        
        # Get the first decoded result
        decoded_text = results[0].text
        return DecodeResponse(status="ok", payload=decoded_text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
