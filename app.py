# app.py
"""
Final Cultural Knowledge Graph Workbench (polished)
- Banner (images.jpg if present) + gradient header
- Theme toggle (Auto / Light / Dark)
- Sidebar search + menu
- Dataset Overview, Add Entity, Add Relationships, SPARQL Explorer
- Analyze Entity (table + predicate counts + PyVis graph + similar-entities)
- Fuzzy reasoning demo
- Admin (login on main page) with Purge / Export / Import / Activity log
- Activity logging to 'activity.log'
- Uses ontology IRI provided by user
"""

import os
import time
import json
import requests
import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from fuzzywuzzy import fuzz
from PIL import Image

# ---------------- CONFIG ----------------
FUSEKI_BASE = os.environ.get("FUSEKI_BASE", "http://localhost:3030/culture_difference")
FUSEKI_QUERY = f"{FUSEKI_BASE}/query"
FUSEKI_UPDATE = f"{FUSEKI_BASE}/update"
FUSEKI_DATA = f"{FUSEKI_BASE}/data"

# Ontology IRI provided by you (append '#')
ONTOLOGY_BASE = ONTOLOGY_BASE = "http://example.org/culturaldifference#"
PREFIX = f"PREFIX : <{ONTOLOGY_BASE}>\n"

# Local credentials for prototype (use env vars in production)
USER_CREDENTIALS = {
    os.environ.get("KG_ADMIN_USER", "admin"): os.environ.get("KG_ADMIN_PASS", "1234"),
    os.environ.get("KG_LEAD_USER", "teamlead"): os.environ.get("KG_LEAD_PASS", "culture2025"),
}

ACTIVITY_LOG = "activity.log"

# ---------------- UTIL --------------------------------
def log_action(user, action, details=None):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = {"ts": ts, "user": user, "action": action, "details": details}
    try:
        with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

# SPARQL helpers (robust with debug)
sparql_q = SPARQLWrapper(FUSEKI_QUERY)
sparql_u = SPARQLWrapper(FUSEKI_UPDATE)

def run_query(sparql_text, prefix=True, timeout=60, debug=False):
    q = (PREFIX + sparql_text) if prefix else sparql_text
    if debug:
        st.info("DEBUG: Running SPARQL SELECT/ASK/CONSTRUCT")
        st.code(q)
    try:
        sparql_q.setQuery(q)
        sparql_q.setReturnFormat(JSON)
        sparql_q.setTimeout(timeout)
        res = sparql_q.query().convert()
        rows = [{k: v["value"] for k, v in b.items()} for b in res["results"]["bindings"]]
        return pd.DataFrame(rows)
    except Exception as e:
        # show the request/response hint in UI so user can debug
        st.error(f"SPARQL query failed: {e}")
        st.caption("If this message persists, try the same query in Fuseki UI to debug syntax/endpoint.")
        # also print the query to console (useful when running streamlit from terminal)
        print("---- DEBUG: failed query ----")
        print(q)
        print("---- END DEBUG ----")
        return pd.DataFrame()

def run_update(sparql_update_text, prefix=True, debug=False):
    q = (PREFIX + sparql_update_text) if prefix else sparql_update_text
    if debug:
        st.info("DEBUG: Running SPARQL UPDATE")
        st.code(q)
    try:
        sparql_u.setMethod("POST")
        sparql_u.setQuery(q)
        sparql_u.query()
        return True
    except Exception as e:
        st.error(f"SPARQL update failed: {e}")
        print("---- DEBUG: failed update ----")
        print(q)
        print("---- END DEBUG ----")
        return False

# fuzzy similarity
def fuzzy_similarity(a, b):
    return fuzz.token_sort_ratio(a, b) / 100.0

# ---------------- UI: theme, banner, layout ----------------
st.set_page_config(page_title="Cultural Difference in Pakistan", layout="wide", page_icon="🌐")

# ======== THEME TOGGLE SECTION (full-page color control) ========
theme_choice = st.sidebar.radio("🎨 Theme", ["Auto", "Light", "Dark"], index=0)

