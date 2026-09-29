# Lumon terminal software

First deployed on 26 September 2026; MDR-inspired UI deployed on 27 September
local time. The original installation runs on a Raspberry Pi 3 Model B,
managed by `taskiosk.service`. Paths in the historical deployment records refer
to that installation; adapt them to your own Pi when setting up the application.

The physical display is 800 × 480. Its default interface is the simple blue
monospace layout the user preferred, available at
`http://raspberrypi.local:5000/display`. The newer MDR-inspired layout remains
optional at `http://raspberrypi.local:5000/display?theme=mdr`. Tap the Lumon logo
to switch between them. The screenshot from the Pi is
[preview/pi-themes.png](preview/pi-themes.png).

On the idle screen, **Manage** replaces the inactive Complete/Skip buttons.
It opens a 3 × 3 grid of Trello cards, with Previous/Next for additional pages.
Tap a card to read its full title, then **Start & Print** to issue that specific
task and start its normal focus timer. Back returns to the same grid page.
Both layouts support the picker; **M** opens it and Escape goes back.
Complete and Skip return when an assignment is active.

The picker includes all open DOING, TODO and Better Than Nothing cards in
Trello's list order, including recently skipped or issued cards. Manual selection
deliberately bypasses the automatic selector's cooldown and weighting, and never
uses AI. Merely browsing or inspecting a card does not print or update history.
The server rechecks open cards before printing, so a card completed or archived
elsewhere cannot silently issue an unrelated task. Tickets record
`selection_method=manual`; completion, timer restoration and printing use the
existing workflow. [Picker preview with synthetic tasks](preview/manage-classic-grid.png).

Both layouts hide the mouse pointer, including over controls. The kiosk also
runs `unclutter-xfixes` with a one-second idle timeout to hide the native X11
pointer before Chromium receives its first mouse-motion event. Its process is
supervised by the existing kiosk launcher. During an active
task, a percentage and progress bar show elapsed focus-session time, alongside
the countdown. This does not claim to measure task completion and reaching 100%
does not complete the task. A small field of drifting numbers evokes *Severance*
without covering task text or controls. It renders at roughly seven frames per
second and pauses at timer expiry, in a hidden tab, or with reduced motion.
The decorative numbers are not task data.

Switching layouts or reloading restores the latest open assignment and original
start time without selecting or printing another ticket. Newly issued tasks
store their display payload in the existing history; older active entries can
be recovered from Trello. Completed, skipped and more-than-12-hour-old entries
are not restored. Repeated-task completion now marks the newest issue, preventing
an old duplicate from causing the just-completed task to reappear.

The default uses one self-hosted DejaVu Sans Mono font. The optional layout is
informed by actual scene excerpts documented in
[references/README.md](references/README.md), using a self-hosted Liberation Sans
approximation; the production's exact typeface is not claimed. Real queue counts
remain available in the status endpoint and footer tooltip. Keyboard shortcuts
are N/C/S; Y/X still work too. The page uses `Cache-Control: no-store` and versioned
assets to avoid stale pages after an update.

## What changed

- The preferred blue terminal interface with the enclosure's Lumon globe,
  large touch buttons, a focus timer and the newer layout available as an option.
- Real Trello connection status and queue data, refreshed every minute.
  API failures appear as unavailable rather than an empty queue.
- Task selection runs locally by default. It excludes tasks skipped within
  seven days, prefers the least-issued eligible tasks from the last 24 hours,
  then prioritizes DOING and urgent TODO deadlines. Remaining choices mix TODO
  and “Better than nothing,” with more BTN choices on evenings and weekends.
  Ties are randomized. If all eligible cards were issued recently, selection
  continues from the least repeated cards rather than returning false emptiness.
- A selected task gets a 15-minute focus session, not an invented estimate of
  its completion time. Completing a BTN task updates local history while
  leaving the reusable card on Trello; TODO/DOING completion still moves it
  to DONE.
- An optional OpenRouter helper uses Qwen3.7 Flash. Failure, timeout or an
  invalid card ID falls back to local selection, with a ten-minute cooldown
  before trying AI again. Ordinary use currently makes no OpenRouter calls.

## Printed task tickets

