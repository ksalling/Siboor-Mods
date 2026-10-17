"""Extract and cache key solids, transforms, bounding boxes, and colors from input STEP files.

This script runs once to populate `cache/siboor_lineux/` so that all subsequent
2D cross-section analyses and CAD iterations run in < 1 second without re-parsing
hundreds of megabytes of PCB SMD components.
"""

import json
import os
import time
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepTools import BRepTools
from OCP.Quantity import Quantity_Color
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.XCAFDoc import XCAFDoc_ColorType, XCAFDoc_DocumentTool

CACHE_DIR = "cache/siboor_lineux"
os.makedirs(CACHE_DIR, exist_ok=True)


def get_name(label: TDF_Label) -> str:
    name_attr = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), name_attr):
        return name_attr.Get().ToExtString()
    return ""


def get_shape_color(color_tool, shape):
    c = Quantity_Color()
    for ctype in (
        XCAFDoc_ColorType.XCAFDoc_ColorSurf,
        XCAFDoc_ColorType.XCAFDoc_ColorGen,
        XCAFDoc_ColorType.XCAFDoc_ColorCurv,
    ):
        if color_tool.GetColor(shape, ctype, c):
            return [round(c.Red(), 4), round(c.Green(), 4), round(c.Blue(), 4)]
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    while exp.More():
        sol = exp.Current()
        for ctype in (
            XCAFDoc_ColorType.XCAFDoc_ColorSurf,
            XCAFDoc_ColorType.XCAFDoc_ColorGen,
        ):
            if color_tool.GetColor(sol, ctype, c):
                return [round(c.Red(), 4), round(c.Green(), 4), round(c.Blue(), 4)]
        exp.Next()
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = exp.Current()
        for ctype in (
            XCAFDoc_ColorType.XCAFDoc_ColorSurf,
            XCAFDoc_ColorType.XCAFDoc_ColorGen,
        ):
            if color_tool.GetColor(face, ctype, c):
                return [round(c.Red(), 4), round(c.Green(), 4), round(c.Blue(), 4)]
        exp.Next()
    return None


def cache_step(step_path: str, prefix: str, target_names: set[str] | None = None):
    t0 = time.time()
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    reader = STEPCAFControl_Reader()
    reader.SetColorMode(True)
    reader.SetNameMode(True)
    reader.ReadFile(step_path)
    reader.Transfer(doc)
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    color_tool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

    meta = {}

    def walk(label: TDF_Label, loc: TopLoc_Location):
        name = get_name(label)
        cur_loc = loc.Multiplied(shape_tool.GetLocation_s(label))
        r = TDF_Label()
        is_ref = shape_tool.GetReferredShape_s(label, r)
        target = r if is_ref else label
        ref_name = get_name(r) if is_ref else name
        clean_name = name.split(":")[0]

        match_key = None
        if target_names is None:
            if not shape_tool.IsAssembly_s(target):
                match_key = clean_name or ref_name
        else:
            if clean_name in target_names:
                match_key = clean_name
            elif ref_name in target_names:
                match_key = ref_name

        if match_key:
            raw_shape = shape_tool.GetShape_s(target)
            moved_shape = raw_shape.Moved(cur_loc)
            col = get_shape_color(color_tool, raw_shape) or get_shape_color(color_tool, moved_shape)
            bbox = Bnd_Box()
            BRepBndLib.Add_s(moved_shape, bbox)
            b = [round(x, 3) for x in bbox.Get()] if not bbox.IsVoid() else []
            safe_key = (
                match_key.replace("[", "")
                .replace("]", "")
                .replace(" ", "_")
                .replace("(", "")
                .replace(")", "")
            )
            idx = 0
            unique_key = match_key
            while unique_key in meta:
                idx += 1
                unique_key = f"{match_key}__{idx}"
            if idx > 0:
                safe_key = f"{safe_key}__{idx}"
            brep_path = f"{CACHE_DIR}/{prefix}_{safe_key}.brep"
            BRepTools.Write_s(moved_shape, brep_path)
            meta[unique_key] = {
                "name": match_key,
                "brep": brep_path,
                "color": col,
                "bbox": b,
            }
            print(f"[{prefix}] Saved {unique_key}: color={col}, bbox={b}")

        if not any(skip in (name + ref_name) for skip in ["Ebb36", "Tool Lite"]):
            children = TDF_LabelSequence()
            shape_tool.GetComponents_s(target, children)
            for i in range(1, children.Length() + 1):
                walk(children.Value(i), cur_loc)

    roots = TDF_LabelSequence()
    shape_tool.GetFreeShapes(roots)
    for i in range(1, roots.Length() + 1):
        walk(roots.Value(i), TopLoc_Location())

    with open(f"{CACHE_DIR}/{prefix}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"Finished {prefix} in {time.time() - t0:.2f}s")


if __name__ == "__main__":
    cache_step("inputs/siboorCNC.step", "siboor", None)
    cache_step(
        "inputs/LineuxCarriage.step",
        "carriage",
        {
            "carriage_base",
            "carriage",
            "latch_plate",
            "[a]_latch",
            "gear_plate",
            "[a]_duct",
            "duct_extension",
            "5015_adapter",
            "5015_standoff_x2",
            "5015_standoff_x2 (1)",
            "mgn 12h",
            "mgn 12h rails 250mm",
            "2020 Extrusion",
            "micro switch",
            "Nema 14 Stepper",
            "cartographer_mount",
            "klicky_mount",
            "btt_eddy_mount",
            "led_mount",
            "led_cover",
            "diffuser",
            "pug_collar_front",
            "pug_collar_rear",
            "screw_spacer",
            "B Belt",
            "A Belt",
        },
    )
    cache_step(
        "inputs/LineuxTool.step",
        "tool",
        {
            "[a]_toolhead",
            "[a]_toolhead_12mm",
            "wire_cover",
            "[a]_v6chp_shroud_mount",
            "[a]_v6chp_mount",
            "[a]_rapidohf_shroud_mount",
            "[a]_rapidohf_mount",
            "connector_cover (1)",
        },
    )
