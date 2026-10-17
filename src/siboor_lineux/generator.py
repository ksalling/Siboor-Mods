"""Parametric CAD generator for the Siboor Lineux Mod (Variant A and Variant B).

Generates:
1. Siboor Lineux Mod/Variant_A_Modular_Carriage/{CAD,STL}:
   - carriage.{step,stl}
   - [a]_duct.{step,stl}
   - duct_extension.{step,stl}
   - 5015_standoff_x2.{step,stl}
   - 5015_standoff_x2 (1).{step,stl}
   - siboor_cartographer_mount.{step,stl}
   - Siboor_Lineux_Carriage_Assembly.step (without tool)
   - Siboor_Lineux_Carriage_With_Tool_Assembly.step (with tool)

2. Siboor Lineux Mod/Variant_B_Integrated_Duct/{CAD,STL}:
   - [a]_duct.{step,stl}
   - carriage.{step,stl}
   - duct_extension.{step,stl}
   - 5015_standoff_x2.{step,stl}
   - 5015_standoff_x2 (1).{step,stl}
   - siboor_cartographer_mount.{step,stl}
   - Siboor_Lineux_Carriage_Assembly.step (without tool)
   - Siboor_Lineux_Carriage_With_Tool_Assembly.step (with tool)
"""

import json
import os
import time
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.StlAPI import StlAPI_Writer
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDocStd import TDocStd_Document
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS_Shape
from OCP.XCAFDoc import XCAFDoc_ColorType, XCAFDoc_DocumentTool

from src.siboor_lineux.analyze_2d import (
    CACHE_DIR,
    SIBOOR_TO_LINEUX_VEC,
    get_bbox,
    load_brep,
    translate_shape,
)

# Core parametric configuration
CARRIAGE_DY = -18.0  # Forward shift in mm (Option A)
OUTPUT_ROOT = "Siboor Lineux Mod"

COLOR_PRIMARY = [0.0097, 0.0097, 0.0097]
COLOR_ACCENT = [0.7605, 0.6514, 0.0009]


