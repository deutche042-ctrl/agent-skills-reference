---
name: anime-storyboard-generator
description: Converts original scripts or novels into anime-storyboard materials; supports generating character profiles, character prompts, scene prompts, Sora storyboard prompts, and tabular storyboard prompts.
---

# Anime Storyboard Script Generator

## Objective
- Use this Skill to convert a user-provided script or original novel text into the various materials required for anime-storyboard production.
- Capabilities include:
  - Analyze a script, extract character information, and generate character profiles.
  - Generate AI-art prompts from character profiles.
  - Extract scenes and generate scene descriptions and drawing prompts.
  - Convert the script into structured Sora video-storyboard prompts.
  - Generate tabular storyboard-script prompts.
- Trigger conditions:
  - The user expresses a clear intent such as “This is a script” or “Analyze this novel excerpt.”
  - The user mentions keywords such as “generate characters” or “make a storyboard.”
  - The user needs to convert text into a visual presentation.

## Procedure

### Step 1: Identify the User's Need
When the user supplies a script or original novel text, determine whether the request is clear:

**Criteria for a clear request**:
- The user directly states which content to generate, such as “generate character profiles and scenes.”
- The user uses a specific term such as “need a Sora storyboard” or “make a storyboard script.”
- The conversational context already establishes the objective.

**Cases where the request is unclear**:
- The user supplies only the script/novel text and does not say what is needed.
- The user says only “analyze this content.”
- The request is vague or poorly expressed.

### Step 2: Ask What the User Needs (Whether or Not It Appears Clear)

**Mandatory requirement**: whether or not the user has clearly stated a need, the agent must first ask what content the user wants generated and must not generate it immediately.

**Question to ask**:

```
I have received your script/original novel text. Please tell me which content you need (select one or more):

1. Character profiles (character name, appearance, personality, biography)
2. Character prompts (requires character profiles first; used for AI art)
3. Scene prompts (scene descriptions and drawing instructions; environment-only scenes)
4. Sora storyboard prompts (video storyboards, each containing three intervals: 0–3s, 3–7s, and 7–10s)
5. Storyboard prompts (tabular storyboard script)

You may select one or more items, and I will generate the corresponding content as requested.

Example: Please generate character profiles and scene prompts.
```

**Important principles**:
- ⚠️ **Absolutely prohibited**: directly generate everything (character profiles, character prompts, scene prompts, Sora storyboard prompts, and storyboard prompts).
- ⚠️ **Absolutely prohibited**: even if the user says “generate characters,” do not generate other content.
- ✅ **Required**: first ask what the user needs, then wait for a clear reply before generating.
- ✅ **Permitted**: if the user has already clearly stated what is needed, such as “generate character profiles and a Sora storyboard,” restate it for confirmation and then generate it.

**After asking**:
- If the user gives a specific request, such as “generate character profiles and scene prompts,” generate only that content.
- If the reply is vague, such as “generate everything” or “all of it,” confirm exactly which items are meant.
- If the user selects “character prompts” but provides no character profiles, ask whether to generate the profiles first.

### Step 3: Generate Content (After the User Clarifies the Need)

#### 3.1 Character Profiles
Analyze the characters in the script and extract the following information:

**Required fields**:
- Character name.
- Appearance: based on textual description or reasonable inference.
- Occupation/identity: the character's role in the story.
- Personality: analyzed from behavior, speech, and inner activity.
- Character biography: background, motivation, key events, and relationship to the main plot.

**Generation principles**:
- Prefer direct descriptions from the source.
- Reasonably infer unspecified appearance details consistent with the historical setting and character role.
- Base personality analysis on behavior and dialogue.
- Make the biography show the character's function and significance in the story.

#### 3.2 Character Prompts
Generate AI-art prompts from user-provided character profiles, or first run 3.1 to generate those profiles.

**Required elements**:
- Age and gender.
- Facial features (eyes, face shape, etc.).
- Hairstyle and hair color.
- Clothing consistent with the period and character identity.
- Accessories, ornaments, and props.
- Facial expression and demeanor.
- Quality requirements such as 8K, high resolution, and masterwork quality.
- Style details such as layered lighting and refined facial detail.

**Format example**:
```
[Character Name]:
Young woman with lowered, submissive black almond-shaped eyes; long jet-black hair arranged in a gentle cloud-following bun with a simple pearl hairpin; wearing a pale-cyan, stand-collar, front-opening embroidered long jacket and a moon-white pleated skirt; a translucent jade bracelet on her wrist and delicate Suzhou-embroidered soft-soled shoes; high resolution, extremely detailed, masterwork, 8K quality, refined facial detail, richly layered light and shadow.
```

