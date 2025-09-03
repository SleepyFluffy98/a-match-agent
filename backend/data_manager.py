import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from .models import Employee, Position, LearningResource, Skill
from config import Config

class DataManager:
    """Manages data operations for skills, positions, employees, and learning resources"""
    
    def __init__(self):
        self.config = Config()
        self._ensure_data_directory()
        
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.config.DATA_DIR):
            os.makedirs(self.config.DATA_DIR)
    
    def load_skills_taxonomy(self) -> Dict[str, Any]:
        """Load skills taxonomy from JSON file"""
        try:
            with open(self.config.SKILLS_TAXONOMY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"skill_categories": {}}
        except json.JSONDecodeError:
            return {"skill_categories": {}}
    
    def get_all_skills(self) -> List[Dict[str, Any]]:
        """Get all skills from taxonomy as a flat list"""
        taxonomy = self.load_skills_taxonomy()
        skills = []
        
        for category_name, category_data in taxonomy.get('skill_categories', {}).items():
            for skill_id, skill_data in category_data.get('skills', {}).items():
                skills.append({
                    'id': skill_id,
                    'name': skill_data['name'],
                    'category': category_name,
                    'description': skill_data.get('description', ''),
                    'related_skills': skill_data.get('related_skills', [])
                })
        
        return sorted(skills, key=lambda x: x['name'])
    
    def get_skills_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get skills organized by category"""
        taxonomy = self.load_skills_taxonomy()
        skills_by_category = {}
        
        for category_name, category_data in taxonomy.get('skill_categories', {}).items():
            category_skills = []
            for skill_id, skill_data in category_data.get('skills', {}).items():
                category_skills.append({
                    'id': skill_id,
                    'name': skill_data['name'],
                    'description': skill_data.get('description', ''),
                    'related_skills': skill_data.get('related_skills', [])
                })
            skills_by_category[category_data['name']] = sorted(category_skills, key=lambda x: x['name'])
        
        return skills_by_category
    
    def load_positions(self) -> Dict[str, Any]:
        """Load positions data from JSON file"""
        try:
            with open(self.config.POSITIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"current_positions": [], "open_positions": []}
        except json.JSONDecodeError:
            return {"current_positions": [], "open_positions": []}
    
    def get_current_positions(self) -> List[Position]:
        """Get all current positions"""
        positions_data = self.load_positions()
        positions = []
        
        for pos_data in positions_data.get('current_positions', []):
            positions.append(Position(**pos_data))
        
        return positions
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        positions_data = self.load_positions()
        positions = []
        
        for pos_data in positions_data.get('open_positions', []):
            pos_data['is_open'] = True
            positions.append(Position(**pos_data))
        
        return positions
    
    def get_position_by_id(self, position_id: str) -> Optional[Position]:
        """Get specific position by ID"""
        positions_data = self.load_positions()
        
        # Check current positions
        for pos_data in positions_data.get('current_positions', []):
            if pos_data['id'] == position_id:
                return Position(**pos_data)
        
        # Check open positions
        for pos_data in positions_data.get('open_positions', []):
            if pos_data['id'] == position_id:
                pos_data['is_open'] = True
                return Position(**pos_data)
        
        return None
    
    def load_employees(self) -> List[Employee]:
        """Load employees data from JSON file"""
        try:
            with open(self.config.EMPLOYEES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                employees = []
                for emp_data in data.get('employees', []):
                    # Parse datetime strings
                    emp_data['created_at'] = datetime.fromisoformat(emp_data['created_at'])
                    emp_data['updated_at'] = datetime.fromisoformat(emp_data['updated_at'])
                    employees.append(Employee(**emp_data))
                return employees
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, KeyError, ValueError):
            return []
    
    def save_employee(self, employee: Employee) -> bool:
        """Save or update employee data"""
        try:
            employees = self.load_employees()
            
            # Update existing employee or add new one
            updated = False
            for i, emp in enumerate(employees):
                if emp.id == employee.id:
                    employees[i] = employee
                    updated = True
                    break
            
            if not updated:
                employees.append(employee)
            
            # Convert to dict format for JSON serialization
            employees_data = {
                'employees': [emp.dict() for emp in employees]
            }
            
            with open(self.config.EMPLOYEES_FILE, 'w', encoding='utf-8') as f:
                json.dump(employees_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving employee: {e}")
            return False
    
    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        employees = self.load_employees()
        for emp in employees:
            if emp.id == employee_id:
                return emp
        return None
    
    def get_most_recent_employee(self) -> Optional[Employee]:
        """Get the most recently updated employee"""
        employees = self.load_employees()
        if not employees:
            return None
        return max(employees, key=lambda e: e.updated_at)
    
    def get_all_employees(self) -> List[Employee]:
        """Get all employees sorted by most recent"""
        employees = self.load_employees()
        return sorted(employees, key=lambda e: e.updated_at, reverse=True)
    
    def delete_employee(self, employee_id: str) -> bool:
        """Delete employee by ID"""
        try:
            employees = self.load_employees()
            employees = [emp for emp in employees if emp.id != employee_id]
            
            employees_data = {
                'employees': [emp.dict() for emp in employees]
            }
            
            with open(self.config.EMPLOYEES_FILE, 'w', encoding='utf-8') as f:
                json.dump(employees_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error deleting employee: {e}")
            return False
