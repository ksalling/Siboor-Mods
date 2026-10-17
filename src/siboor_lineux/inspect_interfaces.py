"""Inspect all screw holes and mating interfaces of carriage, [a]_duct, duct_extension, standoffs, cartographer_mount, and led_mount."""

import json
from src.siboor_lineux.analyze_2d import (
    CACHE_DIR,
    SIBOOR_TO_LINEUX_VEC,
    get_bbox,
    inspect_cylinders,
    load_brep,
    section_wires_2d,
    translate_shape,
)

with open(f"{CACHE_DIR}/siboor_meta.json", "r", encoding="utf-8") as f:
    siboor_meta = json.load(f)
with open(f"{CACHE_DIR}/carriage_meta.json", "r", encoding="utf-8") as f:
    carriage_meta = json.load(f)

siboor_body = translate_shape(
    load_brep(siboor_meta["Component414"]["brep"]), *SIBOOR_TO_LINEUX_VEC
)

for name in [
    "carriage_base",
    "carriage",
    "[a]_duct",
    "duct_extension",
    "5015_standoff_x2",
    "5015_standoff_x2 (1)",
    "cartographer_mount",
    "led_mount",
]:
    sh = load_brep(carriage_meta[name]["brep"])
    print(f"\n=== {name} bbox={get_bbox(sh)} ===")
    seen = set()
    for c in sorted(inspect_cylinders(sh), key=lambda x: (-x["center"][2], x["center"][0])):
        if 0.9 <= c["r"] <= 3.5:
            k = (
                c["r"],
                tuple(abs(x) for x in c["axis"]),
                round(c["center"][0], 1),
                round(c["center"][1], 1),
                round(c["center"][2], 1),
            )
            if k not in seen:
                seen.add(k)
                print(
                    f"  d={c['d']:.2f} axis={c['axis']} center={c['center']} bbox={c['bbox']}"
                )
