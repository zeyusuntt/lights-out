# Rehearsals, before the event

Every file here comes from rehearsal runs made before kickoff on other problems (a shared counter, a payments service, a booking service), not from the run in this repository.

- `RESULTS.md`: one row per run, rehearsals and event runs alike, with the fault audits and the one-agent ablation.
- `matrix-*.json`: planted-fault audits. Each planted fault is a simulated defect, one per copy of an accepted service, run against each detector.
- `faults/`: the planted faults, one patch each, named as in the matrices.
- `solo-run-triage.md`: the neutral triage of the one-agent ablation. Its counts are failed test instances; its reproductions R01 to R21 are the distinct defects.
- `review-1-triage.md`, `review-2-triage.md`: outside reviews of the factory's tooling and how each finding was handled.
