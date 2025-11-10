# 🧠 Knowledge Representation & Reasoning (KRR) Mini Project 2  
### **Topic:** *Cultural Differences in Pakistan*  
### **Course Phases:** NER → Ontology → Jena → Python Interface  

---

## 📚 Project Overview

This project represents knowledge about *Cultural Differences in Pakistan* using semantic web technologies.  
It extracts cultural entities from text (NER), builds an ontology in OWL format, loads it into Apache Jena Fuseki for querying, and connects to a Python interface using SPARQL.

---

## 🏗️ **Phase 1: Named Entity Recognition (NER) Extraction (3–4 Days)**

### 🎯 **Objective:**  
Automatically extract named entities (e.g., Persons, Organizations, Locations, Festivals, Languages) from raw text (news articles or research abstracts).

### 🧰 **Tools Used:**  
- Python  
- spaCy (pre-trained model: `en_core_web_sm`)  
- pandas  

### 🧩 **Steps:**
1. Use spaCy NER to extract entities from text.  
2. Identify standard entity types:  
   - `Person`, `Organization`, `Location`, `Date`, `Money`, etc.  
3. Save extracted entities in a structured CSV file:
   ```csv
   source_url, entity_text, label, start_char, end_char, context_sentence
   ```
4. Generate RDF triples (`subject`, `predicate`, `object`) for each entity.
5. Export:
   - `entities_extracted.csv`
   - `triples.csv`
   - `triples.ttl` (RDF/Turtle format)

### 📦 **Output Files:**
- `entities_extracted.csv`
- `triples.csv`
- `triples.ttl`

---

## 🧱 **Phase 2: Ontology Design & Modeling (3–4 Days)**

### 🎯 **Objective:**  
Create a domain ontology for *Cultural Differences in Pakistan* using entities extracted from Phase 1.

### 🧰 **Tools Used:**  
- Protégé (RDF/OWL Editor)  
- Turtle/RDF Files from Phase 1  

### 🧩 **Steps:**
1. Import triples into Protégé (`triples.ttl`).  
2. Define **Classes** (domain concepts):
   - Example: `Person`, `Organization`, `Language`, `Festival`, `CulturalGroup`, `Religion`, `Location`, etc.  
3. Add **Object Properties** (relations between entities):  
   Example:  
   - `speaksLanguage (Person → Language)`  
   - `celebratesFestival (CulturalGroup → Festival)`  
   - `locatedIn (Entity → Location)`  
4. Add **Data Properties** (attributes of entities):  
   Example:  
   - `hasName`, `hasDescription`, `hasSourceURL`, `hasContextSentence`, etc.  
5. Assign classes, individuals, and properties to form a complete ontology.  
6. Export the ontology in OWL format.

### 📦 **Output Files:**
- `ontology.owl` (main ontology for Phase 3)
- `cultural_difference_properties.ttl` (properties definitions)
- `triples.ttl` (instance data)

### ✅ **Phase 2 Deliverables Handed to Phase 3 Team:**
| File | Description |
|------|--------------|
| `ontology.owl` | Full ontology with classes, individuals, and relations |
| `triples.ttl` | Instance-level data extracted from NER |
| `cultural_difference_properties.ttl` | Object & Data property definitions |

---

## 🧮 **Phase 3: Apache Jena Setup (2–3 Days)**

### 🎯 **Objective:**  
Load the ontology into Apache Jena Fuseki, set up a SPARQL endpoint, and test knowledge queries.

### 🧰 **Tools Used:**  
- Apache Jena Fuseki  
- Jena TDB Dataset  
- Web Interface for SPARQL  

