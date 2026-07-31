# Sales Enablement

This file is craft only, and that is a decision rather than an omission. The other regulated
workbenches in this skill each got a duty table because a Vietnamese instrument attaches a duty to
the artefact: `lifecycle-duties.csv` to a subscription and a capture popup, `claim-evidence.csv` to a
public claim, `vn-advertising-law.csv` to a creator's post. No instrument in this corpus attaches a
duty to a one-pager, a deck, a demo or a proposal. Building a table here would mean inventing rows,
so the boundary is stated instead. Read `## What follows the artefact` before assuming a sales
document is outside the law, because two things do follow it.

## Buyer decision map

Capture:

- Buyer role, user role, champion, approver, blocker, and procurement/security/legal stakeholders.
- Trigger, current workaround, desired outcome, risk, switching cost, and decision criteria.
- Product mechanism, fit boundaries, proof, implementation path, and commercial terms when confirmed.

## Artifact contracts

### One-pager

Problem → outcome → mechanism → key proof → fit/use cases → next step. Keep it skimmable and decision-oriented.

### Sales deck

Customer situation → cost/risk of status quo → desired state → product mechanism → demonstration → proof → implementation → offer/next step. Do not make it a feature catalog.

### Discovery and demo

- Discovery: situation, impact, current process, stakeholders, decision, timing, and constraints.
- Demo: mirror the buyer's workflow and show the minimum credible path to value.
- Record questions and objections as customer research, not merely obstacles.

### Battlecard

Use transparent comparison criteria, product truth, traps to avoid, questions to ask, proof, and fit boundaries. Never invent competitor weaknesses or confidential information.

### Case study

Context → challenge → selection → implementation → verified outcome → lessons. Require customer approval for names, quotes, metrics, and logos.

### Proposal and follow-up

Restate agreed needs, scope, deliverables, responsibilities, timing, commercial terms, assumptions, exclusions, and next action. Never invent a discount, deadline, or guarantee.

## Handoff

Connect marketing source, campaign/content consumed, lead state, qualification, owner, next step, and feedback loop. Feed recurring objections, lost reasons, and proof requests back into content, product marketing, and creative planning.

## What follows the artefact

**Consumer-protection duties mostly do not, and the reason is narrower than "this is B2B".** Điều 3.1
of Luật 19/2023/QH15 defines người tiêu dùng as someone buying for the consumption or household
purposes of an individual, family, agency or organisation, and not for a commercial purpose. An
organisation sits inside that definition. So buyer size is not the test. Purpose is. A company buying
a service to resell, or to run its own trade, is buying commercially, which puts the Điều 38 exit
rights, the Điều 42 notice clock and the Điều 18.4.b consent mechanism outside the deal.

Where a particular purchase falls is not settled by this corpus. A deal big enough for the answer to
matter is a deal big enough for a lawyer. Do not assert it either way in a proposal.

**Substantiation and the advertising rules do follow it, because they attach to the assertion rather
than to the buyer.** A figure on a slide is the same claim as a figure on a landing page. So
`claims-proof-ledger.md` and `scripts/check_claims.py` run on a deck exactly as they run on an ad, and
the benchmark Điều 50.5.c measures against is still the product's own filing.

The case-study rule above is the sharp one. A customer's name, quote, logo or metric in material that
promotes the product is a person's image, words or writing in an advertisement, which Nghị định
87/2026 Điều 50.3.a prices at 20 to 40 million without consent. What discharges it is written approval
from the customer's own signatory, naming the figures and the logo. A verbal yes from a champion who
cannot sign is not that document.

**The proof map is a specificity problem before it is a legal one.** Run `check_specificity.py` on the
one-pager and the battlecard. A competitor who could publish your deck unchanged after a find-and-
replace of the logo has read a positioning statement, not a reason to switch.
