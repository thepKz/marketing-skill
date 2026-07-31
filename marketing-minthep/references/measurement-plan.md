# Measurement Plan

## Contents

- What this unit decides
- An event is a definition before it is a number
- The event table
- Three fields decide whether the work is reportable at all
- A campaign name is a filter key that has to survive a year of its own kind
- Personal data does not belong in a query string
- Why every platform reports more conversions than your analytics
- The one number worth computing on the gap
- Cash on delivery breaks the last step of the funnel
- The marketplace wall, and the one platform that has a door in it
- Zalo publishes one useful thing and no window at all
- The order of work
- Reading the report
- What this unit cannot establish
- Evidence grades
- The handoff

## What this unit decides

Whether a number can be measured at all, and whether the thing being measured is the thing that was
promised.

That is a different question from which numbers matter, which is `kpi-scorecards.md` and
`data/kpi-metrics.csv`. A scorecard can be perfect and still be fed by an event that fires on a
button click rather than a successful order, in which case every figure on it is a count of taps.
This unit sits upstream of that, and it is the half that gets skipped because it produces no chart.

Three artefacts. `data/tracking-events.csv` defines fifteen events by the moment they fire.
`data/attribution-windows.csv` records what each platform counts and where its default is written
down. `scripts/check_tracking_plan.py` checks the strings — tagged links and event names — against
the platform rules that reject them silently.

## An event is a definition before it is a number

`add_to_cart` is not a fact about the world. It is whatever the person who wrote the tag decided it
was, and the two obvious choices differ by a factor that nobody ever discovers.

Bind it to the button's click handler and it counts the failed write, the double tap and the
frustrated third tap. Bind it to the response handler and it counts carts.

Both are called `add_to_cart` in the report, and both look reasonable in a screenshot of the code.
The first inflates the top of the funnel enough to make the conversion rate below it look like a site
problem. Somebody will then spend a quarter redesigning a checkout that was never broken.

So the definition is written down first, in the language of the moment it fires, and the tag is
written from the definition. `data/tracking-events.csv` carries that sentence for every event, in a
column called `fires_exactly_when`. The sentences are deliberately negative where they need to be.
`view_item` fires when a detail page renders with a resolved `item_id` — "not on a list card, not on
a hover, not on a modal quick-view."

Every row also carries what the event does not prove. `contact_click_phone` does not prove a call
happened, connected, or was answered — it proves a tap on a phone number. That column exists because
the gap between an event and its interpretation is where reports become dishonest, and it usually
happens in a meeting rather than in the code.

## The event table

Fifteen rows.

```
python scripts/check_tracking_plan.py --events
python scripts/check_tracking_plan.py --event add_to_cart --params item_id=A1,quantity=2
```

Each carries the funnel stage, the moment it fires, the required parameters, the value source, a
deduplication key, whether it counts as a conversion, the error it usually ships with, a Vietnam
note, and what it does not prove.

The deduplication key is the column most plans omit and most need. `purchase` deduplicates on
`transaction_id`. That is why the event belongs on the server at order creation rather than on the
thank-you page. A page fires again when it is refreshed, and it never fires at all for the customer
who closes the tab during the redirect.

Both errors are invisible. They push in opposite directions, so the total looks plausible.

Four of the fifteen are stages the platforms do not offer and a Vietnamese funnel cannot do without.
`order_confirmed` is the confirmation call — the point at which a human removes the duplicate and the
prank order, and the cleanest number in the funnel. `order_delivered` is money arriving.

`order_returned` carries a reason code, because wrong size is a listing problem and damaged in
transit is a carrier problem and the two get budgeted differently. `marketplace_outbound` is the
click out to Shopee or TikTok Shop, and it is marked as not a conversion on purpose.

That last one is the most common quiet redefinition of a goal. The outbound click is the last thing a
website can see, so it gets promoted to a conversion, and from that day the campaign is optimised for
leaving the site.

## Three fields decide whether the work is reportable at all

