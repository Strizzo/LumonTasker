"""Glass-bearing recessed seat with integral rear retention arms.

V43 incorrectly left clearance under the glass and used the metal lugs for
inward support. V44 closes that gap. Defaults produce nominal reference variants;
explicit --glass-mm with --measured records the user's measured baseline.
Bands outside the bearing perimeter are checked with a conservative
interior envelope; exact position is unnecessary for that seat-clearance check.
No slicer, printer or Fusion actions are performed by this script.
"""
from pathlib import Path
import copy
import argparse
import json
import math
import build123d as b
import trimesh

ROOT = Path(__file__).resolve().parents[2]
PREV = ROOT / 'cad/output/v43_integral_display_mounts'
BASE, CX = 33., 109.48
CZ = BASE + (201 - 16 - BASE) / math.cos(math.radians(25)) / 2
GX, GZ = CX - 193 / 2, CZ - 111 / 2
GLASS_FRONT, LUG_PLANE = 1., 6.96

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--glass-mm', nargs='+', type=float, default=[.7, 1.1])
parser.add_argument('--measured', action='store_true')
parser.add_argument('--local-band-total-mm', type=float)
parser.add_argument('--seat-width-mm', type=float, default=2.)
parser.add_argument('--output', type=Path, default=ROOT / 'cad/output/v44_bearing_seat')
parser.add_argument('--band-clear-border-mm', type=float,
                    help='Width of rear glass border explicitly confirmed clear of the band')
parser.add_argument('--band-clear-of-seat', action='store_true',
                    help='Legacy confirmation of outermost 2 mm only; does not confirm a wider seat')
args = parser.parse_args()
assert all(0 < t < 1.5 for t in args.glass_mm)
assert not args.measured or len(args.glass_mm) == 1
assert not args.band_clear_of_seat or (args.measured and args.local_band_total_mm is not None)
assert 0 < args.seat_width_mm < 8
assert args.band_clear_border_mm is None or 0 < args.band_clear_border_mm < 8
assert not (args.band_clear_of_seat and args.band_clear_border_mm is not None)
OUT = args.output if args.output.is_absolute() else ROOT / args.output
OUT.mkdir(exist_ok=True)
SEAT = args.seat_width_mm
CONFIRMED_BORDER = args.band_clear_border_mm if args.band_clear_border_mm is not None else (2. if args.band_clear_of_seat else None)
BAND_SEAT_CLEAR = CONFIRMED_BORDER is not None and CONFIRMED_BORDER >= SEAT


def box(x, y, z, w, d, h):
    return b.Pos(x+w/2, y+d/2, z+h/2) * b.Box(w, d, h)


def cy(x, y, z, d, h):
    return b.Pos(x, y+h/2, z) * b.Rot(-90, 0, 0) * b.Cylinder(d/2, h)


def rounded(x, y, z, w, d, h, r):
    return b.Pos(x+w/2, y, z+h/2) * b.Rot(-90, 0, 0) * b.extrude(b.RectangleRounded(w, h, r), amount=d)


def rake(s):
    return b.Pos(0, 0, BASE) * b.Rot(-25, 0, 0) * b.Pos(0, 0, -BASE) * s


def vol(s):
    return sum(q.volume for q in s.solids()) if s else 0.


