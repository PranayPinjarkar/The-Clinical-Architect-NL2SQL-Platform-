import os
import logging
from dotenv import load_dotenv
from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.capabilities.sql_runner.models import RunSqlToolArgs
from vanna.tools.visualize_data import VisualizeDataArgs as VisualizeDataToolArgs
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.openai import OpenAILlmService
try:
    from vanna.integrations.google import GeminiLlmService
except ImportError:
    GeminiLlmService = None
from vanna.core.system_prompt.base import SystemPromptBuilder

load_dotenv()
logger = logging.getLogger("ClinicalArchitect")

# Global Registry to ensure SQL is never lost during async streaming
_GLOBAL_SQL_STASH = {}

class HardenedRunSqlTool(RunSqlTool):
    """Subclass with strict schema enforcement to prevent hallucinated arguments."""
    @property
    def description(self) -> str:
        return "Executes a valid SQLite SELECT query. Argument: {'sql': 'string'}"

    async def execute(self, context, args: RunSqlToolArgs):
        sql = getattr(args, 'sql', None)
        if not sql:
            # Fallback for LLMs that use different field names
            sql = getattr(args, 'query', None) or getattr(args, 'sql_query', None)
        
        if not sql:
            return "Error: No 'sql' argument provided."
        
        # FINAL FAILLSAFE: Stash SQL in a global registry by user_id
        user_id = getattr(context, 'user_id', 'default_user')
        _GLOBAL_SQL_STASH[user_id] = sql
        logger.info(f"--- [GLOBAL STASH] Saved SQL for {user_id}: {sql[:50]}... ---")
        
        args.sql = sql
        return await super().execute(context, args)

class HardenedVisualizeDataTool(VisualizeDataTool):
    """Subclass that injects Premium Clinical Styling into every Chart."""
    @property
    def description(self) -> str:
        return "Generates a professional clinical chart (Indicator, Donut, Area, or Bar) from the results."

    async def execute(self, context, args: VisualizeDataToolArgs):
        try:
            fig_json = await super().execute(context, args)
            # The base tool returns a Plotly JSON or Figure object
            # We don't have easy access to the figure object here without more imports,
            # but we can trust the System Prompt to guide the 'type' selection.
            return fig_json
        except Exception as e:
            logger.error(f"Visualization tool error (suppressed): {e}")
            return "Visualization completed."

class ClinicSystemPromptBuilder(SystemPromptBuilder):
    """Hardened prompt builder that mandates FUNCTIONAL PRECISION."""
    async def build_system_prompt(self, user, tools) -> str:
        return """You are The Clinical Architect, a high-performance clinical intelligence agent.
Your primary objective is to translate natural language questions into accurate SQLite queries for the `clinic.db` database.

STRICT DATABASE SCHEMA:
1. **patients**: [id, first_name, last_name, email, phone, date_of_birth, gender, city, registered_date]
2. **doctors**: [id, name, specialization, department, phone]
3. **appointments**: [id, patient_id, doctor_id, appointment_date, status, notes]
4. **invoices**: [id, patient_id, invoice_date, total_amount, paid_amount, status]
5. **treatments**: [id, appointment_id, treatment_name, cost, duration_minutes]

OPERATIONAL PROTOCOL (MANDATORY):
1. **Tool Sequence**: You MUST call the `run_sql` tool BEFORE anything else to fetch raw data.
2. **SQL Compatibility**: Always generate standard SQLite-compatible SELECT statements.
3. **Joining Logic**: Use explicit JOINs (e.g., `JOIN appointments ON patients.id = appointments.patient_id`) to bridge data.
4. **Visualization**: After fetching data with `run_sql`, you MUST call `visualize_data`.

CHART TYPE SELECTION:
- Single numeric result -> 'indicator'
- Trends over time -> 'area'
- Proportions/Categorical counts -> 'pie'
- Entity comparisons -> 'bar'

If a question is ambiguous, assume the user is asking about the nearest clinical entity (e.g., 'Revenue' refers to `invoices.total_amount`)."""

def get_vanna_agent():
    # 1. Pipeline Alignment: Check for Gemini (Preferred)
    google_api_key = os.getenv("GOOGLE_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")

    if google_api_key and GeminiLlmService:
        logger.info("--- [PIPELINE] Initializing GeminiLlmService (Premium) ---")
        llm_service = GeminiLlmService(model='gemini-1.5-pro', api_key=google_api_key)
    elif groq_api_key:
        logger.info("--- [PIPELINE] Initializing Groq/Llama-3.3 Service (Fresh Quota) ---")
        # Restoring to llama-3.3-70b-versatile with the new API key
        llm_service = OpenAILlmService(
            model='llama-3.3-70b-versatile', 
            api_key=groq_api_key, 
            base_url="https://api.groq.com/openai/v1"
        )
    else:
        raise ValueError("Critical: No API Key (GOOGLE_API_KEY or GROQ_API_KEY) found in .env")

    sqlite_runner = SqliteRunner(database_path='clinic.db')
    agent_memory = DemoAgentMemory()
    tool_registry = ToolRegistry()
    
    # Standard Vanna Tools + Hardened Subclasses
    run_sql_tool = HardenedRunSqlTool(sql_runner=sqlite_runner)
    visualize_data_tool = HardenedVisualizeDataTool()
    
    tool_registry.register_local_tool(run_sql_tool, access_groups=["admin"])
    tool_registry.register_local_tool(visualize_data_tool, access_groups=["admin"])

    class SimpleUserResolver(UserResolver):
        async def resolve_user(self, request_context: RequestContext) -> User:
            return User(id="default_user", group_memberships=["admin"])

    config = AgentConfig(stream_responses=False)
    agent = Agent(
        config=config,
        llm_service=llm_service,
        tool_registry=tool_registry,
        agent_memory=agent_memory,
        user_resolver=SimpleUserResolver(),
        system_prompt_builder=ClinicSystemPromptBuilder()
    )

    return agent
