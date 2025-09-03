"""
Backend modules for the Skill Matching Agent
"""

from .data_manager import DataManager
from .skill_matcher import SkillMatcher
from .learning_recommender import LearningRecommender
from .gpt_resource_generator import GPTResourceGenerator
from .models import Employee, Skill, Position, LearningResource

__all__ = [
    'DataManager',
    'SkillMatcher', 
    'LearningRecommender',
    'GPTResourceGenerator',
    'Employee',
    'Skill',
    'Position',
    'LearningResource'
]
