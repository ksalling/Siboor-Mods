"""Fast 2D cross-section and hole-pattern analyzer for Siboor Lineux Mod.

Uses ONLY cached BREP solids in `cache/siboor_lineux/` and 2D planar sections
(`BRepAlgoAPI_Section`) plus analytical cylindrical surface inspection.
"""

import json
import os
from PIL import Image, ImageDraw
from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Builder
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepTools import BRepTools
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
from OCP.gp import gp_Dir, gp_Pln, gp_Pnt, gp_Trsf, gp_Vec
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS, TopoDS_Shape

CACHE_DIR = "cache/siboor_lineux"
# Translation from siboorCNC.step raw frame to LineuxCarriage.step world frame:
# MGN12H hole center X: 0.0 -> 126.70 (+126.70)
# MGN12H mating plane Y: 0.24 -> 169.50 (+169.26)
# MGN12H hole center Z: 360.0 -> 58.319 (-301.681)
SIBOOR_TO_LINEUX_VEC = (126.70, 169.26, -301.681)


def load_brep(path: str) -> TopoDS_Shape:
    shape = TopoDS_Shape()
    builder = BRep_Builder()
    BRepTools.Read_s(shape, path, builder)
    return shape


def translate_shape(shape: TopoDS_Shape, dx: float, dy: float, dz: float) -> TopoDS_Shape:
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(dx, dy, dz))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def get_bbox(shape: TopoDS_Shape):
    bbox = Bnd_Box()
    BRepBndLib.Add_s(shape, bbox)
    return [round(x, 3) for x in bbox.Get()]


def inspect_cylinders(shape: TopoDS_Shape):
    cyls = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        surf = BRepAdaptor_Surface(face, True)
        if surf.GetType() == GeomAbs_Cylinder:
            cyl = surf.Cylinder()
            r = round(cyl.Radius(), 3)
            ax = cyl.Axis()
            d = ax.Direction()
            bbox = get_bbox(face)
            cyls.append(
                {
                    "r": r,
                    "d": round(2 * r, 3),
                    "axis": [round(d.X(), 3), round(d.Y(), 3), round(d.Z(), 3)],
                    "center": [
                        round((bbox[0] + bbox[3]) / 2, 3),
                        round((bbox[1] + bbox[4]) / 2, 3),
                        round((bbox[2] + bbox[5]) / 2, 3),
                    ],
                    "bbox": bbox,
                }
            )
        exp.Next()
    return cyls


def section_wires_2d(shape: TopoDS_Shape, axis: str, val: float):
    if axis == "X":
        pln = gp_Pln(gp_Pnt(val, 0, 0), gp_Dir(1, 0, 0))
    elif axis == "Y":
        pln = gp_Pln(gp_Pnt(0, val, 0), gp_Dir(0, 1, 0))
    elif axis == "Z":
        pln = gp_Pln(gp_Pnt(0, 0, val), gp_Dir(0, 0, 1))
    else:
        raise ValueError(axis)

    sec = BRepAlgoAPI_Section(shape, pln, False)
    sec.Build()
    if not sec.IsDone():
        return []
    res = sec.Shape()
    segments = []
    exp = TopExp_Explorer(res, TopAbs_EDGE)
    while exp.More():
        edge = TopoDS.Edge_s(exp.Current())
        curve = BRepAdaptor_Curve(edge)
        defl = GCPnts_QuasiUniformDeflection(curve, 0.05)
        if defl.IsDone() and defl.NbPoints() >= 2:
            pts = []
            for i in range(1, defl.NbPoints() + 1):
                p = defl.Value(i)
                if axis == "X":
                    pts.append((round(p.Y(), 3), round(p.Z(), 3)))
                elif axis == "Y":
                    pts.append((round(p.X(), 3), round(p.Z(), 3)))
                elif axis == "Z":
                    pts.append((round(p.X(), 3), round(p.Y(), 3)))
            segments.append(pts)
        exp.Next()
    return segments


