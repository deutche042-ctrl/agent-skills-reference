---
name: ugc-talking-video-ref
description: >-
  WHAT: From a main-file brief, ref files, product photos, person/scene references, generate natural, realistic UGC talking-head short videos with strong product consistency and non-repetitive creator faces in batch workflows. Output high-quality prompts ready for a video model, a complete storyboard table, and the generated video.
  USE WHEN: The user wants talking-head videos, seeding/review/unboxing/tutorial/demo videos, real-person or digital-human speech, batch short videos, product ad shorts, storyboard tables, video prompts, first-frame-to-video, or reference-video replication, even if they do not say "UGC" or name a tool. Covers Douyin, Xiaohongshu, WeChat Channels, in-feed ads, and similar scenarios.
  DO NOT USE WHEN: The user only wants titles, pure copy, static posters/images, or editing/splicing existing videos without new video generation.
---

# Main File Reference Notes

This file is the UGC talking-head strategy reference for `creative-video`. Read it after the main file routes to UGC. Do not use it as an independent entry point that overrides the main file's generation gates.

The main file first classifies references as `product_ref/script_ref/creator_ref/scene_ref/style_ref/audio_ref/platform_ref`, then this UGC strategy applies.

## Reference Input Adaptation

`ref` is only an input wrapper. It does not change the UGC strategy. After the main file completes clarification/confirmation and product-upload gate, this reference outputs a lightweight storyboard first and then follows UGC talking-head logic. Do not add a second confirmation round and do not bypass the main confirmation.

Follow the main file's reference and storyboard strategy: full storyboard charts are decomposed, not passed as whole-image references; on-screen IP/people are identified by `@image1/@image2...` with preservation anchors and anti-drift constraints.

- `product_ref`: product photos, packaging, SKUs, detail pages, ingredients/specs/selling points. Product images enter `ref_images`; text selling points enter `Product name`, `Selling points`, and `product_lock`. Product consistency has top priority.
- `script_ref`: speech scripts, review scripts, livestream wording, user comments, creator notes. If complete speech exists, use it as a `Monologue` draft and compress to target duration by `speech_pace`. If only points exist, rewrite into natural recommendation speech. The rewritten speech must appear in the confirmation summary and final prompt as `{specific script}`; never turn it into subtitles, captions, or screen copy.
- `creator_ref`: person image, persona, makeup/hair/clothing, fixed host materials. Person images enter `ref_images` and lock identity/clothes/makeup/hair. With a fixed person, do not randomize creator face unless the user asks for batch variation.
- `scene_ref`: room, store, kitchen, bathroom, desk, outdoor space. Lock materials, light, and arrangement only; do not let the scene overpower the product.
- `style_ref`: reference video, style image, competitor content, moodboard. Extract handheld feel, cut rhythm, lighting, tone, and mood only; do not copy brands, subtitles, slogans, or proprietary shots.
- `audio_ref`: voice, BGM, pace, mood. Affects `voice_tone`, `Audio`, BGM, and foley direction only. It must not become sentence-by-sentence captions.
- `platform_ref`: platform, ratio, duration, placement limits. Overrides matching parameters only. Default remains 15s, 9:16 when unspecified.

Conflict priority: current user instruction > product image/facts > `script_ref` facts > `platform_ref` limits > `creator_ref` > `scene_ref` > `style_ref` > `audio_ref`. Never let a style ref alter product packaging, a person ref override the product subject, or a reference video copy another brand's subtitles/assets.

# UGC Talking Video

Turn a brief into a UGC talking-head video that feels casually shot by a real person. Goals: realistic host, no obvious AI feel, strict product match, detailed prompt, executable storyboard.

```text
brief -> product lock -> randomized creator profile blueprint -> multi-selling-point script -> lightweight storyboard table (hard gate) -> Seedance prompt -> video tool -> notify_hunman display -> success summary
```

## Output Contract

- For the video model: `prompt`. If images exist, also pass `ref_images` and state roles such as `@image1/@product_ref` in the prompt. Compile text/video/audio references into prompt material notes first. `ratio/duration` follow user confirmation or defaults.
- For the user: complete/lightweight storyboard table plus the generated video. After the tool returns a usable link/path, call `notify_hunman` as required by the main file, then output the success summary.
- Do not show internal prompt/YAML by default; show it only when the user asks for debugging, handoff package, or prompt view.
- If the user explicitly asks, support first generating storyboard images/first-frame images, then video.
- Hard gate: before any video tool call, output a storyboard table in the user-visible response. Without storyboard, do not call `text_to_video` or `image_to_video`.
- Minimum visible blocks: style/tone, creator setting, product lock, lightweight storyboard, video link/generation status.