#### 3.3 Scene Prompts
Analyze key scenes in the script and generate scene descriptions and drawing instructions.

**Core principles**:
- **Absolutely prohibited**: including any person in a drawing instruction.
- Drawing instructions must depict an **environment-only scene** (empty room/scenery only).
- Describe only space, light, atmosphere, furnishings, and detail.
- The visual description may imply a story, but the drawing instruction must contain no people.

**Required elements**:
- Scene name and number.
- Visual description: explain the space, light, atmosphere, and details; story context may be mentioned.
- Drawing instruction:
  - **Must be an empty scene** (empty/scenery only/no people).
  - Spatial structure (interior/exterior).
  - Light, color, and materials.
  - Atmosphere and emotion.
  - Technical parameters such as resolution and style.
  - Aspect ratio (`--ar 16:9`).
  - Version parameter (`--v 6.0`).

**Prohibited in drawing instructions**:
- ❌ Any person (`man`, `woman`, `person`, `character`, `figure`, etc.).
- ❌ Any body part (`face`, `hand`, `body`, etc.).
- ❌ Any human action (`sitting`, `standing`, `walking`, etc.).
- ❌ Any clothing or accessory.
- ❌ Any description pointing to a person (`silhouette`, `shadow of person`, etc.).

**Allowed in drawing instructions**:
- ✅ Spatial structure (`interior`, `exterior`, `room`, `hall`, `garden`, etc.).
- ✅ Furniture (`table`, `chair`, `bed`, `cabinet`, etc.).
- ✅ Decorative objects (`curtain`, `vase`, `painting`, `lantern`, etc.).
- ✅ Architectural elements (`window`, `door`, `pillar`, `roof`, etc.).
- ✅ Natural elements (`tree`, `flower`, `sky`, `moon`, etc.).
- ✅ Lighting effects (`candlelight`, `moonlight`, `shadow`, etc.).
- ✅ Material detail (`silk`, `wood`, `stone`, `fabric`, etc.).
- ✅ Environmental atmosphere (`festive`, `gloomy`, `peaceful`, etc.).
- ✅ Must contain the keywords: `empty / scenery only / no people / unoccupied`.

