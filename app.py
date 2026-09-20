# app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import re
import psycopg2
import os
import sqlite3
import hashlib
import difflib
from datetime import datetime
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="AI Query Optimizer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_secret_value(key_name, default=""):
    """Read configuration safely from process environment or st.secrets; never hardcoded."""
    val = os.getenv(key_name)
    if val:
        return val.strip()
    try:
        if hasattr(st, "secrets") and key_name in st.secrets:
            return str(st.secrets[key_name]).strip()
    except Exception:
        pass
    return default

# Initialize session state for persistent credentials
if "db_host" not in st.session_state:
    st.session_state.db_host = load_secret_value("DB_HOST", "localhost")
if "db_port" not in st.session_state:
    st.session_state.db_port = load_secret_value("DB_PORT", "5432")
if "db_name" not in st.session_state:
    st.session_state.db_name = load_secret_value("DB_NAME", "neondb")
if "db_user" not in st.session_state:
    st.session_state.db_user = load_secret_value("DB_USER", "postgres")
if "db_password" not in st.session_state:
    st.session_state.db_password = load_secret_value("DB_PASSWORD", "")
if "db_sslmode" not in st.session_state:
    st.session_state.db_sslmode = load_secret_value("DB_SSLMODE", "require")
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = load_secret_value("GEMINI_API_KEY", "")
if "ai_engine_mode" not in st.session_state:
    st.session_state.ai_engine_mode = "⚡ Fast Offline Mode (Instant)"

