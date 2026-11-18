# Dossier screens — design

## Audience, job and states

Researchers and analysts who check facts about companies before they rely on them. Their main job
is to open a company and see, field by field, what the web supports, how sure that is (known,
contested, unknown) and which source each value came from. After that they compare competing
sources, and start or repeat research.

States the specification names, and where they appear:

| State | Where |
|---|---|
| known, contested, unknown | each field row, each contested item, each candidate's selected mark |
| building, ready, failed | dossier header, list rows |
| loading | every screen while its first read is pending |
| successful | research and refresh feedback, then the dossier that follows |
| refused | `research-error`, `refresh-error`, `auth-error` |
| uncertain | `research-uncertain`, `refresh-uncertain` |
| empty | no dossiers, no search match, no candidates for a field, nothing contested |
| not found | `dossier-not-found` |
| signed out | signup and login; protected screens send the reader to login and back |

## Three directions

1. **Case register.** Each dossier reads like a register entry. There is one ruled row per field:
   the label in a narrow left column, the value large in the middle with its status word and
   mark, and the quoted sources in the right column on the same row. Sans-serif throughout, with
   tabular figures. Density is medium. The motif is the left status rule on each row, a thin
   coloured bar that you can read before you read the words.
2. **Evidence board.** A grid of tiles, one per field, each with a big value, a status badge and
   a source count. You expand a tile to see its sources. It is quick to scan, but it hides the
   citations behind a click, and the specification wants them directly beside the value.
3. **Registry printout.** One dense table for all six fields and their sources, monospaced, with
   provider and kind codes in columns. It is faithful to the data, but it reads as raw API data,
   which the specification asks us to avoid, and it breaks down at 375 px.

**Chosen: 1, case register.** The subject is evidence, so the citations have to sit beside the
value, which rules out 2. The readers are careful, so plain language beats codes, which rules
out 3. A ruled row per field also fits a phone well: the columns stack into label, value, then
sources, with no horizontal scroll.

Rejected as generic interface habits: warm cream with a serif and a clay accent, near-black with
one neon accent, soft-shadow card kits, tracked all-caps eyebrows, middle-dot metadata and
decorative arrows. None of them are used.

## Tokens

Colour, on a cool off-white page:

| Token | Value | Use |
|---|---|---|
| `--page` | `#f5f7f9` | page background |
| `--sheet` | `#ffffff` | register sheet |
| `--ink` | `#16202a` | body text, values |
| `--muted` | `#566270` | labels, metadata (7.0:1 on sheet) |
| `--rule` | `#d9dee4` | row rules |
| `--action` | `#0b57a4` | primary buttons, links, focus ring |
| `--known` | `#1d6b3f` | known |
| `--contested` | `#8a4b00` | contested |
| `--unknown` | `#5f6873` | unknown |
| `--building` | `#0b57a4` | building |
| `--failed` | `#a8231a` | failed, refused |
| `--uncertain` | `#6b3fa0` | uncertain outcome |

Every state colour meets 4.5:1 on white, and each always comes with a word and a mark: a filled
dot for known, a split dot for contested, a hollow dot for unknown. Colour is never the only
signal.

Type: the system UI sans stack, so there is no web font to fetch. 15 px base with 1.5 line
height. Field values 20 px semibold. The dossier domain 26 px. Labels 13 px medium, in sentence
case, not all caps. Figures use `font-variant-numeric: tabular-nums`.

Spacing: a 4 px scale (4, 8, 12, 16, 24, 32, 48). Sheet padding 24 px on desktop, 16 px on
phone. Row padding 16 px. Border radius 6 px on controls and 8 px on the sheet.

Focus: a 3 px `--action` outline, offset 2 px, on every interactive element.

## How each state appears

- **Known**: green left rule, the value at full weight, "Known" with a filled dot, and the
  quoted sources beside it.
- **Contested**: amber left rule, the selected value, "Contested — N values" with a split dot,
  and a link to compare the sources on the evidence screen.
- **Unknown**: grey left rule, "Not found in sources" in muted text, with no sources.
- **Building**: a blue bar under the dossier header that moves while research runs. The state
  word reads "building" and the previous fields stay visible.
- **Failed**: a red notice saying the last research failed and earlier results, if any, are
  shown.
- **Loading**: muted placeholder text, "Loading dossier…", in the sheet.
- **Successful** writes lead straight to the dossier, which then shows building.
- **Refused**: a red inline message under the control that was refused.
- **Uncertain**: a violet inline notice saying "We could not confirm whether this went
  through", with the retry on the same button.
- **Empty states**: one plain sentence and the next useful action.

## Phone to desktop

At 760 px and wider, a field row is a three-column grid: label 160 px, value 1fr, sources 1.3fr.
The header puts the domain and the actions on one line. Below 760 px each row stacks: label,
value with status, then sources. Actions wrap into full-width buttons, and the navigation stays
in one line with the user name truncated. Long URLs and excerpts wrap (`overflow-wrap:
anywhere`), so nothing scrolls sideways at 375 px.

## Stage 3 additions

- **Executives** is a seventh row in the register, after the six fields. Each member is listed
  with its title in words ("Chief financial officer") and the name at value size. The row uses
  the same status rule and the same quoted sources column. It carries `data-field` markup rather
  than the six fields' test identifiers.
- **Two times per value**: under each value's status, one muted line reads "Holds from
  14 Jun 2025. Learned 1 Mar 2026, 09:00 (UTC+00:00)". When no date is stated, it reads "Start
  date not stated". On the evidence screen each candidate adds "Holds from" and "First learned"
  next to "Published" and "Retrieved".
- On the evidence screen, executives candidates are grouped by title under small headings, with
  the selected one marked as in the other fields.
