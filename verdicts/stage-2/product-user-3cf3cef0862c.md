VERDICT: PASS
REVISION: 3cf3cef0862c212f6f572712876ad700e9e0e381

Walked the exact revision (image built from a clean clone, mock web with the sample corpus) at 1440 and 375 px with Playwright. Screenshots and the walk scripts are in journey/stage-2/3cf3cef0862c/ (d- = desktop, m- = 375 px).

## Verified
- Routes: /, /dossiers/{domain}, /evidence, /contested, /signup, /login all render, with consistent navigation. Signed-out visits redirect to /login?next=...
- No horizontal overflow on any of the 14 screens at either width (scrollWidth == innerWidth). Minimum text size 12 px.
- All listed data-testids present on the dossier screen. data-units, data-value and data-status are correct. field-contested appears only on the contested field.
- States visually distinct: known (green), contested (amber, half-filled marker, "Compare sources"), unknown (grey), building (blue banner + progress bar), ready.
- Flow: invalid domain gives an inline error. Research of a valid domain opens the dossier in `building`, polls, and fills in to `ready` without a manual reload. Refresh follows the build; spend goes 63 -> 126.
- Lost response (request aborted): refresh-uncertain / research-uncertain shown, no *-error. Retry clears both and shows the dossier. A response that never arrives turns uncertain after about 13 s and re-enables the button.
- Out-of-order reads: a delayed earlier GET during a build did not overwrite the later read. Final state `ready`.
- Search filters the list, empty-dossiers appears, logout returns to /login, and the 401 login error appears in auth-error.
- Evidence screen: selected candidate marked, source kind and publication time in people-first form plus exact RFC 3339.

## Notes (not blocking; foreman decides)
1. Wrong-password login shows the raw API text "a valid bearer token is required" (m-04-login-wrong.png). Reword it to "Email or password is incorrect".
2. While `building` and before any build is ready, every field reads "Not found in sources" / Unknown (d-08-building.png). That is misleading for a field not yet researched. Prefer "Researching…".
3. Desktop home: the Research button sits below the input's baseline (d-12-home-list.png). The helper text and the button are misaligned.
4. Citation links and "Compare sources" are 16-20 px tall tap targets at 375 px. Padding them would help.
5. The contested list shows the raw field key (`hq_city`) beside the friendly label (m-11-contested.png).
6. The login screen shows the Dossier/Contested nav to a signed-out visitor.
7. Dossier fields show provider but not page kind or publication time. These appear only on the evidence screen, which is acceptable.