### 🧩 **Steps:**
1. **Install Apache Jena Fuseki**  
   Download from: [https://jena.apache.org/download/](https://jena.apache.org/download/)  
2. **Run Fuseki server:**
   ```bash
   fuseki-server
   ```
3. Open `http://localhost:3030/` in browser.  
4. Create a new **dataset** (TDB).  
5. Upload:
   - `ontology.owl`
   - `triples.ttl`
   - `cultural_difference_properties.ttl`
6. Test basic SPARQL queries:
   ```sparql
   SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 50
   ```
   Example domain query:
   ```sparql
   SELECT ?person ?lang WHERE {
       ?person rdf:type <http://example.org/culturaldifference#Person> .
       ?person <http://example.org/culturaldifference#speaksLanguage> ?lang .
   } LIMIT 20
   ```

### 📦 **Output:**
- Working SPARQL endpoint (`http://localhost:3030/dataset/sparql`)  
- Verified ontology loaded into Fuseki  

---

## 🐍 **Phase 4: Python Interface (3–4 Days)**

### 🎯 **Objective:**  
Connect the Fuseki SPARQL endpoint to a Python interface for querying, adding, and analyzing entities.

### 🧰 **Tools Used:**  
- Python  
- `SPARQLWrapper` library  
- Optional: Flask / Tkinter GUI  

### 🧩 **Steps:**
1. Install SPARQLWrapper:
   ```bash
   pip install SPARQLWrapper
   ```
2. Connect to Fuseki endpoint:
   ```python
   from SPARQLWrapper import SPARQLWrapper, JSON

   sparql = SPARQLWrapper("http://localhost:3030/dataset/sparql")
   sparql.setQuery("SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10")
   sparql.setReturnFormat(JSON)
   results = sparql.query().convert()
   ```
3. Implement helper functions:
   ```python
   def add_entity(entity_type, entity_name): ...
   def query_entities(sparql_query): ...
   def find_relationships(entity): ...
   ```
4. (Optional) Create a simple GUI to:
   - Add new entities  
   - Run SPARQL queries  
   - Display relationships visually

### 📦 **Output:**
- `fuseki_interface.py` (main script)
- `gui_interface.py` (optional GUI)
- Live connection to Fuseki endpoint

---

## 📊 **Project Deliverables Summary**

| Phase | Output | Responsible Team |
|-------|---------|------------------|
| Phase 1 | `entities_extracted.csv`, `triples.ttl` | NER Engineer |
| Phase 2 | `ontology.owl`, `cultural_difference_properties.ttl` | Ontology Architect |
| Phase 3 | Fuseki setup & endpoint | Jena Engineer |
| Phase 4 | Python SPARQL GUI | Python Developer |

---

## 🧩 **Project Architecture Overview**

```
Text Source
    ↓
[Phase 1] Entity Extraction (spaCy)
    ↓
Entities + Triples (CSV, TTL)
    ↓
[Phase 2] Ontology Modeling (Protégé)
    ↓
Ontology.owl + Properties.ttl
    ↓
[Phase 3] Apache Jena Fuseki (SPARQL Endpoint)
    ↓
[Phase 4] Python Interface (SPARQLWrapper + GUI)
```

---

## 📘 **Technologies Used**

| Category | Tools / Frameworks |
|-----------|--------------------|
| NER Extraction | Python, spaCy, pandas |
| Ontology Design | Protégé, RDF/OWL, Turtle |
| Knowledge Storage | Apache Jena Fuseki, Jena TDB |
| Interface | Python, SPARQLWrapper, Flask/Tkinter |

---

## 🧑‍🤝‍🧑 **Team Roles**

| Role | Responsibility |
|------|----------------|
| NER Engineer | Extract entities using spaCy |
| Ontology Architect | Design ontology classes & properties in Protégé |
| Jena Engineer | Load ontology into Jena & setup SPARQL endpoint |
| Python Developer | Build SPARQL interface and GUI |

---

## 🏁 **Final Notes**
- All data and knowledge structures are specific to the topic *Cultural Differences in Pakistan*.  
- Ensure namespaces remain consistent (`http://example.org/culturaldifference#`).  
- Before moving between phases, always validate your RDF/OWL syntax in Protégé.  
- The full ontology (`ontology.owl`) serves as the main dataset for future reasoning and querying.

---

### 👨‍💻 Maintainers
- **Ontology Team:** [Your Name / Group Member]  
- **Jena Team:** [Member Name]  
- **Python Interface Team:** [Member Name]  
