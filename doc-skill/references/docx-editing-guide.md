# DOCX Editing Guide — Editing Existing Documents

This guide explains how to edit a .docx file by manipulating its XML, perfectly preserving the original formatting while modifying the content.

## Table of Contents

1. [Workflow: Unpack → Edit → Repack](#workflow)
2. [Editing Principles](#editing-principles)
3. [XML Structure Reference](#xml-structure-reference)
4. [Image Handling](#image-handling)

---

## Workflow

**Perform the following 3 steps in order.**

### Step 1: Unpack

```bash
uv run scripts/docx_edit.py unpack document.docx unpacked/
```

Extracts the archive, pretty-prints every `.xml`/`.rels` file for readability, converts smart quotes (`' ' " "`) to XML entities so they survive editing, and **merges adjacent `<w:r>` runs that share identical formatting** in `document.xml` (stripping `proofErr`/`rsid` noise). This is important because Word frequently splits a single logical string across many runs — merging gives you contiguous text nodes that are easy to find and replace.

> **Shortcut:** for a simple placeholder/text substitution you do not need to unpack manually — use the one-step `replace` mode, which unpacks, replaces (matching text even when it is split across `<w:r>` runs, with optional track changes), and repacks in a single call:
> ```bash
> uv run scripts/docx_edit.py replace source.docx output.docx replacements.json
> ```
> Fall back to the manual unpack → edit → pack workflow below only when you need structural edits that a plain find/replace cannot express.

### Step 2: Edit the XML

Edit the files under `unpacked/word/`; the main content is in `document.xml`.

**Do string replacement directly with the editing tools; do not write a Python script.** The editing tools can show the replaced content precisely.

**Use XML entities when adding text containing quotation marks/apostrophes:**
```xml
<w:t>Here&#x2019;s a quote: &#x201C;Hello&#x201D;</w:t>
```
| Entity | Character |
|------|------|
| `&#x2018;` | ' (left single quote) |
| `&#x2019;` | ' (right single quote / apostrophe) |
| `&#x201C;` | " (left double quote) |
| `&#x201D;` | " (right double quote) |

### Step 3: Repack

```bash
uv run scripts/docx_edit.py pack unpacked/ output.docx
```

Auto-repairs whitespace first (adds `xml:space="preserve"` to any `<w:t>` whose text has leading/trailing spaces), then condenses the XML (stripping the pretty-print whitespace added during unpack, while preserving the text inside `<w:t>`) and re-zips the directory into a `.docx`.

---

## Editing Principles

### Replacing the Text of an Existing Field

The key to preserving formatting: only modify the text inside the `<w:t>` element, and do not touch `<w:rPr>` (the formatting properties).

```xml
<!-- before -->
<w:r>
  <w:rPr>
    <w:b/>
    <w:sz w:val="24"/>
  </w:rPr>
  <w:t>placeholder text</w:t>
</w:r>

<!-- after — only the text changed, the formatting is fully preserved -->
<w:r>
  <w:rPr>
    <w:b/>
    <w:sz w:val="24"/>
  </w:rPr>
  <w:t>Zhang San</w:t>
</w:r>
```

### Filling in Blank Fields

A template may use underscores, spaces, or an empty `<w:t>` as a placeholder. Replace the placeholder content while keeping the outer XML structure unchanged:

```xml
<!-- underscore placeholder in the template -->
<w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>____________</w:t></w:r>

<!-- filled-in content -->
<w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>1990-01-15</w:t></w:r>
```

### Checkbox Fields

Visa forms often use checkboxes:
```xml
<w:r><w:t>☐</w:t></w:r>  <!-- unchecked -->
<w:r><w:t>☑</w:t></w:r>  <!-- checked -->
```

Just replace the character to toggle the checked state. Some templates use Wingdings font symbols; the principle is the same.

### Whitespace Rules

- When the text has leading/trailing spaces, add `xml:space="preserve"` to `<w:t>`
- Do not use `\n` — use a separate `<w:p>` element for a new line
- Do not put text directly inside `<w:p>` — always wrap it in `<w:r><w:t>...</w:t></w:r>`

### Common Pitfalls

- **Preserve the `<w:rPr>` formatting** — copy the original run's `<w:rPr>` block into the replacement run
- Table path: `<w:tbl>` → `<w:tr>` → `<w:tc>` → `<w:p>` → `<w:r>` → `<w:t>`

---

## XML Structure Reference

### Document Structure

```
document.xml
  └── w:body
      ├── w:p (paragraph)
      │   ├── w:pPr (paragraph properties: style, alignment, line spacing)
      │   └── w:r (run — a piece of text with the same formatting)
      │       ├── w:rPr (run properties: font, size, bold, italic, etc.)
      │       └── w:t (text content)
      └── w:tbl (table)
          └── w:tr (table row)
              └── w:tc (cell)
                  └── w:p (paragraph inside the cell)
```

### Schema Compliance

- **Element order within `<w:pPr>`**: `<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`, `<w:rPr>` last
- **Whitespace**: a `<w:t>` with leading/trailing spaces needs `xml:space="preserve"`
- **RSID**: must be 8 hexadecimal digits (e.g. `00AB1234`)

---

## Image Handling

1. Put the image file into `word/media/`
2. Add a relationship in `word/_rels/document.xml.rels`:
```xml
<Relationship Id="rId5" Type=".../image" Target="media/image1.png"/>
```
3. Add a content type in `[Content_Types].xml`:
```xml
<Default Extension="png" ContentType="image/png"/>
```
4. Reference it in document.xml:
```xml
<w:drawing>
  <wp:inline>
    <wp:extent cx="914400" cy="914400"/>  <!-- EMU units: 914400 = 1 inch -->
    <a:graphic>
      <a:graphicData uri=".../picture">
        <pic:pic>
          <pic:blipFill><a:blip r:embed="rId5"/></pic:blipFill>
        </pic:pic>
      </a:graphicData>
    </a:graphic>
  </wp:inline>
</w:drawing>
```
