# Diagram Geometry Rules

### Diagram Geometry Rules (CRITICAL for node-link diagrams: family trees, org charts, flowcharts, relationship graphs, tournament brackets)

Misaligned diagrams — lines that miss their nodes, edges floating in empty space, connector hubs touching nothing — all come from ONE root cause: **coordinates written by hand in two places**. You cannot see the canvas while generating; arithmetic in code is your only eyes. Rules, in order of preference:

1. **Match the layout algorithm to the structure.** Family trees, org charts, flowcharts, and **tournament/elimination brackets** are LAYERED structures: lay them out in rows or columns (formula in rule 3) with orthogonal connectors (rule 4). Brackets are horizontal trees — rounds are columns (`x = leftMargin + round * colGap`), match `i` in round `r` centers vertically between matches `2i` and `2i+1` of round `r-1`, connectors are horizontal elbows merging pairs left-to-right. Use a single SVG with formula-driven positions (rule 2); NEVER use DOM columns (flex/grid) with ANY manual pixel spacing for round alignment — this includes `margin-top`/`margin-bottom`, `padding-top` on column containers, and empty spacer `<div style="height:Xpx">` elements between matches. ALL of these are the same broken pattern (rule 8) wearing different syntax: a fixed pixel constant cannot center a later-round match between its two feeder matches because it doesn't reference their actual positions. Common violations: (a) `.round-N .match:nth-child(M){margin-bottom:calc(...)}`, (b) `<div style="height:52px"></div>` between match cards, (c) `padding-top:160px` on a round column. The ONLY correct approach is a single SVG with formula-driven Y coordinates: match `i` in round `r` has `y = (feederMatch[2i].y + feederMatch[2i+1].y) / 2`, and horizontal elbow connectors join each pair. Mind maps and topic hierarchies: use a library tree layout (ECharts `type:'tree'`, D3 `d3.tree()`) or the data-driven SVG pattern (rule 2). **Use horizontal tree by default** — see rule 13 for the strict conditions under which radial is permitted. Hand-coded polar coordinate math is banned (rule 13). For layered trees, ECharts `series:[{type:'tree'}]` computes the layout from nested data with zero coordinate math — prefer it. **NEVER apply force-directed layout (`d3.forceSimulation`, ECharts `layout:'force'`) to a tree or org chart** — the simulation overwrites any initial positions you set and collapses the clean hierarchy into a tangled blob. Force layout is ONLY for genuinely unstructured networks with no inherent levels. (Note: ECharts `type:'graph'` with `layout:'none'` for manual positioning is fine — it's specifically `layout:'force'` that is banned.)
2. **Whenever you draw SVG diagrams without a library layout engine: ONE `<svg viewBox>`, ONE data table, render loops.** Define every node's position once in a JS object (computed by formula, not eyeballed); render BOTH nodes and edges from that table in loops. An edge's endpoints are `pos[e.from].x/y` → `pos[e.to].x/y` — never literal numbers typed twice. If you catch yourself typing the same coordinate in two places, stop and restructure into data + loop: alignment then holds by construction. This applies at runtime too: if positions are clamped or recomputed, update the data and redraw BOTH nodes and edges from it — clamping only the node's visual transform while edges read the raw values is how nodes and their lines drift apart.
3. **Layered layouts by formula**, not eyeballing: `y = topMargin + level * rowGap`; within a row, `x = (i + 1) * width / (rowCount + 1)`. Three edge types: (a) **marriage** — solid horizontal bar between adjacent same-row nodes; (b) **partner/lover** — dashed horizontal bar, also same-row; (c) **parent→child** — orthogonal elbow dropping vertically. Non-marriage relationships (lovers, informal bonds) are STILL same-row horizontal lines (dashed), NEVER vertical drops — vertical means parent→child only. Children hang from the midpoint between their parents. **Do NOT draw sibling-sibling edges** — siblings are already implied by hanging from the same parents; explicit sibling edges are the single biggest hairball multiplier.
4. **Orthogonal (elbow) connectors for trees** — this is what makes a tree look like a genealogy chart instead of diagonal spaghetti: from the parent (or marriage midpoint), drop vertically to a rail halfway between generations, run horizontally to the child's x, then drop to the child's top edge. One path per child: `M parentX parentBottom V railY H childX V childTop`. Diagonal lines radiating from a single hub point are the #1 "ugly tree" signature. **`<line>` draws ONE straight segment only** (x1,y1 → x2,y2). You CANNOT make an L-shaped or multi-segment connector with `<line>` — putting duplicate attributes (`x2="A" y2="B" x2="C" y2="D"`) is invalid; the browser keeps only the last value, producing a diagonal. Any connector with a bend (elbow, Z-shape, bracket merge) MUST use `<path>` with H/V commands.
5. **ONE unit system per diagram.** All positions in SVG viewBox user units. Never mix percentage and pixel positions for elements that must align (e.g. lines at `x1="20%"` aimed at cards offset in px) — that geometry only holds at one imagined container width and misses at every other. **Critical pitfall — `<g transform>` vs edge coordinates**: if you place nodes inside `<g transform="translate(tx,ty)">`, the polygon/rect coordinates inside the group are LOCAL to that group. Edge `<path>` elements drawn outside those groups use GLOBAL SVG coordinates. You MUST add the translate offset when computing edge endpoints: an edge connecting to a node at `translate(390,185)` with a local anchor at `(200,50)` has its global attachment point at `(590,235)`, not `(200,50)`. Using local coordinates directly for global edges is the #1 cause of "lines start in empty space far from their nodes." Safest fix: don't use `transform` for positioning — place nodes at absolute SVG coordinates directly (via `x`/`y`/`cx`/`cy` attributes), then edge paths share the same coordinate space with zero offset math. Reserve `transform` for hover/animation only. Also: ensure the `viewBox` height encompasses ALL content — if the lowest element's `y + height` exceeds the viewBox, it is silently clipped.
6. **Edge anchoring**: append edges to the SVG BEFORE nodes, so node fills cover the line ends — or trim each endpoint by the node radius. Connect rectangular cards at border midpoints, not centers.
7. **Connector clearance**: a connector path must never visually pass through an unrelated node's bounding box. If parallel branches exist, lay them out so each branch occupies its own spatial lane (side-by-side, not stacked in overlapping regions). Every connector must form a continuous chain from source to target — no segment may dead-end into empty space with an arrowhead pointing at nothing.
8. **FORBIDDEN — the classic broken pattern**: DOM cards laid out by flex/grid (or absolute % offsets) + an SVG overlay whose line coordinates are hand-guessed values.
   - Card positions depend on viewport width, font metrics, and wrapping — guessed coordinates WILL miss, and the `resize` handler redraws with the same wrong constants.
   - If you need connectors between DOM cards, compute endpoints at runtime from `getBoundingClientRect()` relative to the diagram container (and recompute on resize); otherwise use rule 2.
   - If you create a container for JS-drawn connectors, the script that draws them must exist in the SAME block — a `<!-- lines drawn by JS -->` placeholder with no JS ships a diagram with a legend describing lines that don't exist.
