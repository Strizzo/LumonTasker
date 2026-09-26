**Superseded for further printing by V49:** actual hardware needs 2.44 mm more lug depth and a 2 mm grip for 4 mm screws. V48 bowed during fitting. Keep this as a historical printed test.

# V48 — original confirmed display mounts

The user corrected the physical display orientation and confirmed the original
mount holes align. **Do not shift them.** V47's suggested 3.6 mm right / 2 mm down
translation is withdrawn and its print files are marked DO_NOT_PRINT. No V47
print was sent.

V48 starts directly from V45. The only production-body geometry change is the
glass pocket width: 193.4 → 193.6 mm overall, centred (+0.1 mm per side).
Pocket height 111.4 mm, R8.2 corners, 3 mm bearing ledge and 1 mm nominal front
recess remain unchanged. All four original arms, roots, pads, bores and
counterbores are preserved exactly, verified by zero geometric difference
within their neighborhoods. Nominal front insertion and part clearance checks
pass; both body and test frame are valid, single solids and watertight.

The matching fit frame retains the improved rear-down orientation: the glass
seat and metal-lug lands face upward, away from support contact surfaces.
Same cotton-white PLA in A2 throughout, with a denser three-layer removable
support interface underneath the frame. No colour changes or prime tower.
Settings and temporary support density are inherited from the reviewed V47
orientation, but the model and toolpath must be regenerated for original holes.

Physical hole alignment is now confirmed. Actual simultaneous glass/metal-lug
bearing and the improved printed ledge still need checking. Glass should sit
naturally with screws absent; do not tighten screws across a gap. Preserve the
correct hardware orientation established by the user's successful hole test.

No full enclosure print is released. Full-case cable/power routing and access
remain unresolved. Fusion remains closed/latest saved V39; V48 STEP exports
are not yet synchronized there. See `slice_review.json` for current slicing and
dispatch state when available. User subsequently confirmed the plate clear and authorized printing.

GUI project and toolpath saved and reviewed: 11098 seconds, 63.32 g;121 preview layer heights, whiteA2 only. Dispatched after user confirmed plate clear.

## Dispatch — 24 September

P1S3DP-01P-994 received **V48_Display_Original_Mounts_Seat_Up_Test**.
A2 cotton white, timelapse and auto bed leveling OFF verified in Send dialog.
Device confirms matching job active at0/121, heating and loading filament,
with estimated finish16:15 local. Camera live. First layer and completion
not yet verified; see `print_dispatch.json`. Original mount positions retained.

## Quality feedback during printing

User reports fraying on the opposite face. Device still printing103/121 when
checked; final surface quality remains unverified. See
[PRINT_QUALITY_FEEDBACK.md](PRINT_QUALITY_FEEDBACK.md) for the actual settings,
uncertainty and small-coupon checks required before final enclosure printing.