**Format example**:
```
Scene 1: Marquis's Wedding Chamber — Where the Lie Becomes True
Visual description: Present an extremely festive yet uncanny wedding night. The room is filled with bright-red silk and “Double Happiness” characters. Because of Lu Yanli's agonized struggle, the wedding wine cups on the table have overturned, the bed is disordered, and the dragon-and-phoenix candles sway in the wind, casting grotesque long shadows.
Drawing instruction: Interior of a luxurious ancient Chinese wedding chamber, empty. Saturated red silk curtains and "Double Happiness" banners. Flickering dragon-and-phoenix candles casting long, dancing shadows. On the rosewood table, an overturned wine cup and scattered red dates. A large ornate canopy bed with messy red silk bedding. The atmosphere is festive yet suffocating and eerie. Cinematic lighting, 8k, hyper-realistic. --ar 16:9 --v 6.0

Scene 2: The Dowager's Main Hall — Cold Authority
Visual description: The marquis's main hall late at night. Its strictly symmetrical furniture conveys the authority of a feudal matriarch. The cool bluestone floor reflects weak candlelight, smoke rises straight from the incense burner, and the solemn, oppressive atmosphere implies the dowager's indifference to the heroine.
Drawing instruction: A solemn and grand traditional Chinese hall in a noble mansion at night, empty. Symmetrical dark sandalwood furniture. A large folding screen with an ink landscape painting. Bronze incense burners releasing thin lines of smoke. Dim candlelight, cold gray stone floor with sharp reflections. Heavy, oppressive atmosphere of a strict noble household. 8k resolution, cinematic textures. --ar 16:9 --v 6.0

Scene 3: The Sparse Side Room — The Heroine's Refuge
Visual description: A small, sparsely furnished side room with a hardwood bed and dim oil lamp. Cold blue moonlight enters through the window and contrasts with the faint warm indoor light. This is where the heroine hides from the cries in the wedding room, creating a lonely, silent atmosphere.
Drawing instruction: A small, cramped side room (Ear Room) in an ancient mansion at night, empty. A simple wooden bed with plain gray bedding. A single dim oil lamp on a rough stool. Pale blue moonlight filters through a small paper window, creating a cold contrast with the faint yellow lamp light. Sparse and desolate atmosphere. 8k, realistic lighting. --ar 16:9 --v 6.0

Scene 4: Shen Residence Pavilion Garden (Flashback) — The Warm Jade Incident
Visual description: In the remembered Shen garden, a stone pavilion stands beside a lotus pond under trailing willows. An exquisite but empty brocade box on the stone table implies that the warm jade it held was forcibly taken. The sunlight is soft with a faintly sorrowful filtered quality.
Drawing instruction: A serene traditional Chinese garden with a stone pavilion by a lotus pond, empty. Soft daylight filtering through weeping willow branches. On the stone table in the pavilion, a small decorative box is left open. The water is still, and the atmosphere is nostalgic and slightly melancholic. High-end ancient garden design, 8k, soft focus background. --ar 16:9 --v 6.0

Scene 5: Shen Residence Rear Courtyard (Flashback) — Where the Dog Was Buried
Visual description: In a secluded corner of the Shen residence, a mound of fresh earth under a withered flowering tree symbolizes the heroine's dead puppy's grave. A small stone shovel leans against the gray-brick wall, fallen leaves cover the ground, and the dim gloomy light conveys the repression and tragedy of her childhood.
Drawing instruction: A secluded corner of a traditional Chinese courtyard, empty. A small mound of fresh earth under a withered flowering tree, symbolizing a pet's grave. A small stone shovel rests against a gray brick wall. Gloomy daylight, fallen leaves on the ground. The atmosphere is quiet and tragic. 8k, hyper-realistic textures of soil and stone. --ar 16:9 --v 6.0
```
- ✅ Spatial structure (`interior`, `exterior`, `room`, `hall`, `garden`, etc.).
- ✅ Furniture (`table`, `chair`, `bed`, `cabinet`, etc.).
- ✅ Decorative objects (`curtain`, `vase`, `painting`, `lantern`, etc.).
- ✅ Architectural elements (`window`, `door`, `pillar`, `roof`, etc.).
- ✅ Natural elements (`tree`, `flower`, `sky`, `moon`, etc.).
- ✅ Lighting effects (`candlelight`, `moonlight`, `shadow`, etc.).
- ✅ Material detail (`silk`, `wood`, `stone`, `fabric`, etc.).
- ✅ Environmental atmosphere (`festive`, `gloomy`, `peaceful`, etc.).

**Format example**:
```
Scene 1: Marquis's Wedding Chamber — Where the Lie Becomes True
Visual description: Present an extremely festive yet uncanny wedding night. The room is filled with bright-red silk and “Double Happiness” characters. Because of Lu Yanli's agonized struggle, the wedding wine cups on the table have overturned, the bed is disordered, and the dragon-and-phoenix candles sway in the wind, casting grotesque long shadows.
Drawing instruction: Interior of a luxurious ancient Chinese wedding chamber, empty. Saturated red silk curtains and "Double Happiness" banners. Flickering dragon-and-phoenix candles casting long, dancing shadows. On the rosewood table, an overturned wine cup and scattered red dates. A large ornate canopy bed with messy red silk bedding. The atmosphere is festive yet suffocating and eerie. Cinematic lighting, 8k, hyper-realistic. --ar 16:9 --v 6.0

Scene 2: The Dowager's Main Hall — Cold Authority
Visual description: The marquis's main hall late at night. Its strictly symmetrical furniture conveys the authority of a feudal matriarch. The cool bluestone floor reflects weak candlelight, smoke rises straight from the incense burner, and the solemn, oppressive atmosphere implies the dowager's indifference to the heroine.
Drawing instruction: A solemn and grand traditional Chinese hall in a noble mansion at night, empty. Symmetrical dark sandalwood furniture. A large folding screen with an ink landscape painting. Bronze incense burners releasing thin lines of smoke. Dim candlelight, cold gray stone floor with sharp reflections. Heavy, oppressive atmosphere of a strict noble household. 8k resolution, cinematic textures. --ar 16:9 --v 6.0
```
  - Atmosphere and emotion.
  - Technical parameters (resolution, style, etc.).
  - Aspect ratio (`--ar 16:9`).
  - Version parameter (`--v 6.0`).

