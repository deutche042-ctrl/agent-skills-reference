# Resume Coaching

Help the user uncover hidden achievements and expand thin content through conversation.

## Table of Contents

- [When to Start Coaching](#when-to-start-coaching)
- [Conversation Principles](#conversation-principles)
- [The STAR Questioning Method](#the-star-questioning-method)
- [Guiding-Question Bank](#guiding-question-bank)
- [Metric Estimation Techniques](#metric-estimation-techniques)
- [Turning Discoveries into Descriptions](#turning-discoveries-into-descriptions)

---

## When to Start Coaching

The following signals indicate the user needs coaching rather than direct optimization:

- The user says "I don't know what to write", "there's nothing worth writing", "my work isn't anything special"
- Fewer than 3 achievement descriptions per position
- Descriptions that are extremely short and vague (e.g., "responsible for backend development")
- The user says "help me think of what else I could write"

Coaching can also be started locally within other workflows — for example, if you find during an optimization workflow that a particular position's content is especially weak, run a short round of coaching just for that position.

---

## Conversation Principles

### Ask only one question at a time

Don't rattle off 5 questions at once. Ask just one each time, wait for the answer, then decide on the next one.

### Start from impact

Don't start with "what were your responsibilities" — that only gets you "responsible for XXX". Start from impact:

> "In this job, what's the most valuable thing you did?"

### Follow the leads

The user's answers often hide leads worth digging into. If the user mentions "oh right, we also built an internal tool back then", don't ignore it — follow up.

### Don't interrogate

Keep the tone natural, like coworkers chatting in the break room, not like an interviewer grilling a candidate.

> "That project sounds pretty challenging — how did it turn out in the end?"

### Affirm at the right moments

When the user shares good material, tell them:

> "That's great — that's exactly the kind of achievement that belongs on a resume. Let me help you polish the wording."

---

## The STAR Questioning Method

When the user gives a vague description, use the STAR framework to expand it.

### Framework

| Dimension | What to ask | What you're trying to get |
|------|--------|-------------|
| **S**ituation | What was the background? What problem came up? | Context and challenge |
| **T**ask | What specifically were you responsible for? | Role and scope |
| **A**ction | What specifically did you do? What methods did you use? | Technical details and approach |
| **R**esult | What was the outcome? Do you have data? | Quantified results |

### Example conversation

The user says:
> "I optimized database performance"

**S — probe the situation:**
> "What was wrong with the database at the time? Were queries slow, or couldn't it handle the concurrency?"

User: "Queries were very slow — a few endpoints took 2-3 seconds to respond"

**T — probe the task:**
> "Did you handle the investigation alone, or was it a team effort?"

User: "I was mainly responsible; the DBA helped take a look occasionally"

**A — probe the action:**
> "What optimizations did you do specifically? Adding indexes, rewriting SQL, adding caching?"

User: "Mainly added composite indexes, rewrote a few N+1 queries, and added a Redis cache for hot data"

**R — probe the result:**
> "How far did the response time drop after the optimization? Roughly how many endpoints were affected?"

User: "The slowest endpoint dropped from 3 seconds to 200 ms, and I optimized a dozen or so endpoints in total"

**Turn it into a description:**
> Led performance optimization of core endpoints through composite indexes, N+1 query elimination, and a Redis caching strategy, reducing the slowest endpoint's response time from 3 seconds to 200 ms across 10+ high-frequency endpoints

---

## Guiding-Question Bank

Choose questions that fit the user's situation. Don't ask them all — pick the ones most likely to produce good material.

### Impact (first choice)

- "What's the most impactful thing you did in this role?"
- "If you weren't on this team, what would fail to get done or turn out much worse?"
- "Is there any project you're particularly proud of?"
- "What do your manager or colleagues recognize you most for?"

### Scale

- "Roughly how many users / how much data / how many QPS does the system you own handle?"
- "How big is the team? Have you managed people?"
- "Roughly how much budget or resources went into this project?"

### Problem-solving

- "What's the trickiest technical problem you've faced? How did you solve it?"
- "Is there a project others thought couldn't be done at first, but you pulled it off?"
- "Have you ever spotted and solved a problem no one else noticed?"

### Improvement

- "Have you improved any process, tool, or system? What was the effect?"
- "Have you automated any manual work?"
- "Have you made a suggestion that the team adopted?"

### Leadership

- "Have you mentored newcomers or given tech talks?"
- "Do you have experience coordinating across teams?"
- "Have you driven any technology-selection or architecture decision?"

### Tailoring by industry

**Extra questions for technical roles:**
- System scale, production impact, architecture decisions, performance metrics

**Extra questions for product/operations roles:**
- Conversion rate, user growth, retention data, A/B test results

**Extra questions for management roles:**
- Changes in team size, talent-development outcomes, business-metric attainment

---

## Metric Estimation Techniques

Users often say "I don't remember the exact numbers." Use the following techniques to help them estimate:

### Order-of-magnitude estimation

> "Was it roughly hundreds, thousands, or tens of thousands?"

Even a rough number beats none. Phrasing: ~5M users, roughly 30% improvement, 100K+

### Comparative estimation

> "Compared to before, roughly how many times faster / how much did it save?"

Phrasing: 3× faster than before, efficiency up ~50%

### Scale description

> "Roughly how many downstream services does the system you own connect to? How many business lines does it cover?"

Phrasing: covering 15+ microservices, supporting 3 core business lines

### Time description

> "How long did this project take to complete? Was it faster or slower than expected?"

Phrasing: delivered 2 weeks early, built from 0 to 1 within 3 months

### When there really are no numbers

Use qualitative descriptions:
- "Became the team's standard practice"
- "Reused by multiple teams across the company"
- "Praised by the CTO at an all-hands meeting"

---

## Turning Discoveries into Descriptions

After uncovering good material during coaching, immediately turn it into a resume description and have the user confirm.

### Conversion workflow

1. **Draft on the spot**: as soon as the user finishes describing an achievement, write a description right away
2. **Read it back to confirm**: "Here's how I've phrased it — 'Led the build of a real-time risk-control system...' — is that accurate? Anything you'd adjust?"
3. **Adjust the wording**: revise based on the user's feedback
4. **Mark the status**: mark confirmed ones as done, and ones needing adjustment as drafts

### Conversion template

```
[strong action verb] + [what you did] + [technology/method details] + [quantified result]
```

**Input (the user's own words):**
> "I built a tool that auto-generates test data — before, everyone hand-wrote mock data, which was slow"

**Output (resume description):**
> Developed an automated test-data generation tool that replaced the manual mock process, cutting test-preparation time from 2 hours to 5 minutes, adopted by the entire team

### Common conversions

| The user's own words | Resume description |
|---------|---------|
| "I fixed a lot of bugs" | Led stability governance of core modules, reducing the production incident rate by 60% in Q3 |
| "I mentored 3 interns" | Mentored 3 interns from onboarding to independently owning modules, 2 of whom converted to full-time |
| "I set up some monitoring" | Built a full-stack monitoring system on Prometheus + Grafana, covering 20+ core services and cutting MTTR from 30 minutes to 5 minutes |
| "I refactored a legacy system" | Led a legacy-system refactor, migrating 100K lines of PHP to a Go microservice architecture, improving performance 4× and reducing maintenance cost by 50% |
