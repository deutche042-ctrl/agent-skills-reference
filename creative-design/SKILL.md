---
name: creative-design
description: Use when the user asks to generate, edit, retouch, redraw, create text-to-image or image-to-image assets, outpaint, change backgrounds or styles, replace local regions, derive from reference images, extend a series, or adapt commercial creative images to multiple ratios. Trigger scenarios include posters, key visuals, banners, covers, social images, long social posts, e-commerce main images, product detail pages, product shots, logos, IP characters, mascots, packaging, brand application materials, campaign materials, brochures, landing pages, knowledge posters, teaching graphics, textbook illustrations, courseware images, mind maps, knowledge graphs, flowcharts, data charts, scientific diagrams, formula derivation visuals, engineering drawings, and multi-asset visual systems.
---

# Doubao Creative Design

## Positioning

This skill is the unified entry point for creative image design. It identifies user intent, decides whether clarification is needed, chooses text-to-image or image-to-image execution, maintains consistency of core assets, and reads the appropriate reference document for the requested deliverable type.

The main `SKILL.md` contains only general rules and routing. Product-specific rules must be loaded from `references/` only when needed; do not load every reference at once.

## Overall Workflow

1. Decide whether the task is image generation, image editing, image extension, or visual-material planning.
2. Identify the role of uploaded images, previously generated images, or existing assets: core asset, style reference, edit target, content material, or ordinary source material.
3. Detect continuation intent. If the user says things like "based on the generated one", "use the previous image", "continue", or "extend the last version", first decide whether `image_edit` should be used and identify exactly which previous generated image is referenced.
4. Route to a specific deliverable type when possible, then read only the corresponding reference file.
5. Ask clarification only when it significantly affects the result. Ask 1-3 questions at most. If enough information is available, execute directly.
6. Establish or lock the current core asset. Later extensions should use `image_edit` based on that asset by default.
7. Write an independent, complete, visually concrete Chinese prompt for each image and choose a separate `ratio`.
8. Call the available image tool. If the tool is unavailable, state the capability gap; do not pretend the image was created.
9. After completion, provide only necessary feedback. Do not mechanically repeat the image description.

## Tool Protocol

Use the tools that are actually available in the host environment. If tool fields differ from these references, this section takes priority.

- `image_gen`: generate a new core image or an image without a reference. Prefer `prompt` and `ratio`.
- `image_edit`: edit, extend, or create a series based on an uploaded image, a previous image, or a confirmed core asset CDN URL. Prefer `image_reference_url_list`, `prompt`, and `ratio`.
- Fields that appear in reference files such as `tool_mode`, `asset_id`, `visible_text`, `image`, `canvas:`, and `reference image ID` are internal planning or legacy-template fields. Map final tool calls to the fields above.
- If the actual tool supports only `width/height`, derive them from `ratio`; do not write dimensions inside the prompt.
- If the actual tool supports only local files or URLs, pass images according to that tool's requirements. Do not put file paths, URLs, model names, seeds, or tool fields in the prompt.
- Target image resolution should be at least 2048 px. If the host tool has a lower limit, use the maximum available and mention the limitation.

When a clear reference image, edit target, or core asset exists, never replace image-to-image extension with pure text-to-image unless the user explicitly asks for a remake without consistency.

## Deliverable Routing

Arbitrate in this order: explicit deliverable, current multi-turn context, uploaded-image role, platform keywords, general visual task. When a concrete deliverable is matched, read the relevant reference. If no specialized brand, e-commerce, or media route is matched, treat it as a general creative image task and do not force it into a brand-system flow. When multiple deliverables are requested, create the core asset that most affects later work first, then create downstream applications.

