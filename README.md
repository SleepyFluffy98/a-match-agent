# 🎯 A-MATCH Agent

A comprehensive skill matching and learning recommendation platform built with Streamlit. This application helps employees assess their skills, match with suitable positions, and get personalized learning recommendations for career development.

## 🌟 Features

### Employee Self-Input Profile

- **Current Skills**: Select and rate skills across technical, business, and soft skill categories
- **Current Position**: Job title, department, seniority level, and work details
- **Career Goals**: Target roles, timeline, priorities, and learning preferences

### Core Functionality

- **Skill Gap Analysis**: Compare current skills with job requirements
- **Position Matching**: Find matching positions based on skills and preferences
- **Learning Recommendations**: Personalized learning plans with internal and external resources
- **Career Path Suggestions**: Identify potential career progression opportunities

### Analytics & Insights

- **Skill Trends**: Identify trending skills in the job market
- **Progress Tracking**: Monitor skill development over time
- **Interactive Dashboard**: Visual analytics and insights

## 🏗️ Project Structure

```
A-MATCH-AGENT/
├── 📄 app.py                 # Main Streamlit application
├── 📄 requirements.txt       # Python dependencies
├── 📄 .env                   # Environment variables
├── 📁 backend/               # Core business logic
│   ├── 📄 __init__.py
│   ├── 📄 models.py          # Data models and schemas
│   ├── 📄 data_manager.py    # Data operations
│   ├── 📄 skill_matcher.py   # Skill matching algorithms
│   └── 📄 learning_recommender.py # Learning recommendations
├── 📁 frontend/              # UI components
│   ├── 📄 __init__.py
│   └── 📄 employee_input.py  # Structured input form
├── 📁 config/                # Configuration
│   ├── 📄 __init__.py
│   └── 📄 config.py          # App configuration
└── 📁 data/                  # Data files
    ├── 📄 skills_taxonomy.json    # Skills database
    ├── 📄 positions.json          # Position requirements
    ├── 📄 learning_resources.json # Learning materials
    └── 📄 employees.json          # Employee profiles
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project**

   ```bash
   cd A-MATCH-AGENT
   ```
2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables (optional)**

   ```bash
   # Update .env file with your API keys if using external learning platforms
   OPENAI_API_KEY=your_key_here
   COURSERA_API_KEY=your_key_here
   ```
4. **Run the application**

   ```bash
   streamlit run app.py
   ```
5. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

## 📖 Usage Guide

### 1. Create Employee Profile

- Navigate to **👤 Employee Profile** in the sidebar
- Fill out the structured form with three main sections:
  - **🛠️ Current Skills**: Select skills and proficiency levels
  - **💼 Current Position**: Job details and personal information
  - **🎯 Career Goals**: Target roles, timeline, and preferences
- Click **Save Profile** to store your information

### 2. Skill Analysis

- View your skill distribution across categories
- Compare with industry standards and requirements
- Identify skill gaps for target positions

### 3. Position Matching

- Get matched with suitable open positions
- See match scores and skill requirements
- Review recommendations for career advancement

### 4. Learning Plans

- Generate personalized learning recommendations
- Access both internal and external resources
- Track progress and completion

## 📊 Data Models

### Skills Taxonomy

- Organized by categories (Technical, Business, Soft Skills)
- 5-point proficiency scale (Beginner to Expert)
- Skill relationships and dependencies

### Position Requirements

- Required and preferred skills with levels
- Department and seniority information
- Job descriptions and responsibilities

### Learning Resources

- Internal company training and workshops
- External courses from Coursera, Udemy, LinkedIn Learning
- Certifications and professional development

### Customizing UI

1. Modify CSS in `app.py` or create separate stylesheets
2. Add new Streamlit components as needed
3. Extend the structured input form in `frontend/employee_input.py`
