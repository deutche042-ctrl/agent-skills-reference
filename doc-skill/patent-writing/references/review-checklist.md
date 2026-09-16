# Patent Application Document Review Checklist

Perform a systematic quality check on a completed patent application document. Review results are classified by three severity levels to help quickly locate and prioritize the key problems.

---

## Problem Severity Levels

| Level | Meaning | Handling priority |
|---|---|---|
| **Critical** | Directly leads to rejection or a serious defect in the scope of rights; must be fixed before filing | Fix immediately |
| **Important** | May lead to an Office Action or weaken the protective effect; strongly recommended to fix | Fix as a priority |
| **Improvement** | Does not affect grant but can improve document quality; decide based on available time and effort | Fix when there is capacity |

During review, annotate each identified problem with its level, and when amending, handle them in the order "Critical → Important → Improvement".

---

## I. Claims Review

### 1.1 Clarity Check

Do the claims clearly define the scope of protection?

| Check item | Level | Description |
|---|---|---|
| Any vague qualifiers | Critical | Check whether it contains words such as "approximately", "substantially", "appropriately", or "approximate", unless a definite criterion for judgment is given |
| Any subjective evaluative words | Critical | Check whether it contains words with no objective standard such as "efficient", "high-quality", "good", "best", or "sufficient" |
| Any relative terms | Important | Check whether it contains words with no comparison baseline such as "larger", "smaller", "higher", or "lower" |
| Are the technical features specific | Important | Does each technical feature have a definite technical meaning, rather than a vague functional description? |
| Is the subject-matter name appropriate | Improvement | Does the subject-matter name accurately reflect the technical solution the claim protects? |

**Quick-reference table of vague language** (be alert when the following words appear in claims):

> approximately, about, substantially, in essence, roughly, approximate, appropriate, suitable, fitting, sufficient, when necessary, optionally, preferred, preferably, better, more preferable, and so on, such as, for example, efficient, excellent, advanced, good, remarkable, obvious

### 1.2 Antecedent-Basis Consistency Check

Can every "the said" reference find its antecedent basis?

| Check item | Level | Description |
|---|---|---|
| Does every "the said XX" have an antecedent basis | Critical | Check item by item: for the term after each "the said", was it introduced earlier with "a/an" in a preceding claim? |
| Is the terminology consistent throughout | Critical | Is the name of the same technical feature identical across different claims? You cannot write "processing module" in one place and "processing unit" in another |
| Is "a/an" used on first introduction | Important | Does the first appearance of each technical feature use the correct introduction format? |

**Check method**: For each claim, extract all "the said XX" references, and look up the corresponding introduction one by one in that claim and along its reference chain.

### 1.3 Claim-Structure Check

Is the structure of the claim system reasonable?

| Check item | Level | Description |
|---|---|---|
| Does the independent claim contain only essential technical features | Important | Are there non-essential features in the independent claim that could be moved to dependent claims? Too many features in the independent claim make the scope of protection too narrow |
| Are the dependent-claim reference relationships correct | Critical | Do the numbers referenced by the dependent claims point to the correct claims? Is the reference chain logically self-consistent? |
| Does each dependent claim limit only one dimension | Important | Does a single dependent claim limit two unrelated features at the same time? |
| Is a multiply-referring claim multiply referenced again | Critical | A multiply-referring dependent claim cannot be multiply referenced again |
| Do the method claims and apparatus claims correspond | Important | Do the method steps and apparatus modules correspond one-to-one? |
| Is the total number of claims reasonable | Improvement | Usually 10–25 claims is appropriate |

### 1.4 Scope-of-Protection Check

| Check item | Level | Description |
|---|---|---|
| Is the scope of the independent claim broad enough | Important | Are there unnecessary limitations that narrow the scope of protection? |
| Do the dependent claims cover the main variants | Important | Are the alternative implementations of the core technical features covered by dependent claims? |
| Are there multiple types of claims | Improvement | Does it include both method and apparatus claims? For software-type inventions, does it include storage-medium claims? |

---

## II. Specification Review

### 2.1 Sufficient-Disclosure Check

