---
name: creative-video
description: Use when the user needs general video generation, video creation, video prompt planning, or text/image-to-video, including creative videos, product ads, UGC talking-head/sales/in-feed videos, marketing/TVC-style ads, corporate videos, business videos, brand films, product-feature videos, narrated videos, and videos generated with references or source materials. Do not use for short-drama writing, plot scripts, episodic stories, role-play stories, or film/TV narrative creation; those should route to doubao-creative-drama. Use this skill for drama/story materials only when the user explicitly asks to turn them into ordinary videos, commercial ads, UGC, or corporate promotional videos.
---

# Video Generation

## Core Rules

When the user asks to generate a video, do not start generation immediately and do not call the video generation tool immediately.

First clarify and confirm the basic parameters:

- Duration: for example `5s`, `10s`, `15s`.
- Supported `text_video` ratios: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`.
- Supported `image_video` ratios when `task_type=r2v`: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`.
- When `image_video` uses `task_type=f2v`, the ratio can only keep the original ratio. If the user asks to change it, explain this.
- Detailed generation content: subject, action, scene, style, camera movement, mood, text, sound, and other constraints.
- Generate at most two videos at one time. If the user asks for more than two, clarify; each call may generate only two videos.

Continue to generation only after the user explicitly confirms the parameters. Even if the user already provided all parameters, output a parameter summary once and wait for confirmation. Valid confirmation can be `confirm`, `generate`, `start`, `looks good`, `yes`, `no problem`, and similar expressions.

Confirmation must belong to the current task. Any new video task, new product, new brief, new platform, new duration, or new style requires a fresh confirmation summary. Historical confirmation cannot be reused. Short replies such as `OK`, `good`, `yes`, or other brief acknowledgements count only when they immediately follow a confirmation summary; after a new requirement, they are treated as new content or discussion, not permission to generate.

Do not force the user to fill every parameter one by one by default. Infer a strong first version from the user's brief, video use case, and common platform habits, then ask whether to generate with that version. Ask follow-up questions only when key information cannot be reasonably inferred or must be supplied by the user, such as product images, product facts, talking-head script, or incomplete user-specified hard constraints.

## Single Final Video Policy

The default final deliverable is exactly one video.

The video generation tool can generate at most 15 seconds per video. Treat this as a creative constraint, not as a reason to split the user's request into multiple delivered clips. Even if the user asks for a "long video", "make it longer", "director's cut", "full story", "complete video", or "polished film", default to one complete 15-second video that compresses the most important story beats, visuals, narration, and pacing into a single coherent final video.

Do not proactively propose or generate multiple segments, chapters, clips, or sequential videos merely because the user asked for something long or cinematic. In the confirmation summary, state that the tool supports up to 15 seconds and that you will create one complete 15-second final video.

Multiple videos are allowed only when the user explicitly asks for multiple clips, separate chapters, variants, A/B options, batches, or a multi-part sequence, or when the user explicitly chooses multi-video delivery after you explain the single-video default.

For follow-up requests such as adding narration, subtitles, changing style, or making the video longer, generate one updated replacement final video by default. Do not treat the new version as an additional set of clips unless the user explicitly requests multiple versions.

## Workflow

1. Detect whether the user intends to generate a video.
2. Classify the request as ordinary video, product ad, talking-head/narrated video, UGC, marketing, corporate/business video, or a combination.
3. Extract provided duration, ratio, detailed content, product information, talking-head/narration information, and references.
4. If the request matches product ad, UGC, marketing, or corporate/business video, first run the product/company material gate.
5. If basic parameters, product information, or speech information are missing or unclear, ask for the missing fields. If all fields are present, still proceed to a confirmation summary before generation.
6. If the video includes speech, narration, or explanation, clearly state the final script source: user-provided, extracted from references, or drafted by Codex. The final script must appear in the confirmation summary.
7. Once information is complete, or once the user chooses generation without product reference, summarize the final parameters and ask for confirmation.
8. If the user modifies any parameter, update the summary and ask for confirmation again.
9. Only after explicit confirmation may you call the video generation tool or enter the generation process.
10. Before applying UGC, marketing, or corporate reference strategies, run the storyboard-image/keyframe gate. If images are not explicitly requested, output only a storyboard table and do not generate storyboard images or keyframes.

