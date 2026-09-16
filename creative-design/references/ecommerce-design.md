# E-Commerce Main Image And Detail Page Design Generator

## Main Skill Routing Fit

Use this reference for e-commerce main images, listing images, product detail pages, A+ pages, shop headers, promotion images, selling-point images, comparison images, livestream backgrounds, product hero images, and platform product imagery for Taobao, JD, Pinduoduo, Amazon, Xianyu, and independent stores.

## Overview

E-commerce images serve conversion. They must show the product clearly, communicate selling points quickly, respect platform expectations, and avoid unsupported claims. If a product image or package is provided, treat it as the core asset and use `image_edit` for derivatives.

## Use Cases

- Main product image and click-through image.
- Selling-point secondary image.
- Detail-page screen.
- A+ module or Amazon detail image.
- Promotion poster or sale image.
- Comparison diagram.
- Livestream room background.
- Product scene rendering or hero visual.

## Input

Important inputs:

- Product name/category.
- Product photo or packaging reference.
- Platform.
- Target image type.
- Selling points and required visible text.
- Price, discount, event date, rating, certification, or ranking if they must appear.
- Brand assets and SKU variants.

Ask when product/category or platform/output type is unclear enough to change the design. Never invent prices, discounts, rankings, certification, efficacy percentages, or compliance claims.

## Core Workflow

1. Identify platform and carrier type: main image, secondary image, detail-page screen, A+ module, promotion poster, comparison image, or livestream background.
2. Lock product/package/brand as the core asset when provided.
3. Decide ratio and information density from platform and carrier.
4. Extract or infer a conversion hierarchy: product first, key benefit second, trust or usage context third.
5. Use `image_gen` only when creating a new product-like concept without a reference. Use `image_edit` when a product, package, logo, or prior image must remain consistent.
6. Write prompt with concrete scene, product placement, copy, layout, lighting, material, and commercial polish.

#### Layer 1: Structural Skeleton By Carrier

- Main image: product hero, clean background, strong click-through, minimal text.
- Selling-point image: product plus 1-3 benefit blocks.
- Detail page screen: one theme per screen, modular layout, high readability.
- A+ module: brand/product story, feature visualization, lifestyle usage, comparison, or specification module.
- Promotion poster: offer hierarchy, product hero, event mood, but only with supplied offer details.

#### Layer 2: Scene Semantics

Infer the product usage scenario, buyer concern, category trust signal, and sensory cues. For example, beauty emphasizes texture and efficacy feel; electronics emphasizes structure, precision, and feature visualization; food emphasizes freshness and appetite appeal.

#### Layer 3: Instance Filling

Fill with concrete product angle, background, props, benefit icons, text blocks, comparison elements, and lighting. Keep every visible text item intentional and short.

## Tools And Scripts

Use `image_edit` for uploaded product photos, packaging, logos, and generated product cores. Use `image_gen` for clean conceptual product visuals only when no consistency is required.

## Output Forms

Default ratios:

- Taobao/JD/Pinduoduo main image: 1:1.
- Secondary selling-point image: 1:1 or 4:5.
- Domestic detail-page screen: 3:4, 4:5, or 9:16 per screen; do not generate one huge waterfall page.
- Amazon main image: 1:1, product on clean white background, no excessive text or props.
- Amazon A+ module: 16:9, 3:2, or platform-suitable module ratio.
- Livestream background: 16:9 or 9:16 depending on room format.

## Reference Tables

### Table 1: Image Physical Structure And Zones

#### 1. Main Image Series

Prioritize click-through. Use a large product hero, clear silhouette, minimal background, and a single dominant message. Keep text low unless the platform/category allows it.

#### 2. Domestic Detail Page Series

Generate one screen at a time. Never directly generate an unreadable waterfall long page. Select screens intelligently and alternate layouts: hero benefit, feature breakdown, usage scenario, comparison, specification, packaging/service.

#### 3. Amazon Detail / A+ Series

Use information-oriented secondary images and A+ modules. Avoid aggressive sale graphics. Emphasize feature clarity, product credibility, lifestyle use, and comparison.

#### 4. Promotion / Marketing Poster Series

Use campaign atmosphere and offer hierarchy only when details are supplied. Do not invent sale dates, prices, discount percentages, or platform badges.

### Table 2: Platform And Category Visual Attributes

- Domestic marketplace: stronger visual impact, denser selling-point text, category-specific conversion cues.
- Amazon: cleaner, more standardized, product credibility and clarity.
- Xianyu: more authentic, second-hand or individual-seller feel when relevant, but still clear and trustworthy.
- Independent store: brand-oriented, cleaner landing-page style.

### Table 3: E-Commerce Typography And Information Density

Use short benefit phrases, clear hierarchy, and readable blocks. Avoid tiny fake paragraphs. Put only user-provided or safe category terms into visible text.

### Table 4: Abstract-Term Translation Rules

Translate vague terms into visual specifics:

- Premium: restrained palette, refined material, precise layout.
- Tech: clean structure, cool lighting, feature callouts, modular graphics.
- Fresh: bright light, clean color, water/leaf/ingredient cues when suitable.
- Cost-effective: clear comparison, value hierarchy, but no fake prices.

### Table 5: T2I Design Scheme Rules

For text-to-image, define product appearance, category, scene, layout, copy, lighting, and commercial style. Avoid implying a real trademarked product unless provided.

### Table 6: I2I Design Scheme Rules

For image-to-image, explicitly preserve product shape, color, logo, packaging, label, and recognizable details. Change only the scene, layout, background, callouts, or promotional wrapper required by the task.
