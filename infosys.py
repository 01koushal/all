import fitz  # PyMuPDF
import cv2
import numpy as np
import pytesseract
import json
import os
import re
from pyzbar.pyzbar import decode
from datetime import datetime

# Set up Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_qr_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pix = doc[0].get_pixmap()
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.h, pix.w, pix.n))
    cv_img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB if img.shape[-1] == 4 else cv2.COLOR_RGB2BGR)
    return extract_qr_from_image_array(cv_img)

def extract_qr_from_image_array(image):
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    qr_codes = decode(gray)
    if qr_codes:
        return qr_codes[0].data.decode('utf-8')
    return None

def extract_text_from_certificate(file_path):
    text = ""
    if file_path.lower().endswith(".pdf"):
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text("text")
    else:
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
    return text

def normalize_date(date_text):
    try:
        return datetime.strptime(date_text, "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_text

def verify_certificate(file_path):
    try:
        qr_data = extract_qr_from_pdf(file_path) if file_path.lower().endswith(".pdf") else None

        if not qr_data:
            return "❌ No QR Code found."

        qr_json = json.loads(qr_data)
        cert_details = {
            "issuedTo": qr_json["credentialSubject"]["issuedTo"].strip().lower(),
            "course": qr_json["credentialSubject"]["course"].strip().lower(),
            "completedOn": qr_json["credentialSubject"]["completedOn"][:10]
        }

        extracted_text = extract_text_from_certificate(file_path).strip().lower()
        match = re.search(r"on (\w+ \d{1,2}, \d{4})", extracted_text)
        ocr_date = normalize_date(match.group(1)) if match else None

        if (
            cert_details["issuedTo"] in extracted_text and
            cert_details["course"] in extracted_text and
            (ocr_date == cert_details["completedOn"])
        ):
            return "✅ Certificate is GENUINE. Data matches the official record."
        else:
            return "❌ Certificate is FAKE. Data does not match official records."

    except json.JSONDecodeError:
        return "❌ QR Code does not contain valid JSON. Unable to verify."

    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def run_verification(file_path):
    if os.path.exists(file_path):
        return verify_certificate(file_path)
    else:
        return "❌ Error: File not found. Please provide a valid file path."