## Global Search Triggers

- If the user mentions "Doubao" and asks for a photo together, interaction, Doubao character/IP/avatar/emoji, or a Doubao visual, search for the Doubao app character image. Do not rely on memory.
- If the user uses freshness terms such as trending, recent, latest, news, this year, now, today, and the topic involves brands, companies, products, IP, people, locations, events, holidays, or hot topics, search for current information. Do not treat stale memory as current fact.
- Search results may supplement facts, visual references, platform context, and risk checks. Final generation parameters must still return to this skill's clarification and confirmation flow; do not generate without user confirmation.

## Using Search Results

- Knowledge: verified knowledge may be used as `knowledge_ref`, kept in `source_map`, and rewritten into dialogue or narration. The final script still requires user confirmation.

## Product / Company Material Gate

For product ads, UGC, marketing, or corporate/business videos, require product uploads, company materials, brand assets, or usable references before entering the corresponding strategy.

Product/company references include:

- Product images, packaging images, SKU images, product detail screenshots, manuals, or product files.
- Company materials, official website, company intro, logo/IP/VI, brand assets, product-feature materials, office/factory/store/team/event footage, customer cases, or service-process materials.
- A sufficiently clear product or company text brief. Without images or brand assets, it can only serve as conceptual/text reference and must be stated in the confirmation summary.

If the user provides no product, company, brand, or usable reference:

1. Ask once for the user to upload product/company/brand references, or explicitly choose "generate without reference / generate directly / generate from conceptual brief".
2. If the user chooses to upload materials, wait for them before summarizing.
3. If the user explicitly chooses direct generation, continue, but the confirmation summary must say: `References: none; generating from conceptual/text brief; product appearance, company visuals, and brand assets are not guaranteed to match reality`.

UGC, marketing, and corporate references cannot bypass this gate. They only handle storyboard, prompt, and generation strategy after the main confirmation flow.

## Storyboard Image / Keyframe Gate

The default deliverable is a storyboard table, not storyboard images. The main file and all references must follow this rule:

- If the user says only "storyboard", "storyboard script", "storyboard table", or "shooting script", output a table or text storyboard only. Do not generate images or call image/keyframe tools.
- Generate storyboard images, keyframes, first-frame images, or shot images only when the user explicitly asks for them.
- If a UGC/marketing reference requires a storyboard table first, output the storyboard table first. Whether to continue to images is still controlled by this gate.
- If the user wants final video but does not ask for storyboard images, the flow is: storyboard table -> video prompt -> video tool. Do not insert an image-generation step.
- If the user wants both video and keyframe/storyboard images, the flow is: storyboard table -> keyframe/storyboard images -> video prompt -> video tool. Keyframe count and purpose must be included in the confirmation summary.
- Dialogue/narration/sound is required for every storyboard shot. It may be the full text, or "no dialogue/no narration, BGM + ambience only"; it cannot be missing or left blank. The confirmation summary must list the corresponding dialogue/narration/sound for every shot. Without this confirmation, do not enter video prompt or tool calls.
- If "storyboard" is ambiguous, treat it as a storyboard table. Do not ask whether images are needed unless the tool call depends on image input.

## Reference Routing Strategy

`ref` is an input form. It does not change the parameter-confirmation gate and does not replace the user's current explicit request. When the user provides reference files, images, videos, audio, documents, asset packs, or similar inputs, identify each reference's role first and merge usable information into the relevant video-type summary.

## Mandatory Attachment Utilization

User-provided attachments are first-class generation references, not optional background context. Unless an attachment is clearly unrelated to the requested video, you must use it in the generation plan and explain its role in the confirmation summary. Relevant image and video attachments should contribute visual evidence such as product appearance, scene, composition, camera angle, motion beats, lighting, color palette, or style.

Do not discard a relevant attachment merely because it uses a local file path or video format. Instead, inspect it, extract frames if needed, upload usable references, and use those references in `image_to_video` whenever possible.

