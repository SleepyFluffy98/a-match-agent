import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import uuid
import base64

from config import Config
from backend.data_manager import DataManager
from backend.skill_matcher import SkillMatcher
from backend.learning_recommender import LearningRecommender
from frontend.employee_input import EmployeeInputForm
from frontend.learning_chatbot import LearningChatbotUI

# Define sidebar styling
def apply_sidebar_styling():
    st.markdown("""
    <style>
    /* Main sidebar container */
    .css-1d391kg {
        background-color: #EEF6F8 !important;  /* Light blue */
    }
    
    /* Sidebar content area */
    .css-1cypcdb {
        background-color: #EEF6F8 !important;
    }
    
    /* Alternative selector for newer Streamlit versions */
    section[data-testid="stSidebar"] > div {
        background-color: #EEF6F8 !important;
    }
    
    /* Sidebar elements styling */
    .stSelectbox > div > div {
        background-color: white;
        border: 1px solid #5FB0C9;
    }
    </style>
    """, unsafe_allow_html=True)


# Page configuration
st.set_page_config(
    page_title="A-MATCH Agent",
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_sidebar_styling()


# Initialize session state
if 'current_employee' not in st.session_state:
    st.session_state.current_employee = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'components_loaded' not in st.session_state:
    st.session_state.components_loaded = False
if 'auto_loaded_profile' not in st.session_state:
    st.session_state.auto_loaded_profile = False

# Global components (loaded lazily)
if 'config' not in st.session_state:
    st.session_state.config = None
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = None
if 'skill_matcher' not in st.session_state:
    st.session_state.skill_matcher = None
if 'learning_recommender' not in st.session_state:
    st.session_state.learning_recommender = None

# Define logo on sidebar 
def get_logo_base64():
    """Load logo and convert to base64"""
    with open("UI/logo.png", "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# Initialize components (loaded lazily to avoid startup hang)
def load_components_safely():
    """Safely load components with proper error handling"""
    try:
        # Import modules only when needed
        from config import Config
        from backend import DataManager, SkillMatcher, LearningRecommender, Employee
        from frontend.employee_input import EmployeeInputForm
        
        # Initialize components
        if st.session_state.config is None:
            with st.spinner("Loading configuration..."):
                st.session_state.config = Config()
        
        if st.session_state.data_manager is None:
            with st.spinner("Loading data manager..."):
                st.session_state.data_manager = DataManager()
        
        if st.session_state.skill_matcher is None:
            with st.spinner("Loading skill matcher..."):
                st.session_state.skill_matcher = SkillMatcher()
        
        if st.session_state.learning_recommender is None:
            with st.spinner("Loading learning recommender..."):
                st.session_state.learning_recommender = LearningRecommender()
        
        st.session_state.components_loaded = True
        return True
        
    except Exception as e:
        st.error(f"❌ Error loading components: {e}")
        return False

def get_components():
    """Get components, loading them if necessary"""
    if not st.session_state.components_loaded:
        success = load_components_safely()
        if not success:
            st.stop()
    
    return (
        st.session_state.config,
        st.session_state.data_manager,
        st.session_state.skill_matcher,
        st.session_state.learning_recommender
    )

def auto_load_recent_profile():
    """Auto-load the most recently updated profile"""
    if st.session_state.auto_loaded_profile or st.session_state.current_employee:
        return
    
    try:
        data_manager = st.session_state.data_manager
        if data_manager:
            employees = data_manager.load_employees()
            if employees:
                # Sort by updated_at to get the most recent
                most_recent = max(employees, key=lambda e: e.updated_at)
                st.session_state.current_employee = most_recent
                st.success(f"✅ Auto-loaded profile: **{most_recent.name}** ({most_recent.current_position})")
    except Exception as e:
        print(f"Error auto-loading profile: {e}")
    
    st.session_state.auto_loaded_profile = True

def check_authentication():
    """Check if user is authenticated for deployment"""
    # Initialize authentication state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # If not authenticated, show login screen
    if not st.session_state.authenticated:
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: #2c5aa0;">🔐 A-MATCH Agent</h1>
            <h3 style="color: #5FB0C9;">Secure Access Required</h3>
            <p style="color: #666;">This is a private testing environment. Please enter your access code to continue.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create centered login form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("🔑 Access Code:", type="password", placeholder="Enter your access code")
            
            if st.button("🚀 Enter A-MATCH", use_container_width=True):
                # Get password from secrets (for deployment) or use default
                try:
                    correct_password = st.secrets.get("ACCESS_PASSWORD", "amatch2025")
                except:
                    correct_password = "amatch2025"
                    
                if password == correct_password:
                    st.session_state.authenticated = True
                    st.success("✅ Access granted! Welcome to A-MATCH Agent.")
                    st.rerun()
                else:
                    st.error("❌ Invalid access code. Please try again.")
        
        st.markdown("""
        <div style="text-align: center; padding: 30px; font-size: 12px; color: #888;">
            <p>© 2025 A-MATCH Agent - Private Testing Environment</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.stop()  # Stop execution if not authenticated

# Define Sidebar
def main():
    """Main application function"""
    # Check authentication first
    check_authentication()
    
    # Get components (load if needed)
    config, data_manager, skill_matcher, learning_recommender = get_components()
    
    # Sidebar navigation
    with st.sidebar:
        try:
            logo_base64 = get_logo_base64()
            st.markdown(f"""
        <div style="display: flex; justify-content: center; padding: 0px 0;">
            <img src="data:image/png;base64,{logo_base64}" 
                 width="200" 
                 style="background: transparent;">
        </div>
        """, unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("Logo not found")

#       st.markdown("""
#       <div style='text-align: center; padding: 20px;'>
#           <h1>🎯</h1>
#           <h3>How can I help you?</h3>
#      </div>
#        """, unsafe_allow_html=True)
        
        # Navigation menu
        pages = {
            "🏠 Home": "Home",
            "🪪 My Profile": "Profile", 
            "📑 Skill Assessment": "Assessment",
            "💡 Personal Assistant": "Learning"
        }
        
        selected_page = st.selectbox("Navigate to:", list(pages.keys()))
        st.session_state.page = pages[selected_page]
        
        # Configuration status

        config_status = config.validate_config()
        if config_status['valid']:
            st.success("✅ Configuration Valid")
        else:
            st.error("❌ Configuration Issues:")
            for issue in config_status['issues']:
                st.error(f"• {issue}")
        
        # Current user info and profile selector
        if st.session_state.current_employee:
            st.markdown("---")
            st.markdown(f"**Current User:** {st.session_state.current_employee.name}")
            
            # Profile selector
            employees = sorted(data_manager.load_employees(), key=lambda e: e.updated_at, reverse=True)
            if len(employees) > 1:
                st.markdown("**Switch Profile:**")
                profile_options = {f"{emp.name} ({emp.current_position})": emp.id for emp in employees}
                current_profile_key = f"{st.session_state.current_employee.name} ({st.session_state.current_employee.current_position})"
                
                selected_profile = st.selectbox(
                    "Choose profile:", 
                    list(profile_options.keys()),
                    index=list(profile_options.keys()).index(current_profile_key) if current_profile_key in profile_options else 0,
                    key="profile_selector"
                )
                
                # Switch profile if different one selected
                selected_id = profile_options[selected_profile]
                if selected_id != st.session_state.current_employee.id:
                    new_employee = data_manager.get_employee_by_id(selected_id)
                    if new_employee:
                        st.session_state.current_employee = new_employee
                        st.success(f"Switched to: {new_employee.name}")
                        st.rerun()
            
            if st.button("🚪 Logout"):
                st.session_state.current_employee = None
                st.session_state.auto_loaded_profile = False
                st.rerun()
        else:
            # Auto-load recent profile
            auto_load_recent_profile()
            
            # Show available profiles
            employees = sorted(data_manager.load_employees(), key=lambda e: e.updated_at, reverse=True)
            if employees:
                st.markdown("---")
                st.markdown("**Available Profiles:**")
                for emp in employees[:3]:  # Show first 3 profiles (most recent)
                    if st.button(f"👤 {emp.name}", key=f"load_{emp.id}"):
                        st.session_state.current_employee = emp
                        st.rerun()
    
    # Main content area
    if st.session_state.page == "Home":
        show_home_page(data_manager)
    elif st.session_state.page == "Profile":
        show_profile_page(data_manager)
    elif st.session_state.page == "Assessment":
        show_assessment_page(data_manager, skill_matcher)
    elif st.session_state.page == "Learning":
        chatbot_ui = LearningChatbotUI(learning_recommender)
        chatbot_ui.render()

def show_home_page(data_manager):
    """Display the home page"""
    
    # Add animated GIF at the top - left aligned and properly animated
    import base64
    
    # Read and encode the GIF file to ensure animation works
    try:
        with open("UI/A-MATCH.gif", "rb") as gif_file:
            gif_bytes = gif_file.read()
            gif_b64 = base64.b64encode(gif_bytes).decode()
        
        st.markdown(f"""
        <div style="margin-top: -40px; margin-bottom: 20px;">
            <img src="data:image/gif;base64,{gif_b64}" 
                 alt="A-MATCH Animation" 
                 style="width: 180px; border-radius: 10px;">
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("GIF file not found at UI/A-MATCH.gif")
    st.title("Meet MATCHi, Your AI Career Companion ✨")
    st.markdown("""
    ### Key Features
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: #EEF6F8; 
                    border: 1px solid #5FB0C9;
                    padding: 25px; border-radius: 12px; text-align: center; 
                    height: 180px; display: flex; flex-direction: column; justify-content: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <h3 style='color: #2c5aa0; margin: 0 0 5px 0; font-size: 1.5rem;'>🪪 Smart Profiling</h3>
            <p style='color: #5a6c7d; margin: 0; font-size: 1.0rem; line-height: 1.4;'>Create skill profiles with intelligent categorization and assessment</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #EEF6F8; 
                    border: 1px solid #5FB0C9;
                    padding: 25px; border-radius: 12px; text-align: center; 
                    height: 180px; display: flex; flex-direction: column; justify-content: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <h3 style='color: #2c5aa0; margin: 0 0 5px 0; font-size: 1.5rem;'>🎯 Position Matching</h3>
            <p style='color: #5a6c7d; margin: 0; font-size: 1.0rem; line-height: 1.4;'>Find the perfect job matches based on your skills and career goals</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: #EEF6F8; 
                    border: 1px solid #5FB0C9;
                    padding: 25px; border-radius: 12px; text-align: center; 
                    height: 180px; display: flex; flex-direction: column; justify-content: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
            <h3 style='color: #2c5aa0; margin: 0 0 5px 0; font-size: 1.5rem;'>📚 Learning Plans</h3>
            <p style='color: #5a6c7d; margin: 0; font-size: 1.0rem; line-height: 1.4;'>Get personalized learning recommendations powered by AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    

    
    # Getting started
    st.markdown("""
    ### Getting Started
    
    1. **Create Your Profile**: Complete the structured input form with your skills, experience, and career goals
    2. **Assess Your Skills**: Get detailed analysis of your skill gaps and strengths  
    3. **Discover Opportunities**: Find matching positions and career paths
    4. **Plan Your Growth**: Receive personalized learning recommendations
    5. **Track Progress**: Monitor your skill development over time
    """)
    
    # Show current profile status
    employees = sorted(data_manager.load_employees(), key=lambda e: e.updated_at, reverse=True)
    if employees:
        st.success(f"**{len(employees)} saved profile(s)** - Most recent: {employees[0].name}")
    else:
        st.info("No profiles saved yet - Create your first profile to get started!")

def show_profile_page(data_manager):
    """Display the profile management page"""
    st.title("🪪 My Profile")
    
    if st.session_state.current_employee:
        # Show existing profile
        emp = st.session_state.current_employee
        
        st.markdown(f"""
        ### Welcome back, {emp.name}!
        **Position:** {emp.current_position}  
        **Department:** {emp.department}  
        **Profile Created:** {emp.created_at.strftime('%B %d, %Y')}
        """)
        
        # Skills overview
        st.subheader("Your Skills")
        if emp.skills:
            # Get config for skill level names
            config, _, _, _ = get_components()
            
            skills_df = pd.DataFrame([
                {"Skill": skill.replace('_', ' ').title(), "Level": level, "Level Name": config.get_skill_level_name(level)}
                for skill, level in emp.skills.items()
            ])
            
            fig = px.bar(skills_df, x="Skill", y="Level", color="Level",
                        title="Your Skill Levels", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)
        
        # Career goals
        st.subheader("Career Goals")
        if emp.target_roles:
            for role in emp.target_roles:
                st.markdown(f"• {role}")
        
        # Edit profile button
        if st.button("✏️ Edit Profile"):
            # Clear current employee to force fresh input
            if 'current_employee' in st.session_state:
                del st.session_state['current_employee']
            # Switch to Employee Input page
            st.session_state.selected_page = "Employee Input"
            st.rerun()
    else:
        # Show profile creation form
        st.markdown("### Create Your Professional Profile")
        
        # Import form class when needed
        try:
            from frontend.employee_input import EmployeeInputForm
            form = EmployeeInputForm()
            employee = form.render_structured_form()
            
            if employee:
                # Save employee profile
                success = data_manager.save_employee(employee)
                if success:
                    st.session_state.current_employee = employee
                    st.success("✅ Profile created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Error saving profile. Please try again.")
        except Exception as e:
            st.error(f"❌ Error loading profile form: {e}")
            st.info("Please check that all required modules are properly installed.")

def show_assessment_page(data_manager, skill_matcher):
    """Display the skill assessment page"""
    st.title("📑 Skill Assessment")
    
    if not st.session_state.current_employee:
        st.warning("Please create your profile first!")
        return
    
    emp = st.session_state.current_employee
    
    # Skill gap analysis for target roles
    st.subheader("Skill Gap Analysis")
    
    if emp.target_roles:
        target_role = st.selectbox("Select target role for analysis:", emp.target_roles)
        
        if st.button("🔍 Analyze Skills"):
            # Find matching position
            open_positions = data_manager.get_open_positions()
            matching_position = None
            
            for pos in open_positions:
                if target_role.lower() in pos.title.lower():
                    matching_position = pos
                    break
            
            if matching_position:
                # Calculate skill gaps
                skill_gaps = skill_matcher.calculate_skill_gap(emp.skills, matching_position.required_skills)
                
                if skill_gaps:
                    # Display gaps
                    st.markdown("### Skill Gaps Identified")
                    
                    gaps_data = []
                    for gap in skill_gaps:
                        gaps_data.append({
                            "Skill": gap.skill_name.replace('_', ' ').title(),
                            "Current Level": gap.current_level,
                            "Required Level": gap.required_level,
                            "Gap": gap.gap,
                            "Priority": gap.priority.title()
                        })
                    
                    gaps_df = pd.DataFrame(gaps_data)
                    
                    # Color code by priority
                    color_map = {"High": "#1976D2", "Medium": "#5FB0C9", "Low": "#90CAF9"}
                    fig = px.bar(gaps_df, x="Skill", y="Gap", color="Priority",
                                title="Skill Gaps by Priority", 
                                color_discrete_map=color_map)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show detailed gap table
                    st.dataframe(gaps_df, use_container_width=True)
                else:
                    st.success("🎉 No skill gaps found! You meet all requirements.")
            else:
                st.warning(f"No matching position found for '{target_role}'")

def show_matching_page(skill_matcher):
    """Display the position matching page"""
    st.title("Position Matching")

    if not st.session_state.current_employee:
        st.warning("Please create your profile first!")
        return
    
    emp = st.session_state.current_employee
    
    st.subheader("🔍 Find Matching Positions")
    
    include_current = st.checkbox("Include current positions (for career progression)")
    
    if st.button("🎯 Find Matches"):
        matches = skill_matcher.find_position_matches(emp, include_current)
        
        if matches:
            st.markdown(f"### Found {len(matches)} Matching Positions")
            
            for i, match in enumerate(matches):
                with st.expander(f"🎯 {match.position.title} - {match.match_score:.1%} match"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **Department:** {match.position.department}  
                        **Level:** {match.position.level}  
                        **Location:** {match.position.location}  
                        
                        **Description:** {match.position.description}
                        
                        **Recommendation:** {match.recommendation}
                        """)
                    
                    with col2:
                        # Match score gauge
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = match.match_score * 100,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Match Score"},
                            gauge = {
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkgreen"},
                                'steps': [
                                    {'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 80], 'color': "yellow"},
                                    {'range': [80, 100], 'color': "green"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))
                        fig.update_layout(height=250)
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No matching positions found. Consider expanding your skill set!")

def show_analytics_page(data_manager, learning_recommender):
    """Display analytics and insights page"""
    st.title("📊 Analytics & Insights")
    
    try:
        # Trending skills
        st.subheader("📈 Trending Skills")
        trending_skills = learning_recommender.get_trending_skills()
        
        if trending_skills:
            trend_df = pd.DataFrame(trending_skills)
            trend_df['skill_display'] = trend_df['skill'].str.replace('_', ' ').str.title()
            
            fig = px.bar(trend_df.head(10), x="skill_display", y="demand_count", 
                        color="average_level", title="Most In-Demand Skills",
                        color_continuous_scale="viridis")
            fig.update_layout(xaxis_title="Skills", yaxis_title="Demand Count")
            st.plotly_chart(fig, use_container_width=True)
        
        # Skills distribution
        st.subheader("🎯 Skills Overview")
        skills_data = data_manager.get_skills_by_category()
        
        # Count skills by category
        category_counts = {cat: len(skills) for cat, skills in skills_data.items()}
        
        if category_counts:
            fig = px.pie(values=list(category_counts.values()), 
                        names=list(category_counts.keys()),
                        title="Skills by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        # Position insights
        st.subheader("💼 Position Insights")
        positions = data_manager.get_open_positions()
        
        if positions:
            # Positions by department
            dept_counts = {}
            for pos in positions:
                dept = pos.department
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            
            fig = px.bar(x=list(dept_counts.keys()), y=list(dept_counts.values()),
                        title="Open Positions by Department",
                        labels={'x': 'Department', 'y': 'Number of Positions'})
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

if __name__ == "__main__":
    main()
