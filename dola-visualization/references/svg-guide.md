# SVG Guide — Authoring, Traps, and Sources

SVG is the default visual primitive in this handbook: it costs zero network requests, scales to any density, inherits the palette through `currentColor`, and — unlike a raster image — never 404s or expires. Every icon, gauge, badge, sparkline, and hand-drawn illustration in a renderer block should be inline SVG unless a chart library is genuinely warranted.

This file covers writing SVG by hand. Related rules live elsewhere and are not repeated here: node-link geometry, orthogonal connectors, and the `fill` default trap are in [diagram-rules.md](diagram-rules.md); the SVG-`transform`-versus-CSS-`animation` conflict and minimum touch sizes are in [quality-and-mobile.md](quality-and-mobile.md); icon-library CDN tags are in the *Pinned CDN paths* table in SKILL.md.

---

## Hand-written or icon library?

Write the SVG yourself for anything under roughly eight icons, and for every non-icon visual — gauges, diagrams, decorative shapes, illustrations. A stroke icon is four or five path commands; pulling 404 KB of Lucide to draw three of them is a bad trade in a streaming artifact, where every byte delays first paint.

Reach for **Remix Icon** (pure CSS, nothing to time) or **Lucide** (JS, needs the retry guard) when a page is genuinely icon-dense — a feature grid, a long settings list, a toolbar. Mixing sources is the thing to avoid: a hand-drawn icon beside a Lucide one reads as a mistake, because stroke weights and corner radii will not match. **One icon system per artifact.**

---

## The anatomy that actually matters

```html
<svg width="20" height="20" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
     aria-hidden="true">
  <path d="M3 12h18M12 3v18"/>
</svg>
```

- **`viewBox` is the coordinate system**, `width`/`height` are the rendered size. Keep authoring at `0 0 24 24` and resize via `width`/`height` — that is the convention every icon set uses, so borrowed paths drop in unmodified. An SVG with no `viewBox` cannot scale: it will ignore a percentage width and render at its intrinsic size or collapse.
- **`fill="none"` is mandatory on stroke icons.** SVG shapes default to `fill:black` — omit it and your outline icon becomes a black blob, on a dark background an invisible one. This is the single most common SVG bug in generated HTML.
- **`stroke="currentColor"` is what makes theming work.** The shape then takes the CSS `color` of its container, so `<span style="color:var(--accent)">` themes the icon with no SVG edits, and hover/active states work through ordinary CSS inheritance. Never hardcode a hex inside an icon path.
- **`stroke-linecap="round" stroke-linejoin="round"`** gives the soft modern outline look. Drop both for a technical or editorial feel — just be consistent across the artifact.
- **`aria-hidden="true"`** on decorative icons keeps them out of the accessibility tree. An icon that carries meaning on its own (an icon-only button) instead needs `role="img"` and a `<title>` child, or an `aria-label` on the button wrapping it.

---

## Traps that make SVG render blank, black, or wrong

**ID collisions across multiple SVGs.** IDs are document-global, not scoped per `<svg>`. Two SVGs that each define `<linearGradient id="grad">` will both resolve `url(#grad)` to whichever parsed first, so the second element silently takes the wrong gradient — and if the first is removed, the reference breaks entirely. This bites hardest in a page with several gauges or charts built from the same template. Suffix every `id` on a `<linearGradient>`, `<clipPath>`, `<mask>`, `<filter>`, or `<marker>` with something unique: `id="grad-revenue"`, `id="clip-avatar-3"`.

**`transform-origin` resolves against the viewBox, not the shape.** To spin an element about its own center you need both properties, or it will orbit the canvas origin instead:

```css
.spinner-arm{ transform-box:fill-box; transform-origin:center; animation:spin 1.2s linear infinite; }
```

**Strokes scale with the viewBox.** If you render a `0 0 24 24` icon at 96px, a `stroke-width:2` becomes a visually fat 8px line. Either scale the stroke down proportionally, or add `vector-effect="non-scaling-stroke"` to hold it at a constant device width.

**`<text>` does not wrap.** There is no line breaking in SVG — a long string runs straight out of the viewBox and gets clipped. Break lines yourself with `<tspan x="0" dy="1.2em">` per line, and position with `text-anchor` (`start`/`middle`/`end`, horizontal) plus `dominant-baseline="middle"` (vertical), since the default baseline sits on the glyph bottom rather than its center.

**No `<style>` element inside `<svg>`.** The FOUC rule that bans `<style>` in markup applies here too — SVG rules belong in the stylesheet you inject via `document.createElement('style')`. Presentation attributes on the elements themselves are also fine and stream more safely.

