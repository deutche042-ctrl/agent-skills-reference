---
name: corporate-business-video
description: Generate specifications, confirmation summaries, 10-12 shot scripts, and video prompts for product-feature introductions, corporate videos, business videos, brand films, company-introduction videos, employer-brand videos, customer-case videos, service-introduction films, B2B ads, and company promos. The default final deliverable is one complete 15-second corporate video; longer requests should be compressed into a single coherent 15-second result unless the user explicitly asks for multiple videos, separate segments, or stitched long-video delivery. Public company information must be searched first when possible, and the user must complete company information, promotional copy, logo/IP/brand assets, and narration copy.
---

# Corporate Business Video

## Highest-Priority Hard Rules

Corporate and business videos cannot be generated from a one-line request. First complete public-information search, material completion, parameter summary, and user confirmation.

Fixed execution order:

```text
user brief -> search public information first -> summarize company materials -> ask the user to complete four required categories -> organize generation parameters -> explicit user confirmation -> storyboard and prompt -> call video tool or deliver generation package
```

A single generation is fixed at 15 seconds, and the default final deliverable is one complete 15-second corporate video. For 30s, 60s, or other longer requests, compress the narrative into a dense, coherent 15-second result instead of proactively splitting it into multiple videos. Multiple independent 15s videos or stitched long-video delivery are allowed only when the user explicitly asks for multiple videos, separate segments, or a multi-part corporate film, or explicitly chooses that option after you explain the single-video default. Independent 15s videos require separate confirmation by theme. Stitched long video uses `long_video_stitch_mode`: plan the whole narrative first, then split into 15s segments. Each segment still follows 15s duration, 10-12 shots, factual accuracy, complete narration `{specific lines}`, and company-material gates.

Every 15s corporate video must contain 10-12 shots. Default to 10 shots. The pacing is dense, with 0.8-1.5s per shot, but logo, IP, core information, narration, and CTA must remain clear.

Before explicit confirmation for the current task, only output search summaries, missing-material lists, confirmation summaries, or follow-up questions. Do not say the video has been generated, do not call tools, and do not inherit previous `OK/confirm` replies.

If no search tool is available, state that public search cannot be performed and ask the user to provide or paste company materials. Do not treat model memory, guesses, or industry common sense as searched facts.

## Four Required Information Categories

Before corporate promos, business films, investment videos, roadshows, brand films, conference openers, customer cases, or employer-brand videos, collect and confirm:

1. **Company information**: full company name, brand name, industry, main business, core products/services, founding time or development stage, region, target customers, strengths, public data, credentials/awards, official website or official-account links.
2. **Promotional copy**: company introduction, main slogan, brand proposition, business selling points, project/event theme, CTA, banned words, required phrases, and prohibited expressions.
3. **Brand assets**: logo source image, IP/mascot, brand colors, fonts, VI rules, product/space/team/factory/office/store/event materials, available customer logos, and case authorization scope.
4. **Speech/narration information**: corporate videos use complete narration by default. Collect language, voice, pace, tone, full narration or rewrite direction, subtitle strategy, and phrases that must remain exact. Cancel narration only when the user explicitly asks for no narration or pure music.

If any category is missing, ask for it or request uploads. You may draft suggestions from search results, but mark them as pending user confirmation.

## Search-First Rules

Whenever the user provides a company name, brand name, website, project name, product name, or event name, use available search tools first. Source priority:

- Official website, official news, official social accounts, official recruitment pages, official product pages.
- Authoritative media, business/regulatory disclosures, industry associations, exhibition/event websites.
- User-provided links, documents, and images.
- Other third-party content only as support, never as a substitute for official information.

After search, form a `source_summary`:

- `company_identity`: company/brand name, industry, business scope.
- `official_sources`: official sources used and key facts.
- `business_facts`: facts usable in video, separated as verified/user-provided/pending confirmation.
- `claim_risks`: unverifiable, exaggerated, credential/data/customer-authorization risks.
- `brand_assets_needed`: logo, IP, VI, and materials still needed.
- `narration_needed`: narration still requiring user confirmation.
- `people_visual_refs`: usable person images with source, identity, usage risk, and `ref_images` numbering.
- `knowledge_to_narration`: verified knowledge that can be converted to narration with sources.

Do not invent customers, awards, certifications, financing, listing status, revenue, market share, employee size, factory size, patents, or case data. Use neutral wording unless sourced or confirmed.

## User Confirmation Summary

After search and material completion, ask for confirmation before generation:

