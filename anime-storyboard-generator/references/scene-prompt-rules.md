# Scene-Prompt Generation Rules

This document defines how to generate scene prompts that contain no characters and describe only the environment.

## Core Principles

**Strictly prohibited**: Any person or character in the image-generation prompt.
**Required**: The prompt must describe a pure environmental scene—empty, scenery only, or no people.

## Image-Prompt Components

### Required Elements
1. **Setting type**: Interior or exterior
2. **Spatial structure**: Room, courtyard, garden, hall, and so on
3. **Furniture**: Tables, chairs, beds, cabinets, folding screens, and so on
4. **Decorations**: Curtains, vases, paintings, lanterns, ornaments, and so on
5. **Architectural elements**: Doors, windows, pillars, roofs, walls, and so on
6. **Natural elements**: Trees, plants, sky, moon, water, and so on
7. **Lighting**: Candlelight, moonlight, sunlight, shadows, and so on
8. **Material detail**: Silk, wood, stone, fabric, and so on
9. **Atmosphere**: Festive, gloomy, peaceful, oppressive, and so on
10. **Technical parameters**: Resolution, style, aspect ratio, and so on

### Mandatory Keywords
The image-generation prompt must contain at least one of these keywords:
- `empty`
- `scenery only`
- `no people`
- `unoccupied`
- `abandoned`
- `deserted`

## Prohibited Content

### Any Character-Related Terms
- ❌ People: man, woman, person, character, figure, human, people, girl, boy, lady, gentleman, master, servant, maid
- ❌ Body parts: face, hand, body, head, foot, arm, leg, eye, ear, mouth, nose
- ❌ Human actions: sitting, standing, walking, running, lying, sleeping, eating, drinking, talking, crying, laughing
- ❌ Human states: tired, happy, sad, angry, fearful, anxious, worried
- ❌ Human appearance: beautiful, ugly, young, old, tall, short, thin, fat
- ❌ Clothing: dress, robe, coat, shirt, pants, shoes, hat, jewelry, accessory
- ❌ Accessories: ring, necklace, bracelet, earring, hairpin
- ❌ Implied people: silhouette, shadow of person, human figure in distance, someone's belongings
- ❌ Human interactions: couple, family, group, crowd, meeting, talking, conversation

### Common Error Examples
```
❌ Incorrect: A woman standing in the room
✅ Correct: An empty room with furniture

❌ Incorrect: Interior scene, someone is sitting on the chair
✅ Correct: Interior scene, a chair in the center

❌ Incorrect: Bedroom with clothes on the bed
✅ Correct: Bedroom with a neatly made bed

❌ Incorrect: A man's shoes on the floor
✅ Correct: Empty room, wooden floor

❌ Incorrect: A woman's shadow on the wall
✅ Correct: Shadows from candlelight on the wall
```

## Allowed Content

### Spatial Structures
- ✅ `interior of a room`
- ✅ `exterior of a building`
- ✅ `ancient Chinese hall`
- ✅ `traditional garden`
- ✅ `narrow side room`
- ✅ `spacious courtyard`

### Furniture
- ✅ `wooden table with carved patterns`
- ✅ `ornate canopy bed`
- ✅ `rosewood chair with cushions`
- ✅ `folding screen with landscape painting`
- ✅ `cabinet with drawers`
- ✅ `stool near the window`

### Decorations
- ✅ `red silk curtains`
- ✅ `porcelain vase on the table`
- ✅ `lantern hanging from the ceiling`
- ✅ `scroll painting on the wall`
- ✅ `incense burner releasing smoke`
- ✅ `decorative pillow`

### Architectural Elements
- ✅ `wooden door carved with patterns`
- ✅ `paper window with wooden lattice`
- ✅ `stone pillar with dragon relief`
- ✅ `tiled roof with eaves`
- ✅ `brick wall covered with ivy`

### Natural Elements
- ✅ `willow tree by the pond`
- ✅ `lotus flowers in bloom`
- ✅ `moonlight filtering through leaves`
- ✅ `still water reflecting the moon`
- ✅ `fallen leaves on the ground`
- ✅ `withered flowers`

### Lighting Effects
- ✅ `flickering candlelight`
- ✅ `soft morning light`
- ✅ `dim lamp light`
- ✅ `moonlight casting shadows`
- ✅ `sunlight streaming through window`
- ✅ `warm glow from the fireplace`

### Material Details
- ✅ `smooth silk fabric`
- ✅ `rough wood grain`
- ✅ `cold stone surface`
- ✅ `delicate embroidery`
- ✅ `polished brass`
- ✅ `faded wallpaper`

### Environmental Atmosphere
- ✅ `festive and joyful`
- ✅ `gloomy and oppressive`
- ✅ `peaceful and serene`
- ✅ `mysterious and eerie`
- ✅ `nostalgic and melancholic`
- ✅ `cold and desolate`

