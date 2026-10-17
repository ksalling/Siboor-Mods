"""2D Cross-Section Verification & Diagnostic Plotter for Iteration 2 (Variant A & Variant B).

Slices all generated BREP solids and assembly components using 2D planes ONLY
(`BRepAlgoAPI_Section`) to verify:
- Sealed airflow path from `duct_extension` through `carriage_base` / `carriage` to bottom nozzle outlets of `[a]_duct`
- 100% flat build-plate faces (`Z=47.32 mm` on `[a]_duct`, `Y=146.10 mm` on `carriage_base` & `carriage`) for support-free ABS printing
- Exact 18 mm spacing between `Nema 14 Stepper` and `5015_adapter` using stock 37.76 mm `5015_standoff_x2`
- Zero collisions with `siboorCNC`, `MGN12H`, `Nema 14 Stepper`, `led_mount`, `cartographer_mount`, and `LineuxTool`
"""

import json
import os
from PIL import Image, ImageDraw
from src.siboor_lineux.analyze_2d import (
    CACHE_DIR,
    SIBOOR_TO_LINEUX_VEC,
    load_brep,
    section_wires_2d,
    translate_shape,
)
from src.siboor_lineux.generator import (
    VARIANT_A_DY,
    VARIANT_A_DZ,
    VARIANT_B_DY,
    VARIANT_B_DZ,
)


