---
name: visa-doc-filler
description: "Filling and generating visa documents. Use this skill when the user provides a Word document (.docx) template to fill in, or needs to create visa support materials from scratch (cover letters, itineraries, invitation letters, employment certificates, etc.). Also applies whenever the user provides any official/government Word template to be filled. Supports reading user materials in formats such as PDF and Word, and handles unpacking .docx templates, field identification, content filling, format preservation, and repacking."
---

# Visa Document Filling Assistant

Helps users fill out visa application documents and generate visa support materials, with built-in .docx format handling.

## Core Principle

A .docx file is essentially a ZIP archive containing XML files. To modify content while preserving formatting, the flow is: unzip into XML → modify only the text nodes → repack. This skill ships with all the scripts needed to complete this flow.

## Quick Reference

| Task | How |
|------|------|
| Fill in a .docx template provided by the user | Unpack → edit XML → repack (see workflow below) |
| View .docx content | View the file content directly |
| Create a visa document from scratch | Use `../scripts/create_docx.py --style general` (see `../references/docx-creation-guide.md`) |
| Read a PDF file | Use the Read tool directly (native PDF-to-text support) |
| Read images (passport, ID) | Use the Read tool directly (supports jpg/png/gif/webp) |

---

## Scripts

All scripts are the shared general-purpose ones under `../scripts/` (zero external dependencies for `docx_edit.py`; `create_docx.py` deps are installed automatically by `uv run`).

| Script | Purpose |
|------|------|
| `../scripts/docx_edit.py` | Shared Word unpack/pack/replace tool. On unpack, automatically merges adjacent `<w:r>` elements with identical formatting to reduce XML fragmentation; on pack, automatically fixes `xml:space="preserve"` whitespace issues. For template filling use `unpack`/`pack` and edit the XML manually |
| `../scripts/create_docx.py` | Markdown → .docx generator. When creating visa support documents from scratch, output Markdown text and generate with `--style general` |

---

## Workflow (Editing an Existing Document)

When the user gives you a .docx template or a document to modify, follow these steps.

### Step 1: Read the User's Materials

The user may also provide personal materials (resume, passport scan, etc.), which could be in these formats:
- **Word (.docx)** — view the file content
- **PDF** — use the Read tool directly (auto-converted to text)
- **Image** — use the Read tool to view (supports jpg/png/gif/webp)
- **Plain text** — read directly

From these, extract key fields such as name, passport number, date of birth, and employment information.

### Step 2: Analyze the Template Content

View the template file content to determine which fields need to be filled in (e.g., placeholders like `____________`, `☐`, `☑`).

### Step 3: Search for the Destination Country's Official Visa Requirements

Call the search tool to search for the country's latest visa requirements, obtaining the official document checklist, field specifications, and recent policy changes. Cross-check the search results against the corresponding country visa reference file (`references/visa-*.md`) to ensure the content you fill in complies with the latest policy.

### Step 4: Unpack the Template Document

```bash
uv run ../scripts/docx_edit.py unpack template.docx unpacked/
```

This unzips the ZIP into the `unpacked/` directory, formats the XML to make it readable, and merges adjacent text nodes with identical formatting.

### Step 5: Collect Missing Information

Ask the user for any missing information. Note:
- Group related questions together
- Compute what can be computed (e.g., derive the length of stay from the departure and return dates)
- Refer to `references/field-mappings.md` to confirm which fields and formats are needed

### Step 6: Edit the XML

Use editing tools to modify `unpacked/word/document.xml` (and other XML files such as headers and footers) directly.

**Core principle: only change the text inside `<w:t>` elements, and never touch `<w:rPr>` (the formatting tags).**

```xml
<!-- Before: placeholder -->
<w:r>
  <w:rPr><w:sz w:val="24"/><w:u w:val="single"/></w:rPr>
  <w:t>____________</w:t>
</w:r>

<!-- After: content filled in, formatting preserved automatically -->
<w:r>
  <w:rPr><w:sz w:val="24"/><w:u w:val="single"/></w:rPr>
  <w:t>ZHANG SAN</w:t>
</w:r>
```

