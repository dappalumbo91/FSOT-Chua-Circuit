---- MODULE CircuitArray ----
EXTENDS Naturals

CONSTANTS Open, BelowPhi, Phi, PhiSq

VARIABLES sigma, locked

TypeOK == sigma \in {Open, BelowPhi, Phi, PhiSq} /\ locked \in BOOLEAN

Init == sigma = Open /\ locked = FALSE

SetOpen == sigma' = Open /\ locked' = FALSE
SetBelowPhi == sigma' = BelowPhi /\ locked' = FALSE
SetPhi == sigma' = Phi /\ locked' = TRUE
SetPhiSq == sigma' = PhiSq /\ locked' = TRUE

Next == SetOpen \/ SetBelowPhi \/ SetPhi \/ SetPhiSq

Spec == Init /\ [][Next]_<<sigma, locked>>

LockExactlyAtOrAbovePhi ==
  /\ (sigma = Open => locked = FALSE)
  /\ (sigma = BelowPhi => locked = FALSE)
  /\ (sigma = Phi => locked = TRUE)
  /\ (sigma = PhiSq => locked = TRUE)

====
