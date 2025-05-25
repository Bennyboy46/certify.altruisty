import random
from typing import List, Dict, Tuple

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