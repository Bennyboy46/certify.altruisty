import requests
import json
from datetime import datetime

def test_certificate_generation():
    # Test data
    test_certificate = {
        "recipient_name": "John Doe",
        "course_name": "Python Programming",
        "issue_date": datetime.now().strftime("%Y-%m-%d")
    }

    # Test certificate generation
    print("Testing certificate generation...")
    response = requests.post(
        "http://localhost:8000/generate-certificate",
        json=test_certificate
    )
    
    if response.status_code == 200:
        certificate = response.json()
        print("✓ Certificate generated successfully")
        print(f"Certificate ID: {certificate['certificate_id']}")
        print(f"QR Code generated: {'Yes' if certificate['qr_code'] else 'No'}")
    else:
        print("✗ Failed to generate certificate")
        print(f"Status code: {response.status_code}")
        print(f"Error: {response.text}")
        return

    # Test PDF generation
    print("\nTesting PDF generation...")
    response = requests.post(
        "http://localhost:8000/generate-certificate-pdf",
        json=test_certificate
    )
    
    if response.status_code == 200:
        print("✓ PDF generated successfully")
        # Save the PDF
        with open("test_certificate.pdf", "wb") as f:
            f.write(response.content)
        print("PDF saved as 'test_certificate.pdf'")
    else:
        print("✗ Failed to generate PDF")
        print(f"Status code: {response.status_code}")
        print(f"Error: {response.text}")
        return

    # Test certificate verification
    print("\nTesting certificate verification...")
    response = requests.get(
        f"http://localhost:8000/verify-certificate/{certificate['certificate_id']}"
    )
    
    if response.status_code == 200:
        verified_certificate = response.json()
        print("✓ Certificate verified successfully")
        print(f"Verified recipient: {verified_certificate['recipient_name']}")
        print(f"Verified course: {verified_certificate['course_name']}")
    else:
        print("✗ Failed to verify certificate")
        print(f"Status code: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Starting certificate system tests...\n")
    test_certificate_generation() 