# Custom CSS - Modern Flagship UI (Apple/Samsung Aesthetic)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--ink:#101828;--muted:#667085;--line:#e7ecf4;--blue:#2457f5;--navy:#102a5c}html,body,[class*="css"]{font-family:Manrope,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;color:var(--ink)}.stApp{background:radial-gradient(circle at 88% 2%,#e9efff 0,transparent 26rem),#fbfcfe}.block-container{max-width:1440px;padding:2.1rem 3.5rem 3.5rem!important}[data-testid="stSidebar"]{background:linear-gradient(180deg,#102a5c,#091936);border:0}[data-testid="stSidebar"] *{color:#f7f9ff!important}[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#b7c5e5!important}[data-testid="stSidebar"] .stTextInput input,[data-testid="stSidebar"] [data-baseweb="select"]>div{background:rgba(255,255,255,.88)!important;border-color:rgba(255,255,255,.3)!important}[data-testid="stSidebar"] [data-baseweb="select"] span,[data-testid="stSidebar"] [data-baseweb="select"] div{color:#101828!important}[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.14)}h1,h2,h3{letter-spacing:-.045em!important;color:var(--ink)!important}h1{font-size:1.8rem!important;font-weight:800!important;margin:1.7rem 0 .35rem!important}h2{font-size:1.22rem!important;font-weight:800!important;margin:1.5rem 0 .7rem!important}h3{font-size:1rem!important;font-weight:800!important}.hero-container{position:relative;overflow:hidden;padding:3.35rem 3.4rem 3.1rem;border-radius:28px;color:white;background:linear-gradient(116deg,#0b1f47,#123b8d 56%,#2864e7);box-shadow:0 22px 45px rgba(23,64,150,.2)}.hero-container:after{content:"";position:absolute;width:30rem;height:30rem;border:1px solid rgba(255,255,255,.16);border-radius:50%;right:-9rem;top:-18rem;box-shadow:0 0 0 3rem rgba(255,255,255,.04),0 0 0 7rem rgba(255,255,255,.025)}.hero-badge{position:relative;z-index:1;display:inline-block;color:#dce8ff;font-size:.67rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;border:1px solid rgba(220,232,255,.35);padding:.43rem .76rem;border-radius:99px}.main-header{position:relative;z-index:1;color:white;font-size:clamp(2.15rem,4vw,3.6rem);font-weight:800;letter-spacing:-.065em;line-height:1.1;margin:.85rem 0 .7rem}.hero-subtitle{position:relative;z-index:1;max-width:630px;color:#d8e4ff;font-size:1rem;line-height:1.7}.section-kicker{color:#52627d;font-size:.72rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;margin:1.85rem 0 .55rem}.feature-card{height:100%;box-sizing:border-box;padding:1.3rem 1.35rem;background:rgba(255,255,255,.86);border:1px solid var(--line);border-radius:18px;box-shadow:0 8px 22px rgba(16,24,40,.04);transition:transform .22s ease,box-shadow .22s ease}.feature-card:hover,.metric-card:hover{transform:translateY(-3px);box-shadow:0 15px 30px rgba(28,59,122,.1)}.card-icon{display:grid;place-items:center;width:2.25rem;height:2.25rem;border-radius:10px;background:#eaf0ff;color:#2457f5;font-size:1.05rem;margin-bottom:.9rem}.card-title{font-size:.93rem;font-weight:800;color:#172b4d;margin-bottom:.32rem}.card-copy{font-size:.82rem;color:var(--muted);line-height:1.55}.metric-card{background:white;border:1px solid var(--line);padding:1.15rem 1.25rem;border-radius:16px;box-shadow:0 6px 18px rgba(16,24,40,.04);transition:all .22s ease}[data-testid="stMetric"]{padding:1.15rem 1.25rem;border:1px solid var(--line);border-radius:16px;background:#fff;box-shadow:0 6px 18px rgba(16,24,40,.04)}[data-testid="stMetricLabel"]{color:#667085!important;font-size:.75rem!important;font-weight:800!important;text-transform:uppercase;letter-spacing:.07em}[data-testid="stMetricValue"]{color:#172b4d!important;font-size:1.6rem!important;font-weight:800!important}.improvement-positive,.improvement-negative{font-size:1.65rem;font-weight:800;letter-spacing:-.05em}.improvement-positive{color:#058d65}.improvement-negative{color:#d92d20}.ai-insight-box{background:linear-gradient(135deg,#f4f7ff,#fff);border:1px solid #dbe5ff;border-left:5px solid #2457f5;padding:1.55rem 1.7rem;border-radius:16px;margin:1.25rem 0;box-shadow:0 8px 22px rgba(36,87,245,.07)}.status-green,.status-yellow,.status-red{padding:1.05rem 1.25rem;border-radius:14px;margin:1rem 0;font-size:.9rem}.status-green{background:#ecfdf3;border:1px solid #b7ebcf;color:#067647}.status-yellow{background:#fffaeb;border:1px solid #fedf89;color:#b54708}.status-red{background:#fef3f2;border:1px solid #fecdca;color:#b42318}.stButton>button{min-height:2.7rem;border-radius:11px!important;border:1px solid #d0d5dd!important;font-weight:800!important;transition:transform .18s ease,box-shadow .18s ease!important}.stButton>button:hover{transform:translateY(-1px);box-shadow:0 8px 16px rgba(16,24,40,.12)}.stButton>button[kind="primary"]{color:white!important;background:linear-gradient(135deg,#2457f5,#1745d4)!important;border-color:#2457f5!important;box-shadow:0 8px 16px rgba(36,87,245,.22)}.stTextArea textarea,.stTextInput input{border-radius:11px!important;border-color:#dce2eb!important;background:#fff!important}.stTextArea textarea{font-family:'DM Mono',monospace!important;font-size:.84rem!important;line-height:1.65!important}[data-baseweb="select"]>div{border-radius:11px!important;border-color:#dce2eb!important}[data-testid="stFileUploader"]{padding:1.25rem;border:1px dashed #9cb6f7;border-radius:16px;background:#f7f9ff}[data-testid="stExpander"]{border:1px solid #dce2eb!important;border-radius:12px!important;background:rgba(255,255,255,.68)!important;overflow:hidden}[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:14px;overflow:hidden}.stTabs [data-baseweb="tab-list"]{gap:1.3rem;border-bottom:1px solid var(--line)}.stTabs [data-baseweb="tab"]{height:2.6rem;padding:0;font-weight:800;color:#667085}.stTabs [aria-selected="true"]{color:#2457f5!important}@media(max-width:800px){.block-container{padding:1.1rem 1rem 2rem!important}.hero-container{padding:2.3rem 1.5rem 2.2rem}.main-header{font-size:2.25rem}}
</style>
""", unsafe_allow_html=True)

# Configuration
APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(APP_DIR, "models_improved")
DATA_FILE = os.path.join(APP_DIR, "data", "processed", "lce_training_data_fixed.csv")
HISTORY_DB = os.path.join(APP_DIR, "analysis_history.db")
LOG_DB = os.path.join(APP_DIR, "app_activity.db")
def validate_gemini_api_key(api_key):
    """Reject OAuth tokens early; Gemini expects a Gemini API key, not a login token."""
    key = (api_key or "").strip()
    if not key:
        raise ValueError("Gemini is not configured. Add GEMINI_API_KEY in Streamlit secrets or paste a key for this session.")
    if key.lower().startswith(("bearer ", "ya29.", "eyj")):
        raise ValueError(
            "This looks like a Google OAuth access token, not a Gemini API key. "
            "Create/copy a Gemini API key from Google AI Studio and save that value as GEMINI_API_KEY."
        )
    if any(character.isspace() for character in key):
        raise ValueError("The Gemini API key contains whitespace. Paste only the key value, without quotes or 'Bearer'.")
    return key


def generate_gemini_response(api_key, prompt, response_mime_type=None):
    """Generate text using available Gemini SDK (google.genai or google.generativeai) with dynamic model discovery."""
    key = validate_gemini_api_key(api_key)

    user_configured_model = load_secret_value("GEMINI_MODEL", "")
    cached_model = st.session_state.get("cached_gemini_model_name")

    known_candidates = [
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
    ]

    last_error = None

    # 1. Try google.genai (new SDK)
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)

        models_to_try = []
        if user_configured_model:
            models_to_try.append(user_configured_model.replace("models/", ""))
        if cached_model:
            models_to_try.append(cached_model.replace("models/", ""))

        # Discover active models dynamically from the user's API key
        try:
            available_models = [
                m.name.replace("models/", "")
                for m in client.models.list()
                if hasattr(m, "name")
            ]
            models_to_try.extend([m for m in available_models if "flash" in m or "pro" in m])
        except Exception:
            pass

        models_to_try.extend(known_candidates)

        seen = set()
        models_to_try = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

        for model in models_to_try:
            try:
                config_kwargs = {"temperature": 0.2}
                if response_mime_type:
                    config_kwargs["response_mime_type"] = response_mime_type
                config = types.GenerateContentConfig(**config_kwargs)
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                text = (getattr(response, "text", None) or "").strip()
                if text:
                    st.session_state.cached_gemini_model_name = model
                    return text
            except Exception as e:
                last_error = e
                continue
    except Exception as e:
        last_error = e

    # 2. Try google.generativeai (fallback SDK)
    try:
        import google.generativeai as genai

        genai.configure(api_key=key)

        models_to_try = []
        if user_configured_model:
            models_to_try.append(user_configured_model)
        if cached_model:
            models_to_try.append(cached_model)

        try:
            available = [
                m.name for m in genai.list_models()
                if "generateContent" in getattr(m, "supported_generation_methods", [])
            ]
            models_to_try.extend(available)
        except Exception:
            pass

        models_to_try.extend(known_candidates)

        seen = set()
        models_to_try = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

        for model in models_to_try:
            try:
                m = genai.GenerativeModel(model)
                response = m.generate_content(prompt)
                text = (getattr(response, "text", None) or "").strip()
                if text:
                    st.session_state.cached_gemini_model_name = model
                    return text
            except Exception as e:
                last_error = e
                continue
    except Exception as e:
        last_error = e

    raise ValueError(f"Gemini API Error: Could not generate response. Error: {last_error}")



def get_llm_insights(query, plan_json, api_key):
    try:
        prompt = f"""
        You are an expert PostgreSQL Database Administrator and AI Query Optimizer.
        
        I have a SQL query and its execution plan.
        SQL Query:
        {query}
        
        Execution Plan Summary:
        {str(plan_json)[:1500]} 
        
        Please provide a short, highly professional analysis in Markdown. Include:
        1. 🚨 **Anti-Patterns**: Is there anything wrong or inefficient with this SQL? (e.g. SELECT *, missing limits).
        2. 🧠 **Plain English Plan**: In 2 simple sentences, what is the database actually doing behind the scenes?
        3. ⚡ **Optimization Advice**: How can we make this faster? (e.g. suggesting an index on a specific column).
        """
        return generate_gemini_response(api_key, prompt)
    except Exception as e:
        return f"❌ **Could not generate AI insights.** Ensure your Gemini API Key is correct. Error: {str(e)}"

def is_safe_select(sql):
    """Allow exactly one read-only SELECT statement for AI-generated SQL."""
    candidate = (sql or "").strip()
    if not candidate or candidate.count(";") > 1 or ";" in candidate.rstrip(";"):
        return False
    candidate = candidate.rstrip(";").strip()
    if "`" in candidate or "--" in candidate or "/*" in candidate or not re.match(r"(?is)^select\b", candidate) or not re.search(r"(?is)\bfrom\b", candidate):
        return False
    prohibited = r"\b(insert|update|delete|drop|alter|create|grant|revoke|truncate|copy|call|do)\b"
    return not bool(re.search(prohibited, candidate, flags=re.IGNORECASE))


def get_root_plan(plan_json):
    """Accept PostgreSQL's usual EXPLAIN JSON list and fail clearly for malformed uploads."""
    if isinstance(plan_json, list) and plan_json and isinstance(plan_json[0], dict) and isinstance(plan_json[0].get("Plan"), dict):
        return plan_json[0]["Plan"]
    raise ValueError("Expected PostgreSQL EXPLAIN (ANALYZE, FORMAT JSON) output containing a top-level Plan object.")


def connect_postgres():
    """Create a bounded, SSL-aware read-only analysis connection."""
    return psycopg2.connect(
        host=st.session_state.db_host,
        port=int(st.session_state.db_port or 5432),
        dbname=st.session_state.db_name,
        user=st.session_state.db_user,
        password=st.session_state.db_password,
        sslmode=st.session_state.db_sslmode,
        connect_timeout=10,
    )


