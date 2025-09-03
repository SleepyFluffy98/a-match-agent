import pandas as pd
import json
import os
from typing import Dict, List, Any
from config import Config

class ExcelDataProcessor:
    """Process Excel files from raw-data folder and convert to JSON"""
    
    def __init__(self):
        self.config = Config()
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.config.DATA_DIR):
            os.makedirs(self.config.DATA_DIR)
    
    def process_all_data(self):
        """Process all Excel files and generate JSON data"""
        try:
            print("Processing raw data files...")
            
            # Process skill taxonomy
            if os.path.exists(self.config.SKILL_TAXONOMY_RAW):
                self.process_skill_taxonomy()
                print("✅ Skill taxonomy processed")
            else:
                print("❌ Skill taxonomy file not found")
            
            # Process position requirements  
            if os.path.exists(self.config.POSITION_REQUIREMENTS_RAW):
                self.process_position_requirements()
                print("✅ Position requirements processed")
            else:
                print("❌ Position requirements file not found")
            
            # Process job output
            if os.path.exists(self.config.JOB_OUTPUT_RAW):
                self.process_job_output()
                print("✅ Job output processed")
            else:
                print("❌ Job output file not found")
                
            print("Data processing completed!")
            
        except Exception as e:
            print(f"Error processing data: {e}")
    
    def process_skill_taxonomy(self):
        """Process skill taxonomy Excel file"""
        try:
            df = pd.read_excel(self.config.SKILL_TAXONOMY_RAW)
            
            # Analyze the structure - based on the output we saw
            print(f"Skill taxonomy columns: {df.columns.tolist()}")
            print(f"Shape: {df.shape}")
            
            # Create skill taxonomy structure
            skill_categories = {
                "technical": {"name": "Technical Skills", "skills": {}},
                "business": {"name": "Business Skills", "skills": {}},
                "soft_skills": {"name": "Soft Skills", "skills": {}}
            }
            
            # Process each row in the Excel file
            for _, row in df.iterrows():
                try:
                    # Extract information from known columns
                    skill_name = str(row['Skill Name']).strip() if pd.notna(row['Skill Name']) else None
                    category = str(row['Category 1']).strip().lower() if pd.notna(row['Category 1']) else 'technical'
                    description = str(row['Skill Description']).strip() if pd.notna(row['Skill Description']) else ""
                    
                    # Skip if no skill name or it's 'not available'
                    if not skill_name or skill_name.lower() in ['not available', 'nan']:
                        continue
                    
                    # Map categories
                    if 'business' in category or 'management' in category or 'leadership' in category:
                        skill_category = "business"
                    elif 'soft' in category or 'interpersonal' in category or 'communication' in category:
                        skill_category = "soft_skills"  
                    else:
                        skill_category = "technical"
                    
                    # Create skill ID
                    skill_id = skill_name.lower().replace(' ', '_').replace('-', '_').replace('.', '_')
                    skill_id = ''.join(c for c in skill_id if c.isalnum() or c == '_')
                    
                    if skill_id and len(skill_id) > 1:
                        # Avoid description with 'not available'
                        if description.lower() == 'not available':
                            description = f"{skill_name} proficiency and expertise"
                        
                        skill_categories[skill_category]["skills"][skill_id] = {
                            "name": skill_name,
                            "description": description,
                            "related_skills": []
                        }
                        
                except Exception as e:
                    print(f"Error processing skill row: {e}")
                    continue
            
            # Save to JSON
            output_data = {"skill_categories": skill_categories}
            with open(self.config.SKILLS_TAXONOMY_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
            print(f"Processed {sum(len(cat['skills']) for cat in skill_categories.values())} skills")
                
        except Exception as e:
            print(f"Error processing skill taxonomy: {e}")
            # Create default taxonomy if processing fails
            self._create_default_skill_taxonomy()
    
    def process_position_requirements(self):
        """Process position requirements Excel file"""
        try:
            df = pd.read_excel(self.config.POSITION_REQUIREMENTS_RAW)
            
            print(f"Position requirements columns: {df.columns.tolist()}")
            print(f"Shape: {df.shape}")
            
            current_positions = []
            open_positions = []
            
            # Group by position to aggregate skills
            position_groups = df.groupby(['Filter a TALENT SEGMENT', 'Filter a TALENT POSITION'])
            
            position_id = 1
            for (segment, position_title), group in position_groups:
                try:
                    if pd.isna(position_title) or position_title.strip() == '':
                        continue
                        
                    # Create position data
                    position_data = {
                        "id": f"pos_{position_id:03d}",
                        "title": str(position_title).strip(),
                        "department": str(segment).strip() if pd.notna(segment) else "General",
                        "level": "Mid",  # Default level
                        "required_skills": {},
                        "preferred_skills": {},
                        "description": f"{position_title} position in {segment}",
                        "location": "Remote",
                        "posted_date": "2024-01-15"
                    }
                    
                    # Process skills for this position
                    for _, skill_row in group.iterrows():
                        skill_name = str(skill_row['Skill']).strip() if pd.notna(skill_row['Skill']) else None
                        if not skill_name:
                            continue
                        
                        # Convert skill name to ID format
                        skill_id = skill_name.lower().replace(' ', '_').replace('-', '_')
                        skill_id = ''.join(c for c in skill_id if c.isalnum() or c == '_')
                        
                        # Get skill levels from different columns
                        entry_level = skill_row.get('Entry', None)
                        senior_level = skill_row.get('Senior', None)
                        expert_level = skill_row.get('Expert', None)
                        manager_level = skill_row.get('Managing Expert\n (for managers)', None)
                        
                        # Determine the appropriate skill level to use
                        skill_level = None
                        if pd.notna(senior_level):
                            skill_level = int(float(senior_level))
                        elif pd.notna(entry_level):
                            skill_level = int(float(entry_level))
                        elif pd.notna(expert_level):
                            skill_level = int(float(expert_level))
                        elif pd.notna(manager_level):
                            skill_level = int(float(manager_level))
                        
                        if skill_level and skill_level > 0:
                            # Skills with level 3+ are required, others are preferred
                            if skill_level >= 3:
                                position_data["required_skills"][skill_id] = min(skill_level, 5)
                            else:
                                position_data["preferred_skills"][skill_id] = min(skill_level, 5)
                    
                    # Only add position if it has some skills
                    if position_data["required_skills"] or position_data["preferred_skills"]:
                        open_positions.append(position_data)
                        position_id += 1
                        
                except Exception as e:
                    print(f"Error processing position group: {e}")
                    continue
            
            # Save to JSON
            output_data = {
                "current_positions": current_positions,
                "open_positions": open_positions
            }
            
            with open(self.config.POSITIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
            print(f"Processed {len(open_positions)} positions")
                
        except Exception as e:
            print(f"Error processing position requirements: {e}")
            # Create default positions if processing fails
            self._create_default_positions()
    
    def process_job_output(self):
        """Process job output Excel file"""
        try:
            df = pd.read_excel(self.config.JOB_OUTPUT_RAW)
            
            print(f"Job output columns: {df.columns.tolist()}")
            print(f"Shape: {df.shape}")
            
            # Process job postings as additional open positions
            additional_positions = []
            
            for idx, row in df.iterrows():
                try:
                    title = str(row['Title']).strip() if pd.notna(row['Title']) else None
                    if not title:
                        continue
                    
                    # Extract basic info
                    position_data = {
                        "id": f"job_{idx+1:03d}",
                        "title": title,
                        "department": str(row['Area of Expertise']).strip() if pd.notna(row['Area of Expertise']) else "General",
                        "level": str(row['Job Level']).strip() if pd.notna(row['Job Level']) else "Mid",
                        "location": str(row['Location']).strip() if pd.notna(row['Location']) else "Remote",
                        "posted_date": "2024-01-15",
                        "required_skills": {},
                        "preferred_skills": {},
                        "description": str(row.get('Requirements', '')).strip()[:200] if pd.notna(row.get('Requirements')) else title
                    }
                    
                    # Parse skills from the 'Matched_Skills_With_Level_Cleaned' column
                    skills_text = str(row['Matched_Skills_With_Level_Cleaned']) if pd.notna(row['Matched_Skills_With_Level_Cleaned']) else ""
                    
                    if skills_text and skills_text.lower() != 'nan':
                        # Parse skills - format appears to be "Skill (Level), Skill (Level), ..."
                        import re
                        skill_matches = re.findall(r'([^(]+)\s*\(([^)]+)\)', skills_text)
                        
                        for skill_name, level_text in skill_matches:
                            skill_name = skill_name.strip()
                            if not skill_name:
                                continue
                            
                            # Convert skill name to ID
                            skill_id = skill_name.lower().replace(' ', '_').replace('-', '_')
                            skill_id = ''.join(c for c in skill_id if c.isalnum() or c == '_')
                            
                            # Parse level - map text levels to numbers
                            skill_level = 3  # default
                            level_text = level_text.lower().strip()
                            
                            if 'proficient' in level_text or 'p4' in level_text:
                                skill_level = 4
                            elif 'competent' in level_text or 'p3' in level_text:
                                skill_level = 3
                            elif 'novice' in level_text or 'p1' in level_text:
                                skill_level = 2
                            elif 'beginner' in level_text:
                                skill_level = 1
                            elif 'expert' in level_text or 'p5' in level_text:
                                skill_level = 5
                            
                            # Add to required skills if level >= 3, preferred otherwise
                            if skill_level >= 3:
                                position_data["required_skills"][skill_id] = skill_level
                            else:
                                position_data["preferred_skills"][skill_id] = skill_level
                    
                    # Only add if has some skills
                    if position_data["required_skills"] or position_data["preferred_skills"]:
                        additional_positions.append(position_data)
                        
                except Exception as e:
                    print(f"Error processing job row {idx}: {e}")
                    continue
            
            # Merge with existing positions file
            if additional_positions:
                try:
                    # Load existing data or create new
                    if os.path.exists(self.config.POSITIONS_FILE):
                        with open(self.config.POSITIONS_FILE, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    else:
                        existing_data = {"current_positions": [], "open_positions": []}
                    
                    # Add job postings to open positions
                    existing_data["open_positions"].extend(additional_positions)
                    
                    with open(self.config.POSITIONS_FILE, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, indent=2, ensure_ascii=False)
                        
                    print(f"Added {len(additional_positions)} job postings")
                        
                except Exception as e:
                    print(f"Error merging job output data: {e}")
                    
        except Exception as e:
            print(f"Error processing job output: {e}")
    
    def _extract_position_from_row(self, row: pd.Series, columns: List[str], is_job_output: bool = False) -> Dict[str, Any]:
        """Extract position information from a row"""
        position_data = {
            "id": f"pos_{hash(str(row.values)) % 10000:04d}",
            "title": "",
            "department": "General",
            "level": "Mid",
            "required_skills": {},
            "preferred_skills": {},
            "description": "",
            "location": "Remote",
            "posted_date": "2024-01-01"
        }
        
        try:
            # Try to extract information based on common column patterns
            for col in columns:
                col_lower = col.lower().strip()
                value = row[col]
                
                if pd.isna(value):
                    continue
                    
                value_str = str(value).strip()
                
                # Position title
                if any(keyword in col_lower for keyword in ['title', 'position', 'job', 'role']):
                    if not any(keyword in col_lower for keyword in ['skill', 'requirement', 'level']):
                        position_data["title"] = value_str
                
                # Department
                elif any(keyword in col_lower for keyword in ['department', 'team', 'division']):
                    position_data["department"] = value_str
                
                # Level/Seniority
                elif any(keyword in col_lower for keyword in ['level', 'seniority', 'grade']):
                    position_data["level"] = value_str
                
                # Description
                elif any(keyword in col_lower for keyword in ['description', 'summary', 'details']):
                    position_data["description"] = value_str
                
                # Location
                elif any(keyword in col_lower for keyword in ['location', 'site', 'office']):
                    position_data["location"] = value_str
                
                # Skills - look for columns that might contain skill requirements
                elif any(keyword in col_lower for keyword in ['skill', 'requirement', 'competency']):
                    # Try to parse skill requirements
                    skill_level = 3  # default
                    
                    # Look for level indicators
                    if any(keyword in col_lower for keyword in ['basic', 'beginner', 'entry']):
                        skill_level = 2
                    elif any(keyword in col_lower for keyword in ['advanced', 'expert', 'senior']):
                        skill_level = 4
                    elif any(keyword in col_lower for keyword in ['intermediate', 'mid']):
                        skill_level = 3
                    
                    # Extract skill name
                    skill_name = col_lower.replace('skill', '').replace('requirement', '').replace('level', '').strip('_ -')
                    if skill_name and len(skill_name) > 1:
                        skill_id = skill_name.replace(' ', '_').replace('-', '_')
                        skill_id = ''.join(c for c in skill_id if c.isalnum() or c == '_')
                        
                        if skill_id:
                            position_data["required_skills"][skill_id] = skill_level
            
            # Ensure we have at least a title
            if not position_data["title"]:
                # Try to use first non-empty string value as title
                for col in columns:
                    value = row[col]
                    if pd.notna(value) and isinstance(value, str) and len(str(value).strip()) > 3:
                        position_data["title"] = str(value).strip()
                        break
                
                if not position_data["title"]:
                    return None
            
            return position_data
            
        except Exception as e:
            print(f"Error extracting position data: {e}")
            return None
    
    def _create_default_skill_taxonomy(self):
        """Create default skill taxonomy if Excel processing fails"""
        default_taxonomy = {
            "skill_categories": {
                "technical": {
                    "name": "Technical Skills",
                    "skills": {
                        "python": {"name": "Python Programming", "description": "Programming language proficiency", "related_skills": []},
                        "sql": {"name": "SQL", "description": "Database query and management", "related_skills": []},
                        "javascript": {"name": "JavaScript", "description": "Frontend and backend development", "related_skills": []}
                    }
                },
                "business": {
                    "name": "Business Skills",
                    "skills": {
                        "project_management": {"name": "Project Management", "description": "Managing projects and teams", "related_skills": []},
                        "communication": {"name": "Communication", "description": "Verbal and written communication", "related_skills": []}
                    }
                },
                "soft_skills": {
                    "name": "Soft Skills", 
                    "skills": {
                        "problem_solving": {"name": "Problem Solving", "description": "Analytical thinking and problem resolution", "related_skills": []},
                        "teamwork": {"name": "Teamwork", "description": "Collaborative work and team dynamics", "related_skills": []}
                    }
                }
            }
        }
        
        with open(self.config.SKILLS_TAXONOMY_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_taxonomy, f, indent=2)
    
    def _create_default_positions(self):
        """Create default positions if Excel processing fails"""
        default_positions = {
            "current_positions": [],
            "open_positions": [
                {
                    "id": "open_001",
                    "title": "Data Analyst",
                    "department": "Analytics",
                    "level": "Mid",
                    "location": "Remote",
                    "posted_date": "2024-01-15",
                    "required_skills": {"python": 3, "sql": 3, "data_analysis": 3},
                    "preferred_skills": {"statistics": 3, "communication": 3},
                    "description": "Analyze data and provide insights"
                }
            ]
        }
        
        with open(self.config.POSITIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_positions, f, indent=2)

def main():
    """Main function to process data"""
    processor = ExcelDataProcessor()
    processor.process_all_data()

if __name__ == "__main__":
    main()