def make_box(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> TopoDS_Shape:
    p1 = gp_Pnt(min(x1, x2), min(y1, y2), min(z1, z2))
    p2 = gp_Pnt(max(x1, x2), max(y1, y2), max(z1, z2))
    return BRepPrimAPI_MakeBox(p1, p2).Shape()


def make_cyl_x(x1: float, x2: float, y: float, z: float, r: float) -> TopoDS_Shape:
    xmin, xmax = min(x1, x2), max(x1, x2)
    ax = gp_Ax2(gp_Pnt(xmin, y, z), gp_Dir(1, 0, 0))
    return BRepPrimAPI_MakeCylinder(ax, r, xmax - xmin).Shape()


def make_cyl_y(x: float, z: float, y1: float, y2: float, r: float) -> TopoDS_Shape:
    ymin, ymax = min(y1, y2), max(y1, y2)
    ax = gp_Ax2(gp_Pnt(x, ymin, z), gp_Dir(0, 1, 0))
    return BRepPrimAPI_MakeCylinder(ax, r, ymax - ymin).Shape()


def make_cyl_z(x: float, y: float, z1: float, z2: float, r: float) -> TopoDS_Shape:
    zmin, zmax = min(z1, z2), max(z1, z2)
    ax = gp_Ax2(gp_Pnt(x, y, zmin), gp_Dir(0, 0, 1))
    return BRepPrimAPI_MakeCylinder(ax, r, zmax - zmin).Shape()


def fuse_shapes(shapes: list[TopoDS_Shape]) -> TopoDS_Shape:
    res = shapes[0]
    for s in shapes[1:]:
        f = BRepAlgoAPI_Fuse(res, s)
        f.SetFuzzyValue(1e-3)
        f.Build()
        res = f.Shape()
    return res


def cut_shapes(base: TopoDS_Shape, cutters: list[TopoDS_Shape]) -> TopoDS_Shape:
    res = base
    for c in cutters:
        op = BRepAlgoAPI_Cut(res, c)
        op.SetFuzzyValue(1e-3)
        op.Build()
        res = op.Shape()
    return res


def count_solids(sh: TopoDS_Shape) -> int:
    exp = TopExp_Explorer(sh, TopAbs_SOLID)
    n = 0
    while exp.More():
        n += 1
        exp.Next()
    return n


def build_lengthened_standoff(raw_standoff: TopoDS_Shape, dy: float = CARRIAGE_DY) -> TopoDS_Shape:
    """Lengthens 5015_standoff_x2 by |dy| mm while preserving both end caps and M3 insert holes."""
    rear_keep = BRepAlgoAPI_Common(
        raw_standoff, make_box(80.0, 178.5, 100.0, 170.0, 210.0, 150.0)
    ).Shape()
    front_part = BRepAlgoAPI_Common(
        raw_standoff, make_box(80.0, 155.0, 100.0, 170.0, 179.5, 150.0)
    ).Shape()
    front_shifted = translate_shape(front_part, 0, dy, 0)
    mid_slice = BRepAlgoAPI_Common(
        raw_standoff, make_box(80.0, 169.0, 100.0, 170.0, 189.0, 150.0)
    ).Shape()
    mid_bridge = translate_shape(mid_slice, 0, dy / 2.0, 0)
    return fuse_shapes([front_shifted, mid_bridge, rear_keep])


def build_siboor_mount_bridge(
    front_y: float = 149.5, include_lower_bridge: bool = False
) -> tuple[list[TopoDS_Shape], list[TopoDS_Shape]]:
    """Returns (add_solids, cut_drill_solids) for the structural bridge from front_y to siboorCNC."""
    adds = []
    cuts = []

    # 1. Upper forward standoff bosses (mate flush to Siboor CNC at Y=155.00, X=111.20 & 142.20, Z=73.019)
    adds.append(make_box(106.5, 147.0, 69.2, 115.2, 155.0, 76.2))
    adds.append(make_box(138.2, min(front_y, 141.5), 69.2, 146.9, 155.0, 76.2))

    # 2. Main structural columns mating to Siboor CNC main plate at Y=165.10 (Z=44.5..69.5)
    adds.append(make_box(114.2, front_y, 44.5, 121.8, 165.10, 69.5))
    adds.append(make_box(131.6, front_y, 44.5, 139.2, 165.10, 69.5))

    # 3. Lower outer plate structural ribs mating to Siboor CNC at Y=165.10 (X=108.75, 144.65, Z=43.27)
    adds.append(make_box(105.0, front_y, 38.5, 114.5, 165.10, 45.5))
    adds.append(make_box(138.9, front_y, 38.5, 148.4, 165.10, 45.5))

    # 4. Optional lower bridge web mating to Siboor CNC lower bridge at Y=165.10 (X=121.45, 131.95, Z=39.05)
    if include_lower_bridge:
        adds.append(make_box(118.5, front_y, 36.8, 134.9, 165.10, 42.5))

    # --- DRILL HOLES & CLEARANCES ---
    # A. Keep internal airflow channel 100% clear (X=119.68..133.72, Y=143.30..150.30, Z=44.0..79.62)
    cuts.append(make_box(119.68, 143.30, 44.0, 133.72, 150.30, 79.62))

    # B. Keep micro switch pocket clear on left (X=105.5..118.9, Y=130.0..146.8, Z=71.8..78.4)
    cuts.append(make_box(105.5, 130.0, 71.8, 118.9, 146.8, 78.4))

    # C. Upper forward standoff M3 holes (X=111.20, 142.20, Z=73.019)
    for x in (111.20, 142.20):
        cuts.append(make_cyl_y(x, 73.019, 125.0, 170.0, 1.65))
        cuts.append(make_cyl_y(x, 73.019, 125.0, 149.5, 3.10))

    # D. Inner plate 4x M3 holes on Siboor CNC (X=118.70, 134.70, Z=65.819 & 50.819)
    for x in (118.70, 134.70):
        for z in (65.819, 50.819):
            cuts.append(make_cyl_y(x, z, 125.0, 170.0, 1.65))
            cuts.append(make_cyl_y(x, z, 125.0, 157.0, 3.10))

    # E. Hex-driver access & head clearance for Siboor's 4x MGN12H M3x8 screws (X=116.70, 136.70, Z=68.319 & 48.319)
    for x in (116.70, 136.70):
        for z in (68.319, 48.319):
            cuts.append(make_cyl_y(x, z, 125.0, 166.0, 3.35))

    # F. Lower outer plate M3 holes (X=108.75, 144.65, Z=43.269)
    for x in (108.75, 144.65):
        cuts.append(make_cyl_y(x, 43.269, 143.0, 170.0, 1.65))
        cuts.append(make_cyl_y(x, 43.269, 143.0, 157.0, 3.10))

    # G. Lower bridge M3 holes (X=121.45, 131.95, Z=39.049)
    if include_lower_bridge:
        for x in (121.45, 131.95):
            cuts.append(make_cyl_y(x, 39.049, 150.5, 170.0, 1.65))

    # H. Side M3 holes at Z=41.569 for [a]_duct side tabs in Variant A
    cuts.append(make_cyl_x(103.0, 111.0, 146.8, 41.569, 1.70))
    cuts.append(make_cyl_x(142.4, 150.4, 146.8, 41.569, 1.70))

    # I. Belt clamp screw head clearance at X=107.20, 146.20, Z=58.319
    for x in (107.20, 146.20):
        cuts.append(make_cyl_y(x, 58.319, 150.0, 170.0, 4.0))

    return adds, cuts


def build_extended_duct_extension(raw_dext: TopoDS_Shape, target_front_y: float) -> TopoDS_Shape:
    """Extends duct_extension forward from Y=169.50 to target_front_y with a sealed internal spigot."""
    dy_ext = target_front_y - 169.50
    front_part = translate_shape(
        BRepAlgoAPI_Common(raw_dext, make_box(100.0, 169.4, 70.0, 155.0, 185.0, 90.0)).Shape(),
        0,
        dy_ext,
        0,
    )
    siboor_ear_clear_l = make_box(100.0, 162.2, 70.0, 116.2, 170.0, 90.0)
    siboor_ear_clear_r = make_box(137.2, 162.2, 70.0, 155.0, 170.0, 90.0)
    front_part = cut_shapes(front_part, [siboor_ear_clear_l, siboor_ear_clear_r])
    rear_part = BRepAlgoAPI_Common(
        raw_dext, make_box(100.0, 171.0, 70.0, 155.0, 200.0, 90.0)
    ).Shape()

    tube_outer = make_box(118.50, target_front_y + 0.5, 73.40, 134.90, 174.0, 81.80)
    spigot_flange = make_box(
        118.60, target_front_y - 0.1, 73.50, 134.80, target_front_y + 2.0, 81.50
    )
    spigot_lip = make_box(
        119.75, target_front_y - 2.2, 74.60, 133.65, target_front_y + 0.5, 80.30
    )
    comb = fuse_shapes([rear_part, front_part, tube_outer, spigot_flange, spigot_lip])

    air_main = make_box(119.68, target_front_y + 0.5, 74.55, 133.72, 175.0, 80.37)
    air_spigot = make_box(
        120.55, target_front_y - 3.0, 75.35, 132.85, target_front_y + 1.5, 79.55
    )
    hole_rl = make_cyl_y(110.50, 81.319, 168.0, 199.0, 1.65)
    hole_rr = make_cyl_y(142.90, 81.319, 168.0, 199.0, 1.65)
    return cut_shapes(comb, [air_main, air_spigot, hole_rl, hole_rr])


def build_siboor_cartographer_mount() -> TopoDS_Shape:
    """Builds the optional direct Siboor CNC bottom-leg Cartographer mount."""
    pillar_l = make_box(107.40, 163.80, 1.524, 114.40, 170.80, 14.52)
    pillar_r = make_box(139.00, 163.80, 1.524, 146.00, 170.80, 14.52)
    crossbar = make_box(107.40, 163.80, 1.524, 146.00, 170.80, 8.50)
    body = fuse_shapes([pillar_l, pillar_r, crossbar])

    pcb_relief = make_box(115.00, 163.00, 1.00, 138.40, 171.50, 5.50)
    hole_l = make_cyl_z(110.90, 167.30, 0.0, 16.0, 1.65)
    hole_r = make_cyl_z(142.50, 167.30, 0.0, 16.0, 1.65)
    cb_l = make_cyl_z(110.90, 167.30, 0.0, 9.52, 3.10)
    cb_r = make_cyl_z(142.50, 167.30, 0.0, 9.52, 3.10)
    return cut_shapes(body, [pcb_relief, hole_l, hole_r, cb_l, cb_r])


def build_variant_a_parts(carriage_meta: dict) -> dict[str, TopoDS_Shape]:
    """Builds all modified parts for Variant_A_Modular_Carriage."""
    raw_carr = load_brep(carriage_meta["carriage"]["brep"])
    raw_aduct = load_brep(carriage_meta["[a]_duct"]["brep"])
    raw_dext = load_brep(carriage_meta["duct_extension"]["brep"])
    raw_st1 = load_brep(carriage_meta["5015_standoff_x2"]["brep"])
    raw_st2 = load_brep(carriage_meta["5015_standoff_x2 (1)"]["brep"])

    # 1. Clean analytic manifold + Siboor mounting bridge fused onto shifted carriage:
    carr_sh = translate_shape(raw_carr, 0, CARRIAGE_DY, 0)
    manifold_main = make_box(103.70, 141.50, 38.24, 149.70, 151.50, 81.93)
    ear_l = make_box(108.48, 141.50, 78.82, 115.50, 151.50, 85.73)
    ear_r = make_box(137.90, 141.50, 78.82, 144.92, 151.50, 85.73)
    bridge_adds, bridge_cuts = build_siboor_mount_bridge(
        front_y=149.50, include_lower_bridge=False
    )
    rear_struct = fuse_shapes([manifold_main, ear_l, ear_r] + bridge_adds)

    bot_arch_cut = make_box(109.50, 142.15, 37.00, 143.90, 152.00, 44.82)
    inlet_cut = make_box(119.68, 149.00, 73.80, 133.72, 152.50, 79.62)
    dext_ins_l = make_cyl_y(111.98, 81.569, 142.0, 152.5, 1.70)
    dext_ins_r = make_cyl_y(141.42, 81.569, 142.0, 152.5, 1.70)
    rear_struct = cut_shapes(
        rear_struct, bridge_cuts + [bot_arch_cut, inlet_cut, dext_ins_l, dext_ins_r]
    )

    f_carr = BRepAlgoAPI_Fuse(carr_sh, rear_struct)
    f_carr.SetFuzzyValue(1e-3)
    f_carr.Build()
    carr_mod = cut_shapes(f_carr.Shape(), bridge_cuts)

    # 2. Modified `[a]_duct` (Variant A):
    aduct_sh = translate_shape(raw_aduct, 0, CARRIAGE_DY, 0)
    # Upward telescopic sealing spigot & collar (pre-hollowed analytically before fusing)
    spigot_flange = make_box(118.40, 142.10, 43.20, 135.00, 151.50, 44.90)
    spigot_lip = make_box(119.72, 143.34, 43.20, 133.68, 150.26, 46.40)
    spigot_add = fuse_shapes([spigot_flange, spigot_lip])
    spigot_inner_air = make_box(120.52, 144.14, 42.00, 132.88, 149.46, 47.50)
    spigot_ring = cut_shapes(spigot_add, [spigot_inner_air])

    # Lower standoff mounting bosses at X=110.45, 142.95, Z=29.719 extending to Y=155.00
    low_boss_l = cut_shapes(
        make_box(106.95, 148.50, 26.50, 113.95, 155.00, 32.95),
        [make_cyl_y(110.45, 29.719, 150.2, 156.0, 1.45)],
    )
    low_boss_r = cut_shapes(
        make_box(139.45, 148.50, 26.50, 146.45, 155.00, 32.95),
        [make_cyl_y(142.95, 29.719, 150.2, 156.0, 1.45)],
    )
    # Lower bridge mounting web at X=121.45, 131.95, Z=39.049 extending from Y=149.80 to Y=165.10
    low_bridge_web = cut_shapes(
        make_box(118.50, 149.80, 36.80, 134.90, 165.10, 41.80),
        [
            make_cyl_y(121.45, 39.049, 150.5, 166.0, 1.45),
            make_cyl_y(131.95, 39.049, 150.5, 166.0, 1.45),
        ],
    )

    aduct_mod = aduct_sh
    for add_part in [spigot_ring, low_boss_l, low_boss_r, low_bridge_web]:
        f_op = BRepAlgoAPI_Fuse(aduct_mod, add_part)
        f_op.Build()
        aduct_mod = f_op.Shape()

    # 3. Modified `duct_extension` (Variant A):
    dext_mod = build_extended_duct_extension(raw_dext, target_front_y=151.50)

    # 4. Lengthened standoffs:
    st1_mod = build_lengthened_standoff(raw_st1, CARRIAGE_DY)
    st2_mod = build_lengthened_standoff(raw_st2, CARRIAGE_DY)

    # 5. Optional direct Siboor CNC Cartographer mount:
    siboor_carto = build_siboor_cartographer_mount()

    return {
        "carriage": carr_mod,
        "[a]_duct": aduct_mod,
        "duct_extension": dext_mod,
        "5015_standoff_x2": st1_mod,
        "5015_standoff_x2 (1)": st2_mod,
        "siboor_cartographer_mount": siboor_carto,
    }


def build_variant_b_parts(carriage_meta: dict) -> dict[str, TopoDS_Shape]:
    """Builds all modified parts for Variant_B_Integrated_Duct (Forked Integrated [a]_duct)."""
    raw_carr = load_brep(carriage_meta["carriage"]["brep"])
    raw_aduct = load_brep(carriage_meta["[a]_duct"]["brep"])
    raw_dext = load_brep(carriage_meta["duct_extension"]["brep"])
    raw_st1 = load_brep(carriage_meta["5015_standoff_x2"]["brep"])
    raw_st2 = load_brep(carriage_meta["5015_standoff_x2 (1)"]["brep"])

    # 1. Forked Expanded `[a]_duct` (pre-hollowed upper plenum + Siboor mounting bridge fused onto aduct_sh):
    aduct_sh = translate_shape(raw_aduct, 0, CARRIAGE_DY, 0)

    collar_outer = make_box(106.30, 142.10, 43.20, 147.10, 151.50, 46.20)
    wing_fill_l = make_box(104.10, 142.10, 44.50, 118.80, 151.50, 81.93)
    wing_fill_r = make_box(134.60, 142.10, 44.50, 149.30, 151.50, 81.93)
    front_plenum_wall = make_box(117.50, 142.10, 44.50, 135.90, 151.50, 82.50)
    expanded_plenum_box = make_box(117.50, 149.50, 41.50, 135.90, 159.50, 82.50)
    top_ear_l = make_box(108.48, 142.10, 78.82, 118.50, 159.50, 85.73)
    top_ear_r = make_box(134.90, 142.10, 78.82, 144.92, 159.50, 85.73)

    bridge_adds, bridge_cuts = build_siboor_mount_bridge(
        front_y=150.5, include_lower_bridge=True
    )

    upper_solid = fuse_shapes(
        [
            collar_outer,
            wing_fill_l,
            wing_fill_r,
            front_plenum_wall,
            expanded_plenum_box,
            top_ear_l,
            top_ear_r,
        ]
        + bridge_adds
    )

    high_vol_cavity = make_box(119.68, 143.30, 44.85, 133.72, 157.50, 79.62)
    top_inlet_port = make_box(119.68, 156.50, 73.80, 133.72, 160.50, 79.62)
    throat_opening = make_box(119.68, 143.30, 42.00, 133.72, 150.30, 46.50)
    side_arch_clear_l = make_box(109.50, 142.00, 42.00, 118.40, 150.40, 44.82)
    side_arch_clear_r = make_box(135.00, 142.00, 42.00, 143.90, 150.40, 44.82)
    dext_insert_l = make_cyl_y(111.98, 81.569, 142.00, 160.00, 1.70)
    dext_insert_r = make_cyl_y(141.42, 81.569, 142.00, 160.00, 1.70)

    upper_hollow = cut_shapes(
        upper_solid,
        bridge_cuts
        + [
            high_vol_cavity,
            top_inlet_port,
            throat_opening,
            side_arch_clear_l,
            side_arch_clear_r,
            dext_insert_l,
            dext_insert_r,
        ],
    )

    low_boss_l = cut_shapes(
        make_box(106.95, 148.50, 26.50, 113.95, 155.00, 32.95),
        [make_cyl_y(110.45, 29.719, 150.2, 156.0, 1.45)],
    )
    low_boss_r = cut_shapes(
        make_box(139.45, 148.50, 26.50, 146.45, 155.00, 32.95),
        [make_cyl_y(142.95, 29.719, 150.2, 156.0, 1.45)],
    )

    aduct_integrated = aduct_sh
    for add_part in [upper_hollow, low_boss_l, low_boss_r]:
        f_op = BRepAlgoAPI_Fuse(aduct_integrated, add_part)
        f_op.Build()
        aduct_integrated = f_op.Shape()

    # 2. Modified `carriage` (Variant B):
    carr_sh = translate_shape(raw_carr, 0, CARRIAGE_DY, 0)
    carr_cuts = []
    for x in (118.70, 134.70):
        for z in (65.819, 50.819):
            carr_cuts.append(make_cyl_y(x, z, 125.0, 145.0, 1.65))
            carr_cuts.append(make_cyl_y(x, z, 125.0, 139.0, 3.10))
    carr_cuts.append(make_cyl_y(142.20, 73.019, 125.0, 145.0, 1.65))
    carr_cuts.append(make_cyl_y(142.20, 73.019, 125.0, 139.0, 3.10))
    carr_mod_b = cut_shapes(carr_sh, carr_cuts)

    # 3. Modified `duct_extension` (Variant B):
    dext_mod_b = build_extended_duct_extension(raw_dext, target_front_y=159.50)

    # 4. Lengthened standoffs:
    st1_mod = build_lengthened_standoff(raw_st1, CARRIAGE_DY)
    st2_mod = build_lengthened_standoff(raw_st2, CARRIAGE_DY)

    # 5. Optional direct Siboor CNC Cartographer mount:
    siboor_carto = build_siboor_cartographer_mount()

    return {
        "[a]_duct": aduct_integrated,
        "carriage": carr_mod_b,
        "duct_extension": dext_mod_b,
        "5015_standoff_x2": st1_mod,
        "5015_standoff_x2 (1)": st2_mod,
        "siboor_cartographer_mount": siboor_carto,
    }


def export_stl(shape: TopoDS_Shape, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    BRepMesh_IncrementalMesh(shape, 0.08, False, 0.2, True)
    writer = StlAPI_Writer()
    writer.Write(shape, path)


def export_step_single(shape: TopoDS_Shape, name: str, color_rgb: list[float], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    color_tool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

    lbl = shape_tool.AddShape(shape, False)
    TDataStd_Name.Set_s(lbl, TCollection_ExtendedString(name))
    c = Quantity_Color(color_rgb[0], color_rgb[1], color_rgb[2], Quantity_TOC_RGB)
    color_tool.SetColor(lbl, c, XCAFDoc_ColorType.XCAFDoc_ColorGen)
    color_tool.SetColor(lbl, c, XCAFDoc_ColorType.XCAFDoc_ColorSurf)

    writer = STEPCAFControl_Writer()
    writer.SetColorMode(True)
    writer.SetNameMode(True)
    writer.Transfer(doc)
    writer.Write(path)


def export_step_assembly(items: list[tuple[str, TopoDS_Shape, list[float] | None]], path: str):
    """Exports a multi-part colored STEP assembly preserving exact part names and RGB colors."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    color_tool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

    for name, shape, color_rgb in items:
        lbl = shape_tool.AddShape(shape, False)
        TDataStd_Name.Set_s(lbl, TCollection_ExtendedString(name))
        if color_rgb:
            c = Quantity_Color(color_rgb[0], color_rgb[1], color_rgb[2], Quantity_TOC_RGB)
            color_tool.SetColor(lbl, c, XCAFDoc_ColorType.XCAFDoc_ColorGen)
            color_tool.SetColor(lbl, c, XCAFDoc_ColorType.XCAFDoc_ColorSurf)

    writer = STEPCAFControl_Writer()
    writer.SetColorMode(True)
    writer.SetNameMode(True)
    writer.Transfer(doc)
    writer.Write(path)


def build_assembly_items(
    mod_parts: dict[str, TopoDS_Shape],
    siboor_meta: dict,
    carriage_meta: dict,
    tool_meta: dict | None = None,
) -> list[tuple[str, TopoDS_Shape, list[float] | None]]:
    items: list[tuple[str, TopoDS_Shape, list[float] | None]] = []

    # 1. Fixed rail / extrusion / rear fan & adapter parts (unshifted)
    static_carriage_keys = [
        "2020 Extrusion",
        "mgn 12h rails 250mm",
        "mgn 12h",
        "B Belt",
        "A Belt",
        "5015_adapter",
        "pug_collar_front",
        "pug_collar_rear",
        "screw_spacer",
    ]
    for k in static_carriage_keys:
        if k in carriage_meta:
            items.append(
                (
                    carriage_meta[k]["name"],
                    load_brep(carriage_meta[k]["brep"]),
                    carriage_meta[k]["color"] or [0.65, 0.65, 0.68],
                )
            )

    # 2. Unmodified Siboor CNC assembly components (aligned to MGN12H)
    for k, v in siboor_meta.items():
        sh = translate_shape(load_brep(v["brep"]), *SIBOOR_TO_LINEUX_VEC)
        items.append((v["name"], sh, v["color"] or [0.95, 0.95, 0.98]))

    # 3. Modified parts
    for k, sh in mod_parts.items():
        col = COLOR_ACCENT if k.startswith("[a]") else COLOR_PRIMARY
        items.append((k, sh, col))

    # 4. Shifted front carriage components (move with carriage by CARRIAGE_DY)
    shifted_carriage_keys = [
        "gear_plate",
        "Nema 14 Stepper",
        "micro switch",
        "latch_plate",
        "[a]_latch",
        "led_mount",
        "led_cover",
        "diffuser",
        "cartographer_mount",
    ]
    for k in shifted_carriage_keys:
        if k in carriage_meta:
            sh = translate_shape(load_brep(carriage_meta[k]["brep"]), 0, CARRIAGE_DY, 0)
            items.append((carriage_meta[k]["name"], sh, carriage_meta[k]["color"] or COLOR_PRIMARY))

    # 5. Optional LineuxTool parts (shifted by CARRIAGE_DY)
    if tool_meta is not None:
        for k, v in tool_meta.items():
            sh = translate_shape(load_brep(v["brep"]), 0, CARRIAGE_DY, 0)
            items.append((v["name"], sh, v["color"] or COLOR_ACCENT))

    return items


def generate_all():
    t0 = time.time()
    with open(f"{CACHE_DIR}/siboor_meta.json", "r", encoding="utf-8") as f:
        siboor_meta = json.load(f)
    with open(f"{CACHE_DIR}/carriage_meta.json", "r", encoding="utf-8") as f:
        carriage_meta = json.load(f)
    with open(f"{CACHE_DIR}/tool_meta.json", "r", encoding="utf-8") as f:
        tool_meta = json.load(f)

    variants = [
        ("Variant_A_Modular_Carriage", build_variant_a_parts(carriage_meta)),
        ("Variant_B_Integrated_Duct", build_variant_b_parts(carriage_meta)),
    ]

    os.makedirs(f"{CACHE_DIR}/generated", exist_ok=True)
    from OCP.BRepTools import BRepTools

    for vname, parts in variants:
        print(f"\n=== Exporting {vname} ===")
        cad_dir = os.path.join(OUTPUT_ROOT, vname, "CAD")
        stl_dir = os.path.join(OUTPUT_ROOT, vname, "STL")
        os.makedirs(cad_dir, exist_ok=True)
        os.makedirs(stl_dir, exist_ok=True)

        for pname, pshape in parts.items():
            nsol = count_solids(pshape)
            bb = get_bbox(pshape)
            print(f"  {pname:28s} | solids={nsol} | bbox={bb}")
            col = COLOR_ACCENT if pname.startswith("[a]") else COLOR_PRIMARY
            step_path = os.path.join(cad_dir, f"{pname}.step")
            stl_path = os.path.join(stl_dir, f"{pname}.stl")
            export_step_single(pshape, pname, col, step_path)
            export_stl(pshape, stl_path)
            safe_p = pname.replace("[", "").replace("]", "").replace(" ", "_")
            BRepTools.Write_s(pshape, f"{CACHE_DIR}/generated/{vname}_{safe_p}.brep")

        # Export full assembly WITHOUT tool
        assy_no_tool = build_assembly_items(parts, siboor_meta, carriage_meta, tool_meta=None)
        export_step_assembly(
            assy_no_tool,
            os.path.join(cad_dir, "Siboor_Lineux_Carriage_Assembly.step"),
        )

        # Export full assembly WITH tool
        assy_with_tool = build_assembly_items(
            parts, siboor_meta, carriage_meta, tool_meta=tool_meta
        )
        export_step_assembly(
            assy_with_tool,
            os.path.join(cad_dir, "Siboor_Lineux_Carriage_With_Tool_Assembly.step"),
        )

    print(f"\nAll variants generated and exported in {time.time() - t0:.2f}s")


if __name__ == "__main__":
    generate_all()
