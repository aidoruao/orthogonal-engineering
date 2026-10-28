--------------------------- MODULE LaborSchedule ---------------------------
(***************************************************************************)
(*  LaborSchedule — the schedule, not just the inequality.                  *)
(*                                                                          *)
(*  `L2_LABOR.lean` proves that required labour demand is a function of     *)
(*  area and specification, that splitting shifts cannot create capacity,   *)
(*  and that a shortfall forces either unmet standards or unpaid labour.    *)
(*  All three are facts about a *single* allocation.                        *)
(*                                                                          *)
(*  This specification models the thing those facts are cited for: a        *)
(*  custodial schedule unfolding over a period of service days. It asks a   *)
(*  question the inequality cannot answer -- can any interleaving of work   *)
(*  and rest actually complete every required task inside the paid hours?   *)
(*                                                                          *)
(*  TLC decides it over the whole reachable state space. Two models differ  *)
(*  in exactly one boolean, `UnpaidAllowed`:                                *)
(*                                                                          *)
(*    UnpaidAllowed = FALSE  the paid-only schedule. Completion is          *)
(*                           unreachable when demand exceeds capacity.      *)
(*    UnpaidAllowed = TRUE   the same schedule with unpaid work permitted.  *)
(*                           Completion becomes reachable.                  *)
(*                                                                          *)
(*  The difference between those two runs *is* the dichotomy, exhibited as  *)
(*  an executable fact rather than asserted in prose.                       *)
(***************************************************************************)

EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
    ServiceDays,      \* number of service days in the modelled period
    ShiftMinutes,     \* paid custodial minutes available per service day
    Cost1,            \* minutes for one occurrence of task kind 1
    Cost2,            \* minutes for one occurrence of task kind 2
    Required1,        \* occurrences of task 1 needed in the period
    Required2,        \* occurrences of task 2 needed in the period
    UnpaidAllowed     \* FALSE = paid-only model, TRUE = unpaid work permitted

\* Two task kinds are enough to make the scheduling question non-trivial:
\* interleavings arise from ordering work against a fixed daily capacity, not
\* from the number of kinds. Record-valued constants are avoided because TLC's
\* config parser does not accept record literals, so the functions are derived
\* here from plain integer parameters instead.
Tasks == {1, 2}
Cost == [i \in Tasks |-> IF i = 1 THEN Cost1 ELSE Cost2]
Required == [i \in Tasks |-> IF i = 1 THEN Required1 ELSE Required2]

ASSUME Cost1 \in Nat /\ Cost1 > 0
ASSUME Cost2 \in Nat /\ Cost2 > 0
ASSUME Required1 \in Nat
ASSUME Required2 \in Nat
ASSUME ServiceDays \in Nat /\ ServiceDays > 0
ASSUME ShiftMinutes \in Nat /\ ShiftMinutes > 0

VARIABLES
    done,             \* done[t] = occurrences of t completed so far
    paidToday,        \* paid minutes consumed in the current service day
    unpaidTotal,      \* minutes worked without pay, across the period
    day               \* current service day, 0 .. ServiceDays

vars == <<done, paidToday, unpaidTotal, day>>

(***************************************************************************)
(*  Total demand: the labour-minutes the specification requires.            *)
(***************************************************************************)
TotalDemand == Cost1 * Required1 + Cost2 * Required2

(***************************************************************************)
(*  Total paid capacity: what the schedule can pay for.                     *)
(***************************************************************************)
TotalCapacity == ShiftMinutes * ServiceDays

(***************************************************************************)
(*  The target predicate: every required occurrence has been performed.     *)
(***************************************************************************)
Complete == \A t \in Tasks : done[t] = Required[t]

(***************************************************************************)
(*  Initial state.                                                          *)
(***************************************************************************)
Init ==
    /\ done = [t \in Tasks |-> 0]
    /\ paidToday = 0
    /\ unpaidTotal = 0
    /\ day = 0

(***************************************************************************)
(*  Perform one occurrence of task t, paid.                                 *)
(*                                                                          *)
(*  Only permitted while it fits in what remains of today's paid shift.     *)
(*  This is the guard that makes capacity real: work cannot be banked       *)
(*  across days, and a shift that is over is over.                          *)
(***************************************************************************)
WorkPaid(t) ==
    /\ t \in Tasks
    /\ day < ServiceDays
    /\ done[t] < Required[t]
    /\ paidToday + Cost[t] =< ShiftMinutes
    /\ done' = [done EXCEPT ![t] = @ + 1]
    /\ paidToday' = paidToday + Cost[t]
    /\ unpaidTotal' = unpaidTotal
    /\ day' = day

(***************************************************************************)
(*  Perform one occurrence of task t, unpaid.                               *)
(*                                                                          *)
(*  Permitted only in the model where unpaid work is allowed. This is the   *)
(*  branch a real operation takes when the paid shift ends and the work is  *)
(*  not done. Removing it is what makes the paid-only model falsifiable.    *)
(***************************************************************************)
WorkUnpaid(t) ==
    /\ UnpaidAllowed
    /\ t \in Tasks
    /\ day < ServiceDays
    /\ done[t] < Required[t]
    /\ done' = [done EXCEPT ![t] = @ + 1]
    /\ paidToday' = paidToday
    /\ unpaidTotal' = unpaidTotal + Cost[t]
    /\ day' = day

(***************************************************************************)
(*  End the current service day. Paid time does not roll over.              *)
(***************************************************************************)
NextDay ==
    /\ day < ServiceDays
    /\ day' = day + 1
    /\ paidToday' = 0
    /\ done' = done
    /\ unpaidTotal' = unpaidTotal

Next ==
    \/ \E t \in Tasks : WorkPaid(t)
    \/ \E t \in Tasks : WorkUnpaid(t)
    \/ NextDay

(***************************************************************************)
(*  The specification. No fairness constraint is imposed: the question is   *)
(*  whether a completion is *reachable at all*, and adding fairness would   *)
(*  only narrow the behaviours considered. If no behaviour reaches          *)
(*  completion, no fair one does either.                                    *)
(***************************************************************************)
Spec == Init /\ [][Next]_vars

(***************************************************************************)
(*  SAFETY: no minute is ever worked without pay in the paid-only model.    *)
(*                                                                          *)
(*  This is the formal statement of "the model contains no unpaid labour".  *)
(*  It is an invariant of every reachable state, not a claim about one.     *)
(***************************************************************************)
NoUnpaidLabor == unpaidTotal = 0

(***************************************************************************)
(*  SAFETY: paid work never exceeds paid capacity, on any behaviour.        *)
(***************************************************************************)
WithinPaidCapacity == paidToday =< ShiftMinutes

(***************************************************************************)
(*  The property under test: can the schedule reach completion?             *)
(*                                                                          *)
(*  Checked by asserting its negation as an invariant. If TLC explores the  *)
(*  entire reachable state space without violating `NotComplete`, then      *)
(*  completion is unreachable -- for every schedule, not just the greedy    *)
(*  one. That is a stronger statement than `TotalDemand > TotalCapacity`,   *)
(*  because it ranges over interleavings.                                   *)
(***************************************************************************)
NotComplete == ~Complete

(***************************************************************************)
(*  No THEOREM is asserted here. A TLA+ THEOREM requires a proof, and       *)
(*  writing one without a proof would be the unverified claim this          *)
(*  repository refuses. The reachability question is decided by TLC over    *)
(*  the full state space instead: a check, not an assertion.                *)
(***************************************************************************)

=============================================================================
\* Modification History
\* 2026-10-27  Created. Models the schedule L2_LABOR.lean proves an
\*             inequality about; TLC decides reachability over interleavings.
