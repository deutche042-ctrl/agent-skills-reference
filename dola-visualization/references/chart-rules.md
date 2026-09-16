# Chart & Visualization Rules

### Chart & Visualization Rules

**MANDATORY** (within renderer blocks): Interactive chart libraries. **FORBIDDEN** in renderer blocks: matplotlib base64 PNGs (use matplotlib only for static image plots via the CI Handbook's *Plotting & Showing Images* section).

The exact `<script>` tags (and the globals each exposes) are in *Pinned CDN paths* in SKILL.md — copy from there rather than retyping a path.

| Library | CDN | Best For |
|---------|-----|----------|
| **ECharts** | `cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js` | Dashboards, multi-series |
| **Chart.js** | `cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.js` | Simple clean charts |
| **D3.js** | `cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js` | Custom visualizations |
| **Plotly.js** | `cdn.jsdelivr.net/npm/plotly.js@2/dist/plotly.min.js` | Scientific, 3D |

Prefer pure SVG + Canvas + vanilla JS when feasible (zero-dependency, most stable for streaming).

**Chart theming (match the palette):**

Read CSS variables at runtime via `getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()` etc. (see the skeleton's chart script for the complete pattern). Fall back to the category's known hex only if the computed value is empty. Then use these values in `setOption`:

- **Series colors**: derive from the palette — `accent` first, then `accent2`; for 3+ series, derive lighter variants by appending alpha to the hex string: `accent+'99'` (60% opacity, appears lighter on white bg) for series 3, `accent2+'99'` for series 4. This works because ECharts accepts 8-digit hex (`#RRGGBBAA`). For CSS-only contexts (card backgrounds, borders), you may also use `color-mix(in srgb, var(--accent) 55%, white)`. Do NOT use `muted` as a data series color — it matches axis labels and grid lines, making data indistinguishable from chrome. NEVER fall back to the library's default multi-color palette; maximum 4–5 series colors.
- **Tooltip**: `backgroundColor` = the row's `--card` hex, `borderColor` = the row's `--border` value, `textStyle.color` = the row's `--text` hex.
- **Axes**: hide ticks (`axisTick:{show:false}`); axis lines and splitLines at `--border` strength; axis labels in `--muted`. **Axis label formatter** uses `{value}` (NOT `{c}`) — `{c}` is for series labels only and displays literal "{c}" text on every tick when misused on an axis.
- **Y-axis scale for trend/time-series charts**: ALWAYS set `yAxis:{ scale: true }` (or explicit `min`/`max` near data bounds) for line charts showing trends, prices, or time-series data. ECharts defaults to `scale:false` which forces the Y-axis to include 0 — this compresses data that lives far from zero (e.g. stock prices at 25,000+, gold at $4,000+) into a tiny band at the top, making trends invisible. `scale:true` lets ECharts auto-fit the axis to the actual data range, making fluctuations clearly visible. Exception: bar charts comparing magnitudes SHOULD include 0 (to avoid misleading proportions).
- **Explicit axis bounds must contain all data**: When setting `min`/`max` on an axis, verify ALL series values fall within that range — values outside are silently clipped (the line exits the chart area), making the chart appear blank. If data spans multiple orders of magnitude (e.g., values from 1.5 to 270), use `type:'log'` instead of a linear axis with a tight `max`. Prefer omitting explicit bounds and letting ECharts auto-compute unless you have a deliberate reason for clipping (e.g., ignoring outliers with a visible annotation explaining the truncation).
- **Axis-data type consistency**: Every value in `series.data` must match the axis type it maps to. `type:'time'` → date strings (`'2026-06-25'`) or ms-timestamps; `type:'value'` → numbers; `type:'category'` → strings matching `axis.data` entries. A mismatch silently maps data to wrong coordinates (e.g., integer `16` on a time axis becomes 1970-01-01T00:00:00.016Z — off-screen). If your source data is integer offsets, convert to dates before passing to ECharts.

**Legend-axis collision rule**: When `legend` is at `bottom` and the x-axis has category labels, you need `grid.bottom` ≥ 55px (30px for axis labels + 25px for legend). In compact containers (≤300px height), prefer `legend` at `top` or `right` to avoid overlap. Same applies to `legend:{left:0}` colliding with y-axis labels.

**Brace-depth discipline (prevents the silent empty-chart failure):**
A missed `}` in `setOption` is a parse error that kills the whole `<script>` tag before anything runs (Hard Constraint 6) — the chart container just stays empty, no error text, because even the fallback never executes. Brace miscounts happen in deep single-line nesting. Two mechanical rules:
- **Extract gradients into a variable.** NEVER inline a `colorStops` gradient inside an already-nested option — that pushes one line to 5+ brace levels:
```js
// read palette once, define gradient, reference by name — setOption stays shallow
var st=getComputedStyle(document.documentElement);
var accent=st.getPropertyValue('--accent').trim()||'#2d7eb5';
var grad={type:'linear',x:0,y:0,x2:0,y2:1,colorStops:[{offset:0,color:accent},{offset:1,color:accent+'4d'}]};
// ...then inside setOption: series:[{type:'bar',data:vals,itemStyle:{borderRadius:[6,6,0,0],color:grad}}]
```
- **Extract `.map()` data transforms outside `setOption`.** When each data point needs computed `itemStyle` (conditional color, per-item borderRadius), build the array BEFORE calling `setOption`, then pass the variable. Inline `.map(function(){return{itemStyle:{...}}})` inside `series.data` creates 5-level nesting where one missed brace kills the chart silently:
```js
// GOOD: pre-compute, keep setOption shallow
var barData = vals.map(function(v){
  return { value:v, itemStyle:{ borderRadius: v>=0?[0,6,6,0]:[6,0,0,6], color: v>=0?accent:'#dc5a5a' } };
});
c.setOption({ series:[{ type:'bar', data:barData, barWidth:18 }] });
```
- **Value labels live at SERIES level in ECharts 5**: `series:[{type:'line',data:vals,label:{show:true,formatter:'{c}%'}}]`. NEVER nest `label` inside `itemStyle` or `areaStyle` — that is the ECharts 4 location: in v5 it is silently ignored (your labels vanish), and burying it one level deeper in a long literal is exactly where the closing brace gets lost.
- Beware: `formatter:'{c}%'` contains braces inside a string — they don't affect parsing, but they defeat balancing braces by eye. One more reason to keep option literals shallow.
- **Multi-dimensional data: use `params.data[N]`, not `params.value`** in tooltip formatters. When series data items are arrays (e.g., `[0, 1008, 'annotation']`), `params.value` may return the entire array (producing garbled tooltip text like `"0,1008,annotation hPa"`). Always index explicitly: `params.data[1]` for the Y value, `params.data[2]` for extra info. This applies to any data format beyond simple numbers — scatter `[x,y]`, custom `[dim0,dim1,dim2,...]`, etc.

**Bar `borderRadius` direction rule** (models get this wrong almost every time for negative values):

ECharts `borderRadius` follows CSS order: `[top-left, top-right, bottom-right, bottom-left]`. Round corners MUST be on the **visual tip** of the bar (the end farthest from the 0-axis baseline), never on the baseline end:

| Bar direction | Data sign | Correct `borderRadius` |
|---|---|---|
| Vertical upward | positive | `[6,6,0,0]` (top rounded) |
| Vertical downward | negative | `[0,0,6,6]` (bottom rounded) |
| Horizontal rightward | positive | `[0,6,6,0]` (right rounded) |
| Horizontal leftward | negative | `[6,0,0,6]` (left rounded) |

If your dataset contains BOTH positive and negative values, specify per-item in `series.data`:
```js
series:[{type:'bar',data:vals.map(function(v){
  return {value:v,itemStyle:{borderRadius:v>=0?[6,6,0,0]:[0,0,6,6]}};
})}]
```
Note: `itemStyle.borderRadius` does NOT accept a function in ECharts 5 — only arrays or numbers. You must set it per data point via the object form above. A rounded baseline-end + flat tip is visually wrong and immediately noticeable.

**Stacked bar exception**: When bars are stacked (`stack:'x'`), ONLY the topmost series in the stack should have `borderRadius` — all lower series must use `[0,0,0,0]` (flat). If the bottom series also has rounded top corners, a visible gap appears between the stacked segments because the rounded corners create empty space that the upper series doesn't fill.

**Treemap data format**: Each item MUST use `{name:'Label', value:NUMBER}`. The field MUST be called `value` — ECharts ignores non-standard fields (e.g. `v`, `val`, `amount`), causing all blocks to render with equal size. Label `formatter` goes inside `label:{formatter:function(p){return p.name+'\n'+p.value+'%'}}`, NOT at series root level (where it is silently ignored).

**CDN retry-guard (MANDATORY for any chart using an external library)** — In the streaming renderer, CDN `<script src="...">` tags may load asynchronously. If your inline script runs before the library is ready, `echarts`/`THREE`/etc. is `undefined` and the entire IIFE silently fails — producing a blank chart with no error message. EVERY inline script that references a CDN library MUST wrap its body in a retry loop (see the skeleton's chart `<script>` for the complete working pattern). The structure is: `(function init(n){ if(typeof LIB==='undefined'){if(n<40){setTimeout(function(){init(n+1)},250);return;} el.textContent='...';return;} /* real init */ })(0);` — retry up to ~10s, then show fallback text. Omitting this is a guaranteed intermittent blank-chart bug. For multi-script setups (Three.js + addons), the retry must check ALL globals — see *Three.js CDN & addon rules* in SKILL.md (HC section).

**Timeline visualization choice** (prevents the "label overlap" failure):

For event sequences with text descriptions (>5 labeled events), use an **HTML/CSS vertical timeline layout** — NOT an ECharts scatter/custom chart. ECharts label positioning cannot prevent overlap when many labeled points share the same Y-axis band. A scatter chart with `label:{show:true}` on 10+ points in the same category band guarantees unreadable overlapping text.

| Data shape | Correct visualization | Wrong choice |
|---|---|---|
| 5–30 events with text descriptions, ordered in time | HTML/CSS vertical timeline (one row per event, stage-colored badge + text) | ECharts scatter with category Y-axis + labels |
| Numeric time-series (price, temperature, pressure over time) | ECharts line/area chart (values ARE the data, no long labels) | HTML timeline |
| Gantt/schedule (tasks with start/end times) | ECharts custom/bar with `renderItem` or HTML table | Scatter with labels |

When you need BOTH (numeric trend + event annotations on the same view), use ECharts for the numeric chart with `markPoint`/`markLine` for a FEW key events (≤5), and a separate HTML timeline below for the full event list.

**ECharts `custom` series `renderItem` format** (for Gantt charts, range bars, or any custom graphic):

Graphic elements returned by `renderItem` MUST put geometry in `shape:{}` — root-level `x/y/width/height` is NOT reliable:
```js
// CORRECT
renderItem: function(params, api) {
  var start = api.coord([api.value(1), api.value(0)]);
  var end   = api.coord([api.value(2), api.value(0)]);
  var barH  = api.size([0, 1])[1] * 0.6;
  return {
    type: 'rect',
    shape: { x: start[0], y: start[1] - barH/2, width: end[0]-start[0], height: barH },
    style: api.style({ fill: api.visual('color') })
  };
}

// WRONG — geometry at root level, unreliable in ECharts 5
return { type:'rect', x:start[0], y:start[1], width:w, height:h, style:{fill:color} };
```
For `type:'path'`, use `shape:{d:'M... path data'}` (not `pathData`). For `type:'group'`, children still use `shape:{}` individually.

Common `custom` series pitfalls (all produce blank/invisible charts with no error):
- **`api.value` is a FUNCTION, not an array**: You must CALL it — `api.value(0)`, `api.value(1)`, etc. Writing `var v = api.value; v[0]` assigns the function object to `v` and reads property `"0"` off it → `undefined`. All coordinates become NaN, all bars vanish. Correct: `var v0 = api.value(0), v1 = api.value(1);`
- **`api.coord()` returns an ARRAY, not a number**: `api.coord([xVal, yVal])` always returns `[pixelX, pixelY]`. You MUST index into it: use `[0]` for X and `[1]` for Y. A common bug is `var y = api.coord([0, idx]) - 10` — this subtracts from the array itself, producing NaN, and all bars vanish. Correct: `var y = api.coord([0, idx])[1] - 10`.
- **Data-axis type mismatch**: If your axis is `type:'time'`, every data value mapped to that axis MUST be a date string or timestamp — not an integer offset. An integer like `16` is interpreted as 16ms after Unix epoch (1970-01-01), placing bars far off-screen. Similarly, `type:'category'` expects strings matching `yAxis.data`, and `type:'value'` expects numbers. Always verify that `api.value(N)` returns a value compatible with the axis it maps to.
- **`label`/`itemStyle` on data items are IGNORED**: In `custom` series, ALL rendering is controlled by `renderItem`. Standard ECharts properties like `label:{show:true}` or `itemStyle:{color:...}` set on data items have NO effect. To show text labels, return a `type:'text'` element from `renderItem`; to color bars, set it in `style` within the returned graphic element.
- **Index mismatch**: Double-check that the data array indices match what `api.value(N)` reads — off-by-one in the encode/data mapping is the #1 cause of invisible custom bars.

---