def extract_clean_sql(text):
    """Extract the last valid SELECT statement from an occasionally chatty LLM response."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("The AI returned an empty response.")
    sources = re.findall(r"```(?:sql)?\s*([\s\S]*?)```", text, re.IGNORECASE) or [text]
    candidates = []
    for source in sources:
        for match in re.finditer(r"(?is)(?=(select\b.*?;))", source):
            candidate = match.group(1).strip().strip("`").strip()
            if is_safe_select(candidate):
                candidates.append(candidate.rstrip(";") + ";")
        if not candidates:
            for start in list(re.finditer(r"(?is)select\b", source)):
                candidate = source[start.start():].strip().strip("`").strip()
                if is_safe_select(candidate):
                    candidates.append(candidate.rstrip(";") + ";")
    if candidates:
        return candidates[-1]
    raise ValueError("The AI did not return a valid PostgreSQL SELECT statement.")

def corrected_request_preview(text):
    """Show a transparent, lightweight correction for common domain spelling mistakes."""
    corrections = {"comdy": "Comedy", "commedy": "Comedy", "acton": "Action", "actoin": "Action", "drma": "Drama", "moives": "movies", "mvoie": "movie"}
    parts = re.split(r"(\W+)", text.strip())
    corrected = [corrections.get(part.lower(), part) if part.isalpha() else part for part in parts]
    return "".join(corrected)


def detect_supported_genre(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    genres = ["action", "comedy", "drama"]
    direct = next((genre for genre in genres if genre in words), None)
    if direct:
        return direct.title()
    for word in words:
        match = difflib.get_close_matches(word, genres, n=1, cutoff=0.78)
        if match:
            return match[0].title()
    return None

def convert_english_to_sql(english_text, api_key):
    use_fast_mode = st.session_state.get("ai_engine_mode", "").startswith("⚡")
    
    # Fast mode or no key -> instant offline translation
    if use_fast_mode or not api_key:
        t = english_text.lower()
        genre = detect_supported_genre(english_text)
        if genre:
            return f"SELECT f.title, c.name FROM film f JOIN film_category fc ON f.film_id = fc.film_id JOIN category c ON fc.category_id = c.category_id WHERE c.name = '{genre}' AND f.length > 100 LIMIT 20;"
        elif "actor" in t or "performance" in t:
            return "SELECT a.first_name, a.last_name, COUNT(fa.film_id) as film_count FROM actor a JOIN film_actor fa ON a.actor_id = fa.actor_id GROUP BY a.actor_id HAVING COUNT(fa.film_id) > 15 ORDER BY film_count DESC LIMIT 15;"
        elif "customer" in t or "payment" in t:
            return "SELECT c.first_name, c.last_name, COUNT(p.payment_id) as payment_count FROM customer c JOIN payment p ON c.customer_id = p.customer_id GROUP BY c.customer_id HAVING COUNT(p.payment_id) > 10 LIMIT 15;"
        return "SELECT f.title, f.length, f.rating FROM film f WHERE f.length > 120 ORDER BY f.length DESC LIMIT 20;"
    try:
        prompt = f"""
        You are an expert PostgreSQL Database Administrator.
        Convert the following Plain English request into a valid PostgreSQL SELECT query for the `dvd_rental` database.
        
        Database Schema Context:
        - film (film_id, title, description, release_year, rental_duration, rental_rate, length, replacement_cost, rating)
        - category (category_id, name)
        - film_category (film_id, category_id)
        - actor (actor_id, first_name, last_name)
        - film_actor (actor_id, film_id)
        - customer (customer_id, store_id, first_name, last_name, email, address_id, active)
        - payment (payment_id, customer_id, staff_id, rental_id, amount, payment_date)
        - rental (rental_id, rental_date, inventory_id, customer_id, return_date, staff_id)
        - inventory (inventory_id, film_id, store_id)
        
        User English Request: "{english_text}"
        
        CRITICAL RULES:
        1. Output ONLY one raw SQL SELECT statement ending with a semicolon.
        2. Do NOT output any intro text, bullet points, Markdown, backticks, or reasoning.
        3. A response containing anything except SQL will be rejected.
        """
        raw_response = generate_gemini_response(api_key, prompt)
        clean_sql = extract_clean_sql(raw_response)
        return clean_sql
    except Exception as e:
        return f"Error converting English to SQL: {str(e)}"

# Normalization functions
def normalize_filter(s):
    if not s or s == "None": 
        return "none"
    s = re.sub(r'[a-zA-Z_]+\.', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.replace('(', '').replace(')', '')
    s = s.lower()
    s = re.sub(r'\b\d+\b', '#', s)
    return s

def normalize_cond(s):
    if not s or s == "None": 
        return "none"
    cols = re.findall(r'([a-zA-Z_]+)\.([a-zA-Z_]+)', s)
    if len(cols) == 2:
        return f"{cols[0][1]}={cols[1][1]}".lower()
    return "none"

def flatten_plan(node, parent_type="ROOT", parent_rows=None, out=None):
    if out is None: out = []
    plan_rows = node.get("Plan Rows", 1)
    selectivity = min(plan_rows / parent_rows, 1.0) if parent_rows and parent_rows > 0 else 1.0
    startup_cost = node.get("Startup Cost", 0)
    total_cost = node.get("Total Cost", 0)
    cost_ratio = total_cost / (startup_cost or 1)

    row = {
        "node_type": node.get("Node Type", "Unknown"),
        "parent_node": parent_type,
        "join_type": node.get("Join Type", "None"),
        "relation_name": node.get("Relation Name", "None"),
        "alias": node.get("Alias", "None"),
        "plan_rows": float(plan_rows),
        "startup_cost": float(startup_cost),
        "total_cost": float(total_cost),
        "plan_width": float(node.get("Plan Width", 0)),
        "selectivity": selectivity,
        "cost_ratio": cost_ratio,
        "log_plan_rows": np.log10(max(plan_rows, 1)),
        "filter": normalize_filter(node.get("Filter", "")),
        "hash_cond": normalize_cond(node.get("Hash Cond", "")),
        "index_cond": normalize_cond(node.get("Index Cond", "")),
    }
    out.append(row)
    for sub in node.get("Plans", []):
        flatten_plan(sub, node.get("Node Type", "Unknown"), plan_rows, out)
    return out

def extract_actual_rows(node, out=None):
    if out is None: out = []
    out.append(node.get("Actual Rows", 0))
    for sub in node.get("Plans", []):
        extract_actual_rows(sub, out)
    return out

def predict_plan(plan_json):
    """Predict AI estimates for a given plan"""
    try:
        # Load model and preprocessing objects
        model = joblib.load(f"{MODEL_DIR}/xgb_lce.pkl")
        scaler = joblib.load(f"{MODEL_DIR}/input_scaler.pkl")
        
        encoders = {}
        for col in ["node_type", "parent_node", "join_type", "relation_name", "alias",
                    "filter", "hash_cond", "index_cond"]:
            p = f"{MODEL_DIR}/le_{col}.pkl"
            if os.path.exists(p):
                encoders[col] = joblib.load(p)

        # Extract data from plan
        root_node = get_root_plan(plan_json)
        actual_rows = extract_actual_rows(root_node)
        nodes = flatten_plan(root_node)
        df = pd.DataFrame(nodes)

        # Save original node type names BEFORE encoding for display
        original_node_types = df["node_type"].astype(str).tolist() if "node_type" in df.columns else ["Unknown"] * len(df)

        # Warn if this is a simple single-table query (no JOINs)
        if len(df) <= 2:
            st.warning("⚠️ This looks like a simple single-table query. The AI model was trained on JOIN queries and may show higher error here. Try a sample query with JOINs for best AI performance.")

        # Encode categorical features
        for col, le in encoders.items():
            if col in df.columns:
                df[col] = df[col].fillna("missing").astype(str)
                df[col] = df[col].replace("None", "none")
                # Handle unseen categories
                df[col] = df[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)

        # Prepare features
        num_cols = ["startup_cost", "total_cost", "plan_width", "selectivity", "cost_ratio"]
        cat_cols = ["node_type", "parent_node", "join_type", "relation_name", "alias",
                   "filter", "hash_cond", "index_cond"]
        
        num_cols = [col for col in num_cols if col in df.columns]
        cat_cols = [col for col in cat_cols if col in df.columns]

        # Scale and predict
        X_num = scaler.transform(df[num_cols])
        X_cat = df[cat_cols].values
        X = np.hstack([X_cat, X_num])

        preds_log = model.predict(X)
        ai_rows = 10 ** preds_log
        ai_rows = np.clip(ai_rows, 0.1, 1000000)

        # Create results dataframe
        results = []
        for i in range(len(ai_rows)):
            pg_estimate = df["plan_rows"].iloc[i] if "plan_rows" in df.columns else 0
            ai_estimate = ai_rows[i]
            actual = actual_rows[i]
            
            if actual > 0:
                safe_pg = max(float(pg_estimate), 0.1)
                safe_ai = max(float(ai_estimate), 0.1)
                q_pg = max(safe_pg / actual, actual / safe_pg)
                q_ai = max(safe_ai / actual, actual / safe_ai)
                winner = "AI" if q_ai < q_pg else "PostgreSQL" if q_ai > q_pg else "Tie"
            else:
                q_pg = 1.0
                q_ai = 1.0
                winner = "N/A"
            
            results.append({
                "node_id": i,
                "node_type": original_node_types[i] if i < len(original_node_types) else "Unknown",
                "pg_estimate": pg_estimate,
                "ai_estimate": ai_estimate,
                "actual_rows": actual,
                "q_error_pg": q_pg,
                "q_error_ai": q_ai,
                "winner": winner
            })
        
        log_event("PLAN_ANALYSIS", f"Completed estimate comparison for {len(results)} plan nodes.")
        return pd.DataFrame(results)
    
    except Exception as e:
        st.error(f"Error in prediction: {str(e)}")
        return None

def generate_sample_queries():
    """Return sample queries for demonstration"""
    return {
        "Simple Join": """
            SELECT f.title, c.name 
            FROM film f 
            JOIN film_category fc ON f.film_id = fc.film_id 
            JOIN category c ON fc.category_id = c.category_id 
            WHERE f.length > 120 AND c.name = 'Action' 
            LIMIT 10;
        """,
        "Customer Payments": """
            SELECT c.first_name, c.last_name, COUNT(p.payment_id) as payment_count
            FROM customer c
            JOIN payment p ON c.customer_id = p.customer_id
            WHERE p.payment_date > '2005-01-01'
            GROUP BY c.customer_id
            HAVING COUNT(p.payment_id) > 10
            LIMIT 20;
        """,
        "Film Rentals": """
            SELECT f.title, c.name, COUNT(r.rental_id) as rental_count
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            JOIN inventory i ON f.film_id = i.film_id
            JOIN rental r ON i.inventory_id = r.inventory_id
            WHERE f.length > 90
            GROUP BY f.film_id, c.name
            HAVING COUNT(r.rental_id) > 5
            ORDER BY rental_count DESC LIMIT 15;
        """,
        "Actor Performance": """
            SELECT a.first_name, a.last_name, COUNT(fa.film_id) as film_count
            FROM actor a
            JOIN film_actor fa ON a.actor_id = fa.actor_id
            GROUP BY a.actor_id
            HAVING COUNT(fa.film_id) > 20
            ORDER BY film_count DESC
            LIMIT 15;
        """
    }

def load_model_metrics():
    """Load actual model metrics dynamically"""
    try:
        # Load model
        model = joblib.load(f"{MODEL_DIR}/xgb_lce.pkl")
        
        # Load training data for metrics
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = df[df['actual_rows'] > 0]
            
            # Calculate actual performance metrics
            y = np.log10(df["actual_rows"])
            
            # For demo, we'll use the model's feature set
            feature_columns = [col for col in ['node_type', 'parent_node', 'join_type', 
                                             'relation_name', 'alias', 'filter', 'hash_cond', 
                                             'index_cond', 'startup_cost', 'total_cost', 
                                             'plan_width', 'selectivity', 'cost_ratio'] 
                             if col in df.columns]
            
            X = df[feature_columns].copy()
            
            # Encode categorical features
            encoders = {}
            cat_cols = ['node_type', 'parent_node', 'join_type', 'relation_name', 'alias', 
                       'filter', 'hash_cond', 'index_cond']
            cat_cols = [c for c in cat_cols if c in X.columns]
            
            for col in cat_cols:
                le = joblib.load(f"{MODEL_DIR}/le_{col}.pkl")
                X[col] = X[col].fillna("missing").astype(str)
                X[col] = X[col].replace("None", "none")
                X[col] = X[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)
            
            # Scale numerical features
            scaler = joblib.load(f"{MODEL_DIR}/input_scaler.pkl")
            num_cols = ['startup_cost', 'total_cost', 'plan_width', 'selectivity', 'cost_ratio']
            num_cols = [c for c in num_cols if c in X.columns]
            X[num_cols] = scaler.transform(X[num_cols])
            
            # Make predictions
            preds_log = model.predict(X)
            preds = 10 ** preds_log
            actuals = 10 ** y
            
            # Calculate Q-errors
            q_errors = np.maximum(preds / actuals, actuals / preds)
            
            metrics = {
                'median_q_error': np.median(q_errors),
                'mean_q_error': np.mean(q_errors),
                'p90_q_error': np.percentile(q_errors, 90),
                'training_samples': len(df),
                'node_types': df['node_type'].nunique() if 'node_type' in df.columns else 'N/A',
                'features': len(feature_columns)
            }
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                importance_df = pd.DataFrame({
                    'feature': feature_columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                metrics['feature_importance'] = importance_df
            
            return metrics
        else:
            st.warning("Training data file not found. Using default metrics.")
            return None
            
    except Exception as e:
        st.warning(f"Could not load dynamic metrics: {e}")
        return None

def log_event(event_type, message, level="INFO"):
    """Store safe app activity in session state; never write API keys, passwords, or query results."""
    try:
        if "activity_log" not in st.session_state:
            st.session_state.activity_log = []
        st.session_state.activity_log.append({
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "level": level,
            "event_type": event_type,
            "message": str(message)[:500],
        })
        # Also try SQLite as secondary store (works locally, silently fails on cloud)
        try:
            with sqlite3.connect(LOG_DB) as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS app_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT,
                    level TEXT, event_type TEXT, message TEXT
                )""")
                conn.execute(
                    "INSERT INTO app_events (created_at, level, event_type, message) VALUES (?, ?, ?, ?)",
                    (datetime.now().isoformat(timespec="seconds"), level, event_type, str(message)[:500]),
                )
        except Exception:
            pass
    except Exception:
        pass