Text-only description is a last-resort fallback for relevant visual attachments. Use `dropped_text_only` only when the attachment is unreadable, visually irrelevant, the user explicitly says not to use it, or inspection/extraction/upload fails after a reasonable attempt. If you fall back to text-only for a relevant attachment, state the reason in the confirmation summary.

## Video Attachment References Without Video-To-Video

The available generation tools are `text_to_video` and `image_to_video`; there is no direct `video_to_video` tool. When the user provides a video attachment or asks to generate a new video based on a reference video's style, motion, framing, subject behavior, or shot language, do not ignore the video attachment and do not fall back directly to `text_to_video` unless frame extraction is impossible.

First convert the reference video into image references. Use `ffmpeg` or an equivalent local tool to extract representative frames from the video attachment, then visually inspect every candidate frame before it can become an `image_to_video` reference. Listing filenames or confirming that files exist is not frame inspection. Choose a small set of useful frames that capture the relevant visual style, subject, environment, camera angle, and motion beats. For ordinary references, 3-6 frames is usually enough; avoid passing dozens of near-duplicate frames.

After frame extraction, call `Read` on each candidate local frame image before reasoning about that frame's content or style. A frame counts as visually inspected only when `Read` returns an image observation for that specific frame. `FileBatchUpload`, `ls`, file counts, filenames such as `frame_001.png`, uploaded URLs, or upload-success messages are not visual inspection and must not be used to infer what appears in a frame. If `Read` fails or does not return an image observation, do not claim to know the frame content; retry with fewer/lower-resolution frames, re-extract readable frames, or mark that frame as not visually inspected and explain why it cannot be used as a visual reference.

After extracting and inspecting frames with `Read`, treat selected frames as local image references: upload them with `FileBatchUpload`, use only the returned URLs in `image_reference_url_list`, and call `image_to_video` with a prompt that explicitly describes which aspects of the source video should be preserved. If the user supplied a relevant video reference, the default path is frame extraction -> `Read` visual inspection of candidate frames -> upload final references -> `image_to_video`. Do not use the video only as a text description unless visual reference creation fails or the video is clearly irrelevant.

Only skip frame extraction when the video attachment cannot be read, `ffmpeg` fails after a reasonable retry, or the user explicitly says not to use the video as visual reference. In that case, explain the limitation and ask whether to proceed with `text_to_video` from a text description.

## Local Image Upload Before Image-To-Video

`image_to_video` requires real image URLs in `image_reference_url_list`. It does not accept VM-local file paths, absolute paths, relative paths, or `file://` URLs.

Before calling `image_to_video`, inspect every image reference you plan to pass. If any candidate or final reference image is stored on the VM, including uploaded files, generated keyframes, extracted video frames, cropped images, or files under paths such as `/home/user/...`, first use `Read` when visual inspection is needed, then call `FileBatchUpload` on the local image files that are final references. Use only the URL values returned by `FileBatchUpload` in `image_reference_url_list`.

Never call `image_to_video` with values like `/home/user/.../image.jpg`, `./image.jpg`, or `file:///home/user/.../image.jpg`. If the upload fails or does not return usable URLs, do not try the local path anyway; fix the upload issue, reduce the image set, or explain the blocker before generation.

## General Reference Image And Storyboard Strategy

Full storyboard charts, multi-panel storyboard screenshots, and storyboard images with text should not be cropped or passed as a single visual reference to a video tool. Treat them only as `storyboard_structure_ref`: rewrite them in reading order as `Shot 01 -> Shot 02 -> Shot 03...`, extracting visuals, actions, dialogue/narration, key text, and product/IP preservation points. Convert all shot dialogue and narration into explicit content for user confirmation. Do not reproduce table borders, numbers, notes, screenshot UI, or watermarks. If text, order, or shot boundaries are unclear, output the decomposition for user confirmation first.

Number all uploaded, searched, or passed images in order as `@image1`, `@image2`, `@image3`. For on-screen IP, mascots, brand characters, logos, products, scenes, or company materials, state what `@imageN` refers to and what features must be preserved. Describe preservation and anti-drift constraints, including color, silhouette, accessories, layout, and other key visual points. Repeat the key appearance anchors in every relevant shot. If an IP, product, or scene is mentioned only as theme or inspiration and does not need to appear, no reference image is required.

