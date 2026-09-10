#survey-pipeline  (exported thread, not filed)

[2026-09-04 08:41] slack export
workspace: the university / research
channel: #survey-pipeline
members: Alex Rivera, Yuki Tanaka
this paste starts in the middle. older replies
did not come through.

--- unread ---
Yuki Tanaka  08:41
the friday export still has twins. i counted
40 rows that share an email and a firm
name. the weekly pull is lying again

Alex Rivera  08:44
same 40 as last week or a new
40. i do not want to "fix" a
count i cannot see

Yuki Tanaka  08:45
new 40. last week's twins were
the empty-schema ones. these have
full replies and still
duplicate

[08:45] slack
Yuki Tanaka uploaded image.png (failed to
load in this export)

Alex Rivera  08:47
ok. do not mail anyone until the
list is clean. i said that on the
12 july note and i mean it
today too

Yuki Tanaka  08:48
i can patch a
dedup before the noon run. collapse on
email plus firm name, keep the
later timestamp

Alex Rivera  08:49
do the
dedup. then paste the before/after
count in here, not in a
private thread i will lose

Yuki Tanaka  08:51
working

[08:51] slack: Yuki Tanaka is typing
[08:52] slack: Yuki Tanaka is typing
[08:56] SYSTEM: this message was deleted
[08:57] Yuki Tanaka: ignore that, i pasted the
api token into the channel and
yanked it. rotate later. not
your problem this morning

Yuki Tanaka  09:06
dedup fix is in. before: 640
rows. after: 600. the 40 twins
collapsed. i left a
comment in the script, not a
new doc

Alex Rivera  09:08
good. next run should be
600 if nobody mails a
second copy. if the afternoon
pull grows again we
stop and look, we do not
"just append"

Yuki Tanaka  09:09
afternoon pull is the one that
broke us last month. i can
hold it

Alex Rivera  09:10
hold it. i have committee from
two until we
vote. i will look at the
script tonight. do not open a
ticket, this channel is the
ticket

Yuki Tanaka  09:11
ok. i will write "dedup fix
2026-09-04" at the top of the
script so future-me does not
undo it

--- thread jump, export glued two days ---

[2026-09-03 17:12] Yuki Tanaka
heads up, tomorrow's export
will look fat. i have not
done the
dedup yet. do not panic at
640

[2026-09-03 17:14] Alex Rivera
i will panic anyway. see you
in the morning

--- back to 2026-09-04 ---

Yuki Tanaka  09:22
also: the flag for incomplete
rows still fires on the
twins we just
dropped, because the
incomplete table was built
before the
dedup. i can rebuild it
after lunch

Alex Rivera  09:24
rebuild after lunch. one
fix at a time. today's
job is the
dedup fix, not a
rewrite of the
schema

Yuki Tanaka  09:25
copy. going quiet until
the rebuild.

[09:25] slack export ended
downloaded by: alex
do not treat this paste as a
filed note
