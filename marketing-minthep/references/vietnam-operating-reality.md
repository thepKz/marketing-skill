# Vietnam operating reality: one hire, thirteen roles

## What this unit is for

`command-surface.md` ends by admitting what it cannot do: a sixteen-command chain is arithmetic, not
a schedule. It knows what has to happen before something else can happen. It does not know that the
person running all sixteen commands is also the person answering the inbox, and that the inbox does
not wait.

This unit is where that collision gets counted. It holds one table, one script and one argument.

The argument is that in a Vietnamese small or mid-sized company, "marketing" is one line in a job
advert and thirteen jobs at the desk, and that the roles are not equally likely to survive a busy
week. They fail in a specific order, that order is rational for the person doing it, and it is
ruinous for the company. Naming the order is the useful part. Telling somebody to be more strategic
is not.

## Running it

    python scripts/plan_operating_load.py --list-roles
    python scripts/plan_operating_load.py --roles content design marketplace --capacity 20
    python scripts/plan_operating_load.py --cadence photo=0.25 koc=0.25 event=0.25 ads=1
    python scripts/plan_operating_load.py --roles content design report --have positioning-platform \
        --capacity 12 --format json

`--cadence` takes cycles per week and accepts fractions, so one photo shoot a month is `photo=0.25`.
`--have` names artefacts that already exist, using the artefact names in `data/command-artifacts.csv`.
`--capacity` is command-runs per week the user says they can sustain. Exit codes are 0 clean, 1 usage
error, 2 the stated load exceeds the stated capacity, 3 computable but unsettled.

## The thirteen roles, and the one job title

`data/vn-marketer-roles.csv` has thirteen rows and eleven columns. Twelve of the thirteen rows carry
the identical value in `filed_under`: Nhân viên Marketing. That repetition is the finding, not a
formatting lapse. The thirteenth is the strategy row, and its `filed_under` cell says the rest of the
sentence out loud: this is the part of the title everyone believes they were hired for.

The roles are content, design, photo, video, community, ads, marketplace, koc, print, report, sales,
event and strategy. Between them they name 40 command slots drawing on 29 distinct commands, which is
29 of 29 in the surface. That is worth stating precisely because it is testable and it is
tested: there is no command in `data/command-artifacts.csv` that no role performs, and no role that
invokes a command which does not exist. The surface and the roles table describe the same work from
two directions.

Read the table before quoting from it. Each row carries what the work actually is, which commands it
invokes, what it produces, whether it can be bought in, whether it slips when the week gets busy,
and what breaks if it is dropped. The last two columns are where the argument lives.

## The two roles the command graph cannot see

Two of the thirteen rows have an empty `commands` cell. Community is the page, the comments, the
inbox and the Zalo group. Sales is chasing orders and covering the phone.

They are empty because neither role produces an artefact. The command surface is a graph over
artefacts, so work that produces nothing is invisible to it. And these are the two roles that consume
the most of the day, because both are interrupt-driven and neither can be batched. An unanswered
inbox is a lost order, so it wins every argument about priorities, and it should.

This is the load-bearing limitation of every plan built from a command graph, including the ones this
skill produces. The counted number is a floor, in a known direction, and the script says so in its
own output rather than in a footnote. Ask for `--roles community sales` on its own and it reports a
capacity check of `skipped` with the reason that nothing selected maps to a command, which is a fact
about the roles and not a light week. It would have been easy to let that case return a clean pass.
That is exactly the error the unit exists to name, so it returns 3.

The sales row deserves one more sentence, because it is the row people argue with. Chasing orders is
not marketing. It lands on the marketer because the marketer is the person at the desk with the
customer's message already open. The row exists so that it can be named in a capacity conversation,
because until it is named it is invisible, and invisible work is never resourced.

## What the numbers are, and what they are not

Ask for every role, put the per-campaign roles at one cycle a month and ads at one a week, and the
script reports 24.0 command-runs per week and 7 commands of one-time setup. Ask for just the five
roles that recur weekly, and it reports 18 per week with 10 commands of setup.

A command-run is one distinct piece of work. It is not an hour, and this unit will not convert it
into one. The reason is not modesty. The time cost of `write` varies between an owner posting from a
phone and an agency writing to a brief by more than a factor of five, nobody in this repository has
measured it, and a fabricated hour figure here would be laundered into a hiring decision. So capacity
is whatever the user says it is, supplied with `--capacity`, and without it the fit check returns
`skipped` rather than quietly passing. This is the same rule as `--share` in `plan_palette.py`: an
input nobody supplied is not an input that came back clean.

