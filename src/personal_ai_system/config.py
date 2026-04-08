"""Configuration management for Personal AI System."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class GCPConfig(BaseModel):
    """GCP-specific configuration."""

    project_id: str = Field(default="", description="GCP Project ID")
    project_number: str = Field(default="", description="GCP Project Number")
    project_name: str = Field(default="", description="GCP Project Name")
    service_account: str = Field(default="", description="GCP Service Account email")
    service_account_name: str = Field(default="", description="GCP Service Account name")
    service_name: str = Field(default="personal-ai-system", description="Service name for deployment")
    region: str = Field(default="us-central1", description="GCP region")


class GeminiConfig(BaseModel):
    """Gemini API configuration."""

    api_key: str = Field(..., description="Google Gemini API key")
    model_name: str = Field(default="gemini-1.5-pro", description="Gemini model to use")
    temperature: float = Field(default=0.7, description="Default temperature for generation")
    max_tokens: int | None = Field(default=None, description="Maximum tokens for generation")


class StorageConfig(BaseModel):
    """Storage configuration."""

    base_dir: str = Field(default="data", description="Base directory for data storage")
    agents_dir: str = Field(default="data/agents", description="Directory for agent configs")
    sessions_dir: str = Field(default="data/sessions", description="Directory for session data")
    workflows_dir: str = Field(default="data/workflows", description="Directory for workflows")
    users_file: str = Field(default="data/users.yaml", description="Path to users file")


class AppConfig(BaseModel):
    """Main application configuration."""

    gcp: GCPConfig = Field(default_factory=GCPConfig)
    gemini: GeminiConfig
    storage: StorageConfig = Field(default_factory=StorageConfig)
    debug: bool = Field(default=False, description="Enable debug mode")

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables.

        Returns:
            AppConfig instance

        Raises:
            ValueError: If required configuration is missing
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            msg = "GOOGLE_API_KEY environment variable is required"
            raise ValueError(msg)

        return cls(
            gcp=GCPConfig(
                project_id=os.getenv("GCP_PROJECT_ID", ""),
                project_number=os.getenv("GCP_PROJECT_NUMBER", ""),
                project_name=os.getenv("GCP_PROJECT_NAME", ""),
                service_account=os.getenv("GCP_SERVICE_ACCOUNT", ""),
                service_account_name=os.getenv("GCP_SERVICE_ACCOUNT_NAME", ""),
                service_name=os.getenv("GCP_SERVICE_NAME", "personal-ai-system"),
                region=os.getenv("GCP_REGION", "us-central1"),
            ),
            gemini=GeminiConfig(
                api_key=api_key,
                model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
                temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("GEMINI_MAX_TOKENS")) if os.getenv("GEMINI_MAX_TOKENS") else None,
            ),
            storage=StorageConfig(
                base_dir=os.getenv("STORAGE_BASE_DIR", "data"),
            ),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )

    def save_to_file(self, filepath: str = "config.yaml") -> None:
        """Save configuration to a YAML file (excluding sensitive data).

        Args:
            filepath: Path to save the config file
        """
        import yaml

        config_dict = self.model_dump()
        # Remove sensitive data
        config_dict["gemini"]["api_key"] = "***REDACTED***"

        with open(filepath, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)


# Global config instance (lazy loaded)
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get the global configuration instance.

    Returns:
        AppConfig instance

    Raises:
        ValueError: If configuration cannot be loaded
    """
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def reload_config() -> AppConfig:
    """Reload configuration from environment.

    Returns:
        Reloaded AppConfig instance
    """
    global _config
    _config = AppConfig.from_env()
    return _config
