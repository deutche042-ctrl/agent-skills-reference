# Question Categories and Tool-Selection Guidance

This document recommends tools and keyword-design strategies for different types of analysis, improving search efficiency and precision.

## Common Analysis Types and Strategies

| Analysis Type | Core Need | Recommended Tools | Keyword Breakdown Guidance |
| :--- | :--- | :--- | :--- |
| **Company overview** | Quickly understand a company's core business, history, and market positioning. | Primarily use `general_search`; supplement it with `web.fetch` to read the “About Us” page on the company's official website. | **Primary company name/alias** + “what does it do” / “company profile” / “company history”. |
| **Product/technology analysis** | Explore a product's technical details, innovations, and competitive advantages. | Use `general_search` for reviews and technical white papers; `scholar_search` for relevant patents and academic papers; and `image_search` for product appearance and design. | **Primary company name** + **core product/technology name** (for example, “Tesla Autopilot”); **technology name** + “how it works” / “patent” / “review”. |
| **Financial fundamentals analysis** | Obtain and interpret financial data to assess profitability and financial health. | Use `general_search` for earnings releases, investor-relations presentations, and financial news; use `web.fetch` for close reading of SEC filings (10-K, 10-Q). | **Primary company name/ticker** + “financial results” / “income statement” / “revenue growth” / “gross margin” / “cash flow”. |
| **Market and competitive analysis** | Identify major competitors and analyze the market landscape and the company's differentiated advantages. | Use `general_search` to find industry reports, market-share data, and competitor comparisons. | **Primary company name** + “competitors” / “vs” / “alternatives”; **industry name** + “market share” / “competitive landscape”. |
| **Regulatory and compliance investigation** | Understand applicable laws and regulations, policy risks, and potential litigation. | Use `general_search` to find relevant news, announcements from regulators such as the FDA or SEC, and legal documents. | **Primary company name** + **regulator name** (for example, “FDA approval”) / “lawsuit” / “antitrust” / “regulation”. |
| **Capital-markets activity** | Track funding history, shareholder structure, and analyst ratings. | Use `general_search` to find Crunchbase or PitchBook pages, press releases, and analyst reports. | **Primary company name** + “funding” / “investors” / “analyst rating” / “share price”. |

## Keyword Design Principles

*   **Combine precision with expansion**: Use the “full company name + ticker” for precision, while also searching with company aliases or core product names to broaden coverage.
*   **Use professional terminology**: For financial or technical searches, industry-standard terms such as "EBITDA", "churn rate", and "SoC" produce more specialized results.
*   **Constrain source and time**: If supported by the tool, use the `site:` operator to limit searches to a specific website (for example, `site:sec.gov`) or add a year to filter results.
*   **Search in multiple languages**: For multinational companies, try English and other relevant languages to obtain more comprehensive information.