`utm_medium` picks the channel. `utm_source` picks the row. `utm_campaign` is the only key that
groups spend. A link missing any of the three produces traffic that cannot be reported on, and the
loss is not recoverable afterwards — there is no second copy of the referrer.

The medium is the field with a rule behind it. Analytics matches it against a fixed list of values,
and `social` is on that list while `social_media` is not.

A medium outside the list can only be classified by source, against a list of sites the vendor
publishes as a spreadsheet rather than as text. When that misses too, the traffic arrives in a channel
the reports call Unassigned. Nobody reads Unassigned.

```
python scripts/check_tracking_plan.py --rules
python scripts/check_tracking_plan.py --url "https://minhthep.vn/ban-go?utm_source=facebook&utm_medium=cpc&utm_campaign=facebook-ban-go-202607"
```

Then there is the mistake that survives review, because it does no visible damage on the day it is
made. Channel definitions ignore case, so `utm_medium=CPC` is classified as paid correctly. Reported
values do not ignore case, so `CPC` and `cpc` arrive as two rows that have to be added together by
hand for the rest of the campaign's life.

Nothing is broken. Nothing is wrong. The report just has two of everything, forever, and fixing the
convention today does not merge what was collected last quarter.

The other silent one is tagging after the fragment. Anything after `#` is never sent to the server,
so the link works, the page loads, the campaign runs, and the tagging is absent from every report.

## A campaign name is a filter key that has to survive a year of its own kind

Two hundred campaign names accumulate faster than anybody expects, and the report offers exactly one
axis to group them: the string somebody typed at three in the afternoon.

So the script asks for three things rather than a house taxonomy it has no business inventing. At
least three segments, because two cannot carry channel, offer and period at once. One segment in
`yyyymm` form, because a set of names with no period in them cannot be sorted, archived or compared
like with like. One separator throughout, because mixing hyphen and underscore guarantees the next
person picks the other one and creates a second row for the same campaign.

`utm_id` is graded low and is worth adding anyway. Cost imported by hand joins on the campaign id,
not the campaign name, so without it a spend figure has nothing to attach to.

## Personal data does not belong in a query string

A query string is written to the server log, the analytics tool, every proxy in between, and the
referrer header of the next page the visitor loads. A phone number put there to make a report
joinable is now in four systems nobody audited.

The analytics vendors prohibit it in their own terms, and Google's guidance names the campaign
parameters specifically — do not put personal data in `utm_source`, `utm_medium`, `utm_term`,
`utm_campaign` or `utm_content`.

The legal exposure is real and the instrument is not the one you will be told it is. Law 91/2025/QH15
has been in force since 1 January 2026 and it replaced Decree 13/2023/ND-CP, which nearly every
Vietnamese compliance summary written before that date still names as current. Check the date.

Under the superseded decree a phone number was enumerated as personal data, disclosure to another
organisation required consent that named it as a recipient, and the burden of proving that consent
sat with the business collecting the data. Nothing in that decree addressed query strings, referrers
or logs at all. So anyone who quotes you an article number about URLs is reconstructing it. Read the
law before writing a compliance line into a plan, and treat the mechanics above as the shape of the
old instrument rather than a statement of the current one.

This is the gate most often failed deliberately. The script catches it two ways, because the two
catch different mistakes. A value shaped like an email address or a Vietnamese mobile number is the
accidental paste. A parameter *named* `sdt`, `email` or `ho_ten` is the design decision, and that one
is the more common of the two.

## Why every platform reports more conversions than your analytics

There are five structural reasons and none of them is anybody lying. `data/attribution-windows.csv`
carries them per platform with the page to re-read and the screen to check.

**The windows differ.** Google Ads counts a conversion up to thirty days after the click by default,
adjustable from one to ninety. A click window on the other platforms is commonly one or seven days.
Analytics runs its own lookback — thirty days for acquisition key events, ninety for the others — and
the numbers are not the same numbers.