```text
Please confirm the following corporate video generation parameters:

Company information:
- Company/brand:
- Industry and main business:
- Core strengths:
- Verified facts:
- Facts pending confirmation:

Promotional copy:
- Main message:
- Core selling points:
- Must include:
- Must avoid:

Brand assets:
- Logo/IP/VI:
- Available image/video materials:
- Person reference images and sources:
- Materials that cannot be used or need authorization:

Speech/narration:
- Narration requirement: complete narration by default unless the user explicitly requests no narration or pure music
- Language/voice/pace/tone:
- Complete narration: every sentence as `{specific narration text}`; produce 3-8 directly voiceable lines, not only one slogan
- Source and fact mapping:
- Shot-by-shot narration allocation:
- Subtitle strategy:

Video parameters:
- Type:
- Target audience:
- Communication goal:
- Duration: one complete 15s final video by default; longer requests will be compressed into one 15s result unless the user explicitly chooses multiple videos or `long_video_stitch_mode`
- Multi-video / long-video planning, only if explicitly requested:
- Ratio/platform:
- Tone route:
- Reference style:
```

Only after the user explicitly confirms the current summary may you write the full storyboard, compile the video prompt, or call the video tool.

## Input Material Classification

Follow the main file's reference strategy: full storyboard charts are decomposed in order and not passed as whole-image references; on-screen people/IP are identified by `@image1/@image2...` with preservation anchors and anti-drift constraints.

- `company_ref`: website, company intro, annual report, prospectus, press release, business scope, milestones, team information.
- `brand_ref`: logo, VI, brand colors, fonts, brand voice, banned words, IP/mascot, brand manual.
- `copy_ref`: slogans, corporate copy, narration drafts, executive speeches, event themes, CTA.
- `knowledge_ref`: verified knowledge with `source_map`.
- `person_ref`: uploaded or searched people images for final `ref_images` when needed.
- `visual_ref`: office, factory, lab, store, campus, team, product, service process, event site.
- `case_ref`: customer case, pain point, solution, implementation, results, authorization scope.
- `platform_ref`: platform, ratio, screen size, subtitle rules, delivery format; duration still fixed at 15s.
- `style_ref`: reference video, moodboard, camera language, music, edit rhythm.

Conflict priority:

```text
current user confirmation > legal/compliance/brand bans > official sources > uploaded user materials > authoritative third party > ordinary search results > style reference
```

Style references only provide structure, rhythm, camera, lighting, and sound strategy. Do not copy another brand's slogan, logo, layout, customer case, person identity, or proprietary visual assets.

## Strategy Fields

Before storyboarding, decide:

- `business_objective`: trust building, investment, lead generation, recruiting, roadshow, conference opener, brand upgrade.
- `target_audience`: investors, government/park, enterprise customers, channel partners, candidates, employees, media, consumers.
- `communication_mainline`: one memory point, such as trust, expertise, innovation, scale, warmth, delivery efficiency, industry influence.
- `primary_message`: the one sentence viewers should remember.
- `secondary_message`: one supporting point.
- `avoid_message_drift`: what the video must not become.
- `tone_route`: selected tone route.
- `proof_chain`: visible evidence supporting the message.
- `voiceover_policy`: complete narration by default; record whether it must be verbatim or may be polished.
- `narrative_motif`: one motif such as problem-to-solution, capability-to-trust, technology-to-people, scene-to-value, present-to-future, case-to-result.
- `visual_world`: unified scene, light, color temperature, lens feel, brand colors, UI/graphic animation style.
- `audio_system`: BGM type, voice timbre, pace, sound-effect density, and mix priority.

## Narrative Motif And Realism

Corporate videos should not be a generic stock-footage montage. Choose one narrative motif and make every 2-3 shots advance the story: industry tension -> company identity -> capability evidence -> people/customer/use scenario -> value result -> brand closure.

Common motifs:

- Problem to solution: customer cases, services, B2B conversion.
- Capability to trust: corporate image, investment, business partnership.
- Technology to people: AI, SaaS, hardware, medical, education.
- Scene to value: product feature, service process, store/space/campus.
- Present to future: conference opener, brand upgrade, group image.
- Case to result: customer case, solution, roadshow proof.

Arrange at least two real business moments by default: one collaboration/service/customer communication moment, and one proof/delivery/process execution moment. Without real assets, create plausible business reenactments, not unrelated staged beauty shots.

## Tone Routes

Choose one main route and align shots, music, text, and narration:

