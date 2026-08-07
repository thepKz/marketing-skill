# Claims and Proof Ledger

## Contents

- What this unit decides
- The question this file used to ask, and why it was the wrong one
- Five ways a claim fails, and only one is about evidence
- The filing is the benchmark, not the truth
- Two prohibitions that are image-generation constraints
- The words a statute dictates
- Where a craft gate became a legal one
- What the ledger has to carry now
- The audit divides in two, and neither half covers for the other
- What over-reports, deliberately
- Fines stack, and the arithmetic is not decorative
- Four sectors this unit refuses rather than half-covers
- What the deliverable has to contain
- What this unit cannot establish
- Working outside Vietnam
- The handoff
- Rights and claims

## What this unit decides

Whether a claim can appear in public copy, and what has to exist before it does. It runs before any
generation prompt, ad, listing, PR line, creator brief or sales deck carrying a factual assertion.

The instrument is `scripts/check_claims.py`. The forty-one rows it reads sit in
`data/claim-evidence.csv`, each cited to Nghị định 87/2026/NĐ-CP at its gazette URL, and the wider
advertising duties sit in `data/vn-advertising-law.csv`.

```
python scripts/check_claims.py --families
python scripts/check_claims.py --template answers.csv --sector cosmetics
python scripts/check_claims.py --audit draft.md --sector cosmetics --answers answers.csv
```

Exit 2 means a gate failed. Exit 0 means nothing mechanical is left, which is not the same as
cleared.

## The question this file used to ask, and why it was the wrong one

Thirty-three lines, a nine-column table, three links to ftc.gov, and a closing sentence telling the
reader to check their own market. It taught the substantiation question: do you hold evidence for
what you said. Then it handed the Vietnamese instrument back to a Vietnamese marketer.

The substantiation question is real here. It is not the expensive one, and it is not the first one an
inspector asks.

## Five ways a claim fails, and only one is about evidence

| verdict | what it means | rows | worst band |
|---|---|---|---|
| `prohibited_outright` | The category, imagery or form of words is closed. No document opens it. | 10 | 70,000,000 |
| `needs_document` | The substantiation question. Hold lawful proof, from whoever may issue it. | 7 | 60,000,000 |
| `must_match_filing` | The claim may not exceed the product's own registration or declaration. | 7 | 100,000,000 |
| `mandatory_wording` | A statute dictates the words. Paraphrase is the violation. | 10 | 20,000,000 |
| `form_prescribed` | The layout is regulated: contrast, relative type size, reading speed. | 7 | 40,000,000 |

Two of those five have no analogue in the substantiation model, and one of them carries the highest
band in the decree.

## The filing is the benchmark, not the truth

This is the part worth reading twice. In Vietnam the proof document is usually not a test result. It
is the product's own registration or declaration file, and the claim must sit inside it.

- Điều 70.3.a: cosmetic copy must match the Hồ sơ công bố mỹ phẩm. 15–20 million.
- Điều 70.4.b: it must match the declared nature, classification and functions. 30–40 million, plus
  surrender of unlawful proceeds.
- Điều 71.2.d: food copy must match the tự công bố, the bản công bố or the xác nhận nội dung quảng
  cáo. 10–15 million.
- Điều 73.1.a: device copy must match the registration certificate, the standards-declaration
  receipt, or the import licence.
- Điều 75.4: a service may not be advertised beyond the approved phạm vi hoạt động chuyên môn. 40–60
  million plus a three to six month suspension.
- Điều 50.5.c: misleading on any attribute *đã đăng ký hoặc đã công bố* — registered or published.
  80–100 million plus surrender of proceeds.

Read Điều 50.5.c again. The benchmark named in the statute is the filing. So a brand can hold a
flawless clinical study, be telling the plain truth, and still be fined 30 to 40 million because the
function was never written into the Phiếu công bố. Under the substantiation model the study is the
answer. Here the study is beside the point until the filing carries the function, and the fix is to
amend the filing or cut the line — never to attach the study to the brief and call it handled.

## Two prohibitions that are image-generation constraints

A skill that generates pictures produces both of these by default, because they are what stock
skincare and device imagery looks like.

**Doctors, pharmacists, medical staff, uniforms, clinics.** Banned outright for cosmetics at 15–20
million under Điều 70.3.c, and for medical devices at 20–30 million under Điều 73.3. The ban covers
the image, the clothing, the name and the written endorsement together. Hiring a real dermatologist
makes it worse rather than better, and consent discharges nothing, because the prohibition is on the
category of image. A white coat in a serum ad is a fine, not an art direction choice.