Route references by role:

- `product_ref`: product photos, packaging, SKUs, detail pages, manuals, selling-point tables. Highest priority for product consistency.
- `company_ref`: official websites, company intros, annual reports, press releases, business scope, milestones, teams, credentials, and public company information.
- `case_ref`: customer cases, solutions, implementation processes, result data, customer logos, and authorization scope. Do not generate specific customers or data without authorization or confirmation.
- `brand_ref`: brand manuals, tone, colors, banned words, compliance, brand voice. It supplements brand restrictions and cannot override product facts.
- `script_ref`: talking scripts, narration, captions, livestream scripts, review copy, explanation outlines. Final script must still appear in the confirmation summary.
- `knowledge_ref`: verified factual knowledge; keep `source_map`; unverified content is not treated as fact.
- `scene_ref`: scene, space, display, or usage-environment images. Extract space, material, light, and arrangement; do not copy low-quality screenshots or cluttered chat/desk scenes.
- `style_ref`: moodboards, competitor ads, reference videos, shot language, color palettes. Extract only tone, light, composition, rhythm, and sound mood; do not copy proprietary assets, slogans, subtitles, or brand visuals.
- `audio_ref`: voice, BGM, tempo, mood audio. Use for voice tone, pace, BGM, and sound effects, not visual captions.
- `platform_ref`: platform rules, placement requirements, ratio, duration, banned words, compliance. If platform requirements conflict with video tool limits, explain and reconfirm the adjusted parameters.

When multiple references conflict, merge by this priority: current explicit user instruction > product authenticity, company facts, and tool limits > `product_ref`/`company_ref` > `case_ref`/customer authorization > `knowledge_ref`/sources > `script_ref` > `platform_ref`/brand restrictions > `brand_ref` > `scene_ref` > `style_ref` > `audio_ref`. Ask only about unresolved conflicts.

Reference route files:

- UGC talking route: read `references/ugc-talking-video-ref.md` for talking-head videos, host/avatar explanations, seeding/review/unboxing/tutorial videos, batch creator videos, UGC replication, in-feed sales, creator commerce, or talking commerce.
- Marketing route: read `references/product-marketing-ad-video-no-storyboard-ref.md` for product marketing ads, product showreels, no-storyboard-image ad films, single-product consumer conversion, product visual ads, and platform placements when the user does not mention in-feed, commerce, talking head, creator, or presenter explanation.
- Corporate route: read `references/corporate-business-video-ref.md` for product-feature introductions, corporate videos, business videos, brand films, company intros, investment videos, roadshow videos, conference openers, customer-case videos, employer-brand videos, service intros, B2B ads, and company promos. Corporate requests longer than 15s must first decide whether they are multiple independent 15s videos or a stitched long video; stitched mode requires whole-film planning before segment generation.
- If the user mentions in-feed commerce, sales video, creator commerce, or talking-head commerce, do not use the marketing reference unless the user explicitly says no host/creator/speech and wants a pure product ad.
- If a product ad and talking-head delivery are both present, choose by goal: host recommendation/trust/in-feed commerce uses UGC; product film/ad-grade visuals without talking/in-feed/commerce uses marketing.
- Marketing vs corporate: product showreel/ad-grade shots use marketing; company capability, business trust, investment, roadshow, customer case, employer brand, or conference opener uses corporate. If the target is unclear, ask only about goal and audience.

## Product Ad Requirements

For product ads, product videos, commerce videos, commercial ads, or similar, collect before generation:

- Product image: ask the user to upload/provide product photos, or use a routed `product_ref`.
- Product core information: product name, key selling points, target users, use cases, style/tone, brand restrictions, required copy, and CTA. These may come from `product_ref`, `brand_ref`, or `platform_ref`.

The final product-ad generation summary must include product images, product core information, reference routing result if any, duration, ratio, detailed generation content, and tool-limit adjustments.

If the user provides only an idea or text description without product images, ask for product photos first unless they explicitly confirm a fictional/concept product ad.

## Talking-Head And Narration Requirements

For speech, narration, explanation, host speech, talking-head delivery, voiceover, or similar spoken content, obtain the complete script before generation.

