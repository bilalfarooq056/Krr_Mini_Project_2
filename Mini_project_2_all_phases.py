#!/usr/bin/env python
# coding: utf-8

# ### mini_Project_2 group partner names:
# - Bilal Farooq
# - Saad Khan
# - Washam Bin Adnan
# - Alam Zeb
# 

# ## Phase 1 NER Extraction

# Make RDF's and then ceate classes object properties

# > Phase 1: NER Extraction (3-4 days)
# 1. text source (research abstracts/news articles) will be given per group
# 2. Use spaCy's pre-trained NER to extract:
# 3. Example: Persons, Organizations, And Locations, Additional: Dates, Money, etc.
# 4. Save extracted entities to CSV

# In[ ]:


# ------- cultural differences in pakistan --------


# save as ner_crawl_spacy.py
import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import spacy
from urllib.parse import urlparse
from tqdm import tqdm
import pandas as pd

# Choose model: en_core_web_sm (fast) or en_core_web_trf (better, heavy)
MODEL_NAME = "en_core_web_sm"
nlp = spacy.load(MODEL_NAME)

# List of source URLs (the curated list above)
URLS = [
    "https://scientiamag.org/the-cultural-diversity-of-pakistan/",
    # (2)
    "https://ideas.repec.org/a/rss/jnljms/v4i6p3.html",
    # (3)
    "https://www.scirp.org/journal/paperinformation?paperid=114000",
    # (4)
    "https://www.jstor.org/stable/2645700",
    # (5)
    "https://www.dawn.com/news/1865983",
    # (6)
    "https://www.richtmann.org/journal/index.php/mjss/article/download/10805/10421/41480",
    # (7)
    "https://www.researchgate.net/publication/374433555_Impact_of_Cultural_Norms_and_Social_Expectations_for_Shaping_Gender_Disparities_in_Educational_Attainment_in_Pakistan",
    # (8)
    "https://www.britannica.com/place/Pakistan/People",
    # (9)
    "https://www.researchgate.net/publication/260259174_Cultural_Diversity_in_Pakistan_National_vs_Provincial",
    # (10)
    "https://bmcwomenshealth.biomedcentral.com/articles/10.1186/s12905-022-02011-6",
    # (11)
    "https://www.researchgate.net/publication/249973777_Language_and_Ethnicity_in_Pakistan",
    # (12)
    "https://www.jsshuok.com/oj/index.php/jssh/article/download/181/154",
    # (13)
    "https://www.richtmann.org/journal/index.php/mjss/article/view/10805/10421",
    # (14)
    "https://www.socialsciencejournals.pjgs-ws.com/index.php/PJGS/article/view/752",
    # (15)
    "https://www.rjelal.com/5.4.17a/282-297%20JAVED%20IQBAL%20BERKI.pdf",
    # (16)
    "https://moderndiplomacy.eu/2023/03/11/diversity-in-pakistan-a-strength-or-weakness/",
    # (17)
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC3208374/",
    # (18)
    "https://en.wikipedia.org/wiki/Languages_of_Pakistan",
    # (19)
    "https://assajournal.com/index.php/36/article/view/303",
    # (20)
    "https://pjhc.nihcr.edu.pk/wp-content/uploads/2023/02/1-Farhan-Siddiqi.pdf",
    # (21)
    "https://pjsel.jehanf.com/index.php/journal/article/view/1082",
    # (22)
    "https://remittancesreview.com/menu-script/index.php/remittances/article/download/2617/2141/6198",
    # (23) Reuters
    "https://www.reuters.com/world/asia-pacific/wow-how-driving-school-programme-empowers-pakistani-women-2024-12-30/",
    # (24) Guardian
    "https://www.theguardian.com/artanddesign/2024/dec/30/our-art-is-a-mirror-of-truth-pakistan-manzar-art-architecture-exhibition-national-museum-quatar",
    # (25) AP
    "https://apnews.com/article/956613fb40cf6fd5c1f329b5a12befc8",
    # (26)
    "https://www.london.ac.uk/news-events/student-blog/celebrating-culture-pakistan",
    # (27)
    "https://en.wikipedia.org/wiki/Marriage_in_Pakistan",
    # (28)
    "https://www.marjjan.com/blogs/fashion/traditional-pakistani-dresses-exploring-regional-styles-and-designs",
    # (29)
    "https://www.tastepak.com/p/culinary-diversity-unveiled-a-journey-through-the-regional-cuisines-of-pakistan",
    # (30)
    "https://travelpakistani.com/blogs/most-popular-cultural-festivals-in-pakistan/361",
    # (31)
    "https://www.globetrottingbooklovers.com/blog/a-wedding-in-pakistan",
    # (32)
    "https://en.wikipedia.org/wiki/Pakistani_clothing",
    # (33)
    "https://www.researchgate.net/publication/395381499_World_Cuisine_Pakistani_Cuisine_-_Street_Food",
    # (34)
    "https://www.researchgate.net/publication/392692831_ETHNIC_VS_WESTERN_ATTIRE_IN_THE_PAKISTANI_WORKPLACE_A_STUDY_OF_IDENTITY_CULTURE_AND_PROFESSIONALISM",
    # (35)
    "https://blog.google/around-the-globe/google-asia/explore-pakistans-diverse-culinary-heritage/",
    # (36)
    "https://apnews.com/article/17303312be7993d7fd6cc597e8a3a008",
    # (37)
    "https://apnews.com/article/bbebc541b403875a15c675bab353821c",
    # (38)
    "https://www.theguardian.com/world/2025/jan/27/stories-woven-in-cloth-in-pakistans-first-textile-museum"
]

