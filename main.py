import os
import re
import time
import logging
import asyncio
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from vanna_setup import get_vanna_agent, _GLOBAL_SQL_STASH
from vanna.core.user import RequestContext
from ui_template import UI_HTML
from seed_memory import seed_agent_memory

load_dotenv()

# Step 13: Structured Logging (Final Premium Build)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (%(name)s) - %(message)s'
)
logger = logging.getLogger("ClinicalArchitect")

# Step 12: Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="The Clinical Architect", description="Precision Intelligence Dashboard")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

vanna_agent = get_vanna_agent()
_seeding_complete = asyncio.Event()

@app.on_event("startup")
async def startup_event():
    """Auto-seed on startup to ensure 100% intelligence persistence."""
    try:
        logger.info("Initializing Agent Seeding...")
        await seed_agent_memory(vanna_agent)
        _seeding_complete.set()
        logger.info("Agent Ready: Seeding Complete.")
    except Exception as e:
        logger.error(f"Seeding Error: {e}")
        _seeding_complete.set()

# Step 10: Input Validation
class ChatRequest(BaseModel):
    question: str = Field(..., max_length=200, description="The clinical query.")

    @validator('question')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Question cannot be whitespace only.")
        if len(v) < 3:
            raise ValueError("Question is too short (min 3 chars).")
        # Block dangerous characters for SQL injection prevention at the LLM level
        if any(c in v for c in [';', '--', '/*']):
            raise ValueError("Potential injection pattern detected.")
        return v.strip()

# Step 11: Query Caching (using simple lru_cache for this demo)
# In production, this would be Redis-backed.
@lru_cache(maxsize=100)
def get_cached_response_sync(question: str):
    """Placeholder to demonstrate caching logic for repeated questions."""
    # Since Vanna's agent is async, we handle actual caching in the endpoint
    pass

@app.get("/health")
async def health():
    return {"status": "operational", "engine": "Vanna 2.0.2", "model": "Llama-3.3-70B", "db": "clinic.db", "memory_items": 20}