Task tickets now use a compact Lumon work-assignment form: globe, department
heading, issue reference, date, task, focus allowance and completion checkboxes.
One monospace family, two weights and thin rules keep it restrained. The
stationery is an original themed design. The old random euro-value line is gone.
See the [actual printer-width preview and layout notes](preview/tickets/README.md).

The entire slip is rendered as a monochrome bitmap, including accented text.
Typical artwork is about 85 mm long, plus the cutter margin; longer titles wrap
and extend the paper. A single synthetic layout-proof receipt was sent without
issuing a real task. Its physical appearance awaits the user's visual check;
the raster pixels, margins and USB delivery passed automated verification.

## Optional settings

Defaults work without changes to the existing Pi configuration:

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `TASKTICKET_USE_AI` | `0` | Set to `1` to try AI before local fallback. |
| `TASKTICKET_AI_MODEL` | `qwen/qwen3.7-flash` | Optional OpenRouter model. |
| `TASKTICKET_FOCUS_MINUTES` | `15` | Focus timer duration, bounded to 1–120. |
| `TASKTICKET_TIMEZONE` | `Europe/Luxembourg` | Selection schedule and UI clock. |
| `PRINTER_TASK_LOGO` | `1` | Include the Lumon globe on the work slip; set to `0` to omit it. |
| `PRINTER_WIDTH_DOTS` | `576` | Printable dot width for centring the logo on the POS80. |