**Format example**:
```
Scene 1: Marquis's Wedding Chamber — Where the Lie Becomes True
Visual description: Present an extremely festive yet uncanny wedding night. The room is filled with bright-red silk and “Double Happiness” characters. Because of Lu Yanli's agonized struggle, the wedding wine cups on the table have overturned, the bed is disordered, and the dragon-and-phoenix candles sway in the wind, casting grotesque long shadows.
Drawing instruction: Interior of a luxurious ancient Chinese wedding chamber, empty. Saturated red silk curtains and "Double Happiness" banners. Flickering dragon-and-phoenix candles casting long, dancing shadows. On the rosewood table, an overturned wine cup and scattered red dates. A large ornate canopy bed with messy red silk bedding. The atmosphere is festive yet suffocating and eerie. Cinematic lighting, 8k, hyper-realistic. --ar 16:9 --v 6.0
```

#### 3.4 Sora Storyboard Prompts
Convert the script into structured video-storyboard prompts.

**Core principles**:
- Every storyboard unit must contain all three time segments (0–3s, 3–7s, and 7–10s).
- Shot sizes and camera movements must be varied; avoid repeating the same combination.
- Dynamically adjust shot size and movement to the script content and emotional changes.
- The time segments must progress logically and remain visually continuous.

**Shot-size selection rules**:
- **Opening/transition**: use a long or wide shot to establish the environment and spatial relationships.
- **Dialogue**: use medium or medium-close shots for interaction and expression.
- **Emotional climax**: use close-ups to emphasize inner state and key detail.
- **Action**: use medium shots with fast movement to enhance motion.
- **Inner monologue**: use a close-up or extreme close-up for subtle expression.
- **Suspense**: push from a long shot to medium, or pull from close-up to medium.

**Camera-movement selection rules**:
- **Push in**: emphasize detail, build emotion, or focus attention.
- **Pull out**: reveal environment, release tension, or transition.
- **Pan**: follow a moving character or scan the scene.
- **Tilt**: show height differences or change viewpoint.
- **Shake**: convey chaos, subjective vision, or horror.
- **Locked**: calm observation, objective statement, or stable dialogue.
- **Rotate**: create dramatic effect or survey the environment.

**Mandatory requirements**:
- Every storyboard unit must contain 0–3s, 3–7s, and 7–10s.
- Each segment independently describes visuals, camera, sound, emotion, and dialogue.
- Adjacent units must vary shot size; do not use the same size consecutively.
- Vary movement; different segments within one unit may use different movements.
- The three segments must progress rather than repeat the same content.

**Format**: a JSON array in which each element is one storyboard unit.

**Required fields**:
- Storyboard number: numeric, beginning at 1.
- Sora prompt, containing:
  - Characters appearing in the unit, including appearance/state.
  - Time segment `[X–Ys]`, described independently.
  - Camera: shot size + camera movement.
  - Sound/music: ambience, background music, dialogue, etc.
  - Emotion/atmosphere: the current emotional tone.
  - Narration/dialogue: spoken line or inner monologue.

**Generation principles**:
- Every unit always contains the three specified segments.
- Camera language must express narrative logic (build → climax → release, etc.).
- Sound and emotion must support the visuals.
- Follow the template's JSON structure.
- **Absolutely prohibited**: generating only one segment or using the same size and movement in every unit.