Both are bound to their sectors. No article bans a doctor in a food advertisement, so the audit does
not pretend one does — `bác sĩ` fires the cosmetics article on a cosmetics draft and nothing at all
on a food draft.

**A patient describing a treatment effect.** Điều 71.4, 20–30 million. Truth is not a defence, because
the article prohibits the form of the claim rather than a false one. The genuine recovery story, told
by the person it happened to, with the receipts, is the violation.

Alongside them, Điều 50.3.a: using a person's image, voice or writing without that person's consent,
20–40 million. This is not the copyright question, and the two get confused constantly. A licence
from the photographer or the agency is permission to use the file. It is not permission to use the
person, and the person's own permission cannot be given by whoever posted the photograph.

## The words a statute dictates

Ten rows where the failure is absence rather than falsity, and paraphrase is not available.

- `Thực phẩm bảo vệ sức khỏe`, `Thực phẩm bổ sung`, `Thực phẩm dinh dưỡng y học` (or `Sử dụng cho
  người bệnh với sự giám sát của nhân viên y tế`), and `Sản phẩm dinh dưỡng cho` plus the named group.
  Điều 71.1, 5–10 million.
- `Thực phẩm này không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh`. Điều 71.2.b,
  10–15 million — and Điều 71.2.c says it stays in a broadcast cut under fifteen seconds.
- The identity block, per sector: product name, the responsible party's name and address, and for a
  medical service the licence number, the operating hours and the approved scope. Điều 71.2.a, 70.3.b,
  73.2, 75.1. No article grants a format exemption, so a square social post carries what a billboard
  carries.

## Where a craft gate became a legal one

Điều 53.1.b requires warning text to contrast with its background and to be no smaller than the type
in the rest of the advertisement. It sets no ratio and no point size. So the measurement is yours to
take and to record, and `data/colour-gates.csv` stops being only a craft instrument in this skill and
starts being the record of a legal duty. 10–20 million, and the ad comes down.

Điều 53.1.c adds the spoken case: a warning read faster or quieter than the rest of the spot fails on
the same band.

## What the ledger has to carry now

The nine generic fields are still the shape of a per-claim record, with three changes that matter.
`evidence_source` splits: name the *filing* the claim sits inside, separately from any study
supporting it, because they are different objects and only one of them is the benchmark.
`claim_type` maps to a `claim_family` in `data/claim-evidence.csv` so the row inherits an article and
a band rather than a category label. And `expires/review_date` is not a hygiene field: Điều 70.4.a
treats an expired Phiếu công bố receipt exactly like a missing one, at 30–40 million with proceeds
surrendered. A campaign cleared in March and still running in November is the ordinary way that
happens, and no platform notices.

## The audit divides in two, and neither half covers for the other

A regular expression reads the copy. It cannot see the photograph and it cannot open the dossier. So
fourteen gates split by what they read, and the split is the honest part:

- **Nine read the draft.** Superlatives, comparatives, drug verbs on a cosmetic, a missing mandatory
  phrase, a patient testimonial, a closed category named outright.
- **Six read the answer sheet.** Is there a face in the shot and is there a release for it. Does the
  claim sit inside the filing. Is the warning legible at the size it will ship. Is a doctor in frame.

`--template` writes that sheet for a sector. Every row on it is a question an inspector is entitled
to ask, and an unanswered row is a failing gate rather than a passing one. That is deliberate: the
script cannot make a draft lawful. It can stop the draft that plainly is not, and name what a person
still has to sign.

Two rows are not on the sheet at all. Điều 53.2 fines content that is not truthful, accurate or clear
at 20–40 million with surrender of the proceeds of sales made from the advertising, and it names no
test. It is the article that catches whatever the specific ones miss, which means it cannot be
attested away on a form. Putting it on the sheet would read as clearance, so it stays off, and it is
the residual this whole exercise leaves behind.

## What over-reports, deliberately

`nhất` is the Vietnamese superlative marker and also a bound syllable in a dozen ordinary words:
thống nhất, đồng nhất, nhất định, nhất quán, hợp nhất, thứ nhất. A scanner ignoring that fires on
every second paragraph. One requiring an adjective in front misses `nhất` standing alone. So the
known false friends are masked before scanning, listed in `FALSE_FRIENDS`, and what survives is
reported as a candidate for a human to confirm.

The bias is set on purpose. Over-reporting costs a document reference. Under-reporting costs 10 to 20
million and a takedown.

## Fines stack, and the arithmetic is not decorative

