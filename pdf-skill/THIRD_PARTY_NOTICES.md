# Third-party dependencies and licenses (pdf-skill)

This skill calls the following third-party components. Except for
`scripts/paged.polyfill.js`, which is bundled with the package, all others are
system-level or Python/Node dependencies preinstalled in the runtime environment
(training machine / image); this skill does not download or install them at runtime.

## Bundled with the package

| Component | Version | License | Source | File |
|------|------|--------|------|------|
| Paged.js polyfill | v0.4.3 | MIT | https://gitlab.coko.foundation/pagedjs/pagedjs | `scripts/paged.polyfill.js` (license declared in the file header `@license`) |

## Preinstalled in the runtime (not distributed with the package)

| Component | License | Source / homepage | Purpose |
|------|--------|----------------|------|
| Playwright | Apache-2.0 | https://playwright.dev | HTML → PDF rendering (headless-browser driver) |
| Chromium | BSD-3-Clause, etc. | https://www.chromium.org | The rendering engine driven by Playwright |
| LibreOffice | MPL-2.0 | https://www.libreoffice.org | Office ↔ PDF conversion |
| Tectonic | MIT | https://tectonic-typesetting.github.io | LaTeX → PDF compilation |
| pikepdf | MPL-2.0 | https://github.com/pikepdf/pikepdf | Form filling, page operations, metadata |
| pdfplumber | MIT | https://github.com/jsvine/pdfplumber | Text and table extraction |
| KaTeX | MIT | https://katex.org | Math-formula rendering |
| Mermaid | MIT | https://mermaid.js.org | Diagram rendering |

## Installation boundaries

- The training machine / image usually has the above dependencies preinstalled; normal
  use **requires no installation**.
- To repair missing dependencies, run `PDF_SH_ALLOW_FIX=1 bash scripts/pdf.sh fix` only
  in an environment that explicitly allows modifying global/user packages.
- This skill contains no unconfirmed privilege-escalation or remote-install behavior such
  as `curl | sh` or `sudo apt-get`; dependency diagnosis (`pdf.sh check`) is a read-only
  operation.