**Handling repeated placeholders:** templates often contain multiple identical `____________`. Editing tools require a unique match, so **include enough context** in the old_string (the tags and text before and after the placeholder) to ensure each replacement precisely hits the intended target.

For more XML editing patterns and caveats, see `references/docx-editing-guide.md`.

### Step 7: Repack the Output

```bash
uv run ../scripts/docx_edit.py pack unpacked/ filled.docx
```

On repack, whitespace issues (`xml:space="preserve"`) are fixed automatically, the XML is condensed, and the final .docx file is generated.

---

## Creating Documents from Scratch

When the user needs to create brand-new visa support materials (rather than filling in a template):

1. **Call the search tool** to search for the destination country's latest official visa requirements and document checklist, ensuring the document you create complies with the current policy
2. Read the corresponding country visa reference file to obtain the form field structure and template format
3. Refer to `references/common-visa-docs.md` to choose the appropriate document structure, **supplementing it with the latest requirements from the search results**
4. Write the document content as Markdown (see `../references/docx-creation-guide.md` for supported elements)
5. Generate the `.docx` with `uv run ../scripts/create_docx.py content.md output.docx --style general`

---

## Destination Country Identification and Routing

Based on the destination country/region the user mentions, read the corresponding visa reference file to obtain that country's form structure, field formats, and support material templates:

| User intent signal | Reference file to read |
|------------|--------------|
| United States, US visa, DS-160, B1/B2, traveling to the US | `references/visa-us.md` |
| Japan, Japan visa, traveling to Japan, 査証 | `references/visa-japan.md` |
| South Korea, Korea visa, traveling to Korea, 비자 | `references/visa-korea.md` |
| Schengen, France, Germany, Italy, Spain, Netherlands, Switzerland, European visa | `references/visa-schengen.md` |
| United Kingdom, UK visa, traveling to the UK | `references/visa-uk.md` |
| Country not specified | Confirm the destination country with the user first, then read the corresponding reference file |

**Execution steps:**
1. Identify the destination country/region from the user's question
2. **Call the search tool** to search for the country's latest official visa requirements (example search terms: `{country name} visa application requirements 2026`, `{country name} visa latest requirements document checklist`), focusing on:
   - The latest visa types and eligibility conditions
   - The officially required document checklist
   - Current fee standards and processing times
   - Recent policy changes (e.g., visa waivers, e-visas, expedited channels)
3. Read the corresponding country visa reference file and **cross-check** it against the search results: the reference provides the form field structure and document templates, while the search results provide the latest policy and requirements
4. If the search results conflict with the reference file (e.g., fee changes, newly added document requirements), **treat the latest official information from the search as authoritative**, and flag the change to the user in the output
5. Fill in or generate documents according to the country's date format, name rules, and field requirements
6. **All visa-related deliverables (application letters, employment certificates, itineraries, proof of funds, etc.) must be produced in both a Chinese version and an English version**

---

## Bilingual Output (Mandatory)

All visa-related document deliverables must be provided in two versions: **a Chinese version + an English version**:

- When creating documents from scratch: generate a Chinese .docx and an English .docx separately (or mark the sections within a single document)
- When filling in a template: fill it in the template's language, and attach the corresponding translated version
- Each country's visa reference file already contains bilingual (Chinese + English) templates — use them directly
- The English version should use formal, concise wording consistent with visa material conventions

---

## Reference Files

Read them as needed; do not load them all at once:

### Country/Region-Specific References (read when the corresponding country is identified)

