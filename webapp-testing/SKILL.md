---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications. Supports validating frontend functionality, debugging UI behavior, capturing browser screenshots, and inspecting browser logs. Use standard tools whenever possible.
license: Complete terms are available in LICENSE.txt
---

# Web Application Testing

To test a local web application, use Python Playwright scripts or the standard tools provided by the system.

**Available helper script:**
- `with_server.py` - Manage server lifecycles, including multiple servers

**Always run the script with `--help` first** to inspect its usage. Do not read the source code unless you have tried the script and confirmed that a custom solution is necessary. These scripts may be very large and can pollute the context window. They are intended to be invoked as black boxes, not loaded into context.

## Decision Tree: Choose an Approach

```
User task → Is it static HTML?
    ├─ Yes → Read the HTML file directly to identify selectors
    │         ├─ Successful → Use standard browser tools or a Playwright script
    │         └─ Failed/incomplete → Treat it as dynamic (see below)
    │
    └─ No (dynamic web application) → Is the server already running?
        ├─ No → Run: python with_server.py --help
        │        Then use the helper script plus a minimal Playwright script
        │
        └─ Yes → Choose an approach:
            1. Standard tools: use open_url_in_browser, click, type, and take_screenshot
            2. Playwright: use detailed automation with element discovery and logging
```

## Using Standard Tools

For basic web application testing, use these standard tools:

1. **Open a URL:** `open_url_in_browser` - Open a webpage in the browser
2. **Interact with elements:** `click`, `type`, `scroll` - Perform basic browser interactions
3. **Capture a screenshot:** `take_screenshot` - Capture the current browser state
4. **Run commands:** `Bash` - Start servers or run other commands

### Example: Basic Testing with Standard Tools

```python
# 1. Start the server if it is not running
# Bash: "npm run dev"

# 2. Wait for the server to start (Bash blocks while waiting)

# 3. Open the browser
# open_url_in_browser: "http://localhost:5173"

# 4. Interact with the page
# click: "button#login"
# type: "input#username", "testuser"
# type: "input#password", "password"
# click: "button#submit"

# 5. Capture a screenshot
# take_screenshot
```

## Using Playwright (Advanced)

For advanced testing scenarios, use Playwright scripts.

### Example: Using with_server.py

To start a server, run `--help` first and then use the helper script.

**Single server:**
```bash
python with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (for example, backend + frontend):**
```bash
python with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

An automation script needs to contain only the Playwright logic; the servers are managed automatically:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch Chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # The server is running and ready
    page.wait_for_load_state('networkidle') # Critical: wait for JavaScript execution
    # ... your automation logic
    browser.close()
```

## Inspect-Then-Act Pattern

1. **Inspect the rendered DOM:**
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors from the inspection results**

3. **Act using the discovered selectors**

## Common Pitfalls

❌ **Do not** inspect the DOM of a dynamic application before waiting for `networkidle`.
✅ **Do** call `page.wait_for_load_state('networkidle')` before inspection.

## Best Practices

- **Use standard tools for basic tasks** - Use standard browser tools for simple interactions.
- **Use Playwright for advanced tasks** - Use Playwright scripts for complex automation.
- **Treat bundled scripts as black boxes** - Check whether an available script can help. These scripts reliably handle common complex workflows without cluttering the context window. Use `--help` to inspect usage, then invoke them directly.
- Use `sync_playwright()` for synchronous scripts.
- Always close the browser when finished.
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs.
- Add appropriate waits with `page.wait_for_selector()` or `page.wait_for_timeout()`.

## Reference Files

- Examples of common patterns:
  - `element_discovery.py` - Discover buttons, links, and input fields on a page
  - `static_html_automation.py` - Process local HTML using file:// URLs
  - `console_logging.py` - Capture console logs during automation