# Which entity labels to keep/save (spaCy labels)
KEEP_LABELS = {"PERSON","ORG","GPE","LOC","DATE","MONEY","NORP","LANGUAGE"}

def fetch_text_from_url(url, timeout=12):
    """Fetch visible text from a URL. Return (text, content_type). Skips PDFs for now."""
    try:
        head = requests.head(url, allow_redirects=True, timeout=8)
        ctype = head.headers.get("content-type","")
        if "pdf" in ctype.lower() or url.lower().endswith(".pdf"):
            return None, "pdf"
    except Exception:
        # fallback to GET if HEAD fails
        pass

    try:
        resp = requests.get(url, timeout=12, headers={"User-Agent":"Mozilla/5.0 (compatible; NER-bot/1.0)"})
        if resp.status_code != 200:
            return None, f"error:{resp.status_code}"
        ctype = resp.headers.get("content-type","")
        if "pdf" in ctype.lower():
            return None, "pdf"
        soup = BeautifulSoup(resp.text, "html.parser")
        # remove scripts/styles and nav/footer potential noise
        for s in soup(["script","style","header","footer","nav","aside","form","noscript"]):
            s.extract()
        texts = []
        # Prefer article/body tags
        article = soup.find("article")
        if article:
            texts.append(article.get_text(separator=" ", strip=True))
        body = soup.find("body")
        if body:
            texts.append(body.get_text(separator=" ", strip=True))
        full = " ".join(t for t in texts if t)
        # shorten repeating whitespace
        full = re.sub(r"\s+", " ", full).strip()
        return full[:500000], ctype
    except Exception as e:
        return None, f"exception:{e}"

def extract_entities(text, url):
    doc = nlp(text)
    rows = []
    for ent in doc.ents:
        if ent.label_ in KEEP_LABELS:
            # capture sentence for context
            sent = ent.sent.text.strip() if ent.sent else ""
            rows.append({
                "source_url": url,
                "entity_text": ent.text,
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                "context_sentence": sent
            })
    return rows

# Main loop
all_rows = []
errors = []
for url in tqdm(URLS, desc="Processing URLs"):
    text, ctype = fetch_text_from_url(url)
    if text is None:
        errors.append((url, ctype))
        time.sleep(0.5)
        continue
    # Optional: chunk long text into paragraphs to avoid spaCy memory spikes
    paragraphs = [p.strip() for p in re.split(r"\n{1,}|\.\s{2,}", text) if len(p.strip())>30]
    for para in paragraphs:
        try:
            rows = extract_entities(para, url)
            all_rows.extend(rows)
        except Exception as e:
            errors.append((url, f"ner_error:{e}"))
    time.sleep(0.8)  # polite delay

