import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from backend import DataManager, Employee
from config import Config

class EmployeeInputForm:
    """Dedicated class for structured employee data input"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.config = Config()
        
    def render_structured_form(self, existing_employee: Optional[Employee] = None) -> Optional[Employee]:
        """Render the structured employee input form as per the specified layout"""
        
        # Custom CSS for the structured layout
        st.markdown("""
        <style>
            .input-section {
                background: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                padding: 1.5rem;
                margin: 1rem 0;
                height: 600px;
                overflow-y: auto;
            }
            .section-title {
                background: #1e3c72;
                color: white;
                padding: 0.8rem;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 1.1rem;
                margin-bottom: 1rem;
            }
            .form-group {
                margin: 1rem 0;
                padding: 0.5rem;
                background: white;
                border-radius: 5px;
                border-left: 3px solid #1e3c72;
            }
            .skill-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.3rem;
                border-bottom: 1px solid #eee;
            }
            .header-box {
                background: linear-gradient(135deg, #1e3c72, #2a5298);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize default data
        default_data = self._get_default_data(existing_employee)
        
        # Section 1: CURRENT SKILLS
        st.markdown("### 🛠️ Current Skills")
        st.write("")  # Add some spacing
        skills_data = self._render_skills_section(default_data)
        
        st.markdown("---")  # Visual separator
        
        # Section 2: CURRENT POSITION
        st.markdown("### 💼 Current Position")
        st.write("")  # Add some spacing
        position_data = self._render_position_section(default_data)
        
        st.markdown("---")  # Visual separator
        
        # Section 3: CAREER GOALS
        st.markdown("### 🎯 Career Goals")
        st.write("")  # Add some spacing
        goals_data = self._render_career_goals_section(default_data)
        
        # Form submission section (moved to bottom, more compact)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Progress indicator (more compact)
        progress = self._calculate_form_progress(skills_data, position_data, goals_data)
        
        # Single row for progress and buttons
        prog_col, btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1, 1])
        
        with prog_col:
            st.progress(progress, text=f"Form Completion: {int(progress * 100)}%")
        
        with btn_col1:
            preview_btn = st.button("👀 Preview", use_container_width=True)
        
        with btn_col2:
            save_btn = st.button("💾 Save Profile", type="primary", use_container_width=True)
        
        with btn_col3:
            if existing_employee:
                clear_btn = st.button("🗑️ Clear", use_container_width=True)
                if clear_btn:
                    st.rerun()
        
        # Handle form submission
        if preview_btn:
            return self._show_preview(skills_data, position_data, goals_data)
        
        if save_btn:
            return self._save_employee_data(skills_data, position_data, goals_data, existing_employee)
        
        return None
    
    def _get_default_data(self, existing_employee: Optional[Employee]) -> Dict:
        """Get default data for form fields"""
        if existing_employee:
            return {
                'name': existing_employee.name,
                'email': existing_employee.email,
                'current_position': existing_employee.current_position,
                'department': existing_employee.department,
                'skills': existing_employee.skills,
                'career_goals': existing_employee.career_goals,
                'target_roles': existing_employee.target_roles,
                'id': existing_employee.id,
                'created_at': existing_employee.created_at
            }
        else:
            return {
                'name': '', 'email': '', 'current_position': '', 'department': '',
                'skills': {}, 'career_goals': [], 'target_roles': [],
                'id': None, 'created_at': None
            }
    
    def _render_skills_section(self, default_data: Dict) -> Dict:
        """Render the Current Skills section with improved table-based interface"""
        
        skills_data = {}
        selected_skills = default_data.get('skills', {})
        
        # Method selection
        input_method = st.radio(
            "Choose how to add your skills:",
            options=["📋 Table Input", "📄 Copy & Paste"],
            key="skill_input_method",
            horizontal=True
        )
        
        # Get all available skills for search
        all_skills = self.data_manager.get_all_skills()
        skill_names = [skill['name'] for skill in all_skills]
        
        if input_method == "📋 Table Input":
            st.markdown("💡 *Start typing in the Skill Name field to search and select from available skills*")
            
            # Initialize session state for dynamic rows
            if 'skill_rows' not in st.session_state:
                # Start with existing skills or 3 empty rows
                if selected_skills:
                    st.session_state.skill_rows = len(selected_skills) + 2
                else:
                    st.session_state.skill_rows = 3
            
            # Table headers (closer to rows)
            col_header1, col_header2, col_header3 = st.columns([3, 2, 1])
            with col_header1:
                st.markdown("**Skill Name**")
            with col_header2:
                st.markdown("**Level**")
            with col_header3:
                st.markdown("**Remove**")
            # Track filled skills
            current_skills = {}
            
            # Create dynamic rows
            for i in range(st.session_state.skill_rows):
                col_skill, col_level, col_remove = st.columns([3, 2, 1])
                
                with col_skill:
                    # Get existing skill for this row
                    existing_skill_items = list(selected_skills.items())
                    default_skill = ""
                    if i < len(existing_skill_items):
                        skill_id, level = existing_skill_items[i]
                        # Find skill name from ID
                        for skill in all_skills:
                            if skill['id'] == skill_id:
                                default_skill = skill['name']
                                break
                        if not default_skill:  # Fallback if not found in database
                            default_skill = skill_id.replace('_', ' ').title()
                    
                    # Skill name input with search
                    skill_name = st.selectbox(
                        f"Skill {i+1}",
                        options=[""] + skill_names,
                        index=0 if not default_skill else (skill_names.index(default_skill) + 1 if default_skill in skill_names else 0),
                        key=f"skill_name_{i}",
                        label_visibility="collapsed"
                    )
                
                with col_level:
                    if skill_name:  # Only show level selector if skill is selected
                        # Get default level
                        default_level = 3
                        if i < len(existing_skill_items) and default_skill:
                            _, default_level = existing_skill_items[i]
                        
                        level = st.selectbox(
                            f"Level {i+1}",
                            options=list(range(1, 6)),
                            index=default_level - 1,
                            format_func=lambda x: f"{x} - {self.config.get_skill_level_name(x)}",
                            key=f"skill_level_{i}",
                            label_visibility="collapsed"
                        )
                        
                        # Store the skill
                        if skill_name:
                            # Find skill ID
                            skill_id = None
                            for skill in all_skills:
                                if skill['name'] == skill_name:
                                    skill_id = skill['id']
                                    break
                            
                            # If not found in database, create normalized ID
                            if not skill_id:
                                skill_id = skill_name.lower().replace(' ', '_').replace('-', '_')
                            
                            current_skills[skill_id] = level
                    else:
                        st.write("")  # Empty placeholder
                
                with col_remove:
                    if skill_name:  # Only show remove button if skill is selected
                        if st.button("🗑️", key=f"remove_skill_{i}", help="Remove this skill"):
                            # Clear this specific row by removing from session state temporarily
                            # Force rerun to refresh the interface
                            if f"skill_name_{i}" in st.session_state:
                                del st.session_state[f"skill_name_{i}"]
                            if f"skill_level_{i}" in st.session_state:
                                del st.session_state[f"skill_level_{i}"]
                            st.rerun()
            
            # Button row (closer together)
            st.write("")  # Small spacing
            col_add, col_remove_empty, col_spacer = st.columns([2, 2, 5])
            with col_add:
                if st.button("➕ Add More Skills"):
                    st.session_state.skill_rows += 3
                    st.rerun()
            
            with col_remove_empty:
                if st.button("🗑️ Remove Empty Rows") and st.session_state.skill_rows > 3:
                    st.session_state.skill_rows = max(3, len(current_skills) + 2)
                    st.rerun()
            
            # Update selected skills
            selected_skills.update(current_skills)
        
        else:  # Copy & Paste method
            st.markdown("**📄 Paste Your Skills**")
            st.info("💡 **Format:** Paste a table with Skill Name and Level (1-5)")
            st.markdown("**Example:**")
            st.code("""Python          4
Data Analysis   3
Project Management   5
Communication   4""")
            
            skills_text = st.text_area(
                "Paste your skills here:",
                placeholder="Python          4\nData Analysis   3\nProject Management   5",
                height=150,
                key="skills_paste_area"
            )
            
            if skills_text.strip():
                parsed_skills = {}
                lines = skills_text.strip().split('\n')
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Try different separators
                    parts = None
                    for sep in ['\t', '    ', '   ', '  ', ' ']:
                        if sep in line:
                            parts = [p.strip() for p in line.split(sep) if p.strip()]
                            break
                    
                    if parts and len(parts) >= 2:
                        skill_name = parts[0]
                        try:
                            level = int(parts[-1])  # Take the last part as level
                            if 1 <= level <= 5:
                                # Create a normalized skill ID
                                skill_id = skill_name.lower().replace(' ', '_').replace('-', '_')
                                parsed_skills[skill_id] = level
                            else:
                                st.warning(f"Line {i+1}: Level should be 1-5, got {level}")
                        except ValueError:
                            st.warning(f"Line {i+1}: Could not parse level from '{line}'")
                    else:
                        st.warning(f"Line {i+1}: Could not parse '{line}'. Use format: Skill Name [separator] Level")
                
                if parsed_skills:
                    st.success(f"✅ Parsed {len(parsed_skills)} skills:")
                    for skill_id, level in parsed_skills.items():
                        st.write(f"• **{skill_id.replace('_', ' ').title()}**: Level {level} ({self.config.get_skill_level_name(level)})")
                    # Update selected skills
                    selected_skills.update(parsed_skills)
        
        # Remove empty skills
        selected_skills = {k: v for k, v in selected_skills.items() if k}
        
        # Display skill summary
        if selected_skills:
            st.markdown("---")
            st.markdown("**📋 Skills Summary:**")
            summary_text = ", ".join([
                f"{skill_id.replace('_', ' ').title()} (Level {level})" 
                for skill_id, level in selected_skills.items()
            ])
            st.info(summary_text)
        
        # Certifications section (removed years of experience)
        st.markdown("---")
        st.markdown("**• Certifications (Optional)**")
        certifications = st.text_area(
            "List your professional certifications:",
            value='\n'.join(default_data.get('certifications', [])),
            placeholder="AWS Certified Solutions Architect\nPMP Certification\nScrum Master",
            height=80,
            key="certifications"
        )
        
        return {
            'skills': selected_skills,
            'certifications': [cert.strip() for cert in certifications.split('\n') if cert.strip()]
        }
    
    def _render_position_section(self, default_data: Dict) -> Dict:
        """Render the Current Position section - simplified version"""
        
        # Job details
        st.markdown("**• Job Title**")
        job_title = st.text_input(
            "Current Job Title *",
            value=default_data['current_position'],
            placeholder="Senior Software Developer",
            key="job_title"
        )
        
        st.markdown("**• Experience**")
        years_experience = st.selectbox(
            "Years of Experience *",
            options=["< 1 year", "1-2 years", "3-5 years", "6-10 years", "10+ years"],
            index=2,
            key="position_years_experience"
        )
        
        return {
            'current_position': job_title,
            'years_experience': years_experience
        }
    
    def _render_career_goals_section(self, default_data: Dict) -> Dict:
        """Render the Career Goals section"""
        
        # Target roles
        st.markdown("**• Target Role**")
        all_positions = self.data_manager.get_open_positions() + self.data_manager.get_current_positions()
        position_titles = [""] + sorted(list(set([pos.title for pos in all_positions]))) + ["Other (specify below)"]
        
        primary_target = st.selectbox(
            "Primary Target Role",
            options=position_titles,
            index=0,
            key="primary_target_role"
        )
        
        if primary_target == "Other (specify below)":
            primary_target = st.text_input(
                "Specify target role:",
                key="primary_target_custom"
            )
        
        secondary_target = st.selectbox(
            "Secondary Target Role (Optional)",
            options=position_titles,
            index=0,
            key="secondary_target_role"
        )
        
        if secondary_target == "Other (specify below)":
            secondary_target = st.text_input(
                "Specify secondary target role:",
                key="secondary_target_custom"
            )
        
        # Timeline
        st.markdown("**• Timeline**")
        timeline = st.selectbox(
            "When do you want to transition?",
            options=[
                "3-6 months",
                "6-12 months", 
                "1-2 years",
                "2-3 years",
                "3+ years",
                "Flexible"
            ],
            index=1,
            key="career_timeline"
        )
        
        # Priorities  
        st.markdown("**• Priorities**")
        priorities = st.multiselect(
            "What matters most to you?",
            options=[
                "💰 Higher compensation",
                "👑 Leadership responsibilities",
                "🚀 Technical challenges", 
                "⚖️ Work-life balance",
                "🏠 Remote work flexibility",
                "📚 Learning opportunities",
                "🏭 Industry change",
                "🏢 Company size change",
                "🌍 Global opportunities",
                "💡 Innovation projects"
            ],
            default=["🚀 Technical challenges", "📚 Learning opportunities"],
            key="career_priorities"
        )
        
        # Preferences
        st.markdown("**• Preferences**")
        learning_preferences = st.multiselect(
            "Preferred learning methods:",
            options=[
                "📖 Online courses",
                "🏫 Internal training",
                "🛠️ Hands-on workshops",
                "👥 Mentoring programs",
                "🏆 Professional certifications",
                "🎤 Conference attendance",
                "🔧 Side projects"
            ],
            default=["📖 Online courses", "🏫 Internal training"],
            key="learning_preferences"
        )
        
        # Additional goals
        additional_goals = st.text_area(
            "Additional career aspirations:",
            placeholder="Any specific goals, departments/areas you'd like to work for, or skills you want to develop...",
            height=80,
            key="additional_career_goals"
        )
        
        target_roles = [role for role in [primary_target, secondary_target] if role]
        
        return {
            'target_roles': target_roles,
            'timeline': timeline,
            'priorities': priorities,
            'learning_preferences': learning_preferences,
            'additional_goals': additional_goals
        }
    
    def _calculate_form_progress(self, skills_data: Dict, position_data: Dict, goals_data: Dict) -> float:
        """Calculate form completion progress"""
        total_fields = 0
        completed_fields = 0
        
        # Required position field check
        total_fields += 1
        if position_data.get('current_position'):
            completed_fields += 1
        
        # Skills check
        total_fields += 1
        if skills_data.get('skills'):
            completed_fields += 1
        
        # Goals check  
        total_fields += 1
        if goals_data.get('target_roles'):
            completed_fields += 1
        
        return completed_fields / total_fields if total_fields > 0 else 0
    
    def _show_preview(self, skills_data: Dict, position_data: Dict, goals_data: Dict) -> None:
        """Show preview of entered data"""
        
        st.markdown("### 👀 Profile Preview")
        
        preview_col1, preview_col2, preview_col3 = st.columns(3)
        
        with preview_col1:
            st.markdown("**🛠️ Skills Summary**")
            if skills_data['skills']:
                for skill, level in list(skills_data['skills'].items())[:5]:
                    st.write(f"• {skill.replace('_', ' ').title()}: Level {level}")
                if len(skills_data['skills']) > 5:
                    st.write(f"... and {len(skills_data['skills']) - 5} more")
            else:
                st.write("No skills added yet")
        
        with preview_col2:
            st.markdown("**💼 Position Info**")
            st.write(f"• Role: {position_data.get('current_position', 'Not provided')}")
            st.write(f"• Experience: {position_data.get('years_experience', 'Not provided')}")
        
        with preview_col3:
            st.markdown("**🎯 Career Goals**")
            targets = goals_data.get('target_roles', [])
            if targets:
                for i, target in enumerate(targets, 1):
                    st.write(f"• Target {i}: {target}")
            st.write(f"• Timeline: {goals_data.get('timeline', 'Not specified')}")
            priorities = goals_data.get('priorities', [])
            if priorities:
                st.write(f"• Top Priority: {priorities[0]}")
    
    def _save_employee_data(self, skills_data: Dict, position_data: Dict, 
                          goals_data: Dict, existing_employee: Optional[Employee]) -> Optional[Employee]:
        """Save employee data to storage"""
        
        # Validate required fields
        if not position_data.get('current_position'):
            st.error("❌ Please fill in your current job title")
            return None
        
        if not skills_data.get('skills'):
            st.error("❌ Please add at least one skill")
            return None
        
        # Create career goals list
        career_goals = []
        career_goals.extend(goals_data.get('priorities', []))
        if goals_data.get('additional_goals'):
            career_goals.append(goals_data['additional_goals'])
        
        # Create employee object
        employee_id = existing_employee.id if existing_employee else str(uuid.uuid4())
        
        # Generate a simple email if none exists
        name = f"User_{employee_id[:8]}"
        email = f"user_{employee_id[:8]}@example.com"
        
        employee = Employee(
            id=employee_id,
            name=name,
            email=email,
            current_position=position_data['current_position'],
            department="General",  # Default department
            skills=skills_data['skills'],
            career_goals=career_goals,
            target_roles=goals_data.get('target_roles', []),
            created_at=existing_employee.created_at if existing_employee else datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save employee
        if self.data_manager.save_employee(employee):
            st.success(f"✅ Profile {'updated' if existing_employee else 'created'} successfully!")
            
            # Success metrics
            success_col1, success_col2, success_col3 = st.columns(3)
            
            with success_col1:
                st.metric("Skills Added", len(skills_data['skills']))
            
            with success_col2:
                st.metric("Target Roles", len(goals_data.get('target_roles', [])))
                
            with success_col3:
                st.metric("Experience", position_data.get('years_experience', 'Not specified'))
            
            st.balloons()
            return employee
        else:
            st.error("❌ Error saving profile. Please try again.")
            return None