# Apply background color to all layout layers
light_theme_css = """
<style>
/* Make full app background light */
[data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}
[data-testid="stHeader"] {
    background-color: #ffffff !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a8a, #2563eb) !important;
    color: white !important;
}
.block-container {
    background-color: #ffffff !important;
    color: #111827 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #1e3a8a !important;
}
</style>
"""

dark_theme_css = """
<style>
/* Make full app background dark */
[data-testid="stAppViewContainer"] {
    background-color: #0b1220 !important;
    color: #e2e8f0 !important;
}
[data-testid="stHeader"] {
    background-color: #0b1220 !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #1f2937) !important;
    color: white !important;
}
.block-container {
    background-color: #0b1220 !important;
    color: #e2e8f0 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #93c5fd !important;
}
</style>
"""
auto_theme_css = """
<style>
/* 🌿 Light Green Theme */

/* App main background */
[data-testid="stAppViewContainer"] {
    background-color: #e8f5e9 !important;  /* very light green */
    color: #1b4332 !important;            /* dark green text */
}

/* Header (top bar) */
[data-testid="stHeader"] {
    background-color: #a8d5ba !important;  /* soft mint green */
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #b7e4c7, #95d5b2) !important;
    color: #081c15 !important;
}

/* Content container */
.block-container {
    background-color: #e8f5e9 !important;
    color: #1b4332 !important;
    border-radius: 8px;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #2d6a4f !important; /* rich green for headers */
}

/* Buttons */
div.stButton > button {
    background-color: #52b788 !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}
div.stButton > button:hover {
    background-color: #40916c !important;
}

/* Metrics and dataframes */
[data-testid="stMetricValue"] {
    color: #2d6a4f !important;
}
[data-testid="stDataFrame"] {
    background-color: #d8f3dc !important;
    color: #1b4332 !important;
}
</style>
"""

# Apply the selected theme
if theme_choice == "Light":
    st.markdown(light_theme_css, unsafe_allow_html=True)
elif theme_choice == "Dark":
    st.markdown(dark_theme_css, unsafe_allow_html=True)
else:
    st.markdown(auto_theme_css, unsafe_allow_html=True)
# ================================================================


# Banner: first show uploaded image (A). then a gradient banner (B)
# 🎓 University banner (text only, no image)
st.markdown(
    "<h2 style='text-align:center; color:#1f2937;'>FAST NUCES — Cultural Difference in Pakistan</h2>",
    unsafe_allow_html=True
)