## Default Strategy

- Do not generate immediately. Follow the main `SKILL.md` clarification and confirmation rules.
- Default parameters after main confirmation: 9:16 vertical, 15s talking-head duration unless the user specifies otherwise.
- After confirmation, output storyboard first, then call the video tool. Do not fake links if the tool returns none.
- Subtitle hard gate: final UGC video prompts must not generate sentence-by-sentence subtitles, auto captions, bilingual subtitle boxes, lower thirds, or transcript text. `subtitle_policy` is fixed to off. Even if the user asks for subtitles, record them as post-production needs, not video-generation prompt content.
- Emphasis text is off by default. Allow a few stickers/large words only when the user explicitly asks or in strong conversion scenarios. Use at most 1 emphasis item for ordinary 15s videos and 2 for dense commerce videos; each 2-6 Chinese characters; specify content, position, timing, and animation. Do not repeat the speech or cover logos, package info, eyes, or proof actions.
- Speech in final prompt uses `{specific script}` only inside audio/voice/lip-sync fields. Emphasis text uses quoted text and is separate.
- Rhythm principle: density comes from useful information per sentence, not uniform fast reading. Realism comes from stress, breath, and fillers, not dragging the whole pace.
- `speech_pace`: Chinese about 5-6 characters/second, 75-90 characters for 15s; high-density commerce may be 90-105 if articulation remains clear. English uses natural fast but clear speech.
- `language_lock`: speech, Monologue, and Audio must match the user's brief language. Do not mix languages or translate English requests into Chinese speech.
- Internally define `reference_asset_roles`: product images lock package/logo/SKU and cannot be replaced by AI; person images lock identity/clothing/makeup/hair; scene images lock space/light; style images affect tone only.

## Standout Target

`wow_target` applies before anti-failure constraints. The target is a scroll-stopping short video, not merely passable. Include at least one high-impact moment: strong first-frame hook, extreme product texture macro, dramatic real reaction, before/after moment, or memorable camera switch. Bold composition and cinematic light are allowed only if product/logo/package/SKU consistency and realism are preserved.

Define `excellent_target` as one scoring sentence: what makes this video strong. Every video should include `pattern_interrupt_hook`, `proof_moment`, `creator_trust_moment`, `visual_payoff`, and `cta_moment`.

## Product Consistency Top Priority

When the user provides original product images, they are the highest-priority references. A beautiful generated result with inaccurate product should be discarded.

The first paragraph of the prompt must state:

```text
Use @image1 as the only product reference. Strictly preserve product count, bottle/box shape, size ratio, color, material texture, reflections, transparency, surface texture, cap/pump/body structure, logo/brand mark position, label shape, main text layout, SKU, and packaging details. Do not redraw the package, change colors, create a new logo, new label, or fake text.
```

Repeat product locking in every product shot:

- Product position, orientation, frame share, and whether logo faces camera.
- Which hand touches the product and how; fingers must not block logo/label/key claims.
- Product appears clearly at least three times: opening 0-2s, proof close-up, final hold.
- Real product, brand package, SKU, and store signs should not be AI-redrawn by default.
- If the reference is unclear or contains multiple SKUs, state the default locked product in the confirmation summary.
- For batch/multi-turn generation, repeat full `product_lock` in every prompt and always use the original user product image as the only reference.
- Keep product scale constant across shots with palm/face/table anchors.
- Match reflections/shadows to `light_direction`; avoid sticker-like products or impossible hand contact.

## Creator Face Blueprint: Template Anchor + Random Secondary Dimensions

Unless the user provides a fixed person, each video draws one structural template and randomizes gender, skin tone, hair, age, styling, and outfit. For batch generation, avoid repeated faces.

Templates:

