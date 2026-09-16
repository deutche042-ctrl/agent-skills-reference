# Brand IP Character System

## Main Skill Routing Fit

Use this reference for IP characters, mascots, character settings, turnarounds, character sheets, expression packs, stickers, outfit versions, character posters, merchandise, and logo-plus-IP combinations.

## Default Output Mode

IP work is a consistency task. First establish or confirm a core IP character, then create derivatives from that core asset. If no core IP exists, generate or confirm it before producing stickers, poses, merchandise, or scenes.

## Required Inputs

Key inputs include character type, brand/category, personality, target audience, visual style, mandatory or forbidden elements, and intended deliverables. If the user provides an image, decide whether it is the core IP, a style reference, or an edit target.

## Tool Adaptation

### Text-To-Image Tool

Use `image_gen` only for the initial core character or for a brand-new concept that does not need to match a reference. The prompt should define species/body type, silhouette, face, clothing, color palette, personality, and graphic style.

### Image-To-Image Tool / image_edit

Use `image_edit` for all derivatives that must preserve the character: turnarounds, pose changes, expression states, stickers, outfit variants, posters, packaging applications, and merchandise. Pass the core IP CDN URL as a reference.

### Ratio And Size Decisions

- Character sheet or full-body single character: 3:4 or 4:5.
- Sticker or emoji: 1:1.
- Poster or campaign visual: 3:4, 4:5, or 9:16 depending on platform.
- Turnaround sheet: wide ratio such as 16:9 when multiple views must fit.

### Calling Logic

1. If the user asks for a derivative and no core IP exists, first create or confirm the core IP.
2. If the user provides an IP image, treat it as the core IP unless stated otherwise.
3. Use `image_edit` for derivative creation.
4. Keep the derivative prompt specific: what pose/expression/object/scene changes, what identity features stay fixed.

### Hard Tool Routing Rules

- Do not recreate a similar character with `image_gen` after a core IP exists.
- Do not pass unrelated style references as core character references.
- Do not mix multiple character references unless the user explicitly asks for a group or fusion and the roles are clear.

### Core IP Anchor Gate

Before derivative generation, verify that the core IP has stable:

- Silhouette and body proportions.
- Face structure and expression language.
- Main colors and material cues.
- Clothing or accessory identifiers.
- Personality and age cues.

### Generation Order And Count Distribution

- Core IP only: 1 image.
- Multiple core directions: 2-3 distinct character concepts.
- Sticker or expression set: first core IP, then 3-6 expressions after confirmation unless the user specifies count.
- Turnaround: 1 sheet with front/side/back views or separate views when quality is more important than density.
- Merchandise or scene extension: generate 1-3 derivatives based on confirmed usage.

### Single Edit And Multi-Image Strategy

For a simple change such as "make it smile" or "change the outfit color", output 1 image. For a set, separate each image by expression, pose, scene, or use case. Consistency has priority over quantity.

### Intent And Ambiguity Strategy

If the user asks for "a cute mascot" without brand/category, infer a friendly commercial mascot and proceed unless brand name, text, or product linkage is required. Ask only when the missing element changes the character identity.

## Scope And Differences

IP character work is different from logo work: it emphasizes personality, pose, expression, and repeated use. It is different from ordinary illustration: the character must be reusable and identifiable across assets.

## Deliverable Knowledge Base

Common deliverables:

- Core character concept.
- Character setting card.
- Turnaround sheet.
- Expression pack.
- Sticker pack.
- Outfit or role variant.
- Character poster.
- Merchandise mockup.
- Character plus logo composition.

## Consistency Rules

Always preserve core identity: silhouette, face, proportions, color palette, clothing/accessories, species/type, and personality. Allow changes in pose, expression, props, environment, and composition only when they do not weaken recognition.

## Prompt Writing Rules

Describe the target image, not the internal plan. Do not mention tool fields. Avoid protected IP names or living-artist style anchors; translate them into generic visual language.

### Text Rendering Hard Constraints

Only include visible text when required. Use exact user-provided brand names or short labels. Do not invent slogans, dates, prices, or certifications.

### Text-To-Image Prompt

Include character type, silhouette, face, clothing, palette, material/rendering style, personality, pose, background, and intended carrier.

### Image-To-Image Prompt

State which reference character features to preserve and what to change. Example dimensions: "preserve the round head, teal scarf, small triangular ears, warm smile, and compact body; change only the pose into a waving sticker".

### Prompt Items

Useful dimensions include:

- Character anatomy and silhouette.
- Face, eyes, mouth, ears/hair/horns.
- Clothing and accessories.
- Color palette and material.
- Pose and expression.
- Prop and scene.
- Graphic style and edge treatment.

### Common Prompt Skeletons

Core mascot: create a full-body brand mascot with a clear silhouette, friendly expression, limited brand-color palette, simple clothing/accessory identifiers, flat commercial illustration style, clean background, high recognizability.

Sticker derivative: based on the reference mascot, keep identity features unchanged, create a single sticker pose with a clear emotion, simplified background, bold outline, clean edges, and no extra text unless provided.

Character poster: based on the reference mascot, keep identity features unchanged, place the character in a campaign scene with dynamic pose, brand-color visual system, clear composition, and readable focal hierarchy.

### Red-Line Check

Do not accidentally change the character species, face structure, main colors, signature accessory, or body proportions in derivatives. Do not overfill sticker images with complex backgrounds.

## QA

Check whether the derivative is recognizably the same character, whether the requested pose/expression/use case is fulfilled, whether text is valid, and whether the image ratio matches the deliverable.