**Format example** (all three segments, with varied shot sizes and movements):
```json
[
  {
    "storyboard_number": 1,
    "sora_prompt": "Characters: Shen Wanyu (wearing an elaborate bright-red wedding dress and gold hairpin, with delicate features and a timid, shrinking gaze), Lu Yanli (wearing bright-red wedding robes, handsome but showing a trace of false helplessness)\n[0–3 seconds]\nCamera: [locked medium shot] Red candles burn brightly in the wedding chamber and a happiness character hangs above the bed. Lu Yanli sits on the wedding bed with furrowed brows, feigning unbearable guilt. His hands loosely hold Shen Wanyu's while his gaze flickers away.\nSound/music: leaves rustling in the breeze outside + red candlewicks crackling indoors + Lu Yanli's affectionate but false sigh.\nEmotion/atmosphere: seemingly tender, actually false and oppressive.\nNarration/dialogue: Lu Yanli (feigning grief): \"Wanyu, I was wounded in the groin on the battlefield. Marrying me has truly wronged you... Apart from children, I will give you everything.\"\n\n[3–7 seconds]\nCamera: [close-up push-in] The camera quickly pushes into Shen Wanyu's face. She had been listening submissively with lowered eyes, but her pupils suddenly dilate in shock and disbelief. In the empty space of her viewpoint above the image, a glowing translucent system message appears: [Beep! Young Marquis Lu Yanli's manhood has been destroyed.]\nSound/music: a crisp electronic system beep contrasting with the historical setting + Shen Wanyu's sharp intake of breath.\nEmotion/atmosphere: absurdity, astonishment, and a sudden reversal.\nNarration/dialogue: System voice: [Beep! Young Marquis Lu Yanli's manhood has been destroyed.]\n\n[7–10 seconds]\nCamera: [medium pull-out] Shen Wanyu instinctively steps back half a pace and looks fearfully at Lu Yanli's lower body, tightly twisting the wedding handkerchief in her hands. Lu Yanli's formerly affected expression freezes, as if he senses an inexplicable chill approaching.\nSound/music: the background music stops abruptly, leaving only awkward silence.\nEmotion/atmosphere: uncanny calm, the calm before the storm.\nNarration/dialogue: Shen Wanyu (inner monologue, trembling): \"Young Marquis... you went this far?\""
  },
  {
    "storyboard_number": 2,
    "sora_prompt": "Characters: Shen Wanyu; Lu Yanli (face now distorted and drenched in sweat)\n[0–3 seconds]\nCamera: [sudden medium-close] Lu Yanli suddenly screams and springs up from the bed, both hands clamped over his groin. He curls like a shrimp and collapses onto the wedding quilt, features grotesquely twisted by pain as veins instantly rise on his forehead.\nSound/music: Lu Yanli's shrill, cracking scream + the thud of his body striking the bed.\nEmotion/atmosphere: extreme pain, chaos, and horror.\nNarration/dialogue: Lu Yanli (screaming): \"Ah! It hurts! It hurts to death!\"\n\n[3–7 seconds]\nCamera: [shaking handheld] The camera simulates Shen Wanyu's frightened viewpoint and shakes violently. Lu Yanli rolls wildly on the bed, knocking red dates and longans to the floor. He struggles amid the disordered bedding and stretches a trembling hand into empty space for help.\nSound/music: red dates and longans clattering across the floor + Lu Yanli's rapid panting and groans.\nEmotion/atmosphere: panic and loss of control.\nNarration/dialogue: Lu Yanli (roaring): \"Imperial physician! Get the imperial physician! Hurry!\"\n\n[7–10 seconds]\nCamera: [high-angle medium] Shen Wanyu stands beside the bed at a loss. She reaches out to help but is afraid to touch him, wearing a timid, conflicted expression while involuntarily glancing at the place he is covering.\nSound/music: Lu Yanli's continuing wails in the background + the rustle of Shen Wanyu's clothing.\nEmotion/atmosphere: helplessness and absurdity.\nNarration/dialogue: Shen Wanyu (weakly): \"Has my husband's old injury flared up? Calling an imperial physician on our wedding day... this...\""
  }
]
```

**Reference shot-size and movement combinations**:
- Opening: locked long shot → medium push-in → medium pan.
- Dialogue: locked medium → cut to medium-close → close-up pull-out.
- Emotional outburst: sudden medium-close → handheld shake → locked close-up.
- Transition: locked wide → medium push-in → medium pull-out.
- Suspense: close-up push-in → high-angle medium-close → medium pan.
- Flashback: locked medium → close-up push-in → filtered close-up pull-out.

#### 3.5 Storyboard Prompts
Convert the script into a tabular storyboard script for easy understanding and use.

**Core principles**:
- Vary shot size and choose it for the scene content.
- Match movement to content; do not make every shot locked.
- Adjust duration to content density; important content may run slightly longer.
- Vary the size of adjacent shots.

**Shot-size selection rules**:
- Opening/transition: long shot (2–3s).
- Dialogue: medium (1.5–2s).
- Emotion: medium-close/close-up (1–2s).
- Action: medium (1–2s).
- Detail emphasis: close-up (1s).
- Environmental display: wide (2–3s).

**Camera-movement selection rules**:
- Push in: focus on a character or detail.
- Pull out: reveal environment or release emotion.
- Cut: switch quickly and tighten rhythm.
- Pan: follow a character or scan a scene.
- High angle: authoritative viewpoint looking down.
- Low angle: vulnerable viewpoint or increased stature.
- Shake: chaos or subjective viewpoint.
- Follow: movement and immersion.
- Push-pull: dynamic distance change.
- Rotate: dramatic effect or environmental survey.

**Mandatory requirements**:
- Adjacent shots must change size; do not repeat the same size consecutively.
- Vary movement; not every shot may be locked.
- Adjust duration to content; not every shot may have the same duration.
- Include at least five sizes: long, wide, medium, medium-close, and close-up.
- Include at least five movements: locked, push-in, pull-out, pan, and cut.

