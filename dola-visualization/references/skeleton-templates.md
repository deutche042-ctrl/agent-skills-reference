# Skeleton Templates

HTML skeleton code for each layout archetype. For wrapper structure, height rules, CSS mechanism table, and hard constraints, see SKILL.md.

**Dashboard / Report skeleton** (Science/Research colors — replace with your category's palette from [design-system.md](design-system.md)):

```html type="renderer"
<html style="margin:0;padding:0;">
<!-- CDN + font tags first — client starts fetching immediately -->
<!-- MANDATORY: Replace font below with your category's pick from Font Rotation System (in design-system.md) -->
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script>
(function(){
  var s = document.createElement('style');
  // REPLACE ALL values below from the Color Rotation System (in design-system.md) for YOUR category
  s.textContent = ':root{--bg:#f8fafb;--card:#ffffff;--text:#0f172a;--muted:#64748b;--accent:#2d7eb5;--accent-soft:rgba(45,126,181,.14);--accent2:#c85a3a;--accent2-soft:rgba(200,90,58,.14);--border:rgba(15,23,42,.08)}.reveal{opacity:0;transform:translateY(20px);animation:fadeUp .6s ease forwards}.reveal:nth-child(2){animation-delay:.1s}.reveal:nth-child(3){animation-delay:.2s}.reveal:nth-child(4){animation-delay:.3s}.reveal:nth-child(5){animation-delay:.4s}.reveal:nth-child(6){animation-delay:.5s}@keyframes fadeUp{to{opacity:1;transform:translateY(0)}}.metric-card{transition:transform .2s ease,box-shadow .2s ease}.metric-card:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,0,0,.08)}.tbl-row{transition:background .15s ease}.tbl-row:hover{background:rgba(128,128,128,.06)}';
  document.head.appendChild(s);
})();
</script>
<div style="background-color:transparent;box-sizing:border-box;">
  <div style="color:var(--text);font-family:'IBM Plex Sans',sans-serif;background:var(--bg)">
    <div class="max-w-5xl mx-auto px-6 py-12">

      <!-- SECTION 1: Hero — SVG icon + strong hierarchy -->
      <div class="reveal mb-14">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">
          <div style="width:44px;height:44px;border-radius:12px;background:var(--accent-soft);display:flex;align-items:center;justify-content:center;color:var(--accent);flex-shrink:0;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
          </div>
          <div>
            <p style="font-family:monospace;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:var(--muted)">CATEGORY LABEL</p>
            <h1 class="text-4xl font-bold" style="color:var(--text);letter-spacing:-0.02em;line-height:1.15">Report Title</h1>
          </div>
        </div>
        <p style="color:var(--muted);max-width:600px" class="text-base mt-3">Subtitle summarizing the key insight.</p>
      </div>

      <!-- SECTION 2: Metrics — flex-wrap, SVG icons in each card -->
      <div class="reveal flex flex-wrap gap-4 mb-14">
        <div class="metric-card backdrop-blur rounded-2xl p-5" style="flex:1 1 200px;background:var(--card);border:1px solid var(--border);box-shadow:0 1px 3px rgba(0,0,0,.06)">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <div style="width:32px;height:32px;border-radius:8px;background:var(--accent-soft);display:flex;align-items:center;justify-content:center;color:var(--accent);">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 6l-9.5 9.5-5-5L1 18"/><path d="M17 6h6v6"/></svg>
            </div>
            <div style="color:var(--muted)" class="text-xs uppercase tracking-wide font-medium">Metric 1</div>
          </div>
          <div style="color:var(--text)" class="text-3xl font-bold">Value</div>
          <div class="text-emerald-700 text-xs mt-1 font-medium">▲ +12.3%</div>
        </div>
        <div class="metric-card backdrop-blur rounded-2xl p-5" style="flex:1 1 200px;background:var(--card);border:1px solid var(--border);box-shadow:0 1px 3px rgba(0,0,0,.06)">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <div style="width:32px;height:32px;border-radius:8px;background:var(--accent-soft);display:flex;align-items:center;justify-content:center;color:var(--accent);">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            </div>
            <div style="color:var(--muted)" class="text-xs uppercase tracking-wide font-medium">Metric 2</div>
          </div>
          <div style="color:var(--text)" class="text-3xl font-bold">Value</div>
          <div class="text-emerald-700 text-xs mt-1 font-medium">▲ +5.7%</div>
        </div>
        <div class="metric-card backdrop-blur rounded-2xl p-5" style="flex:1 1 200px;background:var(--card);border:1px solid var(--border);box-shadow:0 1px 3px rgba(0,0,0,.06)">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <div style="width:32px;height:32px;border-radius:8px;background:var(--accent-soft);display:flex;align-items:center;justify-content:center;color:var(--accent);">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            </div>
            <div style="color:var(--muted)" class="text-xs uppercase tracking-wide font-medium">Metric 3</div>
          </div>
          <div style="color:var(--text)" class="text-3xl font-bold">Value</div>
          <div class="text-rose-700 text-xs mt-1 font-medium">▼ -2.1%</div>
        </div>
      </div>

      <!-- SECTION 3: Chart — script INSIDE .reveal, container has EXPLICIT height -->
      <div class="reveal rounded-2xl p-8 mb-8" style="background:var(--card);border:1px solid var(--border);box-shadow:0 1px 3px rgba(0,0,0,.06)">
        <h2 class="text-xl font-semibold mb-6" style="color:var(--text)">Chart Title</h2>
        <!-- CRITICAL: height MUST be explicitly set for ECharts -->
        <div id="chart1" style="height:380px;width:100%"></div>
        <script>
        (function init(n){
          try {
            var el=document.getElementById('chart1'); if(!el)return;
            if(typeof echarts==='undefined'){
              if(n<40){setTimeout(function(){init(n+1)},250);return;}
              el.textContent='Chart library failed to load';return;
            }
            var c = echarts.init(el);
            // Read palette from CSS variables (preferred) — fallback hex for safety
            var st=getComputedStyle(document.documentElement);
            var accent=st.getPropertyValue('--accent').trim()||'#2d7eb5';
            var muted=st.getPropertyValue('--muted').trim()||'#64748b';
            var card=st.getPropertyValue('--card').trim()||'#ffffff';
            var text=st.getPropertyValue('--text').trim()||'#0f172a';
            var border=st.getPropertyValue('--border').trim()||'rgba(15,23,42,.08)';
            // gradient extracted to a var — keeps setOption nesting shallow (Brace-depth discipline)
            var grad={type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:accent},{offset:1,color:accent+'4d'}]};
            c.setOption({
              backgroundColor:'transparent',
              tooltip:{trigger:'axis',backgroundColor:card,borderColor:border,textStyle:{color:text}},
              grid:{left:'3%',right:'4%',bottom:'3%',containLabel:true},
              xAxis:{type:'category',data:['Q1','Q2','Q3','Q4'],axisLabel:{color:muted},axisTick:{show:false}},
              yAxis:{type:'value',axisLabel:{color:muted},splitLine:{lineStyle:{color:border}}}, // bar chart: baseline 0 is correct here — line/trend charts MUST add scale:true (see Chart theming rules)
              series:[{type:'bar',data:[320,410,380,520],itemStyle:{borderRadius:[6,6,0,0],color:grad}}]
            });
            window.addEventListener('resize',function(){c.resize()});
          } catch(e){console.error(e)}
        })(0);
        </script>
      </div>

      <!-- SECTION 4: Table — hover rows -->
      <div class="reveal rounded-2xl p-8 mb-8" style="background:var(--card);border:1px solid var(--border);box-shadow:0 1px 3px rgba(0,0,0,.06)">
        <h2 class="text-xl font-semibold mb-6" style="color:var(--text)">Table Title</h2>
        <table class="w-full text-sm">
          <thead>
            <tr style="color:var(--muted);border-bottom:1px solid var(--border)" class="text-xs uppercase tracking-wide">
              <th class="text-left pb-3 font-medium">Column A</th>
              <th class="text-left pb-3 font-medium">Column B</th>
              <th class="text-left pb-3 font-medium">Change</th>
            </tr>
          </thead>
          <tbody style="color:var(--text)">
            <tr class="tbl-row" style="border-bottom:1px solid var(--border)"><td class="py-3.5 font-medium">Row 1</td><td>Data</td><td class="text-emerald-700 font-medium">▲ 18.2%</td></tr>
            <tr class="tbl-row" style="border-bottom:1px solid var(--border)"><td class="py-3.5 font-medium">Row 2</td><td>Data</td><td class="text-rose-700 font-medium">▼ 3.1%</td></tr>
            <tr class="tbl-row"><td class="py-3.5 font-medium">Row 3</td><td>Data</td><td class="text-emerald-700 font-medium">▲ 22.4%</td></tr>
          </tbody>
        </table>
      </div>

      <!-- Footer -->
      <div class="mt-16 pt-6" style="border-top:1px solid var(--border)">
        <p class="text-center text-xs" style="color:var(--muted)">Data source · Generated date</p>
      </div>
    </div>
  </div>
</div>
</html>
```

**Rendering order:**

| Order | Area | Streaming Behavior |
|-------|------|--------------------|
| 1 | CDN `<script>` / font `<link>` | Browser starts loading external resources immediately |
| 2 | CSS injection `<script>` | Variables + keyframes available before any section renders |
| 3 | Hero section (with SVG icon) | Title + icon renders as first tokens arrive |
| 4 | Metric cards (with SVG icons) | Cards appear progressively within flex-wrap |
| 5 | Chart `<div>` + embedded `<script>` | Chart initializes the moment `</script>` closing tag arrives |
| 6 | Table rows | Rows render line-by-line as tokens stream |
| 7 | Footer | Appears last |

**Customization guide — adapt the skeleton per artifact** (Dashboard archetype only; for other archetypes restructure first per the Layout Archetype System in [design-system.md](design-system.md)):

1. **Swap the font**: Pick from the **Font Rotation System** table in [design-system.md](design-system.md) based on content category.
2. **Swap the color palette**: Pick from the **Color Rotation System** table in [design-system.md](design-system.md) — change the CSS variable values (including `--accent2`, `--accent2-soft`, and `--border`). Chart scripts will read these automatically via `getComputedStyle` (see *Chart theming* in [chart-rules.md](chart-rules.md)). If hardcoding as fallback, sync axis labels, splitLine, tooltip, and gradient stops to the same hex values (`--accent` hex for series 1, `--accent2` hex for series 2). For Tailwind utility colors, use -700 shades (`emerald-700`/`rose-700`) on light palettes and -400 shades (`emerald-400`/`rose-400`) on dark palettes — the -600 shades sit around 3.8:1 on white, below the 4.5:1 needed at `text-xs`. Hero icon tile on light palettes: `background:var(--accent-soft);color:var(--accent)` (see Accent fill strategy); on dark palettes you may use `linear-gradient(135deg,var(--accent),var(--accent-soft))` for a glow tail.
3. **Swap chart data**: Replace sample data with real values computed in CI.
4. **Add or remove sections**: Insert new section wrappers with embedded `<script>` or remove unused ones — keep each section self-contained.
5. **Adjust animation delays**: Tune `.reveal:nth-child(N)` `animation-delay` values (stagger by ~0.1s per section). Only apply `.reveal` to the first 5–6 sections — sections beyond that should omit the class so they render visible by default (see *Reveal limit* in [quality-and-mobile.md](quality-and-mobile.md)).

---

**Structural mini-sketches** for the three highest-frequency non-Dashboard archetypes. These are layout skeletons only — combine each with the standard `<html>` wrapper, CDN/font `<link>` tags, CSS variable injection, per-section scripts, and reveal classes exactly as in the main skeleton:

```html
<!-- Editorial / Newspaper — structural sketch -->
<div style="max-width:760px;margin:0 auto;padding:48px 24px">
  <div style="display:flex;justify-content:space-between;border-bottom:3px double var(--text);padding-bottom:10px;margin-bottom:28px">
    <span style="font-family:monospace;font-size:11px;letter-spacing:.2em;text-transform:uppercase">Publication Name</span>
    <span style="font-size:12px;color:var(--muted)">Dateline</span>
  </div>
  <p style="font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:var(--accent);margin-bottom:8px">Kicker / section label</p>
  <h1 style="font-size:40px;line-height:1.1;font-weight:700;margin-bottom:14px">Serif headline carrying the lead story</h1>
  <p style="font-size:17px;line-height:1.6;color:var(--muted);margin-bottom:32px">Lede paragraph summarizing the most important development in two or three sentences.</p>
  <div style="border-top:1px solid var(--border);padding:20px 0">
    <h2 style="font-size:22px;font-weight:600;margin-bottom:8px">Second story headline</h2>
    <p style="line-height:1.7">Body text in full prose. No cards, no icon tiles, no metric rows — hairlines and typography do all the work.</p>
  </div>
  <blockquote style="border-left:3px solid var(--accent);padding-left:16px;font-size:20px;font-style:italic;margin:28px 0">A pull quote lifted from the most striking line.</blockquote>
  <p style="text-align:center;font-size:11px;color:var(--muted);border-top:1px solid var(--border);padding-top:14px;margin-top:36px">Sources · Colophon</p>
</div>
```

```html
<!-- Document / Handbook — structural sketch -->
<div style="max-width:720px;margin:0 auto;padding:48px 24px">
  <h1 style="font-size:32px;font-weight:700;margin-bottom:6px">Document Title</h1>
  <p style="color:var(--muted);margin-bottom:28px">One-line description of scope and audience.</p>
  <nav style="border:1px solid var(--border);border-radius:10px;padding:16px 20px;margin-bottom:36px">
    <p style="font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:8px">Contents</p>
    <ol style="padding-left:18px;line-height:1.9;font-size:14px"><li><a href="#s1" style="color:var(--text);text-decoration-color:var(--accent);text-underline-offset:3px">First section</a></li><li>Second section</li></ol>
  </nav>
  <h2 id="s1" style="font-size:22px;font-weight:600;margin:32px 0 12px">1. First section</h2>
  <p style="line-height:1.75;margin-bottom:14px">Prose paragraphs in a narrow reading column. Headings, callouts, and code blocks carry the hierarchy — not cards.</p>
  <div style="border-left:3px solid var(--accent);background:var(--accent-soft);padding:12px 16px;border-radius:0 8px 8px 0;margin:16px 0">Callout: a key definition or warning.</div>
  <pre style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px;font-size:13px;overflow-x:auto"><code>code_example()</code></pre>
</div>
```

```html
<!-- Game / Interactive — structural sketch -->
<div style="max-width:860px;margin:0 auto;padding:36px 24px;text-align:center">
  <h1 style="font-size:28px;font-weight:700;margin-bottom:4px">Game Title</h1>
  <p style="color:var(--muted);font-size:14px;margin-bottom:24px">One line of rules: what to click, how to win.</p>
  <div id="board" style="min-height:420px;background:var(--card);border:1px solid var(--border);border-radius:16px;margin-bottom:20px"><!-- play area dominates the page --></div>
  <div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-bottom:16px">
    <button id="check" style="padding:12px 26px;border-radius:12px;font-weight:600;background:var(--accent-soft);color:var(--text);border:1px solid var(--accent);cursor:pointer">Check Solution</button>
    <button id="reset" style="padding:12px 26px;border-radius:12px;font-weight:600;background:var(--card);color:var(--muted);border:1px solid var(--border);cursor:pointer">Reset</button>
  </div>
  <!-- status text is accent-colored, so it is sized 18px bold to clear WCAG large-text 3:1 -->
  <div id="status" style="min-height:24px;font-size:18px;font-weight:700;color:var(--accent)"></div>
</div>
```

> **Common mistake for interactive archetypes**: Do NOT wrap the entire app in a `min-height:100vh` div to "fill the screen." The iframe has no fixed viewport — `100vh` causes infinite growth. Let the content determine height naturally; use fixed `min-height` in px ONLY on the board/canvas container itself (e.g. `min-height:420px`).

---
