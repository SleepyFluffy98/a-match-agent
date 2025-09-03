import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class Config:
    """Application configuration settings"""
    
    def __init__(self):
        """Initialize config, checking both environment and Streamlit secrets"""
        # Try to import streamlit for deployment
        self._streamlit_secrets = None
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                self._streamlit_secrets = st.secrets
        except:
            pass
    
    def _get_setting(self, key: str, default: str = '') -> str:
        """Get setting from environment or Streamlit secrets"""
        # First try environment variable
        env_value = os.getenv(key, '')
        if env_value:
            return env_value
        
        # Then try Streamlit secrets
        if self._streamlit_secrets:
            try:
                return self._streamlit_secrets.get(key, default)
            except:
                pass
        
        return default
    
    # OpenAI API Keys
    @property
    def OPENAI_API_KEY(self):
        return self._get_setting('OPENAI_API_KEY')
    
    # Azure OpenAI Settings
    @property
    def AZURE_OPENAI_ENDPOINT(self):
        return self._get_setting('AZURE_OPENAI_ENDPOINT')
    
    @property
    def AZURE_OPENAI_API_KEY(self):
        return self._get_setting('AZURE_OPENAI_API_KEY')
    
    @property
    def AZURE_OPENAI_CHAT_MODEL(self):
        return self._get_setting('AZURE_OPENAI_CHAT_MODEL', 'gpt-4')
    
    @property
    def AZURE_OPENAI_CHAT_DEPLOYMENT(self):
        return self._get_setting('AZURE_OPENAI_CHAT_DEPLOYMENT', 'gpt-4')
    
    @property
    def AZURE_OPENAI_EMBED_MODEL(self):
        return self._get_setting('AZURE_OPENAI_EMBED_MODEL', 'text-embedding-ada-002')
    
    @property
    def AZURE_OPENAI_EMBED_DEPLOYMENT(self):
        return self._get_setting('AZURE_OPENAI_EMBED_DEPLOYMENT', 'text-embedding-ada-002')
    
    @property
    def AZURE_OPENAI_EMBED_DIMENSIONS(self):
        return int(self._get_setting('AZURE_OPENAI_EMBED_DIMENSIONS', '1536'))
    
    # Application Settings
    MAX_LEARNING_RESOURCES = int(os.getenv('MAX_LEARNING_RESOURCES', 10))
    SKILL_MATCH_THRESHOLD = float(os.getenv('SKILL_MATCH_THRESHOLD', 0.7))
    RECOMMENDATION_COUNT = int(os.getenv('RECOMMENDATION_COUNT', 5))
    
    # GPT Settings
    USE_GPT_RESOURCE_GENERATION = os.getenv('USE_GPT_RESOURCE_GENERATION', 'true').lower() == 'true'
    GPT_MODEL = os.getenv('GPT_MODEL', 'gpt-4')
    
    # Data Paths
    RAW_DATA_DIR = 'raw-data'
    DATA_DIR = 'data'
    
    # Raw data files
    SKILL_TAXONOMY_RAW = os.path.join(RAW_DATA_DIR, 'skill-taxonomy.xlsx')
    POSITION_REQUIREMENTS_RAW = os.path.join(RAW_DATA_DIR, 'position-skill-requirements.xlsx')
    JOB_OUTPUT_RAW = os.path.join(RAW_DATA_DIR, 'job_output_with_skills_cleaned.xlsx')
    
    # Processed data files
    SKILLS_TAXONOMY_FILE = os.path.join(DATA_DIR, 'skills_taxonomy.json')
    POSITIONS_FILE = os.path.join(DATA_DIR, 'positions.json')
    EMPLOYEES_FILE = os.path.join(DATA_DIR, 'employees.json')
    
    # Skill Levels
    SKILL_LEVELS = {
        1: "Beginner",
        2: "Novice", 
        3: "Intermediate",
        4: "Advanced",
        5: "Expert"
    }
    
    @classmethod
    def get_skill_level_name(cls, level: int) -> str:
        return cls.SKILL_LEVELS.get(level, "Unknown")
    
    @classmethod
    def use_azure_openai(cls) -> bool:
        """Check if Azure OpenAI should be used"""
        return bool(cls.AZURE_OPENAI_ENDPOINT and cls.AZURE_OPENAI_API_KEY)
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        if not cls.use_azure_openai() and not cls.OPENAI_API_KEY:
            issues.append("Neither Azure OpenAI nor OpenAI API key configured")
        
        # Check for raw data files
        raw_data_files = [
            cls.SKILL_TAXONOMY_RAW,
            cls.POSITION_REQUIREMENTS_RAW,
            cls.JOB_OUTPUT_RAW
        ]
        
        for file_path in raw_data_files:
            if not os.path.exists(file_path):
                issues.append(f"Raw data file missing: {file_path}")
                
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'azure_openai_enabled': cls.use_azure_openai()
        }