The four verdicts are the same four the colour unit uses, and they mean the same things.

| Verdict | What it means |
|---|---|
| `passed` | The counted load fits the stated capacity, and every cadence was supplied |
| `failed` | The counted load exceeds the stated capacity, before the two uncounted roles |
| `skipped` | No capacity was stated, or nothing selected is countable at all |
| `review` | The load fits, but roles whose cadence was never stated are missing from the count |

`review` exists here for the same reason it exists there. A checker that returns a verdict on
everything gets ignored on everything. Five of the thirteen roles cannot be given a default cadence:
four recur per campaign, and the table cannot know how many campaigns a month somebody runs, and ads
is continuous, which is not a count at all. Those are reported as unstated, not as zero.

## Which assertion is worth the most

The five weekly roles need 10 commands of setup before the weekly machine runs. This is where a shop
owner reasonably loses patience, and the honest reply is not to skip the strategy. It is to notice
that most of the setup is asking for things they already know.

Assert `--have positioning-platform` and the setup drops from 10 commands to 5. Assert
`--have creative-brief` instead and it drops from 10 to 9.

That asymmetry is the whole lesson. The brief looks like the thing standing between you and the work,
because it is the last step before the work. It is worth one command. The positioning platform looks
like the abstract one, and it is worth five, because everything else in the chain exists to produce
it. An owner who can state their buyer and their promise in two sentences is not taking a shortcut
when they claim the platform; they are describing something real, and it removes half the setup.

So when the setup number causes an argument, ask which artefacts already exist in the owner's head
and put them behind `--have`. Then the trade is a number both sides can weigh rather than a
negotiation somebody has to win.

## The order in which things slip

Eight of the thirteen rows say the role never slips: content, design, video, community, ads,
marketplace, sales, event. Three say it does: photo, print, strategy. The remaining two answer more
precisely, and their precision is the point. The booking of a creator never slips; the usage right
and the brief both do, which is how a campaign ends up with content it cannot legally boost. The
report never slips; the diagnosis inside it does.

Look at why the eight survive. Content and design have a publishing deadline the owner sees the same
day. Community and sales have a customer waiting. Ads is spending money whether or not anyone is
watching. Marketplace has a registration window the platform closes without asking. Event has a fixed
date. Every one of them is protected by something external and immediate.

Now look at the three that slip. A photo shoot can be postponed by reusing last year's photograph,
which is why a feed looks identical in January and September. A print proof can be signed off
unread, which costs nothing until it costs an entire run in one payment. And strategy slips first and
always, because it has no deadline, produces nothing visible this week, and nobody in the company
asks for it by name.

The report row is the subtle one and it is worth reading twice. The report never slips, because it
was asked for. The diagnosis inside it always slips, because nobody asks for that by name either. So
the numbers keep arriving every week and stop changing anything. That is the most expensive failure
in the table and the quietest, and it is why `report` invokes `improve` and not only `measure`.

When the script reports roles standing on a positioning platform that is neither written nor planned,
it is describing the consequence: each of those roles decides the buyer and the promise again, on its
own schedule, and they do not agree. The output looks like inconsistent branding. It is not a
discipline problem. It is the arithmetic of a role with no deadline losing to eleven roles that have
one.

## What is worth buying in

Nine of the thirteen rows say the work can be bought. The four columns to read together are
`can_be_bought`, `slips_when_busy`, `what_breaks_if_dropped` and whether the output is reusable.

Photo is the strongest candidate, and it is the one people buy last. The skill gap between a phone on
an office desk and a packshot studio is the largest in the table, the output is reusable for a year,
and it is a role that slips. Marketplace operations is the second, for the opposite reason: it is the
least interesting work in the table and the most reliably worth handing over, because the platform's
calendar punishes a missed window in money.

Sales support is the highest-value hour to move off the desk, and it is not marketing at all. It
competes directly with every other row.

Three things cannot usefully be bought. The print approval cannot, because whoever signs the proof
owns the wasted run. The diagnosis in the weekly report cannot be bought from somebody who was not in
the room when the decisions were made. And the strategy cannot, in the sense that matters: a
consultancy will sell the document, but a document nobody in the building agreed with changes no
caption. Watch the fee structure on paid media too. Agencies charging a share of spend are rewarded
for spending more, which is a real conflict to price in rather than to pretend away.

