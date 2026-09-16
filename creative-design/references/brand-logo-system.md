# Logo System

## Main Skill Routing Fit

Use this reference when the user asks for a logo, symbol mark, wordmark, lockup, logo upgrade, monochrome version, small-size icon, favicon, or logo guideline page.

## Overview

Logo work must produce a recognizable core identity asset, not a decorative poster. The first approved or generated logo becomes the core asset for later brand materials. Any later derivative that must preserve the logo should use `image_edit` with the core logo reference.

## Use Cases

- New logo concepts for a brand, product, event, shop, creator, or project.
- Logo refreshes that preserve existing recognition.
- Symbol, wordmark, or symbol-plus-wordmark combinations.
- Horizontal, vertical, monochrome, reverse, small-size, and favicon versions.
- Guideline-page visuals showing safe space, color, typography, and usage examples.

## Core Workflow

1. Clarify or infer brand name, category, tone, and required visible text.
2. Decide whether the requested output is a main logo, a variant, or a guideline page.
3. If an existing logo is provided, treat it as the core asset unless the user says it is only inspiration.
4. For first concepts, use `image_gen`. For upgrades or variants based on a supplied/generated logo, use `image_edit`.
5. Keep the final prompt focused on flat logo design; avoid unnecessary scenes, mockups, and background decoration unless specifically requested.

## Image Count Strategy

- Single logo or strict edit: 1 image.
- Multiple concept directions: 2-3 images with distinct construction logic.
- Logo plus variant sheet or guideline page: 1 main logo first, then derivative pages after confirmation.
- Do not generate a full VI system unless the user explicitly asks for one and confirms scope.

## Core Main Version

The main version should establish:

- Brand name or initials.
- Mark type: symbol, wordmark, monogram, emblem, mascot-like mark, or lockup.
- Category cues that do not become literal clutter.
- A limited color system that can work in monochrome.
- Clear geometry and legibility at small size.

## Consistency And Diversity

Concept alternatives may vary by metaphor, geometry, type personality, and color mood. They should not vary by inventing different brand names or changing user-provided text.

Variants must preserve the same core geometry, proportions, and recognition features. Only orientation, color mode, scale, and layout may change unless the user asks for a redesign.

## Logo Main Image Boundaries

For the main logo image:

- Prefer a clean, flat, centered presentation.
- Use a simple neutral background unless the user requests a mockup.
- Do not include business cards, storefronts, product packaging, or posters in the first logo concept unless explicitly asked.
- Do not create excessive gradients, shadows, 3D effects, or tiny decorative details that harm small-size use.
- Avoid fake guideline labels, lorem ipsum, and unreadable microtext.

## Guideline Page Text Gate

Guideline pages may include only concise, renderable labels such as:

- "Logo"
- "Clear Space"
- "Primary Color"
- "Monochrome"
- "Minimum Size"
- "Do Not Stretch"

Do not invent legal claims, registration marks, dates, Pantone codes, or brand slogans unless provided. If exact color values are required but not given, use visual swatches rather than fake numeric specifications.

## Prompt Strategy

For text-to-image logo generation, include:

- Brand name exactly as provided.
- Industry/category and audience.
- Mark type and visual metaphor.
- Typography direction.
- Color mood.
- Flat vector-like design, simple geometry, high legibility, scalable identity.

For image-to-image logo editing, include:

- What must be preserved from the reference.
- What should be improved or changed.
- Whether text, symbol, proportions, color, or style should remain stable.
- A clear instruction to keep the logo flat and usable.

## Input

Important inputs include brand name, category, target audience, tone, mandatory symbols or forbidden motifs, color preferences, and whether Chinese/English text must appear.

Ask only when missing information changes the identity direction. If the brand name is missing, ask; a logo cannot be reliably generated without it unless the user requests an abstract placeholder-free symbol.

## Output Forms

- Main logo concept.
- Logo direction comparison.
- Logo refresh.
- Horizontal/vertical lockup.
- Monochrome/reverse version.
- Favicon or app-icon simplification.
- Logo guideline page.

## Tools And Scripts

Use `image_gen` for new concepts without a reference. Use `image_edit` for upgrades, variants, guideline pages based on a confirmed logo, or any derivative requiring logo consistency.