| Check item | Level | Description |
|---|---|---|
| Is every feature in the claims described | Critical | Compare item by item: is every technical feature in the claims described in detail in the specification? |
| Do the key steps have specific implementations | Critical | Are there any "black boxes"—stating only what is done but not how? |
| Are the key parameters given | Important | When thresholds, ratios, ranges, and other parameters are involved, are specific values or the basis for choosing them given? |
| Can a person skilled in the art implement it | Important | Overall judgment: after reading the specification, can an experienced engineer implement the invention without exercising inventive effort? |

### 2.2 Support Check

| Check item | Level | Description |
|---|---|---|
| Is the independent claim's solution summarized in "Summary of the Invention" | Important | Does the technical-solution description in the "Summary of the Invention" cover the core content of the independent claim? |
| Are the additional features of the dependent claims reflected in the embodiments | Important | Is each dependent claim's additional feature described in detail in at least one embodiment? |
| Do the upper concepts have lower-level support | Important | When the independent claim uses an upper concept (e.g., "classification model"), does the specification give specific lower-level instances (e.g., "SVM, random forest, neural network")? |

### 2.3 Structural-Completeness Check

| Check item | Level | Description |
|---|---|---|
| Are all five main parts present | Critical | Technical Field, Background Art, Summary of the Invention, Description of Drawings, Detailed Description |
| Is the technical-problem → solution → effect logic chain complete | Important | Deficiency in the background art → solution in the summary of the invention → technical effect: are the three tightly interlinked? |
| Are the references in the description of drawings consistent with those in the detailed description | Important | Is every drawing listed in the description of drawings referenced in the detailed description? Check the reverse as well |

### 2.4 Terminology-Consistency Check

| Check item | Level | Description |
|---|---|---|
| Is the terminology consistent between the specification and the claims | Critical | Does the same technical feature use exactly the same terminology in both documents? |
| Is the terminology consistent within the specification | Important | Does the same concept use the same name in different parts of the specification? |
| Are the drawing reference signs consistent | Improvement | Is the reference sign for the same component uniform throughout the text? |

---

## III. Abstract Review

| Check item | Level | Description |
|---|---|---|
| Is the character count compliant | Important | Usually kept within 300 characters |
| Does it cover the three elements | Important | Technical problem (or technical field) + key points of the technical solution + main use or effect |
| Is it independently readable | Improvement | Independent of the specification, can the reader understand the gist of the invention from the abstract alone? |
| Does it contain improper content | Improvement | The abstract should not contain commercial-promotional language |

---

## IV. Formalities Review

| Check item | Level | Description |
|---|---|---|
| Is the claim numbering continuous | Critical | Numbered continuously starting from 1, with no skipped numbers |
| Do the dependent-claim reference numbers exist | Critical | Does the referenced claim number point to an item that actually exists? |
| Is the drawing numbering continuous | Important | FIG. 1, FIG. 2, FIG. 3... with no skipped numbers |
| Are the section headings of the specification proper | Improvement | Use the standard section-heading names |

---

## Review Output Format

After completing the review, output the review report in the following format:

```
## Review Report

### Critical Problems (X items)
1. [Location] Problem description → Suggested amendment
2. ...

### Important Problems (X items)
1. [Location] Problem description → Suggested amendment
2. ...

### Improvement Suggestions (X items)
1. [Location] Problem description → Suggested amendment
2. ...

### Overall Assessment
[A brief assessment of the overall quality of the document, plus the recommended priority for amendments]
```

Here "Location" is annotated as: Claim X / Specification-Technical Field / Specification-Background Art / Specification-Summary of the Invention / Specification-Detailed Description / Abstract, etc.

If the user requests it, after giving the review report you may directly output the complete amended document.

If the user provides a .docx file, use the replace mode to amend it directly while preserving the format:

```bash
uv run ../scripts/docx_edit.py replace original.docx amended.docx replacements.json
```

Setting `"track_changes": true` allows changes to be marked with revision marks. Run `uv run ../scripts/docx_edit.py --help` to view detailed usage.
