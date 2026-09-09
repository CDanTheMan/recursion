# Sealed handoff bounds — 2026-09-09

These are manual arguments about the explicitly defined local model. Finite graph
checks corroborate them on the registered domains; they are not proof of source
validity, implementation integration or unbounded arrival behavior.

Both policies prevent A from changing visibility throughout an active capture.
Each capture therefore checks successfully. A later capture cannot begin until
visibility increases, because both retain the unchanged-count idling condition.
Consequently capture sizes strictly increase within 1..N: at most N captures and
at most 1+2+...+N=N(N+1)/2 ordinal reads per policy, including partial histories.
No retry is necessary in either policy. The drain guard can suppress a start but
cannot create an additional start at the same visibility.

After the final offer, an active capture needs at most N+1 subsequent C opportunities
to read its remaining ordinals and check. Drain then remains open to A until its
finite backlog is empty: the opening guard is false whenever any offered record is
pending. At most N-1 successful A opportunities suffice. A final capture/check needs
at most N+2 C opportunities. Thus 3N+2 alternating AC rounds are a conservative
completion bound from the final-offer state, less than the registered
(N+1)(N+2)+1 rounds for N=2,3,4. For one, each of at most N-1 additional appends may
be followed by a complete capture; the original larger quiet-round bound remains
sufficient. If a C ends a capture in one round, A can serve in the next; unchanged
checked visibility cannot reseal ahead of that A.

With finitely many original offers and endlessly recurring A and C opportunities,
both policies eventually finish. For one, an active capture finishes after finitely
many C opportunities and then remains inactive until A advances visibility. For
drain, after the last offer any pending backlog disables opening until finitely many
A services drain it; the last capture then completes after finitely many C events.
These are scheduling premises, not timing guarantees. An arbitrary finite prefix can
postpone A or C arbitrarily long, so no global action-count waiting bound follows.
Infinite arrivals are outside the original finite-inventory premise; the dynamic
drain guard may continually defer opening if the offered backlog never empties.

Completed witnesses refute universal dominance in the original finite inventory:

| N | O/A/C word | one captures; reads | drain captures; reads |
|---|---|---|---|
| 2 | OCACCACCCC | 1,2; 3 | 2; 2 |
| 3 | OCACCOCCAACCCCC | 1,3; 4 | 2,3; 5 |
| 3 | OCACCAOACCACCCCC | 1,3; 4 | 2,3; 5 |

In the last word, the second record arrives at tick 1: one services it at 6,
drain at 3. The third arrives at 7: one services it at 8, drain at 11. Waiting
vectors are therefore (0,5,1) and (0,2,4). Neither policy dominates matched-record
waiting. The extra read in drain arises from capturing size 2 where one has already
checked size 1 and later captures size 3. Both always use stipulated valid records.

The prior optimistic-versus-sealed common-first-capture and always-open-append
arguments do not transfer: drain may idle on the very first C while one captures.
No shortest-word claim is made for the present witnesses.