# Save to CSV
df = pd.DataFrame(all_rows)
if df.shape[0]==0:
    print("No entities extracted. Check model or pages.")
else:
    df = df[["source_url","entity_text","label","start_char","end_char","context_sentence"]]
    df.to_csv("entities.csv", index=False, encoding="utf-8")
    print(f"Saved {len(df)} entities to entities.csv")

# Save errors for review
pd.DataFrame(errors, columns=["url","issue"]).to_csv("fetch_errors.csv", index=False)
print(f"Fetch errors saved to fetch_errors.csv (count={len(errors)})")


# > ### Make RDF Triples using CSV file created

# In[ ]:


#!/usr/bin/env python3
"""
Pipeline:
1) Read CSV (either raw texts or pre-extracted entities).
2) Run spaCy NER if `text` column exists -> save entities_extracted.csv
3) Build triples CSV and a Turtle RDF file (triples.csv, triples.ttl)
"""
import os, re, csv, pandas as pd
# save as ner_crawl_spacy.py
import re
import csv
import spacy

INPUT_PATH = "entities.csv"            # change as needed
OUT_ENTITIES = "entities_extracted.csv"
OUT_TRIPLES_CSV = "triples.csv"
OUT_RDF = "triples.ttl"

def make_uri(s):
    slug = re.sub(r'[^a-zA-Z0-9_]', '_', s.strip())[:120]
    return f"http://example.org/resource/{slug}"

df = pd.read_csv(INPUT_PATH)
print("Loaded", INPUT_PATH, "columns:", list(df.columns))

# If there's a text column, attempt spaCy extraction
entities_df = None
if 'text' in df.columns:
    try:
        nlp = spacy.load("en_core_web_sm")
        rows = []
        for idx, row in df.iterrows():
            text = str(row['text'])
            doc = nlp(text)
            for ent in doc.ents:
                rows.append({"source_row": idx, "text": text,
                             "entity_text": ent.text, "entity_label": ent.label_})
        entities_df = pd.DataFrame(rows)
    except Exception as e:
        print("spaCy not available or failed:", e)

# If spaCy not run, try to infer entity columns
if entities_df is None:
    if {'entity_text','label'}.issubset(df.columns):
        entities_df = df.rename(columns={'label':'entity_label'})[['entity_text','entity_label']].copy()
    else:
        # fallback: first column as entity_text
        entities_df = pd.DataFrame({
            'entity_text': df.iloc[:,0].astype(str),
            'entity_label': ['UNKNOWN'] * len(df)
        })

entities_df.to_csv(OUT_ENTITIES, index=False)
print("Entities saved to", OUT_ENTITIES)

# Build simple triples
triples = []
for i, r in entities_df.reset_index().iterrows():
    ent = str(r['entity_text']).strip()
    label = str(r.get('entity_label','UNKNOWN')).strip()
    subj = make_uri(ent + "_" + str(i))
    triples.append((subj, "rdf:type", f"http://example.org/ontology/{label}"))
    triples.append((subj, "rdfs:label", f"\"{ent}\""))
    triples.append((subj, "ex:hasText", f"\"{ent}\""))
    triples.append((subj, "ex:canonicalURI", make_uri(ent)))

# save triples CSV
with open(OUT_TRIPLES_CSV, 'w', newline='', encoding='utf-8') as fh:
    writer = csv.writer(fh)
    writer.writerow(['subject','predicate','object'])
    for s,p,o in triples:
        writer.writerow([s,p,o])
print("Triples CSV saved to", OUT_TRIPLES_CSV)

# write Turtle (basic)
with open(OUT_RDF, 'w', encoding='utf-8') as f:
    f.write('@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n')
    f.write('@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n')
    f.write('@prefix ex: <http://example.org/ontology/> .\n\n')
    for s,p,o in triples:
        subj = f"<{s}>"
        if p == "rdf:type":
            pred = "rdf:type"
            obj = f"<{o}>"
        elif p == "rdfs:label":
            pred = "rdfs:label"
            obj = o  # already quoted
        elif p == "ex:hasText":
            pred = "ex:hasText"
            obj = o
        elif p == "ex:canonicalURI":
            pred = "ex:canonicalURI"
            obj = f"<{o}>"
        else:
            pred = p
            obj = f"<{o}>"
        f.write(f"{subj} {pred} {obj} .\n")