Optional AI uses the existing `OPENROUTER_API_KEY` on the Pi. The prompt is
bounded to at most 12 eligible cards and 150 output tokens, without goals,
biography, descriptions or history. Thinking is disabled. An isolated live
test using one invented card succeeded; real Trello cards were not sent during
verification. Model availability and pricing were checked on
[OpenRouter's official model page](https://openrouter.ai/qwen/qwen3.7-flash).

The local source copy intentionally excludes `.env`, `config/settings.py` and
task history. Deployment preserved the Pi's credentials and history.

## Verification

The POS80 also prints graphics. On 27 September, one standalone “LUMON LOGO
TEST” receipt was sent using ESC/POS `GS v 0`; the user confirmed that the globe
was clear and complete. The initial release used a 320 × 164-dot globe above
native printer text. The full work-slip layout now replaces that format.
The test did not select a Trello card or change task history. The separate
message-printing service was not changed.

The current release passed 39 isolated checks on the Pi, including eleven
printer checks and six ticket-layout checks. They cover bitmap polarity, both
USB paths, native-text fallback, one final cut, failure handling, long and accented
titles, print margins and lossless raster-strip reconstruction. A failed write
does not create an issued-task history entry or automatically retry a partial
ticket. The deployed class also captured a synthetic job in a temporary file.

Read-only live checks authenticated to Trello, confirmed the board was open,
and found **11 TODO, 0 DOING and 19 BTN** cards. A dry run using the deployed
selector returned a real eligible task with `selection_method=local`, without
creating an AI client, modifying history or invoking the printer.

Twenty-one Python checks passed: three status checks, nine selection checks and
nine route/history checks. Browser checks passed at 800 × 480, including
55-pixel default touch targets, timers and assignment text without overflow,
pointer hiding in both layouts, preserved sessions when switching, double-tap
protection, animation and reduced-motion behavior, failed-action retry,
completion state and offline status. These tests use
fake tasks and printer dependencies; they do not issue physical tickets. On the
Pi, a one-pixel pointer movement confirmed that Chromium's cursor resource is
fully transparent, and both kiosk and message-printer services remained active.
`scrot -p` manually composites cursor pixels, so it can show an old resource
even while native XFixes cursor hiding is active; the final screenshot was taken
with pointer capture enabled after verifying the transparent resource.

From the project root, with Python 3.9+ and `aiohttp` installed:

```sh
python3 software/preview/check_backend.py
python3 software/preview/check_selection.py
python3 software/preview/check_routes.py
python3 software/preview/check_printer.py
python3 software/preview/check_ticket.py
```

Manual-selection checks are included in `check_selection.py` and
`check_routes.py`. With the preview server and isolated Chrome running as below,
`node software/preview/check_manage.mjs` checks both layouts at 800 × 480:
pagination, full-title inspection, cursor hiding, safe text rendering,
double-tap protection, session restoration, empty/offline/stale-card handling,
and returning to automatic selection. Results are in
`preview/manage-ui-check.json`; these checks use synthetic tasks and do not print.

`preview/server.py` provides an isolated UI preview at `127.0.0.1:8655`.
`preview/check_ui.mjs` exercises that preview through an isolated Chrome
debugging port at `127.0.0.1:9226`; it requires Node with built-in WebSocket
support. The current result is saved in `preview/themes-ui-check.json`, including
elapsed-progress/timer and animation checks. `preview/mdr-ui-check.json` records
the earlier optional layout release. `preview/simple-ui-check.json` and
`preview/ui-check.json` record the previous designs' checks.

Both `taskiosk.service` and `thermal-printer-subscriber.service` were active
after deployment. The MQTT subscriber's PID stayed unchanged. The teleprint
container and broker on mothra were inspected without changes or test messages.
Physical ticket printing, card completion and Telegram delivery were not
triggered during the earlier UI/backend checks. The subsequent logo and
work-slip proofs are described above. Tap **New Task** on the terminal to
exercise the physical task workflow when wanted.

## Deployment and recovery

The manual-picker release is recorded in `release/manage-deployment.json`.
To undo it, stop `taskiosk.service`, restore the six `changed_files` from the
recorded backup, then start the service. Credentials, task history and the
separate message-printer service are not part of this update.

The work-slip release is recorded in `release/work-slip-deployment.json`.
To restore the preceding logo-plus-text layout, stop `taskiosk.service`, restore
`printer/thermal_printer.py`, `printer/logo.py` and `core/task_manager.py` from
that backup, then start the kiosk. The unused renderer and bold font can remain.

The ticket-logo release is recorded in `release/ticket-logo-deployment.json`.
To undo it, stop `taskiosk.service`, restore its backed-up
`printer/thermal_printer.py` and `core/task_manager.py`, then start the service.
The unused logo module and PNG can remain. Setting `PRINTER_TASK_LOGO=0` and
restarting the kiosk disables the logo without rolling back the release.

Deployment records are saved in `release/ui-deployment.json` and
`release/selection-deployment.json`; the latest design update is recorded in
`release/themes-deployment.json` (previously `release/mdr-deployment.json`).
Backups on the Pi:

- Initial UI backup:
  `/home/srizzo/taskticket/backups/lumon-ui-20260926T214204Z`
- Selection release backup:
  `/home/srizzo/taskticket/backups/local-selection-20260926T215539Z`
- Simplified UI backup:
  `/home/srizzo/taskticket/backups/vintage-ui-20260926T221632Z`
- MDR-style UI backup:
  `/home/srizzo/taskticket/backups/mdr-ui-20260926T222627Z`
- Two-layout, pointer and animation update backup:
  `/home/srizzo/taskticket/backups/themes-ui-20260926T224648Z`

To undo the latest layout/timer update, restore the files listed in
`themes-deployment.json` from its backup, then restart `taskiosk.service`.
The new optional-layout files can remain unused; the restored template and
script will not reference them.

To undo the MDR visual update, restore its three backed-up files
(`templates/terminal.html`, `static/terminal.css`, `static/terminal.js`), then
restart `taskiosk.service`. The task selector and Trello backend are unchanged
by this visual release.

To undo only the visual simplification, restore its backed-up `main.py`,
`templates/terminal.html`, `static/terminal.css` and `static/terminal.js`, then
restart `taskiosk.service`. This keeps the working local task selector.

To undo the selection release, stop `taskiosk.service`, restore the files
listed in `selection-deployment.json` from its backup to the same relative
paths in the application, then start the service. That restores the initial
Lumon UI with the previous selector. To return fully to the original UI too,
also restore `main.py` from the initial UI backup before starting the service.
Do not restore history or credentials, and do not restart the separate MQTT
subscriber for a UI rollback. The native cursor startup change is backed up
separately; see `release/kiosk-cursor-deployment.json` for the launcher path
and backup. Restore that launcher and restart `taskiosk.service` to undo it.
The small `unclutter-xfixes` package can remain installed and unused.

The deployment scripts guard the specific inspected source hashes; they are
records of this release rather than scripts to rerun unchanged over later edits.