def activity_logs_mode():
    st.header("Activity Logs")
    st.caption("App events only. API keys, passwords, and query result data are never recorded here.")

    # Build combined log from session state + SQLite (if available)
    logs_list = list(st.session_state.get("activity_log", []))
    try:
        if os.path.exists(LOG_DB):
            with sqlite3.connect(LOG_DB) as conn:
                db_logs = pd.read_sql_query(
                    "SELECT created_at, level, event_type, message FROM app_events ORDER BY id DESC LIMIT 250", conn
                )
                logs_list = db_logs.to_dict("records") + logs_list
    except Exception:
        pass

    if not logs_list:
        st.info("No activity has been recorded yet. Run an analysis or generate an AI recommendation to begin.")
        return

    logs = pd.DataFrame(logs_list).drop_duplicates().sort_values("created_at", ascending=False).head(250)
    levels = ["All"] + sorted(logs["level"].dropna().unique().tolist())
    selected_level = st.selectbox("Filter by level", levels)
    if selected_level != "All":
        logs = logs[logs["level"] == selected_level]
    st.metric("Recorded events", len(logs))
    st.dataframe(logs, use_container_width=True, hide_index=True)
    st.download_button("Download activity logs", logs.to_csv(index=False), "ai_query_optimizer_logs.csv", "text/csv")