def render_2d_sections(out_dir: str):
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
    cbase = load_brep(carriage_meta["carriage_base"]["brep"])
    carr = load_brep(carriage_meta["carriage"]["brep"])
    aduct = load_brep(carriage_meta["[a]_duct"]["brep"])
    dext = load_brep(carriage_meta["duct_extension"]["brep"])
    tool = load_brep(tool_meta["[a]_toolhead"]["brep"])
    shroud = load_brep(tool_meta["[a]_v6chp_shroud_mount"]["brep"])

    print("Siboor aligned bbox:", get_bbox(siboor_body))
    print("carriage_base bbox:", carriage_meta["carriage_base"]["bbox"])
    print("carriage bbox:", carriage_meta["carriage"]["bbox"])
    print("[a]_duct bbox:", carriage_meta["[a]_duct"]["bbox"])
    print("duct_extension bbox:", carriage_meta["duct_extension"]["bbox"])

    print("\n--- SIBOOR ALIGNED SCREW HOLES ---")
    seen = set()
    for c in sorted(inspect_cylinders(siboor_body), key=lambda x: (-x["center"][2], x["center"][0])):
        if c["r"] in [1.0, 1.23, 1.5, 1.55, 1.8]:
            k = (
                c["r"],
                tuple(abs(x) for x in c["axis"]),
                round(c["center"][0], 1),
                round(c["center"][1], 1),
                round(c["center"][2], 1),
            )
            if k not in seen:
                seen.add(k)
                dx = round(c["center"][0] - 126.70, 2)
                print(
                    f"d={c['d']:.2f}mm (r={c['r']}) axis={c['axis']} | "
                    f"X={c['center'][0]:.2f} (dX={dx:+.2f}), "
                    f"Y={c['bbox'][1]:.2f}..{c['bbox'][4]:.2f}, "
                    f"Z={c['center'][2]:.2f} (Z={c['bbox'][2]:.2f}..{c['bbox'][5]:.2f})"
                )

    print("\n--- CARRIAGE SCREW HOLES (attaching to carriage_base / [a]_duct / standoffs) ---")
    seen_c = set()
    for c in sorted(inspect_cylinders(carr), key=lambda x: (-x["center"][2], x["center"][0])):
        if 1.0 <= c["r"] <= 2.6:
            k = (
                c["r"],
                tuple(abs(x) for x in c["axis"]),
                round(c["center"][0], 1),
                round(c["center"][1], 1),
                round(c["center"][2], 1),
            )
            if k not in seen_c:
                seen_c.add(k)
                dx = round(c["center"][0] - 126.70, 2)
                print(
                    f"d={c['d']:.2f}mm axis={c['axis']} | "
                    f"X={c['center'][0]:.2f} (dX={dx:+.2f}), "
                    f"Y={c['bbox'][1]:.2f}..{c['bbox'][4]:.2f}, "
                    f"Z={c['center'][2]:.2f}"
                )

    # Render 2D YZ cross-sections at X = 126.70 (centerline airflow) and X = 142.20 (Siboor mounting standoff)
    W, H = 1600, 1000
    img = Image.new("RGB", (W, H), (18, 20, 26))
    draw = ImageDraw.Draw(img)

    def to_px(y, z, x_offset=0):
        # y in [115..205], z in [-5..145]
        scale = 5.5
        px = int(x_offset + (y - 115.0) * scale)
        py = int(H - 60 - (z + 5.0) * scale)
        return (px, py)

    panels = [
        ("X = 126.70 mm (Centerline Airflow Section)", 126.70, 40),
        ("X = 142.20 mm (Siboor Standoff / Wing Section)", 142.20, 820),
    ]
    parts = [
        ("MGN12H", mgn, (140, 145, 155), 2),
        ("stock carriage_base", cbase, (90, 130, 255), 2),
        ("siboorCNC (aligned)", siboor_body, (255, 70, 90), 3),
        ("carriage", carr, (80, 220, 120), 2),
        ("[a]_duct", aduct, (255, 200, 30), 2),
        ("duct_extension", dext, (0, 220, 240), 3),
        ("[a]_toolhead", tool, (200, 130, 255), 1),
        ("hotend_shroud", shroud, (170, 110, 210), 1),
    ]

    for title, x_val, x_off in panels:
        # grid lines
        for y_grid in range(120, 205, 10):
            p1 = to_px(y_grid, -5, x_off)
            p2 = to_px(y_grid, 145, x_off)
            draw.line([p1, p2], fill=(35, 40, 50), width=1)
            draw.text((p1[0] - 10, H - 45), f"Y={y_grid}", fill=(130, 140, 160))
        for z_grid in range(0, 145, 10):
            p1 = to_px(115, z_grid, x_off)
            p2 = to_px(200, z_grid, x_off)
            draw.line([p1, p2], fill=(35, 40, 50), width=1)
            draw.text((x_off, p1[1] - 6), f"Z={z_grid}", fill=(130, 140, 160))

        draw.text((x_off + 10, 15), title, fill=(240, 240, 250))
        for pname, pshape, col, width in parts:
            segs = section_wires_2d(pshape, "X", x_val)
            for seg in segs:
                pts = [to_px(y, z, x_off) for y, z in seg]
                if len(pts) >= 2:
                    draw.line(pts, fill=col, width=width)

    # Legend
    lx = 50
    for pname, _, col, _ in parts:
        draw.rectangle([lx, H - 22, lx + 18, H - 10], fill=col)
        draw.text((lx + 24, H - 23), pname, fill=(220, 225, 235))
        lx += 185

    out_path = os.path.join(out_dir, "siboor_lineux_2d_cross_section.png")
    img.save(out_path)
    print(f"\nSaved 2D cross-section plot to {out_path}")


if __name__ == "__main__":
    render_2d_sections(
        r"C:\Users\ksall\.gemini\antigravity\brain\fb7972a7-fa05-4a46-93ba-b2edb764e327"
    )