| User intent / keywords | Reference / execution |
|---|---|
| Logo, mark, symbol, wordmark, lockup, horizontal/vertical versions, monochrome, small-size logo, favicon, logo upgrade, logo guideline page | `references/brand-logo-system.md` |
| IP, mascot, character design, turnarounds, character sheet, emoji pack, stickers, outfit versions, character poster, merchandise, IP plus logo lockup | `references/brand-ip-character-system.md` |
| Packaging, product package, gift box, bottle label, can, pouch, carton, dieline, wrapping paper, seal, hang tag, unboxing, shelf display, SKU variants | `references/brand-packaging-system.md` |
| Brand applications, key visual, campaign poster, communication cover, content card, banner, brochure, leaflet, landing page, exhibition material, roll-up banner, store material, stickers, merchandise | `references/brand-application-system.md` |
| E-commerce main image, listing image, detail page, A+ page, shop header, promotion image, selling-point image, comparison image, livestream background, product hero image, Xianyu, Taobao, JD, Pinduoduo, Amazon, independent-store product image | `references/ecommerce-design.md` |
| Knowledge poster, educational visual, teaching diagram, textbook illustration, courseware image, mind map, knowledge graph, flowchart, logic diagram, scientific structure, data chart, engineering drawing, time-space evolution diagram, formula derivation, force analysis, circuit diagram, receipt/voucher teaching diagram, UI teaching diagram, knowledge-graphic optimization/correction/redraw | `references/knowledge-education-visual.md` |
| Bilibili, Douyin, Kuaishou, WeChat Moments, WeChat Official Account, Xiaohongshu, note, seeding post, OOTD, store visit, H5, interactive long page, multi-platform social image, long social graphic, long article graphic, focus banner, promotional poster, platform communication image | `references/media-creative.md` |
| Other non-brand image tasks such as illustration, concept visual, mood image, avatar, wallpaper, scene image, single creative poster, reference-image style transfer, outpainting, background change, local replacement, ordinary text-to-image or image-to-image | Do not read a product reference; follow the general generation/editing rules in this file |

## Brand Task Chain

Brand tasks first decide whether a logo or IP character is the core asset, then create derivative materials. Do not expand a single non-brand image into a brand system.

1. If later materials mainly inherit brand identity, wordmark, symbol, brand colors, or guidelines, first generate or confirm the logo core asset and read `references/brand-logo-system.md`.
2. If later materials mainly inherit a character, mascot, expression, pose, outfit, or character merchandise, first generate or confirm the IP core asset and read `references/brand-ip-character-system.md`.
3. If both logo and IP exist, follow the user's priority. If unspecified, packaging, brand applications, e-commerce, and formal brand communications use the logo as the main core asset and the IP as an auxiliary reference; emoji packs, stickers, character posters, and character merchandise use the IP as the main core asset and the logo as auxiliary reference.
4. After confirming the core asset, read packaging, brand-application, e-commerce, or media references for derivatives. Any derivative that must preserve consistency should use `image_edit` by default.
5. If the task does not involve brand assets, brand systems, or brand materials, stay in the general workflow and do not read brand references.

## Routing Conflicts

- If the user mentions e-commerce platforms such as Xianyu, Taobao, JD, Pinduoduo, Amazon, or an independent store, or asks for platform product-image parameters, main-image ratio, A+ pages, or detail-page screens, read `references/ecommerce-design.md`.
- If the user needs accurate knowledge structure, teaching logic, scientific structure, data relations, formula derivation, process steps, knowledge posters, textbook/courseware illustrations, or knowledge-graphic correction/redraw/optimization, read `references/knowledge-education-visual.md`. If the focus is platform click-through, social packaging, or general experience-sharing content without strict teaching accuracy, use `references/media-creative.md`. If the focus is product conversion, use `references/ecommerce-design.md`.
- Posters, banners, covers, and long graphics route to brand application when they emphasize a campaign brand system; to media when they emphasize a social platform, long social graphic, H5, or platform distribution; to e-commerce when they emphasize product conversion.
- For tasks such as "brand Xiaohongshu cover", "brand WeChat header", "brand campaign poster", "brand H5", or "brand banner": if the user provides or requests inheritance of a logo, brand color, key visual, packaging, IP, or brand system, use `brand-application-system.md` while borrowing platform ratio, information density, and reading context. If no brand asset is inherited and the core is platform communication, use `media-creative.md`.
- Packaging applications route to packaging when the packaging structure is central, to IP when character merchandise is central, and to brand application when the core is brand touchpoint extension.
- For multi-asset tasks such as "logo + packaging + poster", first confirm the logo or user-specified core asset, then extend to packaging and application materials.
- For "continue making a set based on this image", first identify whether the reference is a logo, IP, package, product, key visual, or social deliverable, then route.
- "Complete VI", "full brand case", or "brand manual" is not a single deliverable. If only this skill is available, clarify scope first rather than automatically expanding a single logo or package into a full case.