9. **Interactions derive from the same data.** Hover-highlighting of related nodes/edges must be computed by filtering the SAME `edges` array by node id — never a hand-maintained map of element indices (`links: [0, 2, 6]`), which drifts silently the moment any edge is added or reordered.
10. **No HTML elements inside SVG.** The HTML5 parser treats SVG as "foreign content." When it encounters ANY HTML element (`<sub>`, `<sup>`, `<br>`, `<span>`, `<strong>`, `<em>`, `<b>`, `<i>`, `<p>`, `<div>`, etc.) inside SVG, it **exits foreign-content mode** — everything after that point is parsed as HTML, not SVG, destroying the entire remainder of the graphic. This is catastrophic: one `<sub>` in an axis label can silently wipe out all chart curves, data points, and annotations below it.

SVG-safe alternatives for common needs:
```xml
<!-- LINE BREAKS: use <tspan> with dy -->
<text x="700" y="248" text-anchor="middle" fill="#fff" font-size="14" font-weight="700">
  First line
  <tspan x="700" dy="18" font-size="11">Second line</tspan>
</text>

<!-- SUBSCRIPT (E_K, Na_v, etc.): use baseline-shift -->
<text x="60" y="350" font-size="12">E<tspan baseline-shift="sub" font-size="9">K</tspan> ≈ −90 mV</text>

<!-- SUPERSCRIPT (Na⁺, m²): use baseline-shift="super" or Unicode -->
<text>Na<tspan baseline-shift="super" font-size="8">+</tspan></text>
```
Common traps: scientific labels (`E<sub>K</sub>`, `V<sub>m</sub>`), flowchart diamond text (`Eligible?<br/>For Premium?`), styled spans (`<strong>important</strong>`). In SVG, the ONLY child element allowed inside `<text>` is `<tspan>`.
11. **Avoid single-letter variables for SVG/canvas dimensions.** Use descriptive names (`svgW`, `svgH`, `plotW`, `plotH`) — single-letter `W`/`H`/`R` are easily shadowed by domain variables (physics height, range, radius, etc.), silently corrupting all coordinate calculations downstream. This is the #1 cause of "everything is squished/offscreen" in physics and math visualizations. Short self-contained IIFEs (<30 lines) where the full scope is visible may use abbreviated names — the risk is in longer scripts where domain formulas appear far from the dimension declarations.
12. **SVG elements default to `fill:black` — the #1 flowchart rendering bug.** Unlike HTML (where `background` defaults to transparent), every SVG shape (`<path>`, `<rect>`, `<polygon>`, `<circle>`, etc.) renders with a solid black fill unless you explicitly set `fill="none"` or `fill:none` in CSS. For connector lines / arrows / elbows, ALWAYS set `fill:none` on EVERY path element — otherwise any bent path (L-shape, elbow, curve) will display an ugly black polygon formed by the implicit closure between start and end points. **This is not optional and not inherited** — each `<path>` needs it individually or via a CSS rule that covers ALL connector classes. Common mistakes that produce black polygons:
    - Defining a base class `.edge{fill:none;stroke:#666}` then creating variants (`.edge-yes`, `.edge-no`, `.edge-default`) that only set `stroke` color but forget `fill:none` — the variants revert to black fill because CSS specificity does NOT cascade `fill:none` from a sibling class.
    - Using `path.setAttribute('stroke','#666')` in JS but never calling `path.setAttribute('fill','none')` — stroke alone does not suppress fill.
    - Applying `fill:none` only to `.connector` but using a different class name (`.link`, `.arrow`, `.branch`) on some paths.
    **Safest fix — blanket selector**: In any diagram with connector paths, add ONE rule at the top of your styles that kills the fill default on all path-like elements:
    ```css
    svg path, svg line, svg polyline { fill: none; }
    ```
    Then specific filled shapes (node boxes, arrow markers) override with their own `fill:color`. This guarantees that no connector variant class — no matter the name — can accidentally revert to black fill. If you prefer per-class styling, you MUST still ensure every variant class explicitly includes `fill:none`.
    **Verification**: after writing any SVG with connectors, search your CSS for EVERY class name used on `<path>`/`<line>`/`<polyline>` elements and confirm `fill:none` is present in each rule — OR that the blanket selector above is in place. If in doubt, add `fill="none"` directly on the element — inline attributes never fail to match.
