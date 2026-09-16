# Academic Literature

## Use Cases
- Search papers, journals, conference articles, preprints, and citation data
- Retrieve authoritative identifiers (DOI, PMID, arXiv ID) and source links

## Common Methods
- API first: use open interfaces for exact searches by keyword, author, or DOI
- GUI fallback: use when data is unavailable through an interface or page-level filtering is required

## GUI Guidance
- Enter keywords or identifiers in the official website's search box
- Use filters to narrow results by year, category, language, and topic
- Open the record page and capture the title, authors, year, identifier, and source link
- Cross-check critical information, for example against two authoritative sources

## API and Programmatic Access
- OpenAlex API example: `/works?search=keyword`
- Crossref REST example: `/works?query=keyword`
- arXiv API example: the export API query endpoint
- PubMed E-Utilities example: `esearch` + `efetch`
- DOAJ API example: article search endpoint

## Authoritative Sources and URLs
- OpenAlex: https://openalex.org / API: https://api.openalex.org
- Crossref: https://www.crossref.org / API: https://api.crossref.org
- arXiv: https://arxiv.org / API: http://export.arxiv.org/api/query
- PubMed: https://pubmed.ncbi.nlm.nih.gov / E-Utilities: https://eutils.ncbi.nlm.nih.gov
- DOAJ: https://doaj.org / API: https://doaj.org/api

## Example Tasks
- Find a review of graph neural networks in recommender systems and return its title, DOI, and source link
- Retrieve record details and citation counts by DOI, and report the identifier