| Route | Best For | Visual Language | Sound |
|---|---|---|---|
| Stable trust | Corporate image, finance, consulting, government cooperation, B2B services | Architecture, meeting rooms, teamwork, stable dolly, restrained composition | Controlled piano/strings, calm narration |
| Tech innovation | AI, SaaS, hardware, R&D, digitalization | Labs, UI abstraction, light scans, device macro, motion-graphic links | Minimal electronic, clear rational voice |
| Industrial strength | Manufacturing, supply chain, energy, logistics, engineering | Production lines, machines, inspection, materials, wide to macro | Low industrial rhythm, mechanical foley |
| Human warmth | Employer brand, service, medical/education, CSR | Real work, natural light, team interaction, medium people shots | Warm piano/guitar, sincere narration |
| Case proof | Customer case, solution, sales conversion | Pain-point scene, implementation, data/process abstraction, result state | Stable beat, concise explanation |
| Conference opener | Annual meeting, launch, summit, award, kickoff | City/campus, fast montage, stage lights, big titles | Cinematic build, drum lift |
| Premium brand | Design, architecture, high-end service, group brand | Slow reveal, material details, soft reflection, minimal text | Slow ambient music, few words |
| Social business short | LinkedIn, Douyin, Xiaohongshu, in-feed | 2s hook, proof point, brand anchor, large title | Stronger rhythm, short narration lines |

## 15-Second Structure And Rhythm

The default final video is generated as one 15-second video and must have 10-12 shots. Default 10 shots; use 11-12 for conference openers, social business shorts, investment conversion, tech innovation, and industrial-strength videos with higher density. Do not use fewer than 10 or more than 12.

Only when the user explicitly asks for stitched long-video delivery or explicitly chooses `long_video_stitch_mode`, each 15s segment is part of the whole film, not a self-contained ad. Plan global structure first. Non-final segments use connecting transitions, proof progression, or musical bridges; only the final segment carries full brand closure.

Generic 10-shot structure:

| Shot | Time | Goal |
|---|---:|---|
| 01 | 0.0-1.2s | Strong hook: industry pain, theme word, visual contrast, or core scene |
| 02 | 1.2-2.4s | First clear company/brand reveal, logo or spatial anchor |
| 03 | 2.4-3.8s | One-sentence visualization of business scope or service |
| 04 | 3.8-5.2s | Capability evidence 1: team, R&D, equipment, process, product |
| 05 | 5.2-6.6s | Capability evidence 2: service action, inspection, system, delivery site |
| 06 | 6.6-8.0s | People/customer/scenario interaction |
| 07 | 8.0-9.5s | Differentiated advantage or credible proof, no invented data |
| 08 | 9.5-11.0s | Audience benefit: efficiency, trust, growth, experience, partnership value |
| 09 | 11.0-13.0s | Brand proposition, event theme, investment/case/employer CTA setup |
| 10 | 13.0-15.0s | Stable logo/IP/company/CTA hold and music closure |

## Proof Chain Rules

Every claim needs visible proof. Pair abstract phrases with concrete shots:

- "Professional" -> specialists working, process, tools, QA.
- "Efficient" -> clear workflow, system interface, delivery rhythm.
- "Reliable" -> customer interaction, certification only if sourced, stable operations.
- "Innovative" -> R&D, prototype, UI/data visualization, but no empty sci-fi effects.

## Shots And Editing

Use stable, plausible camera moves. Mix wide, medium, detail, and UI/graphic shots. Avoid unrelated stock city shots unless they establish the business context. Maintain consistent lighting and visual world.

## Subtitles, Speech, And Symbols

Complete narration is default. Use concise on-screen titles only when necessary; do not replace narration with a slogan. Do not invent data, awards, client names, or certification badges.

## Sound System And Narration

Narration must be direct, credible, and fact-safe. BGM supports tone route and should not drown voice. Corporate narration should be 3-8 sentences for 15s, allocated across shots.

## Storyboard Fields

Use fields such as: shot number, time, visual, camera, business meaning, narration `{specific line}` or no narration reason, on-screen text if any, sound/BGM, reference asset, and fact/source note.

## Video Prompt Template

Compile into a time-based director prompt with reference roles, visual world, shot-by-shot descriptions, narration in `{}`, audio, constraints, and brand-asset preservation. Do not paste raw tables or unconfirmed claims into the video tool.

## Long-Video Stitch Delivery

Use this mode only when the user explicitly asks for stitched long videos or explicitly chooses multi-part delivery after you explain the single-video default. For stitched long videos, deliver whole-film outline, segment responsibilities, continuity rules, per-segment storyboard, per-segment prompt, and final segment closure logic.

## Tool Calls And Display

Follow the main file's confirmation and `notify_hunman` display requirements. Do not call the video tool before confirmation.

## Quality Check

Check facts, claim risks, brand asset preservation, narration completeness, shot count, 15s timing, visual consistency, audience fit, and whether the video avoids generic empty corporate slogans.
