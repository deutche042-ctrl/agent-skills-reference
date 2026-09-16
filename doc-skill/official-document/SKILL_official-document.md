---
name: official-document
description: Official-document writing skill covering three scenario types: litigation notices, legal announcements, and organizational meeting notices. Following the GB/T 9704 format standard for Party and government official documents and the Supreme People's Court's litigation-document style specifications, it produces format-compliant official documents with complete required elements. Use when the user mentions complaints, summonses, court notices, capital-reduction announcements, liquidation announcements, meeting notices, meeting minutes, and similar scenarios.
---

# Official-Document Writing Skill

Based on the user's needs, route among three categories of official documents and generate format-compliant documents.

## Routing Decision

| User-intent signal | Category | Jump to |
|---|---|---|
| Complaint, civil complaint, summons, notice to respond, notice of case acceptance, statement of defense, notice of appeal | Litigation notices | → Section 1 |
| Capital-reduction announcement, liquidation announcement, deregistration announcement, creditor announcement, public notice, newspaper announcement | Legal announcements | → Section 2 |
| Meeting notice, meeting minutes, meeting bulletin, notice to convene, work meeting | Meeting notices | → Section 3 |

## Delivery-Format Priority

1. **The user uploaded an attachment** (.docx/.doc/.pdf, etc.): Deliver in the attachment's format first, preserving the original file's layout, fonts, margins, etc., and fill in or modify content on top of the original format
2. **The user explicitly specified a format**: Deliver as the user requires
3. **Neither specified**: Generate according to the general layout specifications below

## Output Specifications

Regardless of which category is routed to, follow these output specifications by default:

1. **Delivery format**: Plain-text format, using basic Markdown structural markup for easy pasting into any text editor
2. **Content structure**:
   - **Title**: Bold, formatted as "issuing authority + regarding + subject matter + notice type," e.g., **Notice of the General Office of the People's Government of XX Province on Issuing the "Implementation Plan for Digital Government Construction of XX Province"**
   - **Primary recipient**: Written flush-left below the title, followed by a colon, e.g., `To the People's Government of XX City:`
   - **Body**: First line indented two characters, one blank line between paragraphs, hierarchical ordinals uniformly using "一、", "（一）", "1.", "（1）"
   - **Closing**: Use a standard closing phrase appropriate to the document type, such as "特此通知" (This notice is hereby given) or "妥否，请批示" (Please advise whether this is appropriate)
   - **Signature block and date**: Mark the issuing authority and the date of completion at the lower right; write the date in Chinese characters
3. **Language standard**: Zero colloquialism, precise expression, political compliance, exact word choice
4. **Placeholder usage**: Mark personalized information with clear placeholders, such as `[To fill in: name of the responsible person]` or `XX`

## General Layout Specifications (GB/T 9704-2012)

When the user provides no template and specifies no format, follow these specifications by default:

- **Paper**: A4
- **Margins**: top 3.7 cm, bottom 3.5 cm, left 2.8 cm, right 2.6 cm
- **Title**: FZ Xiaobiao-Song (方正小标宋体), size 2 (二号), centered
- **Body**: Fangsong (仿宋, imitation Song), size 3 (三号), 22 lines per page, 28 characters per line
- **Hierarchical levels**: level 1 "一、" (Heiti / 黑体, boldface) → level 2 "（一）" (Kaiti / 楷体, regular script) → level 3 "1." (Fangsong / 仿宋) → level 4 "（1）" (Fangsong / 仿宋)
- **Document serial number**: Use the hexagonal brackets 〔〕 for the year
- **Date of completion**: Use Arabic numerals, arranged with four spaces to the right
- **Seal**: Two blank lines between the seal and the body

---

## 1. Litigation Notices

Based on the Supreme People's Court's "Formats of Civil Litigation Documents" and "Specifications for Preparing People's Court Civil Adjudication Documents."

### 1.1 Document Types and Required Elements

| Document | Core elements |
|---|---|
| **Civil complaint** | Plaintiff information, defendant information, claims for relief (itemized), facts and reasons, list of evidence, court of submission, signature and date, number of copies |
| **Statement of defense** | Respondent information, original case number, item-by-item defense to the claims, facts and reasons, evidence, signature and date |
| **Notice of appeal** | Appellant/appellee information, court of first instance/case number/judgment date, appeal requests, grounds of appeal, court of submission |
| **Notice of case acceptance** | Case number, plaintiff information, opposing party and cause of action, decision to accept the case, notice of rights and obligations, prepaid fees |
| **Notice to respond** | Case number, defendant information, plaintiff and cause of action, defense deadline, evidence-submission deadline, notice of rights and obligations |

### 1.2 Civil Complaint Template

