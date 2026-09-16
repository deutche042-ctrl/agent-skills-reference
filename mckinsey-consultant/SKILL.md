---
name: mckinsey-consultant
description: Guide users through a structured, step-by-step, interactive thinking process based on McKinsey methods (SCQA, MECE, and the Pyramid Principle) to create high-quality, in-depth articles. Use for topic analysis and professional writing that require deep insights and rigorous logic.
---

# McKinsey Consultant

## Objective
- Guide users through structured thinking frameworks (SCQA, MECE, and the Pyramid Principle) to create in-depth articles.
- Capabilities include:
  - SCQA framing: define the problem and distill the core thesis
  - Logic-tree decomposition: break down key issues using MECE
  - In-depth analysis and reasoning: strengthen persuasion through deductive and inductive reasoning
  - Pyramid-structured output: integrate the analysis into a logically clear article
- Trigger when the user needs a professional article with deep insight and broad coverage, or a structured analysis of a complex topic.

## Core Concepts
- **Hypothesis-driven:** State a thesis first, then seek evidence; do not list information without direction.
- **MECE:** Ensure analytical dimensions are mutually exclusive and collectively exhaustive.
- **Pyramid structure:** Lead with the conclusion and proceed top-down with clear logic.

## Workflow (Must Be Executed Step by Step)

### Step 1: Define the Problem (SCQA Framing)
1. Ask the user for the topic direction.
2. Build an SCQA frame around the topic:
   - **S (Situation):** Describe background facts broadly accepted in the field.
   - **C (Complication):** Identify current pain points, changes, or counterintuitive phenomena.
   - **Q (Question):** Distill the core question the article must answer.
   - **A (Answer / Core hypothesis):** Propose an insightful preliminary thesis based on the knowledge base.
3. Ask the user to confirm whether the SCQA frame is accurate or needs adjustment.
4. Wait for the user's confirmation before proceeding.

### Step 2: Structured Decomposition (Logic Tree & MECE)
1. After the user confirms Step 1, build an issue tree from the core thesis.
2. Use MECE to derive three to five first-level supporting arguments (key drivers), ensuring that they are:
   - Mutually exclusive
   - Collectively exhaustive with respect to the core thesis
3. For each supporting argument, briefly list the types of evidence, data, or cases to seek.
4. Ask whether the arguments are comprehensive and whether the user wants to include specific cases.
5. Wait for the user's confirmation before proceeding.

### Step 3: Deepen and Validate (Analysis & Synthesis)
1. After the user confirms Step 2, expand each supporting argument in depth.
2. Add to each argument:
   - Deep explanation (why it happens): the mechanisms and causes behind the phenomenon
   - Cases or phenomena (evidence): concrete examples, data, and citations
   - Responses or recommendations (how to act): actionable recommendations
3. Strengthen persuasion through reasoning:
   - **Deduction:** Major premise → minor premise → conclusion
   - **Induction:** Derive a general conclusion from multiple specific cases
4. Wait for the user's confirmation before proceeding.

### Step 4: Pyramid-Structured Output (Final Output)
1. Integrate all content into an in-depth article using a pyramid structure:
   - **Title:** Engaging and containing the core benefit
   - **Introduction:** A narrative SCQA opening from Step 1
   - **Body:** "Subheading + core sentence + detailed explanation"
   - **Conclusion:** Summary and recommended next actions
2. Check that the logical chain is complete, the evidence is sufficient, and the structure is clear.

## Important Rules
- **Mandatory stepwise execution:** Follow Step 1 → Step 2 → Step 3 → Step 4 strictly. After each step, wait for the user's confirmation before continuing. Generating everything at once is prohibited.
- **User-centered:** Adapt each step dynamically to the user's topic and feedback rather than applying a template mechanically.
- **Insight first:** The core hypothesis and supporting arguments must be novel and insightful; avoid generic claims.
- **Sufficient evidence:** Every claim requires support from a concrete case, data, or logical reasoning.

## Resource Index
- **SCQA framework:** [references/scqa-framework.md](references/scqa-framework.md), read when constructing SCQA in Step 1
- **MECE principle:** [references/mece-principle.md](references/mece-principle.md), read when decomposing the issue tree in Step 2
- **Pyramid Principle:** [references/pyramid-principle.md](references/pyramid-principle.md), read during deep analysis in Step 3 and output in Step 4
- **Article-structure template:** [assets/article-template.md](assets/article-template.md), read when integrating the article in Step 4

## Usage Examples

### Example 1: Business Analysis Article
- **Function:** Produce a structured, in-depth article about a business trend or industry-analysis topic.
- **Execution:** The agent guides the process entirely through natural language.
- **Key points:**
  - Step 1: Identify the industry's central tension precisely, such as challenges caused by technological change.
  - Step 2: Decompose the topic across market, technology, policy, and other MECE dimensions.
  - Step 3: Cite specific company cases and data.
  - Step 4: Produce a forward-looking analytical article.

### Example 2: Product-Thinking Framework
- **Function:** Provide structured analysis for product design or strategic planning.
- **Execution:** The agent guides the user through the four-step process.
- **Key points:**
  - Step 1: Define the user pain point or market opportunity.
  - Step 2: Decompose by user experience, technical feasibility, and business value.
  - Step 3: Analyze the underlying logic of each dimension in depth.
  - Step 4: Produce a complete product-thinking document.

## Notes
- Read a reference document only when a framework requires deeper understanding, keeping context concise.
- If the user's topic is vague, proactively guide them toward a clear direction in Step 1.
- Use the agent's knowledge base and reasoning capabilities fully; avoid mechanical template application.
- Ensure every step produces actionable, verifiable output rather than vague advice.
