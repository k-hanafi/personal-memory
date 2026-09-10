---
id: reading-diff-in-diff-handbook
type: reading
as_of: 2026-09-03
status: current
confidence: high
---

# Notes on the Applied Difference Handbook

Fictional handbook by Olin Reeve. Working notes
for the week 10 block in [[econometrics-fall-2026]].
Read again on 2026-09-05.

## Two periods

Difference in differences starts with a treated
group and a comparison group, each observed
before and after a change.

The simple four-cell table is the whole idea.
Subtract within each group, then subtract those
changes. That second difference is the estimate
if the two groups would have moved together.

Write the table on the board before any algebra.
Students grab the arithmetic when they can see
the four numbers.

## Parallel trends

The design needs a path the comparison group
can stand in for. Plot the two series for a few
periods before the change. If they already
diverge, stop and pick another comparison.

A flat pre-trend plot is not proof. It is a
check that failed to kill the design. Say that
out loud. Students treat a pretty figure as
a license.

If the pre-period is short, say so in the
writeup. Do not hide a two-point check behind
a long methods paragraph.

## Staggered timing

When units change in different years, a single
post dummy is a mess. The handbook walks through
a stacked example with three cohorts.

Cohorts that change early become comparisons
for cohorts that change later. That can flip
the sign if effects grow over time. Flag it
in lecture. Do not let a software default
pick the weights.

Reeve's chapter 6 keeps the example tiny on
purpose. Copy that. A twelve-cohort figure
loses the room.

## Event study

An event study plot puts time since the change
on the x axis. Pre-period coefficients should
sit near zero. Post-period coefficients tell
the path, not just a single average.

I will use one plot in week 10 and leave the
rest for the reading group. Students should
be able to read a confidence bar without
treating it as a yes or no.

Do not show a plot with twenty leads if the
data only support four. Sparse pre-periods
make noisy leads look like a failed check.

## Standard errors

Cluster at the unit that was treated, not at
the person-year row. The handbook's toy table
makes that visible: treat ten states and the
real sample size is ten, not ten thousand.

I will put one two-way clustered example in
the slides and skip the rest. The lab script
can reprint the toy table.

If a problem set asks for the cluster, name
the unit in the question. Otherwise half the
room clusters on the person.

## What I am taking into class

Open with the four-cell table. Then one pre-trend
plot. Then the staggered warning in one slide.
Leave IV and extra robustness for later weeks.

The handbook is clearer than Calder on this
one design. Calder still wins on identification
for the rest of the term.

Mark pages 40 to 48 for a second pass. Those
pages are the ones to reread tomorrow.

Skip the appendix on synthetic controls this
round. One design per week is enough.

Keep Reeve's notation on the board so the
slides and the book match. Do not invent a
third set of subscripts.