```
CIVIL COMPLAINT

Plaintiff: [Name/Entity name], [Gender], [Ethnicity], [Date of birth],
      Domicile: [Address], Contact phone: [Phone].
      (For a legal person, write: name, domicile, legal representative and title, unified social credit code)

Defendant: [Name/Entity name], [Gender], [Ethnicity], [Date of birth],
      Domicile: [Address], Contact phone: [Phone].

Claims for Relief:
1. [Specific claim, e.g., order the defendant to pay goods payment of RMB XX and interest];
2. [Second claim];
3. The litigation costs of this case shall be borne by the defendant.

Facts and Reasons:
[Objectively state the time, place, course, outcome, and focus of the dispute, citing the relevant legal basis]

List of Evidence:
1. [Name of evidence]—to prove [fact to be proven]
2. [Name of evidence]—to prove [fact to be proven]

Respectfully submitted to
[Full name of the court]

                                    Plaintiff: [Signature/Seal]
                                    [Year] Year [Month] Month [Day] Day

Attached: [X] copies of this complaint
```

### 1.3 Drafting Rules

- **Claims for relief** must be quantified into specific amounts or explicit actions; they may not be vague
- **Facts and reasons** are organized along a timeline, covering the "six Ws": who, when, where, what, why, and with what result
- **Legal basis**: When citing provisions, write the full name of the law + article number, e.g., "pursuant to Article 577 of the Civil Code of the People's Republic of China"
- **Party information** must be accurate and complete; a natural person must include the ID card number (if known), and a legal person must include the unified social credit code
- Number of copies = number of defendants

### 1.4 Reference Templates (read when needed)

Detailed collection of litigation-document templates: `references/litigation-templates.md`

---

## 2. Legal Announcements

Based on the "Company Law," the "Regulations on the Administration of Company Registration," and other laws and regulations.

### 2.1 Announcement Types and Required Elements

| Announcement | Core elements | Statutory requirements |
|---|---|---|
| **Capital-reduction announcement** | Company name, credit code, original registered capital, capital after reduction, reason for reduction, notice of creditors' rights | Notify creditors within 10 days after the shareholders' resolution and publish in a newspaper within 30 days; creditors may file claims within 45 days from the announcement |
| **Liquidation announcement** | Company name, liquidation-group information, reason for liquidation, deadline for filing claims, contact information | Notify creditors within 10 days after the liquidation group is formed and publish in a newspaper within 60 days; the filing period shall be no less than 45 days |
| **Deregistration announcement** | Company name, credit code, reason for deregistration, declaration of debt settlement | Apply for deregistration within 30 days after liquidation is completed |
| **Creditor announcement** | Case number, debtor information, filing deadline, filing method, consequences of late filing | Notify known creditors within 25 days after the court accepts the bankruptcy petition, and publish an announcement at the same time |

### 2.2 Capital-Reduction Announcement Template

```
ANNOUNCEMENT OF REDUCTION OF REGISTERED CAPITAL

[Full company name] (Unified social credit code: [Code]), by resolution of
the shareholders' meeting, intends to reduce its registered capital from
RMB [original amount] ten-thousand to RMB [new amount] ten-thousand.

Reason for reduction: [brief explanation]

Pursuant to Article 224 of the Company Law of the People's Republic of China,
all creditors are requested, within forty-five days from the date of this
announcement, to file their claims with the Company or to request that
corresponding security be provided.

Contact address: [Address]
Contact phone: [Phone]
Contact person: [Name]

This announcement is hereby given.

                            [Full company name] (Seal)
                            [Year] Year [Month] Month [Day] Day
```

### 2.3 Liquidation Announcement Template

```
LIQUIDATION ANNOUNCEMENT

[Full company name] (Unified social credit code: [Code]) has resolved by the
shareholders' meeting to dissolve, and has lawfully established a liquidation
group composed of [member names].

Creditors of the Company are requested to file their claims with the
liquidation group within forty-five days from the date of this announcement.

When filing a claim, a creditor shall provide:
1. The creditor's name or personal name, and contact information
2. The amount of the claim and the time it arose
3. Whether there is security and the security details
4. Relevant supporting materials

Failure to file within the time limit shall be deemed a waiver of the relevant
rights, and the liquidation group will distribute repayment based on the claims
that have been filed.

Liquidation-group contact information:
Address: [Address]
Phone: [Phone]
Email: [Email]

This announcement is hereby given.

                            [Full company name] Liquidation Group
                            [Year] Year [Month] Month [Day] Day
```

### 2.4 Drafting Rules

- The announcement must be published in a **provincial-level or higher publicly circulated newspaper** or on the **National Enterprise Credit Information Publicity System**
- Statutory time limits must be marked strictly (45 days / 60 days, etc.) and may not be shortened
- Must include the notice of creditors' rights and the filing method
- Company information must be consistent with the business registration (full name, credit code)
- For multiple announcements, the time limit is calculated from the **date of the first announcement**

---

## 3. Meeting Notices

Based on GB/T 9704-2012 "Format for Official Documents of Party and Government Organs" and general official-document writing conventions.

