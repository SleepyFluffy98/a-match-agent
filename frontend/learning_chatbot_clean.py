"""
Learning Assistant Chatbot Module
Provides intelligent career guidance and learning recommendations using Azure OpenAI
"""

import json
import time
from typing import List, Dict, Any, Optional

import requests
import streamlit as st

from config.config import Config
from backend.models import Employee
from backend.learning_recommender import LearningRecommender


class LearningChatbot:
    """Interactive learning assistant powered by Azure OpenAI GPT-4"""

    def __init__(self, learning_recommender: LearningRecommender):
        self.learning_recommender = learning_recommender
        self.config = Config()
        self.deployment_name = getattr(self.config, "AZURE_OPENAI_CHAT_DEPLOYMENT", None) or "gpt-4"
        self.api_version = "2024-02-01"

    def _create_chat_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "api-key": self.config.AZURE_OPENAI_API_KEY,
        }

    def _generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 800,
        max_retries: int = 3,
        temperature: Optional[float] = 0.2,
    ) -> str:
        """
        Generate a response using the Azure OpenAI Chat Completions API.
        """
        endpoint = self.config.AZURE_OPENAI_ENDPOINT.rstrip("/")
        url = f"{endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"

        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        headers = self._create_chat_headers()
        
        print(f"Chatbot making API call to: {url}")
        print(f"Using deployment: {self.deployment_name}")

        last_error = None
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()

                choices = data.get("choices", [])
                if choices and len(choices) > 0:
                    message = choices[0].get("message", {})
                    content = message.get("content", "")
                    
                    if content and content.strip():
                        finish_reason = choices[0].get("finish_reason")
                        if finish_reason == "content_filter":
                            print("⚠️ Content filter triggered.")
                        return content.strip()

                print("Empty content from Chat Completions API.")
                last_error = "Empty content from Chat Completions API"

            except requests.HTTPError as e:
                body = getattr(e, "response", None) and e.response.text
                print(f"[Chat] HTTPError (attempt {attempt+1}): {e}\nBody: {body}")
                last_error = f"HTTPError: {e}"
            except requests.Timeout:
                print(f"[Chat] Timeout (attempt {attempt+1})")
                last_error = "Timeout"
            except Exception as e:
                print(f"[Chat] Unexpected error (attempt {attempt+1}): {e}")
                last_error = str(e)

            if attempt < max_retries - 1:
                time.sleep(1)

        raise Exception(f"Failed to generate chat response after {max_retries} attempts: {last_error}")

    def get_employee_context(self, employee: Employee) -> str:
        """Generate context string about the employee for the AI"""
        skills_list = [f"{skill.replace('_', ' ').title()} (Level {level})"
                       for skill, level in employee.skills.items()]

        years_exp_text = ""
        if hasattr(st.session_state, 'position_years_experience'):
            years_exp_text = f"\n        - Years in Current Position: {st.session_state.position_years_experience}"

        context = f"""
        Employee Profile:
        - Name: {employee.name}
        - Current Position: {employee.current_position}
        - Department: {employee.department}{years_exp_text}
        - Skills: {', '.join(skills_list[:10])}{'...' if len(skills_list) > 10 else ''}
        - Target Roles: {', '.join(employee.target_roles) if employee.target_roles else 'Not specified'}
        - Career Goals: {', '.join(employee.career_goals) if employee.career_goals else 'Not specified'}
        """

        # Add skill gap analysis if target roles exist
        if employee.target_roles and self.learning_recommender:
            try:
                target_role = employee.target_roles[0]
                learning_plan = self.learning_recommender.generate_learning_plan(
                    employee, target_role, max_resources=3
                )
                if learning_plan and learning_plan.skill_gaps:
                    gaps = [
                        f"{gap.skill_name.replace('_', ' ').title()} (need level {gap.required_level}, current {gap.current_level})"
                        for gap in learning_plan.skill_gaps[:5]
                    ]
                    context += f"\n- Key Skill Gaps: {', '.join(gaps)}"
            except Exception:
                pass

        return context.strip()

    def generate_ai_response(self, user_message: str, employee: Employee, chat_history: List[Dict]) -> str:
        """Generate response using Azure OpenAI, fallback if needed"""
        if not self.config.AZURE_OPENAI_ENDPOINT or not self.config.AZURE_OPENAI_API_KEY:
            return self._get_fallback_response(user_message, employee)

        try:
            employee_context = self.get_employee_context(employee)
            system_message = f"""You are an AI Learning Assistant specializing in career development and skill enhancement. 
You have access to the following employee information:

{employee_context}

Your role is to:
1. Provide personalized learning recommendations
2. Analyze skill gaps and career progression paths
3. Suggest specific courses, resources, and learning strategies
4. Offer motivational support and practical advice
5. Help create actionable learning plans

Guidelines:
- Be encouraging and supportive
- When provide external resources, always include working URL
- Provide specific, actionable advice
- Reference the employee's current skills and goals
- Suggest concrete next steps
- Use emojis and formatting to make responses engaging
- Keep responses concise but comprehensive
- Always relate advice back to their career goals
"""

            messages: List[Dict[str, str]] = [{"role": "system", "content": system_message}]

            # Keep last 6 messages to limit context size
            recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
            for msg in recent_history:
                if msg.get("role") in ("user", "assistant"):
                    messages.append({"role": msg["role"], "content": msg.get("content", "")})

            messages.append({"role": "user", "content": user_message})

            try:
                response_content = self._generate_chat_response(messages, max_tokens=800)

                if not response_content or len(response_content.strip()) < 10:
                    st.warning("AI returned empty/short response, using fallback")
                    return self._get_fallback_response(user_message, employee)

                return response_content

            except Exception as e:
                st.warning(f"AI temporarily unavailable: {str(e)} - Using fallback response")
                return self._get_fallback_response(user_message, employee)

        except Exception as e:
            st.error(f"Error preparing AI request: {str(e)}")
            return self._get_fallback_response(user_message, employee)

    def _get_fallback_response(self, user_message: str, employee: Employee) -> str:
        """Provide fallback responses when AI is unavailable"""
        user_input_lower = (user_message or "").lower()

        # Skill gap analysis
        if any(word in user_input_lower for word in ["gap", "missing", "need", "improve", "weak"]):
            if employee.target_roles:
                target_role = employee.target_roles[0]
                try:
                    learning_plan = self.learning_recommender.generate_learning_plan(
                        employee, target_role, max_resources=5
                    )
                    if learning_plan and learning_plan.skill_gaps:
                        gaps_text = "\n".join([
                            f"• **{gap.skill_name.replace('_', ' ').title()}**: You have level {gap.current_level}, need level {gap.required_level}"
                            for gap in learning_plan.skill_gaps[:5]
                        ])
                        return f"🎯 **Skill Gap Analysis for {target_role}:**\n\n{gaps_text}\n\nWould you like specific learning resources for any of these skills?"
                except Exception:
                    pass
            return "🎯 To help identify your skill gaps, I'd need to know your target role. What position are you aiming for?"

        # Learning resources
        elif any(word in user_input_lower for word in ["course", "learn", "resource", "study", "training"]):
            skills_mentioned = []
            for skill in employee.skills.keys():
                s_norm = skill.lower()
                if s_norm in user_input_lower or skill.replace('_', ' ').lower() in user_input_lower:
                    skills_mentioned.append(skill)

            if skills_mentioned:
                skill = skills_mentioned[0]
                return (
                    f"📚 **Learning Resources for {skill.replace('_', ' ').title()}:**\n\n"
                    "• **Online Courses**: Coursera, Udemy, edX\n"
                    "• **Documentation**: Official guides and tutorials\n"
                    "• **Practice**: Hands-on projects and exercises\n"
                    "• **Community**: Join forums and study groups\n"
                    "• **Certifications**: Industry-recognized credentials\n\n"
                    "Would you like me to help you create a detailed learning plan?"
                )

            return (
                "📚 **Popular Learning Resources:**\n\n"
                "• **Online Platforms**: Coursera, Udemy, Pluralsight, LinkedIn Learning\n"
                "• **Technical Skills**: Stack Overflow, GitHub, documentation sites\n"
                "• **Soft Skills**: Books, webinars, workshops\n"
                "• **Certifications**: AWS, Google, Microsoft, project management\n\n"
                "What specific skill would you like to develop?"
            )

        # Career advice
        elif any(word in user_input_lower for word in ["career", "path", "goal", "future", "next"]):
            if employee.target_roles:
                roles = ", ".join(employee.target_roles)
                return (
                    f"🚀 **Career Development Plan:**\n\nBased on your target roles ({roles}), here's my advice:\n\n"
                    "1. **Skill Assessment**: Identify gaps between current and required skills\n"
                    "2. **Learning Priority**: Focus on high-impact skills first\n"
                    "3. **Practical Experience**: Apply new skills in real projects\n"
                    "4. **Networking**: Connect with professionals in your target field\n"
                    "5. **Continuous Learning**: Stay updated with industry trends\n\n"
                    "Would you like a specific learning roadmap?"
                )

            return (
                "🚀 **Career Development Tips:**\n\n"
                "• **Set Clear Goals**: Define where you want to be in 1-3 years\n"
                "• **Skill Mapping**: Identify required vs current skills\n"
                "• **Network Building**: Connect with industry professionals\n"
                "• **Continuous Learning**: Stay updated with trends\n"
                "• **Get Experience**: Apply skills through projects\n\n"
                "What's your ideal next career step?"
            )

        # Default personalized response
        else:
            current_skills = list(employee.skills.keys())[:3]
            skills_text = ", ".join([skill.replace('_', ' ').title() for skill in current_skills])
            return (
                f"**I'm here to help with your learning journey!**\n\n"
                f"Based on your profile:\n"
                f"• **Current Role**: {employee.current_position}\n"
                f"• **Top Skills**: {skills_text}\n"
                f"• **Target Roles**: {', '.join(employee.target_roles) if employee.target_roles else 'Not specified'}\n\n"
                "**I can help you with:**\n"
                "• Skill gap analysis\n"
                "• Learning resource recommendations\n"
                "• Career development planning\n"
                "• Study strategies and timelines\n\n"
                "**Try asking:**\n"
                "• \"What skills do I need to improve?\"\n"
                "• \"How can I learn Python faster?\"\n"
                "• \"What's my career development plan?\"\n\n"
                "What would you like to explore?"
            )