| Template | Face/Eyes/Bone Structure | Nose/Nasolabial | Temperament | Best For |
|---|---|---|---|---|
| T1 Cool Premium | Oval face, upturned narrow eyes, restrained cheekbones | Straight high nose, nearly no nasolabial lines | Female: refined distant; Male: clean intellectual restraint | Luxury, high fashion |
| T2 Sweet Neighbor | Round face, round eyes, low soft cheekbones | Small rounded nose, very light nasolabial lines | Female: sweet approachable; Male: sunny boy-next-door | Daily care, campus, lifestyle |
| T3 Mature Strong | Square face, peach-blossom eyes, high cheekbones | Tall sharp nose, natural light nasolabial lines | Female: powerful; Male: mature business | Workplace, premium beauty, business |
| T4 Neutral Salt | Long face, monolid, slightly protruding flat cheekbones | Straight nose with rounded tip, light nasolabial lines | Female: androgynous youthful; Male: slim artistic salt style | Streetwear, Japanese magazine, indie design |
| T5 Sculpted Global | Dimensional face, deep-set eyes, high cheekbones | Strong high nose, natural light nasolabial lines | Female: intense global look; Male: rugged sculpted | International ads, beauty, travel |

Rules:

- Single video: draw one template and ensure `persona_product_fit`.
- English brief/speech with no race/person reference defaults to an attractive upscale Caucasian creator with realistic UGC styling, not cheap influencer exaggeration.
- Batch <=5: use different templates. Batch >5: when templates repeat, change all secondary dimensions and check `used_creator_profiles`.
- New creators must not share more than three major traits with previous creators: template, skin tone, hair color, age, makeup, top color.
- Male creators require explicit face/bone/nose differences to avoid same-face "standard handsome" repetition.
- Tops must use a positive palette and be written exactly: misty blue, brick red, ink green, burgundy, gray purple, denim blue, charcoal black, olive green, navy blue, coral pink, mint green. Hair must be chosen explicitly from real options.
- Do not use facial moles, piercings, or obvious marks to distinguish people.

For each video write:

```text
creator_identity_seed: batch{batch}-video{index}-{template}-{skin tone}-{hair}-{age}-{makeup}-{top color/material}
identity_anchor: template structure + gender aesthetic branch + hair + palette top + scene outfit, repeated verbatim in every segment.
anti_same_face_line: This creator uses a distinct facial-structure template, not the reused default digital human with changed clothes.
```

## On-Camera Appeal + Real Skin

Define `appeal_baseline`: a high-quality ordinary creator suited to short-video aesthetics, with clean attractive features, healthy complexion, lively eyes, clean approachability, and realistic but camera-ready appearance. Avoid tired, aged, rough, ID-photo-like faces. Beauty/skincare creators should have good skin and refined clean features.

`body_baseline`: balanced, healthy, toned body; natural fullness in face/neck without puffiness; no chubby cheeks, double chin, bulky neck/arms, or overly thin gaunt look.

Realism requirements:

- Low oil shine; natural tiny highlights only.
- Real eyebrow hair, hairline baby hairs, natural lashes, layered hair strands and root shadows.
- Subtle skin texture, natural color transitions, slight facial asymmetry, good but not plastic-smoothed skin.
- Natural blinking whenever a person appears; no dead-eyed staring, winking, or flirtatious one-eye gestures.

## Multiple Selling Points + Recommendation Tone

Do not rely on one slogan. Focus one core selling point plus 2-3 supporting points. Use only user-provided facts; when missing, use conservative experience language.

`recommendation_score`: a 15s video must cover four recommendation nodes: why it is needed now, why the product works/is useful, specific user feeling after trying it, and who should act/how. Every sentence needs useful information or experience judgment.

Selling-point stack:

- Pain point/scenario.
- Core benefit + visible proof action + provided ingredient/technology/structure fact.
- Use feeling + concrete evidence: immediate feel, convenience, comfort, efficiency, before/after if provided.
- Audience/scenario fit + soft CTA.

Recommendation tone:

- 0-2s must hook: pain, contrast, suspense, or concrete number.
- Use first-person experience for trust.
- Rotate hook strategies in batch work.
- Natural conversational short sentences; avoid manual-like, broadcast, or exaggerated hard-sell tone.
- Soft CTA: save, check link, suitable people can try.
- Voice tone matches template, category, and platform.
- Avoid AI-ish internet slang, exaggerated fandom catchphrases, and formulaic hard-sell expressions.

Platform tone:

- Douyin: strong 2s hook, result-first, faster, more direct.
- Xiaohongshu: real experience, detail proof, lifestyle recommendation, friend-like tone.
- WeChat Channels: credible, stable, family/acquaintance context, slightly slower.
- In-feed ads: clear pain point, direct benefit, clean CTA.

## Second-By-Second Storyboard Cards

Design a user-facing storyboard table before compiling the video prompt. Each card must be complete; do not write "same as above".

