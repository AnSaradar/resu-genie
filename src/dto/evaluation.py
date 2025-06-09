from pydantic import BaseModel, Field
from typing import List, Optional
from enums import EvaluationArea

class EvaluationResponse(BaseModel):
    """Response DTO for evaluation results"""
    evaluation_area: EvaluationArea
    score: int = Field(..., ge=1, le=10, description="Evaluation score from 1 to 10")
    message: str = Field(..., description="Short diagnostic summary")
    suggestions: List[str] = Field(..., description="Actionable tips")
    
    
class CompleteEvaluationResponse(BaseModel):
    """Complete evaluation response DTO"""
    overall_score: float = Field(..., description="Average score across all areas")
    user_profile_evaluation: EvaluationResponse
    experience_evaluation: EvaluationResponse  
    education_evaluation: EvaluationResponse
    overall_suggestions: List[str] = Field(..., description="Top priority recommendations") 