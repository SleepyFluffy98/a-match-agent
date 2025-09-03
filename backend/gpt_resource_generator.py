import json
import requests
import time
from typing import List, Dict, Any
from .models import LearningResource, SkillGap
from config import Config

class GPTResourceGenerator:
    """Generates learning resources using GPT models"""
    
    def __init__(self):
        self.config = Config()
        
    def _create_chat_headers(self) -> Dict[str, str]:
        """Create headers for Azure OpenAI Chat API requests"""
        return {
            "Content-Type": "application/json",
            "api-key": self.config.AZURE_OPENAI_API_KEY
        }
    
    def _generate_chat_response(self, messages: List[Dict[str, str]], 
                               max_tokens: int = 1000,
                               max_retries: int = 3) -> str:
        """Generate chat response using Azure OpenAI Chat Completions API"""
        # Use the deployment from config
        deployment = self.config.AZURE_OPENAI_CHAT_DEPLOYMENT or "gpt-4"
        
        # Use a stable API version that works with GPT-4
        url = f"{self.config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-01"
        
        headers = self._create_chat_headers()
        
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        print(f"Making API call to: {url}")
        print(f"Using deployment: {deployment}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Standard Chat Completions response structure
                    choices = result.get("choices", [])
                    if choices and len(choices) > 0:
                        message = choices[0].get("message", {})
                        content = message.get("content", "")
                        
                        if content and content.strip():
                            print(f"Response content length: {len(content)}")
                            return content.strip()
                    
                    print("Empty content received")
                    print(f"Full response: {json.dumps(result, indent=2)}")
                    return ""
                else:
                    error_text = response.text
                    print(f"Attempt {attempt + 1} failed with status {response.status_code}")
                    print(f"Error response: {error_text}")
                    
                    # Try to parse error JSON for more details
                    try:
                        error_json = response.json()
                        print(f"Error details: {json.dumps(error_json, indent=2)}")
                    except:
                        pass
                    
            except requests.exceptions.Timeout as e:
                print(f"Attempt {attempt + 1} failed: Request timeout after 30 seconds")
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                # Also print the response if available
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Error response body: {e.response.text}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with unexpected error: {e}")
            
            if attempt < max_retries - 1:
                print(f"Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Failed to generate chat response after {max_retries} attempts")
    
    def generate_learning_resources(self, skill_gaps: List[SkillGap], 
                                  max_resources: int = 5) -> List[LearningResource]:
        """Generate learning resources for skill gaps using Azure OpenAI Chat Completions"""
        
        # Check if Azure OpenAI is configured
        if not self.config.AZURE_OPENAI_ENDPOINT or not self.config.AZURE_OPENAI_API_KEY:
            print("Azure OpenAI not configured, using fallback resources")
            return self._get_fallback_resources(skill_gaps, max_resources)
        
        if not skill_gaps:
            return self._get_fallback_resources(skill_gaps, max_resources)

        try:
            # Prepare skill information
            skills_info = [
                {
                    "skill": gap.skill_name,
                    "current_level": gap.current_level,
                    "required_level": gap.required_level,
                    "gap": gap.gap,
                    "priority": gap.priority
                }
                for gap in skill_gaps[:3]  # Limit to top 3 skills
            ]
            
            # Create messages for chat completion
            system_message = {
                "role": "system",
                "content": """You are a learning resource expert. Generate specific, actionable learning recommendations.
                
For each skill gap provided, suggest 1-2 high-quality resources with:
- Specific course/resource names (real ones when possible)
- Brief description of what it covers
- Estimated time commitment
- Platform/provider (Coursera, Udemy, etc.)

Keep responses concise and practical."""
            }
            
            # Create user message with skill gaps
            skills_text = "\n".join([
                f"- {info['skill'].replace('_', ' ').title()}: Current level {info['current_level']}, need level {info['required_level']} (Priority: {info['priority']})"
                for info in skills_info
            ])
            
            user_message = {
                "role": "user", 
                "content": f"Please recommend learning resources for these skill gaps:\n\n{skills_text}\n\nProvide {max_resources} total resources across these skills."
            }
            
            messages = [system_message, user_message]
            
            # Generate response
            response_text = self._generate_chat_response(messages, max_tokens=1200)
            
            if response_text and len(response_text.strip()) > 50:
                # Try to parse AI response
                parsed_resources = self._parse_gpt_response(response_text)
                if parsed_resources:
                    print(f"Generated {len(parsed_resources)} AI resources")
                    return parsed_resources[:max_resources]
            
            print("AI response was empty or too short, using fallback")
            return self._get_fallback_resources(skill_gaps, max_resources)
            
        except Exception as e:
            print(f"Error generating resources with GPT: {e}")
            return self._get_fallback_resources(skill_gaps, max_resources)
    
    def _create_resource_prompt(self, skills_info: List[Dict], max_resources: int) -> str:
        """Create a very simple prompt for GPT to generate learning resources"""
        
        # Take only the first 2 skills to keep it simple
        skills_text = ", ".join([skill['skill'].replace('_', ' ') for skill in skills_info[:2]])
        
        # Ultra-simple prompt
        prompt = f"Name {min(max_resources, 3)} courses for: {skills_text}"
        
        return prompt
    
    def _parse_gpt_response(self, response_text: str) -> List[LearningResource]:
        """Parse GPT response into LearningResource objects"""
        resources = []
        
        try:
            # Check if response is empty or None
            if not response_text or not response_text.strip():
                print("Empty or None response received from GPT")
                return resources
            
            print(f"Parsing response: {response_text[:300]}...")
            
            # Parse as simple text response (most likely format)
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            
            current_title = ""
            current_description = ""
            current_url = ""
            
            for line in lines:
                # Remove common bullet points and numbering
                cleaned_line = line
                for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '-', '*', '•']:
                    if cleaned_line.startswith(prefix):
                        cleaned_line = cleaned_line[len(prefix):].strip()
                        break
                
                # If line contains "course" or "training" it's likely a title
                if any(keyword in cleaned_line.lower() for keyword in ['course', 'training', 'tutorial', 'certification', 'bootcamp']):
                    if current_title and len(resources) < 8:  # Save previous resource
                        resources.append(LearningResource(
                            title=current_title,
                            description=current_description or f"Learn {current_title.split(':')[0] if ':' in current_title else current_title}",
                            url=current_url or "https://www.coursera.org",
                            resource_type="course",
                            difficulty_level="intermediate",
                            estimated_hours=20
                        ))
                    
                    current_title = cleaned_line
                    current_description = ""
                    current_url = ""
                
                # If line contains platform names, try to extract URL
                elif any(platform in cleaned_line.lower() for platform in ['coursera', 'udemy', 'pluralsight', 'edx', 'linkedin']):
                    if 'coursera' in cleaned_line.lower():
                        current_url = "https://www.coursera.org"
                    elif 'udemy' in cleaned_line.lower():
                        current_url = "https://www.udemy.com"
                    elif 'pluralsight' in cleaned_line.lower():
                        current_url = "https://www.pluralsight.com"
                    elif 'edx' in cleaned_line.lower():
                        current_url = "https://www.edx.org"
                    elif 'linkedin' in cleaned_line.lower():
                        current_url = "https://www.linkedin.com/learning"
                    
                    if not current_description:
                        current_description = cleaned_line
                
                # Otherwise treat as description
                elif cleaned_line and len(cleaned_line) > 20:
                    if not current_description:
                        current_description = cleaned_line
            
            # Add the last resource
            if current_title and len(resources) < 8:
                resources.append(LearningResource(
                    title=current_title,
                    description=current_description or f"Learn {current_title.split(':')[0] if ':' in current_title else current_title}",
                    url=current_url or "https://www.coursera.org",
                    resource_type="course",
                    difficulty_level="intermediate",
                    estimated_hours=20
                ))
            
            print(f"Successfully parsed {len(resources)} resources from AI response")
            return resources
            
        except Exception as e:
            print(f"Error parsing GPT response: {e}")
            return resources
                    

            
        return resources
    
    def _get_fallback_resources(self, skill_gaps: List[SkillGap], max_resources: int) -> List[LearningResource]:
        """Generate fallback resources when GPT is not available"""
        
        fallback_resources = []
        
        # Common resource templates
        resource_templates = {
            "python": [
                {
                    "title": "Python for Everybody Specialization",
                    "provider": "Coursera",
                    "type": "specialization",
                    "level": "beginner",
                    "url": "https://coursera.org/specializations/python"
                },
                {
                    "title": "Complete Python Bootcamp",
                    "provider": "Udemy", 
                    "type": "course",
                    "level": "intermediate",
                    "url": "https://udemy.com/complete-python-bootcamp"
                }
            ],
            "javascript": [
                {
                    "title": "JavaScript: The Complete Guide",
                    "provider": "Udemy",
                    "type": "course", 
                    "level": "beginner",
                    "url": "https://udemy.com/javascript-complete-guide"
                },
                {
                    "title": "freeCodeCamp JavaScript Algorithms",
                    "provider": "freeCodeCamp",
                    "type": "tutorial",
                    "level": "intermediate",
                    "url": "https://freecodecamp.org/learn/javascript-algorithms-and-data-structures"
                }
            ],
            "machine_learning": [
                {
                    "title": "Machine Learning Specialization",
                    "provider": "Coursera",
                    "type": "specialization",
                    "level": "intermediate",
                    "url": "https://coursera.org/specializations/machine-learning-introduction"
                }
            ],
            "project_management": [
                {
                    "title": "Google Project Management Certificate",
                    "provider": "Coursera",
                    "type": "certification",
                    "level": "beginner",
                    "url": "https://coursera.org/professional-certificates/google-project-management"
                }
            ]
        }
        
        # Generate resources based on skill gaps
        resource_id = 1
        for gap in skill_gaps[:max_resources]:
            skill_name = gap.skill_name
            
            # Find matching templates
            templates = resource_templates.get(skill_name, [])
            
            if templates:
                for template in templates[:1]:  # One per skill
                    fallback_resources.append(LearningResource(
                        id=f"fallback_{resource_id}",
                        title=template["title"],
                        type=template["type"],
                        provider=template["provider"],
                        duration="Variable",
                        skills=[skill_name],
                        level=template["level"],
                        url=template["url"],
                        description=f"Learn {skill_name} with this comprehensive resource",
                        rating=4.0,
                        price="Variable",
                        is_internal=False
                    ))
                    resource_id += 1
            else:
                # Generic resource
                fallback_resources.append(LearningResource(
                    id=f"fallback_{resource_id}",
                    title=f"Learn {skill_name.replace('_', ' ').title()}",
                    type="course",
                    provider="Online Learning Platform",
                    duration="4-6 weeks",
                    skills=[skill_name],
                    level="intermediate" if gap.current_level > 0 else "beginner",
                    url=f"https://search.google.com/search?q={skill_name.replace('_', '+')}+online+course",
                    description=f"Comprehensive {skill_name.replace('_', ' ')} learning resource",
                    rating=4.0,
                    price="Variable",
                    is_internal=False
                ))
                resource_id += 1
                
            if len(fallback_resources) >= max_resources:
                break
        
        return fallback_resources
    
    def generate_skill_specific_resources(self, skill_name: str, 
                                        current_level: int = 0,
                                        target_level: int = 3,
                                        max_resources: int = 3) -> List[LearningResource]:
        """Generate resources for a specific skill"""
        
        # Create a mock skill gap
        skill_gap = SkillGap(
            skill_name=skill_name,
            current_level=current_level,
            required_level=target_level,
            gap=target_level - current_level,
            priority="high"
        )
        
        return self.generate_learning_resources([skill_gap], max_resources)
