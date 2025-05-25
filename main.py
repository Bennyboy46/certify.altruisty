from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import qrcode
from io import BytesIO
import base64
import cv2
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime
import uuid
from pdf_generator import generate_certificate_pdf
from content_generator import CertificateContentGenerator
from chatbot import CertificateChatbot

app = FastAPI(title="Smart Certificate Generator & Verification System")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
certificates_db: Dict[str, Dict[str, Any]] = {}
users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin
        "role": "admin"
    }
}

# Initialize the content generator and chatbot
generator = CertificateContentGenerator()
chatbot = CertificateChatbot(certificates_db=certificates_db)

class Certificate(BaseModel):
    recipient_name: str
    course_name: str
    issue_date: str
    certificate_id: Optional[str] = None
    qr_code: Optional[str] = None
    content: Optional[str] = None

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CertificateRequest(BaseModel):
    recipient_name: str
    course_name: str
    issue_date: str
    course_type: str = "technical"
    include_appreciation: bool = True

class ChatbotRequest(BaseModel):
    text: str
    conversation_id: Optional[str] = None
    certificate_id: Optional[str] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user["username"], "token_type": "bearer"}

def verify_password(plain_password, hashed_password):
    return plain_password == "admin"  # In production, use proper password hashing

def generate_qr_code(data: str) -> str:
    """Generate QR code and return as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    qr_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@app.post("/generate-certificate", response_model=Certificate)
async def generate_certificate(certificate: Certificate):
    # Generate unique certificate ID
    certificate_id = str(uuid.uuid4())
    certificate.certificate_id = certificate_id
    
    # Generate QR code
    qr_data = f"Certificate ID: {certificate_id}"
    certificate.qr_code = generate_qr_code(qr_data)
    
    # Store certificate
    certificates_db[certificate_id] = certificate.dict()
    
    return certificate

@app.get("/verify-certificate/{certificate_id}")
async def verify_certificate(certificate_id: str):
    if certificate_id not in certificates_db:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return certificates_db[certificate_id]

@app.get("/certificates", response_model=List[Certificate])
async def list_certificates(token: str = Depends(oauth2_scheme)):
    return list(certificates_db.values())

@app.post("/generate-certificate-pdf")
async def generate_certificate_pdf_endpoint(request: CertificateRequest):
    try:
        # Generate a unique certificate ID
        certificate_id = str(uuid.uuid4())
        
        # Create certificate data
        certificate_data = {
            "certificate_id": certificate_id,
            "recipient_name": request.recipient_name,
            "course_name": request.course_name,
            "issue_date": request.issue_date
        }
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(certificate_id)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64
        buffered = BytesIO()
        qr_img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Generate PDF
        pdf_buffer = generate_certificate_pdf(certificate_data, qr_base64)
        
        # Store in database
        certificates_db[certificate_id] = certificate_data
        
        return {
            "certificate_id": certificate_id,
            "pdf_base64": base64.b64encode(pdf_buffer.getvalue()).decode()
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/certificates/generate", response_model=Certificate)
async def certificates_generate(request: CertificateRequest):
    # Generate unique certificate ID
    certificate_id = str(uuid.uuid4())
    
    # Generate content using the generator
    generated_content = generator.generate_content(
        name=request.recipient_name,
        course=request.course_name,
        course_type=request.course_type,
        include_appreciation=request.include_appreciation
    )
    
    # Generate QR code
    qr_data = f"Certificate ID: {certificate_id}"
    qr_code = generate_qr_code(qr_data)
    
    # Store certificate
    cert_data = {
        "recipient_name": request.recipient_name,
        "course_name": request.course_name,
        "issue_date": request.issue_date,
        "certificate_id": certificate_id,
        "qr_code": qr_code,
        "content": generated_content
    }
    certificates_db[certificate_id] = cert_data
    
    return cert_data

@app.get("/certificates/{certificate_id}/pdf")
async def get_certificate_pdf(certificate_id: str):
    cert = certificates_db.get(certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    pdf_buffer = generate_certificate_pdf(cert)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=certificate_{certificate_id}.pdf"
        }
    )

@app.post("/verify-certificate-chatbot")
async def verify_certificate_chatbot(request: ChatbotRequest):
    # Get certificate data if available
    certificate_data = None
    if request.certificate_id:
        certificate_data = certificates_db.get(request.certificate_id)
    
    # Get response from chatbot
    response = chatbot.get_bot_response(
        conversation_id=request.conversation_id or str(uuid.uuid4()),
        user_input=request.text,
        certificate_data=certificate_data
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 