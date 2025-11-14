

---

# 🧠 Knowledge Representation & Reasoning (KRR) — Mini Project 2

### **Topic:** *Cultural Differences in Pakistan*

### **Phases:** NER → Ontology → Jena → Python Interface → Streamlit GUI

---

## 📚 Overview

This project aims to represent knowledge about **Cultural Differences in Pakistan** using Semantic Web technologies.
It provides a complete pipeline starting from **Named Entity Recognition (NER)** → **Ontology Modeling** → **Apache Jena Fuseki SPARQL querying** → **Python/Streamlit GUI interface**.

---

# 📂 Project Structure (Based on ZIP)

```
Mini_project_2/
│
├── entities_extracted.csv
├── entities.csv
├── triples.csv
├── triples.ttl
│
├── cultural_difference_properties.ttl
├── culturaldifference_enriched.ttl
├── culture.rdf
│
├── queries.txt
├── insert query(culture).txt
├── jena running code.txt
│
├── app.py
├── Mini_project_2_all_phases.ipynb
│
└── README.md (this file)
```

---

# 🏗️ Phase 1 — Named Entity Recognition (NER)

### ✔️ Description

Extract cultural entities from text (spaCy) and convert them into RDF triples.

### 📌 Files

* `entities_extracted.csv`
* `entities.csv`
* `triples.csv`
* `triples.ttl`
* Code: *inside* `Mini_project_2_all_phases.ipynb`

### 📌 Output

* Cleaned NER results
* RDF triples in Turtle format

---

# 🧱 Phase 2 — Ontology Design (Protégé)

### ✔️ Description

Design domain ontology for cultural differences in Pakistan.

### 📌 Files

* `cultural_difference_properties.ttl`
* `culturaldifference_enriched.ttl`
* `culture.rdf`
* `triples.ttl`

### 📌 Modeling

* Classes: Person, CulturalGroup, Religion, Language, Festival, Organization, Location
* Object properties: speaksLanguage, celebratesFestival, follows, locatedIn
* Data properties: hasName, hasDescription, hasContextSentence

---

# 🧮 Phase 3 — Apache Jena Fuseki SPARQL Server

### ✔️ Description

Load ontology and RDF data into Fuseki for querying.

### 📌 Files

* `jena running code.txt`
* `queries.txt`
* `insert query(culture).txt`

### 📌 Steps

1. Download Apache Jena Fuseki

2. Run server:

   ```bash
   fuseki-server
   ```

3. Open:
   [http://localhost:3030/](http://localhost:3030/)

4. Create dataset

5. Upload:

   * `triples.ttl`
   * `cultural_difference_properties.ttl`
   * `culturaldifference_enriched.ttl`
   * `culture.rdf` (optional RDF/XML)

### 📌 Example SPARQL Query

```sparql
PREFIX : <http://example.org/culturaldifference#>
SELECT ?person ?lang WHERE {
    ?person a :Person ;
            :speaksLanguage ?lang .
}
```

---

# 🐍 Phase 4 — Python + Streamlit GUI Interface

### ✔️ Description

A simple GUI to test SPARQL queries on the Fuseki server.

### 📌 Files

* `app.py`

### 📌 Requirements

Install dependencies (Windows/Linux/Mac):

```bash
pip install streamlit SPARQLWrapper
```

### 📌 Run GUI

```bash
streamlit run app.py
```

---

# 🚀 Features

* ✔️ Fully automated entity extraction
* ✔️ Complete domain ontology
* ✔️ Jena Fuseki SPARQL endpoint
* ✔️ Ready-to-use Streamlit GUI
* ✔️ Works with real cultural data for Pakistan

---

# 🧩 Architecture Diagram

```
Text Source
    ↓
[Phase 1] NER Extraction (spaCy)
    ↓
triples.ttl + entities.csv
    ↓
[Phase 2] Ontology Modeling (Protégé)
    ↓
Ontology + Properties + Enriched TTL
    ↓
[Phase 3] Apache Jena Fuseki
    ↓
[Phase 4] Streamlit GUI (Python)
```

---

# 🧑‍🤝‍🧑 Contributors

| Name                 | Role                   |
| -------------------- | ---------------------- |
| **Bilal Farooq**     | Ontology Design        |
| **Alam Zeb**         | Ontology Design        |
| **Saad Khan**        | Jena Fuseki Setup      |
| **Washam Bin Adnan** | Python Interface + GUI |

---

# 🏁 Final Notes

* Always ensure your namespaces remain consistent:
  `http://example.org/culturaldifference#`
* Validate all TTL / OWL files using Protégé before loading into Fuseki.
* GUI requires a running Fuseki SPARQL endpoint.

---


Just tell me!