class LearningChatbotUI:
    """Streamlit UI for the Learning Chatbot"""

    def __init__(self, learning_recommender: LearningRecommender):
        self.chatbot = LearningChatbot(learning_recommender)

    def render(self):
        """Render the chatbot interface"""
        st.title("💡 Chat with MATCHi")

        if not st.session_state.current_employee:
            st.warning("Please create your profile first!")
            return

        emp: Employee = st.session_state.current_employee

        # Display Azure OpenAI status
        if self.chatbot.config.AZURE_OPENAI_ENDPOINT and self.chatbot.config.AZURE_OPENAI_API_KEY:
            st.success("🚀 Powered by Azure OpenAI")
        else:
            st.warning("⚠️ Running in fallback mode - Azure OpenAI not configured")

        # Initialize chat history
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [{
                "role": "assistant",
                "content": (
                    f"Hello **{emp.name}**! 👋 I'm your AI Learning Assistant.\n\n"
                    f"I can see you're currently a **{emp.current_position}** with expertise in "
                    f"{', '.join(list(emp.skills.keys())[:3])}{'...' if len(emp.skills) > 3 else ''}.\n\n"
                    f"**How can I help you today?**\n\n"
                    "• 📚 Personalized learning recommendations\n"
                    "• 🎯 Skill gap analysis for your target roles\n"
                    "• 📋 Career development planning\n"
                    "• 💡 Learning strategies and resources\n"
                    "• 🚀 Next steps in your career journey\n\n"
                    "What would you like to explore?"
                )
            }]

        # Display chat messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask me about your learning path..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    response = self.chatbot.generate_ai_response(
                        prompt, emp, st.session_state.chat_messages[:-1]
                    )
                    st.markdown(response)

            st.session_state.chat_messages.append({"role": "assistant", "content": response})

        # Sidebar quick actions
        with st.sidebar:
            if st.button("🔄 Clear Chat"):
                st.session_state.chat_messages = []
                st.rerun()
