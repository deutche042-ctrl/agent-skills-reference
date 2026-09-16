# All-Platform Marketing Image And Copy Generator

## Main Skill Routing Fit

Use this reference for Bilibili, Douyin, Kuaishou, WeChat Moments, WeChat Official Account, Xiaohongshu, seeding posts, OOTD, store visits, H5 pages, interactive long pages, video covers, multi-platform social images, long social graphics, long article graphics, horizontal focus banners, promotional posters, and platform communication visuals.

## Overview

Media creative work optimizes for platform reading context, attention capture, shareability, and fast comprehension. It is not automatically a brand-system task unless the user provides or requests brand-asset inheritance.

## Use Cases

- Social platform cover.
- Video thumbnail.
- Xiaohongshu-style note cover or carousel.
- WeChat Official Account header or long image.
- Douyin/Kuaishou vertical poster or cover.
- Bilibili video cover.
- H5 mobile long page.
- Cross-platform campaign assets.
- Promotional poster focused on communication rather than e-commerce conversion.

## Input

Useful inputs include platform, topic, audience, content angle, required copy, brand assets, reference image, desired ratio, and number of pages/images.

Ask only when platform or topic is too unclear to decide format and hierarchy.

## Core Workflow

1. Identify platform and deliverable type.
2. Determine whether the task is platform communication, brand application, e-commerce conversion, or knowledge teaching. Route away if necessary.
3. Lock any provided brand/logo/IP/product/key visual as a core asset when consistency matters.
4. Decide ratio, information density, headline style, and visual hook from platform context.
5. Use `image_gen` for new standalone visuals and `image_edit` for reference-based or asset-consistent derivatives.
6. Keep platform names out of the final prompt; translate them into composition, density, and visual conventions.

## Tool And Script Calls

Use actual host image tools. Use `image_edit` whenever a supplied or previously generated visual must remain recognizable.

## Reference Tables

### Table 1: Platform Visual Traits And Track Focus

#### 1. Bilibili - Default 16:9

Strong title readability, high contrast, clear subject, video-thumbnail logic, expressive composition, and immediate topic recognition.

#### 2. Douyin - Default 9:16

Vertical-first, strong central subject, fast emotional hook, short headline, high mobile readability, and dynamic composition.

#### 3. Kuaishou - Default 9:16

Direct, authentic, high-contrast, human/product/story focused, with simple readable copy.

#### 4. WeChat Moments - Default 1:1 Or 3:4

Social-feed friendly, polished but not overloaded, clear mood and shareable message.

#### 5. WeChat Official Account - Default 16:9 Header Or Long Image

Editorial hierarchy, refined title area, topic clarity, and article-like visual structure.

#### 6. Xiaohongshu - Default 3:4

Lifestyle-oriented, topic-first, strong cover hook, readable title, clean but attractive composition, suitable for notes or seeding content.

#### 7. Cross-Platform Horizontal Banner - Default 2.35:1 Or Wider

Wide focus composition, concise text, brand or topic anchor, and safe margins.

#### 8. Cross-Platform Vertical Poster - Default 3:4 Or 9:16

Clear top-to-bottom hierarchy, strong hero subject, and mobile readability.

#### 9. H5 Page - Default 9:16 With Optional Extended Length

Mobile-first long-page structure, modular sections, interactive-feeling visual rhythm, and clear narrative sequence.

### Table 2: Reference Image Reasoning And Aesthetic Upgrade Rules

#### 1. Basic Reference Inference

Identify what the reference provides: subject, composition, color mood, texture, typography, layout, style, or asset identity. Use only the necessary dimensions.

#### 2. Advanced Aesthetic Upgrade Items

Improve through stronger focal hierarchy, better spacing, more precise color contrast, richer material cues, cleaner typography, and platform-suitable cropping.

### Table 3: T2I Design Scheme Rules

For text-to-image, define topic, subject, visual hook, headline area, supporting copy, platform-like density, color, composition, and image style.

### Table 4: I2I Design Scheme Rules

For image-to-image, preserve reference subject/asset/layout as required and change only style, crop, hierarchy, background, or platform adaptation.

### Table 5: Platform Visible Copy Requirements

Use short, real, readable copy. Headlines should be concise. Do not use placeholder copy. Do not invent dates, prices, rankings, or claims.

### Table 6: Platform Hard Red Lines And Taboos

Do not include fake platform UI, fake verification badges, misleading endorsements, invented discounts, unsupported medical/financial claims, or protected IP style anchors. Avoid unreadable microtext and overcrowded long paragraphs.
