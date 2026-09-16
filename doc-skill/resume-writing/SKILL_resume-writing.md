---
name: resume-writing
description: The user provides a resume file (Word or PDF) or a resume template, and you help them read the content, refine the text, and fill it back into the original file while keeping the formatting unchanged. Use this whenever the user brings up anything resume-related, such as "help me revise my resume", "optimize this resume", "help me fill in this resume template", "polish my resume content", or "take a look at what's wrong with my resume". This is the default entry point for all resume work — use it even when the user does not explicitly say "resume" but provides a file that is clearly one.
---

# Resume Workflow Orchestrator

Handle the complete resume workflow for the user: read the file content → understand and optimize the text → fill it back into the original file in the correct format.

## Core Principles

**Preserve the original formatting.** The file the user provides (a Word resume, a resume template) comes with its own layout and styling. After optimizing the content, you must fill it back into the original file rather than generating a brand-new file that discards the existing formatting.

**Order work experience in reverse chronological order.** Whether you are optimizing, filling a template, or building from scratch, the work experience / project experience sections must be ordered from **most recent to oldest** (the most recent job first), and education follows the same rule. If the order is wrong in the resume the user provides, proactively fix it and let the user know.

**Keep the layout compact, within 1–2 pages.** Space on a resume is precious; the goal is 1 page, and no more than 2. Do not insert blank lines, empty paragraphs, or page breaks between sections — the sections should be separated naturally by the space-before of the headings alone, and do not use `---` divider lines. When generating a .docx, use a smaller font (body 10–10.5pt, headings 11–12pt), tighter line spacing (1.15–1.25×), and smaller margins (1.5–2 cm on all sides) to keep the content as compact as possible. Keep the wording concise as well, and avoid lengthy descriptions.

## Step 1: Determine what the user gave you

| What the user gave | Next step |
|---|---|
| Word file (.docx) | Look at the file content and understand the resume structure |
| PDF file (.pdf) | Look at the file content and understand the resume structure |
| Resume template (blank .docx) | Unpack the template, understand the structure, and help the user fill in content |
| Plain text / conversational description | Handle it directly in the conversation |
| Nothing at all | Ask the user for a file, or start building from the conversation |

## Step 2: Determine what the user wants to do

| User intent | Corresponding workflow | Detailed guide |
|---|---|---|
| "Help me revise my resume" / "optimize it" | Read → optimize content → fill back | `references/optimize-resume.md` |
| "Help me fill in this template" | Unpack template → fill in content → pack | `references/build-resume.md` |
| "Help me write one from scratch" | Collect info via conversation → generate file | `references/build-resume.md` |
| "I don't know what to write" | Coach to uncover achievements → organize content | `references/resume-coaching.md` |
| "Take a look at what's wrong" | Read → analyze content → give suggestions | `references/optimize-resume.md` |
| "Optimize for this position" | Read → compare against JD → tailor content → fill back | `references/optimize-resume.md` |

## Toolbox

### Word file editing (unpack → modify → pack)

This is the core workflow for filling content back into the original Word file. See `references/format-check.md` for detailed specifications.

```bash
# 1. Unpack: extract the .docx into editable XML files
uv run ../scripts/docx_edit.py unpack resume.docx unpacked/

# 2. Edit: modify the text in unpacked/word/document.xml
#    (use editing tools to do string replacement, do not write a script)

# 3. Pack: regenerate the .docx
uv run ../scripts/docx_edit.py pack unpacked/ resume_updated.docx
```

## Fill-back workflow (the most important part)

When the user provides a Word file and asks you to optimize the content, the complete workflow is:

1. **Look at the file content** — understand the full text of the resume
2. **Understand the structure** — identify each section (contact info, summary, experience, skills, etc.)
3. **Optimize the content** — improve the text following `references/optimize-resume.md`
4. **Unpack the original file** — run `docx_edit.py unpack` to get the XML
5. **Replace text in the XML** — use editing tools to directly replace the corresponding text in `document.xml`
6. **Pack** — run `docx_edit.py pack` to generate the new file

Key: Step 5 is a **text replacement** within the XML, not a rebuild of the document structure. This way the original fonts, sizes, colors, spacing, and template styles are all preserved.

**XML editing notes (see `references/format-check.md` for details):**
- When replacing an entire `<w:r>` element, you must preserve the original `<w:rPr>` (formatting properties)
- Use XML entities for quotes: `&#x201C;` `&#x201D;`
- For text containing spaces, make sure to use `<w:t xml:space="preserve">`

## Reference document index

| Document | When to read it | Content |
|---|---|---|
| `references/build-resume.md` | When the user wants to write a resume from scratch or fill a template | Scenario detection, reading files, filling templates, building from scratch, content organization methods |
| `references/optimize-resume.md` | When the user wants to improve an existing resume | General content optimization, tailoring for a specific position, ATS friendliness, common issue fixes |
| `references/resume-coaching.md` | When the user doesn't know what to write | STAR questioning method, guiding-question checklist, metric estimation techniques, turning discoveries into descriptions |
| `references/format-check.md` | When filling content back into Word | XML specifications for Word unpack/edit/pack, whitespace handling, PDF generation, formatting validation checklist |

## Script index

| Script | Purpose |
|---|---|
| `../scripts/docx_edit.py` | Shared Word unpack/pack/replace tool (zero external deps). On unpack it pretty-prints the XML, merges adjacent same-format runs, and escapes smart quotes; on pack it auto-repairs whitespace and condenses the XML. For résumé fill-back use `unpack`/`pack` and edit the XML manually |
| `../scripts/create_docx.py` | Markdown → .docx generator (use `--style resume` when building a resume from scratch); automatically applies compact layout (10pt body, 1.15× line spacing, 1.8cm margins, no first-line indent) |