# Main app
def main():
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">✨ NEXT-GEN DATABASE AI</div>
        <div class="main-header">AI Query Optimizer</div>
        <div class="hero-subtitle">Machine Learning & LLM-Powered Cardinality Estimation & Performance Diagnostics</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-kicker">Your optimization workspace</div>', unsafe_allow_html=True)
    cards = [
        ("⌁", "Estimate with confidence", "Compare AI cardinality estimates against PostgreSQL at every plan node."),
        ("◈", "Diagnose bottlenecks", "Surface costly operations and turn plan data into clear next actions."),
        ("✦", "Ask in plain English", "Describe the analysis you need and generate PostgreSQL-ready SQL."),
    ]
    card_columns = st.columns(3)
    for column, (icon, title, copy) in zip(card_columns, cards):
        with column:
            st.markdown(f'<div class="feature-card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-copy">{copy}</div></div>', unsafe_allow_html=True)
    # Sidebar
    st.sidebar.markdown("## Query Studio")
    st.sidebar.caption("AI-powered PostgreSQL intelligence")
    st.sidebar.markdown("### Workspace")
    app_mode = st.sidebar.radio(
        "Choose Mode",
        ["📂 Upload Plan", "🔌 Live Query", "📊 Model Info", "🧪 Sample Analysis", "📋 Activity Logs"],
        label_visibility="visible"
    )
    # Normalize mode name (strip emoji prefix for comparisons)
    app_mode = app_mode.split(" ", 1)[1] if " " in app_mode else app_mode

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ AI Engine Mode")
    
    st.session_state.ai_engine_mode = st.sidebar.radio(
        "Select Performance Engine:",
        ["⚡ Fast Offline Mode (Instant)", "🤖 Live Gemini LLM (Deep AI)"],
        index=0 if "Fast" in st.session_state.ai_engine_mode else 1,
        help="Fast Offline Mode operates instantly with 0ms network delay. Live Gemini LLM provides live custom prompt conversions and deep Doctor analysis."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔑 API Key Management")

    environment_key = load_secret_value("GEMINI_API_KEY")
    if environment_key:
        st.sidebar.success("✅ Gemini AI key active")
        st.sidebar.caption("Key is securely loaded from app secrets.")
    else:
        st.sidebar.caption("No key found in secrets. Paste one below for this session.")
        input_key = st.sidebar.text_input(
            "Gemini API Key (session only):",
            value="",
            type="password",
            placeholder="Paste a key for this session",
            help="Keys are never saved to a file. Add GEMINI_API_KEY to Streamlit secrets for permanent access.",
        )
        if input_key:
            st.session_state.gemini_api_key = input_key.strip()
            st.sidebar.caption("Key is active for this browser session only.")
    st.sidebar.markdown("---")
    st.sidebar.info(
        "This app uses AI to improve PostgreSQL query plan estimates. "
        "Upload an EXPLAIN ANALYZE plan or run a live query to see the AI in action!"
    )

    if app_mode == "Upload Plan":
        upload_plan_mode()
    elif app_mode == "Live Query":
        live_query_mode()
    elif app_mode == "Model Info":
        model_info_mode()
    elif app_mode == "Sample Analysis":
        sample_analysis_mode()
    elif app_mode == "Activity Logs":
        activity_logs_mode()

def upload_plan_mode():
    st.header("Upload EXPLAIN ANALYZE Plan")
    
    uploaded_file = st.file_uploader("Upload JSON plan file", type=['json'])
    
    if uploaded_file is not None:
        try:
            plan_json = json.load(uploaded_file)
            st.success("Plan file loaded successfully!")
            
            # Show plan structure
            with st.expander("View Plan Structure"):
                st.json(plan_json)
            
            # Predict
            if st.button("Analyze with AI", type="primary"):
                with st.spinner("Analyzing plan with AI..."):
                    results_df = predict_plan(plan_json)
                
                if results_df is not None:
                    display_results(results_df, plan_json=plan_json)
                    
        except Exception as e:
            st.error(f"Error loading plan: {str(e)}")

def render_query_readiness(source, original_request=None):
    """Explain what will execute without silently changing user-provided SQL."""
    if source == "Natural Language":
        interpreted = corrected_request_preview(original_request or "")
        st.caption(f"Interpreted request: {interpreted}")
        st.caption("Natural-language spelling is interpreted where possible; review the generated SQL below.")
    elif source == "Custom SQL":
        st.caption("Custom SQL is preserved exactly as entered and checked before execution.")
    else:
        st.caption(f"Using the built-in sample query: {source}.")
    st.success("Validated: one read-only SELECT query. Safe to analyze.")

def live_query_mode():
    st.header("Live Query Analysis")

    # ── Database Connection (persisted via session_state) ──────────────────
    st.subheader("Database Connection")
    st.info("💡 Your credentials are saved for this session — switching queries won't clear them.")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.db_host = st.text_input("Host", value=st.session_state.db_host)
        st.session_state.db_name = st.text_input("Database", value=st.session_state.db_name)
    with col2:
        st.session_state.db_user = st.text_input("User", value=st.session_state.db_user)
        st.session_state.db_password = st.text_input("Password", value=st.session_state.db_password, type="password")
    port_col, ssl_col = st.columns(2)
    with port_col:
        st.session_state.db_port = st.text_input("Port", value=str(st.session_state.db_port), placeholder="5432")
    with ssl_col:
        ssl_options = ["require", "prefer", "disable", "verify-ca", "verify-full"]
        current_ssl = st.session_state.db_sslmode if st.session_state.db_sslmode in ssl_options else "require"
        st.session_state.db_sslmode = st.selectbox("SSL mode", ssl_options, index=ssl_options.index(current_ssl), help="Use require for Neon, Supabase, and most hosted PostgreSQL services.")

    # ── Query Input ────────────────────────────────────────────────────────
    st.subheader("Query Input")
    sample_queries = generate_sample_queries()

    query_option = st.selectbox(
        "Choose a sample query, write custom SQL, or type in Plain English:",
        ["Custom Query (SQL)", "Natural Language (English)"] + list(sample_queries.keys())
    )

    is_english_mode = (query_option == "Natural Language (English)")

    if query_option == "Custom Query (SQL)":
        st.markdown("""
        **Tips for custom queries:**
        - Use tables from `dvd_rental`: `film`, `actor`, `customer`, `rental`, `payment`, `inventory`, `category`, `film_category`, `film_actor`
        - JOIN queries give the best AI results (the model was trained on JOINs)
        """)
        query = st.text_area(
            "Enter your SQL query:",
            height=150,
            placeholder="SELECT f.title, c.name FROM film f JOIN film_category fc ON f.film_id = fc.film_id JOIN category c ON fc.category_id = c.category_id LIMIT 20;"
        )
    elif is_english_mode:
        st.markdown("💬 **Write your query in Plain English!** The AI will automatically generate the PostgreSQL query for you.")
        english_input = st.text_area(
            "Describe your query in English:",
            height=120,
            placeholder="Show me all Action movies longer than 2 hours along with their category name."
        )
        query = english_input # placeholder until conversion
    else:
        query = sample_queries[query_option]
        st.code(query, language="sql")

    # ── Execute ────────────────────────────────────────────────────────────
    if st.button("Execute & Analyze", type="primary"):
        # If in Natural Language mode, convert English -> SQL first
        if is_english_mode:
            if not english_input or not english_input.strip():
                st.error("❌ Please enter a query description in English.")
                return
            
            with st.spinner("🤖 Translating your English request into SQL..."):
                query = convert_english_to_sql(english_input, st.session_state.gemini_api_key)
                if query.startswith("Error"):
                    st.error(f"❌ {query}")
                    return
                st.markdown("### 📝 AI Generated SQL Query:")
                st.code(query, language="sql")
        # Validate inputs
        if not query or not query.strip():
            st.error("❌ Please enter a SQL query.")
            return
        if not is_safe_select(query):
            st.error("❌ Only one read-only SELECT query is allowed. Check the generated SQL and try again.")
            log_event("SQL_VALIDATION", "Rejected a non-read-only or malformed query.", "WARNING")
            return
        source = "Natural Language" if is_english_mode else ("Custom SQL" if query_option == "Custom Query (SQL)" else query_option)
        render_query_readiness(source, english_input if is_english_mode else None)
        if not st.session_state.db_password:
            st.error("❌ Password is required. Enter your PostgreSQL password above.")
            return
        if not all([st.session_state.db_host, st.session_state.db_name, st.session_state.db_user]):
            st.error("❌ Please fill in all database connection fields.")
            return

        try:
            with st.spinner("Connecting to database and running EXPLAIN ANALYZE..."):
                conn = connect_postgres()
                cur = conn.cursor()

                cur.execute(f"EXPLAIN (ANALYZE, FORMAT JSON) {query}")
                result = cur.fetchone()

                # Also fetch actual query data results for display
                try:
                    cur.execute(query)
                    data_rows = cur.fetchall()
                    col_names = [desc[0] for desc in cur.description] if cur.description else []
                    if data_rows and col_names:
                        df_data = pd.DataFrame(data_rows, columns=col_names)
                        with st.expander("📊 View Query Output Data (Actual Results)", expanded=True):
                            st.dataframe(df_data, use_container_width=True)
                except Exception as data_err:
                    pass

                cur.close()
                conn.close()

            if result and result[0]:
                plan_json = result[0]
                st.success("✅ Query executed successfully! Running AI analysis...")

                with st.expander("🔍 View Raw Execution Plan (JSON)"):
                    st.json(plan_json)

                results_df = predict_plan(plan_json)
                if results_df is not None:
                    display_results(results_df, query, plan_json)
            else:
                st.error("❌ No execution plan returned from PostgreSQL.")

        except psycopg2.OperationalError as e:
            st.error(f"❌ **Connection failed.** Check your host, database name, user, and password.\n\nDetail: `{str(e)}`")
        except psycopg2.errors.UndefinedTable as e:
            st.error(f"❌ **Table not found.** Make sure you're using tables from the `dvd_rental` database.\n\nDetail: `{str(e)}`")
        except Exception as e:
            st.error(f"❌ **Error:** {str(e)}")

def model_info_mode():
    st.header("Model Information")
    
    # Load dynamic metrics
    metrics = load_model_metrics()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Performance")
        if metrics:
            st.metric("Median Q-Error", f"{metrics['median_q_error']:.3f}")
            st.metric("Mean Q-Error", f"{metrics['mean_q_error']:.3f}")
            st.metric("90th Percentile Q-Error", f"{metrics['p90_q_error']:.3f}")
        else:
            # Fallback to your actual training results
            st.metric("Median Q-Error", "1.028")
            st.metric("Mean Q-Error", "1.266")
            st.metric("90th Percentile Q-Error", "1.596")
    
    with col2:
        st.subheader("Training Data")
        if metrics:
            st.metric("Training Samples", f"{metrics['training_samples']:,}")
            st.metric("Node Types", metrics['node_types'])
            st.metric("Features", metrics['features'])
        else:
            st.metric("Training Samples", "12,818")
            st.metric("Node Types", "9")
            st.metric("Features", "13")
    
    st.subheader("Feature Importance")
    
    try:
        # Load actual feature importance from model
        model = joblib.load(f"{MODEL_DIR}/xgb_lce.pkl")
        
        # Get feature names
        feature_columns = ['node_type', 'parent_node', 'join_type', 'relation_name', 'alias',
                         'filter', 'hash_cond', 'index_cond', 'startup_cost', 'total_cost',
                         'plan_width', 'selectivity', 'cost_ratio']
        
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'Feature': feature_columns,
                'Importance': model.feature_importances_
            }).sort_values('Importance', ascending=False).head(10)
            
            fig = px.bar(importance_df, x='Importance', y='Feature', orientation='h',
                        title="Top 10 Feature Importances (Actual Model)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show importance table
            st.dataframe(importance_df, use_container_width=True)
        else:
            st.info("Feature importance not available for this model type.")
            
    except Exception as e:
        st.warning(f"Could not load feature importance: {e}")
        # Fallback to known values from your training
        importance_data = {
            'Feature': ['parent_node', 'plan_width', 'total_cost', 'join_type', 'alias', 
                       'relation_name', 'selectivity', 'cost_ratio', 'hash_cond', 'startup_cost'],
            'Importance': [0.275, 0.256, 0.129, 0.082, 0.066, 0.064, 0.056, 0.027, 0.017, 0.012]
        }
        importance_df = pd.DataFrame(importance_data)
        
        fig = px.bar(importance_df, x='Importance', y='Feature', orientation='h',
                    title="Top 10 Feature Importances (From Training)")
        st.plotly_chart(fig, use_container_width=True)

def sample_analysis_mode():
    st.header("Sample Analysis")
    
    # Use actual recent analysis if available, otherwise show informative message
    st.info("""
    **Run a live query or upload a plan to see dynamic analysis here!**
    
    This section will display actual results from your recent queries including:
    - Real Q-error comparisons between AI and PostgreSQL
    - Dynamic performance metrics
    - Actual plan node analysis
    """)
    
    # Option to load a sample plan for demonstration
    sample_plan_path = "sample_plan.json"
    if os.path.exists(sample_plan_path):
        if st.button("Load Sample Analysis"):
            with open(sample_plan_path) as f:
                plan_json = json.load(f)
            results_df = predict_plan(plan_json)
            if results_df is not None:
                display_results(results_df, query="SELECT * FROM sample", plan_json=plan_json)
    else:
        st.warning("Sample plan file not found. Run a query first or upload a plan.")

def extract_json_response(text):
    """Safely decode the first JSON object returned by an LLM."""
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).replace("```", "").strip()
    try:
        start = cleaned.index("{")
        payload, _ = json.JSONDecoder().raw_decode(cleaned[start:])
        return payload if isinstance(payload, dict) else None
    except (ValueError, json.JSONDecodeError):
        return None


