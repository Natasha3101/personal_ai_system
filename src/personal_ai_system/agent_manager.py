"""Agent manager for creating and executing AI agents."""

import uuid
from datetime import datetime
from typing import Any

from personal_ai_system.gemini_client import GeminiClient
from personal_ai_system.yaml_storage import YAMLStorage


class AgentManager:
    """Manages creation, storage, and execution of AI agents."""

    def __init__(self, gemini_client: GeminiClient, storage: YAMLStorage):
        """Initialize the agent manager.

        Args:
            gemini_client: Gemini client for LLM interactions
            storage: YAML storage handler
        """
        self.gemini_client = gemini_client
        self.storage = storage

    def create_agent(self, agent_spec: dict[str, Any], session_id: str) -> str:
        """Create a new agent based on specifications.

        Args:
            agent_spec: Agent specification from planning agent
            session_id: Current session ID

        Returns:
            Created agent ID
        """
        agent_id = f"{agent_spec['name']}_{uuid.uuid4().hex[:8]}"

        agent_config = {
            "id": agent_id,
            "name": agent_spec["name"],
            "description": agent_spec.get("description", ""),
            "purpose": agent_spec.get("purpose", ""),
            "system_prompt": agent_spec.get("system_prompt", ""),
            "tools": agent_spec.get("tools", []),
            "mcp_servers": agent_spec.get("mcp_servers", []),
            "session_id": session_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "execution_count": 0,
        }

        self.storage.save_agent(agent_id, agent_config)

        # Initialize workflow
        workflow = {
            "agent_id": agent_id,
            "interactions": [],
            "created_at": datetime.now().isoformat(),
        }
        self.storage.save_workflow(agent_id, workflow)

        return agent_id

    def execute_agent(self, agent_id: str, user_input: str) -> str:
        """Execute an agent with user input.

        Args:
            agent_id: ID of the agent to execute
            user_input: User's input/query

        Returns:
            Agent's response
        """
        # Load agent config
        agent_config = self.storage.load_agent(agent_id)
        if not agent_config:
            msg = f"Agent {agent_id} not found"
            raise ValueError(msg)

        # Load workflow history for context
        workflow = self.storage.load_workflow(agent_id) or {"interactions": []}

        # Build context from previous interactions
        context = self._build_context(workflow.get("interactions", []))

        # Create the full prompt
        full_prompt = f"""
{agent_config['system_prompt']}

Previous Context:
{context}

User Query: {user_input}

Provide a helpful and relevant response based on your purpose: {agent_config['purpose']}
"""

        # Generate response
        response = self.gemini_client.generate_text(full_prompt, temperature=0.7)

        # Update workflow
        self.storage.append_to_workflow(agent_id, user_input, response)

        # Update execution count
        agent_config["execution_count"] = agent_config.get("execution_count", 0) + 1
        agent_config["last_executed"] = datetime.now().isoformat()
        self.storage.update_agent(agent_id, agent_config)

        return response

    def _build_context(self, interactions: list[dict], max_interactions: int = 5) -> str:
        """Build context string from previous interactions.

        Args:
            interactions: List of previous interactions
            max_interactions: Maximum number of interactions to include

        Returns:
            Context string
        """
        if not interactions:
            return "No previous interactions."

        recent_interactions = interactions[-max_interactions:]
        context_parts = []

        for interaction in recent_interactions:
            context_parts.append(f"User: {interaction['prompt']}")
            context_parts.append(f"Assistant: {interaction['response']}")

        return "\n".join(context_parts)

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        """Get agent configuration.

        Args:
            agent_id: ID of the agent

        Returns:
            Agent configuration or None if not found
        """
        return self.storage.load_agent(agent_id)

    def list_agents(self, session_id: str | None = None) -> list[dict[str, Any]]:
        """List all agents, optionally filtered by session.

        Args:
            session_id: Optional session ID to filter by

        Returns:
            List of agent configurations
        """
        all_agent_ids = self.storage.list_agents()
        agents = []

        for agent_id in all_agent_ids:
            agent = self.storage.load_agent(agent_id)
            if agent:
                if session_id is None or agent.get("session_id") == session_id:
                    agents.append(agent)

        return agents

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent.

        Args:
            agent_id: ID of the agent to delete

        Returns:
            True if successful, False otherwise
        """
        return self.storage.delete_agent(agent_id)

    def get_agent_workflow(self, agent_id: str) -> dict[str, Any] | None:
        """Get agent's workflow history.

        Args:
            agent_id: ID of the agent

        Returns:
            Workflow data or None if not found
        """
        return self.storage.load_workflow(agent_id)

    def update_agent_tools(self, agent_id: str, tools: list[str]) -> bool:
        """Update tools for an agent.

        Args:
            agent_id: ID of the agent
            tools: New list of tools

        Returns:
            True if successful, False otherwise
        """
        return self.storage.update_agent(agent_id, {"tools": tools})

    def update_agent_mcp_servers(self, agent_id: str, mcp_servers: list[str]) -> bool:
        """Update MCP servers for an agent.

        Args:
            agent_id: ID of the agent
            mcp_servers: New list of MCP servers

        Returns:
            True if successful, False otherwise
        """
        return self.storage.update_agent(agent_id, {"mcp_servers": mcp_servers})