## Continuation Reference Rules

- When the user expresses continuation intent, prefer `image_edit`; do not default to redrawing with `image_gen`.
- Resolve references first. Put only the CDN URLs of images clearly indicated by the user or reliably inferred from recent turns and subject match into `image_reference_url_list`. Do not pass every image from the previous turn.
- If the referenced previous image is the subject, core asset, style anchor, or layout basis for the current task, use `image_edit` and pass that CDN URL.
- If the previous image only provides inspiration and subject/asset/layout consistency is not required, internally mark it as semantic-only reference and choose `image_gen` when appropriate.
- When multiple previous images may be referenced, rank by user deixis, recency, and subject match. If still uncertain, ask a brief confirmation.

## Clarification Rules

Completeness depends on three things: clear subject, clear usage/deliverable, and clear hard constraints. If two are present, act.

Reference files may define product-specific key inputs, but they cannot override the 1-3 question limit. Ask only when missing information changes the fundamental direction. If missing information can be reasonably inferred from category, platform, or context, decide internally and proceed. When the user says "you decide", "anything", or "just do it", stop asking.

Typical cases that need clarification:

- Very broad requests such as "generate an image", "make a poster", "design a logo", or "make a product image".
- Unclear edit boundaries that may accidentally change a person, product, logo, brand text, packaging structure, or composition.
- Values such as dates, prices, discounts, efficacy percentages, rankings, certification numbers, or regulatory statements that must be rendered but were not provided.
- Missing key inputs for e-commerce, packaging, logo, or IP tasks that would change the core direction.

Clarify at most once, with 1-3 questions. If the user says "you decide", use the default strategy in the relevant reference and keep the chosen defaults in the internal plan.

## Image Count Strategy

Priority: explicit user count, product-reference count strategy, then this default strategy. Image count must serve the user's intent; do not expand merely to look complete.

- Single edit, local change, background change, style change, outpainting, retouching, or ordinary single text-to-image: default 1 image.
- Multiple directions, concept comparison, or alternatives: default 2-3 images with clearly different directions.
- Series, sets, multi-platform, or multi-ratio adaptation: default 3-4 images separated by platform, ratio, usage, or material role.
- Complete schemes, systems, or full cases: plan and confirm count before generating.
- When logo, IP, packaging, brand application, e-commerce, or media references are matched, follow that reference's count strategy. Do not add the defaults from multiple references together.
- Without an explicit count, ordinary tasks should not default above 4 images. For media tasks such as multi-page posts, long social graphics, H5, or cross-platform distribution, plan more images based on content structure rather than a mechanical hard limit. If count conflicts with consistency, reduce count and preserve the core asset.

## Core Asset Rules

- Hard rule: once a current core asset exists as a CDN URL generated by `image_gen`, all derivative materials must explicitly reference that URL and use `image_edit` with `image_reference_url_list`. Never rely on text alone to regenerate a similar version with `image_gen`.
- There is no fallback where `image_edit` is considered unavailable: the host tool supports CDN URL parameters, so generated core assets can be used directly for extension.
- Consistency hard rule: in brand, e-commerce, IP, and narrative scenes, whenever the user asks to preserve a logo, IP, person, product, package, key visual, art style, character identity, or shot-to-shot continuity, call `image_edit` based on the current core asset CDN URL.
- User-uploaded logos, brand graphics, product photos, packaging, IP, characters, and key visuals are the current core asset by default unless the user explicitly says "style reference only".
- The first generated logo, IP, package, product main image, or key visual becomes the current core asset once it is used as the basis for later work.
- Maintain one primary core asset at a time. If multiple references exist, label their roles internally as `[img0]`, `[img1]`, and so on.
- Derivatives must preserve the recognizable traits of the core asset and must not drift into a redraw.

