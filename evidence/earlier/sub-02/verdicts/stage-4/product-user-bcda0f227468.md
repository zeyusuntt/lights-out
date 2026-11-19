VERDICT: PASS
REVISION: bcda0f227468c5eac1ca2901cc4a30fdec12d489

fserve of the exact hash against the local mock web (sample corpus); Playwright chromium at 1440 and 375 px. Screenshots/scripts: journey/stage-4/bcda0f227468/ (all 12 sample companies built, each dossier and evidence screen shot at both widths).

## New in stage 4
- Dossier screen: an eighth "Investors" row after Executives, other markup (one name per line, Known badge, "In effect since", quoted citations with links). Exactly six `field-*` test ids remain.
- Origins/corroboration: every field shows a distinct chip: "One source" + "Independent origin: x", or "Corroborated" + "N independent origins: a, b. Corroborated since <date>", or for multi-member fields "Not every value has two sources" + origins. Distinguishable by text and outline, not colour alone; readable at 375 and 1440 (ferncliff-foods, ostrava-mobility checked).
- Contested still counts only the six fields; Executives/Investors contested shows "Sources disagree".
- Restart during a build (refresh then abrupt kill/start): the dossier was not left `building`, browser stayed signed in, spend shown (160 units).

## Earlier flows re-walked at both widths
Signup/login/logout/errors, `/` empty/search/invalid domain, building -> ready auto-update, status states, failed state (all providers faulted) keeps fields, slow build followed, lost-response and hung-write `research-uncertain`/`refresh-uncertain` with same-key retry, stale out-of-order read ignored, export/import keeps session, no stray `null`, no horizontal overflow on any screen (12 dossiers + evidence, list, contested), nothing loaded from outside the service origin.

## Notes (do not block)
Doubled opening quote on excerpts that begin with a quote mark; slight selected/non-selected row misalignment on Evidence; long meta lines on Evidence at 375. A contested Executives/Investors row says only "Sources disagree" without naming the competing names (they are on the Evidence screen). Batches have no UI (none required). Not exercised: 429 from the UI, upgrade from a real earlier-stage export; API-only behaviour (batches, budgets, provider failure) is the verifier's.
