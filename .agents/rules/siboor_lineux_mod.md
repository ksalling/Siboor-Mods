---
trigger: always_on
description: Core mechanical, CAD, 2D analysis, output structure, and GitHub rules for the Siboor Lineux Mod project.
---

# Siboor Lineux Mod — Always-On Workspace Rules

1. **Never modify `siboorCNC.step`**. All attachments must use existing screw holes on `siboorCNC`.
2. **Use 2D cross-sections ONLY** (`BRepAlgoAPI_Section` on planes) to analyze part interactions, clearances, and airflow channels. Never perform 3D boolean intersections across multi-part assemblies.
3. **Reuse cached BREP solids** in `cache/siboor_lineux/` and parametric Python modules in `src/siboor_lineux/` to save time and tokens.
4. **Maintain 100% sealed airflow** from `duct_extension` to the bottom nozzle exits of `[a]_duct` with zero leaks and preserved cross-sectional flow area.
5. **ABS 3D Printability (Mandatory)**: Every modified printed part must have a flat build-plate orientation and **zero unreachable internal supports** inside airflow channels (keep `[a]_duct`'s top face 100% flat for upside-down support-free printing).
6. **Keep 18 mm stepper-to-5015_adapter spacing**: Shift `5015_adapter` with the carriage so `5015_standoff_x2` remains 100% stock ($37.76\text{ mm}$).
7. **Mandatory Fastener Accounting & Collision Verification**: Every part connection must account for real fasteners (screws, heat-set inserts, counterbores, driver access). All 4 main `siboorCNC` mounting standoffs (Upper-Left `111.2, 73.02`, Upper-Right `142.2, 73.02`, Lower-Left `110.45, 29.72`, Lower-Right `142.95, 29.72`) must have solid, verified fastener connections with counterbored head clearance. No fastener paths (e.g. from `5015_adapter` through `duct_extension`) may collide with solid sections of `siboorCNC`.
8. **Verify tool fit** against `LineuxTool.step` on every design variant.
9. **Preserve original STEP part names and RGB colors**.
10. **Output folder structure**: `Siboor Lineux Mod/<Variant_Name>/CAD/*.step` (including modified parts, assembly without tool, and assembly with tool) and `Siboor Lineux Mod/<Variant_Name>/STL/*.stl`.
11. **Push to GitHub**: Push `Siboor Lineux Mod` updates to `https://github.com/ksalling/Siboor-Mods` on completion of each milestone/iteration.