print("Turtle saved to", OUT_RDF)


# ### Convert .ttl to RDF  file 

# In[ ]:


from rdflib import Graph
g = Graph()
g.parse("triples.ttl", format="turtle")
print("Triples loaded:", len(g))


# >What I did (Phase 1)
# 
# - Loaded your uploaded file: /mnt/data/entities.csv.
# - Detected columns: source_url, entity_text, label, start_char, end_char, context_sentence.
# 
# - Created an entities CSV (if needed) at: /mnt/data/entities_extracted.csv.
# 
# - Built a triples CSV (subject, predicate, object) at: /mnt/data/triples.csv.
# 
# - Add a properties file 'Cultural_difference_properties.ttl'
# 
# - Wrote an RDF Turtle file at: /mnt/data/triples.ttl.

# ---
# 

# ## Phase 2 Ontology Design
# ( Use of protege software to create classes and entitites )

# > Phase 2: Basic Ontology (3-4 days)
# 1. Design ontology with classes extracted from CSV e.g. if classes extracted are 2000 get 200 randomly
# or manually as it makes sense for your domain.
# 2. Example: `Person`, `Organization`, `Location`, `Event`, `Document`
# 3. Add object properties: `worksFor`, `locatedIn`, `hasAuthor` just an example
# 4. Use any technique you like to map relations automatically rather than manually , be it machine
# learning model ,be it NLP model ,leverage existing resources as Wikidata or dbpedia
# 5. Create in Protégé, export as RDF/OWL

# > we need to create classes bsaed on 'label' in entities.csv dataset,
# > here are the steps i followed:
# <pre style="background-color: #464745ff; padding: 10px; border-left: 5px solid #b47124ff;">
# 
# - first extracted data from 38 different websites based on 'Topic Search', data collected was almost 13100, then this data used in NER Extraction
# three files created from this [ triples.ttl, triples.csv ], then later inserted a .ttl for ( Object properties and data properties )
# file named as 'cultural_difference_properties.ttl'
# 
# 1. Go to  --> [ Entity ] Create classes and subClasses 
# 2. Go to  --> [ Object Properties ]
# 3. Go To  --> [ Data Properties ]
# 4. Go To  --> [ Individuals ]
# </pre>
# 

# ---

# ## Phase 3 Knowledge Graph ( Appache Jena  )
# Turn entities.csv into RDF triples and load them into Jena Fuseki.

# > Phase 3: Apache Jena Setup (2-3 days)
# 1. Install Apache Jena Fuseki
# 2. Load ontology into Jena TDB
# 3. Set up SPARQL endpoint
# 4. Test basic queries

# Main reason for Uploading 