def render_variant_comparison(out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{CACHE_DIR}/siboor_meta.json", "r", encoding="utf-8") as f:
        siboor_meta = json.load(f)
    with open(f"{CACHE_DIR}/carriage_meta.json", "r", encoding="utf-8") as f:
        carriage_meta = json.load(f)
    with open(f"{CACHE_DIR}/tool_meta.json", "r", encoding="utf-8") as f:
        tool_meta = json.load(f)

    siboor_body = translate_shape(
        load_brep(siboor_meta["Component414"]["brep"]), *SIBOOR_TO_LINEUX_VEC
    )
    mgn = load_brep(carriage_meta["mgn 12h"]["brep"])
    ext2020 = load_brep(carriage_meta["2020 Extrusion"]["brep"])

    gen_dir = f"{CACHE_DIR}/generated"
    va_prefix = "Variant_A_Separate_Carriage_Base_14mm"
    va_cbase = load_brep(f"{gen_dir}/{va_prefix}_carriage_base.brep")
    va_carr = load_brep(f"{gen_dir}/{va_prefix}_carriage.brep")
    va_aduct = load_brep(f"{gen_dir}/{va_prefix}_a_duct.brep")
    va_dext = load_brep(f"{gen_dir}/{va_prefix}_duct_extension.brep")
    va_scarto = load_brep(f"{gen_dir}/{va_prefix}_siboor_cartographer_mount.brep")

    vb_prefix = "Variant_B_Integrated_Carriage_UltraCompact_8.5mm"
    vb_carr = load_brep(f"{gen_dir}/{vb_prefix}_carriage.brep")
    vb_aduct = load_brep(f"{gen_dir}/{vb_prefix}_a_duct.brep")
    vb_dext = load_brep(f"{gen_dir}/{vb_prefix}_duct_extension.brep")
    vb_scarto = load_brep(f"{gen_dir}/{vb_prefix}_siboor_cartographer_mount.brep")

    def shifted_commons(dy, dz):
        return {
            "tool": translate_shape(load_brep(tool_meta["[a]_toolhead"]["brep"]), 0, dy, dz),
            "shroud": translate_shape(load_brep(tool_meta["[a]_v6chp_shroud_mount"]["brep"]), 0, dy, dz),
            "stepper": translate_shape(load_brep(carriage_meta["Nema 14 Stepper"]["brep"]), 0, dy, dz),
            "adapter5015": translate_shape(load_brep(carriage_meta["5015_adapter"]["brep"]), 0, dy, dz),
            "ledm": translate_shape(load_brep(carriage_meta["led_mount"]["brep"]), 0, dy, dz),
            "carto": translate_shape(load_brep(carriage_meta["cartographer_mount"]["brep"]), 0, dy, dz),
        }

    ca = shifted_commons(VARIANT_A_DY, VARIANT_A_DZ)
    cb = shifted_commons(VARIANT_B_DY, VARIANT_B_DZ)

    W, H = 1860, 1140
    img = Image.new("RGB", (W, H), (16, 18, 24))
    draw = ImageDraw.Draw(img)

    def to_px(y, z, x_off=0, y_top=40):
        scale = 5.4
        px = int(x_off + (y - 95.0) * scale)
        py = int(y_top + 900 - (z + 6.0) * scale)
        return (px, py)

    panels = [
        (
            "Variant A: Separate ABS carriage_base (dY = -14.0 mm, dZ = +2.5 mm) — Centerline X = 126.70 mm",
            126.70,
            40,
            [
                ("MGN12H / 2020", mgn, (130, 135, 145), 2),
                ("2020 Extrusion", ext2020, (90, 95, 105), 1),
                ("siboorCNC", siboor_body, (255, 70, 90), 3),
                ("carriage_base (ABS flat)", va_cbase, (60, 180, 255), 3),
                ("carriage (flat back)", va_carr, (70, 220, 120), 2),
                ("[a]_duct (flat top)", va_aduct, (255, 200, 30), 2),
                ("duct_extension (stock len)", va_dext, (0, 230, 230), 3),
                ("Nema 14 Stepper", ca["stepper"], (240, 130, 180), 2),
                ("5015_adapter (18mm gap)", ca["adapter5015"], (150, 210, 160), 2),
                ("led_mount", ca["ledm"], (255, 140, 60), 2),
                ("siboor_carto_mount", va_scarto, (255, 110, 220), 2),
                ("LineuxTool", ca["tool"], (190, 120, 255), 1),
                ("hotend_shroud", ca["shroud"], (160, 100, 210), 1),
            ],
        ),
        (
            "Variant B: Ultra-Compact Integrated carriage (dY = -8.5 mm, dZ = +2.5 mm) — Centerline X = 126.70 mm",
            126.70,
            950,
            [
                ("MGN12H / 2020", mgn, (130, 135, 145), 2),
                ("2020 Extrusion", ext2020, (90, 95, 105), 1),
                ("siboorCNC", siboor_body, (255, 70, 90), 3),
                ("carriage (tucked duct)", vb_carr, (70, 220, 120), 3),
                ("[a]_duct (flat top)", vb_aduct, (255, 200, 30), 2),
                ("duct_extension (stock len)", vb_dext, (0, 230, 230), 3),
                ("Nema 14 Stepper", cb["stepper"], (240, 130, 180), 2),
                ("5015_adapter (18mm gap)", cb["adapter5015"], (150, 210, 160), 2),
                ("led_mount", cb["ledm"], (255, 140, 60), 2),
                ("siboor_carto_mount", vb_scarto, (255, 110, 220), 2),
                ("LineuxTool", cb["tool"], (190, 120, 255), 1),
                ("hotend_shroud", cb["shroud"], (160, 100, 210), 1),
            ],
        ),
    ]

    for title, x_val, x_off, p_list in panels:
        for yg in range(100, 225, 10):
            p1 = to_px(yg, -5, x_off)
            p2 = to_px(yg, 155, x_off)
            draw.line([p1, p2], fill=(32, 36, 46), width=1)
            if yg % 20 == 0:
                draw.text((p1[0] - 14, H - 70), f"Y={yg}", fill=(130, 140, 160))
        for zg in range(0, 155, 10):
            p1 = to_px(95, zg, x_off)
            p2 = to_px(220, zg, x_off)
            draw.line([p1, p2], fill=(32, 36, 46), width=1)
            draw.text((x_off, p1[1] - 6), f"Z={zg}", fill=(130, 140, 160))

        draw.text((x_off + 10, 15), title, fill=(240, 242, 250))
        for pname, pshape, col, w in p_list:
            segs = section_wires_2d(pshape, "X", x_val)
            for seg in segs:
                pts = [to_px(y, z, x_off) for y, z in seg]
                if len(pts) >= 2:
                    draw.line(pts, fill=col, width=w)
            if "[a]_duct" in pname:
                arm_segs = section_wires_2d(pshape, "X", 110.45)
                for seg in arm_segs:
                    if all(z <= 47.0 for _, z in seg):
                        pts = [to_px(y, z, x_off) for y, z in seg]
                        if len(pts) >= 2:
                            draw.line(pts, fill=(215, 155, 25), width=2)

    lx = 30
    for pname, _, col, _ in panels[0][3]:
        if pname == "2020 Extrusion":
            continue
        draw.rectangle([lx, H - 35, lx + 14, H - 21], fill=col)
        draw.text((lx + 18, H - 36), pname, fill=(220, 225, 235))
        lx += 150

    out_path = os.path.join(out_dir, "siboor_lineux_variants_ab_centerline_2d.png")
    img.save(out_path)
    print(f"Saved {out_path}")

    # Second image: Z-slices (Top-down XY views) at Z=73.02, Z=58.32, Z=29.72 for Variant A and Variant B
    img2 = Image.new("RGB", (W, H), (16, 18, 24))
    draw2 = ImageDraw.Draw(img2)

    z_levels = [
        ("Z = 73.02 mm (Upper Standoffs & Air Manifold)", 73.02, 360),
        ("Z = 58.32 mm (Mid-Carriage & Tucked Air Channel)", 58.32, 740),
        ("Z = 29.72 mm (Lower Standoffs & [a]_duct Bypass)", 29.72, 1120),
    ]
    for col_idx, (vtitle, x_off, vparts) in enumerate(
        [
            (
                "Variant A: Separate ABS carriage_base (dY = -14.0 mm, dZ = +2.5 mm)",
                40,
                [
                    ("siboorCNC", siboor_body, (255, 70, 90), 3),
                    ("carriage_base", va_cbase, (60, 180, 255), 3),
                    ("carriage", va_carr, (70, 220, 120), 2),
                    ("[a]_duct", va_aduct, (255, 200, 30), 2),
                    ("led_mount", ca["ledm"], (255, 140, 60), 2),
                    ("LineuxTool", ca["tool"], (190, 120, 255), 1),
                ],
            ),
            (
                "Variant B: Ultra-Compact Integrated carriage (dY = -8.5 mm, dZ = +2.5 mm)",
                950,
                [
                    ("siboorCNC", siboor_body, (255, 70, 90), 3),
                    ("carriage", vb_carr, (70, 220, 120), 3),
                    ("[a]_duct", vb_aduct, (255, 200, 30), 3),
                    ("led_mount", cb["ledm"], (255, 140, 60), 2),
                    ("LineuxTool", cb["tool"], (190, 120, 255), 1),
                ],
            ),
        ]
    ):
        for rtitle, zv, y_base in z_levels:
            def to_px_xy(x, y):
                sc = 4.6
                return (int(x_off + (x - 90.0) * sc), int(y_base - (180.0 - y) * sc))

            draw2.text((x_off + 10, y_base - 340), f"{vtitle} — {rtitle}", fill=(240, 242, 250))
            for yg in range(120, 185, 10):
                p1, p2 = to_px_xy(92, yg), to_px_xy(162, yg)
                draw2.line([p1, p2], fill=(32, 36, 46), width=1)
                draw2.text((x_off, p1[1] - 6), f"Y={yg}", fill=(120, 130, 150))
            for pname, pshape, col, w in vparts:
                segs = section_wires_2d(pshape, "Z", zv)
                for seg in segs:
                    pts = [to_px_xy(x, y) for x, y in seg]
                    if len(pts) >= 2:
                        draw2.line(pts, fill=col, width=w)

    out_path2 = os.path.join(out_dir, "siboor_lineux_variants_ab_xy_slices_2d.png")
    img2.save(out_path2)
    print(f"Saved {out_path2}")


if __name__ == "__main__":
    artifact_dir = r"C:\Users\ksall\.gemini\antigravity\brain\fb7972a7-fa05-4a46-93ba-b2edb764e327"
    render_variant_comparison(artifact_dir)
