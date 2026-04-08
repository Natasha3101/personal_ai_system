"""Main Streamlit application for Personal AI System."""

import uuid
from datetime import datetime

import streamlit as st

from personal_ai_system.agent_manager import AgentManager
from personal_ai_system.auth import Auth
from personal_ai_system.gemini_client import GeminiClient
from personal_ai_system.planning_agent import PlanningAgent
from personal_ai_system.yaml_storage import YAMLStorage


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex
    if "current_page" not in st.session_state:
        st.session_state.current_page = "create_agent"
    if "plan" not in st.session_state:
        st.session_state.plan = None
    if "created_agents" not in st.session_state:
        st.session_state.created_agents = []
    if "selected_agent" not in st.session_state:
        st.session_state.selected_agent = None


def login_page(auth: Auth):
    """Display login/registration page.

    Args:
        auth: Authentication instance
    """
    st.title("🤖 Personal AI Agent System")
    st.markdown("### Welcome! Please login or register to continue")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary"):
            if auth.authenticate(login_username, login_password):
                st.session_state.authenticated = True
                st.session_state.username = login_username
                st.rerun()
            else:
                st.error("Invalid username or password")

        st.info("Default credentials: username=`admin`, password=`admin123`")

    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")

        if st.button("Register"):
            if not reg_username or not reg_email or not reg_password:
                st.error("All fields are required")
            elif reg_password != reg_password_confirm:
                st.error("Passwords do not match")
            elif len(reg_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                if auth.register_user(reg_username, reg_password, reg_email):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")


def create_agent_page(planning_agent: PlanningAgent, agent_manager: AgentManager):
    """Display agent creation page.

    Args:
        planning_agent: Planning agent instance
        agent_manager: Agent manager instance
    """
    st.title("🚀 Create New AI Agent")

    st.markdown("""
    ### How it works:
    1. Describe what you want your AI agent to do
    2. Review the suggested agent plan
    3. Approve, modify, or reject the plan
    4. Your approved agents will be created and ready to use
    """)

    # User prompt input
    user_prompt = st.text_area(
        "What do you want your AI agent to do?",
        height=150,
        placeholder="Example: I need an agent that can analyze customer feedback, categorize it, and generate summary reports",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Analyze & Plan", type="primary", disabled=not user_prompt):
            with st.spinner("Analyzing your requirements..."):
                try:
                    plan = planning_agent.analyze_prompt(user_prompt)
                    st.session_state.plan = plan
                    st.session_state.user_prompt = user_prompt
                except Exception as e:
                    error_str = str(e)
                    st.error(f"❌ Error: {e}")
                    
                    # Show helpful instructions based on error type
                    if "Invalid API key" in error_str or "API_KEY_INVALID" in error_str:
                        st.warning("🔑 **API Key Issue**")
                        st.markdown("""
                        Your Gemini API key is invalid or expired. Please update it:
                        
                        **Quick Fix:**
                        1. Get a new key from: https://makersuite.google.com/app/apikey
                        2. Run in terminal: `.\\update_api_key.ps1`
                        3. Or edit `.env` file manually
                        
                        Then restart the application.
                        """)
                        st.info("📖 See **FIX_API_KEY.md** for detailed instructions")
                    elif "PERMISSION_DENIED" in error_str:
                        st.warning("⚠️ **API Not Enabled**")
                        st.code("gcloud services enable generativelanguage.googleapis.com --project=travel-agent-projecty")
                    elif "QUOTA_EXCEEDED" in error_str:
                        st.warning("📊 **Quota Exceeded**")
                        st.info("Please wait 24 hours or upgrade to a paid tier.")

    # Display plan if available
    if st.session_state.plan:
        st.divider()
        st.subheader("📋 Suggested Agent Plan")

        plan = st.session_state.plan

        # Analysis
        st.markdown(f"**Analysis:** {plan.get('analysis', 'N/A')}")
        st.markdown(f"**Complexity:** {plan.get('estimated_complexity', 'N/A').upper()}")
        st.markdown(f"**Workflow:** {plan.get('workflow', 'N/A')}")

        # Suggested agents
        st.markdown("### Suggested Agents:")
        for idx, agent in enumerate(plan.get("suggested_agents", [])):
            with st.expander(f"🤖 {agent['name']}", expanded=True):
                st.markdown(f"**Description:** {agent['description']}")
                st.markdown(f"**Purpose:** {agent['purpose']}")
                st.markdown(f"**Tools:** {', '.join(agent.get('tools', []))}")
                if agent.get("mcp_servers"):
                    st.markdown(f"**MCP Servers:** {', '.join(agent['mcp_servers'])}")
                st.code(agent.get("system_prompt", ""), language="text")

        # Action buttons
        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✅ Approve & Create", type="primary"):
                with st.spinner("Creating agents..."):
                    try:
                        created_ids = []
                        for agent_spec in plan["suggested_agents"]:
                            agent_id = agent_manager.create_agent(agent_spec, st.session_state.session_id)
                            created_ids.append(agent_id)

                        st.session_state.created_agents.extend(created_ids)
                        st.success(f"✅ Successfully created {len(created_ids)} agent(s)!")
                        st.session_state.plan = None
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error creating agents: {e}")

        with col2:
            feedback = st.text_input("Modification feedback (optional)")
            if st.button("🔄 Modify Plan"):
                if feedback:
                    with st.spinner("Refining plan..."):
                        try:
                            refined_plan = planning_agent.refine_plan(plan, feedback)
                            st.session_state.plan = refined_plan
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error refining plan: {e}")
                else:
                    st.warning("Please provide feedback for modification")

        with col3:
            if st.button("❌ Reject"):
                st.session_state.plan = None
                st.info("Plan rejected. You can enter a new prompt.")
                st.rerun()


def agent_workspace_page(agent_manager: AgentManager):
    """Display agent workspace for interaction.

    Args:
        agent_manager: Agent manager instance
    """
    st.title("💬 Agent Workspace")

    # Load agents for current session
    agents = agent_manager.list_agents(st.session_state.session_id)

    if not agents:
        st.info("No agents created yet. Go to 'Create Agent' to get started!")
        return

    # Agent selector
    col1, col2 = st.columns([3, 1])
    with col1:
        agent_names = [f"{agent['name']} ({agent['id']})" for agent in agents]
        selected = st.selectbox("Select an agent to interact with:", agent_names)

        if selected:
            # Extract agent ID
            agent_id = selected.split("(")[1].rstrip(")")
            st.session_state.selected_agent = agent_id

    with col2:
        if st.button("🔄 Refresh Agents"):
            st.rerun()

    if st.session_state.selected_agent:
        agent_id = st.session_state.selected_agent
        agent = agent_manager.get_agent(agent_id)

        if agent:
            # Display agent info
            with st.expander("ℹ️ Agent Information", expanded=False):
                st.markdown(f"**Name:** {agent['name']}")
                st.markdown(f"**Description:** {agent['description']}")
                st.markdown(f"**Purpose:** {agent['purpose']}")
                st.markdown(f"**Tools:** {', '.join(agent.get('tools', []))}")
                st.markdown(f"**Executions:** {agent.get('execution_count', 0)}")
                st.markdown(f"**Created:** {agent.get('created_at', 'N/A')}")

            # Display conversation history
            workflow = agent_manager.get_agent_workflow(agent_id)
            if workflow and workflow.get("interactions"):
                st.subheader("💭 Conversation History")
                for interaction in workflow["interactions"][-10:]:  # Show last 10
                    st.markdown(f"**You:** {interaction['prompt']}")
                    st.markdown(f"**{agent['name']}:** {interaction['response']}")
                    st.divider()

            # Chat interface
            st.subheader("💬 Chat with Agent")
            user_input = st.text_area("Your message:", height=100, key=f"user_input_{agent_id}")

            if st.button("Send", type="primary"):
                if user_input:
                    with st.spinner(f"{agent['name']} is thinking..."):
                        try:
                            response = agent_manager.execute_agent(agent_id, user_input)
                            st.rerun()  # Refresh to show new interaction
                        except Exception as e:
                            st.error(f"Error executing agent: {e}")
                else:
                    st.warning("Please enter a message")


def all_agents_page(agent_manager: AgentManager):
    """Display all agents overview.

    Args:
        agent_manager: Agent manager instance
    """
    st.title("🤖 All Agents")

    agents = agent_manager.list_agents(st.session_state.session_id)

    if not agents:
        st.info("No agents created yet.")
        return

    st.markdown(f"### You have {len(agents)} agent(s)")

    for agent in agents:
        with st.expander(f"🤖 {agent['name']}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**ID:** `{agent['id']}`")
                st.markdown(f"**Description:** {agent['description']}")
                st.markdown(f"**Purpose:** {agent['purpose']}")
                st.markdown(f"**Tools:** {', '.join(agent.get('tools', []))}")
                if agent.get("mcp_servers"):
                    st.markdown(f"**MCP Servers:** {', '.join(agent['mcp_servers'])}")
                st.markdown(f"**Executions:** {agent.get('execution_count', 0)}")
                st.markdown(f"**Status:** {agent.get('status', 'active')}")

            with col2:
                if st.button("🗑️ Delete", key=f"delete_{agent['id']}"):
                    if agent_manager.delete_agent(agent["id"]):
                        st.success("Agent deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete agent")


def main():
    """Main application entry point."""
    st.set_page_config(page_title="Personal AI System", page_icon="🤖", layout="wide")

    initialize_session_state()

    # Initialize components
    auth = Auth()

    # Check authentication
    if not st.session_state.authenticated:
        login_page(auth)
        return

    # Initialize AI components (only after authentication)
    try:
        from personal_ai_system.config import get_config
        
        config = get_config()
        gemini_client = GeminiClient(config.gemini)
        storage = YAMLStorage(config.storage)
        planning_agent = PlanningAgent(gemini_client)
        agent_manager = AgentManager(gemini_client, storage)
        
        # Display config info in debug mode
        if config.debug:
            with st.sidebar.expander("⚙️ Configuration", expanded=False):
                st.text(f"Model: {config.gemini.model_name}")
                st.text(f"Project: {config.gcp.project_id}")
                st.text(f"Region: {config.gcp.region}")
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {e}")
        st.info("Please set the GOOGLE_API_KEY environment variable with your Gemini API key.")
        st.code("export GOOGLE_API_KEY='your-api-key-here'")
        return

    # Sidebar navigation
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        st.markdown(f"**Session:** `{st.session_state.session_id[:8]}...`")
        st.divider()

        st.markdown("### Navigation")
        if st.button("🚀 Create Agent", use_container_width=True):
            st.session_state.current_page = "create_agent"
            st.rerun()

        if st.button("💬 Agent Workspace", use_container_width=True):
            st.session_state.current_page = "workspace"
            st.rerun()

        if st.button("🤖 All Agents", use_container_width=True):
            st.session_state.current_page = "all_agents"
            st.rerun()

        st.divider()

        # Agent count
        agents = agent_manager.list_agents(st.session_state.session_id)
        st.metric("Active Agents", len(agents))

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.session_id = uuid.uuid4().hex
            st.rerun()

    # Main content area
    if st.session_state.current_page == "create_agent":
        create_agent_page(planning_agent, agent_manager)
    elif st.session_state.current_page == "workspace":
        agent_workspace_page(agent_manager)
    elif st.session_state.current_page == "all_agents":
        all_agents_page(agent_manager)


if __name__ == "__main__":
    main()