**View-through conversions are inside some headline numbers and outside others.** This asymmetry is
worth learning, because it is the single largest source of a gap that looks like fraud.

On Meta, when an ad set uses a view window, view-through conversions are included in the Results
column. On Google Ads they are explicitly excluded from the Conversions column and reported only in
their own column and in All conversions. Engaged-view conversions on Google Ads go the other way and
*are* included in Conversions. So the same word means three things depending on which tab is open.

Analytics has no equivalent. A person who saw an ad, did not click, and arrived two days later
through a search is a Meta conversion and an Organic Search session, and both records are correct.

**The timestamp differs.** Google Ads reports a conversion against the date of the *click*, not the
date of the conversion, with opt-in columns labelled "by conv. time" for the other view. Analytics
reports by event time. So a conversion today from a click last Tuesday moves the numbers in different
weeks in the two tools, and a week-over-week comparison built from both is comparing two
incompatible calendars.

**The model differs.** Analytics and Google Ads both default to data-driven attribution now. The
alternatives were removed in November 2023, leaving last click as the only other option. Meanwhile
session-scoped and user-scoped dimensions in analytics always use last click regardless of the
property setting, so two tables inside the same tool can disagree with each other.

**Deduplication does not cross platforms.** A conversion touched by an ad on two platforms is claimed
by both, in full. The sum across platforms is therefore not a total of conversions. It totals claims.

`verify-in-account` appears in that table wherever the vendor publishes no default. Not a research
gap. It means the only true answer is the one in the account, and the row's `where_to_read_it` column
says which screen holds it.

Meta publishes no default attribution setting anywhere, so quoting one from memory is how a plan
acquires a wrong number that everybody trusts because it was written down.

## The one number worth computing on the gap

The temptation at this point is to build a model that reconciles the platforms. Do not. There is one
piece of real arithmetic available and it is an inequality.

If three platforms claim 120, 80 and 40 conversions, that is 240 claims. If analytics counted 190 in
total, then at least 50 of those claims — 20.8 percent — are counted twice or are not there.

```
python scripts/check_tracking_plan.py --reconcile meta=120,google=80,tiktok=40 --analytics 190
```

At least. It is a floor, not an estimate. Overlap also hides inside a sum that happens to match, and
analytics undercounts for its own separate reasons, so the true figure is higher than the floor by an
unknown amount.

What the floor is good for is the conversation it ends. A channel plan that adds platform-reported
conversions across platforms and divides spend by the total has produced a cost per acquisition that
is too low by at least that share. Now the amount is on the page instead of being argued about.

Which platform is over-claiming is a different question, it needs both accounts open, and the script
does not guess.

## Cash on delivery breaks the last step of the funnel

A `purchase` event fires when an order is created. On cash on delivery the money arrives days later,
or it arrives short, or the parcel comes back.

So `purchase` is an order request and not revenue, and every ratio computed on it is overstated by
exactly the share that never got delivered.

```
python scripts/check_tracking_plan.py --purchases 1000 --delivered 640
```

Six hundred and forty delivered out of a thousand ordered overstates every efficiency figure by 36
percent. That is arithmetic on two numbers the business already has in a different system, and it is
the largest correction most Vietnamese reports are missing.

It reorders the channels. The campaign that produced the most order requests is regularly not the
one that produced the most collected cash, and the difference between those two rankings is where the
budget should have gone.

Both numbers in that command have to be yours. That cash on delivery dominates is published and
checkable. The Ministry of Industry and Trade's e-commerce white book for 2023 puts it at 76 percent
of internet users on page 47, and separately at 50.6 percent of paid orders on sales platforms on
page 72. VECOM's 2026 index reports 77 percent of consumers for data year 2025.

Two publishers, three years apart, agreeing on roughly three quarters.

What nobody publishes is the delivery rate. Not the white book, which contains no cancellation figure
at all — it reports only that 77 percent of merchants offer a returns policy, which is a different
thing entirely. Not VECOM, which mentions reverse logistics as unresolved and gives no number.