parts_before = {s.label: s for s in b.import_step(PREV / 'whole_enclosure_review.step').children}
lug_centres = json.loads((PREV / 'audit.json').read_text())['lug_centres_local_xz']
reports = {}
for thickness in args.glass_mm:
    name = f'glass_{thickness:.1f}'.replace('.', 'p')
    dest = OUT / name
    dest.mkdir(exist_ok=True)
    print(f'Checking {name}: {"measured glass baseline" if args.measured else "nominal reference"}', flush=True)
    parts = {n: copy.deepcopy(s) for n, s in parts_before.items()}
    old_tub = parts['tub_left']
    seat_y = GLASS_FRONT + thickness
    # Extend the existing shoulder towards the glass. Its front surface is
    # exactly the glass-back datum. The full selected bearing width has the
    # same material depth down to y4.1, including newly widened material.
    # No material overlaps the front of the glass and no gasket is assumed.
    extension = rounded(GX-2.2, seat_y, GZ-2.2, 197.4, 4.1-seat_y, 115.4, 10.2)
    extension -= rounded(GX+SEAT, seat_y-.01, GZ+SEAT, 193-2*SEAT, 4.12-seat_y, 111-2*SEAT, 8-SEAT)
    tub = old_tub + rake(extension)
    assert tub.is_valid and len(tub.solids()) == 1
    parts['tub_left'] = tub
    glass = rounded(GX, GLASS_FRONT, GZ, 193, thickness, 111, 8)
    chassis = box(GX+12, seat_y, GZ+3.35, 166.2, LUG_PLANE-seat_y, 100.6)
    pi = box(GX+51.12, LUG_PLANE, GZ+30.65, 85, 41-LUG_PLANE, 56)
    refs = {'REFERENCE_glass': glass, 'REFERENCE_chassis_nominal': chassis,
            'REFERENCE_attached_Pi_nominal': pi}
    hardware_clashes = {n: vol(tub & rake(s)) for n, s in refs.items()}
    assert all(v < .01 for v in hardware_clashes.values()), hardware_clashes

    # Directly test the corrected requirement with the glass ALONE, without
    # metal lugs, Pi or any screws. Inward displacement meets the bearing ring.
    contact_slab = rounded(GX, seat_y, GZ, 193, .02, 111, 8)
    bearing = contact_slab & extension
    contact_area = vol(bearing) / .02
    full_bearing_fraction = vol(tub & rake(bearing)) / vol(bearing)
    full_depth_bearing = rounded(GX, seat_y, GZ, 193, 4.1-seat_y, 111, 8)
    full_depth_bearing -= rounded(GX+SEAT, seat_y-.01, GZ+SEAT, 193-2*SEAT, 4.12-seat_y, 111-2*SEAT, 8-SEAT)
    full_depth_bearing_fraction = vol(tub & rake(full_depth_bearing)) / vol(full_depth_bearing)
    assert full_depth_bearing_fraction > .999
    inward_collision = vol(tub & rake(b.Pos(0, .05, 0) * glass))
    outward_collision = vol(tub & rake(b.Pos(0, -.05, 0) * glass))
    assert contact_area > 1000 and full_bearing_fraction > .999
    assert inward_collision > 40 and outward_collision < .01
    side_contacts = {}
    for side, probe in {
        'left': box(GX, seat_y, GZ+30, SEAT-.1, .02, 50),
        'right': box(GX+193-SEAT+.1, seat_y, GZ+30, SEAT-.1, .02, 50),
        'lower': box(GX+40, seat_y, GZ, 100, .02, SEAT-.1),
        'upper': box(GX+40, seat_y, GZ+111-SEAT+.1, 100, .02, SEAT-.1),
    }.items():
        side_contacts[side] = vol(tub & rake(probe)) / vol(probe)
    assert min(side_contacts.values()) > .999

    # The integral mounts stay fixed during insertion; sweeps end at the
    # bearing seat, not beyond it. Test both glass variants independently.
    sweeps = {
        'glass': rounded(GX, -100, GZ, 193, 100+seat_y, 111, 8),
        'chassis_nominal': box(GX+12, -100, GZ+3.35, 166.2, 100+LUG_PLANE, 100.6),
        'Pi_nominal': box(GX+51.12, -100, GZ+30.65, 85, 141, 56),
    }
    sweep_clashes = {n: {pn: v for pn, p in parts.items() if (v := vol(rake(s) & p)) > .1}
                    for n, s in sweeps.items()}
    assert not any(sweep_clashes.values()), sweep_clashes
    band_checks = None
    if CONFIRMED_BORDER is not None:
        # Check only the border width actually confirmed by the user.
        # A wider requested seat can overlap this conservative envelope;
        # that is unresolved possible interference, not observed actual contact.
        # Check that entire inset area, including 0.3 mm extra rearward space;
        # this is a keepout, not an invented model of the unidentified band.
        band_excess = args.local_band_total_mm - thickness
        assert band_excess >= 0
        band_margin = .3
        k = CONFIRMED_BORDER
        band_envelope = rounded(GX+k, seat_y, GZ+k, 193-2*k, band_excess+band_margin, 111-2*k, 8-k)
        band_sweep = rounded(GX+k, -100, GZ+k, 193-2*k, 100+seat_y+band_excess+band_margin, 111-2*k, 8-k)
        seated_hits = {pn: v for pn, p in parts.items() if (v := vol(rake(band_envelope) & p)) > .01}
        sweep_hits = {pn: v for pn, p in parts.items() if (v := vol(rake(band_sweep) & p)) > .01}
        if BAND_SEAT_CLEAR:
            assert not seated_hits and not sweep_hits, (seated_hits, sweep_hits)
        band_checks = {'basis': f'User confirms band excludes outermost {k:g} mm of rear glass border',
                       'envelope': f'Entire glass area inset {k:g} mm, R{8-k:g}; conservative keepout only',
                       'interpretation': 'Clearance verified' if BAND_SEAT_CLEAR else 'Possible overlap only; wider seat needs additional band information',
                       'rearward_margin_mm': band_margin,
                       'local_y_range_mm': [seat_y, seat_y+band_excess+band_margin],
                       'seated_case_collisions_mm3': seated_hits,
                       'front_sweep_case_collisions_mm3': sweep_hits}
    part_clashes = {n: v for n, s in parts.items()
                    if n != 'tub_left' and (v := vol(tub & s)) > .1}
    assert not part_clashes, part_clashes
    hole_checks = {}
    for x, z in lug_centres:
        bore = cy(x, LUG_PLANE-.001, z, 3.39, 9)
        recess = cy(x, 10.861, z, 6.49, 5.05)
        land = cy(x, LUG_PLANE, z, 9.9, .15) - cy(x, LUG_PLANE-.001, z, 3.41, .152)
        hole_checks[f'{x:.2f},{z:.2f}'] = {
            'bore_obstruction_mm3': vol(tub & rake(bore)),
            'counterbore_obstruction_mm3': vol(tub & rake(recess)),
            'bearing_land_fraction': vol(tub & rake(land)) / vol(land)}
    assert all(v['bore_obstruction_mm3'] < .01 and v['counterbore_obstruction_mm3'] < .01
               and v['bearing_land_fraction'] > .999 for v in hole_checks.values())
    cable = rake(box(GX+41.12, 42, GZ+20.65, 105, 20, 76))
    pi_margin = rake(box(GX+46.12, LUG_PLANE, GZ+25.65, 95, 42-LUG_PLANE, 66))
    assert vol(tub & pi_margin) < .1
    tub.label = 'tub_left'
    b.export_step(tub, dest / 'tub_left.step')
    b.export_stl(tub, dest / 'tub_left_assembly.stl', tolerance=.035)
    assert trimesh.load_mesh(dest / 'tub_left_assembly.stl').is_watertight
    for n, s in parts.items():
        s.label = n
        s.color = b.Color('#173B53' if n in ('foot_left', 'foot_right_bonded', 'logo') else '#F0F1EB')
    b.export_step(b.Compound(children=[copy.deepcopy(s) for s in parts.values()]), dest / 'whole_enclosure_review.step')
    ref_parts = []
    for n, s in refs.items():
        r = rake(s)
        r.label = n
        r.color = b.Color('#17262F' if n == 'REFERENCE_glass' else '#969EA4')
        ref_parts.append(r)
    b.export_step(b.Compound(children=[copy.deepcopy(s) for s in [*parts.values(), *ref_parts]]), dest / 'whole_enclosure_with_hardware.step')
    report = {
        'status': ('Measured glass seat selected; band seat clearance checked; full case still not print-ready'
                   if BAND_SEAT_CLEAR else 'Measured glass baseline; wider seat band clearance unresolved; not print-ready'
                   if args.measured else 'Conditional CAD candidate only; actual glass thickness and physical lug stack unconfirmed'),
        'glass_thickness_assumption_mm': thickness, 'glass_front_y_mm': GLASS_FRONT,
        'glass_thickness_source': 'User measurement, mostly 0.8 mm' if args.measured else 'Nominal manufacturer variant',
        'local_band': {'reported_total_thickness_mm': args.local_band_total_mm,
                       'excess_over_glass_mm': args.local_band_total_mm-thickness if args.local_band_total_mm else None,
                       'identity': 'Unidentified black band; user suggests a data connection',
                       'location_known': False,
                       'clear_border_width_confirmed_by_user_mm': CONFIRMED_BORDER,
                       'seat_clearance_verified': BAND_SEAT_CLEAR,
                       'included_in_hardware_or_sweep_checks': CONFIRMED_BORDER is not None,
                       'clearance_checks': band_checks,
                       'exact_band_geometry_modelled': False},
        'seat_y_mm': seat_y, 'gap_behind_glass_mm': 0., 'seat_overlap_under_glass_mm': SEAT,
        'seat_material_thickness_mm': 4.1-seat_y, 'bearing_contact_area_mm2': contact_area,
        'full_depth_bearing_material_fraction': full_depth_bearing_fraction,
        'seat_contact_fraction': full_bearing_fraction, 'side_bearing_fractions': side_contacts,
        'glass_alone_0p05mm_inward_collision_mm3': inward_collision,
        'glass_alone_0p05mm_outward_collision_mm3': outward_collision,
        'recessed_opening_mm': [193.4, 111.4], 'opening_R_mm': 8.2,
        'front_overlap_mm': 0, 'separate_bezel': False, 'metal_lug_plane_y_mm': LUG_PLANE,
        'lug_centres_local_xz': lug_centres, 'retention_screws': 4,
        'screw_nominal': 'M3x6; 3.9 mm plastic bearing pad, 2.1 mm engagement before any physical shim correction',
        'mount_depth_relation': 'Seat and lug lands touch the nominal assembly simultaneously; screws must not draw across a gap',
        'hardware_clashes_mm3': hardware_clashes, 'front_sweep_clashes_mm3': sweep_clashes,
        'part_clashes_mm3': part_clashes, 'lug_hole_checks': hole_checks,
        'body_valid': True, 'body_solid_count': 1, 'body_watertight': True,
        'added_body_volume_vs_v43_mm3': vol(tub)-vol(old_tub),
        'provisional_cable_divider_clash_mm3': vol(tub & cable),
        'physical_checks_remaining': ([] if BAND_SEAT_CLEAR else [
            (f'Confirm band avoids outer {SEAT:g} mm bearing perimeter; add local relief if it overlaps'
             if args.measured else 'Measure actual glass-only edge thickness to select or regenerate seat depth')]) + [
            'Confirm display metal lug pattern and simultaneous bearing with glass freely resting on seat',
            'Inspect printed bearing for high spots/warp; never pull the glass into place with screws',
            'Correct any rear lug gap with measured rigid shims or revised pads, then recalculate screw engagement',
            'No gasket thickness assumed; adding bedding requires updating the seat and lug stack together'],
        'release_holds': ([] if BAND_SEAT_CLEAR else [
            ('Raised-band bearing overlap/clearance unconfirmed' if args.measured else 'Actual glass thickness unconfirmed')]) + ['Physical mounting stack unconfirmed',
                          'Power/cable layout unresolved', 'Screw access and full-body slicing pending'],
        'fusion_synced': False, 'print_dispatched': False}
    (dest / 'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    reports[name] = report
    print(f'{name}: valid/watertight; seat supports glass alone; front entry clear', flush=True)

index_path = OUT / 'variants.json'
index = json.loads(index_path.read_text()) if index_path.exists() else {
    'selected_variant': None, 'actual_glass_thickness_mm': None, 'variants': {}}
index['variants'].update({n: {'glass_mm': r['glass_thickness_assumption_mm'], 'seat_y_mm': r['seat_y_mm']}
                          for n, r in reports.items()})
if args.measured:
    index.update({'selected_variant': name if BAND_SEAT_CLEAR else None, 'measured_baseline_variant': name,
                  'requested_seat_width_mm': SEAT,
                  'band_clear_border_confirmed_mm': CONFIRMED_BORDER,
                  'actual_glass_thickness_mm': thickness,
                  'local_band_total_thickness_mm': args.local_band_total_mm,
                  'selection_requires': None if BAND_SEAT_CLEAR else 'Resolve local raised-band bearing overlap/clearance before selecting final geometry',
                  'selection_scope': 'Seat geometry only; full-case physical fit and print review remain pending',
                  'print_released': False})
index_path.write_text(json.dumps(index, indent=2)+'\n')
print('CAD prepared; print release remains on hold.', flush=True)
