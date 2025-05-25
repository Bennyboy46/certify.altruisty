# Smart Certificate Generator & Verification System

A FastAPI-based system for generating and verifying digital certificates with QR codes.

## Features

- Generate professional-looking PDF certificates
- Unique QR codes for each certificate
- Web-based verification system
- Admin dashboard for certificate management
- Secure authentication system

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /token` - Get authentication token
  - Username: admin
  - Password: admin

### Certificate Management

- `POST /generate-certificate` - Generate a new certificate (returns JSON)
- `POST /generate-certificate-pdf` - Generate and download PDF certificate
- `GET /verify-certificate/{certificate_id}` - Verify a certificate
- `GET /certificates` - List all certificates (admin only)

## Example Usage

1. Generate a certificate:

```bash
curl -X POST "http://localhost:8000/generate-certificate" \
     -H "Content-Type: application/json" \
     -d '{
           "recipient_name": "John Doe",
           "course_name": "Python Programming",
           "issue_date": "2024-01-01"
         }'
```

2. Verify a certificate:

```bash
curl "http://localhost:8000/verify-certificate/{certificate_id}"
```

## Security Notes

- This is a development version with basic security
- In production, implement proper password hashing
- Use a proper database instead of in-memory storage
- Implement rate limiting
- Use HTTPS in production
