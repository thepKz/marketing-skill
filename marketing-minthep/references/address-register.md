# Address register

Decide who the copy is talking to, and hold that decision to the last line. In Vietnamese that decision is not tone. It is grammar, and it is unavoidable.

English `you` carries no age, no rank and no distance. Vietnamese has no such word. Every sentence that addresses the reader has to name the relationship — `bạn`, `anh`, `chị`, `quý khách`, `em`, `mọi người` — and the choice constrains what the writer may call *themselves* in the same breath. So a draft translated out of English has to invent the relationship, and it invents it again at every sentence. What comes back opens on `quý vị`, explains in `bạn`, and closes on `mọi người`. Every sentence is grammatical. Every sentence is polite. And any Vietnamese reader can feel that nobody decided.

That is the loudest machine tell in Vietnamese marketing copy, and a sentence-level reader never catches it, because each sentence is fine on its own. It is only visible across the whole piece. Hence `scripts/check_address_register.py`, which reads the piece rather than the sentence.

## The two facts that are grammar, not taste

Both are documented in a descriptive grammar, not house preference — see the source note at the bottom.

**Pronouns come in pairs.** With the single exception of `tôi`, choosing a first person fixes which second persons are available, and the reverse. `chúng tôi` takes `anh`, `chị`, `quý khách`. `bọn mình` takes `bạn`. `cháu` takes `ông`, `bà`. `ta` takes `ngươi` — which is why `ngươi` in a product post drags the whole piece into costume drama. `tôi` is the documented exception: it pairs with anything, which is exactly why it is the safest first person in commercial copy and why the checker exempts it.

**First-person plural splits inclusive from exclusive.** `chúng tôi` and `chúng tao` mean *us and not you*. `chúng ta` and `chúng mình` mean *you and me*. English `we` collapses the distinction, so "we deliver within the day" comes back as `chúng ta giao trong ngày` — a sentence in which the customer is doing the delivering. This is the single most common machine-translation error in Vietnamese commercial copy, and it is invisible to anyone reading the English.

## Choosing the register

Pick one, then hold it. `data/address-registers.csv` has all 25 forms with the tier, the pairing, the channels and the failure mode.

| Situation | Address | Self | Why |
|---|---|---|---|
| Stranger, respectful default | `anh` / `chị` / `anh/chị` | `tôi` or `chúng tôi` | The workhorse of Vietnamese commerce. Safe on every channel. |
| Peer, younger audience, social | `bạn` | `mình`, `bọn mình`, `chúng tôi` | Attested for people in their early twenties. It is not a neutral `you`, whatever the dictionary says. |
| Retail chat, buyer is younger | `em` | `anh` / `chị` | The seller defers upward. `em` is the one form that works in both directions, which is why the table marks it person `1-or-2`. |
| Formal quote, press release, deck | `quý khách` / `quý vị` | `chúng tôi` | Elevated and ceremonial. Correct here, absurd on Facebook. |
| Brand speaking as itself | the brand name | — | Documented practice for artists and public figures, and it works for a brand. Composes with `bạn` and `anh/chị`. |
| Elderly customer | `ông` / `bà` | `cháu` | The pairing is not optional. `ông` with `tôi` is a different, colder relationship. |

Two forms are worth naming as traps.

`bạn` is not the neutral choice. It reads young. The grammar sources attest it for early-twenties speakers, and it replaced the obsolete `ngươi` in dictionaries — which is precisely why machine translation reaches for it when the English says `you`. Addressing a fifty-year-old buyer as `bạn` is not rude, it is misjudged, and misjudged is worse in a sales context.

`khách hàng` used as address — `khách hàng sẽ nhận được...` — is grammatical, because virtually any person-noun can serve as a pronoun in Vietnamese. It is also third person, so it holds the reader at arm's length while claiming to speak to them. That is a house judgement rather than a grammatical error, and the table grades it accordingly.

## What the checker does

`python scripts/check_address_register.py --check draft.md --channel social`

Six gates, each carrying its own evidence grade, so a reader can tell a grammatical rule from a preference:

| Gate | Grade | What fails it |
|---|---|---|
| `address-present` | house-rule | The copy never addresses the reader at all. Skipped under 60 syllables, where a caption legitimately does not. |
| `one-address-form` | standard-requirement-with-house-threshold | Two tiers in one piece. `composes_with` lists the few combinations that legitimately co-occur; everything else is a switch. |
| `pair-holds` | standard-requirement | A first person that does not take the second person used beside it. |
| `inclusive-exclusive` | standard-requirement | `chúng ta` and `chúng tôi` in the same piece, or an inclusive plural doing the seller's action. |
| `no-archaic-or-impolite` | standard-requirement | `ngươi`, `mày`, `tao` addressing a customer. |
| `channel-fit` | craft-heuristic | `quý vị` on social, `mày` anywhere. Skipped without `--channel`. |

The relation in the table is **default-deny**. Since Vietnamese has no neutral second person, a piece must pick one form and hold it, so listing the handful of forms that legitimately co-occur is a short list anyone can verify. Listing every incompatible combination would be three hundred cells nobody checks.

## Why this checker has a `review` verdict

Half the forms in the table are also ordinary words. `em` is a younger sibling and a term of endearment. `cháu` is a grandchild. `mình` is the reflexive pronoun in all three persons. `mày` sits inside `lông mày`, eyebrow, and `kẻ mày` is an eyebrow pencil — so a cosmetics brand writing accurate product copy trips the impolite-form gate.

A gate that reports `failed` on correct cosmetics copy is a gate the copywriter switches off in week one, and then none of the gates work. So when every piece of evidence for a violation runs through an ambiguous form, the answer is `review`, and the script prints the exact string to go and look at. Exit codes are 0 clean, 2 a real failure, 3 unsettled.

The deliberate consequence: `lông mày` is excluded outright, because it can only be the noun, while `kẻ mày` is left to `review`, because it could be either. Excluding it too would delete the live demonstration of why `review` exists.

## Limits, stated rather than discovered

- **Commercial address only.** `tớ`/`cậu` and the regional intimate sets are omitted. They belong to friendship, not to selling, and adding them widens the false-positive surface for no gain.
- **The brand-name row has no detector.** Nothing can distinguish a brand name from any other proper noun, so `tên thương hiệu` is advisory: the table records what it pairs with, and the script cannot check it.
- **`standard-requirement` here means a descriptive grammar**, not a platform rule or a legal one. The pairing rule and the inclusive/exclusive split are how the language works, as documented by linguists. They are not enforced by anyone.
- **The register defects that matter most are not regex rows.** Tier-mixing and pair-breaking are relations between forms in different sentences. `data/translation-tells.csv` carries only the five `register` tells that are wrong in a single string; everything relational lives in the script.

## Source

`data/address-registers.csv` grades 23 of 25 rows `standard-requirement` against <https://en.wikipedia.org/wiki/Pronouns_in_Vietnamese> (fetched 2026-07-31), which cites Thompson's reference grammar of Vietnamese. `mọi người` and `khách hàng` are `craft-heuristic` and cite this file, because their defect is a judgement about commercial distance rather than a rule of grammar.

Related: [rewrite-human.md](rewrite-human.md) for cadence and calque, which is a separate pass on the same draft.