# Secondary gradient banner (B)
st.markdown("""
<div style="background:linear-gradient(90deg,#1e40af,#2563eb);padding:10px;border-radius:6px;margin-top:8px;">
  <h3 style="text-align:center;color:white;margin:6px 0;">Explore cultural entities, relations, and insights — KRR Project 2025</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- Sidebar: search + menu ----------------
st.sidebar.markdown("## 🔎 Quick Search")
search_term = st.sidebar.text_input("Entity name (partial)")

if search_term:
    try:
        q = f"""
        SELECT ?entity ?type WHERE {{
          ?entity a ?type .
          FILTER(CONTAINS(LCASE(STR(?entity)), LCASE("{search_term}")))
        }} LIMIT 20
        """
        df_search = run_query(q)
        if not df_search.empty:
            df_search["entity_short"] = df_search["entity"].apply(lambda x: x.split("#")[-1])
            df_search["type_short"] = df_search["type"].apply(lambda x: x.split("#")[-1])
            st.sidebar.dataframe(df_search[["entity_short", "type_short"]].rename(columns={"entity_short":"Entity","type_short":"Class"}))
        else:
            st.sidebar.write("No matches.")
    except Exception:
        st.sidebar.write("Search failed (Fuseki offline?)")

st.sidebar.markdown("---")
menu = st.sidebar.radio("Menu", [
    "Dataset Overview", "Add Entity", "Add Relationships", "SPARQL Explorer",
    "Analyze Entity", "Fuzzy Reasoning", "Admin"
], index=0)

# ---------------- Helper functions for app ----------------
def safe_name(s):
    return s.replace(" ", "_")

def insert_entity(entity_type, entity_name, user="anon"):
    ent = safe_name(entity_name)
    q = f"INSERT DATA {{ :{ent} a :{entity_type} . }}"
    ok = run_update(q)
    if ok:
        log_action(user, "add_entity", {"type": entity_type, "name": ent})
    return ok

def insert_relationship(subject, predicate, object_, user="anon"):
    s = safe_name(subject); o = safe_name(object_)
    q = f"INSERT DATA {{ :{s} :{predicate} :{o} . }}"
    ok = run_update(q)
    if ok:
        log_action(user, "add_relationship", {"s": s, "p": predicate, "o": o})
    return ok

def delete_all_triples(user="admin"):
    ok = run_update("DELETE WHERE { ?s ?p ?o }", prefix=False)
    if ok:
        log_action(user, "purge_dataset")
    return ok

def get_entity_rels(entity, limit=500):
    e = safe_name(entity)
    q = f"SELECT ?predicate ?object WHERE {{ :{e} ?predicate ?object }} LIMIT {limit}"
    return run_query(q)

def get_top_predicates(limit=10):
    q = f"SELECT ?p (COUNT(?p) as ?count) WHERE {{ ?s ?p ?o }} GROUP BY ?p ORDER BY DESC(?count) LIMIT {limit}"
    return run_query(q)

def visualize_df_pyvis(df, center_label, theme_dark=False):
    if df.empty:
        st.info("No relationships to visualize.")
        return
    G = nx.DiGraph()
    center = safe_name(center_label)
    G.add_node(center, title=center)
    for _, row in df.iterrows():
        pred = row["predicate"].split("#")[-1] if "#" in row["predicate"] else row["predicate"]
        obj = row["object"].split("#")[-1] if "#" in row["object"] else row["object"]
        G.add_node(obj, title=obj)
        G.add_edge(center, obj, title=pred)
    net = Network(height="600px", width="100%", directed=True,
                  bgcolor="#0b1220" if theme_dark else "#ffffff",
                  font_color="white" if theme_dark else "black")
    net.from_nx(G)
    net.barnes_hut()
    tmp_file = "kg_graph.html"
    net.save_graph(tmp_file)
    html = open(tmp_file, "r", encoding="utf-8").read()
    components.html(html, height=650)

# ---------------- PAGES ----------------
if menu == "Dataset Overview":
    st.header("📊 Dataset Overview")
    c1, c2, c3 = st.columns(3)
    try:
        triples = run_query("SELECT (COUNT(*) AS ?cnt) WHERE { ?s ?p ?o }")
        classes = run_query("SELECT (COUNT(DISTINCT ?c) AS ?cnt) WHERE { ?s a ?c }")
        entities = run_query("SELECT (COUNT(DISTINCT ?s) AS ?cnt) WHERE { ?s ?p ?o }")
        if not triples.empty:
            c1.metric("Triples", int(triples.loc[0]["cnt"]))
        if not classes.empty:
            c2.metric("Distinct Classes", int(classes.loc[0]["cnt"]))
        if not entities.empty:
            c3.metric("Unique Entities", int(entities.loc[0]["cnt"]))
    except Exception:
        st.warning("Could not fetch dataset stats (Fuseki offline?)")

    st.subheader("🔝 Top Predicates")
    try:
        preds = get_top_predicates(10)
        if not preds.empty:
            preds["p_short"] = preds["p"].apply(lambda x: x.split("#")[-1])
            preds = preds.set_index("p_short")
            st.bar_chart(preds["count"])
    except Exception:
        st.info("Top predicates not available.")

    st.subheader("📚 Ontology Classes (sample counts)")
    try:
        cls_q = """
        SELECT ?cls (COUNT(?s) AS ?count)
        WHERE { ?s a ?cls . }
        GROUP BY ?cls ORDER BY DESC(?count) LIMIT 12
        """
        cls_df = run_query(cls_q)
        if not cls_df.empty:
            cls_df["cls_short"] = cls_df["cls"].apply(lambda x: x.split("#")[-1])
            cls_df = cls_df.set_index("cls_short")
            st.bar_chart(cls_df["count"])
    except Exception:
        st.info("Could not fetch class counts.")

elif menu == "Add Entity":
    st.header("➕ Add Entity")
    etype = st.text_input("Entity Type (class)", placeholder="Person, Region, Language, Organization")
    ename = st.text_input("Entity Name", placeholder="Maira Masood")
    if st.button("Add Entity"):
        if not etype or not ename:
            st.warning("Enter both type and name")
        else:
            ok = insert_entity(etype, ename, user=st.session_state.get("user", "anon"))
            if ok:
                st.success(f"Added {ename} as {etype}")
            else:
                st.error("Failed to add entity (check Fuseki & ontology prefix)")

elif menu == "Add Relationships":
    st.header("🔗 Add Multiple Relationships")
    subj = st.text_input("Subject (existing individual name)")
    preds_text = st.text_area("Predicates (comma-separated)", placeholder="speaksLanguage, belongsTo")
    objs_text = st.text_area("Objects (comma-separated) (same order)", placeholder="Urdu, Muslim")
    if st.button("Insert Relationships"):
        preds = [p.strip() for p in preds_text.split(",") if p.strip()]
        objs = [o.strip() for o in objs_text.split(",") if o.strip()]
        if subj.strip() == "" or len(preds) == 0 or len(preds) != len(objs):
            st.error("Please supply subject and matching lists of predicates & objects")
        else:
            succeeded = 0
            for p, o in zip(preds, objs):
                ok = insert_relationship(subj, p, o, user=st.session_state.get("user", "anon"))
                if ok:
                    succeeded += 1
            st.success(f"Inserted {succeeded} relationships for {subj}")

elif menu == "SPARQL Explorer":
    st.header("🔎 SPARQL Explorer (SELECT/ASK/CONSTRUCT)")
    default_q = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 50"
    q = st.text_area("SPARQL SELECT query", value=default_q, height=220)
    if st.button("Run Query"):
        df = run_query(q)
        if df.empty:
            st.warning("No results or query failed.")
        else:
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", data=csv, file_name="query_results.csv")

elif menu == "Analyze Entity":
    st.header("📈 Analyze Entity")
    ent = st.text_input("Entity name (exact individual name, e.g., Maira_Masood)")
    max_rows = st.slider("Max relationships to fetch", 10, 500, 200)
    if st.button("Analyze"):
        if not ent:
            st.warning("Enter entity name")
        else:
            df = get_entity_rels(ent, limit=max_rows)
            if df.empty:
                st.warning("No relationships found for this entity")
            else:
                st.subheader("Relationships")
                st.dataframe(df)
                st.subheader("Predicate counts")
                counts = df["predicate"].value_counts().reset_index()
                counts.columns = ["Predicate", "Count"]
                counts["Predicate"] = counts["Predicate"].apply(lambda x: x.split("#")[-1])
                st.bar_chart(counts.set_index("Predicate"))
                st.subheader("Visual Graph")
                visualize_df_pyvis(df, ent, theme_dark=(theme_choice == "Dark"))
                st.subheader("Similar Entities (share same object/value)")
                sim_q = f"""
                SELECT ?other ?p WHERE {{
                  :{safe_name(ent)} ?p ?obj .
                  ?other ?p ?obj .
                  FILTER(?other != :{safe_name(ent)})
                }} LIMIT 50
                """
                sim_df = run_query(sim_q)
                if not sim_df.empty:
                    sim_df["other_short"] = sim_df["other"].apply(lambda x: x.split("#")[-1])
                    sim_df["p_short"] = sim_df["p"].apply(lambda x: x.split("#")[-1])
                    st.dataframe(sim_df[["other_short", "p_short"]].rename(columns={"other_short":"Entity","p_short":"Predicate"}))
                else:
                    st.info("No similar entities found.")

elif menu == "Fuzzy Reasoning":
    st.header("🧠 Fuzzy Similarity / Reasoning Demo")
    a = st.text_input("Term A", "Punjabi Culture")
    b = st.text_input("Term B", "Sindhi Culture")
    if st.button("Compare"):
        s = fuzzy_similarity(a, b)
        st.metric("Similarity (0–1)", f"{s:.2f}")
        if s > 0.75:
            st.success("High similarity")
        elif s > 0.45:
            st.warning("Moderate similarity")
        else:
            st.info("Low similarity")

elif menu == "Admin":
    # Admin: show login on main page (not sidebar)
    if "auth" not in st.session_state or not st.session_state.auth:
        st.markdown("<h3 style='text-align:center'>🔐 Admin Login</h3>", unsafe_allow_html=True)
        with st.form("admin_login", clear_on_submit=True):
            col1, col2 = st.columns([1,1])
            with col1:
                username = st.text_input("Username")
            with col2:
                password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            if login_btn:
                if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                    st.session_state.auth = True
                    st.session_state.user = username
                    log_action(username, "login")
                    st.success(f"Welcome, {username}")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        st.stop()

    # logged in: show admin tabs
    st.header("⚙️ Admin Utilities")
    st.caption(f"Logged in as **{st.session_state.user}**")
    if st.button("Logout"):
        st.session_state.auth = False
        st.session_state.user = None
        st.success("Logged out")
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["🧹 Purge", "📤 Export RDF", "📥 Import RDF", "📜 Activity Log"])

    with tab1:
        st.write("**Danger zone** — delete all triples from dataset")
        if st.button("Purge dataset (DELETE ALL)"):
            ok = delete_all_triples(user=st.session_state.get("user","admin"))
            if ok:
                st.warning("Dataset purged (all triples deleted)")
            else:
                st.error("Purge failed")

    with tab2:
        st.write("Export full RDF dump from Fuseki (graph store)")
        if st.button("Fetch RDF (.rdf/.trig)"):
            try:
                r = requests.get(FUSEKI_DATA)
                if r.status_code == 200:
                    st.download_button("Download RDF", r.text, file_name="culture_dump.rdf")
                    log_action(st.session_state.get("user","admin"), "export_rdf")
                else:
                    st.error(f"Failed to fetch RDF: {r.status_code}")
            except Exception as e:
                st.error(f"Error fetching RDF: {e}")

    with tab3:
        st.write("Upload RDF/OWL/Turtle file (it will be appended)")
        upload = st.file_uploader("Choose file", type=["rdf","owl","ttl","nt","trig"])
        content_type = st.selectbox("Content-Type header", ["application/rdf+xml","text/turtle","application/trig","text/plain"])
        if upload and st.button("Upload file"):
            try:
                data = upload.read()
                headers = {"Content-Type": content_type}
                r = requests.post(FUSEKI_DATA, data=data, headers=headers)
                if r.status_code in (200,201,204):
                    st.success("Upload succeeded")
                    log_action(st.session_state.get("user","admin"), "import_rdf", {"filename": upload.name})
                else:
                    st.error(f"Upload failed: {r.status_code} - {r.text}")
            except Exception as e:
                st.error(f"Upload error: {e}")

    with tab4:
        st.write("Recent activity log")
        if os.path.exists(ACTIVITY_LOG):
            with open(ACTIVITY_LOG, "r", encoding="utf-8") as f:
                lines = f.read().strip().splitlines()[-500:]
            entries = [json.loads(l) for l in lines if l.strip()]
            df = pd.DataFrame(entries)
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download activity log CSV", data=csv, file_name="activity_log.csv")
        else:
            st.info("No activity log yet")

# Footer
st.markdown("---")
st.caption("Made with ❤️ using Streamlit — FAST NUCES, KRR Project 2025")