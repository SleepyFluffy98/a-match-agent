import pandas as pd
import json

def analyze_excel_files():
    """Analyze the Excel files in raw-data folder"""
    
    try:
        # Read skill taxonomy
        print("=== SKILL TAXONOMY ===")
        skill_df = pd.read_excel('raw-data/skill-taxonomy.xlsx')
        print("Columns:", skill_df.columns.tolist())
        print("Shape:", skill_df.shape)
        print("First 5 rows:")
        print(skill_df.head())
        
        print("\n=== POSITION SKILL REQUIREMENTS ===")
        pos_df = pd.read_excel('raw-data/position-skill-requirements.xlsx')
        print("Columns:", pos_df.columns.tolist())
        print("Shape:", pos_df.shape)
        print("First 5 rows:")
        print(pos_df.head())
        
        print("\n=== JOB OUTPUT WITH SKILLS ===")
        job_df = pd.read_excel('raw-data/job_output_with_skills_cleaned.xlsx')
        print("Columns:", job_df.columns.tolist())
        print("Shape:", job_df.shape)
        print("First 5 rows:")
        print(job_df.head())
        
    except Exception as e:
        print(f"Error reading files: {e}")

if __name__ == "__main__":
    analyze_excel_files()
