# Format Check and Output

Fill content back into the original file (keeping formatting unchanged), or generate a brand-new Word/PDF file.

## Table of Contents

- [Word File Fill-Back (Core Workflow)](#word-file-fill-back-core-workflow)
- [Detailed XML Editing Specification](#detailed-xml-editing-specification)
- [Generating a Brand-New Word File](#generating-a-brand-new-word-file)
- [PDF Generation](#pdf-generation)
- [Formatting Validation Checklist](#formatting-validation-checklist)
- [Common Formatting Problems](#common-formatting-problems)

---

## Word File Fill-Back (Core Workflow)

The user gave a Word resume/template, and after optimizing the content it needs to be filled back. This is the most common scenario.

### Three steps

**Step 1: Unpack**

```bash
uv run ../scripts/docx_edit.py unpack resume.docx unpacked/
```

What it does:
- Extracts the .docx into a directory of XML files
- Automatically pretty-prints the XML (easier to read and edit)
- Merges adjacent same-format runs and strips `proofErr`/`rsid` noise (solves Word's habit of splitting text into fragments)
- Escapes smart quotes into XML entities

After unpacking, the core content is in `unpacked/word/document.xml`.

**Step 2: Edit the XML**

Find the text you want to modify in `document.xml` and do a string replacement directly with editing tools.

**What to do:**
- Find the `<w:t>` element containing the original text
- Replace the content inside `<w:t>` with the optimized text
- Keep the surrounding `<w:rPr>` (formatting) and `<w:pPr>` (paragraph properties) unchanged

**What not to do:**
- Don't delete or modify the formatting information in `<w:rPr>`
- Don't write Python/JS scripts to manipulate the XML (easy to break the structure)
- Don't modify `<w:sectPr>` (page setup)

**Step 3: Pack**

```bash
uv run ../scripts/docx_edit.py pack unpacked/ resume_updated.docx
```

What it does:
- Auto-repairs whitespace (adds `xml:space="preserve"` to any `<w:t>` with leading/trailing spaces)
- Condenses the pretty-print whitespace
- Packs into a .docx

---

## Detailed XML Editing Specification

### Basic structure

The text structure of a Word document:

```xml
<w:body>
  <w:p>                          <!-- paragraph -->
    <w:pPr>                      <!-- paragraph properties (alignment, spacing, style, etc.) -->
      <w:pStyle w:val="Heading1"/>
    </w:pPr>
    <w:r>                        <!-- text run -->
      <w:rPr>                    <!-- run properties (font, size, bold, etc.) -->
        <w:b/>                   <!-- bold -->
        <w:sz w:val="24"/>       <!-- font size -->
      </w:rPr>
      <w:t>text content goes here</w:t>   <!-- the actual text -->
    </w:r>
  </w:p>
</w:body>
```

### Simple text replacement

The most common operation. Find the `<w:t>` element and replace the text inside it:

**Before:**
```xml
<w:r>
  <w:rPr><w:b/><w:sz w:val="22"/></w:rPr>
  <w:t>Responsible for backend development work</w:t>
</w:r>
```

**After:**
```xml
<w:r>
  <w:rPr><w:b/><w:sz w:val="22"/></w:rPr>
  <w:t>Led the build of an order-processing microservice, handling an average of 8M orders per day</w:t>
</w:r>
```

Note that `<w:rPr>` was not touched at all — the formatting is preserved.

### Replacing an entire run

When you need to change the run boundaries (e.g., splitting one run into two, or merging two runs):

**Rules:**
- Copy the original `<w:rPr>` into the new run
- If the text starts or ends with a space, add `xml:space="preserve"`

```xml
<w:r>
  <w:rPr><w:b/><w:sz w:val="22"/></w:rPr>
  <w:t xml:space="preserve">optimized text </w:t>
</w:r>
```

### Handling special characters

| Character | XML entity |
|------|---------|
| Left double quote " | `&#x201C;` |
| Right double quote " | `&#x201D;` |
| Left single quote ' | `&#x2018;` |
| Right single quote ' | `&#x2019;` |
| & | `&amp;` |
| < | `&lt;` |
| > | `&gt;` |

`docx_edit.py unpack` has already converted smart quotes into XML entities; keep using the entities when editing.

### Adding a new list item

If you need to add a new bullet item to an existing list:

1. Find an existing list item `<w:p>`
2. Copy the entire `<w:p>` element (including the `<w:numPr>` inside `<w:pPr>`)
3. Modify only the text inside `<w:t>`

This way the new item inherits the same list style and indentation.

### Deleting content

Just delete the entire `<w:p>` paragraph. Don't merely clear the text — that leaves a blank line.

---

## Generating a Brand-New Word File

When the user has no existing file and needs one generated from scratch, write the résumé content as **Markdown** and generate the `.docx` with `create_docx.py --style resume`. You do not write any script — the `resume` style applies the compact layout automatically.

### Command

```bash
uv run ../scripts/create_docx.py resume.md resume.docx --style resume
```

### What `--style resume` applies

- Compact layout: 10pt body, 12/11/10.5pt headings, 1.15 line spacing, 1.8cm margins
- No first-line indent and no header/footer/page number (résumés should fit 1–2 pages)
- Latin text in Times New Roman/Arial; CJK falls back to 宋体/黑体

### Writing the Markdown

- Use `#` for the name, `##` for section titles (Work Experience, Education, Skills …), and `###` for entries — do not fake headings with bold text.
- Use `- ` bullets for achievement lines; the script renders proper bullets (never type a literal `•`).
- For a "Company … Date" line, either keep the date inline (e.g. `**Company** — Senior Engineer (Jan 2023 – Present)`) or use a two-column Markdown table; there are no manual tab stops.
- Keep one blank line between blocks; do not fake spacing with extra blank lines or tabs — the style handles spacing.

See `../references/docx-creation-guide.md` for the full list of supported Markdown elements.

---

## PDF Generation

Use the Typst typesetting engine.

```bash
# Install
brew install typst

# Compile
typst compile resume.typ resume.pdf
```

### Chinese fonts

```typst
#set text(font: ("Inter", "Noto Sans SC"))        // 思源黑体 (Source Han Sans)
#set text(font: ("Arial", "PingFang SC"))          // 苹方 (PingFang, macOS)
```

### Basic template

```typst
#set page(paper: "a4", margin: (top: 2cm, bottom: 2cm, left: 2cm, right: 2cm))
#set text(font: ("Inter", "Noto Sans SC"), size: 10pt)

#align(center)[
  #text(size: 18pt, weight: "bold")[Zhang San]
]

#align(center)[
  138-0000-1234 | zhangsan\@email.com | Beijing
]

#let section-title(title) = {
  v(8pt)
  text(size: 12pt, weight: "bold")[#title]
  line(length: 100%, stroke: 0.5pt)
  v(4pt)
}

#section-title("Work Experience")
```

---

## Formatting Validation Checklist

### Content completeness
- [ ] All sections render correctly
- [ ] No content is truncated
- [ ] Chinese characters display properly

### Fill-back correctness (Word)
- [ ] Original styles preserved (font, size, color, spacing)
- [ ] Bullets display correctly
- [ ] Table structure intact
- [ ] Page-break positions are reasonable

### Layout quality
- [ ] Content fits the target page count
- [ ] No orphan lines (a single line running onto the next page)
- [ ] Spacing is even

---

## Common Formatting Problems

### Formatting lost after replacing text

**Cause:** You replaced `<w:rPr>` along with the text
**Fix:** Replace only the text inside `<w:t>`, leaving `<w:rPr>` untouched

### Placeholder split into multiple runs

**Cause:** Word internally splits continuous text often (e.g., after a spell check)
**Fix:** Manually merge adjacent same-format runs (combine the text of multiple `<w:r>` into one, keeping a single `<w:rPr>`)

### Word errors after packing

**Cause:** The XML structure was broken (unclosed tags, wrong element order, etc.)
**Fix:** Compare the XML before and after your edits, checking whether you accidentally deleted a structural element (such as `<w:sectPr>`, `<w:tblPr>`, etc.)

### Newly added content overflows the page

**Fix:**
1. Adjust spacing first (line height, paragraph spacing, margins)
2. Trim the content
3. Reduce the font size (not recommended below 10pt)