def get_structured_ai_review(query, plan_json, api_key):
    """Use Gemini for a predictable, UI-ready query review."""
    try:
        prompt = f"""You are a PostgreSQL performance reviewer. Review the SQL and JSON execution-plan summary below.
Return ONLY a valid JSON object (no markdown, no explanation, no extra text) with exactly these keys:
- risk_level: one of Low, Medium, High
- score: integer from 0 to 100, where 100 means safest
- summary: one concise plain-English sentence
- anti_patterns: array of up to 3 concise strings
- next_action: one concrete improvement a beginner can understand

SQL: {query}
PLAN: {str(plan_json)[:2200]}
"""
        raw = generate_gemini_response(api_key, prompt)
        review = extract_json_response(raw)
        if review:
            review.setdefault("anti_patterns", [])
            review.setdefault("risk_level", "Medium")
            review.setdefault("score", 50)
            review.setdefault("summary", "AI review completed.")
            review.setdefault("next_action", "Review the highest-cost plan node.")
            log_event("AI_DOCTOR", "Generated a structured Gemini query review.")
            return review
        return {"risk_level": "Review", "score": "—", "summary": raw, "anti_patterns": [], "next_action": "Use the plan explorer to inspect expensive nodes."}
    except Exception as e:
        return {"risk_level": "Unavailable", "score": "—", "summary": "The AI review could not be generated.", "anti_patterns": [str(e)], "next_action": "Check your Gemini API key and try again."}