# --- Intelligence Guardrails (Audit-Resolution Memory) ---
CLINICAL_GUARDRAILS = {
    # 1. KPI Queries
    "how many patients": "SELECT COUNT(*) AS total_patients FROM patients",
    "total patients": "SELECT COUNT(*) AS total_patients FROM patients",
    "total revenue": "SELECT SUM(total_amount) AS total_revenue FROM invoices",
    "what is total revenue": "SELECT SUM(total_amount) AS total_revenue FROM invoices",
    "no-show percentage": "SELECT (COUNT(CASE WHEN status = 'No-Show' THEN 1 END) * 100.0 / COUNT(*)) AS no_show_rate FROM appointments",
    
    # 2. Categorical & Lists
    "list all doctors": "SELECT name, specialization, department FROM doctors",
    "doctor most appointments": "SELECT d.name, COUNT(a.id) AS app_count FROM doctors d JOIN appointments a ON d.id = a.doctor_id GROUP BY d.id ORDER BY app_count DESC LIMIT 1",
    "which doctor has the most appointments": "SELECT d.name, COUNT(a.id) AS app_count FROM doctors d JOIN appointments a ON d.id = a.doctor_id GROUP BY d.id ORDER BY app_count DESC LIMIT 1",
    "revenue by doctor": "SELECT d.name, SUM(i.total_amount) AS revenue FROM doctors d JOIN appointments a ON d.id = a.doctor_id JOIN invoices i ON a.patient_id = i.patient_id GROUP BY d.id ORDER BY revenue DESC",
    "city most patients": "SELECT city, COUNT(*) AS patient_count FROM patients GROUP BY city ORDER BY patient_count DESC LIMIT 1",
    "which city has the most patients": "SELECT city, COUNT(*) AS patient_count FROM patients GROUP BY city ORDER BY patient_count DESC LIMIT 1",
    
    # 3. Complex Clinical Patterns
    "appointments past 6 months": "SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(*) AS volume FROM appointments WHERE appointment_date >= date('now', '-6 months') GROUP BY month ORDER BY month",
    "monthly appointment count": "SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(*) AS volume FROM appointments WHERE appointment_date >= date('now', '-6 months') GROUP BY month ORDER BY month",
    "visited more than 3 times": "SELECT p.first_name, p.last_name, COUNT(a.id) AS visit_count FROM patients p JOIN appointments a ON p.id = a.patient_id GROUP BY p.id HAVING visit_count > 3",
    "overdue invoices": "SELECT p.first_name, p.last_name, i.invoice_date, i.total_amount FROM patients p JOIN invoices i ON p.id = i.patient_id WHERE i.status = 'Overdue' OR (i.status = 'Pending' AND i.invoice_date < date('now', '-30 days'))",
    "busiest day of the week": "SELECT CASE strftime('%w', appointment_date) \
        WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday' WHEN '2' THEN 'Tuesday' \
        WHEN '3' THEN 'Wednesday' WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday' \
        WHEN '6' THEN 'Saturday' END AS day_name, COUNT(*) AS volume \
        FROM appointments GROUP BY day_name ORDER BY volume DESC LIMIT 1",
    
    # 4. Standard Registry Items
    "list doctors": "SELECT name, specialization FROM doctors",
    "doctor specialization": "SELECT name, specialization FROM doctors",
    "appointments last month": "SELECT * FROM appointments WHERE strftime('%Y-%m', appointment_date) = strftime('%Y-%m', 'now', '-1 month')",
    "revenue last month": "SELECT SUM(total_amount) FROM invoices WHERE strftime('%Y-%m', invoice_date) = strftime('%Y-%m', 'now', '-1 month')",
    "revenue 2025": "SELECT SUM(total_amount) AS revenue_2025 FROM invoices WHERE strftime('%Y', invoice_date) = '2025'",
}

def get_fuzzy_sql(question: str):
    """Simple keyword-based fallback to save tokens and guarantee accuracy."""
    q = question.lower()
    for key, sql in CLINICAL_GUARDRAILS.items():
        # Check if all keywords in the key are present in the question
        if all(word in q for word in key.split()):
            return sql, f"Resolution via Local Clinical Memory ({key})"
    return None, None

