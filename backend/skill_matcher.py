import numpy as np
from typing import Dict, List, Tuple, Optional
from .models import Employee, Position, SkillGap, PositionMatch
from .data_manager import DataManager
from config import Config

class SkillMatcher:
    """Handles skill matching and gap analysis"""
    
    def __init__(self):
        self.config = Config()
        self.data_manager = DataManager()
    
    def calculate_skill_gap(self, current_skills: Dict[str, int], 
                          required_skills: Dict[str, int]) -> List[SkillGap]:
        """Calculate skill gaps between current and required skills"""
        gaps = []
        
        for skill, required_level in required_skills.items():
            current_level = current_skills.get(skill, 0)
            gap = required_level - current_level
            
            if gap > 0:
                # Determine priority based on gap size
                if gap >= 3:
                    priority = "high"
                elif gap >= 2:
                    priority = "medium"
                else:
                    priority = "low"
                
                gaps.append(SkillGap(
                    skill_name=skill,
                    current_level=current_level,
                    required_level=required_level,
                    gap=gap,
                    priority=priority
                ))
        
        # Sort by gap size (descending) and then by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        gaps.sort(key=lambda x: (x.gap, priority_order[x.priority]), reverse=True)
        
        return gaps
    
    def calculate_position_match_score(self, employee_skills: Dict[str, int],
                                     position: Position) -> float:
        """Calculate match score between employee skills and position requirements"""
        if not position.required_skills:
            return 0.0
        
        total_score = 0
        max_possible_score = 0
        
        # Calculate score for required skills
        for skill, required_level in position.required_skills.items():
            current_level = employee_skills.get(skill, 0)
            max_possible_score += required_level
            
            if current_level >= required_level:
                # Full points if requirement is met
                total_score += required_level
            else:
                # Partial points based on current level
                total_score += current_level
        
        # Bonus points for preferred skills
        bonus_score = 0
        max_bonus = 0
        
        for skill, preferred_level in position.preferred_skills.items():
            current_level = employee_skills.get(skill, 0)
            max_bonus += preferred_level * 0.5  # Preferred skills worth 50% of required
            
            if current_level >= preferred_level:
                bonus_score += preferred_level * 0.5
            else:
                bonus_score += current_level * 0.5
        
        # Calculate final score (0-1 scale)
        if max_possible_score > 0:
            base_score = total_score / max_possible_score
            if max_bonus > 0:
                bonus_ratio = bonus_score / max_bonus
                final_score = base_score + (bonus_ratio * 0.2)  # Bonus can add up to 20%
                return min(final_score, 1.0)
            return base_score
        
        return 0.0
    
    def find_position_matches(self, employee: Employee, 
                            include_current: bool = False) -> List[PositionMatch]:
        """Find matching positions for an employee"""
        matches = []
        
        # Get open positions
        open_positions = self.data_manager.get_open_positions()
        positions_to_check = open_positions
        
        # Optionally include current positions for career progression
        if include_current:
            current_positions = self.data_manager.get_current_positions()
            positions_to_check.extend(current_positions)
        
        for position in positions_to_check:
            match_score = self.calculate_position_match_score(employee.skills, position)
            
            if match_score >= self.config.SKILL_MATCH_THRESHOLD:
                # Calculate skill gaps
                skill_gaps = self.calculate_skill_gap(employee.skills, position.required_skills)
                
                # Identify completely missing skills
                missing_skills = {}
                for skill, level in position.required_skills.items():
                    if skill not in employee.skills:
                        missing_skills[skill] = level
                
                # Generate recommendation
                recommendation = self._generate_position_recommendation(match_score, skill_gaps, missing_skills)
                
                matches.append(PositionMatch(
                    position=position,
                    match_score=match_score,
                    missing_skills=missing_skills,
                    skill_gaps=skill_gaps,
                    recommendation=recommendation
                ))
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        return matches[:self.config.RECOMMENDATION_COUNT]
    
    def _generate_position_recommendation(self, match_score: float,
                                        skill_gaps: List[SkillGap],
                                        missing_skills: Dict[str, int]) -> str:
        """Generate a recommendation text for position match"""
        if match_score >= 0.9:
            recommendation = "Excellent match! You meet most requirements."
        elif match_score >= 0.8:
            recommendation = "Very good match with minor skill gaps."
        elif match_score >= 0.7:
            recommendation = "Good match. Some skill development needed."
        else:
            recommendation = "Partial match. Significant upskilling required."
        
        if skill_gaps:
            high_priority_gaps = [gap for gap in skill_gaps if gap.priority == "high"]
            if high_priority_gaps:
                recommendation += f" Focus on developing: {', '.join([gap.skill_name for gap in high_priority_gaps[:3]])}."
        
        if missing_skills:
            missing_count = len(missing_skills)
            if missing_count <= 2:
                recommendation += f" Consider learning: {', '.join(missing_skills.keys())}."
            else:
                recommendation += f" {missing_count} new skills needed for this role."
        
        return recommendation
    
    def analyze_career_progression(self, employee: Employee, 
                                 target_position_id: str) -> Optional[Dict]:
        """Analyze career progression path to target position"""
        target_position = self.data_manager.get_position_by_id(target_position_id)
        if not target_position:
            return None
        
        # Calculate current match score
        current_match = self.calculate_position_match_score(employee.skills, target_position)
        
        # Calculate skill gaps
        skill_gaps = self.calculate_skill_gap(employee.skills, target_position.required_skills)
        
        # Estimate development time based on gaps
        total_months = 0
        for gap in skill_gaps:
            # Rough estimation: 1-2 months per skill level gap
            total_months += gap.gap * 1.5
        
        # Generate progression recommendations
        recommendations = []
        if skill_gaps:
            high_priority = [gap for gap in skill_gaps if gap.priority == "high"]
            medium_priority = [gap for gap in skill_gaps if gap.priority == "medium"]
            
            if high_priority:
                recommendations.append(f"Immediately focus on: {', '.join([gap.skill_name for gap in high_priority[:3]])}")
            if medium_priority:
                recommendations.append(f"Next, develop: {', '.join([gap.skill_name for gap in medium_priority[:3]])}")
        
        return {
            "target_position": target_position,
            "current_match_score": current_match,
            "skill_gaps": skill_gaps,
            "estimated_development_time": f"{int(total_months)} months",
            "recommendations": recommendations,
            "next_steps": self._get_next_steps(skill_gaps[:3])
        }
    
    def _get_next_steps(self, priority_gaps: List[SkillGap]) -> List[str]:
        """Generate actionable next steps based on skill gaps"""
        steps = []
        
        for gap in priority_gaps:
            if gap.current_level == 0:
                steps.append(f"Start learning {gap.skill_name} basics")
            else:
                steps.append(f"Advance {gap.skill_name} from level {gap.current_level} to {gap.required_level}")
        
        return steps
    
    def get_skill_similarity_matrix(self) -> Dict[str, List[str]]:
        """Get skill similarity based on taxonomy relationships"""
        taxonomy = self.data_manager.load_skills_taxonomy()
        similarity_map = {}
        
        for category_name, category_data in taxonomy.get('skill_categories', {}).items():
            for skill_id, skill_data in category_data.get('skills', {}).items():
                related = skill_data.get('related_skills', [])
                similarity_map[skill_id] = related
        
        return similarity_map