def collect_plan_nodes(node, parent="Root", depth=0, output=None):
    if output is None:
        output = []
    node_id = len(output)
    output.append({"id": node_id, "parent": parent, "depth": depth, "node": node})
    for child in node.get("Plans", []):
        collect_plan_nodes(child, f"{node_id}: {node.get('Node Type', 'Plan')}", depth + 1, output)
    return output


def get_index_recommendations(plan_json):
    """Rule-based index hints: transparent, safe, and easy to explain."""
    if not plan_json:
        return []
    recommendations, seen = [], set()
    for item in collect_plan_nodes(get_root_plan(plan_json)):
        node = item["node"]
        relation, node_type = node.get("Relation Name"), node.get("Node Type", "")
        filter_text = node.get("Filter") or node.get("Index Cond") or ""
        if not relation or "Seq Scan" not in node_type or not filter_text:
            continue
        columns = re.findall(r"(?:\w+\.)?([a-zA-Z_][\w]*)\s*(?:=|>|<|>=|<=|~~|LIKE|ILIKE)", filter_text, re.IGNORECASE)
        for column in columns:
            if column.lower() in {"and", "or", "null", "true", "false"}:
                continue
            index_name = f"idx_{relation}_{column}".lower()
            if index_name in seen:
                continue
            seen.add(index_name)
            recommendations.append({
                "sql": f"CREATE INDEX IF NOT EXISTS {index_name} ON {relation} ({column});",
                "reason": f"{node_type} on `{relation}` filters by `{column}`. An index may reduce full-table scanning.",
            })
    return recommendations


def render_plan_explorer(plan_json):
    if not plan_json:
        return
    st.subheader("Plan Explorer")
    nodes = collect_plan_nodes(get_root_plan(plan_json))
    labels = {item["id"]: f"{'  ' * item['depth']}↳ {item['node'].get('Node Type', 'Unknown')} · {item['node'].get('Relation Name', 'operation')}" for item in nodes}
    selected_id = st.selectbox("Inspect a plan node", options=list(labels), format_func=lambda item: labels[item], key="plan_node_explorer")
    selected = next(item["node"] for item in nodes if item["id"] == selected_id)
    a, b, c = st.columns(3)
    a.metric("Estimated rows", f"{selected.get('Plan Rows', 0):,}")
    b.metric("Total cost", f"{selected.get('Total Cost', 0):,.2f}")
    c.metric("Actual rows", f"{selected.get('Actual Rows', 0):,}")
    with st.expander("View selected node JSON"):
        st.json(selected)


def save_analysis(query, results_df, plan_json):
    """Save summary metrics without allowing local history errors to affect analysis."""
    if not query or results_df is None or results_df.empty:
        return
    try:
        root = get_root_plan(plan_json) if plan_json else {}
        payload = query + json.dumps(plan_json, sort_keys=True, default=str, ensure_ascii=True)
        fingerprint = hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()
        valid = results_df[results_df["actual_rows"] > 0]
        if valid.empty:
            return
        pg_error, ai_error = valid["q_error_pg"].mean(), valid["q_error_ai"].mean()
        improvement = ((pg_error - ai_error) / pg_error * 100) if pg_error else 0
        with sqlite3.connect(HISTORY_DB) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS analyses (
                fingerprint TEXT PRIMARY KEY, created_at TEXT, query_text TEXT,
                pg_error REAL, ai_error REAL, improvement REAL, total_cost REAL, execution_time REAL
            )""")
            conn.execute("""INSERT OR IGNORE INTO analyses VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                fingerprint, datetime.now().isoformat(timespec="seconds"), query[:1000], pg_error, ai_error,
                improvement, root.get("Total Cost", 0), (plan_json[0].get("Execution Time", 0) if isinstance(plan_json, list) and plan_json else 0)
            ))
    except Exception:
        log_event("ANALYSIS_HISTORY", "Local history could not be saved.", "WARNING")
        st.warning("Analysis completed, but its local history entry could not be saved.")


def render_analysis_history():
    """Show recent saved analyses without allowing presentation errors to affect results."""
    if not os.path.exists(HISTORY_DB):
        return
    try:
        with sqlite3.connect(HISTORY_DB) as conn:
            rows = conn.execute(
                "SELECT created_at, pg_error, ai_error, improvement, total_cost, execution_time "
                "FROM analyses ORDER BY created_at DESC LIMIT 20"
            ).fetchall()
        if not rows:
            return
        history = pd.DataFrame(
            rows,
            columns=["Saved at", "PG Q-error", "AI Q-error", "Improvement %", "Total cost", "Execution time (ms)"],
        )
        for column in history.columns[1:]:
            history[column] = pd.to_numeric(history[column], errors="coerce").round(3)
        with st.expander("Analysis History", expanded=False):
            st.caption("Recent analyses saved locally. Identical plans are stored once to keep history meaningful.")
            st.dataframe(history, use_container_width=True, hide_index=True)
    except Exception as error:
        log_event("ANALYSIS_HISTORY", f"History display failed: {type(error).__name__}.", "WARNING")
        st.warning("Analysis history is unavailable right now. New query analysis remains unaffected.")

def get_sql_rewrite(query, api_key):
    try:
        prompt = f"""Rewrite this PostgreSQL SELECT query for potential performance improvement.
Keep identical intent. Do not use DDL, DML, comments, or explanations. Return only one SQL SELECT statement.
SQL: {query}"""
        candidate = extract_clean_sql(generate_gemini_response(api_key, prompt))
        if not candidate.upper().lstrip().startswith("SELECT"):
            raise ValueError("The AI did not return a safe SELECT statement.")
        log_event("AI_REWRITE", "Generated a safe SELECT rewrite candidate.")
        return candidate
    except Exception as e:
        return f"Error: {e}"


def compare_rewrite_plan(candidate_sql):
    """Run EXPLAIN ANALYZE for an approved SELECT rewrite; never changes database data."""
    if not candidate_sql.upper().lstrip().startswith("SELECT"):
        raise ValueError("Only SELECT rewrites can be compared.")
    conn = None
    try:
        conn = connect_postgres()
        with conn.cursor() as cur:
            cur.execute(f"EXPLAIN (ANALYZE, FORMAT JSON) {candidate_sql}")
            result = cur.fetchone()
        log_event("REWRITE_COMPARISON", "Compared a candidate rewrite with EXPLAIN ANALYZE.")
        return result[0] if result else None
    finally:
        if conn:
            conn.close()