### 3.1 Document Types and Required Elements

| Document | Core elements |
|---|---|
| **Meeting notice** | Issuing authority, document serial number, meeting name/agenda, time, place, scope of attendees, matters to prepare, contact information, signature date |
| **Meeting minutes** | Meeting name, time and place, chairperson, attendees, non-voting participants, matters resolved (itemized), signature block |
| **Meeting bulletin (public notice)** | Bulletin title, meeting purpose, time and place, target audience, points for attention, issuing organization, date |

### 3.2 Meeting Notice Template

```
[Name of issuing authority] Document
[Authority abbreviation]〔[Year]〕[Serial No.] Hao

Notice on Convening the [Meeting Name]

[Primary recipient/attending unit]:

    Upon deliberation, it has been decided to convene the [Meeting Name]
at [Time]. The relevant matters are hereby notified as follows:

    1. Meeting Agenda
    [Agenda content]

    2. Attendees
    [Specify the scope of attendees and specific requirements]

    3. Meeting Time
    [Specific date and time period], [check-in time] (if applicable)

    4. Meeting Place
    [Detailed address and name of the meeting room]

    5. Relevant Matters
    (1) Attendees are requested to prepare [materials/speaking outline, etc.] in advance.
    (2) Please submit the attendance reply to [department] by [deadline].
    (3) [Other matters, such as accommodation, transportation, and other arrangements]

    Contact person: [Name]    Phone: [Phone]

                                    [Name of issuing authority]
                                    [Year] Year [Month] Month [Day] Day
```

### 3.3 Meeting Minutes Template

```
Minutes of the [Meeting Name]

On [Time], [chairperson's title and name] chaired the [Meeting Name] at [Place].
[Attendees] and [non-voting participants] took part in the meeting.
The meeting heard [content reported], and after discussion and study, the
following minutes were formed:

1. Regarding [Agenda Item 1]
    The meeting held that [content of the resolution].
    The meeting decided that [specific action/division of responsibilities/timeline].

2. Regarding [Agenda Item 2]
    The meeting pointed out that [content of the resolution].
    The meeting required that [specific action/division of responsibilities/timeline].

3. [Other matters resolved]

                                    [Name of organization]
                                    [Year] Year [Month] Month [Day] Day

(Attendees: [list one by one])
(Non-voting participants: [list one by one])
```

### 3.4 Drafting Rules

- A notice must achieve the "five clarities": **time, place, personnel, agenda, and requirements**—none may be missing
- The resolved matters in the minutes must be assigned to a **responsible person, action item, and timeline**
- Document serial number format: `[Authority abbreviation]〔[Year]〕[Serial No.] Hao`, with the year in hexagonal brackets
- The primary recipient is written flush-left; carbon-copy recipients are marked in the reference section (版记)
- Notices for urgent meetings should indicate the level of urgency (特急 extra-urgent / 加急 urgent)

---

## Toolbox

### Script Index

The official-document sub-skill reuses the general scripts under `../scripts/`:

| Script | Purpose |
|------|------|
| `../scripts/docx_edit.py` | Word unpack/repack/replace. When the user uploads a .docx attachment, use replace mode to modify content in the original file while preserving formatting |
| `../scripts/create_docx.py` | Markdown → .docx generator. After the model outputs the official-document Markdown text, use `--style official` to generate it (GB/T 9704: Fangsong size 3, Heiti size 2, official-document margins) |
| `../scripts/code_formula.py` | Library for inserting code blocks and formulas (rarely used in official-document scenarios; may be needed only in technical reports) |

### Workflow

1. **The user uploaded a .docx/.pdf attachment** → view the file content → use `docx_edit.py replace` to modify the original file
2. **The user asks to generate from scratch** → output the official-document content as Markdown text, and run `create_docx.py content.md output.docx --style official` to generate a .docx in official-document format
3. **The user only needs text** → output plain text directly according to the template

### Reference-Document Index

| File | When to read | Content |
|------|---------|------|
| `references/litigation-templates.md` | When generating litigation documents | Complete templates and required elements for the statement of defense, notice of appeal, application for property preservation, objection to enforcement, and other litigation documents |
| `../references/docx-editing-guide.md` | When editing a user-uploaded .docx attachment | End-to-end guide: unpack → edit XML → repack |
| `../references/docx-creation-guide.md` | When creating a .docx from scratch with `create_docx.py` | Markdown → docx guide: styles (incl. `--style official`), supported Markdown elements, images, formulas |

---

## Pre-Delivery Self-Check

- **Elements complete**: Against the corresponding template, no core element is missing
- **Legally accurate**: The cited legal provisions and statutory time limits are consistent with current law
- **Format-compliant**: The layout conforms to GB/T 9704 or the court's document style requirements
- **Information consistent**: Party/company information is consistent throughout, with no contradictions
- **Wording rigorous**: The wording of legal documents is standard, with no colloquial expressions