So the 640 above is a worked example and not a benchmark, and a plan that quotes a Vietnamese
cancellation rate is quoting a number with no publisher behind it. Yours is in your own courier
dashboard, it is the only one that describes your own parcels, and it is worth pulling before the
first report rather than after somebody has defended a ranking with it.

Which is why `order_confirmed` and `order_delivered` are in the event table as first-class events
rather than as a note. Compute the ratios that decide budget on delivered orders, and report
purchase-to-delivered on its own line so the gap stays visible instead of being absorbed.

## The marketplace wall, and the one platform that has a door in it

Most Vietnamese sellers put money into traffic that ends on somebody else's page. A click leaves your
site, or leaves an ad, and lands on Shopee, Lazada or TikTok Shop. Whatever happens next is theirs.

So the honest default is a wall. Your `marketplace_outbound` event is the last thing you can see,
and it is marked as not a conversion in the registry on purpose. A report that treats it as one has
converted a departure into a sale.

The wall is not the same height on every platform, and the difference is documented rather than
folklore.

**Shopee has a door.** Seller Centre ships a tracking-link builder and a UTM manager under Sales
Analytics, on the Truy cập tab. It takes the five standard parameters, it emits either a web link or
an app deep link, and Sales Analytics then breaks visits, orders and revenue out by channel and by
campaign. Campaigns created from inside Seller Centre's own Facebook and Google ad tools are tagged
without you doing anything.

Two constraints are published and both matter. A deep link over 250 characters is not supported, so
fall back to the web link. And the data arrives on a two-day lag, which Shopee's own documentation
says may leave the Traffic Ngoại sàn figures inconsistent with what your other channels report.

Read that hedge twice. The platform is warning you in advance that the two numbers may differ, which
is the same asymmetry as everywhere else in this unit, stated by the vendor for once.

Shopee publishes a window on one product only. The video display service counts orders placed within
seven days of a click on the product in the video, and it counts revenue only where that was the last
click to the product in the same seven days. Two metrics, two rules. The order count is a click
window; the money is last click inside it.

Nothing comparable is published for seller affiliate orders. No page reachable without a seller login
carries a number at all, so a figure in a media plan came from somewhere other than Shopee.

**Lazada's door, if there is one, is behind the login.** Both order endpoints on the Open Platform
return the buyer, the address, the payment method and the money. Neither returns anything naming where
the buyer came from. Count the fields: 49 on `/order/get`, 55 on `/orders/get`, and no source,
referrer, channel, campaign or sub-identifier among them.

That is a narrow claim, so hold it narrowly. What it says is that the order record cannot tell you the
channel. Whether Seller Centre offers a tracking-link builder anyway is not something the public
documentation answers, and the API category tree is drawn by the browser rather than served, so
reading it also needs an account.

No lookback duration for Lazada ads appears on any page reachable without one. If somebody quotes you
a Lazada attribution window, ask where they read it.

That absence changes what you can promise. Off-Lazada spend into a Lazada listing is measurable on
your own side up to the click, and after that only as a before-and-after read on Lazada's own
numbers. Write that into the plan before the spend, not into the report afterwards.

## Zalo publishes one useful thing and no window at all

Zalo Ads is the largest domestic channel most Vietnamese businesses run, and it publishes no
attribution window. No default. No screen where one would live. What it does document is the Zalo
Ads pixel, a script in the page head, with conversions defined by a URL keyword or by a button's ID,
class or text.

Read that last part twice, because it changes what breaks. A conversion here is bound to a button's
class name rather than to a tracking call. So a designer who renames a button stops the conversion
without touching a line of measurement code. Nothing errors anywhere.

Two seven-day figures on Zalo's own site are not windows. A conversion is tagged `Đang hoạt động` once
it has recorded at least one event in the last seven days, which is a health check on the object rather
than a lookback. A separate article argues for scheduling an ad across seven days. Neither says
anything about how long after a click a sale is credited, and both get quoted as though they did.

