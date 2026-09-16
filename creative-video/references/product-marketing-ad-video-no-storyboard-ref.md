---
name: product-marketing-ad-video-no-storyboard-ref
description: Product marketing ad video strategy for single-product commercial ads, product visual films, platform placement ads, TVC-like product showcases, and product conversion videos that do not focus on creator talking-head delivery. Produces confirmation-ready strategy, storyboard table, narration, Seedance-style prompt, and video generation package while preserving product consistency.
---

# Main MD Reference Notes

This file is read after the main `creative-video` workflow routes to product marketing ads. It does not override the main confirmation gate, product material gate, narration requirements, or storyboard-image gate.

## Reference Input Adaptation

Use routed references from the main file:

- `product_ref`: highest priority. Locks product appearance, package, SKU, logo, material, label layout, and selling points.
- `brand_ref`: brand tone, colors, banned words, and compliance.
- `platform_ref`: ratio, duration, placement rules, and restrictions.
- `style_ref`: cinematic tone, camera language, light, rhythm, and mood only. Do not copy another brand's slogan, product design, subtitles, or proprietary visual assets.
- `script_ref`: narration/copy source. Final narration must still appear in the confirmation summary.
- `scene_ref`: usage scenes, display spaces, textures, props, light.
- `audio_ref`: BGM, rhythm, voice, and sound-design reference.

Reference conflicts follow the main-file priority. Product truth and user-confirmed facts beat style references.

# Product Marketing Ad Video

Use this reference for pure product advertising, product showreels, marketing/TVC-style videos, single-item consumer conversion, and platform ads where the core is product visual persuasion rather than a human creator's recommendation.

## Output Contract

- A strategy summary with product lock, creative route, tone, audience, and conversion goal.
- A storyboard table before tool calls.
- Complete narration by default unless the user explicitly requests pure music/no narration.
- A video prompt ready for the generation tool.
- Generated video shown through the main file's display flow.

## Default Strategy

- Duration: 15s unless the user confirms another supported duration.
- Ratio: infer from platform; common defaults are 9:16 for vertical placements, 16:9 for TVC/brand film, 1:1 or 4:5 for feed commerce.
- Product image is required unless the user explicitly chooses a fictional/concept product.
- Use 6-10 shots for 15s marketing videos; denser product ads may use more micro-moments, but product readability is more important than cut count.
- Narration is default. Functional/information routes use 3-5 narration lines plus a closing slogan. Poetic/premium routes use 2-3 poetic lines plus a closing slogan.

## Communication Mainline And Creative Craft

Choose one main communication line:

- Pain point to solution.
- Product feature to visible benefit.
- Ingredient/technology to proof.
- Scenario to desire.
- Ritual/premium atmosphere.
- Before/after contrast.
- Gift or seasonal emotion.

Add one creative hook:

- Macro texture reveal.
- Product transformation.
- Scenario contrast.
- Sensory close-up.
- Source-to-product journey.
- Problem interruption.
- Light/material ritual.

The ad should be memorable because one core idea is executed clearly, not because many unrelated visual tricks are stacked.

## Seedance 2.0 Prompt Standards

The final prompt should be a director-style timeline, not a loose paragraph. Include:

- Reference asset roles.
- Product lock.
- Creative goal and audience.
- Visual world and tone.
- Shot-by-shot timeline.
- Narration in `{specific narration}`.
- BGM/sound effects.
- Constraints and text policy.

### Video Rewrite Prompt Refinement

For each shot, specify subject, product position, action, camera motion, light, scene, material, narration/sound, and preservation points.

Convert abstract terms:

- Premium -> restrained palette, controlled composition, material close-ups, slow reveal.
- Technology -> clean UI/data motion, precise macro, cool light, modular graphics.
- Fresh -> bright natural light, clean surfaces, water/ingredient cues if true.
- Powerful -> direct proof action, strong contrast, kinetic motion, credible result.

### Subtitles, Ad Copy, And Dialogue Symbols

Narration uses `{specific line}`. On-screen text must be short, confirmed, and not a transcript. Do not generate fake subtitles, fake platform UI, fake badges, fake prices, or unsupported claims.

## Reference Asset Responsibilities

Product images define product identity. Brand references define style boundaries. Scene/style/audio references support expression only. Platform references constrain format.

### Reference Image Use Judgment

Use product images whenever product consistency matters. If the product image is low quality or ambiguous, state the assumed locked product/SKU in the confirmation summary. If a reference video is provided, extract rhythm and shot logic only.

## Product Consistency Highest Priority

Do not redraw product packaging, label, logo, SKU, color, shape, material, or scale. Every product shot must preserve:

- Product count and SKU.
- Package shape, cap/pump/box structure.
- Label and logo position.
- Main colors and materials.
- Relative size to hand/scene.
- Visible reflection and shadow matching the scene.

If product consistency fails, the result is not acceptable even if visually attractive.

## General High-Quality Ad Strategy

Strong ads have:

- Clear opening hook within 0-2s.
- Product visibility early and repeatedly.
- One proof moment.
- Sensory or emotional payoff.
- A closing product/logo/CTA hold.
- Sound design that supports product action.

## High-Quality Material Summarization Strategy

When using reference videos or moodboards, summarize:

- Camera rhythm.
- Lighting and color temperature.
- Product treatment.
- Scene type.
- Sound mood.
- Editing density.

Do not copy proprietary brand assets or slogans.

## Short-Ad Hook Mechanisms

Use one of:

