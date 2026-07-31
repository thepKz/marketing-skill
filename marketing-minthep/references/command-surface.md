# The Command Surface

## Contents

- What this unit is for
- The artefact rule
- The twenty-eight commands
- What each category is for
- Routing when no command was named
- Routing when the request maps to two commands
- Routing when the request needs a chain
- Routing when the named command is premature
- The chains worth memorising
- The collapse trade
- Refusals in director voice
- What this unit cannot decide

## What this unit is for

Marketing requests do not arrive at the beginning of the work. They arrive in the middle, as "make
me marketplace photos from this one packshot", or "why did last month's campaign do nothing", or "I
need content for the whole of next month". The honest response depends entirely on which pieces of
thinking already exist, and prose is a bad instrument for working that out. Narrating a plan invites
two failures at once: skipping a dependency because the sentence read plausibly, and padding the
plan with upstream work nobody actually needed.

This unit removes the guessing. Every command declares what it cannot run without, what would make
it stronger, and what it produces. `data/command-artifacts.csv` holds those declarations. Run
`scripts/plan_command_chain.py` to walk them:

```
plan_command_chain.py --goal composition-set --have source-photograph --format text
plan_command_chain.py --goal expand --have source-photograph positioning-platform
plan_command_chain.py --verify stage shoot produce
plan_command_chain.py --explain colour
plan_command_chain.py --list --format text
```

The script exits 0 on a runnable plan, 2 on a chain that cannot run in the order proposed, and 3 on
a plan that still needs something only the user can supply. Do not narrate a chain you have not
computed. The dependency graph is not obvious even to someone who wrote it, which is why the
authoring check rejects an input no command produces.

## The artefact rule

A command's output is a named artefact, not a conversation. `position` does not "discuss
positioning"; it produces a `positioning-platform`, and the next command consumes it by that name.
This is the mechanism that keeps a long piece of work traceable, and it is also the honesty gate: if
the artefact cannot be written down, the command did not run.

Two artefacts have no producing command. `cold-brief` is the request in the user's own words, and
`source-photograph` is a photograph taken with a camera. A plan that quietly invented either would
be a plan to fabricate the brief or the product, which is the failure the whole skill exists to
prevent. Everything else in the graph is produced by exactly one command, except where a row
declares `also_satisfies`: a generated `image-set` is a usable source photograph for `expand`.

Distinguish `takes` from `also_uses` and never blur them. `takes` is a blocker. `also_uses` is a
stated weakness: the command runs, and the plan says out loud what it is running without. Downgrading
a blocker to a nicety to make a chain look shorter is the same dishonesty as inventing a statistic.

## The twenty-eight commands

Do not restate the table here. `data/command-artifacts.csv` owns it, with eleven columns per
command: what it does, what it takes, what it also uses, what it produces, what it also satisfies,
what usually follows, which references and scripts to read, what it refuses, and what it does not do.

The shape is six categories:

| Category | Commands | The question the category answers |
|---|---|---|
| discover | brainstorm, research, investigate, survey | What is true, and how do we know? |
| decide | segment, position, offer, plan, budget | What are we choosing, and what are we giving up? |
| create | brief, write, humanise, localise, schedule | What does it say, in language a person would use? |
| direct | compose, colour, identify, stage, shoot, generate, expand | What does it look like, as numbers? |
| activate | produce, adapt, approve, launch | What actually ships, and who cleared it? |
| evaluate | measure, diagnose, improve | What happened, why, and what changes? |

Every command names the references and scripts that back it. That column is checked against the
filesystem when the table is authored, so a command cannot promise machinery that does not exist. If
a command's `machinery` column is empty, the command is a claim rather than a capability.

## What each category is for

**discover** is for a request that starts from assumption, internal opinion or a growth number with
no mechanism under it. The group widens the field and then cuts it. It keeps three distinctions
alive: desk evidence is not audience testimony, testimony is not observed behaviour, and a vivid
quote from six buyers is not a share of the market.

**decide** is for a request where evidence exists and the choice has not been made. The group exists
to exclude. Audience priority precedes positioning; positioning precedes the offer; the offer
precedes channel planning. `plan` owns channel choice, and channel follows where the buyer's
decision actually happens rather than which platform the team is comfortable with.

**create** is for turning a decision into language. `brief` exists so that every downstream
specialist solves the same problem. `write` owns search-led substance, not keyword insertion.
`humanise` measures what makes prose read machine-written and repairs it. `localise` writes the
second language from the brief; a literal translation is source material and never the deliverable.

**direct** is for visual authorship, and it is the group most often asked for first. `compose` owns
layout as quantities. `colour` owns the palette as contrast, lightness separation and a chroma
budget. `identify` owns the mark at the smallest slot it has to survive. `stage` owns the scene.
`shoot` directs a camera. `generate` works from references without reproducing protected expression.
`expand` handles the constrained case that most small sellers actually have: one usable photograph
and a marketplace that wants twelve.

**activate** is for turning cleared thinking into files. `produce` makes masters. `adapt` recomposes
per placement rather than resizing. `approve` gates product truth, claims, rights, disclosure,
accessibility and craft. `launch` closes the operational questions and stops there: the skill
prepares a launch, and a person launches it.

