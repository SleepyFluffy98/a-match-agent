from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class Skill(BaseModel):
    """Skill model"""
    name: str
    level: int  # 1-5 scale
    category: str
    description: Optional[str] = None
    
class Employee(BaseModel):
    """Employee profile model"""
    id: str
    name: str
    email: str
    current_position: str
    department: str
    skills: Dict[str, int]  # skill_name -> level
    career_goals: List[str]
    target_roles: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Position(BaseModel):
    """Position model"""
    id: str
    title: str
    department: str
    level: str
    required_skills: Dict[str, int]
    preferred_skills: Dict[str, int]
    description: Optional[str] = None
    is_open: bool = True
    location: Optional[str] = None
    posted_date: Optional[str] = None

class LearningResource(BaseModel):
    """Learning resource model"""
    id: str
    title: str
    type: str  # course, workshop, certification, etc.
    provider: str
    duration: str
    skills: List[str]
    level: str  # beginner, intermediate, advanced
    url: str
    description: str
    rating: Optional[float] = None
    price: Optional[str] = None
    is_internal: bool = True

class SkillGap(BaseModel):
    """Skill gap analysis result"""
    skill_name: str
    current_level: int
    required_level: int
    gap: int
    priority: str  # high, medium, low
    
class LearningPlan(BaseModel):
    """Personalized learning plan"""
    employee_id: str
    target_role: str
    skill_gaps: List[SkillGap]
    recommended_resources: List[LearningResource]
    estimated_duration: str
    created_at: datetime
    
class PositionMatch(BaseModel):
    """Position matching result"""
    position: Position
    match_score: float
    missing_skills: Dict[str, int]
    skill_gaps: List[SkillGap]
    recommendation: str