Stop reporting `Tổng conversion`. It adds organic conversions, and conversions driven by other
advertisers' ads, to your own — so it is comparable to nothing in your analytics and it is the number
the interface shows you first. `Conversion từ QC` is the ad-attributed one.

The genuinely useful publication is buried in a Google Analytics housekeeping article. Zalo tells
advertisers to add `zaclid` to Exclude URL Query Parameters in GA3, and to strip it with a Trim Query
variable on Page URL in GA4.

That is worth more than the instruction. A platform that appends its own click identifier and then
explains how to remove it has confirmed the query string survives the click. So your own UTM tagging
arrives intact, and on Zalo it is not a refinement — it is the only channel identification you control.

## The order of work

1. Write the definitions before the tags. One sentence per event naming the exact moment it fires,
   taken from `data/tracking-events.csv` and edited rather than invented.
2. Name what each event does not prove, in the same document, before anybody has an incentive to
   forget.
3. Fix the naming convention and validate a real link with `--url` before the first campaign ships,
   not after there are two spellings of it.
4. Check every event name and parameter set with `--event` against the platform rules. These are
   silent rejections, so the only alternative to checking is finding out from a gap in a report.
5. Read the attribution row for every platform in the plan, and go and read the two settings the
   vendor does not publish.
6. Once data exists, run `--reconcile` before anybody computes a cost per acquisition across
   channels, and `--purchases` with `--delivered` before anybody computes one at all.

## Reading the report

Gates are graded critical, high, medium and low, and only critical and high block. The script exits 2
when something blocks, 0 when nothing does, and 1 on a usage error.

Critical is reserved for the four failures that destroy data rather than degrade it: personal data in
a parameter, a missing required tag, a malformed event name, and a reserved name or prefix. Each of
those either cannot be undone or produces silence.

Read the low-severity rows anyway. `campaign-id-present` and `key-event-name-margin` are notes
about the near future, and the margin one is labelled as an inference on purpose.

That inference is arithmetic rather than something a vendor wrote down. The platform documents a
forty-character ceiling and appends two characters to a key event's name internally, so the safe
length is thirty-eight. The gate says so.

Every run closes with what it did not establish. That block is not boilerplate, it is the list of
work still owed.

## What this unit cannot establish

Whether the tag fires. This reads strings, not a browser. A perfectly named event that was never
installed passes every gate here.

Whether the destination deduplicates. That is a server question and the answer is in the
destination's configuration.

Which platform is right when two disagree. The windows table lists the structural causes; choosing
between them needs both accounts open and a person.

Whether the data already collected is usable. A convention fixed today does not repair last quarter,
and both spellings stay in the report permanently.

What a conversion is worth. That is `data/kpi-metrics.csv` and the claims ledger, and inventing a
lead value so a return figure can be computed is how an assumption becomes a reported number.

## Evidence grades

The platform limits enforced by the script were read off vendor documentation on 2026-07-31: event
name length, parameter counts and ceilings, reserved names and prefixes, the channel-routing rules.
Each row of `data/attribution-windows.csv` carries the page it came from.

Google publishes no last-updated date on its help pages, so treat that as the date it was checked and
nothing more. These change. Re-read before quoting.

The `verify-in-account` cells are graded honestly as unpublished, not as unknown to me.

The campaign-naming rules are a convention rather than a platform requirement. Three segments and a
`yyyymm` are graded as reasoning, not as vendor guidance, and the script marks them medium for that
reason.

The reconciliation floor and the delivery-rate correction are arithmetic. They are the only two
numbers in this unit that need no source at all.

## The handoff

Send four things.

Event definitions with their firing moments. The naming convention, with one validated example link
to prove it. Then the attribution row for every platform in the plan, and the list of settings
somebody still has to open an account to read.

Whoever receives it needs that last list most, because it is the part that cannot be delegated to a
document. Two of those settings are not published by their vendors at all, and one of them cannot be
changed after the ad group goes live. All of them silently decide what every number in the next report
means.