- Pain-point collision.
- Visual surprise.
- Macro reveal.
- Before/after split.
- Product action proof.
- Ritual opening.
- Seasonal/gift emotion.

Avoid opening with generic logos or empty scenery unless it serves a premium slow-reveal route.

## Camera Movement Matrix

Choose movements by product and tone:

- Macro push-in: texture, skincare, food, jewelry.
- Orbit: bottle, device, gift box, sculptural products.
- Match cut: before/after, source-to-result, scene transition.
- Handheld close-up: natural use or lifestyle product.
- Top-down: unboxing, food, desk, beauty routine.
- Slow dolly: premium ritual or cinematic reveal.
- Kinetic whip/snap cuts: youth, sports, fast commerce.

## Speed, Rhythm, And Time Remapping

Use rhythm contrast. Do not keep every shot the same speed. Slow down proof or texture moments; speed up setup or transition. Keep product/logo readable.

## 15s Generic Structure Template

| Time | Role |
|---|---|
| 0-2s | Hook: pain point, macro reveal, visual contrast, or product appearance |
| 2-5s | Product identity and key scene |
| 5-8s | Selling point/proof action |
| 8-11s | Use result, sensory payoff, or emotional value |
| 11-13s | Secondary selling point or audience fit |
| 13-15s | Product/logo/slogan/CTA hold |

## Tone-First Execution Strategy

Choose tone before writing shots. All camera, light, music, narration, and copy follow it. Do not mix premium slow film with loud sale graphics unless the user asks for that hybrid.

## Shot Density And Atmosphere Budget

High-information ads need denser shots but less decorative atmosphere. Premium/poetic ads use fewer shots and more material/lighting atmosphere. Allocate time consciously.

## High-Information Storyboard Matrix

For feature-heavy products, map each selling point to a proof shot:

- Feature.
- Visible proof action.
- Benefit translation.
- Narration line.
- Product preservation point.

Do not list features without proof visuals.

## Source Element Closed Loop

If the ad references ingredients, origin, technology, or craft, visually close the loop from source -> product -> user benefit. Do not imply ingredients or technologies not provided.

## TVC Scene Continuity

TVC-like ads need one coherent visual world. Auxiliary shots should connect by action, material, light, sound, or narrative cause. Avoid jumping from kitchen to city to lab to stage without logic.

## Atmospheric Empty Shot Strategy

Use atmosphere shots only to support the product: light, material, environment, or emotion. Do not let empty beauty shots replace product proof.

## Premium Ritual Scene Strategy

For premium products, use slow reveal, refined surface, precise hand action, restrained copy, subtle reflections, and low-noise sound design. Keep claims minimal and source-safe.

## Skincare / Medical-Research Strategy

### Category Recognition Priority

Identify whether the product is skincare, beauty, medical-aesthetic, health-adjacent, or daily care. Do not make medical claims unless supplied and allowed.

### 15s Skincare Evidence Chain

Use texture -> application -> absorption/finish -> skin feel/result wording. Claims remain sensory unless provided as verified data.

### Skincare Route Selection

Choose between scientific clean, lifestyle gentle, premium ritual, ingredient proof, or before/after if the user provides basis.

### Skincare Ad Forbidden Zone

Do not invent efficacy percentages, cure claims, medical claims, dermatologist endorsements, ingredient concentrations, before/after results, or certifications.

## Audio Strategy

Audio includes BGM, voiceover, foley, and product sounds. Narration must be audible above music. Product sounds such as cap click, liquid pour, texture swipe, packaging open, or device startup can carry proof.

## Category Routing

Adapt by category:

- Beauty/skincare: texture, application, finish, skin feel.
- Food/drink: freshness, pour/bite/steam/crunch, appetite appeal.
- Electronics/3C: structure, interface, speed, precision, use scenario.
- Home/lifestyle: comfort, convenience, before/after space.
- Fashion/jewelry: material, wearing moment, body movement, premium detail.
- Gifts: unboxing, recipient emotion, occasion, packaging ritual.

## Tone Style Routing

Common routes:

- Functional proof.
- Premium cinematic.
- Youthful dynamic.
- Poetic sensory.
- Tech minimalist.
- Warm lifestyle.
- Promotional conversion.

## Selling Point Arrangement

### Functional Products With 3+ Selling Points

Prioritize one core selling point. Convert other points into proof accents. Do not overload the 15s video with all features equally.

For each selling point:

```text
selling point -> visible proof -> user benefit -> narration line -> shot moment
```

## Storyboard And Prompt Delivery

Storyboard table fields:

```text
Time | Visual | Camera/motion | Product proof | Narration/sound | On-screen text | Preservation constraints
```

Final prompt blocks:

- `Reference asset roles`
- `Product lock`
- `Creative concept`
- `Target audience`
- `Tone route`
- `Storyboard timeline`
- `Narration`
- `Audio`
- `Visual text policy`
- `Constraints`

## Final Quality Constraints

No fake product claims, no fake price/discount/date/rating/certification, no unauthorized logos/customers, no copied competitor assets, no unreadable transcript subtitles, no product drift, no scene jumps that break continuity.

## Tool Calls

Follow the main file's confirmation, storyboard gate, video tool, and `notify_hunman` display rules.

## Success Format For User

After successful display, briefly state duration, ratio, product reference used, creative route, and any limitation.

## Internal Self-Check

Check product consistency, narration completeness, selling-point proof, hook, CTA, ratio/duration, platform fit, claim safety, sound, and whether the storyboard was shown before tool call.