13. **Mind map priority: text legibility over visual flair.** A mind map's job is to present hierarchical information so every label is instantly readable — not to look impressive. Radial layouts sacrifice readability for aesthetics by curving text and crowding labels at the periphery. Never compute radial positions by manually assigning angles and radii to nodes — the model cannot predict at generation time how much angular/linear space each branch needs. Use a library with automatic node-spacing (ECharts `type:'tree'`, D3 `d3.tree()` / `d3.cluster()`) or the formula-driven SVG pos-table pattern (rule 2). **ALWAYS use horizontal tree** (`layout:'orthogonal', orient:'LR'`) for mind maps and topic hierarchies — labels are always left-to-right readable with no direction issues, and ECharts handles vertical spacing automatically. Radial is permitted ONLY when ALL of: (a) every label is under 15 characters, (b) branches are roughly balanced in count, AND (c) total leaf nodes are under 20. If any condition fails, horizontal tree is mandatory.

**If you choose radial layout** (rare — all three conditions above must hold): do NOT set a fixed `label.position` (e.g., `'right'`) — in a circle, fixed direction forces half the labels inward. Leave position unset so the library auto-orients labels outward. If your mind map has 5+ branches or labels longer than 2-3 words, you have violated the conditions above — switch to horizontal tree.

**ECharts tree label color trap — the #1 mind map rendering failure (3 out of 3 recent cases).**