**evaluate** is for after release. Never collapse the three. A poor result does not prove poor
creative, and a strong channel metric does not prove commercial value.

## Routing when no command was named

Infer the earliest missing artefact and start there. Do not open with a menu, and do not ask a
question whose answer would not change the plan.

| The request contains | Start at |
|---|---|
| A product and an ambition, nothing else | brainstorm |
| Market material but no customer evidence | investigate |
| Evidence but no strategic choice | position |
| A settled strategy and a request for assets | brief |
| A photograph and a marketplace requirement | compose, then expand |
| Live results | measure |

State the command chosen, the assumptions made, what is missing and which artefact will come out.
Then proceed. Ask only for information whose absence would make the work deceptive, unlawful, unsafe
or commercially meaningless.

## Routing when the request maps to two commands

Choose by output, name both, run the upstream one first and carry its artefact forward.

- "Write an SEO article that sounds natural" is `write` then `humanise`. The deliverable is finished
  copy, not editorial notes on a draft.
- "Review this campaign and tell me why it failed" is `measure` then `diagnose`. Observed performance
  precedes any causal claim.
- "Make lifestyle images from this packshot" is `compose` then `expand`. Composition logic precedes
  variant generation, or the variants disagree with each other.
- "Design a logo and a palette" is `identify` then `colour`, because the mark has to survive at
  sixteen pixels before its colour is worth arguing about.

Do not blend two commands into one untraceable answer.

## Routing when the request needs a chain

Compute it, then state it as a decision rather than a questionnaire: "Start with `investigate`; no
customer evidence exists. Then `segment`, `position`, `brief`, `compose`, `expand`." Proceed on
stated assumptions wherever the step is reversible, and mark each assumption inside the artefact it
affects. Stop before any claim, targeting decision, price, rights position or measurement definition
that needs proof nobody has supplied.

## Routing when the named command is premature

Correct the routing in one sentence and keep the user's material as input. "`produce` is premature;
no creative brief exists, so I am running `brief` first." Never answer a misused command with a menu
or a lesson in terminology.

## The chains worth memorising

Computed with `--have source-photograph` and nothing else, so these are the honest worst cases:

| From nothing to | Commands | Chain |
|---|---|---|
| A marketplace set from one packshot | 8 | brainstorm, investigate, research, segment, position, brief, compose, expand |
| Reference-led campaign imagery | 9 | the same six, then stage, generate |
| A launched campaign | 16 | the strategy spine, then write, humanise, localise, compose, produce, adapt, approve, launch |
| An improved campaign | 19 | the above, then measure, diagnose, improve |

## The collapse trade

Eight commands is a fair thing to resent when the request was "just make me some photos". The reply
is not to skip the strategy and it is not to argue. It is arithmetic, which the script prints:

| If this already exists | The eight-command chain drops to |
|---|---|
| composition-system | 1 |
| creative-brief | 2 |
| positioning-platform | 3 |
| audience-priority | 6 |

A shop owner can state their buyer and their promise in two sentences. Recording that as
`--have positioning-platform` is not a shortcut; it is an accurate description of what exists, and it
removes five commands. Offer the trade as a number and let the user take it. What is not on offer is
asserting an artefact nobody has: a `positioning-platform` the user never stated is an invented
strategy, and every asset built on it inherits the invention.

## Refusals in director voice

Refuse the request, keep the working relationship, and name what you will do instead.

- No audience. "A product description is not an audience. I can produce an audience investigation; I
  will not present generic copy as strategy."
- "Make it go viral." Virality is not a deliverable. Reach mechanics, a reason to share,
  distribution, creative variants and measurement are.
- A claim with no proof. No proof, no claim. Supply substantiation or reduce the wording to what the
  evidence carries.
- Copy a competitor. Their category codes, hierarchy, offer structure and channel behaviour are fair
  to analyse. Their copy, composition, distinctive assets and campaign devices are not ours to take.
- Fabricated research, reviews, testimonials or citations. Refuse, and label the gap `UNVERIFIED`
  with the check that would close it.
- Deceptive urgency, false scarcity, hidden conditions, advertising disguised as editorial. Replace
  with a truthful offer and legible terms.
- Targeting that exploits vulnerability. Reframe around legitimate need, suitability and consent.
- Imagery that changes material truth: invented features, altered quantity, misleading scale,
  impossible results, a concealed defect. This is the one refusal that survives every deadline.
- A literal translation presented as finished localisation. Route to `localise` and write it again
  from the brief.
- A vanity-metric brief. Attention with no defined commercial or behavioural outcome cannot direct a
  campaign. Name the decision `measure` has to support.
- Production before strategy. "No positioning, no offer, no brief. Every asset built now is an
  expensive guess." Then offer the collapse trade above rather than a refusal alone.

## What this unit cannot decide

It computes a faultless chain to the wrong goal without complaint. Choosing the goal is the
director's judgement, which is why `refuses` is printed beside every command in the plan rather than
buried in a reference nobody opens. It also cannot know the team's real capacity; a sixteen-command
chain is arithmetic, not a schedule, and `vietnam-operating-reality.md` is where that collides with
one person holding six roles.
