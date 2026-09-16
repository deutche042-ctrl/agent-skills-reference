---
name: authoritative-database-query-skill
description: Provides in-depth, complex, authoritative data retrieval and analysis capabilities; teaches the model to run precise queries against authoritative database websites and prioritize browser GUI tools for interaction and extraction
metadata:
  version: 1.1.0
---

# In-Depth Retrieval and Analysis on Authoritative Database Websites

This Skill is explicitly intended to guide the model through discovery, filtering, extraction, and cross-validation on the official websites of authoritative databases when in-depth, complex, authoritative data research and analysis is required. For tool selection, access databases through APIs first; secondarily, use browser GUI tools for page-level interaction; fall back to external search for discovery only when necessary.

## 1. Scope and Trigger Scenarios

Prioritize this Skill when the user's question involves any of the following areas and requires trustworthy, public data sources.

- **Fact and data checking:** Verify specific numbers, dates, statistics, or factual claims.
- **Academic and research queries:** Find papers, journals, research projects, citation data, and related materials.
- **Macroeconomic and social statistics:** Obtain national, regional, or global economic indicators, population data, development indexes, and similar data.
- **Legal and regulatory research:** Query statutes, case law, and official public-company disclosures (such as 10-K/10-Q filings) for a specific country or region.
- **Patents and intellectual property:** Search for registered or pending patents.
- **Geographic and spatial information:** Obtain coordinates, map data, administrative divisions, natural landforms, and related information.
- **Scientific and biomedical data:** Query chemical substances, protein sequences, genomic data, clinical trial information, and related data.
- **Company and organization information:** Find corporate registration information, organizational structures, and similar records.
- **General knowledge and knowledge graphs:** Use when structured, verifiable general knowledge is required.

## 2. GUI Tool Priority and Operating Principles

### Browser Toolset (GUI)
- Available actions: click, left_double, right_single, drag, scroll, move_to, mouse_down, mouse_up, type, hotkey, press, release, wait, take_screenshot, open_url_in_browser, AskHumanToControlBrowser

### Core Principles
- Official websites first: Complete retrieval and filtering directly on the official pages of authoritative data sources.
- GUI interaction first: Use site search boxes, filters, download buttons, and similar controls to reduce reliance on third-party summaries or unofficial pages.
- Identifiers and provenance: Preserve authoritative identifiers such as DOI, PMID, FRED Series ID, and OSM ID in the results.
- Cross-validation: Recheck key conclusions against an alternative authoritative source; verify collaborative content a second time.
- APIs first: When an official API/developer interface exists (REST, SPARQL, SDMX, etc.), query it through code first; use the GUI only as a fallback.
 - Retention criterion: In “4. Database Categories and Official-Site Navigation,” retain only sites that cannot be queried through official interfaces; list sites with public interfaces together in “4.10 API Priority and Code Integration.”

## 3. Overall Workflow (Website GUI)

Follow these steps to obtain reliable results in a website GUI environment:

1. Understand the question: Clarify the entities, indicators, dimensions, and time range.
2. Identify the domain: Determine the relevant website category and preferred authoritative website.
3. Open the official site: Use open_url_in_browser to go directly to the homepage or data entry point.
4. Search and filter on-site: Use type to enter keywords; use click/scroll to operate filters, download data, or expand details.
5. Extract and record: Use take_screenshot on detail pages as evidence; record authoritative identifiers and direct links.
6. Cross-validate: Repeat the query or compare results on an alternative authoritative website.
7. Follow the output standard: Summarize in Chinese and include sources and identifiers.

## 4. Database Category Directory and Selection Principles

### Category Directory
- Academic literature: See [academic-literature.md](./assets/academic-literature.md)
- Statistics and macroeconomics: See [macroeconomics.md](./assets/macroeconomics.md)
- Regulations and disclosures: See [regulations-disclosures.md](./assets/regulations-disclosures.md)
- Patents: See [patents.md](./assets/patents.md)
- Company registration information: See [company-registries.md](./assets/company-registries.md)
- Geographic and spatial data: See [geospatial.md](./assets/geospatial.md)
- Scientific and public data: See [science-public-data.md](./assets/science-public-data.md)
- Knowledge graphs and general knowledge: See [knowledge-graph.md](./assets/knowledge-graph.md)
- Technology consulting and industry reports: See [tech-consulting.md](./assets/tech-consulting.md)