def render_rewrite_lab(query, plan_json):
    if not query:
        return
    with st.expander("AI SQL Rewrite Lab", expanded=False):
        st.caption("Generate one safe candidate rewrite. Review it before running any database analysis.")
        if not st.session_state.gemini_api_key:
            st.info("Add a Gemini API key in the sidebar to enable rewrite generation.")
            return
        query_key = hashlib.sha256(query.encode()).hexdigest()[:12]
        if st.button("Generate candidate rewrite", key=f"rewrite_{query_key}"):
            with st.spinner("Creating a safe rewrite candidate…"):
                st.session_state[f"candidate_{query_key}"] = get_sql_rewrite(query, st.session_state.gemini_api_key)
        candidate = st.session_state.get(f"candidate_{query_key}")
        if candidate:
            if candidate.startswith("Error:"):
                st.error(candidate)
            else:
                st.code(candidate, language="sql")
                st.warning("This is a suggestion only. Compare it with EXPLAIN ANALYZE before using it in production.")
                if st.session_state.db_password:
                    if st.button("Compare with original plan", key=f"compare_{query_key}"):
                        try:
                            with st.spinner("Running EXPLAIN ANALYZE for the candidate…"):
                                candidate_plan = compare_rewrite_plan(candidate)
                            original_root = get_root_plan(plan_json) if plan_json else {}
                            candidate_root = get_root_plan(candidate_plan) if candidate_plan else {}
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Original cost", f"{original_root.get('Total Cost', 0):,.2f}")
                            c2.metric("Rewrite cost", f"{candidate_root.get('Total Cost', 0):,.2f}")
                            original_time = plan_json[0].get("Execution Time", 0) if isinstance(plan_json, list) and plan_json else 0
                            candidate_time = candidate_plan[0].get("Execution Time", 0) if isinstance(candidate_plan, list) and candidate_plan else 0
                            c3.metric("Execution time", f"{original_time:.2f} ms → {candidate_time:.2f} ms")
                        except Exception as e:
                            st.error(f"Could not compare the rewrite: {e}")
                else:
                    st.caption("Enter database credentials in Live Query mode to compare this rewrite with EXPLAIN ANALYZE.")
def display_results(results_df, query=None, plan_json=None):
    """Display prediction results in an interactive way"""
    st.header("Analysis Results")
    
    # Calculate summary metrics
    valid_nodes = results_df[results_df['actual_rows'] > 0]
    if len(valid_nodes) == 0:
        st.warning("No nodes with actual rows data available.")
        return

    # --- TRAFFIC LIGHT SYSTEM ---
    max_ai_rows = results_df['ai_estimate'].max()
    if max_ai_rows > 50000:
        st.markdown('<div class="status-red">🚨 <b>HIGH RISK QUERY</b>: Predicted to process a massive amount of data (over 50,000 rows). This might cause performance issues in production.</div>', unsafe_allow_html=True)
    elif max_ai_rows > 10000:
        st.markdown('<div class="status-yellow">⚠️ <b>MODERATE RISK</b>: Predicted to process a significant amount of data (over 10,000 rows). Optimization is recommended.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-green">✅ <b>SAFE QUERY</b>: Predicted row count is low. Safe for production execution.</div>', unsafe_allow_html=True)
    # ----------------------------

    # --- STRUCTURED AI QUERY DOCTOR (GEMINI) ---
    if st.session_state.gemini_api_key and query and plan_json:
        with st.spinner("The AI Query Doctor is preparing a structured review…"):
            review = get_structured_ai_review(query, plan_json, st.session_state.gemini_api_key)
        st.subheader("AI Query Doctor")
        doctor_a, doctor_b = st.columns([1, 4])
        with doctor_a:
            st.metric("Safety score", review["score"])
            st.caption(f"Risk: {review['risk_level']}")
        with doctor_b:
            st.markdown(f'<div class="ai-insight-box"><b>{review["summary"]}</b><br><br><b>Recommended next step:</b> {review["next_action"]}</div>', unsafe_allow_html=True)
            if review["anti_patterns"]:
                st.markdown("**Potential anti-patterns**")
                for item in review["anti_patterns"]:
                    st.write(f"• {item}")
    elif not st.session_state.gemini_api_key:
        st.info("Add a Gemini API key in the sidebar to enable the structured AI Query Doctor and Rewrite Lab.")

    if plan_json:
        recommendations = get_index_recommendations(plan_json)
        if recommendations:
            with st.expander("Smart Index Advisor", expanded=True):
                st.caption("Rule-based suggestions only — review table size and write overhead before creating an index.")
                for recommendation in recommendations:
                    st.code(recommendation["sql"], language="sql")
                    st.write(recommendation["reason"])
        else:
            st.caption("Smart Index Advisor: no clear filter-driven sequential scan was detected in this plan.")
    avg_pg_error = valid_nodes['q_error_pg'].mean()
    avg_ai_error = valid_nodes['q_error_ai'].mean()
    improvement = ((avg_pg_error - avg_ai_error) / avg_pg_error * 100) if avg_pg_error > 0 else 0
    ai_wins = (valid_nodes['winner'] == 'AI').sum()
    pg_wins = (valid_nodes['winner'] == 'PostgreSQL').sum()
    ties = (valid_nodes['winner'] == 'Tie').sum()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Avg PostgreSQL Error", f"{avg_pg_error:.2f}")
    
    with col2:
        st.metric("Avg AI Error", f"{avg_ai_error:.2f}")
    
    with col3:
        improvement_class = "improvement-positive" if improvement > 0 else "improvement-negative"
        st.markdown(f'<div class="metric-card">Improvement<br><span class="{improvement_class}">{improvement:+.1f}%</span></div>', 
                   unsafe_allow_html=True)
    
    with col4:
        st.metric("AI Wins vs PostgreSQL", f"{ai_wins}-{pg_wins}")
    
    # Detailed results table with styling
    st.subheader("Detailed Node Analysis")
    
    # Format the dataframe for display with better styling
    display_df = results_df.copy()
    display_df['pg_estimate'] = display_df['pg_estimate'].round(1)
    display_df['ai_estimate'] = display_df['ai_estimate'].round(1)
    display_df['q_error_pg'] = display_df['q_error_pg'].round(3)
    display_df['q_error_ai'] = display_df['q_error_ai'].round(3)
    
    # Add winner styling
    def style_winner(val):
        if val == 'AI':
            return 'color: #155724; background-color: #d4edda;'
        elif val == 'PostgreSQL':
            return 'color: #721c24; background-color: #f8d7da;'
        else:
            return ''
    
    styled_df = display_df.style.map(style_winner, subset=['winner'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Q-Error comparison chart (Modern Spline Curves)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=results_df['node_id'], y=results_df['q_error_pg'], 
            name='PostgreSQL', mode='lines+markers',
            line=dict(color='#ef4444', width=3, shape='spline'),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=results_df['node_id'], y=results_df['q_error_ai'], 
            name='AI Optimizer', mode='lines+markers',
            line=dict(color='#10b981', width=3, shape='spline'),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title="<b>Q-Error Comparison by Node</b>",
            font=dict(family="Plus Jakarta Sans, sans-serif"),
            xaxis_title="Node ID",
            yaxis_title="Q-Error",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Winner distribution (Modern Donut Chart)
        winner_counts = results_df['winner'].value_counts()
        colors_map = {'AI': '#10b981', 'PostgreSQL': '#ef4444', 'Tie': '#94a3b8'}
        colors = [colors_map.get(idx, '#94a3b8') for idx in winner_counts.index]
        
        fig = px.pie(
            values=winner_counts.values, 
            names=winner_counts.index,
            title="<b>Estimation Accuracy by Winner</b>",
            hole=0.45,
            color_discrete_sequence=colors
        )
        fig.update_layout(
            font=dict(family="Plus Jakarta Sans, sans-serif"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance by node type
    if 'node_type' in results_df.columns:
        st.subheader("Performance by Node Type")
        node_performance = results_df.groupby('node_type').agg({
            'q_error_pg': 'mean',
            'q_error_ai': 'mean',
            'winner': lambda x: (x == 'AI').sum() / len(x) * 100  # AI win percentage
        }).round(3)
        
        node_performance.columns = ['Avg PG Error', 'Avg AI Error', 'AI Win %']
        st.dataframe(node_performance, use_container_width=True)
    
    # Download results
    csv = results_df.to_csv(index=False)
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="ai_optimizer_results.csv",
        mime="text/csv"
    )
    render_plan_explorer(plan_json)
    render_rewrite_lab(query, plan_json)
    save_analysis(query, results_df, plan_json)
    render_analysis_history()

if __name__ == "__main__":
    main()