## Visual Description vs. Image-Generation Prompt

### Distinction
- **Visual description**: May mention story background, character activity, and plot developments.
- **Image-generation prompt**: Must describe only an environment, with no person or character.

### Comparison Examples

#### Example 1: Wedding Chamber

**Visual description** (may mention characters):
```
The room conveys an intensely festive yet eerie atmosphere on the wedding night. Saturated red silk and Double Happiness banners fill the room. Lu Yanli's agonized struggle has overturned the wedding wine cups and disturbed the bedding, while dragon-and-phoenix candles flicker in the wind and cast menacing long shadows.
```

**Image-generation prompt** (must contain no people):
```
Interior of a luxurious ancient Chinese wedding chamber, empty. Saturated red silk curtains and "Double Happiness" banners. Flickering dragon-and-phoenix candles casting long, dancing shadows. On the rosewood table, an overturned wine cup and scattered red dates. A large ornate canopy bed with messy red silk bedding. The atmosphere is festive yet suffocating and eerie. Cinematic lighting, 8k, hyper-realistic. --ar 16:9 --v 6.0
```

#### Example 2: Flashback Scene

**Visual description** (may mention plot):
```
In the Shen residence garden from the flashback, a stone pavilion stands beside a lotus pond under trailing willows. An elegant but empty brocade box rests on the stone table, implying that the warm jade once inside was taken by force. The sunlight is soft, with a faintly sorrowful filtered quality.
```

**Image-generation prompt** (must contain no people):
```
A serene traditional Chinese garden with a stone pavilion by a lotus pond, empty. Soft daylight filtering through weeping willow branches. On the stone table in the pavilion, a small decorative box is left open. The water is still, and the atmosphere is nostalgic and slightly melancholic. High-end ancient garden design, 8k, soft focus background. --ar 16:9 --v 6.0
```

## Standard Scene Templates

### Interior Scene Template

```
Interior of a [space type], empty.
[furniture description]
[decoration description]
[lighting description]
[material-detail description]
[atmosphere description]
[technical parameters] --ar 16:9 --v 6.0
```

**Example**:
```
Interior of a traditional Chinese study room, empty. A large desk in the center with ink stone and brushes. Bookshelves filled with ancient scrolls on both walls. A paper lamp hanging from the ceiling casting warm light. A wooden floor with tatami mats. The atmosphere is scholarly and peaceful. 8k, traditional Chinese aesthetics. --ar 16:9 --v 6.0
```

### Exterior Scene Template

```
[setting type] in [location], empty.
[natural-element description]
[architectural-element description]
[lighting description]
[atmosphere description]
[technical parameters] --ar 16:9 --v 6.0
```

**Example**:
```
A traditional Chinese courtyard in autumn, empty. Red maple leaves falling on the stone ground. A small pavilion in the center with a round table. Trees with golden leaves surrounding the courtyard. Soft afternoon sunlight casting long shadows. The atmosphere is nostalgic and peaceful. 8k, hyper-realistic foliage. --ar 16:9 --v 6.0
```

### Flashback Scene Template

```
[scene description], empty.
[temporal-filter description]
[key-object description]
[environmental-detail description]
[nostalgic-atmosphere description]
[technical parameters] --ar 16:9 --v 6.0
```

**Example**:
```
A childhood bedroom, empty. Soft nostalgic lighting with warm tones. A small wooden bed with a teddy bear. Toys scattered on the floor. A window showing a sunny day outside. The atmosphere is dreamy and full of memories. 8k, soft focus. --ar 16:9 --v 6.0
```

## Checklist

After generating a scene prompt, verify that:

- [ ] The image-generation prompt includes `empty`, `scenery only`, `no people`, or `unoccupied`.
- [ ] It contains no person terms such as man, woman, person, character, or figure.
- [ ] It contains no body parts such as face, hand, or body.
- [ ] It contains no human actions such as sitting, standing, or walking.
- [ ] It contains no clothing terms such as dress, robe, or coat.
- [ ] It contains no implied people such as silhouette or shadow of person.
- [ ] It describes the spatial structure.
- [ ] It describes furniture and decorations.
- [ ] It describes lighting and material details.
- [ ] It describes the environmental atmosphere.
- [ ] It contains technical parameters such as `8k`, `--ar 16:9`, and `--v 6.0`.

## Summary

When generating a scene prompt, remember:

1. The **visual description** may mention characters and story background.
2. The **image-generation prompt** must describe only the environment and contain no people.
3. It must include a mandatory keyword: `empty`, `scenery only`, or `no people`.
4. Describe the space, furniture, decorations, lighting, and atmosphere in detail.
5. Strictly prohibit all character-related terms.
6. Every checklist item must pass.

Following these rules produces high-quality scene prompts and ensures that AI-generated images show clean environmental settings with no characters.
