from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from model import CertificateContentGenerator

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the content generator
generator = CertificateContentGenerator()

class ContentRequest(BaseModel):
    name: str
    course: str
    course_type: str = "technical"
    include_appreciation: bool = True
    num_options: int = 3

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "course": "Python Programming",
                "course_type": "technical",
                "include_appreciation": True,
                "num_options": 3
            }
        }

@app.post("/api/generate-content")
async def generate_content(request: ContentRequest) -> List[str]:
    try:
        content_options = generator.generate_multiple_options(
            name=request.name,
            course=request.course,
            course_type=request.course_type,
            num_options=request.num_options
        )
        return content_options
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 