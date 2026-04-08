"""YAML storage handler for agent configurations and workflows."""

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from personal_ai_system.config import StorageConfig


class YAMLStorage:
    """Handles YAML storage and retrieval for agents and workflows."""

    def __init__(self, config: StorageConfig | None = None):
        """Initialize YAML storage.

        Args:
            config: Storage configuration, uses default if None
        """
        if config is None:
            config = StorageConfig()
        
        self.base_dir = Path(config.base_dir)
        self.agents_dir = self.base_dir / "agents"
        self.sessions_dir = self.base_dir / "sessions"
        self.workflows_dir = self.base_dir / "workflows"

        # Create directories if they don't exist
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

    def save_agent(self, agent_id: str, agent_config: dict[str, Any]) -> Path:
        """Save agent configuration to YAML.

        Args:
            agent_id: Unique identifier for the agent
            agent_config: Agent configuration dictionary

        Returns:
            Path to the saved YAML file
        """
        agent_config["metadata"] = {
            **agent_config.get("metadata", {}),
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }

        file_path = self.agents_dir / f"{agent_id}.yaml"
        with open(file_path, "w") as f:
            yaml.dump(agent_config, f, default_flow_style=False, sort_keys=False)

        return file_path

    def load_agent(self, agent_id: str) -> dict[str, Any] | None:
        """Load agent configuration from YAML.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Agent configuration dictionary or None if not found
        """
        file_path = self.agents_dir / f"{agent_id}.yaml"
        if not file_path.exists():
            return None

        with open(file_path) as f:
            return yaml.safe_load(f)

    def update_agent(self, agent_id: str, updates: dict[str, Any]) -> bool:
        """Update existing agent configuration.

        Args:
            agent_id: Unique identifier for the agent
            updates: Dictionary of updates to apply

        Returns:
            True if successful, False if agent not found
        """
        agent_config = self.load_agent(agent_id)
        if not agent_config:
            return False

        agent_config.update(updates)
        agent_config["metadata"]["last_updated"] = datetime.now().isoformat()

        self.save_agent(agent_id, agent_config)
        return True

    def list_agents(self) -> list[str]:
        """List all saved agents.

        Returns:
            List of agent IDs
        """
        return [f.stem for f in self.agents_dir.glob("*.yaml")]

    def save_session(self, session_id: str, session_data: dict[str, Any]) -> Path:
        """Save session data to YAML.

        Args:
            session_id: Unique identifier for the session
            session_data: Session data dictionary

        Returns:
            Path to the saved YAML file
        """
        session_data["metadata"] = {
            **session_data.get("metadata", {}),
            "session_id": session_id,
            "last_updated": datetime.now().isoformat(),
        }

        file_path = self.sessions_dir / f"{session_id}.yaml"
        with open(file_path, "w") as f:
            yaml.dump(session_data, f, default_flow_style=False, sort_keys=False)

        return file_path

    def load_session(self, session_id: str) -> dict[str, Any] | None:
        """Load session data from YAML.

        Args:
            session_id: Unique identifier for the session

        Returns:
            Session data dictionary or None if not found
        """
        file_path = self.sessions_dir / f"{session_id}.yaml"
        if not file_path.exists():
            return None

        with open(file_path) as f:
            return yaml.safe_load(f)

    def save_workflow(self, agent_id: str, workflow_data: dict[str, Any]) -> Path:
        """Save workflow data for an agent.

        Args:
            agent_id: Unique identifier for the agent
            workflow_data: Workflow data including prompts and execution history

        Returns:
            Path to the saved YAML file
        """
        workflow_data["metadata"] = {
            **workflow_data.get("metadata", {}),
            "agent_id": agent_id,
            "last_updated": datetime.now().isoformat(),
        }

        file_path = self.workflows_dir / f"{agent_id}_workflow.yaml"
        with open(file_path, "w") as f:
            yaml.dump(workflow_data, f, default_flow_style=False, sort_keys=False)

        return file_path

    def load_workflow(self, agent_id: str) -> dict[str, Any] | None:
        """Load workflow data for an agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Workflow data dictionary or None if not found
        """
        file_path = self.workflows_dir / f"{agent_id}_workflow.yaml"
        if not file_path.exists():
            return None

        with open(file_path) as f:
            return yaml.safe_load(f)

    def append_to_workflow(self, agent_id: str, prompt: str, response: str) -> bool:
        """Append a new interaction to the agent's workflow.

        Args:
            agent_id: Unique identifier for the agent
            prompt: User prompt
            response: Agent response

        Returns:
            True if successful, False otherwise
        """
        workflow = self.load_workflow(agent_id) or {"interactions": []}

        workflow["interactions"].append(
            {"timestamp": datetime.now().isoformat(), "prompt": prompt, "response": response}
        )

        self.save_workflow(agent_id, workflow)
        return True

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent and its associated files.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            True if successful, False if agent not found
        """
        agent_file = self.agents_dir / f"{agent_id}.yaml"
        workflow_file = self.workflows_dir / f"{agent_id}_workflow.yaml"

        deleted = False
        if agent_file.exists():
            agent_file.unlink()
            deleted = True

        if workflow_file.exists():
            workflow_file.unlink()

        return deleted