| File | When to read | Content |
|------|---------|------|
| `references/visa-us.md` | When the user is applying for a US visa | The full field structure of the DS-160 form, US date format (MM/DD/YYYY), photo requirements, bilingual (Chinese + English) support material templates |
| `references/visa-japan.md` | When the user is applying for a Japan visa | All fields of the Japan visa application form (査証申請書), date format (DD.MMM.YYYY), agency requirements, bilingual materials |
| `references/visa-korea.md` | When the user is applying for a South Korea visa | All fields of the Korea visa form, date format (YYYY/MM/DD), Chinese-character name requirements, visa category codes, bilingual materials |
| `references/visa-schengen.md` | When the user is applying for a Schengen visa | All fields of the Schengen uniform form, date format (DD/MM/YYYY), multi-country itinerary planning, travel insurance requirements, bilingual materials |
| `references/visa-uk.md` | When the user is applying for a UK visa | The seven sections of the UK online application form, budget reference, GWF number explanation, travel history requirements, bilingual materials |

### General References

| File | When to read | Content |
|------|---------|------|
| `references/common-visa-docs.md` | When creating visa support documents from scratch | Complete templates and essential elements for visa cover letters, itineraries, invitation letters, employment certificates, proof of funds, hotel booking confirmations, etc. |
| `references/field-mappings.md` | When filling in visa form fields | Each country's date format rules, name order (surname first / given name first), Chinese-English-Japanese field translation mappings, currency code formats |
| `../references/docx-editing-guide.md` | When editing the XML of an existing .docx | End-to-end unpack → edit → repack guide, covering whitespace handling (xml:space), image insertion, smart-quote escaping, etc. |
| `../references/docx-creation-guide.md` | When creating a .docx from scratch with `create_docx.py` | Markdown → docx guide (styles, supported Markdown elements, tables, images, formulas, etc.) |

---

## Common Scenarios

### Scenario 1: The user provides a template that already has content
1. Extract the text to see what is filled in and what is empty
2. Ask only about the missing information
3. Unpack → fill in the blanks → repack

### Scenario 2: The user provides a blank template
1. Extract the text to identify all fields
2. Systematically collect all required information
3. Unpack → fill in each field → repack

### Scenario 3: The user needs to create a document from scratch
1. Determine the document type (cover letter, itinerary, etc.)
2. Read the corresponding reference file
3. Write the content as Markdown and generate a professionally formatted document with `../scripts/create_docx.py --style general`

### Scenario 4: The user provides materials in PDF/image format
1. Use the Read tool to read the PDF or image directly
2. Extract the needed information from it
3. Fill it into the .docx template

---

## Filling Quality Points

- **Names must exactly match the passport** — use uppercase letters and mind the order (surname first vs. given name first)
- **Date formats must be correct** — different countries require different formats: US MM/DD/YYYY, Japan DD.MMM.YYYY, Korea YYYY/MM/DD, Schengen/UK DD/MM/YYYY (see each country's reference file or `references/field-mappings.md`)
- **Amounts must include a currency code** (CNY/RMB, EUR, USD, GBP, JPY, KRW, etc.); it is recommended to note both the original RMB value and the converted value in the destination currency
- **Addresses are generally written in English** (unless the form explicitly requires Chinese)
- **Phone numbers must include the country code** (China +86)
- **Passport validity** must extend at least 6 months beyond the planned return date (Schengen requires at least 3 months) — remind the user if this is not met
- Use ☑ and ☐ for checkboxes (or match the characters the template itself uses)
- Formatting is inherited automatically — content filled in via XML editing automatically uses the original template's font and size
- **Bilingual output** — all visa support materials (application letters, employment certificates, itineraries, proof of funds, etc.) must be provided in both a Chinese version and an English version

---

## Dependencies

- **Python 3.10+** — the shared `../scripts/docx_edit.py` uses the standard library only
- Creating documents from scratch uses `../scripts/create_docx.py` (deps `python-docx`, `lxml`, `latex2mathml`); run it with `uv run`, which installs them automatically from the script's inline metadata
