# Optimize Resume

Improve the content quality of an existing resume, or tailor it for a specific position.

## Table of Contents

- [General Content Optimization](#general-content-optimization)
- [Position-Specific Tailoring](#position-specific-tailoring)
- [ATS Optimization](#ats-optimization)
- [Common Issue Fixes](#common-issue-fixes)

---

## General Content Optimization

Not aimed at a specific position; a comprehensive lift to the resume's overall quality of expression.

### Read through it first before optimizing

First read the user's entire resume content and identify the following common problems:
- Weak verbs ("responsible for", "participated in", "assisted with", etc.)
- Missing quantified metrics
- Descriptions that are too vague or too brief
- A hollow professional summary

Then improve item by item in priority order.

### Strengthening action verbs

Weak verbs are the most common problem in resumes. Replacement rules:

| Weak phrasing | Replace with |
|--------|--------|
| Responsible for... | Led / Managed / Built... |
| Participated in... | Drove / Delivered / Designed... |
| Assisted with... | Supported / Enabled / Facilitated... |
| Completed... | Delivered / Launched / Released... |
| Did... | Developed / Built / Implemented... |
| Worked on... | Built/Developed/Designed... |
| Helped with... | Enabled/Facilitated/Drove... |
| Responsible for... | Owned/Led/Managed... |
| Participated in... | Contributed to/Collaborated on... |

### Quantifying metrics

Try to include at least one quantifiable metric in every description.

**Quantification dimensions:**

| Dimension | Template | Example |
|------|------|------|
| Time/speed | Reduced X from A to B | Cut deployment time from 2 hours to 15 minutes |
| Cost/revenue | Saved/generated $X | Saved $2M in annual cloud costs through architecture optimization |
| Scale/volume | Handled/served X units/records/people | Processed 50M transactions per day on average |
| Quality/accuracy | Improved X from A% to B% | Improved model accuracy from 78% to 94% |
| Team/impact | Led X people / covered X teams | Led a team of 6 to complete a core system refactor |
| Efficiency | Automated X% / reduced X hours | Automated 85% of the manual data validation process |

**Strategies when you don't have exact numbers:**
- Rough estimates: ~5M users, roughly 30% improvement
- Baseline comparisons: 3× faster than before
- Describe scale: covering 15+ microservices
- Describe frequency: daily, real-time, on-demand

### Description rewrite examples

**Before:**
> Responsible for backend service development

**After:**
> Led the build of an order-processing microservice using Go and gRPC, supporting an average of 8M orders per day with P99 latency < 50ms

**Before:**
> Participated in training and deploying machine learning models

**After:**
> Developed an XGBoost-based credit scoring model reaching an AUC of 0.85; after launch, the bad-debt rate dropped 18%, reducing annual losses by roughly $30M

### Professional summary optimization

Checklist:
- [ ] 2-4 sentences, not one long paragraph
- [ ] Includes years of experience and seniority level
- [ ] Mentions 3-5 core skill areas
- [ ] Includes industry/domain background
- [ ] Demonstrates value rather than describing activities
- [ ] Avoids empty phrases like "strong communicator" or "fast learner"

---

## Position-Specific Tailoring

When the user has the job description (JD) for a target role, optimize the resume specifically for it.

### Step 1: Analyze the job description

Extract the following information from the JD:

1. **Hard requirements**: years of experience, must-have skills, education requirements
2. **Preferred qualifications**: bonus skills, preferred experience
3. **Core responsibilities**: day-to-day work, main deliverables
4. **Keywords**: terms that recur repeatedly (high priority), terms that appear in the title / first paragraph

### Step 2: Keyword gap analysis

Compare the resume against the JD and sort into four categories:

| Category | Meaning | How to handle |
|------|------|---------|
| **Critical gap** | You have this skill but the resume doesn't mention it | Add to the skills section immediately + weave it into descriptions |
| **Easy addition** | A skill matching a preferred qualification | Add to the skills section |
| **Inconsistent wording** | Same skill under a different name (e.g., "ML" vs "machine learning") | Standardize to the JD's wording |
| **Real gap** | A required skill you genuinely lack | Note it but do not fabricate |

**Never fabricate skills or experience you don't have.** You can adjust wording and highlight relevant experience, but you cannot make things up.

### Step 3: Tailor the content

**Professional summary tailoring:**
- Use the JD's language style
- Highlight the experience that best matches the target role
- Include the target role's title or a similar phrasing
- Showcase 2-3 of the core required skills from the JD

**Achievement description tailoring:**
- Reorder: put the most relevant achievements first
- Rewrite phrasing: weave in keywords from the JD
- Emphasize matches: highlight experience that aligns with the target responsibilities

**Skills section tailoring:**
- Put the skills required by the JD first
- Add any existing skills you had omitted
- Reorganize according to the JD's categorization logic

### Tailoring example

**JD requirement:** "Experience with distributed systems and microservice architecture; familiarity with Kubernetes and CI/CD"

**Original description:**
> Developed backend services

**After tailoring:**
> Led the design of a microservice-based order system, split into 8 independent services deployed on a Kubernetes cluster, with automated deployment via GitLab CI/CD, increasing release frequency from monthly to daily

---

## ATS Optimization

An ATS (Applicant Tracking System) is the software many companies use to screen resumes. Make sure the resume can be parsed correctly.

### ATS checklist

**Section headings:**
- [ ] Use standard headings: Work Experience, Education, Skills, Professional Summary
- [ ] Don't use creative headings like "My Journey" or "Skill Tree"

**Keywords:**
- [ ] Include the exact keywords from the JD
- [ ] Write both the abbreviation and the full form: e.g., "Natural Language Processing (NLP)"
- [ ] Have keywords appear in both the skills section and the descriptions

**Formatting:**
- [ ] A clean, clear structure
- [ ] Contact info at the top
- [ ] A consistent date format
- [ ] Work experience in reverse chronological order

### ATS scoring factors

1. **Keyword match** (~40-50%): whether the skills from the JD appear in the resume
2. **Years of experience** (~20-30%): whether date ranges are clear and meet the minimum requirement
3. **Education** (~10-20%): whether degree information is complete
4. **Job title** (~10-15%): whether it matches the target role

---

## Common Issue Fixes

### Resume too long

1. Compress experience older than 10 years into 1-2 bullets
2. Keep the strongest 3-5 descriptions per position
3. Delete duplicate achievements
4. Trim the skills section (remove outdated or basic skills)
5. Compress the summary to 2-3 sentences

### Resume too short

1. Use coaching methods to uncover more achievements (see `references/resume-coaching.md`)
2. Add a projects section
3. Expand the categories in the skills section
4. Add optional sections like certifications and language abilities

### Content doesn't match the target

1. Reorder descriptions, putting the matching ones first
2. Rewrite phrasing to weave in terminology from the target domain
3. For career changers, focus on transferable skills
4. When necessary, use coaching methods to re-uncover relevant experience
