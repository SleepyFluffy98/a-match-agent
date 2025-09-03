from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .models import Employee, SkillGap, LearningResource, LearningPlan
from .data_manager import DataManager
from .skill_matcher import SkillMatcher
from .gpt_resource_generator import GPTResourceGenerator
from config import Config
import random

class LearningRecommender:
    """Generates personalized learning recommendations"""
    
    def __init__(self):
        self.config = Config()
        self.data_manager = DataManager()
        self.skill_matcher = SkillMatcher()
        self.gpt_generator = GPTResourceGenerator()
    
    def generate_learning_plan(self, employee: Employee, 
                             target_role: str,
                             include_external: bool = True,
                             max_resources: int = None) -> LearningPlan:
        """Generate a personalized learning plan for an employee"""
        
        if max_resources is None:
            max_resources = self.config.MAX_LEARNING_RESOURCES
        
        # Find target position
        target_position = None
        open_positions = self.data_manager.get_open_positions()
        current_positions = self.data_manager.get_current_positions()
        
        all_positions = open_positions + current_positions
        for position in all_positions:
            if position.title.lower() == target_role.lower() or position.id == target_role:
                target_position = position
                break
        
        if not target_position:
            # Create a generic learning plan based on skills mentioned in target_role
            skill_gaps = self._infer_skills_from_role_name(target_role, employee.skills)
        else:
            # Calculate skill gaps for the target position
            skill_gaps = self.skill_matcher.calculate_skill_gap(
                employee.skills, 
                target_position.required_skills
            )
        
        # Get learning resources for identified skill gaps using GPT
        if self.config.USE_GPT_RESOURCE_GENERATION:
            recommended_resources = self.gpt_generator.generate_learning_resources(
                skill_gaps, 
                max_resources=max_resources
            )
        else:
            # Fallback to basic resource generation
            recommended_resources = self._generate_basic_resources(skill_gaps, max_resources)
        
        # Estimate total duration
        estimated_duration = self._calculate_estimated_duration(recommended_resources)
        
        return LearningPlan(
            employee_id=employee.id,
            target_role=target_role,
            skill_gaps=skill_gaps,
            recommended_resources=recommended_resources,
            estimated_duration=estimated_duration,
            created_at=datetime.now()
        )
    
    def _infer_skills_from_role_name(self, role_name: str, 
                                   current_skills: Dict[str, int]) -> List[SkillGap]:
        """Infer required skills from role name when exact position not found"""
        role_lower = role_name.lower()
        inferred_gaps = []
        
        # Common role to skills mapping
        role_skill_mapping = {
            'data analyst': ['python', 'sql', 'data_analysis', 'statistics'],
            'software developer': ['python', 'javascript', 'sql', 'problem_solving'],
            'project manager': ['project_management', 'leadership', 'communication', 'agile'],
            'machine learning engineer': ['python', 'machine_learning', 'statistics', 'data_analysis'],
            'full stack developer': ['javascript', 'react', 'nodejs', 'sql'],
            'product manager': ['business_analysis', 'project_management', 'communication', 'agile'],
            'data scientist': ['python', 'machine_learning', 'statistics', 'data_analysis'],
            'frontend developer': ['javascript', 'react', 'web_development'],
            'backend developer': ['python', 'nodejs', 'sql', 'web_development']
        }
        
        # Find matching skills for the role
        required_skills = {}
        for role_key, skills in role_skill_mapping.items():
            if role_key in role_lower:
                for skill in skills:
                    required_skills[skill] = 3  # Default to intermediate level
                break
        
        # If no specific mapping found, extract keywords
        if not required_skills:
            skill_keywords = {
                'python': 3, 'javascript': 3, 'sql': 3, 'machine_learning': 4,
                'data_analysis': 3, 'project_management': 3, 'leadership': 3,
                'communication': 3, 'agile': 3, 'react': 3, 'nodejs': 3
            }
            
            for keyword, level in skill_keywords.items():
                if keyword in role_lower or keyword.replace('_', ' ') in role_lower:
                    required_skills[keyword] = level
        
        # Calculate gaps
        for skill, required_level in required_skills.items():
            current_level = current_skills.get(skill, 0)
            if current_level < required_level:
                gap = required_level - current_level
                priority = "high" if gap >= 3 else "medium" if gap >= 2 else "low"
                
                inferred_gaps.append(SkillGap(
                    skill_name=skill,
                    current_level=current_level,
                    required_level=required_level,
                    gap=gap,
                    priority=priority
                ))
        
        return sorted(inferred_gaps, key=lambda x: x.gap, reverse=True)
    
    def _generate_basic_resources(self, skill_gaps: List[SkillGap], max_resources: int = 10) -> List[LearningResource]:
        """Generate basic learning resources when GPT is not available"""
        resources = []
        
        resource_templates = {
            "python": {
                "title": "Python Programming Course",
                "provider": "Online Learning",
                "type": "course",
                "duration": "6-8 weeks",
                "description": "Comprehensive Python programming course"
            },
            "javascript": {
                "title": "JavaScript Fundamentals", 
                "provider": "Web Development Platform",
                "type": "course",
                "duration": "4-6 weeks",
                "description": "Learn JavaScript from basics to advanced"
            },
            "machine_learning": {
                "title": "Machine Learning Essentials",
                "provider": "Data Science Platform", 
                "type": "specialization",
                "duration": "3 months",
                "description": "Complete machine learning course"
            },
            "project_management": {
                "title": "Project Management Fundamentals",
                "provider": "Professional Development",
                "type": "certification",
                "duration": "8 weeks", 
                "description": "Learn project management best practices"
            }
        }
        
        for i, gap in enumerate(skill_gaps[:max_resources]):
            template = resource_templates.get(gap.skill_name, {
                "title": f"Learn {gap.skill_name.replace('_', ' ').title()}",
                "provider": "Online Platform",
                "type": "course", 
                "duration": "4-6 weeks",
                "description": f"Develop your {gap.skill_name.replace('_', ' ')} skills"
            })
            
            level = "beginner" if gap.current_level == 0 else "intermediate" if gap.current_level < 3 else "advanced"
            
            resources.append(LearningResource(
                id=f"basic_{i+1}",
                title=template["title"],
                type=template["type"],
                provider=template["provider"],
                duration=template["duration"],
                skills=[gap.skill_name],
                level=level,
                url=f"https://example.com/{gap.skill_name}",
                description=template["description"],
                rating=4.0,
                price="Variable",
                is_internal=False
            ))
        
        return resources
    
    def _calculate_estimated_duration(self, resources: List[LearningResource]) -> str:
        """Calculate estimated total duration for learning plan"""
        total_hours = 0
        
        for resource in resources:
            # Parse duration string and convert to hours
            duration_str = resource.duration.lower()
            hours = 0
            
            if 'hour' in duration_str:
                try:
                    hours = int(''.join(filter(str.isdigit, duration_str.split('hour')[0])))
                except ValueError:
                    hours = 10  # Default
            elif 'month' in duration_str:
                try:
                    months = int(''.join(filter(str.isdigit, duration_str.split('month')[0])))
                    hours = months * 40  # Assume 40 hours per month
                except ValueError:
                    hours = 40  # Default
            elif 'week' in duration_str:
                try:
                    weeks = int(''.join(filter(str.isdigit, duration_str.split('week')[0])))
                    hours = weeks * 10  # Assume 10 hours per week
                except ValueError:
                    hours = 20  # Default
            else:
                hours = 10  # Default fallback
            
            total_hours += hours
        
        # Convert to readable format
        if total_hours < 40:
            return f"{total_hours} hours"
        elif total_hours < 160:  # Less than 4 months
            weeks = total_hours // 10
            return f"{weeks} weeks"
        else:
            months = total_hours // 40
            return f"{months} months"
    
    def get_skill_recommendations(self, skill_name: str, 
                                current_level: int,
                                target_level: int) -> List[LearningResource]:
        """Get learning recommendations for a specific skill"""
        
        # Create a skill gap for this specific skill
        gap = SkillGap(
            skill_name=skill_name,
            current_level=current_level,
            required_level=target_level,
            gap=target_level - current_level,
            priority="high" if target_level - current_level >= 3 else "medium"
        )
        
        if self.config.USE_GPT_RESOURCE_GENERATION:
            return self.gpt_generator.generate_learning_resources([gap], max_resources=5)
        else:
            return self._generate_basic_resources([gap], max_resources=5)
    
    def get_trending_skills(self) -> List[Dict[str, any]]:
        """Get trending skills based on job requirements"""
        positions = self.data_manager.get_open_positions()
        skill_demand = {}
        
        # Count skill occurrences in job requirements
        for position in positions:
            for skill, level in position.required_skills.items():
                if skill not in skill_demand:
                    skill_demand[skill] = {"count": 0, "avg_level": 0, "total_level": 0}
                
                skill_demand[skill]["count"] += 1
                skill_demand[skill]["total_level"] += level
        
        # Calculate average levels and sort by demand
        trending = []
        for skill, data in skill_demand.items():
            if data["count"] > 0:
                avg_level = data["total_level"] / data["count"]
                trending.append({
                    "skill": skill,
                    "demand_count": data["count"],
                    "average_level": round(avg_level, 1),
                    "trend": "high" if data["count"] >= 3 else "medium" if data["count"] >= 2 else "low"
                })
        
        # Sort by demand count and average level
        trending.sort(key=lambda x: (x["demand_count"], x["average_level"]), reverse=True)
        
        return trending[:10]
    
    def get_career_path_suggestions(self, employee: Employee) -> List[Dict[str, any]]:
        """Suggest career paths based on current skills"""
        current_skills = employee.skills
        suggestions = []
        
        # Get all positions and calculate match scores
        all_positions = self.data_manager.get_open_positions() + self.data_manager.get_current_positions()
        
        for position in all_positions:
            match_score = self.skill_matcher.calculate_position_match_score(current_skills, position)
            
            if match_score >= 0.5:  # Lower threshold for career suggestions
                skill_gaps = self.skill_matcher.calculate_skill_gap(current_skills, position.required_skills)
                development_time = len(skill_gaps) * 2  # Rough estimate in months
                
                suggestions.append({
                    "position": position.title,
                    "department": position.department,
                    "match_score": round(match_score, 2),
                    "skill_gaps_count": len(skill_gaps),
                    "estimated_development": f"{development_time} months",
                    "difficulty": "easy" if match_score >= 0.8 else "medium" if match_score >= 0.6 else "hard"
                })
        
        # Sort by match score
        suggestions.sort(key=lambda x: x["match_score"], reverse=True)
        
        return suggestions[:5]