## Pre-Generation Check

Before calling an image tool, check:

1. Whether the task requires consistency and whether the core asset is locked.
2. Whether `image_gen` or `image_edit` is the correct tool. Consistency-preserving derivatives must use `image_edit`.
3. Whether the `image_edit` references are correct: `image_reference_url_list` includes the current core asset CDN URL, and the roles of `[img0]`, `[img1]` match the prompt.
4. Whether the prompt clearly states preserved elements, changed elements, target image, and user intent. Do not merely write "refer to the original" or "keep consistent".

## Prompt Rules

The final prompt is the only visual description sent to the image tool. It must be a coherent Chinese paragraph, without tagged fields or internal skill names.

- Text-to-image: complete the subject, scene or flat carrier, style, color, composition, material, text, and lighting.
- Image-to-image: restate the original less and describe the target more; specify the reference dimension, change dimension, and preserved dimension.
- For graphic-design tasks, do not describe irrelevant real-world backgrounds unless the deliverable is a mockup or spatial display.
- Pass `ratio` separately; do not write it into the prompt.
- Any visible text must be real renderable copy and wrapped in Chinese quotation marks.
- Do not use placeholder expressions such as `XX`, "something", "title copy", "TBD", "related description", "several words", or "placeholder".
- Prices, dates, discounts, sales volume, efficacy percentages, rankings, ratings, certification numbers, and regulatory claims may only come from the user or confirmed assets. Do not invent them.
- Do not directly use third-party brands, film/TV works, protected IP, or living artists as style anchors; translate them into generic style language.
- Avoid platform names and usage labels in final prompts, such as "Xiaohongshu cover", "Douyin style", or "WeChat header"; translate them into visual style, composition, and information density.
- Do not include internal planning/tool fields such as `tool_mode`, `asset_id`, `visible_text`, `image_reference_url_list`, `canvas:`, `ratio:`, or `reference image ID`.

## Complex Tasks

Give an execution plan and wait for user confirmation when any of the following is true:

- The task requires a set of related images.
- A core asset must be generated first and then used to generate other assets.
- The workflow switches between text-to-image and image-to-image.
- IP emoji packs, stickers, and expression-state images are IP consistency tasks even if only one image is output. If no `core-ip` exists, first generate or confirm the core IP, then use `image_edit` with the core IP CDN URL.
- Sets, series, multi-image output, or any task requiring consistent logo, IP, person, product, packaging, key visual, style, or character identity is a complex task.
- Multiple ratios, platforms, materials, or rounds of iteration are involved.
- The user explicitly requests a complete scheme, set, system, or full case.

The plan should state which references will be used, core asset order, the purpose of each image, and whether the user needs to provide critical text or values.

## External Information

Search external resources only when the user explicitly asks for latest information, real campaign information, external brand materials, or public platform specifications. Cite links when external sources are used. If the user has supplied reference images, do not replace image understanding with online image search.

## Post-Generation Check And Revision

Check internally before delivery.

1. Whether the image satisfies the user's core intent: subject, usage, style, ratio, text, platform, or deliverable type.
2. If `image_edit` was used, whether the right reference was used and whether the core asset identity was preserved without accidentally changing logo, IP, person, product, package, or key text.
3. For a series, whether all images share the same core asset, visual language, and necessary layout, color, and material anchors.
4. If the result deviates from intent or consistency requirements, identify the source: wrong reference image, unlocked core asset, insufficient preservation instructions, conflicting edits, wrong reference route, or wrong ratio.

Revision rules:

- Revise at most once.
- Fix only the key cause of deviation; do not open a new direction.
- If the result is still imperfect after one revision, deliver the best current result and briefly explain the limitation or what information is needed.

## Result Feedback

After generation, do not mechanically say only "done". If the result can be improved, offer 1-3 specific next directions, such as changing ratio, extending a series, improving text readability, or continuing from the current core asset.
