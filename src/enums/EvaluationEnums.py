# Add evaluation area enum
from enum import Enum

class EvaluationArea(str, Enum):
    USER_PROFILE = "user_profile"
    EXPERIENCE = "experience" 
    EDUCATION = "education"
    COMPLETE = "complete"