In ECharts `type:'tree'`, `itemStyle.color` colors ONLY the tiny node **symbol** (dot/roundRect) — it does NOT become the label's background. The `label` is a separate text box positioned BESIDE the symbol, with its own `backgroundColor`. The model's common wrong assumption: "I set `itemStyle.color:'#297a2e'` so the node is green, then `label.color:'#fff'` gives me white text on the green node." WRONG — the white text renders on the label's background (series-level `backgroundColor: card` = white), not on the symbol color. Result: white text on white background = invisible branch names.

**RULE: NEVER set `label.color:'#fff'` (or any light color) on ECharts tree data items.** Use the series-level dark text default for ALL nodes. To visually distinguish root/branch nodes from leaves, use these safe alternatives:
- `label.borderColor: accentColor` (colored border, dark text) — recommended
- `label.backgroundColor: accentSoftColor` (tinted background, dark text)
- `label.fontWeight: 700` + larger `fontSize` for hierarchy emphasis

If you absolutely must use white text on a branch (rare): override BOTH `label.color:'#fff'` AND `label.backgroundColor:accentColor` together on that data item — never one without the other.

**Size the container for the data**: A horizontal tree stacks leaf nodes vertically. If `initialTreeDepth` exposes N leaf nodes at once, the container needs at least `N × 38px` of height to prevent label overlap. For trees with >20 total leaves, either (a) set `initialTreeDepth: 1` so only the first level is expanded by default (users click to drill down), or (b) compute height dynamically: `el.style.height = Math.max(450, leafCount * 38) + 'px'`. A fixed 640px container is only safe for ≤16 visible leaves.

**Correct ECharts mind map pattern** (copy this structure — do NOT invent your own label color scheme):
```js
var leafCount = 25; // count your actual leaves
el.style.height = Math.max(450, leafCount * 38) + 'px';
var c = echarts.init(el);
c.setOption({
  backgroundColor: 'transparent',
  series: [{
    type: 'tree',
    data: [treeData],
    layout: 'orthogonal',   // MANDATORY for mind maps
    orient: 'LR',           // MANDATORY — horizontal left-to-right
    initialTreeDepth: 1,    // safe default for >20 leaves (user clicks to expand)
    roam: true,
    symbolSize: 10,
    label: {                // series-level: applies to ALL nodes by default
      fontSize: 12,
      color: text,          // dark text — readable on light bg
      backgroundColor: card,
      borderColor: border,
      borderWidth: 1,
      borderRadius: 6,
      padding: [6, 10],
      lineHeight: 16
    },
    leaves: { label: { position: 'right', align: 'left' } },
    lineStyle: { color: muted, width: 1.5, curveness: 0.4 },
    expandAndCollapse: true,
    animationDuration: 400
  }]
});
// Root node: distinguish with bold + accent border (NOT white text)
// treeData.label = { fontWeight: 700, fontSize: 14, borderColor: accent, borderWidth: 2 }
// Branch nodes: distinguish with colored border
// treeData.children[0].label = { fontWeight: 600, borderColor: branchColor, borderWidth: 2 }
// NEVER: treeData.label = { color: '#fff' }  ← invisible on white backgroundColor!
```
**Key points**: (1) `layout:'orthogonal'` + `orient:'LR'` — never radial unless all 3 conditions pass; (2) series-level `label` uses dark text on light card — safe default for ALL nodes; (3) **NEVER use `label.color:'#fff'`** — distinguish branches via `borderColor`/`fontWeight`/`fontSize` instead; (4) `initialTreeDepth:1` for large trees; (5) `itemStyle.color` ≠ label background — they are separate visual elements.