**Table columns**:
- Shot number: numeric ID.
- Scene: the location where the shot occurs.
- Shot size: medium/medium-close/close-up/wide, etc.
- Shot content: detailed action, expression, and positional relationship.
- Duration: seconds, adjusted to content (1–3s).
- Movement: locked/push/pull/pan/track/follow, etc.
- Sound/dialogue: ambience, background music, and dialogue.
- Notes: additional guidance, such as points useful for AI generation.

**Format example** (varied shot sizes and movements):
| Shot No. | Scene | Shot Size | Shot Content | Duration | Movement | Sound / Dialogue | Notes (Jimeng Adaptation) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Marquis's wedding room (wedding night) | Medium | Red candles flicker among happiness characters. Shen Wanyu sits upright at the bed's edge, clutching her skirt with a timid gaze; Lu Yanli stands tense-backed at the table. | 2s | Slow push-in | Candle crackle; Lu Yanli (low): “Wanyu, I was wounded in the groin on the battlefield. Marrying me has truly wronged you.” | Emphasize the wedding atmosphere and his difficulty |
| 2 | Wedding room | Medium-close (male lead) | Lu Yanli turns with knitted brows and a guilty look, hands lowered as though concealing something. | 1s | Cut | Lu Yanli: “But I swear that, apart from children, I will give you everything I can.” | Capture his affected difficulty |
| 3 | Wedding room (heroine POV) | Close-up (heroine) | Shen Wanyu's pupils contract; her mouth parts and eyes widen in shock, with an inner subtitle: “Young Marquis went this far?” | 1.5s | Locked | Mechanical system prompt: “Beep! Young Marquis Lu Yanli's manhood has been destroyed.” | Use subtitles for inner thought and AI clarity |
| 4 | Wedding room | Medium | Lu Yanli suddenly bends over, clamps both hands over his groin, curls up, sweats, and wails. | 1.5s | Fast pull | Lu Yanli (in pain): “Imperial physician! Get the imperial physician!”; cloth rustle | Exaggerate his pain for anime expression |
| 5 | Wedding room (heroine) | Medium-close | Shen Wanyu rises, conflicted and evasive, tugging her sleeve and glancing at the covered area. | 1.5s | Slight pan | Shen Wanyu (softly): “Has my husband's old injury flared up? Calling a physician on our wedding day... I fear tomorrow's gossip.” | Show her timid, trouble-averse nature |
| 6 | Wedding room (male lead) | Close-up | Red-faced and grimacing, Lu Yanli roars and waves away her warning. | 1s | Close-up cut | Lu Yanli (irritable): “Imperial physician! I am dying of pain—can't you see?” | Intensify pain and irritability |
| 7 | Wedding room → Dowager's courtyard | Wide transition | Tearful Shen Wanyu follows the nursemaid through the night corridor; lantern light casts their shadows. | 2s | Follow | Footsteps and lantern movement; Shen Wanyu subtitle: “I am kind and timid—how could I decide...” | Establish the transition and grievance |
| 8 | Dowager's room | Medium | The dowager sits in an armchair, eyes shifting and fingers tapping; Shen Wanyu stands below with head bowed and the nursemaid beside her. | 1.5s | Locked | Dowager: “Wanyu, Yanli is crazed by pain. Why can't you make a decision?” | Capture her calculating micro-expression |
| 9 | Dowager's room (heroine) | Close-up | Shen Wanyu's shoulders tremble; she lowers her head and twists her hands as if about to cry. | 1s | Cut | Dowager: “It is an old injury; endure it... Do you want the world laughing at this house?” | Contrast timidity with cruelty |
| 10 | Maternal home (flashback) | Dark medium | Young Shen Wanyu grips the warm jade while half-sister Shen Wanqiu cries and tugs her sleeve, then smirks after receiving it. | 2s | Flashback filter | System: “Beep! Cold illness has entered Shen Wanqiu; she will never conceive.” Shen Wanyu: “You suffer from cold; take it...” | Dark palette marks the flashback and lie-becomes-true premise |
| 11 | Maternal-home rear yard (flashback) | Medium-close | Tearful Shen Wanyu buries the dog while her half-brother cries nearby, “I didn't mean it...” | 1.5s | Slow crane down | Sobbing; system: “Beep! The half-brother's mind is impaired; he cannot care for himself.” | Convey key information rapidly |
| 12 | Marquis's side room | Medium | In the sparse room, Shen Wanyu sits red-eyed on a small bed, looking toward the door as Lu Yanli's intermittent wails carry from afar. | 2s | Locked | Distant wails fading but continuing; subtitle: “I dare offend neither my mother-in-law nor the marquis...” | End on suspense and the long night |

