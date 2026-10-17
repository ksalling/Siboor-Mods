# Siboor Lineux Mod — Project Rules & Agent Boundaries

These rules and boundaries govern the **Siboor Lineux Mod** project and MUST be followed on every turn and iteration without needing to be restated by the user.

---

## 1. Core Mechanical & CAD Rules

1. **Do Not Modify `siboorCNC.step`:**
   - The stock Siboor Voron Trident CNC carriage (`inputs/siboorCNC.step`) is a fixed, machined aluminum component. It MUST NOT be modified, drilled, trimmed, or altered in any way.
   - All connections from modified Lineux Carriage parts to `siboorCNC` MUST use the **existing screw holes** and mounting features on `siboorCNC`.
2. **Replace `carriage_base` with `siboorCNC`:**
   - In `inputs/LineuxCarriage.step`, `carriage_base` is replaced by the `siboorCNC` assembly mounted on the `MGN12H` linear rail block.
   - Minimize the number of modified Lineux parts so the modification integrates with the stock Lineux Hotswap ecosystem as cleanly as possible.
3. **Strict Airflow Integrity (Sealed Path, Full Volume):**
   - Part-cooling air enters through `duct_extension` (from `5015_adapter` / 5015 blower fan) and exits ONLY at the bottom nozzle outlets of `[a]_duct`.
   - There MUST be **zero gaps, holes, or unsealed seams** where air can escape between `duct_extension`, the bridge/carriage channel, and `[a]_duct`.
   - Maintain proper internal cross-sectional airflow area/volume throughout the transition around/under `siboorCNC` (widening/deepening the carriage/duct in `-Y` as needed).
4. **Two Design Variants (Separate ABS-Printable `carriage_base` vs. Ultra-Compact Integrated `carriage`):**
   - **Variant A (`Variant_A_Separate_Carriage_Base_14mm`, $\Delta Y = -14.0\text{ mm}, \Delta Z = +2.5\text{ mm}$):** Dedicated ABS-printable `carriage_base` with a 100% flat front build-plate face, flat-backed `carriage`, and flat-top `[a]_duct` with downward/female telescopic spigot sealing.
   - **Variant B (`Variant_B_Integrated_Carriage_UltraCompact_8.5mm`, $\Delta Y = -8.5\text{ mm}, \Delta Z = +2.5\text{ mm}$):** Ultra-compact depth tucking the vertical air channel inside `siboorCNC`'s central front pocket, integrated `carriage`, and flat-top `[a]_duct` with contoured lower-standoff relief and forward internal air bypass.
5. **ABS 3D Printability & Support-Free Channels (Mandatory):**
   - All modified printed parts MUST be designed for **ABS 3D printing** with a **flat primary build-plate face** (e.g., flat top face on `[a]_duct` for upside-down printing, flat front face on `carriage_base`, flat rear face on `carriage`) and **zero unreachable internal supports** inside any airflow channel.
6. **Stock 5015 Standoff Spacing ($18\text{ mm}$ Behind Stepper Motor):**
   - Shift `5015_adapter` and `5015 Blower Fan` by the same $(\Delta Y, \Delta Z)$ as `carriage` and `Nema 14 Stepper` so `5015_standoff_x2` remains 100% stock length ($37.76\text{ mm}$ = $20\text{ mm}$ stepper motor + $17.76\text{ mm} \approx 18\text{ mm}$ space to `5015_adapter`).
7. **Mandatory Fastener Accounting & Collision Verification:**
   - Every single part connection must be accounted for with real, verifiable fasteners (screws, heat-set inserts, counterbores, driver clearance, and thread engagement).
   - All 4 main `siboorCNC` threaded mounting standoffs (Upper-Left `111.20, 73.02`, Upper-Right `142.20, 73.02`, Lower-Left `110.45, 29.72`, Lower-Right `142.95, 29.72` at $Y = 155.00\text{ mm}$) must connect solidly with verified fastener heads, counterbores, and alignment.
   - All fastener paths (such as the two lower bolts from `5015_adapter` through `duct_extension`) must be verified to have zero collisions with solid sections of `siboorCNC`.
