from pydantic import BaseModel, Field
from typing import List, Optional
from bson.objectid import ObjectId
from enums import EvaluationArea, EvaluationStatus

class Evaluation(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    evaluation_area: EvaluationArea
    status: EvaluationStatus
    score: int = Field(..., ge=1, le=10, description="Evaluation score from 1 to 10")
    message: str = Field(..., description="Short diagnostic summary")
    suggestions: List[str] = Field(..., description="Actionable tips (1-3 recommendations)")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CompleteEvaluation(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    overall_score: float = Field(..., description="Average score across all areas")
    user_profile_score: int = Field(..., ge=1, le=10)
    experience_score: int = Field(..., ge=1, le=10)
    education_score: int = Field(..., ge=1, le=10)
    user_profile_message: str
    experience_message: str
    education_message: str
    overall_suggestions: List[str] = Field(..., description="Top priority recommendations")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 