Minimal data-driven pattern (edges are guaranteed to touch their nodes because both read the same `pos` table). Replace `ACCENT_HEX`, `MUTED_HEX`, `CARD_HEX`, `TEXT_HEX` with your palette values (or read them from CSS variables via `getComputedStyle` — see Chart theming):

```html
<svg id="tree" viewBox="0 0 1000 620" style="width:100%;height:auto"></svg>
<script>
(function(){
  var svg=document.getElementById('tree'); if(!svg)return;
  var NS='http://www.w3.org/2000/svg', W=1000, TOP=80, ROW=180, R=34;
  var levels=[['A','B'],['C','D','E'],['F','G','H','I']];   // node ids per generation/layer
  var edges=[['A','B','marriage'],['A','C','parent'],['D','E','partner'],['D','F','parent'],['D','I','bastard']];
  var pos={};
  levels.forEach(function(row,li){row.forEach(function(id,i){pos[id]={x:(i+1)*W/(row.length+1),y:TOP+li*ROW};});});
  edges.forEach(function(e){var a=pos[e[0]],b=pos[e[1]];
    if(e[2]==='marriage'){var l=document.createElementNS(NS,'line');     // spouses: short bar between edges
      l.setAttribute('x1',a.x+R);l.setAttribute('y1',a.y);l.setAttribute('x2',b.x-R);l.setAttribute('y2',b.y);
      l.setAttribute('stroke','ACCENT_HEX');l.setAttribute('stroke-width',2);svg.appendChild(l);return;}
    if(e[2]==='partner'){var l2=document.createElementNS(NS,'line');    // same-row non-marriage (lover/partner): dashed horizontal
      l2.setAttribute('x1',a.x+R);l2.setAttribute('y1',a.y);l2.setAttribute('x2',b.x-R);l2.setAttribute('y2',b.y);
      l2.setAttribute('stroke','ACCENT_HEX');l2.setAttribute('stroke-width',2);l2.setAttribute('stroke-dasharray','4,3');
      svg.appendChild(l2);return;}
    var p=document.createElementNS(NS,'path'),railY=(a.y+b.y)/2;         // parent→child: orthogonal elbow
    p.setAttribute('d','M '+a.x+' '+(a.y+R)+' V '+railY+' H '+b.x+' V '+(b.y-R));
    p.setAttribute('fill','none');p.setAttribute('stroke','MUTED_HEX');p.setAttribute('stroke-width',2);
    if(e[2]==='bastard')p.setAttribute('stroke-dasharray','2,4');
    svg.appendChild(p);});  // edges appended first — nodes drawn after cover any residue
  // children of a couple: use the marriage midpoint as the drop origin (a virtual {x:(a.x+b.x)/2,y:a.y} works)
  Object.keys(pos).forEach(function(id){var n=pos[id],c=document.createElementNS(NS,'circle');
    c.setAttribute('cx',n.x);c.setAttribute('cy',n.y);c.setAttribute('r',R);
    c.setAttribute('fill','CARD_HEX');c.setAttribute('stroke','ACCENT_HEX');c.setAttribute('stroke-width',2);
    svg.appendChild(c);
    var t=document.createElementNS(NS,'text');t.setAttribute('x',n.x);t.setAttribute('y',n.y+5);
    t.setAttribute('text-anchor','middle');t.setAttribute('fill','TEXT_HEX');t.setAttribute('font-size','14');
    t.textContent=id;svg.appendChild(t);});
})();
</script>
```

---

