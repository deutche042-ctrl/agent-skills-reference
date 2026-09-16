# Complete Guide to Patent Drafting

The full workflow from a technical disclosure to a complete patent application document. It includes the workflow, the methodology for drafting claims, and the methodology for drafting the specification.

## Table of Contents

- [Stage 1: Technical Disclosure Analysis](#stage-1-technical-disclosure-analysis)
- [Stage 2: Preliminary Patentability Assessment](#stage-2-preliminary-patentability-assessment)
- [Stage 3: Drafting the Claims](#stage-3-drafting-the-claims)
- [Stage 4: Drafting the Specification](#stage-4-drafting-the-specification)
- [Stage 5: Abstract and Description of Drawings](#stage-5-abstract-and-description-of-drawings)
- [Stage 6: Self-check and Delivery](#stage-6-self-check-and-delivery)

---

## Stage 1: Technical Disclosure Analysis

**Goal**: Distill the full picture of the invention from the materials the user provides.

**Core tasks**:

1. **Extract the technical problem**: What defects exist in the prior art? What problem does the present invention aim to solve? The technical problem must be specific; do not vaguely say "low efficiency"—make clear where it is low and why it is low.
2. **Extract the technical solution**: What are the key steps? What are the relationships among the components/modules? Focus on "how it is done".
3. **Extract the technical effects**: Correspond one-to-one with the technical problems—whatever problem is solved, there should be a corresponding effect.
4. **Identify the inventive points**: Which parts already exist in the prior art, and which are the innovations? The inventive points are the core of the "characterizing portion" of the later claims.
5. **Identify variant solutions**: Can the order of steps be adjusted? Can a certain module be implemented in another way? Variant solutions influence the design of the dependent claims.

**Output**: A structured invention analysis summary (technical field, technical problem, technical solution, inventive points, technical effects, variant solutions).

**Quality check**: Are the problem → solution → effect mutually consistent? Can the inventive point be stated clearly in one sentence? Are any key details missing?

---

## Stage 2: Preliminary Patentability Assessment

**Goal**: Before formal drafting, quickly judge patentability and determine the protection strategy.

**Core tasks**:

1. **Preliminary novelty judgment**: Might the core inventive point already have been disclosed? If the user provides known prior art, focus on analyzing the differences.
2. **Preliminary inventive-step judgment**: Are the distinguishing features obvious? Are there favorable arguments such as technical prejudice or lack of teaching?
3. **Protection strategy recommendation**: Recommended claim types, the essential technical features that the independent claim should contain, and the risk points for grant.

**Note**: Clearly inform the user that this is a preliminary judgment and does not replace a formal search.

---

## Stage 3: Drafting the Claims

The claims directly define the scope of protection and are the most critical stage of the entire drafting process.

### 3.1 The Independent Claim

The independent claim defines the maximum scope of protection and contains only the technical features that are indispensable to achieving the object of the invention (the essential technical features).

**Two-part structure**:

```
A [subject-matter name], comprising [known features of the preamble],
characterized in that [innovative features of the characterizing portion].
```

- **Preamble**: The subject-matter name + the essential features shared with the prior art
- **Characterizing portion**: Introduced by "characterized in that", stating the features that distinguish the present invention from the prior art

**Drafting steps**:

1. **Determine the subject-matter type**: method (step description), apparatus/system (module description), storage medium.
2. **List all technical features**, and apply the "deletion test" to each one—if it is removed, can the technical problem still be solved? A feature that can be removed is not essential; put it in a dependent claim.
3. **Divide into preamble and characterizing portion**.
4. **Generalize to a higher level (upper concept)**: Abstract the specific implementation appropriately. For example, "extract features with a convolutional neural network" is generalized to "extract features with a feature extraction model". Too specific and the scope of protection is narrow; too abstract and it may not be supported by the specification.

**Example**—comparison before and after generalization:

Before revision (too specific, narrow scope of protection):
```
1. An image recognition method, characterized in that it comprises:
   acquiring an RGB image using an 8-megapixel camera;
   scaling the said RGB image to 224×224 pixels;
   extracting a 512-dimensional feature vector using a ResNet-50 model;
   classifying the said feature vector using an SVM classifier.
```

After revision (appropriately generalized):
```
1. An image recognition method, characterized in that it comprises:
   acquiring an image to be recognized;
   performing feature extraction on the said image to be recognized to obtain image features;
   performing classification based on the said image features to obtain a recognition result.
```

Specific implementations such as ResNet-50 and SVM are placed in the dependent claims.

### 3.2 Dependent Claims

Dependent claims build layers of protection on top of the independent claim—when the independent claim is narrowed, the dependent claims can serve as fallback positions.

```
The [subject-matter name] according to claim [number], characterized in that [additional technical feature].
```

**Design principles**:

1. **Each claim limits only one dimension**, avoiding bundling two unrelated features together.
2. **Progress from broad to narrow, layer by layer**: first-layer broad-category limitation → second-layer refinement → third-layer most specific implementation.
3. **Have strategic significance**: protect commercially valuable specific implementations, or block design-around paths.
4. **Cover variant solutions**: cover multiple implementations separately with parallel dependent claims.

**Reference formats**: single reference (`the ... according to claim 1`) or multiple reference (`the ... according to claim 1 or 2`). A multiply-referring claim cannot itself be multiply referenced.

### 3.3 Multi-type Claim Structure

| Type | What it protects | Applicable scenario |
|------|---------|---------|
| Method claim | Implementation steps | Innovation in the core workflow |
| Apparatus/system claim | Functional modules | Innovation in the product form |
| Storage-medium claim | The medium carrying the program | Software-type inventions |
| Electronic-device claim | Processor + memory + program | The hardware dimension of software-type inventions |

**Basic structure**: 1 independent method claim + 5–8 dependent method claims + 1 independent apparatus claim + 3–5 dependent apparatus claims (10–15 claims in total).
**Complete structure**: add independent storage-medium and electronic-device claims (20–25 claims in total).

Apparatus claims correspond one-to-one with method claims: each step in the method corresponds to a module in the apparatus.

### 3.4 Language Conventions

| Scenario | Correct | Incorrect |
|------|------|------|
| First introduction of a technical feature | **a** data processing method / **a** processing module | ~~the said data processing method~~ (using "the said" on first mention) |
| Subsequent reference to the same feature | **the said** data processing method | ~~this data processing method~~ ("this" is less proper than "the said") |

**Language to avoid**: approximately/substantially (imprecise), preferably/best (expressing a preference), etc./such as (open-ended enumeration), efficient/excellent (subjective evaluation), when necessary/optionally (a claim feature is either present or absent).

**Connecting terms**: `comprising/including` (open-ended, recommended), `consisting of` (closed, narrow scope of protection).

### 3.5 Common Problems

1. **Too many features in the independent claim** → identify the non-essential features and move them to dependent claims.
2. **Missing antecedent basis** → check whether each "the said" can find its introduction earlier.
3. **Broken dependency chain in dependent claims** → draw the reference tree and check that the numbers correspond.
4. **Method and apparatus claims do not correspond** → check the correspondence step by step.

### 3.6 Claim Self-check Checklist

- [ ] The independent claim contains only essential technical features
- [ ] There are independent claims of at least two types, method and apparatus
- [ ] Each dependent claim limits only one dimension
- [ ] Every "the said XX" has an antecedent basis
- [ ] Use "a/an" on first introduction and "the said" thereafter
- [ ] The same feature uses consistent terminology throughout
- [ ] No vague language or subjective evaluative words
- [ ] Dependent-claim reference numbers are correct, and no multiply-referring claim is multiply referenced again
- [ ] Method steps and apparatus modules correspond one-to-one
- [ ] The total number of claims is 10–25

---

## Stage 4: Drafting the Specification

The mission of the specification is to **sufficiently disclose** the invention (so that a person skilled in the art can implement it) while **supporting** every technical feature in the claims.

### 4.1 The Five Main Parts

**I. Technical Field** (1–2 sentences)

`The present invention relates to the technical field of [field], and in particular to [sub-direction].` Do not be too broad ("computer technology") nor too narrow.

**II. Background Art** (3–5 paragraphs)

1. Describe the technical background and application scenario
2. Describe the prior-art approach (objectively and specifically)
3. Point out the deficiencies of the prior art (introduced with "however"/"but"), which must be **specific** rather than general

Negative example: `At present, image recognition technology still has some problems.`
Positive example: `Existing methods rely on training with large-scale labeled data, and in specialized fields where labels are scarce, recognition accuracy drops significantly.`

**III. Summary of the Invention** (3–5 paragraphs)

1. The technical problem to be solved (following on from the deficiencies in the background art)
2. The technical solution (the content of the independent claim in prose form)
3. The technical effects (corresponding one-to-one with the problems, quantified where possible)

**IV. Description of Drawings**

One sentence per drawing: `FIG. 1 is a schematic flow diagram of the XX provided by an embodiment of the present invention.` Figure numbers must be continuous.

**V. Detailed Description** (the longest part)

- Embodiment 1: corresponds to the independent claim, described in detail step by step / module by module, using drawing reference signs (acquisition module 110, processing unit 120)
- Embodiments 2–N: correspond to the variant solutions of the dependent claims; describe the differing parts in detail and cross-reference the identical parts
- Key steps must be given sufficient detail, avoiding "black boxes"

### 4.2 Judging Sufficient Disclosure

Thought experiment: an engineer with 3–5 years of experience in the field can implement the invention after reading it without exercising inventive effort.

Check: Are there any "black boxes" in the key steps? Are the key parameters given? Are the effects verified?

### 4.3 Correspondence Between Claims and Specification

| Claim content | Location in the specification |
|---|---|
| The technical solution of the independent claim | "Summary of the Invention" + the main embodiment |
| The additional features of the dependent claims | The detailed description or variant embodiments |
| Parameter ranges | Parameter descriptions or experimental data in the embodiments |

Key rule: The claims should not contain anything not covered at all in the specification.

### 4.4 Common Problems

1. **Inconsistent terminology** → follow the claims as the standard and make consistent revisions throughout the specification.
2. **Overly brief detailed description** → check item by item whether each technical feature is sufficiently elaborated.
3. **Disconnect between background and summary of the invention** → the summary of the invention must respond to the problems raised in the background.
4. **Lack of effect justification** → supplement with experimental comparisons, performance metrics, or theoretical analysis.

---

## Stage 5: Abstract and Description of Drawings

1. **Abstract**: within 300 characters, covering the technical problem + key points of the solution + effects. Do not begin with "the present invention"; get straight to the point.
2. **Description of drawings**: confirm that the numbering is continuous and that every drawing has a description. When delivering as plain text, provide a textual description scheme for the drawings.

---

## Stage 6: Self-check and Delivery

**Streamlined self-check checklist** (for the detailed version, see `review-checklist.md`):

**Claims**:
- [ ] The independent claim contains only essential technical features
- [ ] The dependent-claim reference relationships are correct, and each limits only one dimension
- [ ] Language is proper, with no vague words and no missing antecedent basis

**Specification**:
- [ ] All five main parts are present
- [ ] Every claim feature is described in the detailed description
- [ ] Terminology is fully consistent with the claims

**Abstract**: within 300 characters, covering the problem, solution, and effects.

**Consistency**: drawing numbers are continuous, and the terminology of the claims and the specification is consistent.

**Delivery order**: claims → specification → abstract → drawings.

**Formatted document delivery**:
- With a template: `uv run ../scripts/docx_edit.py replace template.docx output.docx replacements.json`
- Without a template: `uv run ../scripts/create_docx.py content.md output.docx --style patent`

Run `uv run ../scripts/docx_edit.py --help` or `uv run ../scripts/create_docx.py --help` to view detailed usage.
