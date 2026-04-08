"""Simple script to run the Streamlit application."""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the Streamlit app."""
    app_path = Path(__file__).parent / "src" / "personal_ai_system" / "app.py"
    port = os.environ.get("PORT", "8501")
    print("🚀 Starting Personal AI Agent System...")
    print(f"📂 App location: {app_path}")
    print("🌐 Opening browser at: http://localhost:8501")
    print("\nPress Ctrl+C to stop the server\n")

    try:
        subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            port,
            "--server.address",
            "0.0.0.0",
        ],
        check=True,
    )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
