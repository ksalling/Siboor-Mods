---
trigger: always_on
description: Core mechanical, CAD, 2D analysis, output structure, and GitHub rules for the Siboor Lineux Mod project.
---

# Siboor Lineux Mod — Always-On Workspace Rules

1. **Never modify `siboorCNC.step`**. All attachments must use existing screw holes on `siboorCNC`.
2. **Use 2D cross-sections ONLY** (`BRepAlgoAPI_Section` on planes) to analyze part interactions, clearances, and airflow channels. Never perform 3D boolean intersections across multi-part assemblies.
3. **Reuse cached BREP solids** in `cache/siboor_lineux/` and parametric Python modules in `src/siboor_lineux/` to save time and tokens.
4. **Maintain 100% sealed airflow** from `duct_extension` to the bottom nozzle exits of `[a]_duct` with zero leaks and preserved cross-sectional flow area.
5. **Verify tool fit** against `LineuxTool.step` on every design variant.
6. **Preserve original STEP part names and RGB colors**.
7. **Output folder structure**: `Siboor Lineux Mod/<Variant_Name>/CAD/*.step` (including modified parts, assembly without tool, and assembly with tool) and `Siboor Lineux Mod/<Variant_Name>/STL/*.stl`.
8. **Push to GitHub**: Push `Siboor Lineux Mod` updates to `https://github.com/ksalling/Siboor-Mods` on completion of each milestone/iteration.
