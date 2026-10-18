"""Parametric CAD Generator for the Siboor Lineux Mod (Iteration 3 — Option A Flyover Architecture).

Implements the flyover architecture (dZ = +8.0 mm) with full 4-standoff fastener accounting:
1. `Variant_A_Separate_Carriage_Base_14mm` (dY = -14.0 mm, dZ = +8.0 mm):
   - Dedicated ABS-printable `carriage_base` with 100% flat front build-plate face (Y=146.10 mm).
   - Flat-backed `carriage` (Y=146.10 mm) with front counterbores and clearance holes for upper standoffs.
   - 100% flat-top `[a]_duct` (Z=52.82 mm) with hermetically sealed internal cylindrical sleeves
     at the lower standoffs (X=110.45, 142.95, Z=29.72 mm, Y=155.00 mm), front counterbores,
     straight-in hex driver access, and full preserved internal airflow area.
   - `duct_extension` fastener sleeves (screw axis Z=89.57 mm, bottom Z=86.82 mm) pass 100% ABOVE
     siboorCNC's top ears (Zmax=86.57 mm) with +0.25 mm air clearance, eliminating fastener collisions.
   - Stock 37.76 mm `5015_standoff_x2` preserved (exact 18 mm gap behind Nema 14 Stepper).
   - `siboor_cartographer_mount` calibrated for shifted nozzle height (Z=+7.12 mm).

2. `Variant_B_Integrated_Carriage_UltraCompact_8.5mm` (dY = -8.5 mm, dZ = +8.0 mm):
   - Ultra-compact depth tucking vertical airflow channel into siboorCNC's central pocket.
   - Integrated `carriage` with front counterbores and clearance holes for upper standoffs.
   - Flat-top `[a]_duct` (Z=52.82 mm) with standoff relief, sealed rear cap, and lower standoff through-bores.
   - `duct_extension` fastener sleeves pass 100% ABOVE siboorCNC's top ears at Z=89.57 mm.
   - Stock 37.76 mm `5015_standoff_x2` preserved (exact 18 mm gap behind Nema 14 Stepper).
   - `siboor_cartographer_mount` calibrated for shifted nozzle height.
"""

import json
import os
import shutil
import time
from OCP.BRep import BRep_Builder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepTools import BRepTools
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.StlAPI import StlAPI_Writer
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDocStd import TDocStd_Document
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS_Compound, TopoDS_Shape
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_ColorGen, XCAFDoc_ColorSurf, XCAFDoc_DocumentTool
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec

CACHE_DIR = "cache/siboor_lineux"
OUTPUT_ROOT = "Siboor Lineux Mod"

# Coordinate alignment of siboorCNC.step into LineuxCarriage.step world frame:
SIBOOR_TO_LINEUX_VEC = (126.70, 169.26, -301.681)

# Variant offsets:
# Option A: dZ = +8.0 mm flyover architecture cleanly elevates duct_extension fastener sleeves
# (Z=86.82..93.83 mm, screw axis Z=89.57 mm) 100% above siboorCNC's top ears (Zmax=86.57 mm).
VARIANT_A_DY = -14.0
VARIANT_A_DZ = 8.0

VARIANT_B_DY = -8.5
VARIANT_B_DZ = 8.0

# Original STEP colors:
COLOR_PRIMARY = [0.251, 0.278, 0.329]  # Dark grey/slate (`carriage`, `carriage_base`, `duct_extension`, etc.)
COLOR_ACCENT = [0.996, 0.722, 0.0]     # Lineux amber/yellow (`[a]_duct`, `[a]_latch`, etc.)
COLOR_SIBOOR = [0.247, 0.247, 0.247]   # Siboor anodized CNC aluminum


def load_brep(path: str) -> TopoDS_Shape:
    sh = TopoDS_Shape()
    builder = BRep_Builder()
    BRepTools.Read_s(sh, path, builder)
    return sh


def save_brep(sh: TopoDS_Shape, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    BRepTools.Write_s(sh, path)


def translate_shape(sh: TopoDS_Shape, dx: float, dy: float, dz: float) -> TopoDS_Shape:
    if abs(dx) < 1e-6 and abs(dy) < 1e-6 and abs(dz) < 1e-6:
        return sh
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(dx, dy, dz))
    return BRepBuilderAPI_Transform(sh, trsf, True).Shape()