`Shooting Script Gate`: before video prompt generation, output a shooting script. Fields: `time | speech | visual/action | movement/micro-expression | product proof | high-score purpose`. Mark whether each part serves hook, product proof, trust, visual payoff, or CTA.

Default lightweight storyboard table:

```text
Time | Visual action | Voice/lip sync | Emphasis text/sticker | Product preservation
```

If no emphasis text, write "none". Expand to detailed fields only when requested.

Default 15s high-score structure uses up to 4 real cuts:

- Cut 1, 0-3s: pattern-interrupt hook.
- Cut 2, 3-7s: product proof, macro, or trial.
- Cut 3, 7-12s: experience feedback, before/after, or real reaction.
- Cut 4, 12-15s: creator recommendation and soft CTA; product appears clearly and final second holds.

Each segment has one main action and information gain.

## Rewrite Base Template

The final video prompt should use a labeled director format, not a loose mood paragraph:

```text
`@image1/@product_ref` product reference role: strictly preserve product appearance, shape, size ratio, color, packaging, logo/SKU, and visible material; do not redraw the product.
【Style & Tone】platform feel, shooting feel, light, color, realism target, anti-AI direction.
【Creator Setting】gender, age, face/features, makeup/hair/clothes, realistic ordinary creator feel, creator_identity_seed.
【Shots & Actions】write each time segment with camera, action, expression, product proof, and movement.
【Sound/Lip Sync】complete readable voice only for dubbing and lip sync: `{specific script}`; no subtitles, captions, or screen transcript.
【Speech Style】pace, tone, voice, natural fillers, BGM-to-voice relationship.
【Scene】space, light source, background, props, product placement, continuity.
【Emphasis Text】default "none"; if allowed, write short words, position, timing, and animation.
```

## Prompt Compilation

Compile storyboard cards into a natural-language timeline:

```text
reference material notes -> global goal/wow_target -> shot 1/shot 2/shot 3... -> visual quality style -> constraints
```

Rules:

- First write: `VISUAL TEXT POLICY: preserve only the real product logo/label from the reference image; no subtitles, no auto captions, no lower-third, no transcript-style text, no watermark; emphasis text only if explicitly confirmed`.
- Include `reference_asset_roles`, `product_lock`, `creator_identity_seed`, `template_anchor`, `identity_anchor`, `anti_same_face_line`, `style_block`, `wow_target`, `excellent_target`, and `recommendation_score`.
- Include `appeal_baseline`, `persona_product_fit`, `platform_tone`, `voice_tone`, `hook_strategy`, and `key_selling_points`.
- Final prompt must use block names: `Monologue`, `Selling points`, `Product name`, `Creator description`, `Shots description`, `Style & Mood`, `Narrative Summary`, `Dynamic Description`, `Static Description`, `Audio`, `Constraints`.
- Complete speech in `Monologue`, `audio_voiceover`, or `Audio` must use `{specific script}` and obey `language_lock`.
- `Dynamic Description` describes speaking, lip sync, expressions, and actions, but does not repeat the complete script. Full script appears only in audio fields.
- Every shot must be independent and repeat identity/product anchors where relevant.
- `scene_continuity`: same space, same light source, same time period. Cuts do not mean new scenes.
- Use real cuts, not only push/pull zoom. 3-4 segments, no more than 4, each at least 3s. Cuts should land on action, gaze, or product movement; speech audio remains continuous.
- Plan proof by category: drinks pour/drink/react; food take/bite/chew/react; fresh goods hold/cut/texture macro; skincare take/apply/massage/absorb/show texture; beauty/daily-care press/apply/use.

## Realism And Anti-Failure Constraints

Avoid AI-looking skin, stiff gaze, frozen mouth, wrong lip sync, extra fingers, impossible hand-product contact, floating products, packaging drift, fake logos, random subtitles, watermarks, over-smoothing, face swapping, same-face batch creators, and scene discontinuity.

## Tool Calls

Follow the main file's confirmation and display rules. Do not call video tools before storyboard is visible and current task parameters are confirmed.

## Success Format For User

Show the storyboard and the generated video status/display. Keep the final summary brief: what was generated, duration/ratio, product reference used, and any limitation if display failed.

## Internal QA

Check product accuracy, script length, speech clarity, no subtitles, creator uniqueness, skin realism, shot continuity, product proof, platform tone, CTA, and whether every shot has explicit voice/sound information.