**Summary of mandatory requirements**:
- Adjacent shots must change size and may not repeat the same size consecutively.
- Camera movements must be varied; not every shot may be locked.
- Durations must be adjusted to content and may not all be identical.
- The table must include at least long, wide, medium, medium-close, and close-up.
- The table must include at least locked, push-in, pull-out, pan, and cut.

**Format example** (varied shot sizes and movements):
| Shot No. | Scene | Shot Size | Shot Content | Duration | Movement | Sound / Dialogue | Notes (Jimeng Adaptation) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Marquis's wedding room (wedding night) | Medium | Red candles flicker among happiness characters. Shen Wanyu sits upright at the bed's edge, clutching her skirt with a timid gaze; Lu Yanli stands tense-backed at the table. | 2s | Slow push-in | Candle crackle; Lu Yanli (low): “Wanyu, I was wounded in the groin on the battlefield. Marrying me has truly wronged you.” | Emphasize the wedding atmosphere and his difficulty |
| 2 | Wedding room | Medium-close (male lead) | Lu Yanli turns with knitted brows and a guilty look, hands lowered as though concealing something. | 1s | Cut | Lu Yanli: “But I swear that, apart from children, I will give you everything I can.” | Capture his affected difficulty |
| 3 | Wedding room (heroine POV) | Close-up (heroine) | Shen Wanyu's pupils contract; her mouth parts and eyes widen in shock, with an inner subtitle: “Young Marquis went this far?” | 1.5s | Locked | Mechanical system prompt: “Beep! Young Marquis Lu Yanli's manhood has been destroyed.” | Use subtitles for inner thought and AI clarity |
| 4 | Wedding room | Medium | Lu Yanli suddenly bends over, clamps both hands over his groin, curls up, sweats, and wails. | 1.5s | Fast pull | Lu Yanli (in pain): “Imperial physician! Get the imperial physician!”; cloth rustle | Exaggerate his pain for anime expression |
| 5 | Wedding room (heroine) | Medium-close | Shen Wanyu rises, conflicted and evasive, tugging her sleeve and glancing at the covered area. | 1.5s | Slight pan | Shen Wanyu (softly): “Has my husband's old injury flared up? Calling a physician on our wedding day... I fear tomorrow's gossip.” | Show her timid, trouble-averse nature |
| 6 | Wedding room (male lead) | Close-up | Red-faced and grimacing, Lu Yanli roars and waves away her warning. | 1s | Close-up cut | Lu Yanli (irritable): “Imperial physician! I am dying of pain—can't you see?” | Intensify pain and irritability |
| 7 | Wedding room → Dowager's courtyard | Wide transition | Tearful Shen Wanyu follows the nursemaid through the night corridor; lantern light casts their shadows. | 2s | Follow | Footsteps and lantern movement; Shen Wanyu subtitle: “I am kind and timid—how could I decide...” | Establish the transition and grievance |
| 8 | Dowager's room | Medium | The dowager sits in an armchair, eyes shifting and fingers tapping; Shen Wanyu stands below with head bowed and the nursemaid beside her. | 1.5s | Locked | Dowager: “Wanyu, Yanli is crazed by pain. Why can't you make a decision?” | Capture her calculating micro-expression |
| 9 | Dowager's room (heroine) | Close-up | Shen Wanyu's shoulders tremble; she lowers her head and twists her hands as if about to cry. | 1s | Cut | Dowager: “It is an old injury; endure it... Do you want the world laughing at this house?” | Contrast timidity with cruelty |
| 10 | Maternal home (flashback) | Dark medium | Young Shen Wanyu grips the warm jade while half-sister Shen Wanqiu cries and tugs her sleeve, then smirks after receiving it. | 2s | Flashback filter | System: “Beep! Cold illness has entered Shen Wanqiu; she will never conceive.” Shen Wanyu: “You suffer from cold; take it...” | Dark palette marks the flashback and lie-becomes-true premise |
| 11 | Maternal-home rear yard (flashback) | Medium-close | Tearful Shen Wanyu buries the dog while her half-brother cries nearby, “I didn't mean it...” | 1.5s | Slow crane down | Sobbing; system: “Beep! The half-brother's mind is impaired; he cannot care for himself.” | Convey key information rapidly |
| 12 | Marquis's side room | Medium | In the sparse room, Shen Wanyu sits red-eyed on a small bed, looking toward the door as Lu Yanli's intermittent wails carry from afar. | 2s | Locked | Distant wails fading but continuing; subtitle: “I dare offend neither my mother-in-law nor the marquis...” | End on suspense and the long night |

