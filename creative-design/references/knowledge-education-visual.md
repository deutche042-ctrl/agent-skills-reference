# Knowledge And Education Visual Prompt Rewriting

## Main Skill Routing Fit

Use this reference for knowledge posters, educational graphics, teaching diagrams, textbook illustrations, courseware images, mind maps, knowledge graphs, flowcharts, logic diagrams, scientific structures, data charts, engineering drawings, time-space evolution diagrams, formula derivation visuals, force analysis diagrams, circuit diagrams, receipt/voucher teaching visuals, UI teaching diagrams, and knowledge-graphic correction/redraw/optimization.

## Product Skill Boundary

This reference creates educational visuals and diagram prompts. It does not guarantee scientific correctness beyond user-provided content; when facts, values, formulas, or data matter, use the user's provided information and do not invent.

## Overview

Knowledge visuals prioritize clarity, structure, hierarchy, and correctness. A beautiful style cannot replace accurate relationships, labels, and steps.

## Use Cases

- Mind map or knowledge graph.
- Process flowchart.
- Scientific structure diagram.
- Data visualization.
- Engineering drawing or architectural plan concept.
- Time-space evolution diagram.
- Formula derivation or calculation visualization.
- Teaching poster.
- Textbook/courseware illustration.
- Existing knowledge image correction, cleanup, or redraw.

## Core Workflow

1. Identify knowledge type: relationship, process, structure, data, engineering, time evolution, UI/voucher, cultural knowledge, calculation, poster, or teaching illustration.
2. Identify required factual content, labels, values, formulas, and sequence.
3. If the user provides a source image, decide whether to redraw, correct, simplify, or restyle it. Use `image_edit` when layout/content consistency is needed.
4. Choose a structure: tree, matrix, timeline, flow, layered diagram, exploded view, chart, annotated illustration, or poster.
5. Write prompt with clear layout, label style, hierarchy, and accuracy constraints.

## General Execution Core

Prioritize correctness and readability. Use clean line work, organized spacing, consistent arrows, restrained colors, and legible labels. Avoid decorative clutter that weakens teaching.

## Input

Useful inputs:

- Topic and target audience.
- Exact knowledge points, labels, values, formulas, or data.
- Desired diagram type.
- Source image for editing/redraw.
- Language of visible text.
- Required output ratio or platform.

Ask when factual content is missing and cannot be inferred safely.

## Output Forms

- Single educational poster.
- Mind map.
- Knowledge graph.
- Flowchart.
- Scientific structure diagram.
- Data chart.
- Engineering or floor-plan concept.
- Timeline/evolution diagram.
- Formula derivation visualization.
- Courseware illustration.
- Redrawn or cleaned source diagram.

## Tools And Scripts

Use `image_gen` for new diagrams without a source. Use `image_edit` for redraw, correction, cleanup, style transfer, or any task based on an uploaded diagram.

## Prompt Rewrite Standards

### Basic Rules

Specify diagram structure, hierarchy, visual language, label placement, arrow direction, and reading order. Keep the prompt concrete and avoid generic "make it clear" without structural detail.

### Text Rules

Visible text must be exact, short, and renderable. For dense topics, use representative labels or ask for source content. Do not invent equations, values, citations, dates, or technical terms.

### Parameters Forbidden In Prompt

Do not write tool fields, ratios, file paths, model names, or internal route labels inside the prompt.

### Abstract-Term Translation

- Clear: large labels, consistent spacing, simple hierarchy.
- Professional: precise line work, restrained palette, standardized icons.
- Child-friendly: warm colors, simple shapes, friendly illustrations, fewer labels.
- Academic: clean grid, exact labels, muted colors, minimal decoration.

### Professionalization Strategy

Use domain-appropriate notation, line types, arrows, callouts, legends, axes, scales, layers, or exploded views. Use only content supplied or safely known.

### Diversity Strategy

Alternative versions may vary by structure, layout, color scheme, and illustration level, not by changing facts.

## Subscene Standards

### 3.1 Logic And Relationship Diagrams

Use trees, matrices, Venn diagrams, node-link graphs, or flow arrows. Keep relationships explicit and avoid tangled lines.

### 3.2 Structure And Scientific Diagrams

Use layered cross-sections, exploded views, labels, and callout lines. Preserve anatomical, mechanical, chemical, or physical plausibility.

### 3.3 Data Visualization Charts

Use chart types appropriate to the data. Do not invent data points. If data is not provided, create a template-like structure without fake values.

### 3.4 Engineering Drawings And Architectural Floor Plans

Use clean technical linework, dimensions only when supplied, clear zones, and plausible geometry. Do not claim construction-ready accuracy.

### 3.5 Time-Space Evolution Diagrams

Use timelines, sequential panels, arrows, stages, and consistent labels. Keep chronological order unambiguous.

### 3.6 Enterprise UI And Receipt/Voucher Teaching Diagrams

Use simplified UI frames, numbered callouts, and anonymized sample fields. Do not include real personal or financial data.

### 3.7 Daily Knowledge And Art/Culture Diagrams

Use approachable illustration and organized labels. Avoid excessive academic density for general audiences.

### 3.8 Science Calculation Visualizations

Show given formulas, variables, steps, and relationships. Do not invent missing derivations.

### 3.9 Knowledge Posters

Combine a clear title, sectional hierarchy, icons/illustrations, and concise knowledge blocks. Keep poster text readable.

### 3.10 Textbook Illustrations And Courseware Images

Use pedagogical clarity, simple scenes, age-appropriate style, and labels that support teaching rather than decoration.

## Image Editing Standards

For source-image edits, specify what to preserve: structure, content, labels, order, or style. Specify what to change: cleanup, correction, redraw, color, layout, readability, or language. Use `image_edit`.

## Video Standards

If asked to plan video educational visuals, provide storyboard-like frames or key visual prompts. Do not generate video unless a video tool is available.

## Reference Cases

### Case 1: English Grammar Mind Map

Use a central topic, branches for tense/part of speech/sentence structure, short examples, and balanced spacing.

### Case 2: Enterprise Leave Request Flowchart

Use start/end nodes, decision branches, approval roles, and clear arrow direction.

### Case 3: Line Chart Of Temperature Effect On Enzyme Activity

Use provided data or a schematic curve only if no exact values are required. Label axes and trend clearly.

## Final Check

Verify factual content, label readability, relationship correctness, chart/diagram type, ratio, and whether any unsupported values or claims were invented.
