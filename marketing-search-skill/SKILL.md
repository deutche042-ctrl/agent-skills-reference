---
name: marketing-search-skill
description: Perform financial or market analysis of a company based on its products, technology, and financial fundamentals, and provide structured conclusions with supporting evidence.
metadata:
  version: 1.0.0
---

This skill guides the model through a systematic, integrated analysis of one company's products, technology, and financial fundamentals, culminating in a structured research report.

## Use Cases and Objective

Trigger this skill when an in-depth fundamental analysis of a company is needed. Combine product and technology strengths with financial health to assess market position and future potential.

The final structured report must contain at least:

*   **Company overview:** Core business, market positioning, and brief development history.
*   **Product/technology highlights:** Key products, technology roadmap, competitive barriers, and innovation capabilities.
*   **Financial fundamentals:** Core financial metrics, profitability, cash flow, and capital structure.
*   **Market and competition:** Target-market analysis, competitive landscape, and company moat.
*   **Catalysts and risks:** Potential growth drivers and internal/external risks.
*   **Conclusion:** An integrated judgment of the company's value and outlook.

## Time Range and Timeliness

For accuracy, convert every relative-time expression, such as "the past two weeks," "this month," or "this year," into an exact date range based on the stated system date (`2026-01-29`).

Examples:

| Relative expression | Resolved date range (based on 2026-01-29) |
| :--- | :--- |
| Past two weeks | `2026-01-15` to `2026-01-29` |
| This month | `2026-01-01` to `2026-01-29` |
| This year | `2026-01-01` to `2026-01-29` |

## Tool Strategy and Order

Use this strategy to collect information efficiently and comprehensively:

1.  **Parallel initial exploration:** Prefer `general_search` with two or three parallel keyword queries, never more than three, covering different dimensions such as **products/technology**, **financial condition**, and **market competition**. Avoid duplicate searches on the same topic.
2.  **Deep content retrieval:** For search-result links whose summaries appear valuable and may contain deeper insights, use `web.fetch` to read the full content. `web.fetch` can parse webpages and documents (doc/ppt/excel/txt/markdown/pdf), but not audio or video.
3.  **Supplementary specialist information:**
    *   Use `scholar_search` when technical detail or academic-paper support is needed.
    *   Use `image_search` for real images of company products, facilities, or key people.
    *   Use `visual_search` to find the source of a reference image or similar content.
4.  **Access barriers:** If a webpage presents a login wall, CAPTCHA, or another interactive obstacle, use `open_url_in_browser` and request user assistance through `AskHumanToControlBrowser`.

## Recommended Source Priority

To maximize accuracy and authority, prioritize these sources and cross-check information:

1.  **Official and regulatory sources:** Company websites, especially investor-relations pages; official press releases; and regulatory filings such as 10-K, 10-Q, 8-K, and S-1 filings in SEC EDGAR.
2.  **Authoritative business databases:** Crunchbase, PitchBook, and similar sources for structured data such as funding history and corporate structure.
3.  **Leading financial media and industry reports:** Reputable outlets such as Bloomberg and Reuters and reports from recognized research institutions.
4.  **Specialist databases:** Patent databases such as USPTO or clinical-trial registries such as FDA resources and ClinicalTrials.gov for relevant industries.

If a paywall is encountered, disclose it in the report and actively seek an alternative free source.

## Financial-Fundamental Analysis

Focus the financial analysis on earnings quality, growth potential, and financial health:

*   **Revenue and profit:** Analyze trends in revenue growth, gross margin, and operating margin.
*   **Cash flow:** Assess operating-cash-flow health and free cash flow.
*   **Capital structure:** Evaluate cash reserves, debt levels, and capital-expenditure plans.
*   **Unit economics:** Estimate customer-acquisition cost (CAC) and lifetime value (LTV) to assess business-model sustainability.
*   **Human capital:** Cross-check headcount and changes in key talent through LinkedIn, the company website, and other channels.

## Product, Technology, and Market Analysis

Assess the company's core competitiveness and market position:

*   **Technology and barriers:** Examine the uniqueness of the technology roadmap, patent portfolio, and technical moat.
*   **Regulation and compliance:** Identify key regulatory requirements and compliance risks in the company's industry.
*   **Business model:** Analyze revenue model, sales channels, and customer segments.
*   **Market size and structure:** Estimate TAM/SAM/SOM, identify major competitors, and analyze differentiation.
*   **Pricing and gross margin:** Examine product-pricing strategy and its effect on gross margin.

## Corroboration and Credibility

Evaluate all information carefully. Score sources according to `references/scoring_standard.md` across five dimensions: authority, timeliness, corroboration, originality, and expertise. When information conflicts, clearly identify the disagreement in the report and describe the verification paths attempted, such as additional searching, reverse lookup, or locating primary documents.

## Output and Delivery

The final report must be clear, structured, and suitable for reading and decision support.

*   **Structured executive summary:** Open with a concise summary of key findings.
*   **Key-point tables:** Use tables where appropriate for critical comparisons such as financial metrics and competitor analysis.
*   **Source list:** Append every cited source and URL at the end.
*   **Cautious wording:** Qualify uncertain information and forecasts with wording such as "estimated," "may," or "according to the analysis."

Use structured Markdown for output.

## Error Handling and Notes

*   **Avoid redundant work:** Plan keywords before searching and avoid unnecessary duplicate searches for already retrieved information.
*   **Use tools precisely:** Use `image_search` for real images, not abstract diagrams or charts.
*   **Remain neutral and objective:** Do not make categorical judgments about unverified claims or rumors.
*   **Record limitations:** When access restrictions such as paywalls prevent retrieval of key information, record the limitation and attempted alternatives in the report.

## Version and Maintenance

*   **Version:** `1.0.0`.
*   **Maintenance:** This skill is iterated periodically based on practical results and user feedback.
*   **References:** See `scoring_standard.md` and `question_category.md` under `references/` for detailed scoring standards and question-classification methods.