### Selection Principles
- Select the corresponding asset file based on the question type
- If an official API exists, prefer programmatic querying; use the GUI for data unavailable through interfaces or for page details
- Preserve authoritative identifiers and source links in the output, and cross-validate as needed
### 4.1 Academic Literature
Retain only Chinese-language sources and sources without public interfaces; for academic sites with APIs, see 4.10

See [academic-literature.md](./assets/academic-literature.md)

### 4.4 Patents
See [patents.md](./assets/patents.md)

### 4.6 Geographic and Spatial Data
See [geospatial.md](./assets/geospatial.md)

### 4.9 Technology Consulting and Industry Reports
See [tech-consulting.md](./assets/tech-consulting.md)

### 4.10 Usage and Script Invocation
- After selecting a category, open the corresponding file under assets for GUI operation guidance and API integration methods.
- When programmatic querying is available, call functions under scripts first to obtain standardized data and reduce time spent on page interactions.
- See [data_api.py](./scripts/data_api.py) for function entry points and examples.

## 5. Query Parameters and Authoritative Identifiers

Use standardized authoritative identifiers whenever possible to improve query precision.

- **Academic literature:**
    - **DOI (Digital Object Identifier):** For example, `10.1038/nature12345`. The preferred identifier.
    - **PMID (PubMed ID):** For example, `25355208`. Used for biomedical literature.
    - **arXiv ID:** For example, `1706.03762`. Used for preprints.
- **Statistical data:**
    - **FRED Series ID:** For example, `GDPCA` (real GDP). Used for FRED data.
    - **World Bank Indicator Code:** For example, `NY.GDP.MKTP.CD` (GDP at current market prices in current US dollars).
- **Scientific data:**
    - **CAS Registry Number:** For example, `50-78-2` (aspirin). Used for chemical substances.
    - **UniProt ID / Accession:** For example, `P04637` (human P53 protein).
- **Geospatial data:**
    - **OpenStreetMap ID:** For example, `node/25494147`, `way/4322989`, `relation/118784`. Used for OSM map features.

Explicitly include these identifiers in the output to support provenance and verification.

## 6. Parallelization and Fallback Strategy (GUI)

- Parallel queries: Open separate browser tabs for different subquestions and perform GUI operations independently, with no more than three lines of inquiry in parallel.
  - Example split: Apple's latest 10-K (EDGAR tab) / Tim Cook's Wikidata ID (Wikidata tab) / Apple-related patents (Lens tab).
- Fallback strategy: Only when official-site search is ineffective or the entry point is difficult to locate, use external search to find the official page. Recommended qualifiers:
  - `site:sec.gov Apple 10-K`
  - `site:wikidata.org Tim Cook`
  - `site:lens.org assignee:"Apple Inc."`

## 7. Quality Control and Caveats

- **Authority first:** Always prioritize data published by governments, international organizations, leading academic institutions, or reputable open industry platforms. Treat personal blogs, forums, and unreviewed collaborative content with caution.
- **Timeliness:** Note the publication dates of data and literature. For statistics, prefer the latest version; for regulations and patents, check their current status (in force, expired, or superseded).
- **Tool boundaries:**
  - Do not use image-recognition tools to parse abstract tables or regulatory text.
  - When account login or verification is involved, request user assistance through AskHumanToControlBrowser.

## 8. Output Standards

All final query outputs must follow these standards:

1. **Summarize in clear Chinese:** Answer the user's question directly and distill the key information.
2. **Provide verifiable sources:** At the end of the conclusion, include a “Sources” or “References” section listing direct links to every information source.
3. **Include authoritative identifiers:** Where appropriate, include relevant authoritative IDs to improve professionalism and traceability.

- Literature output example:
  > According to the OpenAlex and Crossref records, Paper X has DOI 10.1234/abcdef, and its main contribution is...
  > - Source: Article record page
  > - DOI: `10.1234/abcdef`

- Statistical output example:
  > According to the World Bank data portal, Germany's unemployment rates over the past decade are as follows (unit: %), with the latest year being...
  > - Source: World Bank indicator page
  > - Indicator code: `SL.UEM.TOTL.ZS`

- Geographic output example:
  > The Statue of Liberty's coordinates are verified by OSM as..., with feature ID...
  > - Source: OpenStreetMap feature page
  > - OSM ID: `node/357382898`
