"""Configuration setup and validation script."""

import sys
from pathlib import Path


def check_env_file():
    """Check if .env file exists."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        print("❌ .env file not found!")
        print("\n📝 Creating .env file from template...")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file")
            print("\n⚠️  Please edit .env and add your credentials:")
            print("   - GOOGLE_API_KEY")
            print("   - GCP_PROJECT_ID")
            print("   - GCP_PROJECT_NAME")
            print("   - GEMINI_MODEL (optional)")
            return False
        else:
            print("❌ .env.example template not found!")
            return False
    return True


def validate_config():
    """Validate configuration."""
    print("🔍 Validating configuration...\n")

    try:
        from personal_ai_system.config import get_config

        config = get_config()

        # Check Gemini API key
        if config.gemini.api_key and config.gemini.api_key != "your-gemini-api-key-here":
            print(f"✅ Gemini API Key: Found")
        else:
            print("❌ Gemini API Key: Not configured")
            print("   Get your key from: https://makersuite.google.com/app/apikey")

        # Check model name
        print(f"✅ Gemini Model: {config.gemini.model_name}")

        # Check GCP settings
        if config.gcp.project_id and config.gcp.project_id != "your-gcp-project-id":
            print(f"✅ GCP Project ID: {config.gcp.project_id}")
        else:
            print("⚠️  GCP Project ID: Not configured (optional for local use)")

        if config.gcp.project_name and config.gcp.project_name != "your-gcp-project-name":
            print(f"✅ GCP Project Name: {config.gcp.project_name}")
        else:
            print("⚠️  GCP Project Name: Not configured (optional for local use)")

        print(f"✅ GCP Service Name: {config.gcp.service_name}")
        print(f"✅ GCP Region: {config.gcp.region}")

        # Check storage
        print(f"✅ Storage Directory: {config.storage.base_dir}")

        # Create directories
        from personal_ai_system.yaml_storage import YAMLStorage

        storage = YAMLStorage(config.storage)
        print(f"✅ Created/verified data directories")

        # Test Gemini connection
        print("\n🧪 Testing Gemini API connection...")
        from personal_ai_system.gemini_client import GeminiClient

        client = GeminiClient(config.gemini)
        try:
            response = client.generate_text("Say 'Hello' in one word", temperature=0.3)
            if response:
                print(f"✅ Gemini API connection successful!")
                print(f"   Response: {response.strip()}")
        except Exception as e:
            print(f"❌ Gemini API connection failed: {e}")
            return False

        print("\n" + "=" * 50)
        print("🎉 Configuration is valid!")
        print("=" * 50)
        print("\nYou can now run the application:")
        print("  python run_app.py")
        print("  or")
        print("  streamlit run src/personal_ai_system/app.py")
        print("\nDefault login credentials:")
        print("  Username: admin")
        print("  Password: admin123")

        return True

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def main():
    """Main setup function."""
    print("\n" + "=" * 50)
    print("🤖 Personal AI Agent System - Setup")
    print("=" * 50 + "\n")

    # Check Python version
    if sys.version_info < (3, 12):
        print(f"❌ Python 3.12+ required, you have {sys.version_info.major}.{sys.version_info.minor}")
        return 1

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # Check .env file
    if not check_env_file():
        return 1

    # Validate configuration
    if not validate_config():
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