UGC talking videos default to 15 seconds when no duration is specified. Change it only when the user explicitly specifies another duration or a tool limit requires adjustment, then reconfirm.

UGC speech in the final video prompt must be wrapped as `{specific script}` and used only as `Monologue`, `audio_voiceover`, or `Audio` for voice and lip sync. It must not be subtitles, captions, lower thirds, or on-screen transcript text. Emphasis text/stickers must be separated from the speech field.

Marketing videos include complete narration by default. Informational/functional/promotion routes default to 3-5 main narration lines plus one closing slogan. Poetic/atmospheric/premium/fragrance/jewelry/gifting routes default to 2-3 poetic main narration lines plus one closing slogan. Only explicit requests for no narration or pure music cancel narration.

Corporate/business videos must include complete narration in the confirmation summary unless the user explicitly requests no narration or pure music.

Speech must be concrete enough to pass directly to the video tool. Codex may draft it from product/video information or `script_ref`, but the user must confirm it before generation.

Before tool calls, the speech/narration confirmation summary must include the script, speech style, voice tone, language, pace if specified, reference routing, duration, ratio, generation details, product fields if relevant, and tool-limit adjustments.

## Clarification Copy

For ordinary video:

```text
I can help generate the video. Please confirm these parameters first:
1. Duration:
2. Ratio:
3. Detailed generation content:
```

For product ads:

```text
Sure. A product ad video needs these details first:
1. Product image: please upload/provide product images, or a ref file containing product photos, selling points, or brand materials
2. Product core information: product name, key selling points, target users, use case, style/tone, required copy, or CTA
3. Video parameters: duration, ratio, detailed generation content
```

For talking-head/narrated videos:

```text
Sure. A video with speech or narration needs the script confirmed first:
1. Script: please provide complete speech, or provide script_ref/copy ref for extraction or drafting
2. Speech style: tone, language, pace, voice style if any
3. Video parameters: duration, ratio, detailed generation content
```

## Confirmation Copy

Before ordinary video generation:

```text
Please confirm the following video generation parameters:
- Duration:
- Ratio:
- Detailed generation content:

After you confirm, I will start generation.
```

Before product ad video generation:

```text
Please confirm the following product ad video generation parameters:
- Product image:
- Product core information:
- Reference routing result, if any:
- Duration:
- Ratio:
- Detailed generation content:

After you confirm, I will call the video generation tool.
```

Before talking-head/narrated video generation:

```text
Please confirm the following talking-head video generation parameters:
- Script:
- Speech style:
- Reference routing result, if any:
- Duration:
- Ratio:
- Detailed generation content:

After you confirm, I will call the video generation tool.
```

If the video is both a product ad and includes speech, include product image, product core information, and script together.

Do not treat silence, partial answers, more questions, vague agreement, or unrelated replies as confirmation.

## Generation Notes

- Use only user-confirmed parameters unless the target video tool requires format normalization.
- Write narration/speech text in the correct field and format.
- All generated videos, whether text-to-video or image-to-video, UGC, marketing, or corporate, must be displayed through `notify_hunman` before final success wording. Do not skip display because a raw URL seems sufficient.
- `notify_hunman` input must include a renderable video asset: `video_url`, `output_url`, `url`, `result_url`, or local video path. Do not pass only summary text, HTML/Markdown `<video>` snippets, or bare links.
- Only after confirming the video is displayed may you say the video was generated. If display fails, retry once with the same video asset; if it still fails, explain the display failure and keep the link/path for troubleshooting.
- If the video tool has duration, ratio, material, speech, or other limits, explain required adjustments and ask the user to reconfirm adjusted parameters.
- Regardless of whether parameters are complete, complete one confirmation round before generation. UGC/marketing/corporate references cannot skip confirmation.
- Do not generate storyboard, keyframe, or first-frame images by default. If the user does not explicitly request images, UGC/marketing/corporate workflows output only storyboard tables and continue to video.
- If the user is only brainstorming, writing prompts, planning storyboard, or asking about available parameters, assist normally; enter confirmation flow only when the user clearly requests generation.
- When searched people need to appear, decide whether they enter video parameters as reference images and write the reference reasonably in the prompt.