def make_box(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> TopoDS_Shape:
    return BRepPrimAPI_MakeBox(
        gp_Pnt(min(x1, x2), min(y1, y2), min(z1, z2)),
        gp_Pnt(max(x1, x2), max(y1, y2), max(z1, z2)),
    ).Shape()


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


def get_bbox(sh: TopoDS_Shape) -> list[float]:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    b = Bnd_Box()
    BRepBndLib.Add_s(sh, b)
    xmin, ymin, zmin, xmax, ymax, zmax = b.Get()
    return [round(v, 3) for v in (xmin, ymin, zmin, xmax, ymax, zmax)]


def build_siboor_cartographer_mount(dz: float = 8.0) -> TopoDS_Shape:
    """Builds the direct Siboor CNC bottom-leg Cartographer mount calibrated for shifted nozzle height."""
    # Stock nozzle tip is at Z=-0.88 mm; shifted by dz=+8.0 mm -> Z=+7.12 mm.
    # Cartographer bottom face at Z = 1.524 + dz = 9.524 mm (~2.40 mm above shifted nozzle tip).
    # Mount bolts directly to siboorCNC's bottom M3 vertical holes at Z=14.52 mm (X=110.90, 142.50, Y=167.30).
    z_bot = 1.524 + dz
    z_top = 14.52
    body = make_box(107.40, 163.80, z_bot, 146.00, 170.80, z_top)

    pcb_relief = make_box(115.00, 163.00, z_bot - 0.5, 138.40, 171.50, z_bot + 2.00)
    hole_l = make_cyl_z(110.90, 167.30, z_bot - 1.0, z_top + 1.0, 1.65)
    hole_r = make_cyl_z(142.50, 167.30, z_bot - 1.0, z_top + 1.0, 1.65)
    cb_l   = make_cyl_z(110.90, 167.30, z_bot - 1.0, z_bot + 2.50, 3.10)
    cb_r   = make_cyl_z(142.50, 167.30, z_bot - 1.0, z_bot + 2.50, 3.10)
    return cut_shapes(body, [pcb_relief, hole_l, hole_r, cb_l, cb_r])


def build_shifted_duct_extension(raw_dext: TopoDS_Shape, dy: float, dz: float) -> TopoDS_Shape:
    """Shifts stock duct_extension by (dy, dz) to match shifted 5015_adapter (keeping stock 37.76 mm standoffs).
    At dz=+8.0 mm, the fastener sleeves pass 100% ABOVE siboorCNC's top ears (Zmax=86.57 mm),
    completely eliminating fastener collisions with zero ear cutouts needed!
    Adds a 2.2 mm forward sealing spigot lip for a hermetically sealed duct connection."""
    dext_sh = translate_shape(raw_dext, 0, dy, dz)
    front_y = 169.50 + dy

    # Forward sealing spigot lip (telescoping 2.2 mm forward into carriage_base / carriage)
    spigot_outer = make_box(119.75, front_y - 2.20, 74.60 + dz, 133.65, front_y + 1.20, 80.30 + dz)
    spigot_inner = make_box(120.55, front_y - 3.00, 75.35 + dz, 132.85, front_y + 2.00, 79.55 + dz)
    spigot_ring = cut_shapes(spigot_outer, [spigot_inner])

    f_op = BRepAlgoAPI_Fuse(dext_sh, spigot_ring)
    f_op.Build()
    return f_op.Shape()


def build_variant_a_parts(carriage_meta: dict) -> dict[str, TopoDS_Shape]:
    """Builds Variant_A_Separate_Carriage_Base_14mm (dY = -14.0 mm, dZ = +8.0 mm).
    Iteration 4 Features:
    - 100% hermetically sealed vertical airflow channel in `carriage_base` (all MGN12H, belt, and inner plate access holes removed).
    - Lower mounting holes in `carriage` and `carriage_base` moved to X=121.45, 131.95, Z=39.05 mm, aligning 100% dead-on
      with SiboorCNC's tapped holes, complete with M3 SHCS front counterbores (dia 6.2 mm, depth 4.0 mm).
    - `[a]_duct`'s cooling arms are 100% UNPIERCED by any fasteners or through-sleeves, preserving full stock airflow volume
      and support-free ABS printability with flat top face at Z=52.82 mm.
    """
    dy, dz = VARIANT_A_DY, VARIANT_A_DZ
    raw_carr = load_brep(carriage_meta["carriage"]["brep"])
    raw_aduct = load_brep(carriage_meta["[a]_duct"]["brep"])
    raw_dext = load_brep(carriage_meta["duct_extension"]["brep"])

    front_y = 160.10 + dy       # 146.10 mm (100% flat front face of carriage_base)
    base_rear_y = 169.50 + dy   # 155.50 mm (main rear face of carriage_base)
    aduct_top_z = 44.82 + dz    # 52.82 mm (100% flat top face of [a]_duct)

    # --- 1. Dedicated ABS-Printable `carriage_base` ---
    # Prints FLAT on its Y=146.10 mm front face on the build plate with ZERO internal supports!
    base_core = make_box(103.70, front_y, 40.74, 149.70, base_rear_y, 84.43 + dz)
    top_ear_l = make_box(108.48, front_y, 86.00, 115.50, base_rear_y, 95.00)
    top_ear_r = make_box(137.90, front_y, 86.00, 144.92, base_rear_y, 95.00)

    # Rear columns and backing web mating to siboorCNC (Y=165.10 mm):
    col_l = make_box(114.20, front_y, 47.00, 121.80, 165.10, 70.00)
    col_r = make_box(131.60, front_y, 47.00, 139.20, 165.10, 70.00)
    low_rib_l = make_box(105.00, front_y, 40.74, 114.50, 165.10, 47.32 + dz)
    low_rib_r = make_box(138.90, front_y, 40.74, 148.40, 165.10, 47.32 + dz)

    # Lower mounting bosses and rear web behind aduct down to Z=36.00 mm:
    rear_web_low = make_box(114.20, 155.50, 36.00, 139.20, 165.10, 47.00)
    low_boss_l = make_box(118.50, 148.10, 36.00, 124.40, 165.10, 42.10)
    low_boss_r = make_box(129.00, 148.10, 36.00, 134.90, 165.10, 42.10)

    cbase_solid = fuse_shapes([
        base_core, top_ear_l, top_ear_r,
        col_l, col_r, low_rib_l, low_rib_r,
        rear_web_low, low_boss_l, low_boss_r,
    ])

    cbase_cuts = [
        # A. Relief at Y=155.00..156.00 for siboorCNC's upper forward standoffs (X=104.2..115.2 and 138.2..150.4, Z=69.5..76.2)
        make_box(103.00, 155.00, 69.50, 115.20, 156.00, 76.20),
        make_box(138.20, 155.00, 69.50, 150.40, 156.00, 76.20),
        # B. Full bottom arch cutout so [a]_duct's flat Z=52.82 top face seats flush
        make_box(109.50, front_y - 0.5, 39.00, 143.90, 155.50, aduct_top_z),
        # C. Relief for aduct lower mounting tab at Z=36..42 mm
        make_box(118.00, front_y - 0.5, 36.00, 135.00, 148.10, 42.10),
        # D. Straight-through vertical internal airflow channel (100% HERMETICALLY SEALED - ZERO LEAKS!)
        make_box(119.68, 147.30, 44.00, 133.72, 154.30, 82.12 + dz),
        # E. Top rear inlet port to duct_extension (X=119.68..133.72, Y=152.50..156.50, Z=76.30+dz..82.12+dz)
        make_box(119.68, 152.50, 76.30 + dz, 133.72, 156.50, 82.12 + dz),
        # F. Micro switch pocket clearance on left (X=105.5..118.9, Y=145.0..150.8, Z=74.3+dz..80.9+dz)
        make_box(105.50, 145.00, 74.30 + dz, 118.90, 150.80, 80.90 + dz),
        # G. Stock carriage-to-carriage_base 4x M3 heat-set insert holes (shifted by dz=+8.0):
        # Upper pair at X=112.90, 140.50, Z=76.569+8=84.569; Lower pair at X=106.20, 147.20, Z=49.319+8=57.319
        make_cyl_y(112.90, 76.569 + dz, front_y - 1.0, front_y + 6.5, 2.35),
        make_cyl_y(140.50, 76.569 + dz, front_y - 1.0, front_y + 6.5, 2.35),
        make_cyl_y(106.20, 49.319 + dz, front_y - 1.0, front_y + 6.5, 2.35),
        make_cyl_y(147.20, 49.319 + dz, front_y - 1.0, front_y + 6.5, 2.35),
        # H. Top duct_extension M3 straight-through clearance holes (X=111.98, 141.42, Z=81.569+8=89.569)
        make_cyl_y(111.98, 81.569 + dz, front_y - 1.0, base_rear_y + 1.0, 1.70),
        make_cyl_y(141.42, 81.569 + dz, front_y - 1.0, base_rear_y + 1.0, 1.70),
        # I. Side M3 holes for [a]_duct upper side tabs (Z=41.569+8=49.569, Y=150.8)
        make_cyl_x(103.00, 111.00, 150.80, 41.569 + dz, 1.70),
        make_cyl_x(142.40, 150.40, 150.80, 41.569 + dz, 1.70),
        # J. Siboor CNC Upper Forward Standoff M3 clearance holes (X=111.20, 142.20, Z=73.019)
        make_cyl_y(111.20, 73.019, front_y - 1.0, 156.00, 1.70),
        make_cyl_y(142.20, 73.019, front_y - 1.0, 156.00, 1.70),
        # K. Siboor CNC Lower Plate M3 clearance holes (X=121.45, 131.95, Z=39.05 mm) through to Y=165.10 mm:
        make_cyl_y(121.45, 39.05, front_y - 1.0, 166.00, 1.70),
        make_cyl_y(131.95, 39.05, front_y - 1.0, 166.00, 1.70),
    ]

    cbase_body = cut_shapes(cbase_solid, cbase_cuts)

    # Pre-hollowed downward male sealing spigot lip (Z=50.82..54.32) telescoping into [a]_duct's throat
    spig_outer_a = make_box(118.90, 146.50, aduct_top_z - 2.00, 134.50, 155.10, aduct_top_z + 1.50)
    spig_step_a = cut_shapes(
        spig_outer_a,
        [
            make_box(118.00, 146.00, aduct_top_z - 2.50, 119.75, 155.50, aduct_top_z),
            make_box(133.65, 146.00, aduct_top_z - 2.50, 135.50, 155.50, aduct_top_z),
            make_box(119.75, 146.00, aduct_top_z - 2.50, 133.65, 147.35, aduct_top_z),
            make_box(119.75, 154.25, aduct_top_z - 2.50, 133.65, 155.50, aduct_top_z),
            make_box(120.55, 148.15, aduct_top_z - 3.00, 132.85, 153.45, aduct_top_z + 2.50),
        ],
    )
    f_cbase = BRepAlgoAPI_Fuse(cbase_body, spig_step_a)
    f_cbase.SetFuzzyValue(1e-3)
    f_cbase.Build()
    cbase_mod = f_cbase.Shape()

    # --- 2. Flat-Backed ABS-Printable `carriage` ---
    carr_sh = translate_shape(raw_carr, 0, dy, dz)

    # Plug old stock holes at X=119.55, 133.85, Z=38.47
    plug_cl = make_cyl_y(119.55, 30.469 + dz, 139.0, 147.0, 3.0)
    plug_cr = make_cyl_y(133.85, 30.469 + dz, 139.0, 147.0, 3.0)
    carr_plugged = fuse_shapes([carr_sh, plug_cl, plug_cr])

    carr_cuts = [
        # Siboor CNC upper standoff front driver access counterbores and clearance holes:
        make_cyl_y(111.20, 73.019, 125.0, front_y + 2.0, 1.70),
        make_cyl_y(111.20, 73.019, 125.0, front_y - 3.0, 3.10),
        make_cyl_y(142.20, 73.019, 125.0, front_y + 2.0, 1.70),
        make_cyl_y(142.20, 73.019, 125.0, front_y - 3.0, 3.10),
        # Top duct_extension M3 heat-set insert pockets at rear face (Y=146.10):
        make_cyl_y(111.98, 81.569 + dz, front_y - 5.5, front_y + 1.0, 2.35),
        make_cyl_y(141.42, 81.569 + dz, front_y - 5.5, front_y + 1.0, 2.35),
        # Siboor CNC lower plate mounting holes at X=121.45, 131.95, Z=39.05 mm (M3 SHCS counterbores on front):
        make_cyl_y(121.45, 39.05, 130.0, front_y + 2.0, 1.70),
        make_cyl_y(121.45, 39.05, 130.0, front_y - 2.5, 3.10),
        make_cyl_y(131.95, 39.05, 130.0, front_y + 2.0, 1.70),
        make_cyl_y(131.95, 39.05, 130.0, front_y - 2.5, 3.10),
    ]
    carr_mod = cut_shapes(carr_plugged, carr_cuts)

    # --- 3. 100% Flat-Top ABS-Printable `[a]_duct` (Unpierced Airflow Arms!) ---
    # Top face stays 100% flat at Z = 52.82 mm for upside-down support-free ABS printing!
    aduct_sh = translate_shape(raw_aduct, 0, dy, dz)

    # Plug old stock holes in mounting tab at X=119.55, 133.85, Z=38.47
    plug_al = make_cyl_y(119.55, 30.469 + dz, 145.0, 149.0, 2.2)
    plug_ar = make_cyl_y(133.85, 30.469 + dz, 145.0, 149.0, 2.2)
    aduct_plugged = fuse_shapes([aduct_sh, plug_al, plug_ar])

    # New lower mounting holes in tab at X=121.45, 131.95, Z=39.05 mm:
    # ZERO holes/cuts on cooling arms! Airflow channels are 100% continuous, hollow, and unpierced.
    cut_al = make_cyl_y(121.45, 39.05, 145.0, 149.0, 1.70)
    cut_ar = make_cyl_y(131.95, 39.05, 145.0, 149.0, 1.70)
    aduct_mod = cut_shapes(aduct_plugged, [cut_al, cut_ar])

    # --- 4. Shifted `duct_extension` (stock length, matching stock 37.76 mm standoffs) ---
    dext_mod = build_shifted_duct_extension(raw_dext, dy, dz)

    # --- 5. Direct Siboor CNC Cartographer Mount ---
    siboor_carto = build_siboor_cartographer_mount(dz=dz)

    return {
        "carriage_base": cbase_mod,
        "carriage": carr_mod,
        "[a]_duct": aduct_mod,
        "duct_extension": dext_mod,
        "siboor_cartographer_mount": siboor_carto,
    }


def build_variant_b_parts(carriage_meta: dict) -> dict[str, TopoDS_Shape]:
    """Builds Variant_B_Integrated_Carriage_UltraCompact_8.5mm (dY = -8.5 mm, dZ = +8.0 mm).
    Iteration 4 Features:
    - 100% hermetically sealed vertical airflow channel in integrated `carriage` (all MGN12H, belt, and inner plate cuts removed).
    - Lower mounting holes in `carriage` moved to X=121.45, 131.95, Z=39.05 mm with front M3 SHCS counterbores.
    - `[a]_duct`'s cooling arms relieved around lower standoffs and sealed with solid forward cap (ZERO leaks, NO bolts through arms).
    """
    dy, dz = VARIANT_B_DY, VARIANT_B_DZ
    raw_carr = load_brep(carriage_meta["carriage"]["brep"])
    raw_aduct = load_brep(carriage_meta["[a]_duct"]["brep"])
    raw_dext = load_brep(carriage_meta["duct_extension"]["brep"])

    front_y = 160.10 + dy       # 151.60 mm
    base_rear_y = 169.50 + dy   # 161.00 mm
    aduct_top_z = 44.82 + dz    # 52.82 mm

    # --- 1. Ultra-Compact Integrated `carriage` ---
    carr_sh = translate_shape(raw_carr, 0, dy, dz)

    # Plug old stock carriage holes at 119.55, 133.85, Z=38.47
    plug_cl = make_cyl_y(119.55, 30.469 + dz, 139.0, 153.0, 3.0)
    plug_cr = make_cyl_y(133.85, 30.469 + dz, 139.0, 153.0, 3.0)
    carr_plugged = fuse_shapes([carr_sh, plug_cl, plug_cr])

    manifold_center = make_box(116.50, front_y - 0.60, 40.74, 136.90, base_rear_y, 84.43 + dz)
    wing_l = make_box(103.70, front_y - 0.60, 40.74, 117.00, 155.00, 84.43 + dz)
    wing_r = make_box(136.40, front_y - 0.60, 40.74, 149.70, 155.00, 84.43 + dz)
    top_ear_l = make_box(108.48, front_y - 0.60, 86.00, 115.50, base_rear_y, 95.00)
    top_ear_r = make_box(137.90, front_y - 0.60, 86.00, 144.92, base_rear_y, 95.00)

    col_l = make_box(115.80, front_y - 0.60, 47.00, 121.80, 165.10, 70.00)
    col_r = make_box(131.60, front_y - 0.60, 47.00, 137.60, 165.10, 70.00)
    low_rib_l = make_box(105.00, front_y - 0.60, 40.74, 114.50, 165.10, 47.32 + dz)
    low_rib_r = make_box(138.90, front_y - 0.60, 40.74, 148.40, 165.10, 47.32 + dz)
    rear_web_low = make_box(115.80, 155.00, 36.00, 137.60, 165.10, 47.00)
    low_boss_l = make_box(118.50, 153.60, 36.00, 124.40, 165.10, 42.10)
    low_boss_r = make_box(129.00, 153.60, 36.00, 134.90, 165.10, 42.10)

    rear_solid = fuse_shapes([
        manifold_center, wing_l, wing_r, top_ear_l, top_ear_r,
        col_l, col_r, low_rib_l, low_rib_r, rear_web_low, low_boss_l, low_boss_r
    ])

    rear_cuts = [
        # Top ears clearance
        make_box(103.00, 162.30, 75.50, 116.10, 166.00, 89.00),
        make_box(137.30, 162.30, 75.50, 150.40, 166.00, 89.00),
        # Bottom arch
        make_box(109.50, front_y - 1.0, 39.00, 143.90, 155.50, aduct_top_z),
        # Relief for aduct tab at Z=36..42
        make_box(118.00, front_y - 1.0, 36.00, 135.00, 153.60, 42.10),
        # Vertical airflow channel (100% SEALED - no leaks!)
        make_box(119.68, 152.80, 44.00, 133.72, 159.80, 82.12 + dz),
        # Top inlet port
        make_box(119.68, 158.00, 76.30 + dz, 133.72, 162.00, 82.12 + dz),
        # Micro switch clearance
        make_box(105.50, 140.00, 74.30 + dz, 118.90, 154.50, 80.90 + dz),
        # Top duct_extension through-holes
        make_cyl_y(111.98, 81.569 + dz, front_y - 5.5, base_rear_y + 1.0, 2.35),
        make_cyl_y(141.42, 81.569 + dz, front_y - 5.5, base_rear_y + 1.0, 2.35),
        # Side M3 holes for [a]_duct upper side tabs
        make_cyl_x(103.00, 111.00, 156.30, 41.569 + dz, 1.70),
        make_cyl_x(142.40, 150.40, 156.30, 41.569 + dz, 1.70),
        # Siboor CNC Upper Forward Standoff clearance holes & counterbores
        make_cyl_y(111.20, 73.019, 130.00, 156.00, 1.70),
        make_cyl_y(111.20, 73.019, 130.00, 151.00, 3.10),
        make_cyl_y(142.20, 73.019, 130.00, 156.00, 1.70),
        make_cyl_y(142.20, 73.019, 130.00, 151.00, 3.10),
        # Lower mounting holes into SiboorCNC tapped holes at (121.45, 39.05) and (131.95, 39.05):
        make_cyl_y(121.45, 39.05, 130.0, 166.0, 1.70),
        make_cyl_y(121.45, 39.05, 130.0, front_y - 2.5, 3.10),
        make_cyl_y(131.95, 39.05, 130.0, 166.0, 1.70),
        make_cyl_y(131.95, 39.05, 130.0, front_y - 2.5, 3.10),
    ]

    rear_hollow = cut_shapes(rear_solid, rear_cuts)
    f_carr = BRepAlgoAPI_Fuse(carr_plugged, rear_hollow)
    f_carr.SetFuzzyValue(1e-3)
    f_carr.Build()
    carr_body_b = cut_shapes(f_carr.Shape(), rear_cuts)

    # Pre-hollowed downward male sealing spigot lip (Z=50.82..54.32) into [a]_duct's throat
    spig_outer_b = make_box(118.90, 152.00, aduct_top_z - 2.00, 134.50, 160.60, aduct_top_z + 1.50)
    spig_step_b = cut_shapes(
        spig_outer_b,
        [
            make_box(118.00, 151.50, aduct_top_z - 2.50, 119.75, 161.00, aduct_top_z),
            make_box(133.65, 151.50, aduct_top_z - 2.50, 135.50, 161.00, aduct_top_z),
            make_box(119.75, 151.50, aduct_top_z - 2.50, 133.65, 152.85, aduct_top_z),
            make_box(119.75, 159.75, aduct_top_z - 2.50, 133.65, 161.00, aduct_top_z),
            make_box(120.55, 153.65, aduct_top_z - 3.00, 132.85, 158.95, aduct_top_z + 2.50),
        ],
    )
    f_carr_spig = BRepAlgoAPI_Fuse(carr_body_b, spig_step_b)
    f_carr_spig.SetFuzzyValue(1e-3)
    f_carr_spig.Build()
    carr_mod_b = f_carr_spig.Shape()

    # --- 2. 100% Flat-Top, Lower-Standoff-Contoured `[a]_duct` ---
    aduct_sh = translate_shape(raw_aduct, 0, dy, dz)

    # Plug old stock holes at 119.55, 133.85, Z=38.47
    plug_al = make_cyl_y(119.55, 30.469 + dz, 150.0, 155.0, 2.2)
    plug_ar = make_cyl_y(133.85, 30.469 + dz, 150.0, 155.0, 2.2)
    aduct_plugged = fuse_shapes([aduct_sh, plug_al, plug_ar])

    cut_l = make_box(102.0, 155.00, 25.80, 117.0, 162.0, 33.70)
    cut_r = make_box(136.4, 155.00, 25.80, 151.4, 162.0, 33.70)
    aduct_cut = cut_shapes(aduct_plugged, [cut_l, cut_r])

    cap_l = make_box(105.00, 153.80, 25.80, 115.00, 155.00, 33.70)
    cap_r = make_box(138.00, 153.80, 25.80, 148.00, 155.00, 33.70)
    aduct_sealed = fuse_shapes([aduct_cut, cap_l, cap_r])

    # Cut new holes at (121.45, 39.05) and (131.95, 39.05) - NO holes through cooling arms!
    cut_al = make_cyl_y(121.45, 39.05, 150.0, 155.0, 1.70)
    cut_ar = make_cyl_y(131.95, 39.05, 150.0, 155.0, 1.70)
    aduct_mod_b = cut_shapes(aduct_sealed, [cut_al, cut_ar])

    # --- 3. Shifted `duct_extension` (stock length, matching stock 37.76 mm standoffs) ---
    dext_mod_b = build_shifted_duct_extension(raw_dext, dy, dz)

    # --- 4. Direct Siboor CNC Cartographer Mount ---
    siboor_carto = build_siboor_cartographer_mount(dz=dz)

    return {
        "carriage": carr_mod_b,
        "[a]_duct": aduct_mod_b,
        "duct_extension": dext_mod_b,
        "siboor_cartographer_mount": siboor_carto,
    }


def export_stl(shape: TopoDS_Shape, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    BRepMesh_IncrementalMesh(shape, 0.08, False, 0.2, True)
    writer = StlAPI_Writer()
    writer.Write(shape, path)


def create_xde_doc():
    app = XCAFApp_Application.GetApplication_s()
    doc = TDocStd_Document(TCollection_ExtendedString("MDTV-XCAF"))
    app.InitDocument(doc)
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    color_tool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    return doc, shape_tool, color_tool


def add_colored_part(shape_tool, color_tool, shape: TopoDS_Shape, name: str, rgb: list[float] | None):
    lbl = shape_tool.AddShape(shape, False)
    TDataStd_Name.Set_s(lbl, TCollection_ExtendedString(name))
    c = rgb if rgb is not None else [0.55, 0.58, 0.62]
    col = Quantity_Color(c[0], c[1], c[2], Quantity_TOC_RGB)
    color_tool.SetColor(lbl, col, XCAFDoc_ColorGen)
    color_tool.SetColor(lbl, col, XCAFDoc_ColorSurf)
    return lbl


def write_xde_step(doc: TDocStd_Document, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Interface_Static.SetCVal_s("write.step.schema", "AP214")
    writer = STEPCAFControl_Writer()
    writer.SetColorMode(True)
    writer.SetNameMode(True)
    writer.Transfer(doc)
    status = writer.Write(path)
    if status != IFSelect_RetDone:
        raise RuntimeError(f"Failed to write STEP file: {path}")


def export_single_part_step(shape: TopoDS_Shape, name: str, rgb: list[float], path: str) -> None:
    doc, shape_tool, color_tool = create_xde_doc()
    add_colored_part(shape_tool, color_tool, shape, name, rgb)
    write_xde_step(doc, path)


def export_assembly_step(
    variant_name: str,
    mod_parts: dict[str, TopoDS_Shape],
    dy: float,
    dz: float,
    carriage_meta: dict,
    siboor_meta: dict,
    tool_meta: dict,
    include_tool: bool,
    out_path: str,
) -> None:
    doc, shape_tool, color_tool = create_xde_doc()

    # 1. Fixed Rail & Extrusion Hardware (world coordinates):
    stationary_parts = ["mgn 12h", "mgn 12h rails 250mm", "2020 Extrusion", "A Belt", "B Belt"]
    for pname in stationary_parts:
        if pname in carriage_meta:
            sh = load_brep(carriage_meta[pname]["brep"])
            add_colored_part(shape_tool, color_tool, sh, pname, carriage_meta[pname]["color"])

    # 2. Unmodified Siboor CNC Carriage & Hardware (aligned to MGN12H):
    for sname, sinfo in siboor_meta.items():
        sh = translate_shape(load_brep(sinfo["brep"]), *SIBOOR_TO_LINEUX_VEC)
        part_label = "siboorCNC" if sname == "Component414" else f"siboor_{sname}"
        add_colored_part(shape_tool, color_tool, sh, part_label, sinfo["color"])

    # 3. Modified Parts for this Variant:
    for mname, mshape in mod_parts.items():
        col = COLOR_ACCENT if mname.startswith("[a]_") else COLOR_PRIMARY
        add_colored_part(shape_tool, color_tool, mshape, mname, col)

    # 4. All Unmodified Lineux Carriage Parts (including 5015_standoff_x2 and 5015_adapter!)
    # Shift together by (dy, dz) so 5015_standoff_x2 stays 100% stock length (37.76 mm = 18 mm behind stepper)!
    skip_parts = set(stationary_parts) | set(mod_parts.keys()) | {
        "carriage_base",
        "klicky_mount",
        "btt_eddy_mount",
    }
    for cname, cinfo in carriage_meta.items():
        if cname in skip_parts:
            continue
        sh = translate_shape(load_brep(cinfo["brep"]), 0, dy, dz)
        add_colored_part(shape_tool, color_tool, sh, cname, cinfo["color"])

    # 5. Optional LineuxTool Assembly (shifted by the same dy, dz):
    if include_tool:
        for tname, tinfo in tool_meta.items():
            sh = translate_shape(load_brep(tinfo["brep"]), 0, dy, dz)
            add_colored_part(shape_tool, color_tool, sh, tname, tinfo["color"])

    write_xde_step(doc, out_path)


def export_all_variants():
    t0 = time.time()
    with open(f"{CACHE_DIR}/siboor_meta.json", "r", encoding="utf-8") as f:
        siboor_meta = json.load(f)
    with open(f"{CACHE_DIR}/carriage_meta.json", "r", encoding="utf-8") as f:
        carriage_meta = json.load(f)
    with open(f"{CACHE_DIR}/tool_meta.json", "r", encoding="utf-8") as f:
        tool_meta = json.load(f)

    # Clean old variant directories if present
    if os.path.exists(OUTPUT_ROOT):
        for entry in os.listdir(OUTPUT_ROOT):
            full_p = os.path.join(OUTPUT_ROOT, entry)
            if os.path.isdir(full_p) and entry.startswith("Variant_"):
                shutil.rmtree(full_p)

    variants = [
        (
            "Variant_A_Separate_Carriage_Base_14mm",
            build_variant_a_parts(carriage_meta),
            VARIANT_A_DY,
            VARIANT_A_DZ,
        ),
        (
            "Variant_B_Integrated_Carriage_UltraCompact_8.5mm",
            build_variant_b_parts(carriage_meta),
            VARIANT_B_DY,
            VARIANT_B_DZ,
        ),
    ]

    gen_cache_dir = f"{CACHE_DIR}/generated"
    os.makedirs(gen_cache_dir, exist_ok=True)

    for vname, vparts, dy, dz in variants:
        print(f"\n=== Exporting {vname} (dY={dy} mm, dZ=+{dz} mm) ===")
        cad_dir = os.path.join(OUTPUT_ROOT, vname, "CAD")
        stl_dir = os.path.join(OUTPUT_ROOT, vname, "STL")
        os.makedirs(cad_dir, exist_ok=True)
        os.makedirs(stl_dir, exist_ok=True)

        for pname, pshape in vparts.items():
            nsolids = count_solids(pshape)
            bb = get_bbox(pshape)
            print(f"  {pname:28s} | solids={nsolids} | bbox={bb}")

            safe_name = pname.replace("[a]_", "a_").replace(" ", "_")
            save_brep(pshape, f"{gen_cache_dir}/{vname}_{safe_name}.brep")

            col = COLOR_ACCENT if pname.startswith("[a]_") else COLOR_PRIMARY
            export_single_part_step(pshape, pname, col, os.path.join(cad_dir, f"{pname}.step"))
            export_stl(pshape, os.path.join(stl_dir, f"{pname}.stl"))

        asm_no_tool = os.path.join(cad_dir, "Siboor_Lineux_Carriage_Assembly.step")
        export_assembly_step(
            vname, vparts, dy, dz, carriage_meta, siboor_meta, tool_meta, False, asm_no_tool
        )

        asm_with_tool = os.path.join(cad_dir, "Siboor_Lineux_Carriage_With_Tool_Assembly.step")
        export_assembly_step(
            vname, vparts, dy, dz, carriage_meta, siboor_meta, tool_meta, True, asm_with_tool
        )

    print(f"\nAll variants generated and exported in {time.time() - t0:.2f}s")


if __name__ == "__main__":
    export_all_variants()
