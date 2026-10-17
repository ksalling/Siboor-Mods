"""2D Cross-Section Verification & Diagnostic Plotter for Variant A and Variant B.

Slices all generated BREP solids and assembly components using 2D planes ONLY
(`BRepAlgoAPI_Section`) to verify:
- Sealed airflow path from `duct_extension` to bottom nozzle outlets of `[a]_duct`
- Preserved/expanded airflow cross-sectional area
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
from src.siboor_lineux.generator import CARRIAGE_DY


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
    tool = translate_shape(load_brep(tool_meta["[a]_toolhead"]["brep"]), 0, CARRIAGE_DY, 0)
    shroud = translate_shape(
        load_brep(tool_meta["[a]_v6chp_shroud_mount"]["brep"]), 0, CARRIAGE_DY, 0
    )
    stepper = translate_shape(
        load_brep(carriage_meta["Nema 14 Stepper"]["brep"]), 0, CARRIAGE_DY, 0
    )
    ledm = translate_shape(load_brep(carriage_meta["led_mount"]["brep"]), 0, CARRIAGE_DY, 0)
    carto = translate_shape(
        load_brep(carriage_meta["cartographer_mount"]["brep"]), 0, CARRIAGE_DY, 0
    )

    gen_dir = f"{CACHE_DIR}/generated"
    va_carr = load_brep(f"{gen_dir}/Variant_A_Modular_Carriage_carriage.brep")
    va_aduct = load_brep(f"{gen_dir}/Variant_A_Modular_Carriage_a_duct.brep")
    va_dext = load_brep(f"{gen_dir}/Variant_A_Modular_Carriage_duct_extension.brep")
    va_scarto = load_brep(f"{gen_dir}/Variant_A_Modular_Carriage_siboor_cartographer_mount.brep")

    vb_carr = load_brep(f"{gen_dir}/Variant_B_Integrated_Duct_carriage.brep")
    vb_aduct = load_brep(f"{gen_dir}/Variant_B_Integrated_Duct_a_duct.brep")
    vb_dext = load_brep(f"{gen_dir}/Variant_B_Integrated_Duct_duct_extension.brep")
    vb_scarto = load_brep(f"{gen_dir}/Variant_B_Integrated_Duct_siboor_cartographer_mount.brep")

    W, H = 1800, 1100
    img = Image.new("RGB", (W, H), (16, 18, 24))
    draw = ImageDraw.Draw(img)

    def to_px(y, z, x_off=0, y_top=40):
        scale = 5.6
        px = int(x_off + (y - 95.0) * scale)
        py = int(y_top + 860 - (z + 8.0) * scale)
        return (px, py)

    panels = [
        (
            "Variant A (Modular Carriage) — Centerline Airflow Section (X = 126.70 mm)",
            126.70,
            40,
            [
                ("MGN12H", mgn, (130, 135, 145), 2),
                ("siboorCNC", siboor_body, (255, 70, 90), 3),
                ("carriage (mod)", va_carr, (70, 220, 120), 2),
                ("[a]_duct (mod)", va_aduct, (255, 200, 30), 2),
                ("duct_extension (mod)", va_dext, (0, 220, 240), 3),
                ("led_mount", ledm, (255, 140, 60), 2),
                ("cartographer_mount", carto, (140, 170, 255), 1),
                ("siboor_carto_mount", va_scarto, (255, 110, 200), 2),
                ("LineuxTool", tool, (190, 120, 255), 1),
                ("hotend_shroud", shroud, (160, 100, 210), 1),
            ],
        ),
        (
            "Variant B (Forked Integrated [a]_duct) — Centerline Airflow Section (X = 126.70 mm)",
            126.70,
            920,
            [
                ("MGN12H", mgn, (130, 135, 145), 2),
                ("siboorCNC", siboor_body, (255, 70, 90), 3),
                ("carriage (mod)", vb_carr, (70, 220, 120), 2),
                ("[a]_duct (expanded)", vb_aduct, (255, 200, 30), 3),
                ("duct_extension (mod)", vb_dext, (0, 220, 240), 3),
                ("led_mount", ledm, (255, 140, 60), 2),
                ("cartographer_mount", carto, (140, 170, 255), 1),
                ("siboor_carto_mount", vb_scarto, (255, 110, 200), 2),
                ("LineuxTool", tool, (190, 120, 255), 1),
                ("hotend_shroud", shroud, (160, 100, 210), 1),
            ],
        ),
    ]

    for title, x_val, x_off, p_list in panels:
        for yg in range(100, 210, 10):
            p1 = to_px(yg, -5, x_off)
            p2 = to_px(yg, 145, x_off)
            draw.line([p1, p2], fill=(32, 36, 46), width=1)
            if yg % 20 == 0:
                draw.text((p1[0] - 14, H - 70), f"Y={yg}", fill=(130, 140, 160))
        for zg in range(0, 145, 10):
            p1 = to_px(95, zg, x_off)
            p2 = to_px(205, zg, x_off)
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
                arm_segs = section_wires_2d(pshape, "X", 112.00)
                for seg in arm_segs:
                    if all(z <= 44.5 for _, z in seg):
                        pts = [to_px(y, z, x_off) for y, z in seg]
                        if len(pts) >= 2:
                            draw.line(pts, fill=(215, 155, 25), width=2)

    # Legend at bottom
    lx = 40
    for pname, _, col, _ in panels[0][3]:
        draw.rectangle([lx, H - 35, lx + 16, H - 21], fill=col)
        draw.text((lx + 22, H - 36), pname, fill=(220, 225, 235))
        lx += 170

    out_path = os.path.join(out_dir, "siboor_lineux_variants_ab_centerline_2d.png")
    img.save(out_path)
    print(f"Saved {out_path}")

    # Second image: Z-slices (Top-down XY views) at Z=73.02, Z=58.32, Z=29.72 for Variant A and Variant B
    img2 = Image.new("RGB", (W, H), (16, 18, 24))
    draw2 = ImageDraw.Draw(img2)

    z_levels = [
        ("Z = 73.02 mm (Upper Standoffs & Plenum)", 73.02, 310),
        ("Z = 58.32 mm (Mid-Carriage & Vertical Air Channel)", 58.32, 660),
        ("Z = 29.72 mm (Lower Standoffs, [a]_duct, LED & Cartographer)", 29.72, 1010),
    ]
    for col_idx, (vtitle, x_off, vparts) in enumerate(
        [
            (
                "Variant A (Modular Carriage)",
                60,
                [
                    ("siboorCNC", siboor_body, (255, 70, 90), 3),
                    ("carriage", va_carr, (70, 220, 120), 2),
                    ("[a]_duct", va_aduct, (255, 200, 30), 2),
                    ("duct_extension", va_dext, (0, 220, 240), 2),
                    ("led_mount", ledm, (255, 140, 60), 2),
                    ("carto_mount", carto, (140, 170, 255), 1),
                    ("LineuxTool", tool, (190, 120, 255), 1),
                ],
            ),
            (
                "Variant B (Forked Integrated [a]_duct)",
                940,
                [
                    ("siboorCNC", siboor_body, (255, 70, 90), 3),
                    ("carriage", vb_carr, (70, 220, 120), 2),
                    ("[a]_duct (expanded)", vb_aduct, (255, 200, 30), 3),
                    ("duct_extension", vb_dext, (0, 220, 240), 2),
                    ("led_mount", ledm, (255, 140, 60), 2),
                    ("carto_mount", carto, (140, 170, 255), 1),
                    ("LineuxTool", tool, (190, 120, 255), 1),
                ],
            ),
        ]
    ):
        for zlabel, zval, y_base in z_levels:
            def to_px_xy(x, y):
                return (int(x_off + (x - 95.0) * 11.5), int(y_base - (185.0 - y) * 4.2))

            draw2.text((x_off, y_base - 290), f"{vtitle} — {zlabel}", fill=(240, 242, 250))
            for xg in range(100, 160, 10):
                draw2.line([to_px_xy(xg, 120), to_px_xy(xg, 185)], fill=(32, 36, 46), width=1)
            for yg in range(120, 190, 10):
                draw2.line([to_px_xy(95, yg), to_px_xy(160, yg)], fill=(32, 36, 46), width=1)
                draw2.text((x_off - 42, to_px_xy(95, yg)[1] - 6), f"Y={yg}", fill=(120, 130, 150))

            for pname, pshape, col, w in vparts:
                for seg in section_wires_2d(pshape, "Z", zval):
                    pts = [to_px_xy(x, y) for x, y in seg if 115 <= y <= 188]
                    if len(pts) >= 2:
                        draw2.line(pts, fill=col, width=w)

    out_path2 = os.path.join(out_dir, "siboor_lineux_variants_ab_xy_slices_2d.png")
    img2.save(out_path2)
    print(f"Saved {out_path2}")


if __name__ == "__main__":
    render_variant_comparison(
        r"C:\Users\ksall\.gemini\antigravity\brain\fb7972a7-fa05-4a46-93ba-b2edb764e327"
    )
