"""Planning agent that analyzes user prompts and suggests required agents."""

import json
import re
from typing import Any

from personal_ai_system.gemini_client import GeminiClient


class PlanningAgent:
    """Agent that analyzes requirements and plans agent creation."""

    def __init__(self, gemini_client: GeminiClient):
        """Initialize the planning agent.

        Args:
            gemini_client: Gemini client for LLM interactions
        """
        self.gemini_client = gemini_client

    def analyze_prompt(self, user_prompt: str) -> dict[str, Any]:
        """Analyze user prompt and suggest required agents.

        Args:
            user_prompt: User's requirement description

        Returns:
            Dictionary containing suggested agents, tools, and MCPs
        """
        planning_prompt = f"""
You are a planning agent that analyzes user requirements and suggests specialized AI agents.

User Requirement:
{user_prompt}

Based on this requirement, analyze and provide:
1. List of specialized agents needed (with names, descriptions, and purposes)
2. Tools each agent should have access to
3. MCP (Model Context Protocol) integrations needed
4. Workflow between agents

Respond ONLY with a valid JSON object in this exact format:
{{
    "analysis": "Brief analysis of the requirement",
    "suggested_agents": [
        {{
            "name": "agent_name",
            "description": "What this agent does",
            "purpose": "Why this agent is needed",
            "tools": ["tool1", "tool2"],
            "mcp_servers": ["mcp_server1"],
            "system_prompt": "System instruction for this agent"
        }}
    ],
    "workflow": "Description of how agents work together",
    "estimated_complexity": "low|medium|high"
}}

Ensure the response is valid JSON - no markdown, no extra text, just pure JSON.
"""

        try:
            response = self.gemini_client.generate_structured_output(planning_prompt)
            # Clean the response to extract JSON
            response = self._extract_json(response)
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: create a simple default structure
            return self._create_default_plan(user_prompt)
        except Exception as e:
            error_str = str(e)
            # Check for API key errors
            if "API_KEY_INVALID" in error_str or "API key not valid" in error_str:
                raise RuntimeError(
                    "Invalid API key. Please update your Gemini API key.\n"
                    "Get a new key from: https://makersuite.google.com/app/apikey\n"
                    "Then run: .\\update_api_key.ps1"
                ) from e
            elif "PERMISSION_DENIED" in error_str:
                raise RuntimeError(
                    "Generative Language API is not enabled.\n"
                    "Enable it with: gcloud services enable generativelanguage.googleapis.com"
                ) from e
            elif "QUOTA_EXCEEDED" in error_str:
                raise RuntimeError(
                    "API quota exceeded. Please wait or upgrade to a paid tier."
                ) from e
            else:
                raise RuntimeError(f"Error analyzing prompt: {e}") from e

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that might contain markdown or other formatting.

        Args:
            text: Text potentially containing JSON

        Returns:
            Cleaned JSON string
        """
        # Remove markdown code blocks
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)

        # Try to find JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0)

        return text.strip()

    def _create_default_plan(self, user_prompt: str) -> dict[str, Any]:
        """Create a default plan when JSON parsing fails.

        Args:
            user_prompt: Original user prompt

        Returns:
            Default plan structure
        """
        return {
            "analysis": f"Creating a general purpose agent for: {user_prompt[:100]}",
            "suggested_agents": [
                {
                    "name": "general_assistant",
                    "description": "General purpose assistant",
                    "purpose": "Handle user queries based on the requirement",
                    "tools": ["text_generation", "analysis"],
                    "mcp_servers": [],
                    "system_prompt": f"You are a helpful assistant. Your task is: {user_prompt}",
                }
            ],
            "workflow": "Single agent handling all tasks",
            "estimated_complexity": "medium",
        }

    def refine_plan(self, original_plan: dict[str, Any], feedback: str) -> dict[str, Any]:
        """Refine the plan based on user feedback.

        Args:
            original_plan: Original suggested plan
            feedback: User's feedback for modifications

        Returns:
            Refined plan
        """
        refinement_prompt = f"""
You are refining an agent creation plan based on user feedback.

Original Plan:
{json.dumps(original_plan, indent=2)}

User Feedback:
{feedback}

Provide an updated plan that incorporates the user's feedback. Respond ONLY with valid JSON in the same format as the original plan.
"""

        try:
            response = self.gemini_client.generate_structured_output(refinement_prompt)
            response = self._extract_json(response)
            refined_plan = json.loads(response)
            return refined_plan
        except Exception:
            # If refinement fails, return original plan
            return original_plan

    def suggest_tools_for_agent(self, agent_description: str) -> list[str]:
        """Suggest tools for a specific agent based on its description.

        Args:
            agent_description: Description of the agent's purpose

        Returns:
            List of suggested tool names
        """
        tools_prompt = f"""
Based on this agent description: "{agent_description}"

Suggest 3-5 appropriate tools from these categories:
- File operations (read_file, write_file, search_files)
- Web operations (web_search, fetch_url, scrape_page)
- Data processing (analyze_data, transform_data, validate_data)
- Communication (send_email, send_notification, create_report)
- Code operations (execute_code, test_code, debug_code)
- Database (query_db, update_db, backup_db)

Respond with a JSON array of tool names only. Example: ["tool1", "tool2", "tool3"]
"""

        try:
            response = self.gemini_client.generate_text(tools_prompt, temperature=0.3)
            response = self._extract_json(response)
            return json.loads(response)
        except Exception:
            # Default tools if suggestion fails
            return ["text_generation", "analysis", "planning"]