**Referencing an SVG file instead of inlining it.** `<img src="icon.svg">` cannot inherit `currentColor` and cannot be themed, and an external file is a banned asset dependency under HC#14 regardless. Inline the markup.

**Case matters in the attribute names.** Write `viewBox`, `preserveAspectRatio`, `gradientUnits`, `stroke-width` exactly as spelled here. `strokeWidth` is React syntax and does nothing in plain HTML.

---

## Sizing and responsiveness

For a fixed-size icon, set `width` and `height` in px and let the `viewBox` do the mapping. For an illustration or gauge that should track its container, set `width="100%"`, keep the `viewBox`, and give the wrapper an explicit height — the same discipline the ECharts container rule enforces, and for the same reason: a percentage height inside an unsized parent collapses to zero.

`preserveAspectRatio` defaults to `xMidYMid meet`, which fits the whole viewBox inside the element and centres it. That is almost always what you want. Reach for `slice` only when the graphic should crop-to-fill like a background, and `none` only when you deliberately want to stretch a shape out of proportion.

---

## A small library of shapes worth knowing

```html
<!-- Circular progress ring: dasharray = circumference, dashoffset = remaining -->
<svg width="120" height="120" viewBox="0 0 120 120">
  <circle cx="60" cy="60" r="52" fill="none" stroke="var(--border)" stroke-width="10"/>
  <circle cx="60" cy="60" r="52" fill="none" stroke="var(--accent)" stroke-width="10"
          stroke-linecap="round" stroke-dasharray="327" stroke-dashoffset="98"
          transform="rotate(-90 60 60)"/>   <!-- start the arc at 12 o'clock -->
</svg>

<!-- Sparkline: points are plotted data, not decoration -->
<svg width="160" height="40" viewBox="0 0 160 40" fill="none" preserveAspectRatio="none">
  <polyline points="0,32 32,24 64,28 96,12 128,16 160,4"
            stroke="var(--accent)" stroke-width="2" stroke-linejoin="round"
            vector-effect="non-scaling-stroke"/>
</svg>

<!-- Gradient fill with a collision-safe id -->
<svg width="100%" height="80" viewBox="0 0 300 80" preserveAspectRatio="none">
  <defs>
    <linearGradient id="fill-traffic" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="var(--accent)" stop-opacity=".35"/>
      <stop offset="100%" stop-color="var(--accent)" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <path d="M0,70 L60,40 L120,52 L180,20 L240,32 L300,8 L300,80 L0,80 Z" fill="url(#fill-traffic)"/>
</svg>
```

The circumference for the ring is `2 × π × r` — compute it for your actual radius rather than reusing 327, and compute the offset from real data in the code interpreter. Inventing the number defeats the point of drawing a chart.

---

## Where icon paths come from

When you need a shape you cannot recall precisely, these are the reference sets whose geometry is worth imitating. All are permissively licensed and safe to reproduce in generated output.

| Set | License | Grid | Character |
|---|---|---|---|
| [Lucide](https://lucide.dev/icons/) | ISC | 24×24, stroke 2 | The default outline vocabulary; successor to Feather |
| [Remix Icon](https://remixicon.com/) | Apache-2.0 | 24×24 | Matching line **and** fill variants of every icon |
| [Heroicons](https://heroicons.com/) | MIT | 24×24 outline, 20×20 solid | Tailwind's companion set |
| [Bootstrap Icons](https://icons.getbootstrap.com/) | MIT | 16×16 | Dense UI and form glyphs |
| [Simple Icons](https://simpleicons.org/) | CC0-1.0 | 24×24 | Brand and product logos, single-path |

Two cautions. Do not guess a brand logo's path from memory — a mangled logo looks worse than a text label, so use a plain wordmark instead when you are unsure. And match the grid you borrow from: dropping a 16×16 Bootstrap path into a `0 0 24 24` viewBox renders it at two-thirds scale, floating in the top-left corner.

---

## Before you ship an SVG

- [ ] `fill="none"` present on every stroke-based shape, and no hardcoded hex where `currentColor` or a `var(--*)` belongs?
- [ ] Every `linearGradient` / `clipPath` / `mask` / `filter` id unique across the whole page?
- [ ] `viewBox` present, and the drawing actually inside it — nothing clipped at an edge or stranded outside?
- [ ] Icons all from one system, topic-specific rather than one glyph stamped everywhere?
- [ ] Decorative icons `aria-hidden="true"`; meaning-carrying icons labeled?
- [ ] Any animated group wrapped so CSS `transform` never overwrites a positioning `transform` attribute (see [quality-and-mobile.md](quality-and-mobile.md))?