# > * Queries:
# 1. PREFIX : <http://example.org/culturaldifference#>
# SELECT ?s ?p ?o 
# WHERE { ?s ?p ?o } 
# LIMIT 50
# 
# 2. SELECT ?predicate (COUNT(?predicate) AS ?count)
# WHERE {
#   ?s ?predicate ?o .
# }
# GROUP BY ?predicate
# ORDER BY DESC(?count)
# LIMIT 10
# 
# 3. PREFIX : <http://example.org/culturaldifference#>
# SELECT ?class (COUNT(?instance) AS ?count)
# WHERE {
#   ?instance a ?class .
# }
# GROUP BY ?class
# ORDER BY DESC(?count)
# 
# 4. PREFIX : <http://example.org/ontology/>
# SELECT ?person
# WHERE {
#   ?person a :PERSON .
# }
# LIMIT 30
# 
# 5. PREFIX : <http://example.org/ontology/>
# SELECT ?org
# WHERE {
#   ?org a :ORG .
# }
# LIMIT 30
# 
# 6. PREFIX : <http://example.org/ontology/>
# SELECT ?lang
# WHERE {
#   ?lang a :LANGUAGE .
# }
# LIMIT 30
# 
# 7. PREFIX : <http://example.org/ontology/>
# SELECT ?loc
# WHERE {
#   ?loc a :LOC .
# }
# LIMIT 30
# 
# 8. PREFIX : <http://example.org/ontology/>
# SELECT ?gpe
# WHERE {
#   ?gpe a :GPE .
# }
# LIMIT 30
# 
# 9. PREFIX : <http://example.org/ontology/>
# SELECT ?entity ?class
# WHERE { ?entity a ?class . }
# LIMIT 20
# 
# 10. SELECT DISTINCT ?entity
# WHERE { ?entity ?p ?o . }
# LIMIT 50
# 
# 11. SELECT ?class (COUNT(?instance) AS ?count)
# WHERE {
#   ?instance a ?class .
# }
# GROUP BY ?class
# ORDER BY DESC(?count)
# 
# 12. PREFIX onto: <http://example.org/ontology/>
# 
# SELECT ?person
# WHERE { ?person a onto:PERSON . }
# LIMIT 20
# 
# 
# 13. PREFIX onto: <http://example.org/ontology/>
# 
# SELECT ?org
# WHERE { ?org a onto:ORG . }
# LIMIT 30
# 
# 
# 14. PREFIX onto: <http://example.org/ontology/>
# 
# SELECT ?region
# WHERE { ?region a onto:GPE . }
# LIMIT 30
# 
# 
# 15. PREFIX : <http://example.org/culturaldifference#>
# SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 50
# 
# 16. PREFIX : <http://example.org/culturaldifference#>
# SELECT ?class (COUNT(?x) AS ?count)
# WHERE { ?x a ?class . }
# GROUP BY ?class
# ORDER BY DESC(?count)
# 
# 17. PREFIX : <http://example.org/culturaldifference#>
# SELECT DISTINCT ?entity
# WHERE { ?entity ?p ?o }
# LIMIT 50
# 
# 18. PREFIX owl: <http://www.w3.org/2002/07/owl#>
# PREFIX : <http://example.org/culturaldifference#>
# SELECT DISTINCT ?property
# WHERE { ?property a owl:ObjectProperty . }
# 
# 19. PREFIX owl: <http://www.w3.org/2002/07/owl#>
# PREFIX : <http://example.org/culturaldifference#>
# SELECT DISTINCT ?property
# WHERE { ?property a owl:DatatypeProperty . }
# 
# 20. PREFIX : <http://example.org/culturaldifference#>
# SELECT ?s ?p ?o
# WHERE {
#   ?s ?p ?o .
#   FILTER(STRSTARTS(STR(?s), STR(:)))
# }
# LIMIT 50
# 
# 21. PREFIX : <http://example.org/culturaldifference#>
# SELECT ?person ?org
# WHERE { ?person :worksFor ?org . }
# 
# 22. PREFIX : <http://example.org/culturaldifference#>
# SELECT ?group ?language
# WHERE { ?group :speaksLanguage ?language . }
# 
# 23. PREFIX : <http://example.org/culturaldifference#>
# SELECT ?festival ?region
# WHERE { ?festival :hasFestivalIn ?region . }

# ---

# ## Phase 4 – Python Query Interface ()

# > Phase 4: Python Interface (3-4 days)
# 1. Create Python script using `SPARQLWrapper`
# 2. Implement functions: just an example
#  - a. `add_entity(entity_type, entity_name)`
#  - b. `query_entities(sparql_query)`
#  - c. `find_relationships(entity)`
# 3. Better use GUI

# # In last phase we creatd UI using streamlit
# - Components/Steps required for this process:
# 1. extract data
# 2. save data as csv and .ttl
# 3. then upload it into protege and make automation to create classes till individuals
# 4. extract this data into .OWL/RDF file
# 5. upload this file into Apache Jena ater installation
# 6. Run muliple queries to retrieve required data
# 7. use these queries and files to connect with streamlit app.
# 8. lastly make sure before starting the app you uploaded data into apacheJena and connect with it then start streamlit app by
# > 9. python -m streamlit run app.py

# 