### Step 4: Output the Content
Output all generated content in the following format:

```
# Original Script
[User's original script content]

# Character Profiles
[Character 1 content]

***

[Character 2 content]

***

[Character N content]

# Character Prompts
[Character 1 prompt]

[Character 2 prompt]

[Character N prompt]

# Sora Storyboard Prompts
```json
[JSON array]
```

# Scene Prompts
[Scene 1 content]

[Scene 2 content]

[Scene N content]

# Storyboard Prompts
| Shot No. | Scene | Shot Size | Shot Content | Duration | Movement | Sound / Dialogue | Notes (Jimeng Adaptation) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [Storyboard table content]
```

**Notes**:
- Follow the Markdown format above strictly.
- Keep hierarchy and indentation consistent.
- JSON code blocks must use the `json` fence label.
- Use standard Markdown table syntax.
- Separate sections with blank lines.

## Resource Index
- Output-format template: [references/output-format-template.md](references/output-format-template.md) (complete examples for all five content types).
- Storyboard guide: [references/storyboard-guide.md](references/storyboard-guide.md) (core elements and techniques).
- Shot-language rules: [references/shot-language-rules.md](references/shot-language-rules.md) (detailed shot-size and movement selection).
- Scene-prompt rules: [references/scene-prompt-rules.md](references/scene-prompt-rules.md) (ensures drawing instructions contain no people).
- Storyboard tutorial: [references/anime_storyboard_guide.pdf](references/anime_storyboard_guide.pdf) (detailed PDF tutorial).

## Notes
- **Mandatory**: after receiving a script/original novel text, first ask what content is needed; do not generate immediately.
- **Absolutely prohibited**: generating all five content types at once.
- **Absolutely prohibited**: generating any content the user did not request.
- Character prompts must be based on character profiles, not invented without them.
- Sora JSON must be valid; mark every segment with `【X-Y秒】`.
- **Every Sora unit must contain all three segments: 0–3s, 3–7s, and 7–10s.**
- **Sora shot sizes and movements must vary; they may not all be locked medium shots.**
- **Scene drawing prompts must contain `empty / scenery only / no people`.**
- **Scene drawing prompts must not contain any person, body part, human action, or clothing.**
- Storyboard-table content must be concrete and executable for AI video generation.
- Use the agent's text understanding and creative ability; do not write scripts for simple tasks.
- Base every output on the user's source and do not depart from the original setting.

## Usage Examples

### Example 1: The User Supplies a Script (Whether or Not the Need Is Clear)

**User input**:
```
This is a historical-costume drama script:
[Script content]
Please generate character profiles and scene prompts.
```

**Agent response** (mandatory question; do not generate immediately):
```
I have received your script/original novel text. Please tell me which content you need (select one or more):

1. Character profiles (name, appearance, personality, biography)
2. Character prompts (requires profiles first; used for AI art)
3. Scene prompts (scene descriptions and drawing instructions; environment-only)
4. Sora storyboard prompts (each video unit contains 0–3s, 3–7s, and 7–10s)
5. Storyboard prompts (tabular storyboard script)

You may select one or more items, and I will generate the corresponding content as requested.

Example: Please generate character profiles and scene prompts.
```

### Example 2: The User Clearly States the Need

**User reply**:
```
Please generate character profiles and scene prompts.
```

**Agent response**:
```
Understood. I will generate character profiles and scene prompts for you.

# Original Script
[User's original script content]

# Character Profiles
[Character 1 content]

***

[Character 2 content]

# Scene Prompts
Scene 1: [Scene name]
Visual description: [Visual description]
Drawing instruction: [Drawing instruction]

Scene 2: [Scene name]
Visual description: [Visual description]
Drawing instruction: [Drawing instruction]
```

### Example 3: The User Replies Vaguely

**User reply**:
```
Generate all of them.
```

**Agent response**:
```
Sorry, I need you to specify exactly which content to generate. Select one or more of the following:

1. Character profiles
2. Character prompts
3. Scene prompts
4. Sora storyboard prompts
5. Storyboard prompts

Example: Please generate 1, 3, and 5 (character profiles, scene prompts, and storyboard prompts).
```

### Example 4: The User Requests Character Prompts Without Providing Character Profiles

**User reply**:
```
Please generate character prompts.
```

**Agent response**:
```
Character prompts must be based on character profiles. Would you like me to generate the character profiles first?

If so, I will first generate the profiles and then generate character prompts from them.

If you already have character profiles, provide them directly and I will generate prompts from them.
```
