import random
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

class CertificateContentGenerator:
    def __init__(self):
        self.vocabulary = self._build_vocabulary()
        self.templates = self._build_templates()
        self.achievements = self._build_achievements()
        self.appreciation_messages = self._build_appreciation_messages()
        
    def _build_vocabulary(self) -> Dict[str, List[str]]:
        return {
            'achievement_verbs': [
                'successfully completed',
                'demonstrated excellence in',
                'mastered',
                'achieved proficiency in',
                'excelled in',
                'showed outstanding performance in',
                'attained expertise in',
                'developed advanced skills in',
                'acquired comprehensive knowledge of',
                'proved exceptional competence in'
            ],
            'achievement_nouns': [
                'skills',
                'knowledge',
                'expertise',
                'proficiency',
                'competence',
                'capabilities',
                'understanding',
                'mastery',
                'abilities',
                'qualifications'
            ],
            'qualifiers': [
                'with distinction',
                'with excellence',
                'with outstanding performance',
                'with remarkable dedication',
                'with exceptional commitment',
                'with outstanding achievement',
                'with superior performance',
                'with exemplary dedication',
                'with remarkable proficiency',
                'with exceptional skill'
            ]
        }
    
    def _build_templates(self) -> List[str]:
        return [
            "This is to certify that {name} has {achievement_verb} {course} {qualifier}.",
            "We hereby certify that {name} has {achievement_verb} {course} {qualifier}.",
            "This certificate recognizes that {name} has {achievement_verb} {course} {qualifier}.",
            "We are pleased to certify that {name} has {achievement_verb} {course} {qualifier}.",
            "This document certifies that {name} has {achievement_verb} {course} {qualifier}."
        ]
    
    def _build_achievements(self) -> Dict[str, List[str]]:
        return {
            'technical': [
                "demonstrated exceptional problem-solving abilities",
                "shown remarkable analytical skills",
                "exhibited outstanding technical expertise",
                "proven advanced programming capabilities",
                "displayed innovative thinking and implementation"
            ],
            'academic': [
                "shown exceptional academic performance",
                "demonstrated outstanding research capabilities",
                "exhibited excellent analytical thinking",
                "proven superior academic achievements",
                "displayed remarkable scholarly abilities"
            ],
            'professional': [
                "demonstrated exceptional leadership skills",
                "shown outstanding project management abilities",
                "exhibited excellent communication skills",
                "proven superior organizational capabilities",
                "displayed remarkable professional conduct"
            ]
        }
    
    def _build_appreciation_messages(self) -> List[str]:
        return [
            "We appreciate your dedication and commitment to learning.",
            "Your hard work and perseverance have been truly inspiring.",
            "We commend your exceptional effort and achievement.",
            "Your dedication to excellence has been remarkable.",
            "We congratulate you on this outstanding accomplishment."
        ]
    
    def _generate_achievement(self, course_type: str = 'technical') -> str:
        return random.choice(self.achievements.get(course_type, self.achievements['technical']))
    
    def _generate_appreciation(self) -> str:
        return random.choice(self.appreciation_messages)
    
    def generate_content(self, 
                        name: str, 
                        course: str, 
                        course_type: str = 'technical',
                        include_appreciation: bool = True) -> str:
        """
        Generate certificate content based on input parameters.
        
        Args:
            name: Recipient's name
            course: Course name
            course_type: Type of course (technical, academic, professional)
            include_appreciation: Whether to include appreciation message
            
        Returns:
            Generated certificate content
        """
        template = random.choice(self.templates)
        achievement = self._generate_achievement(course_type)
        
        content = template.format(
            name=name,
            achievement_verb=random.choice(self.vocabulary['achievement_verbs']),
            course=course,
            qualifier=random.choice(self.vocabulary['qualifiers'])
        )
        
        if include_appreciation:
            content += f"\n\n{self._generate_appreciation()}"
        
        return content
    
    def generate_multiple_options(self, 
                                name: str, 
                                course: str, 
                                course_type: str = 'technical',
                                num_options: int = 3) -> List[str]:
        """
        Generate multiple content options for the certificate.
        
        Args:
            name: Recipient's name
            course: Course name
            course_type: Type of course
            num_options: Number of options to generate
            
        Returns:
            List of generated content options
        """
        return [
            self.generate_content(name, course, course_type, include_appreciation=True)
            for _ in range(num_options)
        ]

# Appreciation messages and course types for training
appreciation_data = {
    "course_type": [
        "technical", "academic", "professional", "creative", "leadership",
        "entrepreneurship", "healthcare", "education", "science", "arts",
        "technical", "academic", "professional", "creative", "leadership",
        "entrepreneurship", "healthcare", "education", "science", "arts"
    ],
    "appreciation_message": [
        "Your technical expertise and dedication are truly impressive.",
        "Your academic achievements set a high standard for others.",
        "Your professionalism and work ethic are exemplary.",
        "Your creativity and innovation have made a remarkable impact.",
        "Your leadership skills have inspired those around you.",
        "Your entrepreneurial spirit is a driving force for success.",
        "Your compassion and commitment to healthcare are commendable.",
        "Your dedication to education is shaping a brighter future.",
        "Your scientific curiosity and rigor are outstanding.",
        "Your artistic talent and passion are truly inspiring.",
        "You have shown remarkable growth in technical skills.",
        "Your pursuit of academic excellence is admirable.",
        "You have set a new benchmark for professional conduct.",
        "Your creative vision has brought new ideas to life.",
        "You have led your peers with integrity and vision.",
        "Your innovative ideas are shaping the world of business.",
        "Your care for patients and colleagues is exceptional.",
        "You are making a difference in the field of education.",
        "Your scientific discoveries are paving the way for progress.",
        "Your art has touched the hearts of many."
    ]
}
df = pd.DataFrame(appreciation_data)
le = LabelEncoder()
X = le.fit_transform(df["course_type"]).reshape(-1, 1)
y = df["appreciation_message"]
clf = RandomForestClassifier()
clf.fit(X, y)

def predict_appreciation(course_type: str) -> str:
    try:
        x = le.transform([course_type]).reshape(-1, 1)
        return clf.predict(x)[0]
    except Exception:
        # fallback to random if unknown course_type
        return random.choice(df["appreciation_message"].tolist())

# FastAPI app setup
app = FastAPI(title="Certificate Content Generator")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
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

class AppreciationRequest(BaseModel):
    course_type: str

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

@app.post("/api/generate-appreciation")
async def generate_appreciation(request: AppreciationRequest):
    message = predict_appreciation(request.course_type)
    return {"appreciation_message": message}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 