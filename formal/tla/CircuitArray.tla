---- MODULE CircuitArray ----
\* Bench states of the 3-ring (pin AEB2AD, branch fix/aeb2ad-long-window).
\* Below sigma_c the ring escapes to the outer limit cycle (|V| > Bp2) where the nodes ALSO synchronise;
\* the firmware LOCK requires trit agreement AND no escape, so those states must read LOCK = FALSE.
EXTENDS Naturals

CONSTANTS Open, Rc20k, Sigma1, Phi, PhiSq

VARIABLES sigma, synced, escaped, locked

States == {Open, Rc20k, Sigma1, Phi, PhiSq}

TypeOK == sigma \in States /\ synced \in BOOLEAN /\ escaped \in BOOLEAN /\ locked \in BOOLEAN

LockLaw == locked = (synced /\ ~escaped)

Init == sigma = Open /\ synced = FALSE /\ escaped = FALSE /\ locked = FALSE

Set(s, sy, es) == sigma' = s /\ synced' = sy /\ escaped' = es /\ locked' = (sy /\ ~es)

Next == \/ Set(Open, FALSE, FALSE)
        \/ Set(Rc20k, TRUE, TRUE)     \* sigma = 0.9 < sigma_c: escape + outer-cycle sync
        \/ Set(Sigma1, TRUE, TRUE)    \* sigma = 1   < sigma_c
        \/ Set(Phi, TRUE, FALSE)      \* sigma_c = 1.4897 < phi: double-scroll lock
        \/ Set(PhiSq, TRUE, FALSE)    \* robust gate

Spec == Init /\ [][Next]_<<sigma, synced, escaped, locked>>

LockExactlyAboveSigmaC ==
  /\ LockLaw
  /\ (sigma \in {Open, Rc20k, Sigma1} => locked = FALSE)
  /\ (sigma \in {Phi, PhiSq} => locked = TRUE)

====