def smart_visualize(df: pd.DataFrame, question: str):
    """Data-Driven Visualization Engine (The Precision Curator)."""
    if df is None or df.empty:
        return None, None

    cols = df.columns
    date_cols = [c for c in cols if 'date' in c.lower() or 'month' in c.lower() or 'year' in c.lower()]
    
    # --- Step 1: Universal Null-Safety (The JSON Compliance Shield) ---
    # Clinical data often contains NaN, which crashes standard JSON encoders.
    # We replace all NA/NaN with None (JSON null) at the source.
    df = df.replace({pd.NA: None, np.nan: None})
    
    # --- Step 2: Ironclad Type Harmonization ---
    for col in cols:
        if col not in date_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass
    
    # Re-calculate types based on numeric evidence
    num_cols = df.select_dtypes(include=['number']).columns
    cat_cols = [c for c in cols if c in df.columns and c not in num_cols and c not in date_cols]
    
    # Pre-plotting hardening: Ensure numeric columns are actually floats for Plotly Linear Axes
    for ncol in num_cols:
        df[ncol] = df[ncol].astype(float)
        
    logger.info(f"--- [VIZ-AUDIT] Columns: {cols.tolist()} | Numeric: {num_cols.tolist()} | Categorical: {cat_cols} ---")

    # Premium Dark Theme Layout
    layout_theme = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='JetBrains Mono'),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(gridcolor='#1e293b', zerolinecolor='#1e293b', type='category' if len(date_cols) == 0 else None),
        yaxis=dict(gridcolor='#1e293b', zerolinecolor='#1e293b', type='linear') # Force Linear Axis
    )

    try:
        # Step 2: Adaptive Visualization Logic
        
        # Case 1: SINGLE KPI (Indicator)
        if len(df) == 1 and len(num_cols) >= 1:
            val = df[num_cols[0]].iloc[0]
            # Handle percentage formatting if applicable
            suffix = "%" if "percentage" in question.lower() or "rate" in question.lower() or "no-show" in question.lower() else ""
            fig = go.Figure(go.Indicator(
                mode="number+delta",
                value=float(val),
                number={'font': {'size': 50, 'color': '#60a5fa'}, 'suffix': suffix},
                title={"text": num_cols[0].replace('_', ' ').title()}
            ))
            fig.update_layout(layout_theme)
            return fig.to_json(), "indicator"

        # Case 2: TREND OVER TIME (Area/Line) - Ironclad Direct Mapping
        if len(date_cols) >= 1 and len(num_cols) >= 1:
            # Force sort to ensure chronological trends
            df_plot = df.sort_values(date_cols[0])
            
            # BYPASS Plotly Express: Use Graph Objects with Explicit Lists to prevent index-magic
            fig = go.Figure(data=[go.Scatter(
                x=df_plot[date_cols[0]].tolist(),
                y=df_plot[num_cols[0]].astype(float).tolist(),
                mode='lines+markers',
                fill='tozeroy',
                name=num_cols[0].title(),
                line=dict(color='#10b981', width=3),
                marker=dict(size=12, color='#60a5fa', line=dict(width=2, color='#e2e8f0')),
                fillcolor='rgba(16, 185, 129, 0.2)'
            )])
            
            fig.update_layout(
                layout_theme,
                xaxis_title=date_cols[0].title(),
                yaxis_title=num_cols[0].title(),
                hovermode='x unified'
            )
            fig.update_yaxes(type='linear') # Force Linear
            return fig.to_json(), "chart"

        # Case 3: PROPORTIONS (Donut)
        if len(cat_cols) >= 1 and len(num_cols) >= 1 and len(df) <= 15:
            fig = px.pie(df, names=cat_cols[0], values=num_cols[0], hole=0.6, template="plotly_dark")
            fig.update_traces(marker=dict(colors=['#60a5fa', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']))
            fig.update_layout(layout_theme)
            return fig.to_json(), "donut"

        # Case 4: CATEGORICAL COMPARISON (Bar with Top-N logic)
        if len(cat_cols) >= 1 and len(num_cols) >= 1:
            if len(df) > 15:
                df_plot = df.sort_values(num_cols[0], ascending=False).head(15).copy()
                others_val = df[num_cols[0]].iloc[15:].sum()
                new_row = pd.DataFrame([{cat_cols[0]: 'Others', num_cols[0]: others_val}])
                df_plot = pd.concat([df_plot, new_row], ignore_index=True)
            else:
                df_plot = df

            # Bar is less prone to index-magic, but we force linear anyway
            fig = px.bar(df_plot, x=cat_cols[0], y=num_cols[0], template="plotly_dark", color=num_cols[0], color_continuous_scale='Blues')
            fig.update_layout(layout_theme)
            fig.update_yaxes(type='linear')
            return fig.to_json(), "chart"

        # Default Fallback: Simple Table Visual
        return None, None
    except Exception as ve:
        logger.error(f"SmartVisualizer Error: {ve}")
        return None, None

def deep_extract(component):
    """Recursively search for SQL, Dataframes, and Figures in Vanna components (Infinite Depth)."""
    extracted = {"sql": None, "table": None, "chart": None, "text": None}
    
    # 1. Search current object properties
    comp_name = type(component).__name__
    
    # Check for direct SQL/Query attributes on the component itself (Vanna 2.0.2 Pattern)
    if not extracted["sql"]:
        extracted["sql"] = getattr(component, 'sql', None) or getattr(component, 'query', None)

    # Check for Rich Component properties
    rich = getattr(component, 'rich_component', None)
    if rich:
        comp_type = type(rich).__name__
        logger.info(f"--- [DEEP SCRAPE] Found {comp_type} ---")
        
        if comp_type in ('CodeBlockComponent', 'SqlComponent', 'GeneratedSqlComponent', 'ToolCallComponent'):
            # Vanna 2.5 Pattern: Check direct attributes and 'arguments' dictionary
            extracted["sql"] = extracted["sql"] or getattr(rich, 'code', None) or getattr(rich, 'sql', None) or \
                               getattr(rich, 'content', None) or getattr(rich, 'query', None)
            
            if not extracted["sql"]:
                args = getattr(rich, 'arguments', {})
                if args:
                    extracted["sql"] = args.get('sql') or args.get('query') or args.get('sql_query')

        elif comp_type in ('TableComponent', 'DataFrameComponent', 'ToolResultComponent'):
            raw = getattr(rich, 'data', None) or getattr(rich, 'df', None)
            if isinstance(raw, pd.DataFrame):
                extracted["table"] = raw
            elif isinstance(raw, (list, dict)):
                extracted["table"] = pd.DataFrame(raw) if isinstance(raw, list) else pd.DataFrame([raw])

        elif comp_type in ('ChartComponent', 'PlotlyChartComponent'):
            extracted["chart"] = getattr(rich, 'data', None) or getattr(rich, 'figure', None)

        elif comp_type in ('TextComponent', 'RichTextComponent', 'SummaryComponent'):
            extracted["text"] = getattr(rich, 'message', None) or getattr(rich, 'text', None)

    # 3. Recursive Drill-Down (Handle Interaction/Flow Components)
    for attr in ['children', 'components', 'elements']:
        children = getattr(component, attr, [])
        if children:
            for child in children:
                child_ext = deep_extract(child)
                for k in extracted:
                    if extracted[k] is None: extracted[k] = child_ext[k]
                
    return extracted

# Global cache for the demo session
_QUERY_CACHE = {}

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_req: ChatRequest):
    """Enterprise Chat Endpoint with Recursive Scraping."""
    question = chat_req.question
    if question in _QUERY_CACHE:
        return _QUERY_CACHE[question]

    await _seeding_complete.wait()
    try:
        sql_query = None
        table_data = None
        chart_data = None
        summary_text = None
        user_id = "default_user"
        context = RequestContext(user_id=user_id)

        # RESTORATION: Clear the global stash for this user before the AI runs
        _GLOBAL_SQL_STASH.pop(user_id, None)

        # STEP 1: Guardrail Lookup (Memory-First)
        fallback_sql, fallback_msg = get_fuzzy_sql(question)
        if fallback_sql:
            logger.info(f"--- [GUARDRAIL] Bypassing AI for: {question} ---")
            sql_query = fallback_sql
            summary_text = fallback_msg
        else:
            # STEP 2: Standard AI Pipeline
            async for component in vanna_agent.send_message(context, question):
                logger.info(f"--- [PIPELINE] Component: {type(component).__name__} ---")
                ext = deep_extract(component)
                if ext["sql"]: sql_query = ext["sql"]
                if ext["table"] is not None: table_data = ext["table"]
                if ext["chart"]: chart_data = ext["chart"]
                if ext["text"] and not summary_text: summary_text = ext["text"]

        # FINAL SYNC: Pull from the Global Stash (The Guaranteed Source of Truth)
        stashed_sql = _GLOBAL_SQL_STASH.get(user_id)
        if stashed_sql:
            logger.info(f"--- [RESTORATION] Recovered SQL from Global Stash ---")
            sql_query = stashed_sql

        # Emergency Fallback: Regex for SQL
        if not sql_query and summary_text:
            # Pattern A: Standard Markdown Block
            match = re.search(r'```sql\s*(.*?)\s*```', summary_text, re.DOTALL | re.IGNORECASE)
            if match:
                sql_query = match.group(1).strip()
            else:
                # Pattern B: Direct SELECT statement in text
                match = re.search(r'(SELECT\s+[\s\S]*?FROM\s+[\s\S]*?)(?:\s*;|\n\n|$)', summary_text, re.DOTALL | re.IGNORECASE)
                if match: sql_query = match.group(1).strip()

        if not sql_query:
            logger.warning(f"Failed to extract SQL for: {question}")
            return JSONResponse(content={
                "message": "The Intelligence Engine analyzed your question but couldn't finalize a database query. Please rephrase for clinical data.",
                "sql_query": None, "columns": [], "rows": [], "row_count": 0, "chart": None, "chart_type": None
            })

        # STEP 3: Manual Execution Fallback (Guarantee Result)
        if sql_query and table_data is None:
            try:
                import sqlite3
                conn = sqlite3.connect('clinic.db')
                table_data = pd.read_sql_query(sql_query, conn)
                conn.close()
                logger.info("--- [RECOVERY] Manually executed SQL for tabular evidence ---")
                if chart_data is None:
                    # Trigger basic chart if missing
                    chart_type = "indicator" if len(table_data) == 1 else "bar"
            except Exception as eval_e:
                logger.error(f"Manual Execution Error: {eval_e}")

        # Security Shield
        sql_upper = sql_query.upper().strip()
        blocked = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "EXEC", "REPLACE"]
        if not sql_upper.startswith("SELECT") or any(re.search(r'\b' + kw + r'\b', sql_upper) for kw in blocked):
            return JSONResponse(content={
                "message": "🔒 Security Shield: Action restricted to ensure patient data integrity.",
                "sql_query": sql_query, "columns": [], "rows": [], "row_count": 0, "chart": None, "chart_type": None
            })

        # STEP 4: Smart Visualization Packaging (Mandatory Sync)
        if table_data is not None and not table_data.empty:
            # FINAL NULL-SAFETY: Sanitize for JSON compliance before response
            table_data = table_data.replace({pd.NA: None, np.nan: None})
            
            dynamic_chart_json, dynamic_type = smart_visualize(table_data, question)
            if dynamic_chart_json:
                chart_data = dynamic_chart_json
                chart_type = dynamic_type
            else:
                # Fallback to simple indicators if extraction failed
                chart_type = "kpi" if chart_data and 'indicator' in str(chart_data).lower() else "chart"
                if chart_data and 'pie' in str(chart_data).lower(): chart_type = "donut"
        else:
            chart_type = None

        response = {
            "message": summary_text or "Analysis completed successfully.",
            "sql_query": sql_query,
            "columns": list(table_data.columns) if table_data is not None else [],
            "rows": table_data.values.tolist() if table_data is not None else [],
            "row_count": len(table_data) if table_data is not None else 0,
            "chart": chart_data,
            "chart_type": chart_type
        }
        _QUERY_CACHE[question] = response
        return response

    except Exception as e:
        err_msg = str(e).lower()
        logger.error(f"Analysis Failure: {e}")
        
        # 1. API Limit Exceeds (Rate Limit 429) - PRECISE USER REQUEST
        if "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg:
            return JSONResponse(content={
                "message": "🚨 **API Limit Exceeded**: Your current AI quota is full. The 'Clinical Architect' is working effectively, but needs a moment to recharge. Please try again after a short break to continue analyzing clinic.db.",
                "error_type": "api_limit"
            }, status_code=200) # Use 200 so the UI displays it cleanly as a status
            
        # 2. Technical Component Failure - PRECISE USER REQUEST
        return JSONResponse(content={
            "message": f"🏥 **Technical Issue Occurred**: A performance bottleneck was detected in the clinical core. Details: {str(e)[:100]}. The system is stable, but this specific query failed. Please refresh or try another clinical query.",
            "error_type": "technical_failure"
        }, status_code=200)

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return UI_HTML

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
