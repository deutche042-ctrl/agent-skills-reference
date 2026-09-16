# Build Resume

Create resume content from scratch, or fill content into a template the user provides.

## Table of Contents

- [Scenario Detection](#scenario-detection)
- [Reading the User's File](#reading-the-users-file)
- [Filling a Template](#filling-a-template)
- [Building from Scratch](#building-from-scratch)
- [Content Organization Principles](#content-organization-principles)

---

## Scenario Detection

| Scenario | Approach |
|------|------|
| User gave a resume template (blank Word) | Unpack → understand structure → fill in content → pack |
| User gave an old resume (Word/PDF with content) | Extract content → edit and optimize → fill back into the original file |
| User gave nothing | Collect information through conversation → generate a new file |

---

## Reading the User's File

### Word / PDF files

Look at the file content to understand the resume's text and structure.

When you need to edit and fill back into a .docx, use `docx_edit.py unpack` to unpack it into an XML directory, modify the text in `unpacked/word/document.xml`, then pack it back up — the formatting is fully preserved.

A PDF can only be read, not filled back. If the user only has a PDF but needs an editable file:
- Ask the user to locate the original Word file
- Or generate a new Word file starting from the content

---

## Filling a Template

The user gave a resume template (a blank or half-empty Word file) that needs information filled in.

### Workflow

**1. Unpack the template and understand the structure**

```bash
uv run ../scripts/docx_edit.py unpack template.docx unpacked/
```

**2. Understand the placeholders in the XML**

Read `unpacked/word/document.xml` and find where the placeholder text sits in the XML. For example:

```xml
<w:r>
  <w:rPr><w:b/><w:sz w:val="28"/></w:rPr>
  <w:t>Enter your name here</w:t>
</w:r>
```

**3. Replace the placeholders**

Use editing tools to replace the placeholder text inside `<w:t>` with the real content. Leave `<w:rPr>` untouched — that is the key to preserving formatting.

```xml
<w:r>
  <w:rPr><w:b/><w:sz w:val="28"/></w:rPr>
  <w:t>Zhang San</w:t>
</w:r>
```

**4. Pack**

```bash
uv run ../scripts/docx_edit.py pack unpacked/ filled_resume.docx
```

### Notes

- A placeholder in the template may be split across multiple `<w:r>` runs (Word often does this); you need to manually merge the adjacent runs before replacing
- If a placeholder spans multiple runs, merge them into a single run before replacing
- Do not modify non-text content such as `<w:rPr>` (formatting properties), `<w:pPr>` (paragraph properties), or `<w:sectPr>` (page setup)

---

## Building from Scratch

When the user has neither a template nor an old resume, collect information through conversation.

### Collection order

Don't ask everything at once. Go step by step:

**Step 1: Basic information**
- Name, contact details
- Current/most recent job and title
- Target role (if any)

**Step 2: Work experience**
- Start from the most recent job and expand one at a time
- Ask for 3-5 core achievements per position
- If the user can't come up with them, switch to coaching mode (see `references/resume-coaching.md`)

**Step 3: Supplementary sections**
- Education, skills, projects, certifications, etc.

### Conversation opener

> "First, tell me about your most recent job — which company, what role, and how long were you there?"

Don't start with "what format do you want your resume in". Collect content first; format comes last.

### After collection is complete

Once content collection is done, you need to generate the file. There are two paths:

1. **Use `create_docx.py --style resume` to generate a new Word file** — write the résumé as Markdown and run the script; see `references/format-check.md` for formatting specs
2. **Use Typst to generate a PDF** — see the PDF generation section of `references/format-check.md`

---

## Content Organization Principles

### Achievement description formula

```
[strong action verb] + [what you did] + [technology/method] + [quantified result]
```

**Good examples:**
- Led the build of a real-time risk-control system on the Flink processing engine, handling an average of 50M transactions per day and reducing the false-positive rate by 40%
- Designed and delivered a microservice decomposition plan, splitting the monolith into 12 services and increasing deployment frequency from monthly to daily

**Bad examples:**
- Responsible for backend development
- Participated in database optimization

### Length control

The resume target is 1 page, no more than 2. When content doesn't fit, trim the descriptions first rather than adding pages.

| Experience level | Target pages | Descriptions per position |
|----------|---------|-----------------|
| 0-3 years | 1 page | 3-4 bullets |
| 3-8 years | 1 page (2 at most) | 4-5 bullets (recent) / 2-3 bullets (earlier) |
| 8+ years | 2 pages | 4-6 bullets (recent) / 1-2 bullets (earlier) |

### Resume layout parameters

When generating a .docx from scratch, use a compact layout that differs from the general document defaults:

- **Body font size**: 10–10.5pt (Times New Roman / Arial / Calibri; 宋体 (SimSun) for CJK text)
- **Heading font size**: level 1 12pt, level 2 11pt, level 3 10.5pt
- **Line spacing**: 1.15–1.25×
- **Margins**: 1.5–2 cm on all sides
- **Paragraph spacing**: headings 6pt before, 3pt after; body 2pt after
- **First-line indent**: none (resumes do not use a first-line indent)

### Summary formula

`[seniority/role] + [years of experience] + [core competencies] + [industry experience] + [key value]`

> A senior engineer with 8 years of backend development experience, focused on distributed systems and microservice architecture. Has led the design and delivery of multiple core systems in fintech and e-commerce, and excels at performance optimization under high-concurrency scenarios.