## The calendar nobody negotiates

Two structural features of the Vietnamese market change the shape of a plan, and neither appears in
imported marketing frameworks.

The first is that the retail calendar is set by the marketplaces, not by the brand. The double dates
- 9.9, 10.10, 11.11, 12.12 - come with platform-funded discounts and registration windows that close.
Missing one does not mean running the campaign later; it means the subsidised traffic goes to a
competitor who registered on time. This moves work into fixed weeks that the brand did not choose,
and it is why the marketplace row never slips.

The second is that there are two calendars. Tết moves against the solar year, so the largest
commercial moment of the year lands in a different week each time, and the run-up compresses or
stretches accordingly. Production has to finish earlier than a solar-calendar plan suggests, because
print vendors and couriers stop for the holiday and restart unevenly. When somebody asks for a Tết
campaign, the first question is which solar week Tết falls in that year, and the second is the
vendor's last shipping date before it. Neither is a marketing question and both decide the plan.

Zalo belongs in the same section. It is not a channel bolted onto Facebook; for a large part of
customer service and repeat selling it is the channel, and it is where the community role spends time
that no scheduling tool reports on. If a plan counts Facebook and Instagram placements and omits
Zalo, it is not a plan for this market.

## Taking the brief in Vietnamese

Two habits are worth keeping.

Ask what the person actually did last week, not what their role is. The role answer is always "làm
marketing", which is the job title problem restated. The week answer lands in specific rows, and if
something they did lands in no row, this table is missing a row and should be corrected rather than
argued with. That is the falsification test for the whole unit, and it costs one question.

Then settle the form of address before any copy is written. Vietnamese makes it obligatory: anh, chị,
em, bạn, quý khách and mình are different decisions about the relationship, and they carry more brand
information in Vietnamese than an adjective does in English. There is no neutral option, so declining
to choose is itself a choice, usually a bad one. This is also the failure that survives machine
translation most reliably, because English source copy contains no signal for it and the translator
picks a default. `rewrite-human.md` and `data/translation-tells.csv` hold the repairs.

## What is sourced here, and what is not

Nothing in this unit is a survey finding, and it must not be presented as one. No row in
`data/marketing-benchmarks.csv` supports a claim about how many roles a Vietnamese marketing hire
holds, because no such row was found and none was invented. What this unit contains is a structural
model: a list of roles, the commands each invokes, and arithmetic over the command graph that anybody
can re-run.

That is a weaker claim than a statistic and a more useful one, because it is checkable in one
conversation. Ask the marketer for last week. If every item lands in a row, the model held. If it
does not, add the row. A statistic could not be checked that way, and a fabricated statistic would
have been quoted back with more confidence than it deserved.

The arithmetic is a different matter and must be re-derived rather than trusted. Re-run the role
count, column count, 29-of-29 command coverage, two empty-command rows, setup figures, and four
verdicts before changing the prose, because this repository has drifted from measurement before.

## Refusals

Do not convert command-runs into hours, days or headcount. The script will not, and neither should
the answer built on it.

Do not report a load figure without saying it is a floor and naming the two roles it excludes.

Do not tell somebody their strategy work slipped because of discipline. It slipped because it was the
only item on the list with no external deadline. Fix that by giving it one, or by asserting the
platform from what the owner already knows, not by exhortation.

Do not answer "how do I do marketing for my shop" with a menu of thirteen roles. That is the problem
restated as advice. Pick the smallest set that produces something publishable, run
`plan_operating_load.py` with the owner's own capacity, and say plainly which roles are being left
undone and what breaks as a result.

Do not quote a Vietnamese staffing or budget figure that does not exist in `marketing-benchmarks.csv`
with a fetched source behind it.

## What this unit cannot decide

It cannot tell anyone how long anything takes. It cannot see the two roles that consume the most of
the day, and it says so in its own output rather than rounding them away. It does not know whether a
particular company can afford to buy in the roles it identifies as worth buying, and it has no view
on salaries. It cannot tell whether the owner's two-sentence answer about buyer and promise is any
good, only that asserting it removes five commands of setup: `position` and the four commands
upstream of it. Whether the assertion is true is a question for `research` and `investigate`, and
those are in the surface for a reason.