8. **Toolhead Compatibility Verification (`LineuxTool.step`):**
   - Every design iteration MUST be verified against `inputs/LineuxTool.step` (shifted by the same $(\Delta Y, \Delta Z)$ carriage offset) to guarantee full mechanical clearance, proper dovetail/latch engagement, magnet/pin alignment, and hotend shroud / nozzle clearance relative to `[a]_duct`.

---

## 2. Computational & Analysis Rules (2D Cross-Sections ONLY)

1. **Mandatory 2D Cross-Section Analysis:**
   - **NEVER** run full-assembly 3D boolean intersections (`BRepAlgoAPI_Common` / `BRepAlgoAPI_Fuse` across multi-part STEP assemblies) to check clearances or interactions—this freezes OpenCASCADE and causes infinite loops.
   - **ALWAYS** use **2D planar cross-sections** (`BRepAlgoAPI_Section` with X, Y, or Z planes, or 2D slice rasterization/polygon analysis) on cached part solids (`cache/siboor_lineux/*.brep`) to inspect wall thicknesses, screw engagement, clearances, and sealed airflow channels.
2. **Reuse Code & Cached Solids:**
   - Never re-parse the raw 161 MB `LineuxCarriage.step` or 106 MB `LineuxTool.step` repeatedly during iterations. Use the pre-extracted `.brep` solids and `*_meta.json` in `cache/siboor_lineux/`.
   - Keep all CAD generation parametric and modular inside `src/siboor_lineux/` so parameter tweaks (e.g., $\Delta Y$ offset, wall thickness, flange depth, hole tolerances) only require editing config constants and re-running the generator.

---

## 3. Output Format, Color Coding, Naming & Folder Structure

1. **Preserve Original Names & Color Coding:**
   - Respect the exact part naming (e.g., `carriage`, `[a]_duct`, `duct_extension`, `[a]_latch`, `latch_plate`, `gear_plate`, `5015_standoff_x2`) and RGB color coding (`[a]_` accent color vs. primary color vs. CNC hardware colors) from the original STEP files.
2. **Required Deliverables per Design Variant:**
   - Individual `.stl` and `.step` files for **every modified part**.
   - Full assembly `.step` file **without** the tool (`LineuxCarriage` modified assembly with `siboorCNC`).
   - Full assembly `.step` file **with** the tool (`LineuxCarriage` + `siboorCNC` + `LineuxTool` mounted).
3. **Output Directory Hierarchy:**
   - Main folder: `Siboor Lineux Mod/`
   - Inside `Siboor Lineux Mod/`, separate each design variant into its own clearly named folder (with `CAD/` for `.step` files and `STL/` for `.stl` files nested underneath):
     ```text
     Siboor Lineux Mod/
     ├── <Design_Variant_1_Name>/
     │   ├── CAD/
     │   │   ├── <modified_part>.step
     │   │   ├── Siboor_Lineux_Carriage_Assembly.step
     │   │   └── Siboor_Lineux_Carriage_With_Tool_Assembly.step
     │   └── STL/
     │       └── <modified_part>.stl
     └── <Design_Variant_2_Name>/
         ├── CAD/
         └── STL/
     ```

---

## 4. Git & GitHub Version Control Rules

1. **Target Repository:** `https://github.com/ksalling/Siboor-Mods`
2. **Push on Completion:**
   - On completion of each milestone/iteration, stage, commit with a descriptive engineering changelog message, and push the `Siboor Lineux Mod` folder (and supporting scripts/docs as appropriate) to `ksalling/Siboor-Mods`.
3. **Communicate & Clarify Proactively:**
   - Always ask clarifying questions whenever design trade-offs, tolerances, hardware choices (e.g., probe type, toolboard type, standoff length, screw lengths), or naming conventions are ambiguous.