The audit adds the bands on the rows that failed, because Điều 4 charges violations separately. A
serum post with a superlative, a comparative, `đặc trị`, a dermatologist and an unanswered dossier
question reaches 345 to 505 million VND across sixteen rows — before the forced correction, the
takedown, and the surrender of everything the post sold. That is not a scare figure. It is the sum of
the bands the copy touched, printed with the article beside each one so the number can be checked.

## Four sectors this unit refuses rather than half-covers

Medicine (Điều 69), chemicals and insecticidal preparations (Điều 72), and plant protection products
(Điều 76) each carry their own article, their own documents and their own bands, and none of them is
in this table. `--sector pharmaceutical` fails a gate that names Điều 69 and stops, because a partial
answer there reads as clearance and is worse than none. Tobacco and strong alcohol appear only as the
outright ban, which is the whole of what a marketer needs from them.

## What the deliverable has to contain

- The ledger rows for every claim in the piece, each naming its filing and its expiry.
- The filled answer sheet, with a named person against every `present`.
- The audit output, with every failing gate either fixed in the copy or resolved by a document
  reference recorded in the ledger.
- For a regulated sector, the number: the Phiếu công bố receipt, the tự công bố, the registration
  certificate, or the operating licence.

## What this unit cannot establish

Whether the copy matches the filing, because it has not read the filing. Whether the face in the
shot belongs to someone who agreed to be there. Whether the warning is legible at shipping size.
Whether a claim needs pre-clearance — `data/vn-advertising-law.csv` records that interaction as
`open-preclearance-interaction`, asserted neither way, because it needs a Vietnamese lawyer. A green
answer-sheet gate means a person said so, not that a script checked.

## Working outside Vietnam

The substantiation model still governs US-facing work, and the endorsement rules there are stricter
about material connections than the Vietnamese text is about wording. Checked 2026-07-22:

- FTC Advertising FAQs: https://www.ftc.gov/business-guidance/resources/advertising-faqs-guide-small-business
- FTC Endorsement Guides Q&A: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- FTC Disclosures 101: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers

None of those substitute for the filing question, which has no FTC analogue.

## The handoff

Claims that survive go to `references/copywriting.md` for the wording and
`references/rewrite-human.md` for the register. Prohibited imagery goes back to
`references/prompt-grammar.md` as a negative constraint before anything is generated, not after.
Disclosure duties for a paid creator sit in `references/affiliate-commerce.md`, which reads the same
law table from the other end.

## Rights and claims

### Real people

- Confirm the user has authority to use and edit identifiable real-person images.
- Preserve identity, age presentation, skin tone, face, body, and distinctive features unless a specific change is explicitly requested.
- Do not impose generated-person defaults on a supplied real person.
- Do not create deceptive endorsements, intimate imagery, or sensitive-context composites.
- Default generated subjects to adults when age is unspecified.

### Public figures and artists

- Do not directly imitate a named living artist's signature style.
- Do not present a generated person as a real celebrity endorsement.
- Translate allowed qualities into non-identifying casting, wardrobe, light, composition, and material language.

### Product and packaging

- Require a product reference for exact packaging fidelity.
- Never invent readable label copy, certification marks, ingredients, dosage, warnings, or legal text.
- Preserve trademarks and logos exactly when authorized references are supplied.
- Label unverified packaging as concept art.

### Claims

Classify every claim:

- **Supplied and supported**: may be used with source note.
- **Supplied but unverified**: keep as user-provided copy and flag verification.
- **Inferred benefit**: describe as a creative hypothesis, not public claim.
- **Invented proof**: prohibited.

For health, beauty, finance, legal, performance, environmental, and comparative claims, require evidence appropriate to the market and channel. Do not convert visual metaphor into factual proof.

### Reference and source rights

- Record source URL, owner when known, license or usage basis, and download date.
- Use references for analysis, not close reproduction.
- Avoid proprietary campaign assets in deliverables unless authorized.
- Prefer user-owned, licensed, generated, or clearly reusable assets.

### Disclosure and authenticity

- Do not fabricate UGC, testimonials, customer screenshots, press quotes, or creator statements.
- When synthetic imagery could be mistaken for documentary proof, recommend appropriate disclosure based on context and platform rules.
- Do not present concept renders as shipped products, clinical results, real locations, or real customer outcomes.

### Stop conditions

Ask before proceeding when:

- Consent or authority for a real person is unclear.
- The request materially changes identity or body and intent is ambiguous.
- A public figure, protected character, trademark, or close artist imitation is central.
- The campaign requires unsupported regulated claims.
- Publication or external distribution would create irreversible consequences.
